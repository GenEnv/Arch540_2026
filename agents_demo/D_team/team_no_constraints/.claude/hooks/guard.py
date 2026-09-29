#!/usr/bin/env python3
"""PreToolUse guard. Exit 2 blocks the tool call and the message on stderr goes back to the model."""
import sys, json, os, re, time
root = os.environ.get("CLAUDE_PROJECT_DIR") or os.getcwd()
sys.path.insert(0, os.path.join(root, "tools"))
d = json.load(sys.stdin)
tool, inp, agent = d.get("tool_name"), d.get("tool_input", {}), d.get("agent_type")  # agent_type absent = main session
os.makedirs(os.path.join(root, "logs"), exist_ok=True)

def log(decision, why=""):
    with open(os.path.join(root, "logs", "hooks.jsonl"), "a") as f:
        f.write(json.dumps({"t": time.strftime("%H:%M:%S"), "tool": tool, "agent": agent or "main", "decision": decision,
                            "why": why, "target": str(inp.get("file_path") or inp.get("subagent_type") or inp.get("command", ""))[:140]}) + "\n")

def block(msg):
    log("BLOCK", msg)
    print("BLOCKED by project hook: " + msg, file=sys.stderr)
    sys.exit(2)

LIM = json.load(open(os.path.join(root, "limits.json")))
SOLO = LIM.get("solo", False)  # ablation: one context does every role
PROTECTED = ["tools/", "tests/", "brief.md", "limits.json", ".claude/", "logs/"]

if tool in ("Agent", "Task"):
    lim = json.load(open(os.path.join(root, "limits.json")))
    p = os.path.join(root, "logs", "agent_calls.json")
    c = json.load(open(p)) if os.path.exists(p) else {"total": 0, "designer": 0}
    kind = inp.get("subagent_type", "")
    if c["total"] >= lim["max_agent_calls"]:
        block(f"subagent budget used up ({c['total']} of {lim['max_agent_calls']} launches). Finish with what you have.")
    if kind == "designer" and c["designer"] >= lim["max_designer_calls"]:
        block(f"designer limit reached ({c['designer']} of {lim['max_designer_calls']}). No more design rounds.")
    c["total"] += 1
    c["designer"] += kind == "designer"
    json.dump(c, open(p, "w"))
    log("allow", f"launch {c['total']}/{lim['max_agent_calls']}")
    sys.exit(0)

if tool in ("Write", "Edit", "MultiEdit"):
    fp = os.path.abspath(inp.get("file_path", ""))
    rel = os.path.relpath(fp, root)
    if rel.startswith(".."):
        block("writing outside the project folder is not allowed.")
    if any(rel.startswith(p) or rel == p.rstrip("/") for p in PROTECTED):
        block(f"{rel} is read-only for every agent (evaluation tools, tests, brief, limits and settings are protected).")
    own = {"blackboard/checklist.md": "constraints", "blackboard/review.md": "reviewer"}
    if rel in own and agent != own[rel] and not SOLO:
        block(f"{rel} belongs to the {own[rel]} role. You are {agent or 'the orchestrator'}.")
    if rel.startswith("blackboard/schemes/"):
        if agent != "designer" and not SOLO:
            block("only designers write schemes. You are " + (agent or "the orchestrator") + ".")
        if not re.fullmatch(r"blackboard/schemes/[A-Za-z0-9]+_r[12]\.json", rel):
            block("scheme files must be named <strategy>_r1.json or <strategy>_r2.json (rounds are limited to 2).")
    if rel.startswith("blackboard/metrics/") or rel.startswith("blackboard/drawings/"):
        block("metrics and drawings are written only by the analysis tool, never by hand.")
    if rel in ("blackboard/decisions.md", "blackboard/state.json", "blackboard/plan.md") or rel.startswith("final/"):
        if agent and not SOLO:
            block(f"{rel} belongs to the orchestrator. You are {agent}.")
    if rel == "final/final_scheme.json":
        if tool != "Write":
            block("write final_scheme.json in one piece with Write.")
        try:
            import geom
            res = geom.evaluate(json.loads(inp["content"]))
        except Exception as e:
            block(f"final scheme is not valid: {e}")
        if not res["hard_pass"]:
            bad = [f"{r['rule']} (value {r['value']}, limit {r['limit']})" for r in res["rules"] if not r["pass"]]
            block("this scheme fails hard rules, so it cannot be written as the final scheme: " + "; ".join(bad))
    log("allow", rel)
    sys.exit(0)

if tool == "Bash":
    cmd = inp.get("command", "")
    writes = re.search(r"(>|\btee\b|\bcp\b|\bmv\b|sed\s+-i|\brm\b|\bchmod\b)", cmd)
    touches = re.search(r"(tools/|tests/|brief\.md|limits\.json|\.claude/|final/final_scheme|blackboard/metrics)", cmd)
    runs_ok = re.match(r"\s*(python3|python3?)\s+(tools/(analyze|evaluate|draw|board)\.py|tests/test_tools\.py)", cmd)
    if writes and touches and not runs_ok:
        block("this command would change a protected file. Use the Write tool and follow the ownership rules.")
    log("allow", "bash")
sys.exit(0)
