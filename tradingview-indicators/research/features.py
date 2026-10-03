import numpy as np, pandas as pd
from common import *
from revdots import waves

def features(d):
    c = d.c.to_numpy(); h = d.h.to_numpy(); l = d.l.to_numpy(); o = d.o.to_numpy(); v = d.v.to_numpy()
    f = pd.DataFrame(index=d.index)
    w1, w2 = waves(d)
    f["w1"], f["w2"] = w1, w2
    up = np.r_[False, (w1[1:] > w2[1:]) & (w1[:-1] <= w2[:-1])]
    dn = np.r_[False, (w1[1:] < w2[1:]) & (w1[:-1] >= w2[:-1])]
    f["up"], f["dn"] = up, dn
    r = rsi(c, 14); f["rsi"] = r
    f["k"] = sma(stoch(r, 14), 3)
    a = atr(d); f["atr"] = a; f["atrp"] = a / np.abs(c)
    e200 = ema(c, 200); e50 = ema(c, 50); e20 = ema(c, 20)
    f["d200"] = (c - e200) / a          # distance from EMA200 in ATRs
    f["d50"] = (c - e50) / a
    f["d20"] = (c - e20) / a
    hh = pd.Series(h).rolling(252, min_periods=60).max().to_numpy()
    ll = pd.Series(l).rolling(252, min_periods=60).min().to_numpy()
    f["dd252"] = (c - hh) / a           # drawdown from 1y high in ATRs
    f["ru252"] = (c - ll) / a
    lo20 = pd.Series(l).rolling(20).min().to_numpy(); hi20 = pd.Series(h).rolling(20).max().to_numpy()
    f["near_lo20"] = (pd.Series(l).rolling(5).min().to_numpy() <= lo20 + 1e-12)
    f["near_hi20"] = (pd.Series(h).rolling(5).max().to_numpy() >= hi20 - 1e-12)
    vv = pd.Series(np.where(v > 0, v, np.nan))
    f["volz"] = ((vv - vv.rolling(50, min_periods=20).mean()) / vv.rolling(50, min_periods=20).std()).to_numpy()
    f["volz5"] = pd.Series(f["volz"].to_numpy()).rolling(5, min_periods=1).max().to_numpy()
    rng = np.where(h - l > 0, h - l, np.nan)
    f["clv"] = (c - l) / rng            # close location in bar range (1 = at high)
    f["body"] = (c - o) / a
    f["ret5"] = pd.Series(np.log(np.abs(c))).diff(5).to_numpy() / f["atrp"].to_numpy()
    # momentum oscillators slope
    f["w1_up"] = np.r_[False, w1[1:] > w1[:-1]]
    return f

def divergences(w2, lo, hi, bot_lim=-40, top_lim=45, look=60):
    n = len(w2); bull = np.zeros(n, bool); bear = np.zeros(n, bool)
    pb = pt = None
    for i in range(4, n):
        if w2[i-4] > w2[i-2] and w2[i-3] > w2[i-2] and w2[i-2] < w2[i-1] and w2[i-2] < w2[i] and w2[i-2] <= bot_lim:
            if pb and (i - 2 - pb[0]) <= look and w2[i-2] > pb[1] and lo[i-2] < pb[2]: bull[i] = True
            pb = (i - 2, w2[i-2], lo[i-2])
        if w2[i-4] < w2[i-2] and w2[i-3] < w2[i-2] and w2[i-2] > w2[i-1] and w2[i-2] > w2[i] and w2[i-2] >= top_lim:
            if pt and (i - 2 - pt[0]) <= look and w2[i-2] < pt[1] and hi[i-2] > pt[2]: bear[i] = True
            pt = (i - 2, w2[i-2], hi[i-2])
    return bull, bear

def recent(x, n):
    return pd.Series(x.astype(float)).rolling(n, min_periods=1).max().to_numpy() > 0

def all_data(thr_mult=7.0, min_thr=0.04):
    out = {}
    for _, u in U.iterrows():
        d = load(u.file)
        if (d.c <= 0).any():
            d = d[d.c > 0]
        f = features(d)
        bull, bear = divergences(f.w2.to_numpy(), d.l.to_numpy(), d.h.to_numpy())
        f["bull_div"], f["bear_div"] = bull, bear
        thr = max(min_thr, thr_mult * np.nanmedian(f.atrp))
        piv = zigzag(d.c.to_numpy(), thr)
        out[u.sym] = dict(cls=u.cls, d=d, f=f, piv=piv, thr=thr)
    return out
