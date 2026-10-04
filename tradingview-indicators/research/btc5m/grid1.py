"""Reversal entries x exits x costs on BTC 5m (IS 2020-23, VAL 2024)."""
import numpy as np, pandas as pd, itertools, warnings; warnings.filterwarnings("ignore")
from lab import run, per
df = pd.read_pickle("btc5m_raw.pkl"); F = pd.read_pickle("btc5m_feat.pkl")
def nz(x): return np.nan_to_num(np.asarray(x, dtype=float))
w2, rsi7, bb, clv, cvd3, h1t, h4t = (nz(F[k]) for k in ("wt2", "rsi7", "bb", "clv", "cvd3", "h1_trend", "h4_trend"))
c = df.c.to_numpy(); o = df.o.to_numpy()
cu, cd, tu, td = (F[k].to_numpy(bool) for k in ("cross_up", "cross_dn", "turn_up", "turn_dn"))
bdv, sdv = F.bull_div6.to_numpy(bool), F.bear_div6.to_numpy(bool)
E = {
 "big buy/sell (wt2 +-53 cross)": (cu & (w2 <= -53), cd & (w2 >= 53)),
 "big + divergence":              (cu & (w2 <= -53) & bdv, cd & (w2 >= 53) & sdv),
 "early turn (wt2 +-60)":         (tu & (w1 := nz(F.wt1)) < w2) & (w2 <= -60) if False else (tu & (nz(F.wt1) < w2) & (w2 <= -60), td & (nz(F.wt1) > w2) & (w2 >= 60)),
 "stretch: rsi7<20 & bb<-1 + green bar": ((rsi7 < 20) & (bb < -1) & (c > o) & (clv > 0.5), (rsi7 > 80) & (bb > 1) & (c < o) & (clv < 0.5)),
 "stretch + seller exhaustion (cvd3<-0.3)": ((rsi7 < 25) & (bb < -1) & (cvd3 < -0.3) & (c > o), (rsi7 > 75) & (bb > 1) & (cvd3 > 0.3) & (c < o)),
}
rows = []
for (en, (L, S)), (slk, tpk, mb), cost in itertools.product(E.items(), [(1, 1, 24), (1.5, 1, 24), (2, 1, 36), (2, 0.75, 24), (3, 1, 48), (1, 0.5, 12), (1.5, 0.75, 24), (1, 1.5, 36)], (0.0, 0.04, 0.1)):
    for side in ("long", "both"):
        LL, SS = (L, np.zeros_like(S)) if side == "long" else (L, S & ~L)
        T = run(df, F, LL, SS, slk, tpk, mb, cost)
        r = {"entry": en, "side": side, "SL": slk, "TP": tpk, "bars": mb, "cost%": cost}; r.update(per(T)); rows.append(r)
R = pd.DataFrame(rows); R.to_pickle("grid1.pkl")
pd.set_option("display.width", 260); pd.set_option("display.max_rows", 400); pd.set_option("display.max_colwidth", 40)
print("Rows with IS win >= 60% at 0.04% cost, sorted by IS PF:")
q = R[(R["cost%"] == 0.04) & (R["IS 20-23 win"] >= 60)].sort_values("IS 20-23 pf", ascending=False)
print(q.head(25).to_string(index=False))
print("\nBest IS PF at 0% cost (gross edge):")
print(R[R["cost%"] == 0.0].sort_values("IS 20-23 pf", ascending=False).head(15).to_string(index=False))
