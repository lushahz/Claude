"""Divergence-snap rule: volatility gate, cost sensitivity, per-year breakdown, London-break add-on."""
import numpy as np, pandas as pd, warnings; warnings.filterwarnings("ignore")
from glab import run, stats, session_mask
df = pd.read_pickle("bars/XAUUSD_5m.pkl"); f = pd.read_pickle("bars/XAUUSD_feat.pkl"); X = pd.read_pickle("bars/XAUUSD_xfeat.pkl")
def nz(x): return np.nan_to_num(np.asarray(x, dtype=float), nan=0.0)
c = df.c.to_numpy(); cp = np.r_[c[0], c[:-1]]; a = f.atr.to_numpy()
sess = session_mask(df.index); res = nz(X.gd_res12); lead = nz(X.xag_lead12); clv = nz(f.clv); h4 = nz(f.h4_trend)
def div_sig(thr):
    bL = pd.Series(res <= -thr).rolling(3, min_periods=1).max().to_numpy() > 0
    bS = pd.Series(res >= thr).rolling(3, min_periods=1).max().to_numpy() > 0
    L = sess & bL & (c > cp) & (clv > 0.6) & (lead > 0) & (h4 >= 0)
    S = sess & bS & (c < cp) & (clv < 0.4) & (lead < 0) & (h4 <= 0)
    return L, S
KW = dict(stop_k=1.5, tgt_k=2.0, max_bars=36)
rows = []
for thr in (2.0, 2.5):
    L0, S0 = div_sig(thr)
    for gate in (0.0, 1.0, 1.5, 2.0, 2.5):
        L = L0 & (a >= gate); S = S0 & (a >= gate)
        for cost in (0.20, 0.30, 0.50):
            T = run(df, f, L | S, np.where(L, 1.0, -1.0), cost=cost, **KW)
            r = {"thr": thr, "minATR$": gate, "cost": cost}
            for per, m in (("all", T.date > "2000"), ("09-19", T.date < "2020"), ("20-22", (T.date >= "2020") & (T.date < "2023")), ("23-26", T.date >= "2023"), ("25-26", T.date >= "2025")):
                s_ = stats(T[m]); r.update({f"{per}_{k}": v for k, v in s_.items() if k in ("n", "win", "pf")})
            rows.append(r)
pd.set_option("display.width", 260); pd.set_option("display.max_rows", 500)
print(pd.DataFrame(rows).to_string(index=False))
L, S = div_sig(2.5); T = run(df, f, L | S, np.where(L, 1.0, -1.0), cost=0.30, **KW)
T["yr"] = T.date.dt.year
print(T.groupby("yr").apply(lambda g: pd.Series(stats(g))).drop(columns="label").to_string())
print("long/short split 2023+:"); T2 = T[T.date >= "2023"]
for s in (1, -1): print(s, stats(T2[T2.side == s]))
