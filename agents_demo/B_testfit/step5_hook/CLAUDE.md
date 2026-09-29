# Project rules for the test-fit

- Work in `work/`. The final layout goes into `output/layout.json` with the file-writing tool, never from a shell command.
- Round limit: you may revise a failing layout at most 2 times. If it still fails after that, stop and end your final message with UNRESOLVED. Never claim success without a passing check.
- A hook in this project checks every layout written into `output/` and refuses failing ones. That is not a problem to route around.
