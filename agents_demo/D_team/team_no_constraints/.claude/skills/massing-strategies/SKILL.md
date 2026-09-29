---
name: massing-strategies
description: Massing strategies, the scheme file format and shadow rules of thumb for the corner block. Use when designing or revising a massing scheme.
---
# Massing strategies for the corner block

## Scheme file format (JSON, one scheme per file)
```
{"name": "short label", "strategy": "A_south_bar",
 "buildings": [ {"id": "S", "x0": 3, "y0": 3, "x1": 60, "y1": 21, "storeys": 9, "retail": true} ],
 "daycare": {"x0": 5, "y0": 30, "x1": 22, "y1": 46,
             "play": {"x0": 5, "y0": 10, "x1": 22, "y1": 28}},
 "courtyard": {"x0": 30, "y0": 25, "x1": 70, "y1": 50},
 "mix": {"studio": 15, "1b": 40, "2b": 30, "3b": 15}}
```
- Every volume is an axis-aligned rectangle in metres (x east 0 to 100, y north 0 to 70). Use only these keys.
- "storeys" counts the ground floor. Height = 4.5 + 3.1 x (storeys - 1).
- "retail": true only counts on a building whose south edge touches the south setback line (y0 = 3).
- The daycare is a one-storey building. Its play area, the courtyard and all buildings must not overlap.
- "mix" percentages add up to 100.

## Shadow rules of thumb (equinox, latitude 49.3 degrees, solar time)
- A building's shadow always reaches about 1.16 x its height straight north of its north edge, at every hour. Sideways it drifts west in the morning and east in the afternoon, by up to about 0.9 x height at 10:00 and 14:00.
- Park test: north edge y1 plus 1.16 x height must stay at or below 70 m (allowing the 5 m2 tolerance).
- Play-area sun: shadows fall north of buildings, so the play area is sunniest to the east or west of tall volumes, or north of low volumes. Around 3 hours of sun between 09:00 and 15:00 is the minimum.

## Strategies (each designer owns exactly one)
- A_south_bar: one deep bar on the south street, the daycare on its own on the east or west part of the site.
- B_corner_tower: low or medium bars, plus one tall volume inside the south-east corner zone to use the 55 m allowance.
- C_perimeter: bars on the south and east (and west) edges enclosing the courtyard, stepping down toward the park.
- D_stepped: several bars in steps, tallest at the south and lowest at the north, staggered so the play area is not shaded.
- E_split_bars: two parallel east-west bars with a wide gap (tower separation and sun in between). Not assigned by default.

## Method
1. Read the checklist. 2. Estimate floor area from footprints x storeys and check FSR and homes by hand
   (homes are about net area divided by 62 to 67 m2 per home, net = 82% of floor area minus retail).
3. Check every north edge against the park test. 4. Place the play area for sun, the courtyard away from the street.
5. Write the file. 6. Reply with three lines: what the idea is, your own expected weak point, anything in the checklist you disagree with.
