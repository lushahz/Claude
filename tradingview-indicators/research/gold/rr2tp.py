"""1:2 minimum reward:risk with TP1/TP2: SL s, TP2 = 2s (or 2.5s), TP1 options, breakeven, 1h filter, hold time."""
import numpy as np, pandas as pd, itertools, warnings; warnings.filterwarnings("ignore")
from tp12lib import sim2, df, f, L, S
from glab import session_end_flags
o, h, l, c = (df[k].to_numpy() for k in "ohlc"); a = f.atr.to_numpy(); se = session_end_flags(df.index)
h1 = np.nan_to_num(f.h1_trend.to_numpy())
dates = df.index.to_numpy()
FL = {"none": (L, S), "h1": (L & (h1 > 0), S & (h1 < 0))}
rows = []
for fn, (LL, SS) in FL.items():
    sig = LL | SS; side = np.where(LL, 1.0, -1.0)
    for sk, rr, t1m, be, mb in itertools.product((1.0, 1.25, 1.5), (2.0, 2.5), (None, 1.0, 1.5), (False, True), (36, 72)):
        if t1m is None and be: continue
        t2 = sk * rr; t1 = t2 if t1m is None else sk * t1m
        R = sim2(o, h, l, c, a, sig, side, sk, t1, t2, mb, se, 0.30, be)
        d = pd.to_datetime(dates[R[:, 0].astype(int)])
        r = {"filter": fn, "SL": sk, "RR": rr, "TP1": "-" if t1m is None else f"{t1m:g}R", "BE": be, "bars": mb}
        for per, m in (("09-19", d < "2020"), ("20-22", (d >= "2020") & (d < "2023")), ("23-26", d >= "2023"), ("20-26", d >= "2020")):
            m = np.asarray(m); p = R[m, 1]; w = p[p > 0].sum(); ls = -p[p < 0].sum()
            r[f"{per}_pf"] = round(w / ls, 2) if ls else np.inf
            if per == "20-26": r["n"] = len(p); r["win"] = round((p > 0).mean(), 3); r["tot$"] = round(p.sum(), 0)
        r["minRecent"] = min(r["20-22_pf"], r["23-26_pf"])
        rows.append(r)
R = pd.DataFrame(rows); R.to_pickle("rr2tp.pkl")
pd.set_option("display.width", 250); pd.set_option("display.max_rows", 300)
print(R.sort_values(["minRecent", "09-19_pf"], ascending=False).head(20).to_string(index=False))
print("\nNo filter, best by minRecent:"); print(R[R["filter"] == "none"].sort_values("minRecent", ascending=False).head(8).to_string(index=False))
