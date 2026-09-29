#!/usr/bin/env python
"""Numbers about the trade-off front. Usage: python tools/front.py [family_name]
Reads results/evals.jsonl. Prints text only."""
import json, os, sys
import numpy as np
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, HERE)
import frontlib as fl, evaluate as ev

def load(fam=None):
    p = os.path.join(ev.ROOT, "results", "evals.jsonl")
    rows = [json.loads(l) for l in open(p) if l.strip()] if os.path.exists(p) else []
    rows = [r for r in rows if r.get("valid")]
    if fam: rows = [r for r in rows if r["family"] == fam]
    return rows

def coarse(r):
    hf = ev.heightfield([tuple(b) for b in r["boxes"]])
    return hf.reshape(20, 4, 15, 4).mean(axis=(1, 3))

def main():
    fam = sys.argv[1] if len(sys.argv) > 1 else None
    rows = load(fam)
    if not rows:
        print("no evaluated designs yet"); return
    G = np.array([fl.goodness(r["gfa"], r["sun"], r["sf"]) for r in rows])
    m = fl.pareto_mask(G)
    F = [r for r, k in zip(rows, m) if k]; GF = G[m]
    order = np.argsort(-np.array([r["gfa"] for r in F])); F = [F[i] for i in order]; GF = GF[order]
    print(f"{len(rows)} valid designs, front has {len(F)} points, hypervolume {fl.hypervolume(G):.4f}")
    print("\nFRONT (sorted by gfa)")
    print(f"{'id':<28}{'family':<16}{'gfa m2':>8}{'sun h':>7}{'sf':>7}")
    for r in F[:40]:
        print(f"{r['id']:<28}{r['family']:<16}{r['gfa']:8.0f}{r['sun']:7.2f}{r['sf']:7.3f}")
    if len(F) > 40: print(f"... {len(F)-40} more")
    print("\nFRONT POINTS PER FAMILY (all families seen; 0 means the family never reaches the front)")
    fams = {}
    for r in rows: fams.setdefault(r["family"], [0, 0])[0] += 1
    for r in F: fams[r["family"]][1] += 1
    for f, (n, k) in sorted(fams.items(), key=lambda x: -x[1][1]):
        print(f"  {f:<16} evaluated {n:<5} on front {k}")
    print("\nBEST GFA THAT STILL HAS AT LEAST S SUN HOURS (a flat step means the front is thin there)")
    for S in (0, 0.5, 1, 1.5, 2, 2.5, 3, 3.5, 4, 5):
        c = [r for r in rows if r["sun"] >= S]
        if c:
            b = max(c, key=lambda r: r["gfa"]); print(f"  sun >= {S:<3} best gfa {b['gfa']:7.0f}  ({b['id']}, {b['family']}, sf {b['sf']:.3f})")
        else: print(f"  sun >= {S:<3} NO DESIGN")
    print("\nBEST SHAPE FACTOR AT LEAST G GFA")
    for Gv in (2000, 5000, 10000, 15000, 20000, 30000, 40000):
        c = [r for r in rows if r["gfa"] >= Gv]
        if c:
            b = min(c, key=lambda r: r["sf"]); print(f"  gfa >= {Gv:<6} best sf {b['sf']:.3f}  ({b['id']}, {b['family']}, sun {b['sun']:.2f})")
        else: print(f"  gfa >= {Gv:<6} NO DESIGN")
    if len(F) > 1:
        d = np.linalg.norm(np.diff(GF, axis=0), axis=1)
        print("\nLARGEST GAPS between neighbouring front points (normalised 0-1 space; midpoint = an empty target)")
        for i in np.argsort(-d)[:5]:
            a, b = F[i], F[i + 1]
            print(f"  gap {d[i]:.3f}: {a['id']} (gfa {a['gfa']:.0f}, sun {a['sun']:.2f}, sf {a['sf']:.3f}) -> "
                  f"{b['id']} (gfa {b['gfa']:.0f}, sun {b['sun']:.2f}, sf {b['sf']:.3f}); "
                  f"empty midpoint about gfa {(a['gfa']+b['gfa'])/2:.0f}, sun {(a['sun']+b['sun'])/2:.2f}, sf {(a['sf']+b['sf'])/2:.3f}")
        C = [coarse(r) for r in F]
        pairs = []
        for i in range(len(F)):
            for j in range(i + 1, len(F)):
                pairs.append((float(np.abs(C[i] - C[j]).mean()), i, j))
        pairs.sort()
        print("\nNEAR-DUPLICATE front pairs (mean storey difference on a 4 m grid; below 0.1 is nearly the same building)")
        for dist, i, j in pairs[:5]:
            print(f"  {dist:.3f}: {F[i]['id']} and {F[j]['id']}")
main()
