import pickle, numpy as np, pandas as pd, itertools
from features import recent
data = pickle.load(open("data.pkl","rb"))
SPLIT = pd.Timestamp("2019-01-01")

def rmin(x, n): return pd.Series(x).rolling(n, min_periods=1).min().to_numpy()
def rmax(x, n): return pd.Series(x).rolling(n, min_periods=1).max().to_numpy()

def cooldown(sig, n):
    out = np.zeros_like(sig); last = -10**9
    for i in np.flatnonzero(sig):
        if i - last > n: out[i] = True; last = i
    return out

def outcomes(x, side, tgt=4.0, stp=2.0, horizon=40):
    """For every bar: enter next open; +1 if target (tgt ATR) hit before stop (stp ATR) within horizon, 0 otherwise; fwd 20-bar return in ATR."""
    d = x["d"]; f = x["f"]
    o, h, l, c = d.o.to_numpy(), d.h.to_numpy(), d.l.to_numpy(), d.c.to_numpy(); a = f.atr.to_numpy()
    n = len(d); win = np.full(n, np.nan); fwd = np.full(n, np.nan)
    return o, h, l, c, a, n

def eval_signals(x, sig, side, tgt=4.0, stp=2.0, horizon=40):
    d = x["d"]; f = x["f"]
    o, h, l, c = d.o.to_numpy(), d.h.to_numpy(), d.l.to_numpy(), d.c.to_numpy(); a = f.atr.to_numpy()
    n = len(d); res = []
    piv = [i for i, t in x["piv"] if t == (-1 if side > 0 else 1)]
    piv = np.array(piv) if piv else np.array([-10**9])
    for i in np.flatnonzero(sig):
        if i + 1 >= n or np.isnan(a[i]): continue
        ep = o[i + 1]; T = ep + side * tgt * a[i]; S = ep - side * stp * a[i]
        outcome = 0.0; j_end = min(n, i + 1 + horizon)
        for j in range(i + 1, j_end):
            if side > 0:
                if l[j] <= S: outcome = 0; break
                if h[j] >= T: outcome = 1; break
            else:
                if h[j] >= S: outcome = 0; break
                if l[j] <= T: outcome = 1; break
        else:
            outcome = 0.5 if side * (c[j_end - 1] - ep) > 0 else 0   # timed out
        k = min(n - 1, i + 20)
        fwd = side * (c[k] - ep) / a[i]
        near = np.min(np.abs(piv - i)) <= 10 if True else False
        caught = np.any((piv >= i - 10) & (piv <= i + 5))
        res.append((d.index[i], outcome, fwd, caught))
    return res

def build(x, side, p):
    f = x["f"]; w2 = f.w2.to_numpy(); r = f.rsi.to_numpy(); d50 = f.d50.to_numpy()
    cross = f.up.to_numpy() if side > 0 else f.dn.to_numpy()
    s = side
    sig = cross.copy()
    if p.get("wave") is not None:
        sig &= (s * rmax(-s * w2, 3) * -1 <= p["wave"]) if s > 0 else (rmax(w2, 3) >= -p["wave"])
    if p.get("rsi") is not None:
        sig &= (rmin(r, p["rsi_look"]) <= p["rsi"]) if s > 0 else (rmax(r, p["rsi_look"]) >= 100 - p["rsi"])
    if p.get("stretch") is not None:
        sig &= (rmin(d50, 10) <= -p["stretch"]) if s > 0 else (rmax(d50, 10) >= p["stretch"])
    if p.get("div"):
        dv = f.bull_div.to_numpy() if s > 0 else f.bear_div.to_numpy()
        sig &= recent(dv, 10)
    if p.get("candle"):
        clv = f.clv.to_numpy()
        sig &= (clv >= 0.5) if s > 0 else (clv <= 0.5)
    if p.get("cool"):
        sig = cooldown(sig, p["cool"])
    return sig

def run(p, side, period=None):
    allres = []; nsig = 0; years = 0
    for sym, x in data.items():
        sig = build(x, side, p)
        sig[:250] = False
        idx = x["d"].index
        if period == "IS": sig &= (idx < SPLIT)
        if period == "OOS": sig &= (idx >= SPLIT)
        res = eval_signals(x, sig, side)
        allres += [(sym, x["cls"]) + r for r in res]
        span = idx[250:]
        if period == "IS": span = span[span < SPLIT]
        if period == "OOS": span = span[span >= SPLIT]
        years += len(span) / 252
    R = pd.DataFrame(allres, columns=["sym", "cls", "date", "win", "fwd", "caught"])
    return R, years

def summary(R, years):
    if len(R) == 0: return dict(n=0)
    return dict(n=len(R), per_mkt_yr=round(len(R) / years, 2), winrate=round(R.win.mean(), 3),
                fwd20=round(R.fwd.mean(), 2), caught=round(R.caught.mean(), 3))
