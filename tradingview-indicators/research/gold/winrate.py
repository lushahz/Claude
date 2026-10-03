"""Can the win rate go above 60% without destroying profitability? Part A: exit geometry on the same signals."""
import numpy as np, pandas as pd, itertools, warnings; warnings.filterwarnings("ignore")
from glab import run, stats, session_mask
import grid2_fams as G
df, f = G.df, G.f; X = pd.read_pickle("bars/XAUUSD_xfeat.pkl")
def nz(x): return np.nan_to_num(np.asarray(x, dtype=float), nan=0.0)
c = df.c.to_numpy(); cp = np.r_[c[0], c[:-1]]; a = f.atr.to_numpy()
sess = session_mask(df.index); res = nz(X.gd_res12); lead = nz(X.xag_lead12); clv = nz(f.clv); h4 = nz(f.h4_trend)
bL = pd.Series(res <= -2.5).rolling(3, min_periods=1).max().to_numpy() > 0
bS = pd.Series(res >= 2.5).rolling(3, min_periods=1).max().to_numpy() > 0
divL = bL & (c > cp) & (clv > 0.6) & (lead > 0) & (h4 >= 0); divS = bS & (c < cp) & (clv < 0.4) & (lead < 0) & (h4 <= 0)
lonL, lonS = G.fams["London breaks Asian range + h4 trend (buf 0.0)"]
gate = a >= 2.0
L = (divL | lonL) & sess & gate; S = (divS | lonS) & sess & gate & ~L
np.save("sigL.npy", L); np.save("sigS.npy", S)
rows = []
for sk, tk, mb, be in itertools.product((1.0, 1.5, 2.0, 2.5, 3.0), (0.5, 0.75, 1.0, 1.25, 1.5, 2.0), (12, 36, 72), (0.0, 0.5, 1.0)):
    if be and be >= tk: continue
    T = run(df, f, L | S, np.where(L, 1.0, -1.0), stop_k=sk, tgt_k=tk, max_bars=mb, be_k=be, cost=0.30)
    r = {"stop": sk, "tgt": tk, "bars": mb, "be": be}
    for per, m in (("09-19", T.date < "2020"), ("20-22", (T.date >= "2020") & (T.date < "2023")), ("23-26", T.date >= "2023")):
        s_ = stats(T[m]); r[f"{per}_n"] = s_["n"]; r[f"{per}_win"] = s_["win"]; r[f"{per}_pf"] = s_["pf"]
    rows.append(r)
R = pd.DataFrame(rows); R.to_pickle("winrate_exits.pkl")
pd.set_option("display.width", 250); pd.set_option("display.max_rows", 400)
print("All configs with win >= 60% in 2020-22 AND 2023-26, sorted by 2020-22 PF:")
q = R[(R["20-22_win"] >= 0.60) & (R["23-26_win"] >= 0.60)].sort_values("20-22_pf", ascending=False)
print(q.head(25).to_string(index=False))
print("\nBest 2020-22 PF overall (for reference):"); print(R.sort_values("20-22_pf", ascending=False).head(10).to_string(index=False))
