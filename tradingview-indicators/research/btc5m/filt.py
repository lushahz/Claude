"""Filters on top of the early-turn reversal (SL3/TP1/48, ATR >= 0.2%): which ones lift gross PF in EVERY year 2020-2024?"""
import numpy as np, pandas as pd, warnings; warnings.filterwarnings("ignore")
from tp3 import sim3, df, F, o, h, l, c, a, atrp, nz, w1, w2, tu, td, cu, cd
g = atrp >= 0.2
baseL = tu & (w1 < w2) & (w2 <= -60) & g; baseS = td & (w1 > w2) & (w2 >= 60) & g
def f(k): return nz(F[k])
cl = f("clv"); 
FL = {  # (long condition, short condition)
 "none": (True, True),
 "h1 waves in zone (h1 wt2 < 0 / > 0)": (f("h1_wt2") < 0, f("h1_wt2") > 0),
 "h1 waves deep (< -40 / > 40)": (f("h1_wt2") < -40, f("h1_wt2") > 40),
 "h4 waves in zone": (f("h4_wt2") < 0, f("h4_wt2") > 0),
 "h4 trend not against": (f("h4_trend") >= 0, f("h4_trend") <= 0),
 "h4 trend against (fade)": (f("h4_trend") < 0, f("h4_trend") > 0),
 "d1 trend with": (f("d1_trend") > 0, f("d1_trend") < 0),
 "seller/buyer exhaustion cvd12 (<-0.1 / >0.1)": (f("cvd12") < -0.1, f("cvd12") > 0.1),
 "taker flow already flipping (cvd3 > 0 / < 0)": (f("cvd3") > 0, f("cvd3") < 0),
 "volume spike (vz > 1)": (f("vz") > 1, f("vz") > 1),
 "stretched below/above VWAP (> 2 ATR)": (f("d_vwap") < -2, f("d_vwap") > 2),
 "far from EMA50 (> 2 ATR)": (f("d_ema50") < -2, f("d_ema50") > 2),
 "bb outside (< -1 / > 1)": (f("bb") < -1, f("bb") > 1),
 "rsi7 extreme (<25 / >75)": (f("rsi7") < 25, f("rsi7") > 75),
 "stoch K extreme (<10 / >90)": (f("stk") < 10, f("stk") > 90),
 "rejection wick (> 0.3 ATR)": (f("wick_dn") > 0.3, f("wick_up") > 0.3),
 "near day low/high (< 1 ATR)": (f("d_daylo") < 1, f("d_dayhi") > -1),
 "divergence within 6 bars": (F.bull_div6.to_numpy(bool), F.bear_div6.to_numpy(bool)),
 "ETH weaker/stronger (eth_rel12 < 0 / > 0)": (f("eth_rel12") < 0, f("eth_rel12") > 0),
 "funding positive/negative (crowded)": (f("fund") > 1, f("fund") < 0.5),
 "premium z low/high": (f("prem_z") < -1, f("prem_z") > 1),
 "weekday only": (F.dow.to_numpy() < 5, F.dow.to_numpy() < 5),
 "US hours 13-21 UTC": ((F.hour.to_numpy() >= 13) & (F.hour.to_numpy() < 21),) * 2,
 "Asia hours 0-8 UTC": ((F.hour.to_numpy() < 8),) * 2,
}
rows = []
for name, (fl, fs) in FL.items():
    L = baseL & fl; S = baseS & fs & ~L
    for cost in (0.0, 0.04):
        R = sim3(o, h, l, c, a, L, S, 3.0, 1.0, 1.0, 1.0, 1.0, 0.0, False, 48, cost)
        yr = df.index[R[:, 0].astype(int)].year; p = R[:, 2]
        r = {"filter": name, "cost": cost}
        for Y in range(2020, 2025):
            m = yr == Y; w = p[m][p[m] > 0].sum(); ls = -p[m][p[m] < 0].sum(); r[str(Y)] = round(w / ls, 2) if ls else np.nan
        m = yr < 2025; w = p[m][p[m] > 0].sum(); ls = -p[m][p[m] < 0].sum()
        r.update({"n": int(m.sum()), "win%": round(100 * (p[m] > 0).mean(), 1), "PF": round(w / ls, 2), "minPF": min(r[str(Y)] for Y in range(2020, 2025))})
        rows.append(r)
R = pd.DataFrame(rows); pd.set_option("display.width", 220); pd.set_option("display.max_rows", 200)
print(R[R.cost == 0.0].sort_values("minPF", ascending=False).to_string(index=False))
print(); print(R[R.cost == 0.04].sort_values("minPF", ascending=False).head(10).to_string(index=False))
