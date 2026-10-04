"""Reversal candidates: gross and net results by volatility (ATR % of price) and by exit width (no ML)."""
import numpy as np, pandas as pd, warnings; warnings.filterwarnings("ignore")
import ml
idx = np.r_[np.flatnonzero(ml.candL), np.flatnonzero(ml.candS & ~ml.candL)]
side = np.r_[np.ones(ml.candL.sum()), -np.ones((ml.candS & ~ml.candL).sum())]
F = ml.F; yr = ml.df.index.year.to_numpy()[idx]; atrp = F.atr_pct.to_numpy()[idx]
bdv, sdv = F.bull_div6.to_numpy(bool)[idx], F.bear_div6.to_numpy(bool)[idx]
cross = np.where(side > 0, F.cross_up.to_numpy(bool)[idx], F.cross_dn.to_numpy(bool)[idx])
w2 = F.wt2.to_numpy()[idx] * side
groups = {"all candidates": np.ones(len(idx), bool), "big cross (|wt2|>=53)": cross & (w2 <= -53),
          "big + divergence": cross & (w2 <= -53) & np.where(side > 0, bdv, sdv)}
rows = []
for (slk, tpk, mb) in ((2, 1, 36), (3, 1, 48), (3, 1.5, 72), (4, 2, 96), (6, 2, 144), (6, 3, 288)):
    g = ml.label(ml.o, ml.h, ml.l, ml.c, ml.a, idx, side, float(slk), float(tpk), int(mb))
    for gn, gm in groups.items():
        for lo, hi in ((0, 0.15), (0.15, 0.25), (0.25, 0.4), (0.4, 9)):
            m = gm & (atrp >= lo) & (atrp < hi) & (yr < 2025) & np.isfinite(g)
            r = {"exit": f"SL{slk}/TP{tpk}/{mb}", "group": gn, "ATR%": f"{lo}-{hi}", "n": int(m.sum())}
            for cost in (0.0, 0.04, 0.08):
                p = g[m] - cost; w = p[p > 0].sum(); ls = -p[p < 0].sum()
                r[f"win@{cost}"] = round(100 * (p > 0).mean(), 1); r[f"pf@{cost}"] = round(w / ls, 2) if ls else np.nan
            rows.append(r)
R = pd.DataFrame(rows); R.to_pickle("volx.pkl")
pd.set_option("display.width", 220); pd.set_option("display.max_rows", 300)
print(R.to_string(index=False))
print("\nShare of 5m bars by ATR% bucket, 2024-26:", pd.cut(F.atr_pct[F.index >= "2024"], [0, .15, .25, .4, 9]).value_counts(normalize=True).round(3).to_dict())
