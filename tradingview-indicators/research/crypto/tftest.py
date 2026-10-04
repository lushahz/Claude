"""Reversal Dots oscillator on crypto: which timeframe works with Entry / SL / TP1 / TP2 / TP3?
Binance spot 1h data (12 coins, 2019-2026), resampled to 4h, 1D, 1W. Signals as in the Pine script:
big buy = WaveTrend cross up with slow wave <= -53, big sell = cross down with slow wave >= 53;
setup = big signal while the higher timeframe's last closed slow wave is <= 0 (buy) / >= 0 (sell).
Entry next bar open. SL = swing low/high of the last 10 bars -/+ 0.25 ATR (or 1.5 ATR). TP1/TP2/TP3 = 1R/2R/3R,
one third each. Costs as % round trip."""
import numpy as np, pandas as pd, glob, zipfile, io, itertools, warnings; warnings.filterwarnings("ignore")
from numba import njit

def load(sym):
    fr = []
    for fn in sorted(glob.glob(f"zips/{sym}-1h-*.zip")):
        z = zipfile.ZipFile(fn); d = pd.read_csv(io.BytesIO(z.read(z.namelist()[0])), header=None, usecols=range(6))
        fr.append(d)
    d = pd.concat(fr); t = d[0].astype("int64")
    t = np.where(t > 1e14, t // 1000, t)          # Binance switched to microseconds in 2025
    d.index = pd.to_datetime(t, unit="ms"); d = d[~d.index.duplicated()].sort_index()
    d.columns = ["t", "o", "h", "l", "c", "v"]; return d[["o", "h", "l", "c"]].astype(float)

def rs(d, rule):
    kw = dict(label="left", closed="left")
    if rule == "1W": rule, kw = "W-MON", dict(label="left", closed="left")
    g = d.resample(rule, **kw)
    return pd.DataFrame({"o": g.o.first(), "h": g.h.max(), "l": g.l.min(), "c": g.c.last()}).dropna()

def ema(x, n): return pd.Series(x).ewm(span=n, adjust=False).mean().to_numpy()
def waves(d):
    src = ((d.h + d.l + d.c) / 3).to_numpy(); esa = ema(src, 9); de = ema(np.abs(src - esa), 9)
    de = np.maximum(de, np.abs(esa) * 1e-4); ci = (src - esa) / (0.015 * de)
    w1 = ema(ci, 12); w2 = pd.Series(w1).rolling(3).mean().to_numpy(); return w1, w2
def atr(d, n=14):
    h, l, c = d.h.to_numpy(), d.l.to_numpy(), d.c.to_numpy(); pc = np.r_[c[0], c[:-1]]
    tr = np.maximum(h - l, np.maximum(abs(h - pc), abs(l - pc))); return pd.Series(tr).ewm(alpha=1 / n, adjust=False).mean().to_numpy()

PERIOD = {"1h": "1h", "4h": "4h", "1D": "1D", "1W": "7D"}
def signals(d, dh, tf, htf):
    w1, w2 = waves(d); p1, p2 = np.r_[np.nan, w1[:-1]], np.r_[np.nan, w2[:-1]]
    up = (w1 > w2) & (p1 <= p2); dn = (w1 < w2) & (p1 >= p2)
    big_b = up & (w2 <= -53); big_s = dn & (w2 >= 53)
    _, hw2 = waves(dh); H = pd.Series(hw2, index=dh.index + pd.Timedelta(PERIOD[htf]))   # known after the HTF bar closes
    hv = H.reindex(d.index, method="ffill").to_numpy()
    e50 = ema(d.c.to_numpy(), 50); c = d.c.to_numpy()
    return {"setup": (big_b & (hv <= 0), big_s & (hv >= 0)), "big": (big_b, big_s),
            "confirm": (up & (w2 < 0) & (c > e50) & ~big_b, dn & (w2 > 0) & (c < e50) & ~big_s)}, (big_b, big_s)

@njit(cache=True)
def sim(o, h, l, c, a, L, S, oppL, oppS, swing, sl_mode, be, opp_exit, cost):
    n = len(c); out = np.zeros((n, 5)); k = 0; i = 0
    while i < n - 1:
        s = 1.0 if L[i] else (-1.0 if S[i] else 0.0)
        if s == 0.0 or not np.isfinite(a[i]): i += 1; continue
        e = i + 1; ep = o[e]
        if sl_mode == 0:
            st = (swing[i, 0] - 0.25 * a[i]) if s > 0 else (swing[i, 1] + 0.25 * a[i])
        else:
            st = ep - s * 1.5 * a[i]
        risk = s * (ep - st)
        if risk <= 0.2 * a[i]: risk = 0.2 * a[i]; st = ep - s * risk
        tp = np.array([ep + s * risk, ep + s * 2 * risk, ep + s * 3 * risk]); got = 0; pnl = 0.0; j = e
        while j < n:
            stop_hit = (l[j] <= st) if s > 0 else (h[j] >= st)
            if stop_hit:
                xp = min(o[j], st) if s > 0 else max(o[j], st)
                pnl += (3 - got) / 3.0 * s * (xp - ep); break
            while got < 3 and ((h[j] >= tp[got]) if s > 0 else (l[j] <= tp[got])):
                pnl += 1 / 3.0 * s * (tp[got] - ep); got += 1
                if be and got == 1: st = ep
            if got == 3: break
            if opp_exit and ((oppS[j]) if s > 0 else (oppL[j])):
                pnl += (3 - got) / 3.0 * s * (c[j] - ep); break
            if j == n - 1: pnl += (3 - got) / 3.0 * s * (c[j] - ep); break
            j += 1
        r_net = (pnl - cost * ep) / risk
        out[k, 0] = e; out[k, 1] = s; out[k, 2] = r_net; out[k, 3] = got; out[k, 4] = (pnl / ep - cost) * 100
        k += 1; i = j + 1
    return out[:k]

if __name__ == "__main__":
    SYMS = ["BTCUSDT", "ETHUSDT", "SOLUSDT", "BNBUSDT", "XRPUSDT", "ADAUSDT", "DOGEUSDT", "LINKUSDT", "AVAXUSDT", "LTCUSDT", "DOTUSDT", "TRXUSDT"]
    TF = [("1h", "4h"), ("4h", "1D"), ("1D", "1W")]
    rows = []; allT = []
    for sym in SYMS:
        d1 = load(sym); frames = {"1h": d1, "4h": rs(d1, "4h"), "1D": rs(d1, "1D"), "1W": rs(d1, "1W")}
        for tf, htf in TF:
            d = frames[tf]; dh = frames[htf]
            sig, (bb, bs) = signals(d, dh, tf, htf)
            o, h, l, c = (d[k].to_numpy() for k in "ohlc"); a = atr(d)
            swing = np.c_[pd.Series(l).rolling(10, min_periods=1).min().to_numpy(), pd.Series(h).rolling(10, min_periods=1).max().to_numpy()]
            for trig, sl_mode, be, opp, cost in itertools.product(("setup", "big", "confirm"), (0, 1), (False, True), (False, True), (0.001, 0.002)):
                L, S = sig[trig]
                R = sim(o, h, l, c, a, L, S, bb, bs, swing, sl_mode, be, opp, cost)
                T = pd.DataFrame(R, columns=["e", "side", "R", "tps", "pct"]); T["date"] = d.index[T.e.astype(int)]
                T["sym"] = sym; T["tf"] = tf; T["trig"] = trig; T["sl"] = ["swing", "1.5ATR"][sl_mode]; T["be"] = be; T["opp"] = opp; T["cost"] = cost
                allT.append(T)
        print(sym, "done", flush=True)
    A = pd.concat(allT); A = A[A.date >= "2020-01-01"]; A.to_pickle("tf_trades.pkl")
    def st(x):
        w = x.R[x.R > 0].sum(); ls = -x.R[x.R < 0].sum()
        yrs = (x.date.max() - x.date.min()).days / 365 if len(x) > 1 else 1
        return pd.Series({"trades": len(x), "per_coin_yr": round(len(x) / 12 / 6.7, 1), "win%": round(100 * (x.R > 0).mean(), 1),
                          "TP1%": round(100 * (x.tps >= 1).mean(), 1), "TP3%": round(100 * (x.tps >= 3).mean(), 1),
                          "avgR": round(x.R.mean(), 3), "PF": round(w / ls, 2) if ls else np.nan, "avg%": round(x.pct.mean(), 2),
                          "coins+": int((x.groupby("sym").R.sum() > 0).sum())})
    pd.set_option("display.width", 250); pd.set_option("display.max_rows", 500)
    base = A[(A.cost == 0.001)]
    G = base.groupby(["tf", "trig", "sl", "be", "opp"]).apply(st).reset_index()
    print(G.sort_values(["tf", "PF"], ascending=[True, False]).to_string(index=False))
