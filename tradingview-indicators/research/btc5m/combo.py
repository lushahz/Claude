"""Combinations of the robust filters on the early-turn reversal, with a few exit / gate variants. Years 2020-2024 only."""
import numpy as np, pandas as pd, itertools, warnings; warnings.filterwarnings("ignore")
from tp3 import sim3, df, F, o, h, l, c, a, atrp, nz, w1, w2, tu, td
def f(k): return nz(F[k])
FL = {"dayX": (f("d_daylo") < 1, f("d_dayhi") > -1), "cvd": (f("cvd12") < -0.1, f("cvd12") > 0.1),
      "h4": (f("h4_trend") >= 0, f("h4_trend") <= 0), "prem": (f("prem_z") < -1, f("prem_z") > 1)}
rows = []
for k in range(0, 4):
    for combo in itertools.combinations(FL, k):
        for gate, (slk, tpk, mb), wl in itertools.product((0.15, 0.2, 0.25), ((3, 1, 48), (2, 1, 36), (4, 1.5, 72)), (60,)):
            L = tu & (w1 < w2) & (w2 <= -wl) & (atrp >= gate); S = td & (w1 > w2) & (w2 >= wl) & (atrp >= gate)
            for nm in combo: L = L & FL[nm][0]; S = S & FL[nm][1]
            S = S & ~L
            for cost in (0.0, 0.04, 0.06):
                R = sim3(o, h, l, c, a, L, S, float(slk), float(tpk), float(tpk), float(tpk), 1.0, 0.0, False, mb, cost)
                yr = df.index[R[:, 0].astype(int)].year; p = R[:, 2]
                r = {"filters": "+".join(combo) or "none", "gate": gate, "exit": f"SL{slk}/TP{tpk}", "cost": cost}
                pfs = []
                for Y in range(2020, 2025):
                    m = yr == Y; w = p[m][p[m] > 0].sum(); ls = -p[m][p[m] < 0].sum(); pfs.append(w / ls if ls else np.nan); r[str(Y)] = round(pfs[-1], 2)
                m = yr < 2025; w = p[m][p[m] > 0].sum(); ls = -p[m][p[m] < 0].sum()
                r.update({"n": int(m.sum()), "per_wk": round(m.sum() / 261, 1), "win%": round(100 * (p[m] > 0).mean(), 1), "PF": round(w / ls, 2), "minPF": round(np.nanmin(pfs), 2)})
                rows.append(r)
R = pd.DataFrame(rows); R.to_pickle("combo.pkl")
pd.set_option("display.width", 240); pd.set_option("display.max_rows", 200)
for cost in (0.0, 0.04, 0.06):
    print(f"\n=== cost {cost}%: n >= 150, win >= 60, sorted by worst-year PF ===")
    q = R[(R.cost == cost) & (R.n >= 150) & (R["win%"] >= 60)].sort_values(["minPF", "PF"], ascending=False)
    print(q.head(12).to_string(index=False))
