"""Part C: robustness of the best high-win-rate candidates (per year, costs, and without the ATR gate before 2020)."""
import numpy as np, pandas as pd, warnings; warnings.filterwarnings("ignore")
from glab import run, stats, session_mask
import grid2_fams as G
df, f = G.df, G.f; X = pd.read_pickle("bars/XAUUSD_xfeat.pkl")
def nz(x): return np.nan_to_num(np.asarray(x, dtype=float), nan=0.0)
c = df.c.to_numpy(); cp = np.r_[c[0], c[:-1]]; a = f.atr.to_numpy()
sess = session_mask(df.index); res = nz(X.gd_res12); lead = nz(X.xag_lead12); clv = nz(f.clv)
h4 = nz(f.h4_trend); h1 = nz(f.h1_trend); m15 = nz(f.m15_trend); d50 = nz(f.d_ema50)
bL = pd.Series(res <= -2.5).rolling(3, min_periods=1).max().to_numpy() > 0
bS = pd.Series(res >= 2.5).rolling(3, min_periods=1).max().to_numpy() > 0
divL = bL & (c > cp) & (clv > 0.6) & (lead > 0) & (h4 >= 0); divS = bS & (c < cp) & (clv < 0.4) & (lead < 0) & (h4 <= 0)
lonL, lonS = G.fams["London breaks Asian range + h4 trend (buf 0.0)"]
def sig(gate, filt):
    L = (divL | lonL) & sess & (a >= gate); S = (divS | lonS) & sess & (a >= gate) & ~L
    if filt == "h1+m15": L &= (h1 > 0) & (m15 >= 0); S &= (h1 < 0) & (m15 <= 0)
    if filt == "ema50": L &= d50 > 0; S &= d50 < 0
    return L, S
C = [("A h1+m15, s2.5/t1.25", "h1+m15", dict(stop_k=2.5, tgt_k=1.25, max_bars=36)),
     ("B h1+m15, s2/t2", "h1+m15", dict(stop_k=2.0, tgt_k=2.0, max_bars=36)),
     ("C ema50, s2.5/t1.25", "ema50", dict(stop_k=2.5, tgt_k=1.25, max_bars=36)),
     ("D h1+m15, s2/t1.5", "h1+m15", dict(stop_k=2.0, tgt_k=1.5, max_bars=36))]
rows = []; yrs = {}
for name, filt, kw in C:
    for gate in (2.0, 0.0):
        L, S = sig(gate, filt)
        for cost in (0.20, 0.30, 0.50):
            T = run(df, f, L | S, np.where(L, 1.0, -1.0), cost=cost, **kw)
            r = {"cand": name, "minATR": gate, "cost": cost}
            for per, m in (("09-19", T.date < "2020"), ("20-22", (T.date >= "2020") & (T.date < "2023")), ("23-26", T.date >= "2023")):
                s_ = stats(T[m]); r[f"{per}_n"] = s_["n"]; r[f"{per}_win"] = s_.get("win"); r[f"{per}_pf"] = s_.get("pf")
            rows.append(r)
            if gate == 2.0 and cost == 0.30:
                T["yr"] = T.date.dt.year; g = T[T.yr >= 2020].groupby("yr")
                yrs[name] = g.apply(lambda x: f"{100*(x.pnl>0).mean():.0f}% / {x.pnl[x.pnl>0].sum()/-x.pnl[x.pnl<0].sum():.2f} ({len(x)})")
                w = (T[T.date >= "2020"].pnl > 0).astype(int).to_numpy(); mx = cur = 0
                for v in w: cur = cur + 1 if v == 0 else 0; mx = max(mx, cur)
                p = T[T.date >= "2020"].pnl; print(name, "2020+: avg win $%.2f avg loss $%.2f, longest losing streak %d" % (p[p > 0].mean(), p[p < 0].mean(), mx))
pd.set_option("display.width", 250); pd.set_option("display.max_rows", 200)
print(pd.DataFrame(rows).to_string(index=False))
print("\nWin % / PF (trades) by year, ATR gate $2, cost $0.30:"); print(pd.DataFrame(yrs).to_string())
