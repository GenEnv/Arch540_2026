# Agents: the demo folders (ARCH 540, session 4)

These are the project folders used in the session notes, one folder per step. The notes are in this repository too: download it and open `agents_notes.html` in a browser (on GitHub it shows as code, not as a page). Every step changes one thing: the prompt, or a file in the folder. Open a step, run it, and compare what you get with the result in the notes.

## 0. Download

On the course repository page (https://github.com/GenEnv/Arch540_2026), click **Code**, then **Download ZIP**, and unzip it. This folder is `agents_demo/` inside it. Or, if you use git: `git clone https://github.com/GenEnv/Arch540_2026.git`, then `cd Arch540_2026/agents_demo`

## 1. Set up once

You need:

- **A Claude Pro, Max or Team account.** The free plan does not include Claude Code.
- **Claude Code.** In a terminal:
  - macOS or Linux: `curl -fsSL https://claude.ai/install.sh | bash`
  - Windows: use WSL (Windows Subsystem for Linux), then run the macOS/Linux command inside it. Demo C needs a Linux or macOS system.
  - Then open a new terminal and check: `claude --version`
  - Official guide: https://code.claude.com/docs/en/setup
- **Python 3 with four packages** (demos B, C and D; demo A needs only Python):

  ```
  python3 -m pip install -r requirements.txt
  ```

The first time you run `claude`, it opens a browser to log in.

## 2. Run one step

1. Open `PROMPTS.md` in the demo folder (for example `A_writing/PROMPTS.md`). It lists each step, the folder to use and the exact prompt.
2. Copy the step folder, so the original stays clean for the next run:

   ```
   cp -r A_writing/step2_counter ~/Desktop/try_step2
   cd ~/Desktop/try_step2
   claude
   ```

3. Paste the prompt. When Claude asks for permission to edit a file or run a command, read what it wants to do, then allow it.
4. When it has finished, look at what it made (the files in the folder) and at what it did (scroll up in the terminal).

To run the same step again, make a new copy. The same prompt gives different results each time; run it more than once before you draw a conclusion.

## 3. What is in a step folder

The files you would write yourself are plain text:

| File | What it is |
|---|---|
| `CLAUDE.md` | Memory: read at the start of every session in this folder |
| `.claude/skills/<name>/SKILL.md` | A written method (skill) |
| `.claude/agents/<name>.md` | A helper (subagent): its job, its tools, what it may see |
| `.claude/settings.json` | Settings, including hooks: scripts that run at fixed moments |
| `brief.md`, `rules.md`, `notes.md` | The task |

Folders starting with `.` are hidden. On a Mac, press Cmd + Shift + . in Finder to show them.

The `.py` files are small tools (a word counter, a rule checker, a scoring script). You do not need to read them. You can ask Claude to explain one, or to write one like it for your own project.

## 4. Which demos to run

| Demo | Time per run | Suggestion |
|---|---|---|
| A. Writing with a reviewer | under a minute | run every step |
| B. Site test-fit | about 3 to 10 minutes | run steps 2, 3 and 5 |
| C. Exploring a design space | 10 to 30 minutes | pick one step |
| D. A team of agents | 30 to 60 minutes, about 10 agents | read the recorded run in the notes first; runs can use up a Pro plan's 5-hour allowance |

Long runs count against your plan's usage limits. You can check how much you have used with `/usage` inside Claude Code.

## 5. Make it yours

The point of the demos is the files, not the prompts. Take a folder, change one file (a line in `CLAUDE.md`, a rule in a skill, what a reviewer may see) and run it again. Then try the same structure on a task from your own project.
