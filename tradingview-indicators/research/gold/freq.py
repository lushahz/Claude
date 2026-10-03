"""More trades with 1:2 exits (SL 1.25, TP1 1.5R half, TP2 2R, 72 bars): loosen divergence threshold, 1h rule, ATR gate, session."""
import numpy as np, pandas as pd, itertools, warnings; warnings.filterwarnings("ignore")
from tp12lib import sim2
from glab import session_mask, session_end_flags
import grid2_fams as G
df, f = G.df, G.f; X = pd.read_pickle("bars/XAUUSD_xfeat.pkl")
def nz(x): return np.nan_to_num(np.asarray(x, dtype=float), nan=0.0)
o, h, l, c = (df[k].to_numpy() for k in "ohlc"); cp = np.r_[c[0], c[:-1]]; a = f.atr.to_numpy()
res = nz(X.gd_res12); lead = nz(X.xag_lead12); clv = nz(f.clv); h4 = nz(f.h4_trend); h1 = nz(f.h1_trend)
se = session_end_flags(df.index); dates = df.index
lonL0, lonS0 = G.fams["London breaks Asian range + h4 trend (buf 0.0)"]
def build(z, h1rule, gate, sess_hours):
    bL = pd.Series(res <= -z).rolling(3, min_periods=1).max().to_numpy() > 0
    bS = pd.Series(res >= z).rolling(3, min_periods=1).max().to_numpy() > 0
    dL = bL & (c > cp) & (clv > 0.6) & (lead > 0) & (h4 >= 0); dS = bS & (c < cp) & (clv < 0.4) & (lead < 0) & (h4 <= 0)
    sess = session_mask(df.index, *sess_hours)
    L = (dL | lonL0) & sess & (a >= gate); S = (dS | lonS0) & sess & (a >= gate)
    if h1rule == "strict": L &= h1 > 0; S &= h1 < 0
    if h1rule == "not against": L &= h1 >= 0; S &= h1 <= 0
    return L, S & ~L
rows = []
for z, h1rule, gate, sh in itertools.product((2.5, 2.0, 1.5), ("strict", "not against", "off"), (2.0, 1.5), ((7, 16), (6, 18))):
    L, S = build(z, h1rule, gate, sh)
    sig = L | S; side = np.where(L, 1.0, -1.0)
    R = sim2(o, h, l, c, a, sig, side, 1.25, 1.875, 2.5, 72, se, 0.30, False)
    d = pd.to_datetime(dates.to_numpy()[R[:, 0].astype(int)])
    r = {"divZ": z, "h1": h1rule, "minATR": gate, "session": f"{sh[0]}-{sh[1]}"}
    for per, m in (("09-19", d < "2020"), ("20-22", (d >= "2020") & (d < "2023")), ("23-26", d >= "2023"), ("25-26", d >= "2025")):
        m = np.asarray(m); p = R[m, 1]; w = p[p > 0].sum(); ls = -p[p < 0].sum()
        r[f"{per}_pf"] = round(w / ls, 2) if ls else np.inf
        if per == "25-26": r["trades/week 25-26"] = round(len(p) / (len(pd.bdate_range("2025-01-01", "2026-09-24")) / 5), 2); r["win 25-26"] = round((p > 0).mean(), 2)
        if per == "20-22": r["n20-26"] = int((d >= "2020").sum())
    r["minRecent"] = min(r["20-22_pf"], r["23-26_pf"])
    rows.append(r)
R = pd.DataFrame(rows); R.to_pickle("freq.pkl")
pd.set_option("display.width", 250); pd.set_option("display.max_rows", 100)
print(R.sort_values("trades/week 25-26").to_string(index=False))
