"""Version B details: TP structures (chosen on 2020-24 only), per year, per side."""
import numpy as np, pandas as pd, warnings; warnings.filterwarnings("ignore")
from tp3 import sim3, df, F, o, h, l, c, a, atrp, nz, w1, w2, tu, td
def f(k): return nz(F[k])
g = atrp >= 0.2
L = tu & (w1 < w2) & (w2 <= -60) & g & (f("d_daylo") < 1); S = td & (w1 > w2) & (w2 >= 60) & g & (f("d_dayhi") > -1) & ~L
def show(R, label):
    d = df.index[R[:, 0].astype(int)]; p = R[:, 2]
    out = {"structure": label}
    for nm, m in (("dev 20-24", d < "2025"), ("hold 25-26", d >= "2025")):
        pp = p[m]; w = pp[pp > 0].sum(); ls = -pp[pp < 0].sum()
        out[f"{nm} win%"] = round(100 * (pp > 0).mean(), 1); out[f"{nm} PF"] = round(w / ls, 2)
    return out
rows = []
for lab, x in (("single TP1 1.5 ATR", (1.5, 1.5, 1.5, 1.0, 0.0, False)),
               ("TP1 1.5 (60%) / TP2 2.5 (20%) / TP3 3.5 (20%), SL fixed", (1.5, 2.5, 3.5, 0.6, 0.2, False)),
               ("TP1 1.5 (50%) / TP2 2.5 (25%) / TP3 3.5 (25%), SL fixed", (1.5, 2.5, 3.5, 0.5, 0.25, False)),
               ("TP1 1.0 (50%) / TP2 1.5 (25%) / TP3 2.5 (25%), SL fixed", (1.0, 1.5, 2.5, 0.5, 0.25, False)),
               ("TP1 1.5 (thirds) / 2.5 / 3.5, SL fixed", (1.5, 2.5, 3.5, 1/3, 1/3, False))):
    R = sim3(o, h, l, c, a, L, S, 4.0, *x[:5], x[5], 72, 0.04); rows.append(show(R, lab))
pd.set_option("display.width", 220); pd.set_option("display.max_colwidth", 70)
print("Cost 0.04%:"); print(pd.DataFrame(rows).to_string(index=False))
# chosen: single 1.5 ATR. Per year and per side at 0.04 and 0.06
for cost in (0.04, 0.06):
    R = sim3(o, h, l, c, a, L, S, 4.0, 1.5, 1.5, 1.5, 1.0, 0.0, False, 72, cost)
    T = pd.DataFrame({"date": df.index[R[:, 0].astype(int)], "side": np.where(R[:, 1] > 0, "long", "short"), "p": R[:, 2]})
    T["yr"] = T.date.dt.year
    def st(x):
        w = x.p[x.p > 0].sum(); ls = -x.p[x.p < 0].sum()
        return pd.Series({"trades": len(x), "win%": round(100 * (x.p > 0).mean(), 1), "PF": round(w / ls, 2) if ls else np.inf, "total%": round(x.p.sum(), 1)})
    print(f"\ncost {cost}% by year:"); print(T.groupby("yr").apply(st).T.to_string())
    print(f"cost {cost}% by side:"); print(T.groupby("side").apply(st).to_string())
    # streaks and drawdown in % of price per trade (1 unit each)
    eq = T.p.cumsum(); dd = (eq - eq.cummax()).min(); ls = (T.p <= 0).astype(int).to_numpy(); mx = cur = 0
    for v in ls: cur = cur + 1 if v else 0; mx = max(mx, cur)
    print(f"max drawdown {dd:.1f}% (sum of trade %), longest losing streak {mx}, avg win {T.p[T.p>0].mean():.3f}%, avg loss {T.p[T.p<=0].mean():.3f}%")
