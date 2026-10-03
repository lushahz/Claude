"""Final 1:2 configuration: current signals + 1h trend agreement, stop 1.25 ATR, target 2.5 ATR, max 72 bars."""
import numpy as np, pandas as pd, warnings; warnings.filterwarnings("ignore")
from glab import run, stats, session_mask
import grid2_fams as G
df, f = G.df, G.f; X = pd.read_pickle("bars/XAUUSD_xfeat.pkl")
def nz(x): return np.nan_to_num(np.asarray(x, dtype=float), nan=0.0)
c = df.c.to_numpy(); cp = np.r_[c[0], c[:-1]]; a = f.atr.to_numpy()
sess = session_mask(df.index); res = nz(X.gd_res12); lead = nz(X.xag_lead12); clv = nz(f.clv); h4 = nz(f.h4_trend); h1 = nz(f.h1_trend)
bL = pd.Series(res <= -2.5).rolling(3, min_periods=1).max().to_numpy() > 0
bS = pd.Series(res >= 2.5).rolling(3, min_periods=1).max().to_numpy() > 0
divL = bL & (c > cp) & (clv > 0.6) & (lead > 0) & (h4 >= 0); divS = bS & (c < cp) & (clv < 0.4) & (lead < 0) & (h4 <= 0)
lonL, lonS = G.fams["London breaks Asian range + h4 trend (buf 0.0)"]
L = (divL | lonL) & sess & (a >= 2.0) & (h1 > 0); S = (divS | lonS) & sess & (a >= 2.0) & (h1 < 0) & ~L
KW = dict(stop_k=1.25, tgt_k=2.5, max_bars=72)
for cost in (0.20, 0.30, 0.50):
    T = run(df, f, L | S, np.where(L, 1.0, -1.0), cost=cost, **KW); out = []
    for per, m in (("2009-19", T.date < "2020"), ("2020-22", (T.date >= "2020") & (T.date < "2023")), ("2023-26", T.date >= "2023"), ("2020-26", T.date >= "2020")):
        out.append(f"{per}: {stats(T[m])}")
    print(f"cost ${cost}:"); print("  " + "\n  ".join(out))
T = run(df, f, L | S, np.where(L, 1.0, -1.0), cost=0.30, **KW); T["yr"] = T.date.dt.year
print(T.groupby("yr").apply(lambda g: pd.Series(stats(g))).drop(columns="label").to_string())
R = T[T.date >= "2020"]; w = R.pnl > 0
print("2020+ avg win $%.2f avg loss $%.2f  target hits %.1f%%  stop hits %.1f%%" % (R.pnl[w].mean(), R.pnl[~w].mean(), 100*(R.rr >= 1.9).mean(), 100*(R.rr <= -0.95).mean()))
mx = cur = 0
for v in w.astype(int): cur = cur + 1 if v == 0 else 0; mx = max(mx, cur)
print("longest losing streak 2020+:", mx); print("by side 2020+:"); print(R.groupby("side").apply(lambda g: pd.Series(stats(g))).drop(columns="label").to_string())
src = {"div": divL | divS, "lon": lonL | lonS}; ent = pd.Series(np.arange(len(c)), index=df.index)
sig_i = ent.reindex(R.date).to_numpy() - 1
for k, v in src.items(): print(k, stats(R[v[sig_i]]))
