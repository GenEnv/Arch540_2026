#!/usr/bin/env python3
"""Stop hook. Counts words in statement*; if over 150, blocks the stop (exit 2) and tells the model.
After 3 blocks it lets the agent stop (round limit)."""
import glob, json, os, re, sys
root = os.environ.get("CLAUDE_PROJECT_DIR", ".")
files = sorted(glob.glob(os.path.join(root, "statement*")))
if not files:
    sys.exit(0)
text = open(files[0]).read()
body = "\n".join(l for l in text.splitlines() if not l.lstrip().startswith("#"))
n = len([w for w in body.split() if re.search(r"[A-Za-z0-9]", w)])
cf = os.path.join(root, ".guard_count")
c = int(open(cf).read()) if os.path.exists(cf) else 0
log = open(os.path.join(root, "guard.log"), "a")
if n > 150 and c < 3:
    open(cf, "w").write(str(c + 1))
    msg = f"BLOCKED by word limit hook: {os.path.basename(files[0])} has {n} words, the limit is 150. Cut it to 150 or fewer, then finish. (block {c+1} of 3)"
    log.write(msg + "\n"); print(msg, file=sys.stderr); sys.exit(2)
log.write(f"ALLOWED: {n} words, blocks so far {c}\n")
sys.exit(0)
