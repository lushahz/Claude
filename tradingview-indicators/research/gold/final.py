"""Backtest of the exact Pine defaults: divergence snap (2.5 sigma, silver, h4) + London Asian-range break (h4), session 07-16 UTC, min ATR gate."""
import numpy as np, pandas as pd, warnings; warnings.filterwarnings("ignore")
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
KW = dict(stop_k=1.5, tgt_k=2.0, max_bars=36)
rows = []
for gate in (0.0, 2.0):
    for name, (L, S) in (("divergence only", (divL, divS)), ("London only", (lonL, lonS)), ("combined (Pine default)", (divL | lonL, (divS | lonS) & ~(divL | lonL)))):
        L = L & sess & (a >= gate); S = S & sess & (a >= gate)
        for cost in (0.20, 0.30, 0.50):
            T = run(df, f, L | S, np.where(L, 1.0, -1.0), cost=cost, **KW)
            r = {"setup": name, "minATR": gate, "cost": cost}
            for per, m in (("09-19", T.date < "2020"), ("20-22", (T.date >= "2020") & (T.date < "2023")), ("23-26", T.date >= "2023"), ("25-26", T.date >= "2025")):
                s_ = stats(T[m]); r.update({f"{per}_{k}": v for k, v in s_.items() if k in ("n", "win", "pf", "total_$")})
            rows.append(r)
            if gate == 2.0 and cost == 0.30 and name.startswith("combined"): Tc = T
pd.set_option("display.width", 300); pd.set_option("display.max_columns", 40)
print(pd.DataFrame(rows).to_string(index=False))
Tc["yr"] = Tc.date.dt.year
print(Tc.groupby("yr").apply(lambda g: pd.Series(stats(g))).drop(columns="label").to_string())
Tc.to_pickle("final_trades.pkl")
