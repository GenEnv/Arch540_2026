#!/usr/bin/env python3
"""Rule checker for the site test-fit (the oracle of the session).

Usage:  python check.py layout.json [lot.json]
Prints pass/fail per rule, the offending buildings, total floor area (GFA).
Exit code 0 = all rules pass, 1 = at least one rule fails, 2 = bad input file.

Layout file: {"buildings": [{"id": "A", "type": "tower|slab|short",
              "x": 10, "y": 10, "storeys": 8, "rotated": false}, ...]}
(x, y) is the south-west corner of the footprint. rotated=true swaps width and depth.
"""
import json, sys, os, itertools
from shapely.geometry import Polygon, box
from shapely.ops import unary_union

TYPES = {  # width (x), depth (y), min storeys, max storeys
    "tower": (18.0, 18.0, 8, 12),
    "slab": (40.0, 12.0, 4, 8),
    "short": (24.0, 12.0, 4, 8),
}
STOREY_H = 3.2
SETBACK = 3.0
SUN_FACTOR = 0.7
MIN_GAP = 12.0
MAX_H = 40.0
MIN_OPEN = 0.25
EPS = 1e-6


class BadInput(Exception):
    pass


def load_lot(path):
    with open(path) as f:
        return Polygon(json.load(f)["polygon"])


def parse_layout(data):
    try:
        raw = data["buildings"]
        out = []
        for i, b in enumerate(raw):
            t = b["type"]
            if t not in TYPES:
                raise BadInput(f"building {i}: unknown type '{t}' (use tower, slab or short)")
            w, d, _, _ = TYPES[t]
            if b.get("rotated", False):
                w, d = d, w
            x, y = float(b["x"]), float(b["y"])
            n = int(b["storeys"])
            out.append({"id": str(b.get("id", i)), "type": t, "x": x, "y": y, "n": n,
                        "h": n * STOREY_H, "box": box(x, y, x + w, y + d)})
        return out
    except KeyError as e:
        raise BadInput(f"missing field {e}")


def check(bs, lot):
    """Return (results, gfa). results = list of (rule, title, ok, [messages])."""
    res = []
    inner = lot.buffer(-SETBACK, join_style=2)
    # R1 setback
    msgs = [f"{b['id']} ({b['type']}) is closer than {SETBACK:g} m to the boundary or outside the lot"
            for b in bs if not inner.buffer(EPS).contains(b["box"])]
    res.append(("R1", f"{SETBACK:g} m setback from the boundary", not msgs, msgs))
    # R2 sun gap
    msgs = []
    for a, b in itertools.permutations(bs, 2):  # a is south, b is north
        ax0, ay0, ax1, ay1 = a["box"].bounds
        bx0, by0, bx1, by1 = b["box"].bounds
        x_overlap = min(ax1, bx1) - max(ax0, bx0)
        if x_overlap > EPS and by0 >= ay1 - EPS:
            gap = by0 - ay1
            need = SUN_FACTOR * a["h"]
            if gap < need - EPS:
                msgs.append(f"{b['id']} is north of {a['id']} with gap {gap:.1f} m, needs {need:.1f} m "
                            f"(0.7 x {a['h']:.1f} m)")
    res.append(("R2", "north-south gap >= 0.7 x height of the southern building", not msgs, msgs))
    # R3 min distance
    msgs = []
    for a, b in itertools.combinations(bs, 2):
        d = a["box"].distance(b["box"])
        if d < MIN_GAP - EPS:
            msgs.append(f"{a['id']} and {b['id']} are {d:.1f} m apart, need {MIN_GAP:g} m")
    res.append(("R3", f"any two buildings >= {MIN_GAP:g} m apart", not msgs, msgs))
    # R4 height and storey range
    msgs = []
    for b in bs:
        _, _, lo, hi = TYPES[b["type"]]
        if b["h"] > MAX_H + EPS:
            msgs.append(f"{b['id']} is {b['h']:.1f} m high, limit {MAX_H:g} m")
        if not (lo <= b["n"] <= hi):
            msgs.append(f"{b['id']} ({b['type']}) has {b['n']} storeys, allowed {lo}-{hi}")
    res.append(("R4", f"height <= {MAX_H:g} m and storeys within the type's range", not msgs, msgs))
    # R5 open space
    cover = unary_union([b["box"] for b in bs]).area if bs else 0.0
    open_frac = 1 - cover / lot.area
    ok = open_frac >= MIN_OPEN - EPS
    msgs = [] if ok else [f"open space is {open_frac*100:.1f} %, need {MIN_OPEN*100:g} %"]
    res.append(("R5", f">= {MIN_OPEN*100:g} % of the lot left open", ok, msgs))
    gfa = sum(b["box"].area * b["n"] for b in bs)
    return res, gfa, open_frac


def run(layout_path, lot_path=None, quiet=False):
    lot_path = lot_path or os.path.join(os.path.dirname(os.path.abspath(__file__)), "lot.json")
    lot = load_lot(lot_path)
    try:
        with open(layout_path) as f:
            data = json.load(f)
        bs = parse_layout(data)
    except (OSError, ValueError, BadInput, TypeError) as e:
        if not quiet:
            print(f"BAD INPUT: {e}")
        return 2, None
    res, gfa, open_frac = check(bs, lot)
    ok = all(r[2] for r in res)
    if not quiet:
        for rule, title, passed, msgs in res:
            print(f"{rule} {'PASS' if passed else 'FAIL'}  {title}")
            for m in msgs:
                print(f"     - {m}")
        print(f"Buildings: {len(bs)}   Total floor area (GFA): {gfa:,.0f} m2   Open space: {open_frac*100:.1f} %")
        print("RESULT: " + ("ALL RULES PASS" if ok else "RULES BROKEN: " + ", ".join(r[0] for r in res if not r[2])))
    return (0 if ok else 1), {"ok": ok, "gfa": gfa, "open": open_frac,
                              "failed": [r[0] for r in res if not r[2]], "n": len(bs)}


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print(__doc__)
        sys.exit(2)
    code, _ = run(sys.argv[1], sys.argv[2] if len(sys.argv) > 2 else None)
    sys.exit(code)
