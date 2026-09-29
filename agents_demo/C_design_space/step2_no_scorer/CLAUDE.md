# Housing site study, Vancouver

Site: a flat residential lot, 80 m wide (east-west) by 60 m deep (north-south) at latitude 49.25 N. The street is on the south edge.
A massing is a set of boxes: each box has a footprint rectangle and a number of storeys (3.2 m each).

## Hard limits
- 3 m setback: every box stays at least 3 m inside the lot edge.
- Height limit 45 m, so 1 to 14 storeys.
- Buildings must be at least 6 m apart. Boxes that touch or overlap count as one building.
- Every box at least 6 m by 6 m. At most 60 boxes per design.
- Daylight depth: no part of a building may be more than 9 m from an outside wall or courtyard. In plain terms, bars are at most about 18 m wide, and touching boxes may not be joined into a deeper block.
- The programme needs at least 8,000 m2 of gross floor area. A design below that is not scored.

## The three goals
1. Gross floor area (GFA, m2): more is better.
2. Winter sun: average hours of direct sun on the open ground (ground not under a building) on the winter solstice, 9:00 to 15:00 solar time. The ground counted is the lot plus a 15 m ring around it (the street and the neighbours), so shadows that fall off the lot still cost you. Maximum possible 6.0. More is better.
3. Shape factor (SF): outside wall and roof area divided by volume. Lower is better (a compact building loses less heat).
These pull against each other. A set of designs where no other design is better on all three is called the front (the Pareto front).

## Tools in this project
- `tools/evaluate.py` measures designs. It is the only source of numbers you may trust. It is provided; you do not change it.
- `tools/front.py` prints the current front and where it is thin, as numbers.
- Write your own small scripts in `work/`. Save designs in `work/`.
- Run Python as `python3`.

## Design file format
A JSON list. Coordinates in metres (x east 0..80, y north 0..60), rounded to whole metres.
```
[{"id": "rows_3_h6", "family": "rows", "params": {"count": 3},
  "boxes": [{"x0": 5, "y0": 5, "x1": 75, "y1": 17, "storeys": 6}]}]
```
`family` names the type of massing (use the same name for designs made the same way).
Run: `python3 tools/evaluate.py work/designs_round1.json`
Each call is one round. Results are appended to `results/evals.jsonl`. After a round, run `python3 tools/front.py` to read the front table, the gaps and the per-family counts. Work from these numbers. You cannot see pictures.

## Note for this job
There is no `tools/` folder in this project: nothing here can measure a design. Ignore the "Tools in this project" section above.
