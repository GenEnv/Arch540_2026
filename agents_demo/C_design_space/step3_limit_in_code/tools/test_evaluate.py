"""Checks that the evaluator does what it says. Run: python tools/test_evaluate.py"""
import math, os, sys
import numpy as np
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import evaluate as ev
import frontlib as fl

def test_noon_altitude():
    v = ev.sun_vectors()
    alt = ev.altitude_deg(v[3])
    assert abs(alt - (90 - 49.25 - 23.44)) < 1e-6, alt      # 17.31 deg by hand
    assert v[3][0] == 0 and v[3][1] < 0                      # due south at noon
    assert v[0][0] > 0 and v[6][0] < 0                       # east in the morning, west in the afternoon
    print("noon altitude", round(alt, 3), "deg  ok")

def test_shadow_length_matches_hand_calculation():
    noon = ev.sun_vectors()[3:4]
    for storeys in (1, 2, 3, 4):
        boxes = [(30, 20, 40, 30, storeys)]
        sm = ev.sun_map(boxes, vecs=noon)       # one time step only, weight 0.5 -> shaded=0, lit=0.5
        M = ev.MARGIN
        col = sm[35 + M, :]                      # column through the middle of the box
        north = col[30 + M:]
        shaded_cells = int(np.sum(north == 0))  # the domain reaches 15 m past the lot, so up to 45 m of shadow fits
        hand = storeys * ev.STOREY_H / math.tan(math.radians(90 - 49.25 - 23.44))
        assert abs(shaded_cells - hand) <= 1.0, (storeys, shaded_cells, hand)
        # cells beside the shadow (x outside the box at noon) are lit
        assert sm[45 + M, 35 + M] > 0 and sm[25 + M, 35 + M] > 0
        print(f"{storeys} storey: shadow {shaded_cells} m on grid, hand h/tan(alt) = {hand:.2f} m  ok")

def test_empty_lot_full_sun():
    hf_boxes = []
    sm = ev.sun_map(hf_boxes)
    assert abs(np.nanmean(sm) - 6.0) < 1e-9

def test_box_geometry():
    b = [(10, 10, 20, 20, 2)]                    # 10 x 10 x 6.4 m
    hf = ev.heightfield(b)
    env, vol = ev.envelope_and_volume(hf)
    assert vol == 10 * 10 * 6.4
    assert abs(env - (100 + 4 * 10 * 6.4)) < 1e-9
    s = ev.score_boxes(b)
    assert s["gfa"] == 200
    print("box envelope", env, "volume", vol, "sf", round(s["sf"], 3), "ok")

def test_limits():
    assert ev.check_limits([(3, 3, 20, 20, 5)]) == []
    assert ev.check_limits([(2, 3, 20, 20, 5)])                 # setback
    assert ev.check_limits([(3, 3, 20, 20, 15)])                # height
    assert ev.check_limits([(3, 3, 20, 20, 5), (24, 3, 40, 20, 5)])   # 4 m gap
    assert ev.check_limits([(3, 3, 20, 20, 5), (26, 3, 40, 20, 5)]) == []  # 6 m gap
    assert ev.check_limits([(3, 3, 20, 20, 5), (20, 3, 40, 20, 8)]) == []  # touching = one building
    assert ev.check_limits([(3, 3, 8, 20, 5)])                  # 5 m wide

def test_hypervolume():
    assert abs(fl.hypervolume(np.array([[0.5, 0.5, 0.5]])) - 0.125) < 1e-12
    G = np.array([[1, 0.5, 0.5], [0.5, 1, 0.5]])
    # union of two boxes: 0.25 + 0.25 - overlap 0.5*0.5*0.5=0.125 -> 0.375
    assert abs(fl.hypervolume(G) - 0.375) < 1e-12

if __name__ == "__main__":
    for n, f in list(globals().items()):
        if n.startswith("test_"):
            f(); print("PASS", n)
