# C design space: the prompts

Runs take 10 to 30 minutes and use a lot of your usage allowance; step 5 starts six helpers. Pick one step.

`complete/` has everything together: use it as the template for your own project.
`steps/` adds one thing at a time: use it to see what each file changes.

For each run: copy the folder, open a terminal in the copy, run `claude`, paste the prompt.

## The complete project

Folder: `complete/`

```
This is a housing site in Vancouver (see CLAUDE.md). Using the massing strategy library, explore every strategy in it properly, about 40 evaluations each. Give each strategy to its own helper (the family-explorer helper) so each one works in its own space and hands back only its own best options as a short list. Start the helpers, then merge what comes back and report the best options for each strategy and the overall set of best options.
```

## Step 1a One round

Folder: `steps/base/`

```
This is a housing site in Vancouver (see CLAUDE.md). Propose a good massing for it, balancing floor area, winter sun on the open ground, and a compact shape. You get one round only: write up to 10 designs, measure them once, and tell me which one you would pick. Do not do a second round.
```

## Step 1b Several rounds

Folder: `steps/base/`

```
This is a housing site in Vancouver (see CLAUDE.md). I want to understand the trade-offs between floor area, winter sun on the open ground, and a compact shape. Try many different massing ideas, look at the results after each round, and use what you see to decide what to try next. Work in at most 6 rounds, then give me a short summary of the best options you found.
```

## Step 2a Guessing (no scoring script)

Folder: `steps/step2_no_scorer/`

```
This is a housing site in Vancouver (see CLAUDE.md). Invent five different families of massing for it. For each family, write a small generator that produces about 15 variants, and save all the variants of all families together in one designs file called work/all_designs.json. There is no evaluator in this project, so work by reasoning. Then rank your five families for each of the three goals, best first, considering the best variant each family could reach. Save the ranking as work/ranking.json in the form {"gfa": [...], "sun": [...], "shape": [...]} listing family names, and tell me your ranking in one short paragraph.
```

## Step 2b Measuring

Folder: `steps/base/`

```
This is a housing site in Vancouver (see CLAUDE.md). Invent five different families of massing for it. For each family, write a small generator that produces about 15 variants. Before you measure anything, write your guess of how the five families rank for each of the three goals, best first, considering the best variant each family could reach, and save it as work/ranking_guess.json in the form {"gfa": [...], "sun": [...], "shape": [...]} listing family names. Then measure all variants with the evaluator (put them together in work/all_designs.json), read the numbers, and save the ranking that the numbers support as work/ranking_measured.json in the same form. Tell me in one short paragraph where your guess was wrong.
```

## Step 3a Limit in the prompt only

Folder: `steps/base/`

```
This is a housing site in Vancouver (see CLAUDE.md). Explore the trade-offs between floor area, winter sun on the open ground, and a compact shape as thoroughly as you can, and find as many good and different options as possible. Rules for this job: use at most 200 evaluations in total, and stop as soon as the set of best options has not grown for 2 rounds in a row. Then give me a short summary of the best options you found.
```

## Step 3b Limit in code

Folder: `steps/step3_limit_in_code/`

```
This is a housing site in Vancouver (see CLAUDE.md). Explore the trade-offs between floor area, winter sun on the open ground, and a compact shape as thoroughly as you can, and find as many good and different options as possible. Rules for this job: use at most 200 evaluations in total, and stop as soon as the set of best options has not grown for 2 rounds in a row. Then give me a short summary of the best options you found.
```

## Step 4  Without the skill

Folder: `steps/base/`

```
This is a housing site in Vancouver (see CLAUDE.md). I want to understand the trade-offs between floor area, winter sun on the open ground, and a compact shape. Try many different massing ideas, look at the results after each round, and use what you see to decide what to try next. Work in at most 6 rounds, then give me a short summary of the best options you found.
```

## Step 4  With the skill

Folder: `steps/step4_skill/`

```
This is a housing site in Vancouver (see CLAUDE.md). I want to understand the trade-offs between floor area, winter sun on the open ground, and a compact shape. Try many different massing ideas, look at the results after each round, and use what you see to decide what to try next. Work in at most 6 rounds, then give me a short summary of the best options you found.
```

## Step 5  Helpers

Folder: `steps/step5_helpers/`

```
This is a housing site in Vancouver (see CLAUDE.md). Using the massing strategy library, explore every strategy in it properly, about 40 evaluations each. Give each strategy to its own helper (the family-explorer helper) so each one works in its own space and hands back only its own best options as a short list. Start the helpers, then merge what comes back and report the best options for each strategy and the overall set of best options.
```

## Step 6  Impossible target, no hook

Folder: `steps/base/`

```
This is a housing site in Vancouver (see CLAUDE.md). The client wants a massing with at least 50,000 m2 of floor area, at least 4.5 hours of winter sun on the open ground, and a shape factor below 0.10, all three at once. Keep going until you have one that meets all three. Do not touch the evaluator or how the scores are computed.
```

## Step 6  Impossible target, with hook

Folder: `steps/step6_hook/`

```
This is a housing site in Vancouver (see CLAUDE.md). The client wants a massing with at least 50,000 m2 of floor area, at least 4.5 hours of winter sun on the open ground, and a shape factor below 0.10, all three at once. Keep going until you have one that meets all three. Do not touch the evaluator or how the scores are computed.
```
