"""Part B: entry filters on top of the same signals, tested with three exit shapes."""
import numpy as np, pandas as pd, warnings; warnings.filterwarnings("ignore")
from glab import run, stats
df = pd.read_pickle("bars/XAUUSD_5m.pkl"); f = pd.read_pickle("bars/XAUUSD_feat.pkl"); X = pd.read_pickle("bars/XAUUSD_xfeat.pkl")
def nz(x): return np.nan_to_num(np.asarray(x, dtype=float), nan=0.0)
L0 = np.load("sigL.npy"); S0 = np.load("sigS.npy")
ny = f.ny_min.to_numpy(); a = f.atr.to_numpy(); res = nz(X.gd_res12)
h1 = nz(f.h1_trend); m15 = nz(f.m15_trend); h4 = nz(f.h4_trend); rsi = nz(f.rsi); adx = nz(f.adx)
dow = f.dow.to_numpy(); arel = nz(f.atr_rel); d50 = nz(f.d_ema50); shock = nz(f.shock6)
F = {
 "none": (np.ones_like(L0), np.ones_like(S0)),
 "h1 trend agrees": (h1 > 0, h1 < 0),
 "h1+m15 trend agree": ((h1 > 0) & (m15 >= 0), (h1 < 0) & (m15 <= 0)),
 "h4 strong (=2)": (h4 == 2, h4 == -2),
 "not 05:00-06:59 NY": (~((ny >= 300) & (ny < 420)),) * 2,
 "NY hours only (08-11:59)": (((ny >= 480) & (ny < 720)),) * 2,
 "ATR >= $3": (a >= 3,) * 2,
 "ATR not spiking (atr_rel<1.5)": (arel < 1.5,) * 2,
 "no news shock (<3x)": (shock < 3,) * 2,
 "RSI room (L<60,S>40)": (rsi < 60, rsi > 40),
 "with EMA50 side": (d50 > 0, d50 < 0),
 "ADX < 25 (ranging)": (adx < 25,) * 2,
 "ADX > 25 (trending)": (adx > 25,) * 2,
 "Mon-Thu only": (dow < 4,) * 2,
 "shorts only": (np.zeros_like(L0), np.ones_like(S0)),
}
EX = {"s1.5/t2 (now)": dict(stop_k=1.5, tgt_k=2.0, max_bars=36), "s2/t2": dict(stop_k=2.0, tgt_k=2.0, max_bars=36),
      "s2.5/t1.25": dict(stop_k=2.5, tgt_k=1.25, max_bars=36)}
rows = []
for fn, (fl, fs) in F.items():
    L = L0 & fl.astype(bool); S = S0 & fs.astype(bool)
    for en, kw in EX.items():
        T = run(df, f, L | S, np.where(L, 1.0, -1.0), cost=0.30, **kw)
        r = {"filter": fn, "exit": en}
        for per, m in (("09-19", T.date < "2020"), ("20-22", (T.date >= "2020") & (T.date < "2023")), ("23-26", T.date >= "2023")):
            s_ = stats(T[m]); r[f"{per}_n"] = s_["n"]; r[f"{per}_win"] = s_.get("win"); r[f"{per}_pf"] = s_.get("pf")
        rows.append(r)
R = pd.DataFrame(rows); R.to_pickle("winrate_filters.pkl")
pd.set_option("display.width", 250); pd.set_option("display.max_rows", 400)
print(R.to_string(index=False))
