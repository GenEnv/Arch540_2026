"""Evaluation engine for the mixed-use block. Site frame: x = east, y = north, metres.
South street is below y=0, east street is right of x=100, the park is north of y=70."""
import math
from shapely.geometry import box, MultiPoint
from shapely.ops import unary_union
from shapely import affinity

LAT = 49.28  # degrees north, equinox (declination 0), solar time
SITE = box(0, 0, 100, 70)
SITE_AREA = SITE.area
PARK = box(-100, 70, 200, 150)
BUILDABLE = box(2, 3, 97, 66)  # setbacks: west 2, south 3, east 3, north 4
FSR_CAP = 2.8
HEIGHT_CAP = 40.0
CORNER_ZONE = box(70, 0, 100, 30)
CORNER_CAP = 55.0
TOWER_MIN_H = 25.0   # a building taller than this counts as a tower
TOWER_SEP = 25.0     # metres between towers
GROUND_H, TYP_H = 4.5, 3.1
DAYCARE_H = 4.0
EFF = 0.82           # net saleable / gross floor area
NET = {"studio": 33.0, "1b": 50.0, "2b": 75.0, "3b": 98.0}
MIX_TARGET = {"studio": 10, "1b": 35, "2b": 35, "3b": 20}
MIX_TOL = 5
HOMES_MIN, HOMES_MAX = 220, 280
HOMES_CLIENT_MIN = 250   # from the client email (soft, flagged)
RETAIL_MIN = 1200.0
DAYCARE_MIN_GFA = 260.0
PLAY_MIN = 259.0
COURT_MIN = 400.0
PLAY_SUN_MIN = 3.0       # hours, equinox 09:00-15:00
PARK_SHADOW_TOL = 5.0    # m2
WALL_COST, FLOOR_COST, TOWER_PREMIUM, TOWER_FLOORS = 1600.0, 3800.0, 0.15, 12

PARK_TIMES = [10 + 0.5 * i for i in range(9)]   # 10:00..14:00
PLAY_TIMES = [9, 10, 11, 12, 13, 14, 15]

def rect(d):
    return box(d["x0"], d["y0"], d["x1"], d["y1"])

def height(storeys):
    return GROUND_H + (storeys - 1) * TYP_H

def sun(t):
    """Return (altitude_rad, azimuth_from_south_rad) at solar time t on the equinox."""
    H = math.radians(15 * (t - 12))
    phi = math.radians(LAT)
    alt = math.asin(math.cos(phi) * math.cos(H))
    az = math.atan2(math.sin(H), math.sin(phi) * math.cos(H))
    return alt, az

def shadow_vector(t, h):
    alt, az = sun(t)
    L = h / math.tan(alt)
    return L * math.sin(az), L * math.cos(az)

def prism_shadow(poly, h, t):
    dx, dy = shadow_vector(t, h)
    moved = affinity.translate(poly, dx, dy)
    return MultiPoint(list(poly.exterior.coords) + list(moved.exterior.coords)).convex_hull

def solids(scheme):
    """List of (id, polygon, height, storeys, kind)."""
    out = []
    for b in scheme.get("buildings", []):
        out.append((b["id"], rect(b), height(b["storeys"]), b["storeys"], "building"))
    dc = scheme.get("daycare")
    if dc:
        out.append(("daycare", rect(dc), DAYCARE_H, 1, "daycare"))
    return out

def shadow_union(scheme, t, skip_ids=()):
    shapes = [prism_shadow(p, h, t) for (i, p, h, s, k) in solids(scheme) if i not in skip_ids]
    return unary_union(shapes) if shapes else box(0, 0, 0, 0)

def park_shadow(scheme):
    areas = [shadow_union(scheme, t).intersection(PARK).area for t in PARK_TIMES]
    return max(areas), sum(areas) / len(areas), areas

def play_sun(scheme):
    """Sun hours on the play area between 09:00 and 15:00 (trapezoid over sunlit fraction)."""
    play = rect(scheme["daycare"]["play"])
    fr = []
    for t in PLAY_TIMES:
        sh = shadow_union(scheme, t).intersection(play).area
        fr.append(1 - sh / play.area)
    hours = sum((fr[i] + fr[i + 1]) / 2 for i in range(len(fr) - 1))
    return hours, fr

def mix_ok(mix):
    keys = list(MIX_TARGET)
    if any(k not in mix for k in keys):
        return False, "missing key"
    if abs(sum(mix.values()) - 100) > 1e-9:
        return False, f"sum {sum(mix.values())}"
    for k in keys:
        if abs(mix[k] - MIX_TARGET[k]) > MIX_TOL + 1e-9:
            return False, f"{k}={mix[k]}"
    return True, "ok"

def avg_net(mix):
    return sum(NET[k] * mix[k] / 100 for k in NET)

def cost_index(scheme):
    """Rough construction cost proxy in millions of dollars (relative, not a quote)."""
    total = 0.0
    for (i, p, h, s, k) in solids(scheme):
        floor = p.area * s * FLOOR_COST
        prem = 0.0
        if s > TOWER_FLOORS:
            prem = p.area * (s - TOWER_FLOORS) * FLOOR_COST * TOWER_PREMIUM
        env = p.length * h * WALL_COST + p.area * WALL_COST
        total += floor + prem + env
    return total / 1e6

def evaluate(scheme):
    S = solids(scheme)
    rules, R = [], lambda name, ok, val, lim: rules.append({"rule": name, "pass": bool(ok), "value": val, "limit": lim})
    bl = scheme.get("buildings", [])
    dc = scheme.get("daycare")
    court = scheme.get("courtyard")
    if not dc or "play" not in dc or not court:
        raise ValueError("scheme needs buildings, daycare (with play), courtyard, mix")
    mix = scheme.get("mix", dict(MIX_TARGET))

    # geometry sanity and setbacks
    outside = [i for (i, p, h, s, k) in S if not BUILDABLE.buffer(1e-6).contains(p)]
    R("setbacks", not outside, outside or "all inside", "W2 S3 E3 N4 m")
    play, courtp = rect(dc["play"]), rect(court)
    R("open_spaces_on_site", SITE.buffer(1e-6).contains(play) and SITE.buffer(1e-6).contains(courtp),
      "ok" if SITE.buffer(1e-6).contains(play) and SITE.buffer(1e-6).contains(courtp) else "outside site", "inside site")
    overlaps = []
    for a in range(len(S)):
        for b in range(a + 1, len(S)):
            if S[a][1].intersection(S[b][1]).area > 0.01:
                overlaps.append(f"{S[a][0]}/{S[b][0]}")
    for nm, sp in (("play", play), ("courtyard", courtp)):
        for (i, p, h, s, k) in S:
            if p.intersection(sp).area > 0.01:
                overlaps.append(f"{nm}/{i}")
    if play.intersection(courtp).area > 0.01:
        overlaps.append("play/courtyard")
    R("no_overlap", not overlaps, overlaps or "none", "none")

    # areas
    gfa_b = sum(p.area * s for (i, p, h, s, k) in S if k == "building")
    gfa_dc = sum(p.area * s for (i, p, h, s, k) in S if k == "daycare")
    gfa = gfa_b + gfa_dc
    retail = sum(rect(b).area for b in bl if b.get("retail") and b["y0"] <= 3.5 + 1e-9)
    res_gfa = gfa_b - retail
    net_res = res_gfa * EFF
    mok, mmsg = mix_ok(mix)
    an = avg_net(mix) if mok else avg_net(MIX_TARGET)
    homes = int(net_res // an)
    n3 = int(homes * mix.get("3b", 0) / 100)
    fsr = gfa / SITE_AREA
    R("fsr_cap", fsr <= FSR_CAP + 1e-9, round(fsr, 3), FSR_CAP)
    R("mix_within_tolerance", mok, mmsg, f"target {MIX_TARGET} +-{MIX_TOL}")
    R("homes_range", HOMES_MIN <= homes <= HOMES_MAX, homes, f"{HOMES_MIN}-{HOMES_MAX}")
    R("retail_min", retail >= RETAIL_MIN, round(retail, 1), RETAIL_MIN)
    R("daycare_building", gfa_dc >= DAYCARE_MIN_GFA, round(gfa_dc, 1), DAYCARE_MIN_GFA)
    R("play_area_size", play.area >= PLAY_MIN, round(play.area, 1), PLAY_MIN)
    R("courtyard_size", courtp.area >= COURT_MIN, round(courtp.area, 1), COURT_MIN)

    # heights
    bad_h = []
    for (i, p, h, s, k) in S:
        cap = CORNER_CAP if CORNER_ZONE.buffer(1e-6).contains(p) else HEIGHT_CAP
        if h > cap + 1e-9:
            bad_h.append(f"{i}:{h:.1f}>{cap}")
    R("height_caps", not bad_h, bad_h or "ok", f"{HEIGHT_CAP} m, {CORNER_CAP} m in corner zone")
    towers = [(i, p) for (i, p, h, s, k) in S if h > TOWER_MIN_H]
    close = [f"{towers[a][0]}/{towers[b][0]}:{towers[a][1].distance(towers[b][1]):.1f}"
             for a in range(len(towers)) for b in range(a + 1, len(towers))
             if towers[a][1].distance(towers[b][1]) < TOWER_SEP - 1e-9]
    R("tower_separation", not close, close or "ok", f">={TOWER_SEP} m between buildings over {TOWER_MIN_H} m")

    # sun and shadow
    pmax, pmean, pareas = park_shadow(scheme)
    R("park_shadow", pmax <= PARK_SHADOW_TOL, round(pmax, 1), f"<= {PARK_SHADOW_TOL} m2 at any time 10:00-14:00")
    ps, fr = play_sun(scheme)
    R("play_area_sun", ps >= PLAY_SUN_MIN, round(ps, 2), f">= {PLAY_SUN_MIN} h between 09:00 and 15:00")

    hard_pass = all(r["pass"] for r in rules)
    return {
        "hard_pass": hard_pass,
        "hard_failures": [r["rule"] for r in rules if not r["pass"]],
        "rules": rules,
        "metrics": {
            "homes": homes, "homes_3b": n3, "share_3b_pct": mix.get("3b"),
            "gfa_total": round(gfa, 1), "fsr": round(fsr, 3), "retail_gfa": round(retail, 1),
            "residential_gfa": round(res_gfa, 1), "daycare_gfa": round(gfa_dc, 1),
            "play_area_m2": round(play.area, 1), "play_sun_hours": round(ps, 2),
            "park_shadow_max_m2": round(pmax, 1), "park_shadow_mean_m2": round(pmean, 1),
            "cost_index_musd": round(cost_index(scheme), 2),
            "cost_per_home_kusd": round(cost_index(scheme) * 1000 / homes, 1) if homes else None,
            "tallest_m": round(max(h for (i, p, h, s, k) in S if k == "building"), 1) if bl else 0,
            "meets_client_250": homes >= HOMES_CLIENT_MIN,
        },
    }
