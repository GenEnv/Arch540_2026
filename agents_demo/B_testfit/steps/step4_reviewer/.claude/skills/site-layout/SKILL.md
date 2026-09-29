---
name: site-layout
description: How a designer approaches a site test-fit (massing buildings on a lot under planning rules to get maximum floor area). Use whenever asked to lay out buildings on a site, do a test-fit, or maximise floor area under setback, spacing and sun-gap rules.
---

# Site test-fit method

A test-fit is not one drawing. It is a comparison of several organising ideas on the same lot. Work like this.

## 1. Read the rules first
Write down, in two lines each, what the rules do to the scheme before you place anything.
- Low buildings are limited mostly by the 12 m spacing.
- Tall buildings behind each other are limited by the sun gap (0.7 x height of the southern one), so tall and deep rows cost a lot of land.
- The setback and the odd lot outline cut the usable area. Draw the inner (setback) line first.

## 2. Choose an organising logic, then set out its lines
Before placing a building, decide the lines it hangs on (row lines, a court edge, a spine axis, the setback line) and say them in one sentence. Use these strategies. Try all of them; each suits a different reading of the lot.
- **Rows**: parallel slabs, east-west, stacked from the street northwards. Use when the lot is wide. Storeys can step up towards the north so the sun gap stays small.
- **Courtyard**: slabs and short slabs around a central open court, open to the south. Use when you want one strong shared space.
- **Towers on a low base**: one or two low slabs along the street, towers set behind them, staggered so their east-west extents do not overlap. Use when height is worth its sun gap.
- **Spine**: a central open strip running north-south, slabs turned a quarter turn (north-south) on both sides. Use when the lot is deep.
- **Perimeter**: buildings hugging the setback line around the edge, leaving the middle open. Use when the outline is awkward.
- **Tower field**: towers only, staggered so no two overlap in east-west extent. Use to see what pure height gives.

## 3. Exhaust the variants
For each strategy make at least three variants (change the count, the storeys, the offset, the orientation, which types you use). Save every scheme as its own layout file in `work/schemes/`, named `<strategy>_<number>`. Check each one with the checker. Keep the ones that pass, and note the floor area of each.

## 4. Check after every change
Run the checker on every scheme you save. Never say a scheme follows the rules unless the checker said so. If a scheme fails, fix it or drop it. Never change a rule, a building size or a storey range to make a scheme pass.

## 5. Deliver and report
- Put the best passing scheme in `output/layout.json` and draw it in `output/plan.png`.
- Draw `output/gallery.png`: all your passing schemes as small plans side by side, each titled with strategy name and floor area.
- Report a table: strategy, best floor area, which rule limited it, one phrase on how it looks. Say which strategy won and why.
- If no scheme passes, do not deliver a layout. Say UNRESOLVED and list what you tried.
