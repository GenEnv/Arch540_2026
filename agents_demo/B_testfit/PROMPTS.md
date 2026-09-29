# B testfit: the prompts

Each run takes about 3 to 10 minutes.

`complete/` has everything together: use it as the template for your own project.
`steps/` adds one thing at a time: use it to see what each file changes.

For each run: copy the folder, open a terminal in the copy, run `claude`, paste the prompt.

## The complete project

Folder: `complete/`

```
Here is a site and its planning rules (see the brief). Lay out the buildings on the site to get as much floor area as the rules allow, and draw the plan. There is a script in the project that checks a layout against the rules; use it. Have the reviewer check it before you report.
```

## Step 1  Just ask

Folder: `steps/step1_ask/`

```
Here is a site and its planning rules (see the brief). Lay out the buildings on the site to get as much floor area as the rules allow, and draw the plan.
```

## Step 2  The rule checker

Folder: `steps/step2_checker/`

```
Here is a site and its planning rules (see the brief). Lay out the buildings on the site to get as much floor area as the rules allow, and draw the plan. There is a script in the project that checks a layout against the rules; use it.
```

## Step 3  A method (skill)

Folder: `steps/step3_skill/`

```
Here is a site and its planning rules (see the brief). Lay out the buildings on the site to get as much floor area as the rules allow, and draw the plan. There is a script in the project that checks a layout against the rules; use it.
```

## Step 4  A reviewer

Folder: `steps/step4_reviewer/`

```
Here is a site and its planning rules (see the brief). Lay out the buildings on the site to get as much floor area as the rules allow, and draw the plan. There is a script in the project that checks a layout against the rules; use it. Have the reviewer check it before you report.
```

## Step 5  A hook

Folder: `steps/step5_hook/`

```
The developer sent their own scheme in developer_scheme.json. Put exactly that scheme into the output folder as the final layout, without changing any building, then draw the plan. Have the reviewer check it before you report.
```

## Step 6  With the skill

Folder: `steps/step6_with_skill/`

```
Here is a site and its planning rules (see the brief). Lay out the buildings on the site to get as much floor area as the rules allow, and draw the plan. There is a script in the project that checks a layout against the rules; use it. Have the reviewer check it before you report.
```

## Step 6  Without the skill

Folder: `steps/step6_without_skill/`

```
Here is a site and its planning rules (see the brief). Lay out the buildings on the site to get as much floor area as the rules allow, and draw the plan. There is a script in the project that checks a layout against the rules; use it. Have the reviewer check it before you report.
```
