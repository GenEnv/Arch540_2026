---
name: massing-strategies
description: A library of building massing strategies and a method for exploring them on the housing lot. Use whenever you are asked to explore, compare or improve massing options, trade-offs between floor area, sun and shape, or to find where the set of designs is thin.
---

# Massing strategies and how to use them

Do not stay inside one family. A family is a way of building a massing from a few parameters. Changing the parameters of one family only moves you along one curve. Adding a new family opens a new region of results.

## The families (name them exactly like this in the "family" field)
1. `rows`: parallel bars. Parameters: count, bar depth, spacing (at least 6 m), storeys per bar, orientation (east-west or north-south).
2. `courtyard`: bars around an open court (perimeter block). Parameters: outer size, bar depth, which sides are built, storeys per side. A court open to the south lets low sun in.
3. `north_high_south_low`: heights step up towards the north edge so shadows fall on the back of the lot. Parameters: number of steps, storeys of the lowest and highest bar, depth per step.
4. `point_towers`: separate square or slim towers on a loose grid. Parameters: tower count, footprint, storeys, positions (keep them in the north and east, away from the sunny south-west).
5. `terraced`: one building whose storeys step down in a staircase, from the north wall to the south wall, or from the middle to both sides. Parameters: steps, storeys at each step (touching boxes).
6. `podium_tower`: a low wide podium (2 to 4 storeys) with one or two towers on top or beside it. Parameters: podium size, tower footprint, tower storeys, tower position.

Mixtures of two families are allowed. Give a mixture its own family name.

## Method
1. Round 1: write at least one generator per family above, 8 to 15 variants each, spread across the parameter range. Evaluate.
2. After every round, read `tools/front.py`. Ask three questions in numbers:
   - Which families have zero points on the front? Look at the per-family table.
   - Where is the front thin? Use the "best GFA that still has at least S sun hours" table and the largest gaps list. A flat step or a large gap is an empty region.
   - Which front points are near-duplicates? Do not spend evaluations there.
3. Next round: aim designs at the largest gap. Choose or invent the family that could plausibly reach that region, and set its parameters to target the empty midpoint given in the gaps list. If no family fits, invent a new one (a new way of placing boxes) and name it.
4. Stop when two rounds in a row do not improve the front, or when a limit is reached.
5. Report: the best design per family, the families that reached the front, and the empty regions that remain.
