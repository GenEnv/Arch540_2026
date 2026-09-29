#!/usr/bin/env python3
"""PreToolUse hook. Runs OUTSIDE the model. Before any write into output/*.json it runs the rule checker
on the content about to be written. If a rule fails the write is blocked (exit code 2) and the message on
stderr is shown to the model. It also counts blocks: after LIMIT blocks it tells the model to stop."""
import json, os, re, subprocess, sys, tempfile

PROJ = os.environ.get("CLAUDE_PROJECT_DIR") or os.getcwd()
PY = "python3"
STATE = os.path.join(PROJ, ".claude", "hooks", "state")
os.makedirs(STATE, exist_ok=True)
try:
    LIMIT = int(open(os.path.join(PROJ, ".claude", "hooks", "limit.txt")).read().strip())
except Exception:
    LIMIT = 6

def block(msg):
    n_file = os.path.join(STATE, "blocks.txt")
    n = int(open(n_file).read()) + 1 if os.path.exists(n_file) else 1
    open(n_file, "w").write(str(n))
    with open(os.path.join(STATE, "log.txt"), "a") as f:
        f.write(f"--- block {n} ---\n{msg}\n")
    tail = f"\n(blocked write {n} of {LIMIT} allowed)"
    if n >= LIMIT:
        tail += ("\nROUND LIMIT REACHED. Do not try to write output/layout.json again. Stop now and end your "
                 "final message with the word UNRESOLVED, saying which rules still fail.")
    print(msg + tail, file=sys.stderr)
    sys.exit(2)

def run_check(text):
    with tempfile.NamedTemporaryFile("w", suffix=".json", delete=False) as f:
        f.write(text)
    r = subprocess.run([PY, os.path.join(PROJ, "check.py"), f.name], capture_output=True, text=True)
    os.unlink(f.name)
    return r.returncode, r.stdout

ev = json.load(sys.stdin)
tool, ti = ev.get("tool_name"), ev.get("tool_input", {})
out_dir = os.path.join(PROJ, "output") + os.sep

if tool in ("Write", "Edit"):
    path = os.path.abspath(os.path.join(PROJ, ti.get("file_path", "")))
    if path.startswith(out_dir) and path.endswith(".json"):
        if tool == "Write":
            text = ti.get("content", "")
        else:
            try:
                text = open(path).read().replace(ti["old_string"], ti["new_string"], 1)
            except Exception:
                text = ""
        code, out = run_check(text)
        if code != 0:
            block("BLOCKED by the layout gate: this layout breaks the planning rules, so it was not written to output/.\n" + out)
elif tool == "Bash":
    cmd = ti.get("command", "")
    if re.search(r"output/[\w./-]*\.json", cmd) and re.search(r"(>|open\(|write|dump|tee|cp |mv )", cmd) and "check.py" not in cmd:
        block("BLOCKED by the layout gate: do not write into output/*.json from a shell command. "
              "Save the layout with the file-writing tool so it can be checked first.")
sys.exit(0)
