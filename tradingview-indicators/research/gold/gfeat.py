"""Gold 5-minute feature engine. All features use only information available at the bar's close."""
import numpy as np, pandas as pd
from numba import njit

def ema(x, n):  return pd.Series(x).ewm(span=n, adjust=False).mean().to_numpy()
def rma(x, n):  return pd.Series(x).ewm(alpha=1.0 / n, adjust=False).mean().to_numpy()
def sma(x, n):  return pd.Series(x).rolling(n, min_periods=n).mean().to_numpy()
def rstd(x, n): return pd.Series(x).rolling(n, min_periods=n).std(ddof=0).to_numpy()
def rmax(x, n): return pd.Series(x).rolling(n, min_periods=1).max().to_numpy()
def rmin(x, n): return pd.Series(x).rolling(n, min_periods=1).min().to_numpy()

def rsi(c, n=14):
    ch = np.diff(c, prepend=c[0])
    up = rma(np.maximum(ch, 0), n); dn = rma(np.maximum(-ch, 0), n)
    with np.errstate(all="ignore"):
        return np.where(dn == 0, 100.0, 100 - 100 / (1 + up / dn))

def atr(h, l, c, n=14):
    pc = np.r_[c[0], c[:-1]]
    tr = np.maximum(h - l, np.maximum(np.abs(h - pc), np.abs(l - pc)))
    return rma(tr, n)

def wavetrend(h, l, c, ch=9, avg=12, ma=3):
    src = (h + l + c) / 3
    esa = ema(src, ch); de = ema(np.abs(src - esa), ch)
    de = np.maximum(de, np.abs(esa) * 1e-4)
    w1 = ema((src - esa) / (0.015 * de), avg); w2 = sma(w1, ma)
    return w1, w2

def adx(h, l, c, n=14):
    up = np.diff(h, prepend=h[0]); dn = -np.diff(l, prepend=l[0])
    pdm = np.where((up > dn) & (up > 0), up, 0.0); mdm = np.where((dn > up) & (dn > 0), dn, 0.0)
    a = atr(h, l, c, n)
    with np.errstate(all="ignore"):
        pdi = 100 * rma(pdm, n) / a; mdi = 100 * rma(mdm, n) / a
        dx = 100 * np.abs(pdi - mdi) / np.maximum(pdi + mdi, 1e-12)
    return rma(dx, n), pdi, mdi

@njit(cache=True)
def supertrend(h, l, c, a, mult):
    n = len(c); dirn = np.ones(n); up = np.zeros(n); dn = np.zeros(n)
    for i in range(n):
        hl2 = (h[i] + l[i]) / 2
        bu = hl2 - mult * a[i]; bd = hl2 + mult * a[i]
        if i == 0:
            up[i] = bu; dn[i] = bd; continue
        up[i] = max(bu, up[i-1]) if c[i-1] > up[i-1] else bu
        dn[i] = min(bd, dn[i-1]) if c[i-1] < dn[i-1] else bd
        if dirn[i-1] == -1 and c[i] > dn[i-1]: dirn[i] = 1
        elif dirn[i-1] == 1 and c[i] < up[i-1]: dirn[i] = -1
        else: dirn[i] = dirn[i-1]
    return dirn

def htf(df, rule, cols):
    """Completed higher-timeframe bars only: value of the last *closed* HTF bar, forward-filled onto 5m bars."""
    g = df.resample(rule, label="left", closed="left")
    H = pd.DataFrame({"o": g.o.first(), "h": g.h.max(), "l": g.l.min(), "c": g.c.last()}).dropna()
    out = {}
    c = H.c.to_numpy()
    if "ema" in cols:
        e20, e50 = ema(c, 20), ema(c, 50)
        out["trend"] = np.sign(c - e50) + np.sign(e20 - e50)          # -2..2
        out["e50dist"] = (c - e50) / atr(H.h.to_numpy(), H.l.to_numpy(), c)
    if "rsi" in cols: out["rsi"] = rsi(c)
    if "wt" in cols:
        _, w2 = wavetrend(H.h.to_numpy(), H.l.to_numpy(), c); out["wt"] = w2
    X = pd.DataFrame(out, index=H.index)
    # an HTF bar labelled t (covering t..t+rule) is known only at t+rule: shift the index
    X.index = X.index + pd.Timedelta(rule)
    return X.reindex(df.index, method="ffill")

def features(df):
    o, h, l, c = (df[k].to_numpy() for k in "ohlc")
    f = pd.DataFrame(index=df.index)
    a = atr(h, l, c, 14); f["atr"] = a
    f["atr_rel"] = a / sma(a, 288)                                  # vs 1-day average
    for n in (9, 21, 50, 200):
        e = ema(c, n); f[f"d_ema{n}"] = (c - e) / a
    f["ema_stack"] = np.sign(ema(c, 9) - ema(c, 21)) + np.sign(ema(c, 21) - ema(c, 50)) + np.sign(ema(c, 50) - ema(c, 200))
    f["rsi"] = rsi(c, 14); f["rsi7"] = rsi(c, 7)
    lo14, hi14 = rmin(l, 14), rmax(h, 14)
    k = 100 * (c - lo14) / np.maximum(hi14 - lo14, 1e-12); f["stoch"] = sma(k, 3)
    m = ema(c, 12) - ema(c, 26); sig = ema(m, 9); f["macd_h"] = (m - sig) / a; f["macd"] = m / a
    w1, w2 = wavetrend(h, l, c); f["wt1"], f["wt2"] = w1, w2
    f["wt_up"] = (w1 > w2) & (np.r_[w1[0], w1[:-1]] <= np.r_[w2[0], w2[:-1]])
    f["wt_dn"] = (w1 < w2) & (np.r_[w1[0], w1[:-1]] >= np.r_[w2[0], w2[:-1]])
    tp = (h + l + c) / 3; f["cci"] = (tp - sma(tp, 20)) / np.maximum(rstd(tp, 20), 1e-12)
    mid = sma(c, 20); sd = rstd(c, 20)
    f["bb_pos"] = (c - mid) / np.maximum(2 * sd, 1e-12); f["bb_width"] = 4 * sd / a
    f["kc_pos"] = (c - ema(c, 20)) / (2 * a)
    f["don_pos"] = (c - rmin(l, 20)) / np.maximum(rmax(h, 20) - rmin(l, 20), 1e-12)
    ad, pdi, mdi = adx(h, l, c); f["adx"] = ad; f["di"] = pdi - mdi
    f["st"] = supertrend(h, l, c, atr(h, l, c, 10), 3.0)
    f["roc3"] = (c - np.r_[np.full(3, c[0]), c[:-3]]) / a
    f["roc12"] = (c - np.r_[np.full(12, c[0]), c[:-12]]) / a
    rng = np.maximum(h - l, 1e-12)
    f["clv"] = (c - l) / rng; f["body"] = (c - o) / a; f["range"] = (h - l) / a
    f["wick_up"] = (h - np.maximum(o, c)) / a; f["wick_dn"] = (np.minimum(o, c) - l) / a
    # time (UTC + New York, DST aware)
    ny = df.index.tz_localize("UTC").tz_convert("America/New_York")
    f["hour_utc"] = df.index.hour + df.index.minute / 60
    f["ny_min"] = ny.hour * 60 + ny.minute
    f["dow"] = df.index.dayofweek
    # trading day = rolls at 17:00 New York
    tday = (ny - pd.Timedelta(hours=17)).normalize().tz_localize(None)
    f["tday"] = tday
    d = pd.DataFrame({"h": h, "l": l, "c": c, "tday": tday}, index=df.index)
    dg = d.groupby("tday")
    # session TWAP (no real volume in spot gold data)
    f["d_twap"] = (c - dg.c.transform(lambda s: s.expanding().mean()).to_numpy()) / a
    # prior day high / low / close
    daily = dg.agg(H=("h", "max"), L=("l", "min"), C=("c", "last"))
    prev = daily.shift(1).reindex(tday).to_numpy()
    f["d_pdh"] = (c - prev[:, 0]) / a; f["d_pdl"] = (c - prev[:, 1]) / a; f["d_pdc"] = (c - prev[:, 2]) / a
    piv = (prev[:, 0] + prev[:, 1] + prev[:, 2]) / 3
    f["d_pivot"] = (c - piv) / a
    # day so far high/low
    f["d_dayhi"] = (c - dg.h.cummax().to_numpy()) / a; f["d_daylo"] = (c - dg.l.cummin().to_numpy()) / a
    # Asian range (17:00-03:00 NY = before London) high/low for the trading day
    asia = (f["ny_min"] >= 17 * 60) | (f["ny_min"] < 3 * 60)
    ah = pd.Series(np.where(asia, h, np.nan), index=df.index).groupby(tday).cummax()
    al = pd.Series(np.where(asia, l, np.nan), index=df.index).groupby(tday).cummin()
    ah = ah.groupby(tday).ffill().to_numpy(); al = al.groupby(tday).ffill().to_numpy()
    f["d_asia_hi"] = (c - ah) / a; f["d_asia_lo"] = (c - al) / a; f["asia_rng"] = (ah - al) / a
    # round numbers
    f["d_r10"] = ((c + 5) % 10 - 5) / a; f["d_r50"] = ((c + 25) % 50 - 25) / a
    # shock bar (news proxy): range > 3x ATR in the last 6 bars
    f["shock6"] = rmax((h - l) / np.r_[a[0], a[:-1]], 6)
    # higher timeframes
    for rule, tag in (("15min", "m15"), ("1h", "h1"), ("4h", "h4")):
        X = htf(df, rule, ("ema", "rsi", "wt"))
        for col in X.columns: f[f"{tag}_{col}"] = X[col].to_numpy()
    return f
