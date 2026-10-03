import numpy as np, pandas as pd
from revdots import ema, rsi, sma
from lab import rmin, rmax
g = pd.read_csv("macro.csv", index_col=0, parse_dates=True)
g.index = g.index - pd.Timedelta(days=1)          # CMC 00:00 snapshot = previous day's daily close
def wt_close(c, ch=9, avg=12, ma=3):
    esa = ema(c, ch); de = ema(np.abs(c - esa), ch)
    ci = np.where(de == 0, 0, (c - esa) / (0.015 * np.where(de == 0, 1, de))); w1 = ema(ci, avg); return w1, sma(w1, ma)
M = pd.DataFrame(index=g.index)
for name in ["total", "btcd", "usdtd"]:
    s = g[name].to_numpy(dtype=float)
    M[name] = s; M[name + "_rsi"] = rsi(s, 14)
    M[name + "_e20"] = ema(s, 20); M[name + "_e50"] = ema(s, 50); M[name + "_e200"] = ema(s, 200)
    w1, w2 = wt_close(s); M[name + "_w2"] = w2
hi = pd.Series(g.total.to_numpy()).rolling(365, min_periods=100).max().to_numpy()
M["total_dd"] = g.total.to_numpy() / hi - 1
e50, e200 = M.total_e50.to_numpy(), M.total_e200.to_numpy()
M["total_deathx"] = (e50 < e200) & np.r_[False, (e50 >= e200)[:-1]]
M["total_golden"] = e50 > e200
M = M[M.index >= "2014-01-01"]
def attach(x):
    m = M.reindex(x["d"].index).ffill()
    return m
