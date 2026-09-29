"""Pareto front, hypervolume and normalisation. Part of the protected harness."""
import numpy as np

GFA_REF = 56000.0   # m2, about 74 x 54 m x 14 storeys (theoretical ceiling)
SUN_REF = 6.0       # hours, 9:00-15:00
SF_CAP = 1.0        # shape factor at or above this scores 0


def goodness(gfa, sun, sf):
    """Normalised vector, all three 'bigger is better', each in 0..1."""
    return np.array([min(gfa / GFA_REF, 1.0), min(sun / SUN_REF, 1.0),
                     float(np.clip(1.0 - sf / SF_CAP, 0.0, 1.0))])


def pareto_mask(G):
    """G: (n,3) goodness array. True where the point is not dominated."""
    n = len(G)
    keep = np.ones(n, bool)
    for i in range(n):
        if not keep[i]:
            continue
        dom = np.all(G >= G[i], axis=1) & np.any(G > G[i], axis=1)
        if dom.any():
            keep[i] = False
    return keep


def hypervolume(G):
    """Exact 3D hypervolume of goodness points against the origin (0,0,0)."""
    G = np.asarray(G, float)
    if len(G) == 0:
        return 0.0
    G = G[pareto_mask(G)]
    order = np.argsort(-G[:, 2])
    G = G[order]
    hv = 0.0
    for k in range(len(G)):
        z_hi = G[k, 2]
        z_lo = G[k + 1, 2] if k + 1 < len(G) else 0.0
        if z_hi <= z_lo:
            continue
        P = G[: k + 1, :2]
        # 2D area of union of rectangles [0,x]x[0,y]
        idx = np.argsort(-P[:, 0])
        P = P[idx]
        area, ymax = 0.0, 0.0
        for j in range(len(P)):
            x = P[j, 0]
            x_next = P[j + 1, 0] if j + 1 < len(P) else 0.0
            ymax = max(ymax, P[j, 1])
            area += (x - x_next) * ymax
        hv += area * (z_hi - z_lo)
    return float(hv)
