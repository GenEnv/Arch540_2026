# Site test-fit brief

A developer wants a residential test-fit on the lot in `lot.json`. The street runs along the south edge of the lot (the edge that starts at 0,0). North is up. All numbers are in metres. The plan is 2D only.

## Buildings you can use (as many of each as you like)
| Type | Footprint (east-west x north-south) | Storeys |
|---|---|---|
| tower | 18 x 18 | 8 to 12 |
| slab | 40 x 12 | 4 to 8 |
| short | 24 x 12 | 4 to 8 |

Storey height is 3.2 m. Buildings are rectangles. They may be turned a quarter turn (east-west and north-south swapped) but not any other angle.

## Goal
As much total floor area as the rules allow. Floor area of one building = footprint area x storeys. Total = sum over all buildings.

## What to deliver
- `output/layout.json`: your final layout (see `layout_format.md`).
- `output/plan.png`: a drawing of the plan (lot outline, setback line, every building labelled with type and storeys, the street side marked, total floor area written on the sheet).
- A short report in your final message: the total floor area, and which rule stopped you from adding more.

## Environment
Run Python with `python3` (it already has numpy, shapely and matplotlib). Do not install anything.
