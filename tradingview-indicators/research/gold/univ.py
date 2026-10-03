import numpy as np, pandas as pd, warnings; warnings.filterwarnings("ignore")
from glab import session_mask
df = pd.read_pickle("bars/XAUUSD_5m.pkl"); f = pd.read_pickle("bars/XAUUSD_feat.pkl")
c = df.c.to_numpy(); a = f.atr.to_numpy()
o_next = np.r_[df.o.to_numpy()[1:], np.nan]
for H in (6, 12):
    f[f"fwd{H}"] = (np.r_[c[H:], np.full(H, np.nan)] - o_next) / a     # entry next open, exit close H bars later, in ATR
sess = session_mask(df.index) & (df.n.to_numpy() >= 4)
IS = (df.index < "2020-01-01"); OOS = (df.index >= "2023-01-01")
cols = [k for k in f.columns if k not in ("tday", "fwd6", "fwd12", "atr", "wt_up", "wt_dn")]
rows = []
for col in cols:
    for per, m in (("IS", IS), ("OOS", OOS)):
        x = f.loc[sess & m, col]; y = f.loc[sess & m, "fwd12"]
        ok = x.notna() & y.notna() & np.isfinite(x)
        x, y = x[ok], y[ok]
        if x.nunique() < 5: 
            q = x
        else:
            q = pd.qcut(x.rank(method="first"), 10, labels=False)
        g = y.groupby(q).mean()
        rows.append({"feature": col, "period": per, "spread_top_minus_bottom": round(g.iloc[-1] - g.iloc[0], 3),
                     "bottom": round(g.iloc[0], 3), "top": round(g.iloc[-1], 3), "spearman": round(x.corr(y, method="spearman"), 4)})
R = pd.DataFrame(rows).pivot(index="feature", columns="period", values=["spearman", "spread_top_minus_bottom"])
R["abs"] = R[("spearman", "IS")].abs()
pd.set_option("display.width", 200); pd.set_option("display.max_rows", 100)
print(R.sort_values("abs", ascending=False).round(4).to_string())
print("baseline mean fwd12 (ATR) IS/OOS:", round(f.loc[sess & IS, "fwd12"].mean(), 4), round(f.loc[sess & OOS, "fwd12"].mean(), 4))
