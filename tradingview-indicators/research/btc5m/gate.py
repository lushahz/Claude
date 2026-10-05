"""How much does lowering the volatility gate cost? Exact indicator rules, varying min ATR %."""
import numpy as np, pandas as pd, warnings; warnings.filterwarnings("ignore")
from tp3 import sim3, df, F, o, h, l, c, a, atrp, nz, w1, w2, tu, td
def f(k): return nz(F[k])
rows = []
for gate in (0.2, 0.15, 0.12, 0.10, 0.0):
    g = atrp >= gate
    L = tu & (w1 < w2) & (w2 <= -60) & g & (f("d_daylo") < 1); S = td & (w1 > w2) & (w2 >= 60) & g & (f("d_dayhi") > -1) & ~L
    for cost in (0.0, 0.02, 0.04):
        R = sim3(o, h, l, c, a, L, S, 4.0, 1.0, 1.5, 2.5, 0.5, 0.25, False, 72, cost)
        d = df.index[R[:, 0].astype(int)]; p = R[:, 2]
        r = {"min ATR%": gate, "cost%": cost}
        for nm, m in (("2020-24", d < "2025"), ("2025-26", d >= "2025")):
            pp = p[m]; w = pp[pp > 0].sum(); ls = -pp[pp < 0].sum()
            r[f"{nm} /week"] = round(len(pp) / (261 if nm == "2020-24" else 87), 1); r[f"{nm} win%"] = round(100 * (pp > 0).mean(), 1); r[f"{nm} PF"] = round(w / ls, 2)
        rows.append(r)
pd.set_option("display.width", 200); print(pd.DataFrame(rows).to_string(index=False))
