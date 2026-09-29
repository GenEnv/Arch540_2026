#!/usr/bin/env python3
"""Checker for the project statement. Usage: python3 tools/check.py <statement file>
Prints the exact word count (title lines starting with # are not counted)
and lists every number in the statement, marking numbers that do not appear in notes.md."""
import re, sys
text = open(sys.argv[1]).read()
notes = open("notes.md").read()
body = "\n".join(l for l in text.splitlines() if not l.lstrip().startswith("#"))
words = [w for w in body.split() if re.search(r"[A-Za-z0-9]", w)]
print(f"WORD COUNT: {len(words)} (limit 150)")
nums = re.findall(r"\d[\d,\.]*", body)
note_nums = set(re.findall(r"\d[\d,\.]*", notes))
for n in dict.fromkeys(nums):
    n2 = n.rstrip(".,")
    print(f"number {n2}: {'in notes' if n2 in note_nums else 'NOT IN NOTES'}")
