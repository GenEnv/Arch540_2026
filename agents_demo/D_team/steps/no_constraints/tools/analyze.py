"""Usage: python tools/analyze.py <scheme_id>
Reads blackboard/schemes/<id>.json, writes blackboard/metrics/<id>.json and blackboard/drawings/<id>.png,
prints the numbers. This is the only way metrics get written."""
import json, sys, os
sys.path.insert(0, os.path.dirname(__file__))
import geom, draw
root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
def run(sid):
    sp = os.path.join(root, "blackboard", "schemes", sid + ".json")
    s = json.load(open(sp))
    r = geom.evaluate(s)
    json.dump(r, open(os.path.join(root, "blackboard", "metrics", sid + ".json"), "w"), indent=1)
    draw.draw(s, os.path.join(root, "blackboard", "drawings", sid + ".png"), title=f"{sid}: {s.get('name','')}", res=r)
    return r
if __name__ == "__main__":
    for sid in sys.argv[1:]:
        try:
            r = run(sid.replace(".json", ""))
            print(sid, "HARD PASS" if r["hard_pass"] else "HARD FAIL " + ",".join(r["hard_failures"]))
            print(" ", json.dumps(r["metrics"]))
            for x in r["rules"]:
                if not x["pass"]: print("  fail:", x["rule"], x["value"], "limit", x["limit"])
        except Exception as e:
            print(sid, "ERROR", type(e).__name__, e)
