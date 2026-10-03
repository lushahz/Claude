"""TP1 / TP2 test on the indicator's signals: half closed at TP1, rest at TP2; optional stop to breakeven after TP1."""
import numpy as np, pandas as pd, itertools, warnings; warnings.filterwarnings("ignore")
from numba import njit
from glab import session_end_flags
import grid2_fams as G
df, f = G.df, G.f
L = np.load("sigL.npy"); S = np.load("sigS.npy")   # exact indicator signals (gate $2, session)

@njit(cache=True)
def sim2(o, h, l, c, a, sig, side, sk, t1, t2, mb, se, cost, be):
    n = len(c); out = np.zeros((n, 4)); k = 0; i = 0
    while i < n - 1:
        if not sig[i]: i += 1; continue
        s = side[i]; e = i + 1; ep = o[e]; risk = sk * a[i]
        st = ep - s * risk; p1 = ep + s * t1 * a[i]; p2 = ep + s * t2 * a[i]
        hit1 = False; leg1 = 0.0; j = e; xp = np.nan
        while j < n:
            if s > 0:
                if l[j] <= st: xp = min(o[j], st); break
                if not hit1 and h[j] >= p1: hit1 = True; leg1 = p1 - ep
                if h[j] >= p2: xp = max(o[j], p2); break
            else:
                if h[j] >= st: xp = max(o[j], st); break
                if not hit1 and l[j] <= p1: hit1 = True; leg1 = ep - p1
                if l[j] <= p2: xp = min(o[j], p2); break
            if hit1 and be: st = max(st, ep) if s > 0 else min(st, ep)
            if j - e + 1 >= mb or se[j] or j == n - 1: xp = c[j]; break
            j += 1
        leg2 = s * (xp - ep)
        if not hit1: leg1 = leg2
        out[k, 0] = e; out[k, 1] = 0.5 * leg1 + 0.5 * leg2 - cost; out[k, 2] = hit1; out[k, 3] = out[k, 1] / risk
        k += 1; i = j + 1
    return out[:k]

