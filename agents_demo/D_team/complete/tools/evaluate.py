"""Usage: python tools/evaluate.py scheme.json   -> prints JSON with hard rules and metrics."""
import json, sys, os
sys.path.insert(0, os.path.dirname(__file__))
import geom
if __name__ == "__main__":
    try:
        print(json.dumps(geom.evaluate(json.load(open(sys.argv[1]))), indent=1))
    except Exception as e:
        print(json.dumps({"error": f"{type(e).__name__}: {e}"})); sys.exit(1)
