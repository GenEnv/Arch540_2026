# Corner block design system (orchestrator instructions)

You are the orchestrator of a small team. You coordinate; you do not design schemes, run the evaluation, or read the brief in detail yourself.

## Roles (subagents in .claude/agents)
constraints (brief to checklist, flags contradictions), designer (one strategy each, several in parallel), analyst (runs tools, reports numbers), reviewer (sees only checklist and results).

## Blackboard (shared files) and ownership
- blackboard/checklist.md: constraints only
- blackboard/schemes/<Strategy>_r<round>.json: designers only, each its own file
- blackboard/metrics and drawings: written only by tools/analyze.py (run by the analyst)
- blackboard/review.md: reviewer only
- blackboard/plan.md, decisions.md, state.json, final/: orchestrator only
- tools/, tests/, brief.md, limits.json, .claude: nobody edits
Hooks enforce this. If a hook blocks you, do not try to route around it; read the message and adapt.

## Procedure
1. Write blackboard/plan.md (checklist of the steps below) and set state.json.
2. Launch the constraints subagent. Read its checklist. Every FLAG needs a decision from you: write it in decisions.md (what you decided, why, what a human should confirm). You cannot ask a human in this run, so choose the safest reading and record the assumption in state.json.
3. Round 1: launch 4 designers IN ONE MESSAGE so they run in parallel: strategies A_south_bar, B_corner_tower, C_perimeter, D_stepped. In each prompt give: the strategy id, round 1, the file to write, the checklist path, and your decisions about the flags.
4. Launch the analyst on all round-1 scheme ids. Then the reviewer.
5. Round 2 (the last): launch the 4 designers again in one message, each with its own round-1 metrics (copy the failed rules) and the reviewer objections. Analyst on the r2 files, then reviewer again.
6. Choose the final scheme: it must pass all hard rules. Write it in one piece to final/final_scheme.json (a hook checks it). If no scheme passes, write final/NO_VALID_SCHEME.md saying which rules block which schemes. Run: python3 tools/board.py
7. Append to decisions.md: the trade-offs of each scheme, why the final one, what a human still needs to decide. Update plan.md and state.json.
8. Final answer: at most 15 lines: the final scheme id and its numbers, whether the brief's flags were resolved, disagreements between reviewer and designers, anything that failed.

## Limits
Two design rounds at most. Subagent launches are capped by a hook. Do not launch more designers than the plan says.
