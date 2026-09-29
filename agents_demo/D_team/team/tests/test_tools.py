"""Run: python tests/test_tools.py  (plain asserts, no test framework needed)"""
import math, os, sys, copy
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "tools"))
import geom
from shapely.geometry import box

def approx(a, b, tol): assert abs(a - b) <= tol, (a, b)

def base():
    return {"buildings": [{"id": "A", "x0": 3, "y0": 3, "x1": 60, "y1": 23, "storeys": 12, "retail": True}],
            "daycare": {"x0": 70, "y0": 40, "x1": 85, "y1": 50, "play": {"x0": 70, "y0": 51, "x1": 90, "y1": 64}},
            "courtyard": {"x0": 5, "y0": 30, "x1": 40, "y1": 50}, "mix": dict(geom.MIX_TARGET)}

def test_sun_noon():
    alt, az = geom.sun(12); approx(math.degrees(alt), 90 - 49.28, 1e-6); approx(az, 0, 1e-9)
def test_sun_1000():
    alt, az = geom.sun(10); approx(math.degrees(alt), 34.4, 0.1); approx(math.degrees(az), -37.3, 0.1)
def test_shadow_north_component_is_h_tan_lat():
    for t in (9, 10, 12, 14, 15):
        dx, dy = geom.shadow_vector(t, 30); approx(dy, 30 * math.tan(math.radians(geom.LAT)), 1e-6)
def test_shadow_direction_morning_west():
    dx, dy = geom.shadow_vector(10, 20); assert dx < 0 and dy > 0
def test_prism_shadow_area_noon():
    p = box(0, 0, 10, 10); s = geom.prism_shadow(p, 20, 12)
    approx(s.area, 100 + 10 * 20 * math.tan(math.radians(49.28)), 0.01)
def test_height():
    approx(geom.height(1), 4.5, 1e-9); approx(geom.height(10), 4.5 + 9 * 3.1, 1e-9)
def test_area_tally():
    s = base(); r = geom.evaluate(s); m = r["metrics"]
    gfa = 57 * 20 * 12 + 15 * 10; approx(m["gfa_total"], gfa, 0.2)
    approx(m["retail_gfa"], 57 * 20, 0.2)
    net = (57 * 20 * 11) * geom.EFF; approx(m["homes"], net // geom.avg_net(geom.MIX_TARGET), 0)
    approx(m["fsr"], gfa / 7000, 0.001)
def test_retail_needs_south_frontage():
    s = base(); s["buildings"][0]["y0"] = 10; s["buildings"][0]["y1"] = 30
    approx(geom.evaluate(s)["metrics"]["retail_gfa"], 0, 1e-9)
def test_setback_fail():
    s = base(); s["buildings"][0]["x0"] = 0.5
    assert "setbacks" in geom.evaluate(s)["hard_failures"]
def test_overlap_fail():
    s = base(); s["courtyard"] = {"x0": 10, "y0": 10, "x1": 30, "y1": 40}
    assert "no_overlap" in geom.evaluate(s)["hard_failures"]
def test_height_cap_and_corner():
    s = base(); s["buildings"][0].update(storeys=14)  # 44.8 m
    assert "height_caps" in geom.evaluate(s)["hard_failures"]
    s = base(); s["buildings"] = [{"id": "T", "x0": 72, "y0": 4, "x1": 92, "y1": 24, "storeys": 16, "retail": False}]  # 51 m in corner
    assert "height_caps" not in geom.evaluate(s)["hard_failures"]
def test_tower_separation():
    s = base(); s["buildings"] = [{"id": "A", "x0": 3, "y0": 3, "x1": 23, "y1": 23, "storeys": 10, "retail": True},
                                  {"id": "B", "x0": 33, "y0": 3, "x1": 53, "y1": 23, "storeys": 10, "retail": False}]  # 10 m apart, 32 m tall
    assert "tower_separation" in geom.evaluate(s)["hard_failures"]
    s["buildings"][1]["x0"] = 50; s["buildings"][1]["x1"] = 70
    assert "tower_separation" not in geom.evaluate(s)["hard_failures"]
def test_park_shadow_reach():
    # noon shadow reach north = tan(lat) h = 1.16 h. A 20 m box with north edge at y=50 reaches y=73.3 -> shadow on park
    s = base(); s["buildings"] = [{"id": "A", "x0": 3, "y0": 30, "x1": 40, "y1": 50, "storeys": 6, "retail": False}]
    h = geom.height(6);     mx, _, _ = geom.park_shadow(s); approx(mx > 0, True, 0)
    s["buildings"][0].update(y0=3, y1=20); mx, _, _ = geom.park_shadow(s); approx(mx, 0, 1e-9)  # 20+1.1667*20=43
def test_park_shadow_exact_edge():
    # north edge at y=66, height h: at noon reaches 66+1.16667h; h=3.0 -> 69.5 no shadow; h=4.5 (1 storey) -> 71.25
    s = base(); s["buildings"] = [{"id": "A", "x0": 3, "y0": 60, "x1": 40, "y1": 66, "storeys": 1, "retail": False}]
    mx, _, _ = geom.park_shadow(s); assert mx > 1
    strip = 66 + geom.shadow_vector(12, 4.5)[1] - 70; approx(strip, 4.5 * math.tan(math.radians(49.28)) - 4, 1e-6)
def test_play_sun_open_is_full():
    s = base(); s["buildings"] = []; s["daycare"]["play"] = {"x0": 70, "y0": 5, "x1": 90, "y1": 18}; hrs, fr = geom.play_sun(s)
    approx(hrs, 6, 0.01)
def test_play_sun_shaded_south():
    s = base(); s["daycare"]["play"] = {"x0": 3, "y0": 24, "x1": 25, "y1": 38}  # just north of a 12-storey bar
    hrs, fr = geom.play_sun(s); assert hrs < 1.0
def test_cost_tower_premium():
    a = base(); b = copy.deepcopy(a); b["buildings"][0]["storeys"] = 13
    a["buildings"][0]["storeys"] = 12
    ca, cb = geom.cost_index(a), geom.cost_index(b); assert cb > ca
    per_a = ca / 12; per_b = cb / 13; assert per_b > per_a * 0.999
def test_mix_bounds():
    assert geom.mix_ok({"studio": 10, "1b": 35, "2b": 35, "3b": 20})[0]
    assert not geom.mix_ok({"studio": 10, "1b": 25, "2b": 45, "3b": 20})[0]
    assert not geom.mix_ok({"studio": 10, "1b": 35, "2b": 35, "3b": 25})[0]
def test_contradiction_homes_vs_fsr():
    """Planted contradiction: even the smallest allowed mix cannot reach 250 homes under the FSR cap."""
    best = {"studio": 15, "1b": 40, "2b": 30, "3b": 15}; assert geom.mix_ok(best)[0]
    max_res_gfa = geom.FSR_CAP * geom.SITE_AREA - geom.RETAIL_MIN - geom.DAYCARE_MIN_GFA
    max_homes = max_res_gfa * geom.EFF / geom.avg_net(best)
    assert max_homes < 250, max_homes
    assert max_homes >= 220, max_homes
    print("   max homes under FSR cap:", round(max_homes, 1))

if __name__ == "__main__":
    fs = [(k, v) for k, v in sorted(globals().items()) if k.startswith("test_")]
    bad = 0
    for k, f in fs:
        try: f(); print("ok  ", k)
        except Exception as e: bad += 1; print("FAIL", k, repr(e))
    print(f"{len(fs) - bad}/{len(fs)} passed"); sys.exit(1 if bad else 0)
