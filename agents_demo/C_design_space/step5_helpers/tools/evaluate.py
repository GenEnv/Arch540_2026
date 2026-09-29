#!/usr/bin/env python
"""Massing evaluator for the Vancouver lot. Part of the protected harness: do not edit.

Usage:  python tools/evaluate.py designs.json

A designs file is a JSON list. Each design:
  {"id": "rows_3_4", "family": "rows", "params": {...optional...},
   "boxes": [{"x0": 5, "y0": 5, "x1": 75, "y1": 15, "storeys": 4}, ...]}
x runs east 0..80, y runs north 0..60, the street is on the south edge (y=0).
Coordinates are rounded to whole metres. One storey = 3.2 m.

Hard limits (a design that breaks one is not scored):
  * every box at least 3 m inside the lot edge (setback)
  * every box at least 6 m wide and 6 m deep
  * 1 to 14 storeys (14 x 3.2 = 44.8 m, limit 45 m)
  * boxes that do not touch or overlap must be at least 6 m apart
  * at most 60 boxes per design
  * gross floor area at least 8,000 m2 (the housing programme)
  * daylight depth: no point of the plan more than 9 m from an outside wall or courtyard
    (in practice: bars at most 18 m wide, however boxes are joined)
Objectives (all computed here):
  gfa  gross floor area, m2, maximise
  sun  average winter-solstice sun hours on open ground (not under a building),
       counting the lot plus a 15 m ring of neighbouring ground (street and neighbours),
       9:00-15:00 solar time, latitude 49.25 N, maximise (max 6.0)
  sf   shape factor = envelope area / volume, 1/m, minimise
       (envelope = roofs + walls, ground contact excluded)
"""
import json
import os
import sys
import time
import fcntl
import numpy as np
from scipy import ndimage

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import frontlib as fl  # noqa: E402

ROOT = os.path.dirname(HERE)
LOT_W, LOT_D = 80, 60
SETBACK = 3
MIN_SIDE = 6
MIN_GAP = 6.0
STOREY_H = 3.2
MARGIN = 15  # metres of neighbouring open ground (street and neighbours) counted around the lot
MAX_STOREYS = 14
MAX_BOXES = 60
MIN_GFA = 8000  # programme minimum, m2
MAX_DEPTH_R = 9  # daylight depth: no point of a building further than 9 m from an outside face (18 m wide plan)
LAT = 49.25
DECL = -23.44  # winter solstice
HOURS = [9, 10, 11, 12, 13, 14, 15]
WEIGHTS = np.array([0.5, 1, 1, 1, 1, 1, 0.5])  # trapezoid, total 6 h


# ---------------------------------------------------------------- geometry
def sun_vectors(lat=LAT, decl=DECL, hours=HOURS):
    """Unit vectors pointing TO the sun, (east, north, up), one per hour (solar time)."""
    phi, dl = np.radians(lat), np.radians(decl)
    out = []
    for t in hours:
        H = np.radians(15.0 * (t - 12))
        east = -np.cos(dl) * np.sin(H)
        north = np.sin(dl) * np.cos(phi) - np.cos(dl) * np.sin(phi) * np.cos(H)
        up = np.sin(phi) * np.sin(dl) + np.cos(phi) * np.cos(dl) * np.cos(H)
        out.append((east, north, up))
    return np.array(out)


def altitude_deg(v):
    return float(np.degrees(np.arcsin(v[2])))


def round_boxes(boxes):
    return [(int(round(b["x0"])), int(round(b["y0"])), int(round(b["x1"])),
             int(round(b["y1"])), int(b["storeys"])) for b in boxes]


def check_limits(boxes):
    """boxes: rounded tuples. Returns list of violation strings."""
    v = []
    if not boxes:
        return ["no boxes"]
    if len(boxes) > MAX_BOXES:
        v.append(f"more than {MAX_BOXES} boxes")
    for i, (x0, y0, x1, y1, s) in enumerate(boxes):
        if x1 <= x0 or y1 <= y0:
            v.append(f"box {i} has no area")
            continue
        if x0 < SETBACK or y0 < SETBACK or x1 > LOT_W - SETBACK or y1 > LOT_D - SETBACK:
            v.append(f"box {i} breaks the {SETBACK} m setback")
        if (x1 - x0) < MIN_SIDE or (y1 - y0) < MIN_SIDE:
            v.append(f"box {i} is thinner than {MIN_SIDE} m")
        if s < 1 or s > MAX_STOREYS:
            v.append(f"box {i} has {s} storeys (allowed 1-{MAX_STOREYS})")
    for i in range(len(boxes)):
        for j in range(i + 1, len(boxes)):
            a, b = boxes[i], boxes[j]
            dx = max(b[0] - a[2], a[0] - b[2], 0)
            dy = max(b[1] - a[3], a[1] - b[3], 0)
            d = (dx * dx + dy * dy) ** 0.5
            if 0 < d < MIN_GAP:
                v.append(f"boxes {i} and {j} are {d:.1f} m apart (need {MIN_GAP:g} or touching)")
    return v[:6]


def heightfield(boxes):
    """(LOT_W, LOT_D) array of storeys per 1 m cell; cell [i,j] covers x i..i+1, y j..j+1."""
    hf = np.zeros((LOT_W, LOT_D), int)
    for x0, y0, x1, y1, s in boxes:
        sub = hf[max(x0, 0):min(x1, LOT_W), max(y0, 0):min(y1, LOT_D)]
        np.maximum(sub, s, out=sub)
    return hf


def sun_map(boxes, hf=None, vecs=None):
    """Sun hours (0..6) for each ground cell of the lot plus a MARGIN-wide ring of neighbouring
    ground. Shape (LOT_W+2*MARGIN, LOT_D+2*MARGIN); NaN where covered by a building.
    Cell [i,j] covers x = i-MARGIN .. i-MARGIN+1, y = j-MARGIN .. j-MARGIN+1."""
    hf = heightfield(boxes) if hf is None else hf
    vecs = sun_vectors() if vecs is None else vecs
    M = MARGIN
    full = np.zeros((LOT_W + 2 * M, LOT_D + 2 * M), int)
    full[M:M + LOT_W, M:M + LOT_D] = hf
    ii, jj = np.meshgrid(np.arange(full.shape[0]) - M + 0.5, np.arange(full.shape[1]) - M + 0.5, indexing="ij")
    open_mask = full == 0
    ox, oy = ii[open_mask], jj[open_mask]
    oz = 0.05
    hours = np.zeros(ox.shape)
    for k, (dx, dy, dz) in enumerate(vecs):
        if dz <= 0:
            continue
        dx = dx if abs(dx) > 1e-12 else 1e-12
        dy = dy if abs(dy) > 1e-12 else 1e-12
        shaded = np.zeros(ox.shape, bool)
        for x0, y0, x1, y1, s in boxes:
            H = s * STOREY_H
            t1 = (x0 - ox) / dx
            t2 = (x1 - ox) / dx
            tx0, tx1 = np.minimum(t1, t2), np.maximum(t1, t2)
            t1 = (y0 - oy) / dy
            t2 = (y1 - oy) / dy
            ty0, ty1 = np.minimum(t1, t2), np.maximum(t1, t2)
            tz0, tz1 = (0 - oz) / dz, (H - oz) / dz
            t_in = np.maximum(np.maximum(tx0, ty0), tz0)
            t_out = np.minimum(np.minimum(tx1, ty1), tz1)
            shaded |= t_out > np.maximum(t_in, 0.0)
        hours[~shaded] += WEIGHTS[k]
    out = np.full(full.shape, np.nan)
    out[open_mask] = hours
    return out


def envelope_and_volume(hf):
    h = hf.astype(float)
    roof = float((h > 0).sum())
    pad = np.pad(h, 1)
    walls = 0.0
    for a, b in ((pad[1:-1, 1:-1], pad[2:, 1:-1]), (pad[1:-1, 1:-1], pad[:-2, 1:-1]),
                 (pad[1:-1, 1:-1], pad[1:-1, 2:]), (pad[1:-1, 1:-1], pad[1:-1, :-2])):
        walls += float(np.maximum(a - b, 0).sum()) * STOREY_H
    volume = float(h.sum()) * STOREY_H
    return roof + walls, volume


def score_boxes(boxes):
    """Pure scoring of rounded box tuples (no limit checks, no counting)."""
    hf = heightfield(boxes)
    sm = sun_map(boxes, hf)
    open_vals = sm[~np.isnan(sm)]
    sun = float(open_vals.mean()) if len(open_vals) else 0.0
    env, vol = envelope_and_volume(hf)
    gfa = float(hf.sum())
    return {"gfa": gfa, "sun": sun, "sf": env / vol if vol > 0 else 9.9,
            "max_height_m": float(hf.max() * STOREY_H),
            "coverage": float((hf > 0).mean())}


# ------------------------------------------------------------ counted layer
def _limits():
    p = os.path.join(HERE, "limits.json")
    d = {"max_evals": 10 ** 9, "stall_rounds": 0}
    if os.path.exists(p):
        d.update(json.load(open(p)))
    return d


def _load_evals(path):
    out = []
    if os.path.exists(path):
        for line in open(path):
            line = line.strip()
            if line:
                out.append(json.loads(line))
    return out


def _hv_of(rows):
    G = [fl.goodness(r["gfa"], r["sun"], r["sf"]) for r in rows if r.get("valid")]
    return fl.hypervolume(np.array(G)) if G else 0.0


def main(argv):
    if len(argv) < 2:
        print(__doc__)
        return 2
    results = os.path.join(ROOT, "results")
    state_dir = os.path.join(ROOT, ".state")
    os.makedirs(results, exist_ok=True)
    os.makedirs(state_dir, exist_ok=True)
    lim = _limits()
    lockf = open(os.path.join(state_dir, "lock"), "w")
    fcntl.flock(lockf, fcntl.LOCK_EX)
    spath = os.path.join(state_dir, "counter.json")
    st = json.load(open(spath)) if os.path.exists(spath) else {
        "evals": 0, "rounds": 0, "best_hv": 0.0, "stall": 0}
    epath = os.path.join(results, "evals.jsonl")
    lpath = os.path.join(results, "eval_log.jsonl")

    designs = json.load(open(argv[1]))
    if isinstance(designs, dict):
        designs = designs.get("designs", [designs])

    def log(entry):
        entry["t"] = time.strftime("%H:%M:%S")
        with open(lpath, "a") as f:
            f.write(json.dumps(entry) + "\n")

    # harness-side refusals
    if st["evals"] >= lim["max_evals"]:
        msg = f"REFUSED: evaluation budget of {lim['max_evals']} is used up ({st['evals']} done). Stop and report."
        log({"event": "refused", "reason": "budget", "asked": len(designs), "evals": st["evals"]})
        print(msg)
        return 3
    if lim["stall_rounds"] and st["stall"] >= lim["stall_rounds"]:
        msg = (f"REFUSED: the front has not expanded for {st['stall']} rounds in a row. "
               f"Stop and report.")
        log({"event": "refused", "reason": "stall", "asked": len(designs), "evals": st["evals"]})
        print(msg)
        return 3
    remaining = lim["max_evals"] - st["evals"]
    cut = 0
    if len(designs) > remaining:
        cut = len(designs) - remaining
        designs = designs[:remaining]

    prior = _load_evals(epath)
    hv_before = _hv_of(prior)
    rnd = st["rounds"] + 1
    rows = []
    for d in designs:
        st["evals"] += 1
        bx = round_boxes(d.get("boxes", []))
        viol = check_limits(bx)
        row = {"eval": st["evals"], "round": rnd, "id": d.get("id", f"d{st['evals']}"),
               "family": d.get("family", "unnamed"), "params": d.get("params", {}),
               "boxes": [list(b) for b in bx], "valid": not viol, "violations": viol}
        if not viol:
            row.update(score_boxes(bx))
            occ = heightfield(bx) > 0
            depth = float(ndimage.distance_transform_edt(np.pad(occ, 1)).max())
            row["plan_depth_r"] = depth
            if depth > MAX_DEPTH_R:
                row["valid"] = False
                row["violations"] = [f"plan too deep: a point is {depth:.0f} m from the nearest outside wall (limit {MAX_DEPTH_R} m, so about 18 m wide bars)"]
            elif row["gfa"] < MIN_GFA:
                row["valid"] = False
                row["violations"] = [f"gross floor area {row['gfa']:.0f} m2 is below the programme minimum of {MIN_GFA} m2"]
        rows.append(row)
    with open(epath, "a") as f:
        for r in rows:
            f.write(json.dumps(r) + "\n")
    allrows = prior + rows
    hv_after = _hv_of(allrows)
    expanded = hv_after > st["best_hv"] * (1 + 1e-4) + 1e-9
    st["stall"] = 0 if expanded else st["stall"] + 1
    st["best_hv"] = max(st["best_hv"], hv_after)
    st["rounds"] = rnd
    json.dump(st, open(spath, "w"))

    valid = [r for r in rows if r["valid"]]
    G = np.array([fl.goodness(r["gfa"], r["sun"], r["sf"]) for r in allrows if r["valid"]])
    fam_of = [r["family"] for r in allrows if r["valid"]]
    front_fams = {}
    if len(G):
        for m, f in zip(fl.pareto_mask(G), fam_of):
            if m:
                front_fams[f] = front_fams.get(f, 0) + 1
    log({"event": "round", "round": rnd, "n": len(rows), "valid": len(valid), "evals": st["evals"],
         "hv": round(hv_after, 5), "hv_before": round(hv_before, 5), "expanded": bool(expanded),
         "stall": st["stall"], "front_size": int(sum(front_fams.values())),
         "front_families": front_fams})

    print(f"round {rnd}: {len(rows)} designs sent, {len(valid)} valid, {len(rows) - len(valid)} broke a limit")
    if len(rows) <= 12:
        for r in rows:
            if r["valid"]:
                print(f"  {r['id']:<28} {r['family']:<14} gfa {r['gfa']:8.0f}  sun {r['sun']:4.2f} h  sf {r['sf']:5.3f}")
            else:
                print(f"  {r['id']:<28} {r['family']:<14} INVALID: {'; '.join(r['violations'][:2])}")
    else:
        fams = {}
        for r in rows:
            fams.setdefault(r["family"], []).append(r)
        for f, rs in fams.items():
            v = [r for r in rs if r["valid"]]
            if v:
                print(f"  {f:<16} n={len(rs):<4} valid={len(v):<4} best gfa {max(r['gfa'] for r in v):8.0f}"
                      f"  best sun {max(r['sun'] for r in v):4.2f}  best sf {min(r['sf'] for r in v):5.3f}")
            else:
                print(f"  {f:<16} n={len(rs):<4} valid=0 (e.g. {rs[0]['violations'][:1]})")
    print(f"front now: {sum(front_fams.values())} points, families on front: {front_fams}")
    print(f"hypervolume {hv_before:.4f} -> {hv_after:.4f} "
          f"({'front expanded' if expanded else 'front did NOT expand'}; rounds without expansion: {st['stall']})")
    left = "unlimited" if lim["max_evals"] >= 10 ** 9 else str(lim["max_evals"] - st["evals"])
    print(f"evaluations used {st['evals']}, remaining {left}")
    if cut:
        print(f"NOTE: {cut} designs were NOT evaluated because the budget ran out.")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
