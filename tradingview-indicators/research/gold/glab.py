"""Trade simulation for gold 5m: entry at next bar open, ATR stop/target, max hold, flat at session end. Costs in $/oz round trip."""
import numpy as np, pandas as pd
from numba import njit

SESSION = (7.0, 16.0)          # UTC hours, London + New York

@njit(cache=True)
def simulate(o, h, l, c, a, sig, side, stop_k, tgt_k, max_bars, sess_end, cost, trail_k, be_k):
    """sig: bool entries at bar i (decided at close); side: +1/-1 per bar. Returns per-trade arrays.
    One position at a time. Exits: stop, target, optional trailing stop (trail_k*ATR from best close),
    optional move stop to breakeven after be_k*ATR favourable, max_bars, or session end (bar flagged)."""
    n = len(c)
    ent_i = np.empty(n, np.int64); ext_i = np.empty(n, np.int64); pnl = np.empty(n); rr = np.empty(n); sides = np.empty(n)
    k = 0; i = 0
    while i < n - 1:
        if not sig[i]:
            i += 1; continue
        s = side[i]; e = i + 1; ep = o[e]; risk = stop_k * a[i]
        st = ep - s * risk; tg = ep + s * tgt_k * a[i]; best = ep
        j = e; xp = np.nan
        while j < n:
            # stop first (conservative), then target
            if s > 0:
                if l[j] <= st: xp = min(o[j], st); break
                if h[j] >= tg: xp = max(o[j], tg); break
            else:
                if h[j] >= st: xp = max(o[j], st); break
                if l[j] <= tg: xp = min(o[j], tg); break
            # update after the bar
            if s > 0: best = max(best, c[j])
            else: best = min(best, c[j])
            if be_k > 0 and s * (best - ep) >= be_k * a[i]:
                st = max(st, ep) if s > 0 else min(st, ep)
            if trail_k > 0:
                tr = best - s * trail_k * a[j]
                st = max(st, tr) if s > 0 else min(st, tr)
            if j - e + 1 >= max_bars or sess_end[j] or j == n - 1:
                xp = c[j]; break
            j += 1
        ent_i[k] = e; ext_i[k] = j; sides[k] = s
        pnl[k] = s * (xp - ep) - cost; rr[k] = pnl[k] / risk
        k += 1
        i = j + 1
    return ent_i[:k], ext_i[:k], sides[:k], pnl[:k], rr[:k]

def session_mask(idx, start=SESSION[0], end=SESSION[1]):
    hr = idx.hour + idx.minute / 60
    return (hr >= start) & (hr < end)

def session_end_flags(idx, end=SESSION[1]):
    hr = idx.hour + idx.minute / 60
    nxt = np.r_[hr[1:], 0]
    same_day = np.r_[(idx[1:].date == idx[:-1].date), False]
    return ((hr < end) & (nxt >= end)) | ~same_day | (hr >= end)

def stats(T, label=""):
    if len(T) == 0: return {"label": label, "n": 0}
    w = T.pnl[T.pnl > 0].sum(); L = -T.pnl[T.pnl < 0].sum()
    days = T.date.dt.normalize().nunique()
    return {"label": label, "n": len(T), "per_day": round(len(T) / max(days, 1), 2), "win": round((T.pnl > 0).mean(), 3),
            "avg_$": round(T.pnl.mean(), 3), "avg_R": round(T.rr.mean(), 3), "pf": round(w / L, 2) if L else np.inf,
            "total_$": round(T.pnl.sum(), 1)}

def run(df, f, sig, side, stop_k=1.0, tgt_k=1.5, max_bars=24, cost=0.30, trail_k=0.0, be_k=0.0):
    o, h, l, c = (df[k].to_numpy() for k in "ohlc")
    a = f.atr.to_numpy()
    se = session_end_flags(df.index)
    e, x, s, p, r = simulate(o, h, l, c, a, sig.astype(np.bool_), side.astype(np.float64), stop_k, tgt_k, max_bars, se, cost, trail_k, be_k)
    return pd.DataFrame({"date": df.index[e], "exit": df.index[x], "side": s, "pnl": p, "rr": r, "bars": x - e + 1})
