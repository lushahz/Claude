"""Gold-vs-dollar divergence reversion (+ silver confirmation), session only, with candle trigger."""
import numpy as np, pandas as pd, warnings; warnings.filterwarnings("ignore")
from glab import run, stats, session_mask
df = pd.read_pickle("bars/XAUUSD_5m.pkl"); f = pd.read_pickle("bars/XAUUSD_feat.pkl"); X = pd.read_pickle("bars/XAUUSD_xfeat.pkl")
def nz(x): return np.nan_to_num(np.asarray(x, dtype=float), nan=0.0)
c = df.c.to_numpy(); o = df.o.to_numpy(); cp = np.r_[c[0], c[:-1]]
sess = session_mask(df.index); res = nz(X.gd_res12); lead = nz(X.xag_lead12); clv = nz(f.clv); h4 = nz(f.h4_trend)
ny = f.ny_min.to_numpy(); notEarly = ~((ny >= 300) & (ny < 420))   # skip 05:00-06:59 NY drift slots
rows = []
for thr in (1.5, 2.0, 2.5, 3.0):
    base_L = pd.Series(res <= -thr).rolling(3, min_periods=1).max().to_numpy() > 0
    base_S = pd.Series(res >= thr).rolling(3, min_periods=1).max().to_numpy() > 0
    trigL = (c > cp) & (clv > 0.6); trigS = (c < cp) & (clv < 0.4)
    for var in ("plain", "+silver", "+h4", "+silver+h4", "+silver-early"):
        L = sess & base_L & trigL; S = sess & base_S & trigS
        if "silver" in var: L &= lead > 0; S &= lead < 0
        if "h4" in var: L &= h4 >= 0; S &= h4 <= 0
        if "early" in var: L &= notEarly; S &= notEarly
        for en, kw in (("s1/t1.5/24", dict(stop_k=1.0, tgt_k=1.5, max_bars=24)), ("s1.5/t2/36", dict(stop_k=1.5, tgt_k=2.0, max_bars=36))):
            for cost in (0.0, 0.30):
                T = run(df, f, L | S, np.where(L, 1.0, -1.0), cost=cost, **kw)
                r = {"thr": thr, "var": var, "exit": en, "cost": cost}
                for per, m in (("IS", T.date < "2020"), ("VAL", (T.date >= "2020") & (T.date < "2023")), ("OOS", T.date >= "2023"), ("25-26", T.date >= "2025")):
                    s_ = stats(T[m]); r.update({f"{per}_{k}": v for k, v in s_.items() if k in ("n", "win", "pf")})
                rows.append(r)
pd.set_option("display.width", 260); pd.set_option("display.max_rows", 500)
R = pd.DataFrame(rows); print(R.to_string(index=False)); R.to_pickle("grid3.pkl")
