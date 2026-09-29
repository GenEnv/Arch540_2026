"""Usage: python tools/draw.py scheme.json out.png  -> plan with shadows + oblique view."""
import json, sys, os
sys.path.insert(0, os.path.dirname(__file__))
import matplotlib; matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import Polygon as MP, Rectangle
import geom

def poly_xy(g):
    return list(g.exterior.coords) if g.geom_type == "Polygon" else []

def add_geom(ax, g, **kw):
    if g.is_empty: return
    for p in (g.geoms if hasattr(g, "geoms") else [g]):
        if p.geom_type == "Polygon":
            ax.add_patch(MP(poly_xy(p), closed=True, **kw))

def draw(scheme, path, title=None, res=None):
    res = res or geom.evaluate(scheme)
    m = res["metrics"]
    fig = plt.figure(figsize=(11, 5.4))
    ax = fig.add_axes([0.03, 0.08, 0.5, 0.82])
    ax.set_xlim(-25, 135); ax.set_ylim(-18, 100); ax.set_aspect("equal"); ax.axis("off")
    ax.add_patch(Rectangle((-25, 70), 160, 30, fc="#cfe6c4", ec="none")); ax.text(30, 92, "PARK", color="#4d7a3d", ha="center", fontsize=9)
    ax.add_patch(Rectangle((-25, -18), 160, 18, fc="#e4e4e0", ec="none")); ax.text(30, -10, "SOUTH STREET", color="#777", ha="center", fontsize=8)
    ax.add_patch(Rectangle((100, 0), 35, 70, fc="#e4e4e0", ec="none")); ax.text(118, 35, "EAST\nSTREET", color="#777", ha="center", fontsize=8)
    ax.add_patch(Rectangle((0, 0), 100, 70, fc="#fbfbf9", ec="#333", lw=1))
    b = geom.BUILDABLE.bounds
    ax.add_patch(Rectangle((b[0], b[1]), b[2]-b[0], b[3]-b[1], fc="none", ec="#999", lw=0.7, ls="--"))
    for t, col in ((10, "#3a6ea5"), (12, "#888888"), (14, "#8e44ad")):
        add_geom(ax, geom.shadow_union(scheme, t), fc=col, alpha=0.16, ec=col, lw=0.6)
    pk = geom.shadow_union(scheme, 10)
    for t in geom.PARK_TIMES[1:]:
        pk = pk.union(geom.shadow_union(scheme, t))
    add_geom(ax, pk.intersection(geom.PARK), fc="#d62728", alpha=0.55, ec="none")
    c = scheme["courtyard"]; add_geom(ax, geom.rect(c), fc="#b9dca8", alpha=0.9, ec="#5e9e3e", lw=1)
    ax.text((c["x0"]+c["x1"])/2, (c["y0"]+c["y1"])/2, "courtyard", ha="center", va="center", fontsize=7, color="#2d5a1e")
    pl = scheme["daycare"]["play"]; add_geom(ax, geom.rect(pl), fc="#ffe79a", ec="#c9a227", lw=1)
    ax.text((pl["x0"]+pl["x1"])/2, (pl["y0"]+pl["y1"])/2, "play", ha="center", va="center", fontsize=7)
    hmax = max([s[2] for s in geom.solids(scheme)] + [1])
    for (i, p, h, s, k) in geom.solids(scheme):
        shade = 0.9 - 0.6 * min(h / 55, 1)
        fc = "#f2c14e" if k == "daycare" else (shade, shade, shade + 0.03)
        add_geom(ax, p, fc=fc, ec="#222", lw=1)
        cx, cy = p.centroid.x, p.centroid.y
        ax.text(cx, cy, f"{i}\n{s}f {h:.0f}m", ha="center", va="center", fontsize=6.5, color="#111")
    ax.set_title(title or scheme.get("name", ""), fontsize=10, loc="left")
    ax.text(-24, -16.5, "shadows: blue 10:00, grey 12:00, purple 14:00; red = shadow on park", fontsize=6.5, color="#444")
    # oblique view
    ax2 = fig.add_axes([0.53, 0.08, 0.28, 0.82]); ax2.set_aspect("equal"); ax2.axis("off")
    def pr(x, y, z):  # oblique projection looking from the south-west
        return (x + 0.45 * y, 0.5 * y + z * 1.1)
    ax2.add_patch(MP([pr(0,0,0), pr(100,0,0), pr(100,70,0), pr(0,70,0)], fc="#fbfbf9", ec="#333", lw=0.8))
    ax2.add_patch(MP([pr(-25,70,0), pr(135,70,0), pr(135,100,0), pr(-25,100,0)], fc="#cfe6c4", ec="none", zorder=0))
    order = sorted(geom.solids(scheme), key=lambda s: -s[1].centroid.y)
    for (i, p, h, s, k) in order:
        x0, y0, x1, y1 = p.bounds
        top = "#f2c14e" if k == "daycare" else "#dcdcdc"
        for poly, col in (([pr(x0,y0,0), pr(x1,y0,0), pr(x1,y0,h), pr(x0,y0,h)], "#b8b8b8"),
                          ([pr(x1,y0,0), pr(x1,y1,0), pr(x1,y1,h), pr(x1,y0,h)], "#9a9a9a"),
                          ([pr(x0,y0,h), pr(x1,y0,h), pr(x1,y1,h), pr(x0,y1,h)], top)):
            ax2.add_patch(MP(poly, fc=col, ec="#222", lw=0.6))
    ax2.autoscale_view(); ax2.set_xlim(-10, 160); ax2.set_ylim(-5, 130)
    ax2.text(-10, 128, "oblique view from the south-west", fontsize=8, va="top")
    # metrics text
    ax3 = fig.add_axes([0.80, 0.08, 0.19, 0.82]); ax3.axis("off")
    lines = [("homes", m["homes"]), ("3b homes", m["homes_3b"]), ("FSR", m["fsr"]), ("tallest m", m["tallest_m"]),
             ("play sun h", m["play_sun_hours"]), ("park shadow m2", m["park_shadow_max_m2"]),
             ("cost $M", m["cost_index_musd"]), ("retail m2", m["retail_gfa"])]
    y = 0.98
    for k, v in lines:
        ax3.text(0, y, f"{k}", fontsize=8, va="top", color="#555"); ax3.text(1, y, f"{v}", fontsize=8, va="top", ha="right"); y -= 0.06
    ok = res["hard_pass"]
    ax3.text(0, y - 0.03, "ALL HARD RULES PASS" if ok else "FAILS: " + ", ".join(res["hard_failures"]),
             fontsize=8, va="top", color="#2d7a1e" if ok else "#b8371f", wrap=True, weight="bold")
    fig.savefig(path, dpi=110); plt.close(fig)

if __name__ == "__main__":
    draw(json.load(open(sys.argv[1])), sys.argv[2])
