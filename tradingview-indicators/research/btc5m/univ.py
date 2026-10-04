"""Which features predict the next 1 / 3 hours of BTC 5m? Spearman IC by period, and top-vs-bottom decile spread."""
import numpy as np, pandas as pd, warnings; warnings.filterwarnings("ignore")
df = pd.read_pickle("btc5m_raw.pkl"); F = pd.read_pickle("btc5m_feat.pkl")
c = df.c.to_numpy(); o = df.o.to_numpy(); a = F.atr.to_numpy(); ent = np.r_[o[1:], np.nan]
yr = df.index.year
rows = []
for H in (12, 36):
    fwd = (np.r_[c[H:], np.full(H, np.nan)] - ent) / a
    for col in F.columns:
        if col in ("atr",): continue
        x = F[col].to_numpy(dtype=float); r = {"feat": col, "H": H}
        for nm, m in (("20-21", yr <= 2021), ("22-23", (yr >= 2022) & (yr <= 2023)), ("24-26", yr >= 2024)):
            mm = m & np.isfinite(x) & np.isfinite(fwd)
            r[nm] = round(pd.Series(x[mm]).corr(pd.Series(fwd[mm]), method="spearman"), 4)
        rows.append(r)
R = pd.DataFrame(rows)
R["same_sign"] = (np.sign(R["20-21"]) == np.sign(R["22-23"])) & (np.sign(R["22-23"]) == np.sign(R["24-26"]))
R["min_abs"] = R[["20-21", "22-23", "24-26"]].abs().min(axis=1)
pd.set_option("display.width", 200); pd.set_option("display.max_rows", 200)
print(R[R.same_sign].sort_values("min_abs", ascending=False).head(30).to_string(index=False))
# time of day: mean fwd12 return by UTC hour, per period
fwd = (np.r_[c[12:], np.full(12, np.nan)] - ent) / a
T = pd.DataFrame({"h": df.index.hour, "r": fwd, "p": np.where(yr <= 2021, "20-21", np.where(yr <= 2023, "22-23", "24-26"))}).dropna()
print((T.groupby(["h", "p"]).r.mean().unstack() * 100).round(1).T.to_string())
