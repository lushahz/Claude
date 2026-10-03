"""User trades 1:2 (stop : target). Find the most robust stop size, hold time and filter for that geometry."""
import numpy as np, pandas as pd, itertools, warnings; warnings.filterwarnings("ignore")
from glab import run, stats, session_mask
import grid2_fams as G
df, f = G.df, G.f; X = pd.read_pickle("bars/XAUUSD_xfeat.pkl")
def nz(x): return np.nan_to_num(np.asarray(x, dtype=float), nan=0.0)
c = df.c.to_numpy(); cp = np.r_[c[0], c[:-1]]; a = f.atr.to_numpy(); ny = f.ny_min.to_numpy(); dow = f.dow.to_numpy()
sess = session_mask(df.index); res = nz(X.gd_res12); lead = nz(X.xag_lead12); clv = nz(f.clv)
h4 = nz(f.h4_trend); h1 = nz(f.h1_trend); m15 = nz(f.m15_trend); d50 = nz(f.d_ema50)
bL = pd.Series(res <= -2.5).rolling(3, min_periods=1).max().to_numpy() > 0
bS = pd.Series(res >= 2.5).rolling(3, min_periods=1).max().to_numpy() > 0
divL = bL & (c > cp) & (clv > 0.6) & (lead > 0) & (h4 >= 0); divS = bS & (c < cp) & (clv < 0.4) & (lead < 0) & (h4 <= 0)
lonL, lonS = G.fams["London breaks Asian range + h4 trend (buf 0.0)"]
FL = {"none": (True, True), "h1 agrees": (h1 > 0, h1 < 0), "h1+m15 agree": ((h1 > 0) & (m15 >= 0), (h1 < 0) & (m15 <= 0)),
      "h4 strong": (h4 == 2, h4 == -2), "not 05-07 NY": (~((ny >= 300) & (ny < 420)),) * 2, "Mon-Thu": (dow < 4,) * 2,
      "EMA50 side": (d50 > 0, d50 < 0)}
rows = []
for gate in (2.0, 0.0):
    for fn, (fl, fs) in FL.items():
        L = (divL | lonL) & sess & (a >= gate) & fl; S = (divS | lonS) & sess & (a >= gate) & fs & ~L
        for sk, mb in itertools.product((0.75, 1.0, 1.25, 1.5, 2.0), (36, 72)):
            T = run(df, f, L | S, np.where(L, 1.0, -1.0), stop_k=sk, tgt_k=2 * sk, max_bars=mb, cost=0.30)
            r = {"gate": gate, "filter": fn, "stop": sk, "tgt": 2 * sk, "bars": mb}
            for per, m in (("09-19", T.date < "2020"), ("20-22", (T.date >= "2020") & (T.date < "2023")), ("23-26", T.date >= "2023")):
                s_ = stats(T[m]); r[f"{per}_n"] = s_["n"]; r[f"{per}_win"] = s_.get("win"); r[f"{per}_pf"] = s_.get("pf")
            r["min_pf"] = min(r["09-19_pf"], r["20-22_pf"], r["23-26_pf"]); r["min_recent"] = min(r["20-22_pf"], r["23-26_pf"])
            rows.append(r)
R = pd.DataFrame(rows); R.to_pickle("rr2.pkl")
pd.set_option("display.width", 250); pd.set_option("display.max_rows", 400)
print("Top 25 by weakest recent period (2020-22 vs 2023-26), 1:2 only:")
print(R.sort_values(["min_recent", "min_pf"], ascending=False).head(25).to_string(index=False))
print("\nNo extra filter, gate $2:"); print(R[(R.gate == 2.0) & (R["filter"] == "none")].to_string(index=False))
