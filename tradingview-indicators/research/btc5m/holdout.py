"""ONE-TIME hold-out test, Jan 2025 - Aug 2026, of the two pre-registered candidates (and TP1/TP2/TP3 variants)."""
import numpy as np, pandas as pd, itertools, warnings; warnings.filterwarnings("ignore")
from tp3 import sim3, df, F, o, h, l, c, a, atrp, nz, w1, w2, tu, td
def f(k): return nz(F[k])
g = atrp >= 0.2
baseL = tu & (w1 < w2) & (w2 <= -60) & g; baseS = td & (w1 > w2) & (w2 >= 60) & g
C = {"A strict (cvd+h4+prem)": (baseL & (f("cvd12") < -0.1) & (f("h4_trend") >= 0) & (f("prem_z") < -1),
                                baseS & (f("cvd12") > 0.1) & (f("h4_trend") <= 0) & (f("prem_z") > 1)),
     "B standard (near day low/high)": (baseL & (f("d_daylo") < 1), baseS & (f("d_dayhi") > -1))}
X = {"single TP 1.5 ATR": (4, 1.5, 1.5, 1.5, 1.0, 0.0, False),
     "TP1 1.5 / TP2 2.5 / TP3 3.5, thirds, SL to entry after TP1": (4, 1.5, 2.5, 3.5, 1/3, 1/3, True),
     "TP1 1.5 (50%) / TP2 2.5 (25%) / TP3 3.5 (25%), SL to entry": (4, 1.5, 2.5, 3.5, 0.5, 0.25, True)}
rows = []
for (cn, (L, S)), (xn, x), cost in itertools.product(C.items(), X.items(), (0.0, 0.04, 0.06, 0.1)):
    R = sim3(o, h, l, c, a, L, S & ~L, *x[:6], x[6], 72 if x[4] == 1.0 else 144, cost)
    d = df.index[R[:, 0].astype(int)]; p = R[:, 2]
    for per, m in (("2020-24 (dev)", d < "2025"), ("2025-26 HOLD-OUT", d >= "2025")):
        pp = p[m]; w = pp[pp > 0].sum(); ls = -pp[pp < 0].sum()
        rows.append({"candidate": cn, "exit": xn, "cost": cost, "period": per, "trades": len(pp),
                     "per_week": round(len(pp) / (87 if per.startswith("2025") else 261), 2),
                     "win%": round(100 * (pp > 0).mean(), 1), "PF": round(w / ls, 2) if ls else np.inf, "avg%": round(pp.mean(), 3), "total%": round(pp.sum(), 1)})
R = pd.DataFrame(rows); R.to_pickle("holdout.pkl")
pd.set_option("display.width", 250); pd.set_option("display.max_rows", 100); pd.set_option("display.max_colwidth", 60)
print(R.to_string(index=False))
