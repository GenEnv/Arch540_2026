#!/usr/bin/env python
"""For humans only (the agent does not need it). Axonometric sheets and front scatter.
python render.py gallery EVALS.jsonl OUT.png [--title T] [--per-family N] [--front-only|--all] [--upto-round K] [--family F]
python render.py scatter EVALS.jsonl OUT.png [--title T] [--upto-round K]
"""
import json, os, sys, argparse
import numpy as np
import matplotlib; matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.collections import PolyCollection
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, HERE)
import frontlib as fl, evaluate as ev

def load(path, upto=None, fam=None):
    rows = [json.loads(l) for l in open(path) if l.strip()]
    rows = [r for r in rows if r.get("valid")]
    if upto: rows = [r for r in rows if r["round"] <= upto]
    if fam: rows = [r for r in rows if r["family"] == fam]
    return rows

def front_of(rows):
    if not rows: return []
    G = np.array([fl.goodness(r["gfa"], r["sun"], r["sf"]) for r in rows])
    return [r for r, k in zip(rows, fl.pareto_mask(G)) if k]

PAL = ["#3a6ea5", "#e0642f", "#5e9e3e", "#8a4fa0", "#c9a227", "#2a9d9d", "#b5485d", "#6b6b6b", "#7a5c3a", "#1f4e79"]
def fam_colors(names):
    return {n: PAL[i % len(PAL)] for i, n in enumerate(sorted(set(names)))}

def proj(x, y, z, a=np.radians(35)):
    # camera from south-west; x east, y north
    u = (x - y) * np.cos(a) * 0.9
    v = (x + y) * np.sin(a) * 0.55 + z
    return u, v

def draw_design(ax, r, c=2, sunmap=True):
    boxes = [tuple(b) for b in r["boxes"]]
    hf = ev.heightfield(boxes)
    sm = ev.sun_map(boxes, hf)
    W, D = hf.shape
    polys, cols = [], []
    def P(pts): return [proj(*p) for p in pts]
    # ground: lot plus the neighbouring ring
    M = ev.MARGIN
    for I in range(0, sm.shape[0], c):
        for J in range(0, sm.shape[1], c):
            blk = sm[I:I+c, J:J+c]
            if np.all(np.isnan(blk)): continue
            t = float(np.nanmean(blk)) / 6.0
            col = (0.72 + 0.26*t, 0.76 + 0.19*t, 0.88 - 0.22*t)
            inlot = (I >= M and J >= M and I < M + W and J < M + D)
            if not inlot: col = tuple(0.5 + 0.5*x for x in col)
            x0, y0 = I - M, J - M
            polys.append(P([(x0, y0, 0), (x0+c, y0, 0), (x0+c, y0+c, 0), (x0, y0+c, 0)])); cols.append(col)
    ground_n = len(polys)
    cells = [(i, j) for i in range(W) for j in range(D) if hf[i, j] > 0]
    cells.sort(key=lambda p: -(p[0] + p[1]))
    sh = ev.STOREY_H
    for i, j in cells:
        h = hf[i, j] * sh
        hs = hf[i, j - 1] * sh if j > 0 else 0
        hw = hf[i - 1, j] * sh if i > 0 else 0
        if h > hs:
            polys.append(P([(i, j, hs), (i+1, j, hs), (i+1, j, h), (i, j, h)])); cols.append((0.80, 0.80, 0.82))
        if h > hw:
            polys.append(P([(i, j, hw), (i, j+1, hw), (i, j+1, h), (i, j, h)])); cols.append((0.62, 0.62, 0.66))
        polys.append(P([(i, j, h), (i+1, j, h), (i+1, j+1, h), (i, j+1, h)])); cols.append((0.95, 0.95, 0.96))
    pc = PolyCollection([np.array(p) for p in polys], facecolors=cols,
                        edgecolors=[c_ if k >= ground_n else c_ for k, c_ in enumerate(cols)], linewidths=0.15)
    ax.add_collection(pc)
    lot = P([(0, 0, 0), (W, 0, 0), (W, D, 0), (0, D, 0), (0, 0, 0)])
    ax.plot(*zip(*lot), color="#555", lw=0.6, zorder=0)
    pc.set_zorder(1)
    ax.set_xlim(-(D + M) * 0.75 - 4, (W + M) * 0.75 + 8); ax.set_ylim(-M * 0.9, (W + D + 2 * M) * 0.32 + 46 * 1.0)
    ax.set_aspect("equal"); ax.axis("off")

def gallery(a):
    rows = load(a.evals, a.upto_round, a.family)
    if a.group == "gclass":
        sys.path.insert(0, os.path.expanduser("~/dev/arch540-s04/D3_massing_moo"))
        import analysis
        for r in rows: r["family"] = analysis.classify(r["boxes"])
    if not a.all: pool = front_of(rows)
    else: pool = rows
    byfam = {}
    for r in pool: byfam.setdefault(r["family"], []).append(r)
    ncol = a.cols
    # thin each family evenly along gfa
    sel = {}
    for f, rs in byfam.items():
        rs = sorted(rs, key=lambda r: r["gfa"])
        if len(rs) > a.per_family:
            idx = np.unique(np.linspace(0, len(rs) - 1, a.per_family).round().astype(int)); rs = [rs[i] for i in idx]
        sel[f] = rs
    total_rows = sum(int(np.ceil(len(v) / ncol)) for v in sel.values())
    if total_rows == 0:
        print("nothing to draw"); return
    cw, chh = 2.5, 2.35
    fig = plt.figure(figsize=(ncol * cw, total_rows * chh + 0.6 * len(sel) + 0.6), facecolor="white")
    heights = []
    for f, v in sel.items(): heights += [0.28] + [1] * int(np.ceil(len(v) / ncol))
    gs = fig.add_gridspec(len(heights), ncol, height_ratios=heights, hspace=0.06, wspace=0.02, top=0.965, bottom=0.01, left=0.01, right=0.99)
    colors = fam_colors(byfam.keys()); k = 0
    nfront = len(front_of(rows))
    fig.suptitle(f"{a.title}   ({len(rows)} valid designs, {nfront} on the front; drawn: {sum(len(v) for v in sel.values())})", fontsize=11, x=0.01, ha="left")
    for f, v in sel.items():
        ax = fig.add_subplot(gs[k, :]); ax.axis("off")
        nf = len([1 for r in front_of(rows) if r["family"] == f])
        ax.text(0.0, 0.5, f"{f}   (on front: {nf})", fontsize=10, weight="bold", color=colors[f], va="center"); k += 1
        nr = int(np.ceil(len(v) / ncol))
        for q, r in enumerate(v):
            ax = fig.add_subplot(gs[k + q // ncol, q % ncol])
            draw_design(ax, r)
            ax.text(0.02, 0.02, f"GFA {r['gfa']/1000:.1f}k  sun {r['sun']:.1f}h  SF {r['sf']:.2f}", transform=ax.transAxes, fontsize=6.5, color="#222")
        k += nr
    fig.savefig(a.out, dpi=130); print("wrote", a.out)

def scatter(a):
    rows = load(a.evals, a.upto_round)
    F = front_of(rows)
    fams = [r["family"] for r in rows]; colors = fam_colors(fams)
    fig, axs = plt.subplots(1, 2, figsize=(11, 4.4))
    for ax, (xk, yk, xl, yl) in zip(axs, [("gfa", "sun", "gross floor area (m2)", "sun hours on open ground"), ("gfa", "sf", "gross floor area (m2)", "shape factor (lower is better)")]):
        for f in sorted(set(fams)):
            R = [r for r in rows if r["family"] == f]
            ax.scatter([r[xk] for r in R], [r[yk] for r in R], s=9, alpha=0.45, color=colors[f], label=f, lw=0)
        ax.scatter([r[xk] for r in F], [r[yk] for r in F], s=34, facecolors="none", edgecolors="k", lw=0.8, label="front")
        ax.set_xlabel(xl); ax.set_ylabel(yl); ax.grid(alpha=0.2)
    axs[0].legend(fontsize=7, loc="upper right", ncol=1)
    G = np.array([fl.goodness(r["gfa"], r["sun"], r["sf"]) for r in rows]) if rows else np.zeros((0, 3))
    fig.suptitle(f"{a.title}  n={len(rows)}  front={len(F)}  hypervolume={fl.hypervolume(G):.3f}", fontsize=10)
    fig.tight_layout(); fig.savefig(a.out, dpi=140); print("wrote", a.out)

if __name__ == "__main__":
    p = argparse.ArgumentParser(); p.add_argument("mode"); p.add_argument("evals"); p.add_argument("out")
    p.add_argument("--title", default=""); p.add_argument("--per-family", type=int, default=6, dest="per_family")
    p.add_argument("--cols", type=int, default=6)
    p.add_argument("--all", action="store_true"); p.add_argument("--upto-round", type=int, default=None, dest="upto_round")
    p.add_argument("--family", default=None); p.add_argument("--group", default="name")
    a = p.parse_args()
    gallery(a) if a.mode == "gallery" else scatter(a)
