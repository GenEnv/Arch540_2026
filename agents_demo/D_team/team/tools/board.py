"""Usage: python tools/board.py [out_prefix]  -> candidate board PNG + trade-off table (md) from blackboard/."""
import json, sys, os, glob
sys.path.insert(0, os.path.dirname(__file__))
import matplotlib; matplotlib.use("Agg")
import matplotlib.pyplot as plt
from PIL import Image
root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
def main(prefix="final/board"):
    ids = sorted(os.path.basename(p)[:-5] for p in glob.glob(os.path.join(root, "blackboard/metrics/*.json")))
    rows = []
    for i in ids:
        r = json.load(open(os.path.join(root, f"blackboard/metrics/{i}.json"))); m = r["metrics"]
        rows.append((i, r["hard_pass"], m, r["hard_failures"]))
    md = ["| scheme | hard rules | homes | 3b | play sun h | park shadow m2 | cost $M | FSR | failed |", "|---|---|---|---|---|---|---|---|---|"]
    for i, ok, m, f in rows:
        md.append(f"| {i} | {'pass' if ok else 'FAIL'} | {m['homes']} | {m['homes_3b']} | {m['play_sun_hours']} | {m['park_shadow_max_m2']} | {m['cost_index_musd']} | {m['fsr']} | {', '.join(f)} |")
    open(os.path.join(root, prefix + "_tradeoff.md"), "w").write("\n".join(md) + "\n")
    imgs = [(i, os.path.join(root, f"blackboard/drawings/{i}.png")) for i in ids if os.path.exists(os.path.join(root, f"blackboard/drawings/{i}.png"))]
    if not imgs: return
    cols = 2; rws = (len(imgs) + cols - 1) // cols
    ims = [Image.open(p) for _, p in imgs]; w, h = ims[0].size
    sheet = Image.new("RGB", (w * cols, h * rws), "white")
    for k, im in enumerate(ims):
        sheet.paste(im.resize((w, h)), ((k % cols) * w, (k // cols) * h))
    sheet.save(os.path.join(root, prefix + ".png"))
    print("wrote", prefix + ".png", prefix + "_tradeoff.md", len(imgs), "schemes")
if __name__ == "__main__":
    main(*sys.argv[1:])
