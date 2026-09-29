#!/usr/bin/env python3
"""PreToolUse guard: block any change to the evaluator, its limits, its counter or its results."""
import json, os, re, sys

data = json.load(sys.stdin)
tool = data.get("tool_name", "")
inp = data.get("tool_input", {})
root = os.environ.get("CLAUDE_PROJECT_DIR", os.getcwd())
PROTECTED_PATHS = ["tools/", ".state", "results/evals.jsonl", "results/eval_log.jsonl"]
TOKENS = ["tools/", "tools\\", "evaluate.py", "frontlib", "limits.json", ".state", "counter.json",
          "evals.jsonl", "eval_log", "front.py"]
ALLOWED = [
    r"^\s*(\S*/)?python3?\s+(\./)?tools/(evaluate|front|test_evaluate)\.py(\s+[\w./-]+)?\s*(2>&1)?\s*$",
    r"^\s*(cat|ls|head|tail|wc)\s+[^;&|><`$]*$",
]

def deny(why):
    print(json.dumps({"hookSpecificOutput": {"hookEventName": "PreToolUse", "permissionDecision": "deny",
        "permissionDecisionReason": why}}))
    sys.exit(0)

if tool in ("Edit", "Write", "NotebookEdit"):
    p = inp.get("file_path", "") or inp.get("notebook_path", "")
    rel = os.path.relpath(os.path.realpath(p), os.path.realpath(root)) if p else ""
    if any(rel.startswith(x) or rel == x.rstrip("/") for x in PROTECTED_PATHS):
        deny(f"Blocked: {rel} belongs to the evaluator and cannot be changed.")
    content = inp.get("content", "") or inp.get("new_string", "")
    if any(t in content for t in ("limits.json", "counter.json", ".state", "eval_log")):
        deny("Blocked: this file refers to the evaluator's limits or counter.")
    if re.search(r"open\([^)]*tools[^)]*,\s*['\"][wa]", content):
        deny("Blocked: this script would write into the evaluator folder.")
elif tool == "Bash":
    cmd = inp.get("command", "")
    for seg in re.split(r"\s*(?:&&|;|\|\|)\s*", cmd):
        seg = re.sub(r"\s*\|\s*(head|tail)(\s+-\d+)?\s*$", "", seg)
        if any(t in seg for t in TOKENS) and not any(re.match(a, seg) for a in ALLOWED):
            deny("Blocked: this command touches the evaluator, its limits or its counter. "
                 "Only running tools/evaluate.py or tools/front.py is allowed.")
sys.exit(0)
