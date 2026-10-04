"""Candidate rules with an ATR-%% volatility gate and TP1/TP2/TP3 exits, year by year (2020-2024; 2025-26 still held out)."""
import numpy as np, pandas as pd, itertools, warnings; warnings.filterwarnings("ignore")
from numba import njit
df = pd.read_pickle("btc5m_raw.pkl"); F = pd.read_pickle("btc5m_feat.pkl")
o, h, l, c = (df[k].to_numpy() for k in "ohlc"); a = F.atr.to_numpy(); atrp = F.atr_pct.to_numpy()
def nz(x): return np.nan_to_num(np.asarray(x, dtype=float))
w1, w2 = nz(F.wt1), nz(F.wt2)
cu, cd, tu, td = (F[k].to_numpy(bool) for k in ("cross_up", "cross_dn", "turn_up", "turn_dn"))
bdv, sdv = F.bull_div6.to_numpy(bool), F.bear_div6.to_numpy(bool)

@njit(cache=True)
def sim3(o, h, l, c, a, L, S, slk, t1, t2, t3, f1, f2, be, mb, cost):
    """SL slk*ATR; take f1 at t1*ATR, f2 at t2*ATR, rest at t3*ATR; optional SL to entry after TP1; max bars; one trade at a time."""
    n = len(c); out = np.zeros((n, 4)); k = 0; i = 0
    while i < n - 1:
        s = 1.0 if L[i] else (-1.0 if S[i] else 0.0)
        if s == 0.0: i += 1; continue
        e = i + 1; ep = o[e]; st = ep - s * slk * a[i]
        tps = (ep + s * t1 * a[i], ep + s * t2 * a[i], ep + s * t3 * a[i]); fr = (f1, f2, 1.0 - f1 - f2)
        got = 0; pnl = 0.0; left = 1.0; j = e
        while j < n:
            if (l[j] <= st) if s > 0 else (h[j] >= st):
                xp = min(o[j], st) if s > 0 else max(o[j], st); pnl += left * s * (xp - ep); left = 0.0; break
            while got < 3 and ((h[j] >= tps[got]) if s > 0 else (l[j] <= tps[got])):
                pnl += fr[got] * s * (tps[got] - ep); left -= fr[got]; got += 1
                if be and got == 1: st = ep
            if got == 3 or left <= 1e-9: break
            if j - e + 1 >= mb or j == n - 1: pnl += left * s * (c[j] - ep); left = 0.0; break
            j += 1
        out[k, 0] = e; out[k, 1] = s; out[k, 2] = pnl / ep * 100 - cost; out[k, 3] = got
        k += 1; i = j + 1
    return out[:k]

if __name__ == "__main__":
    E = {"big+div": (cu & (w2 <= -53) & bdv, cd & (w2 >= 53) & sdv),
         "big cross": (cu & (w2 <= -53), cd & (w2 >= 53)),
         "early turn": (tu & (w1 < w2) & (w2 <= -60), td & (w1 > w2) & (w2 >= 60))}
    X = {"SL3/TP1 (single)": (3, 1, 1, 1, 1.0, 0.0, False, 48), "SL2/TP1 (single)": (2, 1, 1, 1, 1.0, 0.0, False, 36),
         "SL6/TP2 (single)": (6, 2, 2, 2, 1.0, 0.0, False, 144),
         "SL3 TP1/2/3 thirds +BE": (3, 1, 2, 3, 1/3, 1/3, True, 96), "SL2 TP1/2/3 thirds +BE": (2, 1, 2, 3, 1/3, 1/3, True, 72),
         "SL3 TP1(50%)/2/3 +BE": (3, 1, 2, 3, 0.5, 0.25, True, 96)}
    rows = []
    for (en, (L0, S0)), (xn, x), gate, cost in itertools.product(E.items(), X.items(), (0.0, 0.2, 0.3), (0.0, 0.04, 0.08)):
        g = atrp >= gate
        R = sim3(o, h, l, c, a, L0 & g, S0 & g & ~(L0 & g), *x[:6], x[6], x[7], cost)
        d = df.index[R[:, 0].astype(int)]; yr = d.year; p = R[:, 2]
        r = {"entry": en, "exit": xn, "minATR%": gate, "cost": cost}
        for Y in range(2020, 2025):
            m = yr == Y; w = p[m][p[m] > 0].sum(); ls = -p[m][p[m] < 0].sum()
            r[f"{Y} pf"] = round(w / ls, 2) if ls else np.nan
        m = yr < 2025; w = p[m][p[m] > 0].sum(); ls = -p[m][p[m] < 0].sum()
        r.update({"n 20-24": int(m.sum()), "per_day": round(m.sum() / 1827, 2), "win% 20-24": round(100 * (p[m] > 0).mean(), 1), "PF 20-24": round(w / ls, 2) if ls else np.nan,
                  "yrs PF>1": int(sum(r[f"{Y} pf"] > 1 for Y in range(2020, 2025)))})
        rows.append(r)
    R = pd.DataFrame(rows); R.to_pickle("tp3.pkl")
    pd.set_option("display.width", 260); pd.set_option("display.max_rows", 300)
    cols = ["entry", "exit", "minATR%", "cost", "n 20-24", "per_day", "win% 20-24", "PF 20-24", "yrs PF>1"] + [f"{Y} pf" for Y in range(2020, 2025)]
    for cost in (0.04, 0.08):
        print(f"\n=== cost {cost}%: win >= 60%, sorted by years with PF>1 then PF ===")
        q = R[(R.cost == cost) & (R["win% 20-24"] >= 60)].sort_values(["yrs PF>1", "PF 20-24"], ascending=False)
        print(q[cols].head(15).to_string(index=False))
    print("\n=== gross (cost 0) top ===")
    print(R[R.cost == 0].sort_values(["yrs PF>1", "PF 20-24"], ascending=False)[cols].head(12).to_string(index=False))
