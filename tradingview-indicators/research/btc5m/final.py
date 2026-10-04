"""Exact defaults of btc-5m-reversal-dots.pine: per year, per side, by cost."""
import numpy as np, pandas as pd, warnings; warnings.filterwarnings("ignore")
from tp3 import sim3, df, F, o, h, l, c, a, atrp, nz, w1, w2, tu, td
def f(k): return nz(F[k])
g = atrp >= 0.2
L = tu & (w1 < w2) & (w2 <= -60) & g & (f("d_daylo") < 1); S = td & (w1 > w2) & (w2 >= 60) & g & (f("d_dayhi") > -1) & ~L
def st(p):
    w = p[p > 0].sum(); ls = -p[p < 0].sum(); return len(p), round(100 * (p > 0).mean(), 1), round(w / ls, 2) if ls else np.inf, round(p.sum(), 1)
rows = []
for cost in (0.0, 0.02, 0.04, 0.06, 0.08, 0.10):
    R = sim3(o, h, l, c, a, L, S, 4.0, 1.0, 1.5, 2.5, 0.5, 0.25, False, 72, cost)
    d = df.index[R[:, 0].astype(int)]; p = R[:, 2]; s = R[:, 1]; tp = R[:, 3]
    for nm, m in (("2020-24 dev", d < "2025"), ("2025-26 hold-out", d >= "2025"), ("all", d > "2000")):
        n, win, pf, tot = st(p[m]); rows.append({"cost%": cost, "period": nm, "trades": n, "win%": win, "PF": pf, "net % (sum)": tot,
                                                 "TP1 hit%": round(100 * (tp[m] >= 1).mean(), 1), "TP3 hit%": round(100 * (tp[m] >= 3).mean(), 1)})
    if cost == 0.04:
        T = pd.DataFrame({"yr": d.year, "side": np.where(s > 0, "long", "short"), "p": p})
        yrs = T.groupby("yr").p.apply(lambda x: pd.Series(dict(zip(["trades", "win%", "PF", "net%"], st(x.to_numpy()))))).unstack()
        sides = T.groupby("side").p.apply(lambda x: pd.Series(dict(zip(["trades", "win%", "PF", "net%"], st(x.to_numpy()))))).unstack()
        pw = p[p > 0].mean(); pl = p[p <= 0].mean(); mx = cur = 0
        for v in (p <= 0): cur = cur + 1 if v else 0; mx = max(mx, cur)
        weeks = (d.max() - d.min()).days / 7
pd.set_option("display.width", 200)
print(pd.DataFrame(rows).to_string(index=False))
print("\n0.04% cost by year:"); print(yrs.to_string())
print("\n0.04% by side:"); print(sides.to_string())
print(f"\navg win {pw:.3f}%  avg loss {pl:.3f}%  longest losing streak {mx}  trades/week {len(p)/weeks:.2f}")
