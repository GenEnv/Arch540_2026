# Agents: demo folders (ARCH 540, session 4)

Open `agents_notes.html` in a browser for the notes. Each demo folder has:

- `complete/`: the whole project. Copy it as the template for your own project.
- `steps/`: the same project, one piece at a time, to see what each piece changes.
- `PROMPTS.md`: which folder to use and what to type.

## Run one

Once: `python3 -m pip install -r requirements.txt` (demos B, C, D).

```
cp -r A_writing/complete ~/Desktop/try
cd ~/Desktop/try
claude
```

Paste the prompt from `PROMPTS.md`. Work in a copy, so the original stays clean.

## How long

A: under a minute. B: 3 to 10 minutes. C: 10 to 30 minutes. D: 30 to 60 minutes and about 10 agents; read its run in the notes first. Long runs use a lot of your plan's allowance (`/usage` shows how much).
