"""Same oscillator trade rules on 5-minute crypto (HTF 1H, as the script's auto setting), BTC/ETH/SOL 2024-2026."""
import numpy as np, pandas as pd, glob, zipfile, io, itertools, warnings; warnings.filterwarnings("ignore")
import tftest as T   # reuse waves, atr, sim (module-level backtest is guarded below)
def load5(sym):
    fr = []
    for fn in sorted(glob.glob(f"z5/{sym}-5m-*.zip")):
        z = zipfile.ZipFile(fn); fr.append(pd.read_csv(io.BytesIO(z.read(z.namelist()[0])), header=None, usecols=range(6)))
    d = pd.concat(fr); t = d[0].astype("int64"); t = np.where(t > 1e14, t // 1000, t)
    d.index = pd.to_datetime(t, unit="ms"); d = d[~d.index.duplicated()].sort_index()
    d.columns = ["t", "o", "h", "l", "c", "v"]; return d[["o", "h", "l", "c"]].astype(float)
T.PERIOD["15m"] = "15min"
rows = []
for sym in ("BTCUSDT", "ETHUSDT", "SOLUSDT"):
    d = load5(sym); dh = T.rs(d, "1h")
    for tf, dd, hh, htf in (("5m", d, dh, "1h"), ("15m", T.rs(d, "15min"), dh, "1h")):
        sig, (bb, bs) = T.signals(dd, hh, tf, htf)
        o, h, l, c = (dd[k].to_numpy() for k in "ohlc"); a = T.atr(dd)
        swing = np.c_[pd.Series(l).rolling(10, min_periods=1).min().to_numpy(), pd.Series(h).rolling(10, min_periods=1).max().to_numpy()]
        for trig, cost, longs in itertools.product(("big", "setup", "confirm"), (0.001, 0.0004, 0.0), (True, False)):
            L, S = sig[trig]
            if longs: S = np.zeros_like(S)
            R = T.sim(o, h, l, c, a, L, S, bb, bs, swing, 0, True, False, cost)
            rows.append(pd.DataFrame({"R": R[:, 2], "tps": R[:, 3], "pct": R[:, 4], "sym": sym, "tf": tf, "trig": trig, "cost": cost, "dir": "long" if longs else "long+short"}))
A = pd.concat(rows)
def st(x):
    w = x.R[x.R > 0].sum(); ls = -x.R[x.R < 0].sum()
    return pd.Series({"trades": len(x), "per_coin_day": round(len(x) / 3 / 1000, 1), "win%": round(100 * (x.R > 0).mean(), 1), "PF": round(w / ls, 2), "avg%": round(x.pct.mean(), 3), "coins+": int((x.groupby("sym").R.sum() > 0).sum())})
pd.set_option("display.width", 200); pd.set_option("display.max_rows", 100)
print(A.groupby(["tf", "dir", "trig", "cost"]).apply(st).to_string())
