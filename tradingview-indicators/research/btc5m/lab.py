"""Trade simulator for BTC 5m: entry next bar open, ATR stop / target, max bars, one position at a time, cost in % round trip."""
import numpy as np, pandas as pd
from numba import njit

@njit(cache=True)
def sim(o, h, l, c, a, L, S, sl_k, tp_k, max_bars, cost_pct):
    n = len(c); out = np.zeros((n, 4)); k = 0; i = 0
    while i < n - 1:
        s = 1.0 if L[i] else (-1.0 if S[i] else 0.0)
        if s == 0.0 or not np.isfinite(a[i]) or a[i] <= 0: i += 1; continue
        e = i + 1; ep = o[e]; risk = sl_k * a[i]; st = ep - s * risk; tg = ep + s * tp_k * a[i]; j = e; xp = c[n-1]
        while j < n:
            if s > 0:
                if l[j] <= st: xp = min(o[j], st); break
                if h[j] >= tg: xp = max(o[j], tg); break
            else:
                if h[j] >= st: xp = max(o[j], st); break
                if l[j] <= tg: xp = min(o[j], tg); break
            if j - e + 1 >= max_bars or j == n - 1: xp = c[j]; break
            j += 1
        pnl = s * (xp - ep) / ep * 100 - cost_pct          # % of price, net
        out[k, 0] = e; out[k, 1] = s; out[k, 2] = pnl; out[k, 3] = pnl / (risk / ep * 100)
        k += 1; i = j + 1
    return out[:k]

def run(df, F, L, S, sl_k, tp_k, max_bars, cost_pct):
    o, h, l, c = (df[k].to_numpy() for k in "ohlc")
    R = sim(o, h, l, c, F.atr.to_numpy(), L.astype(np.bool_), S.astype(np.bool_), sl_k, tp_k, max_bars, cost_pct)
    return pd.DataFrame({"date": df.index[R[:, 0].astype(int)], "side": R[:, 1], "pct": R[:, 2], "R": R[:, 3]})

def stats(T):
    if len(T) == 0: return {"n": 0, "win": np.nan, "pf": np.nan, "avg%": np.nan}
    w = T.pct[T.pct > 0].sum(); ls = -T.pct[T.pct < 0].sum()
    return {"n": len(T), "win": round(100 * (T.pct > 0).mean(), 1), "pf": round(w / ls, 2) if ls > 0 else np.inf, "avg%": round(T.pct.mean(), 3)}

PERIODS = (("IS 20-23", ("2020", "2024")), ("VAL 2024", ("2024", "2025")))   # 2025-26 is the final hold-out
def per(T):
    out = {}
    for nm, (a, b) in PERIODS:
        s = stats(T[(T.date >= a) & (T.date < b)])
        out.update({f"{nm} n": s["n"], f"{nm} win": s["win"], f"{nm} pf": s["pf"]})
    return out
