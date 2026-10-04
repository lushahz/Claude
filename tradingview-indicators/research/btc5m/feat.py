"""Feature engine for BTC 5m (all values known at the bar's close)."""
import numpy as np, pandas as pd
from numba import njit
def ema(x, n): return pd.Series(x).ewm(span=n, adjust=False).mean().to_numpy()
def rma(x, n): return pd.Series(x).ewm(alpha=1.0 / n, adjust=False).mean().to_numpy()
def sma(x, n): return pd.Series(x).rolling(n, min_periods=n).mean().to_numpy()
def rstd(x, n): return pd.Series(x).rolling(n, min_periods=n).std(ddof=0).to_numpy()
def rmax(x, n): return pd.Series(x).rolling(n, min_periods=1).max().to_numpy()
def rmin(x, n): return pd.Series(x).rolling(n, min_periods=1).min().to_numpy()
def lag(x, k=1): return np.r_[np.full(k, np.nan), x[:-k]]
def rsi(c, n=14):
    ch = np.diff(c, prepend=c[0]); up = rma(np.maximum(ch, 0), n); dn = rma(np.maximum(-ch, 0), n)
    with np.errstate(all="ignore"): return np.where(dn == 0, 100.0, 100 - 100 / (1 + up / dn))
def atr(h, l, c, n=14):
    pc = np.r_[c[0], c[:-1]]; return rma(np.maximum(h - l, np.maximum(abs(h - pc), abs(l - pc))), n)
def waves(h, l, c):
    src = (h + l + c) / 3; esa = ema(src, 9); de = np.maximum(ema(np.abs(src - esa), 9), np.abs(esa) * 1e-4)
    w1 = ema((src - esa) / (0.015 * de), 12); return w1, sma(w1, 3)
def stochk(c, n=14, k=3):
    r = rsi(np.log(c), n); lo, hi = rmin(r, n), rmax(r, n)
    return sma(100 * (r - lo) / np.maximum(hi - lo, 1e-12), k)

@njit(cache=True)
def divergences(w2, h, l, top_lim, bot_lim, lookback):
    n = len(w2); bear = np.zeros(n, np.bool_); bull = np.zeros(n, np.bool_)
    pTw = np.nan; pTp = np.nan; pTb = -1; pBw = np.nan; pBp = np.nan; pBb = -1
    for i in range(4, n):
        if w2[i-4] < w2[i-2] and w2[i-3] < w2[i-2] and w2[i-2] > w2[i-1] and w2[i-2] > w2[i] and w2[i-2] >= top_lim:
            if pTb >= 0 and (i - 2) - pTb <= lookback and w2[i-2] < pTw and h[i-2] > pTp: bear[i] = True
            pTw = w2[i-2]; pTp = h[i-2]; pTb = i - 2
        if w2[i-4] > w2[i-2] and w2[i-3] > w2[i-2] and w2[i-2] < w2[i-1] and w2[i-2] < w2[i] and w2[i-2] <= bot_lim:
            if pBb >= 0 and (i - 2) - pBb <= lookback and w2[i-2] > pBw and l[i-2] < pBp: bull[i] = True
            pBw = w2[i-2]; pBp = l[i-2]; pBb = i - 2
    return bull, bear

def htf(df, rule):
    g = df.resample(rule, label="left", closed="left")
    H = pd.DataFrame({"h": g.h.max(), "l": g.l.min(), "c": g.c.last()}).dropna()
    hh, ll, cc = (H[k].to_numpy() for k in "hlc"); _, w2 = waves(hh, ll, cc)
    X = pd.DataFrame({"wt2": w2, "rsi": rsi(cc), "trend": np.sign(cc - ema(cc, 50)) + np.sign(ema(cc, 20) - ema(cc, 50)),
                      "e50": (cc - ema(cc, 50)) / atr(hh, ll, cc)}, index=H.index + pd.Timedelta(rule))
    return X.reindex(df.index, method="ffill")

def features(df):
    o, h, l, c, v = (df[k].to_numpy() for k in ("o", "h", "l", "c", "v"))
    F = pd.DataFrame(index=df.index); a = atr(h, l, c); F["atr"] = a; F["atr_pct"] = a / c * 100
    F["atr_rel"] = a / sma(a, 288)
    w1, w2 = waves(h, l, c); F["wt1"], F["wt2"] = w1, w2
    F["cross_up"] = (w1 > w2) & (lag(w1) <= lag(w2)); F["cross_dn"] = (w1 < w2) & (lag(w1) >= lag(w2))
    F["turn_up"] = (w1 > lag(w1)) & (lag(w1) <= lag(w1, 2)); F["turn_dn"] = (w1 < lag(w1)) & (lag(w1) >= lag(w1, 2))
    F["stk"] = stochk(c); F["rsi"] = rsi(c); F["rsi7"] = rsi(c, 7)
    bull, bear = divergences(w2, h, l, 45.0, -40.0, 60); F["bull_div"] = bull; F["bear_div"] = bear
    F["bull_div6"] = pd.Series(bull).rolling(7, min_periods=1).max().to_numpy() > 0
    F["bear_div6"] = pd.Series(bear).rolling(7, min_periods=1).max().to_numpy() > 0
    for n in (20, 50, 200): F[f"d_ema{n}"] = (c - ema(c, n)) / a
    mid, sd = sma(c, 20), rstd(c, 20); F["bb"] = (c - mid) / np.maximum(2 * sd, 1e-12); F["bbw"] = 4 * sd / a
    for n in (1, 3, 12, 48): F[f"ret{n}"] = (c - lag(c, n)) / a
    rng = np.maximum(h - l, 1e-12); F["clv"] = (c - l) / rng; F["body"] = (c - o) / a; F["range"] = (h - l) / a
    F["wick_dn"] = (np.minimum(o, c) - l) / a; F["wick_up"] = (h - np.maximum(o, c)) / a
    # order flow: taker buy share and cumulative delta
    tb = df.tbv.to_numpy(); delta = 2 * tb - v
    F["tbr"] = tb / np.maximum(v, 1e-12); F["vz"] = (v - sma(v, 288)) / np.maximum(rstd(v, 288), 1e-12)
    for n in (3, 12): F[f"cvd{n}"] = pd.Series(delta).rolling(n).sum().to_numpy() / np.maximum(sma(v, 288) * n, 1e-12)
    fd = 2 * df.ftbv.to_numpy() - df.fv.to_numpy(); F["fcvd12"] = pd.Series(fd).rolling(12).sum().to_numpy() / np.maximum(sma(df.fv.to_numpy(), 288) * 12, 1e-12)
    # VWAP of the UTC day
    day = df.index.normalize(); pv = pd.Series((h + l + c) / 3 * v, index=df.index)
    vw = pv.groupby(day).cumsum() / pd.Series(v, index=df.index).groupby(day).cumsum()
    F["d_vwap"] = (c - vw.to_numpy()) / a
    dd = pd.DataFrame({"h": h, "l": l}, index=df.index).groupby(day)
    F["d_dayhi"] = (c - dd.h.cummax().to_numpy()) / a; F["d_daylo"] = (c - dd.l.cummin().to_numpy()) / a
    daily = pd.DataFrame({"h": h, "l": l, "c": c}, index=df.index).resample("1D").agg({"h": "max", "l": "min", "c": "last"}).shift(1)
    pdv = daily.reindex(day).to_numpy(); F["d_pdh"] = (c - pdv[:, 0]) / a; F["d_pdl"] = (c - pdv[:, 1]) / a
    # derivatives
    F["basis"] = (df.fc.to_numpy() / c - 1) * 1e4                                 # bp
    F["prem_z"] = pd.Series(df.prem.to_numpy()).sub(pd.Series(df.prem.to_numpy()).rolling(288).mean()).div(pd.Series(df.prem.to_numpy()).rolling(288).std()).to_numpy()
    F["fund"] = df.fund.to_numpy() * 1e4                                         # bp per 8h
    # ETH relative strength
    e = df.eth.to_numpy(); F["eth_rel12"] = (np.log(e / lag(e, 12)) - np.log(c / lag(c, 12))) / (rstd(np.diff(np.log(c), prepend=np.nan), 288) * np.sqrt(12))
    # time
    F["hour"] = df.index.hour; F["dow"] = df.index.dayofweek
    # higher timeframes (completed bars only)
    for rule, tag in (("15min", "m15"), ("1h", "h1"), ("4h", "h4"), ("1D", "d1")):
        X = htf(df, rule)
        for col in X.columns: F[f"{tag}_{col}"] = X[col].to_numpy()
    return F

if __name__ == "__main__":
    import time; t0 = time.time()
    df = pd.read_pickle("btc5m_raw.pkl"); F = features(df); F.to_pickle("btc5m_feat.pkl")
    print(F.shape, f"{time.time()-t0:.0f}s"); print(F.describe().T[["mean", "std"]].round(3).to_string())
