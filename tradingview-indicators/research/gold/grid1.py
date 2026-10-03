import numpy as np, pandas as pd, itertools, warnings; warnings.filterwarnings("ignore")
from glab import run, stats, session_mask
df = pd.read_pickle("bars/XAUUSD_5m.pkl"); f = pd.read_pickle("bars/XAUUSD_feat.pkl")
sess = session_mask(df.index) & (df.n.to_numpy() >= 4)
c = df.c.to_numpy(); cp = np.r_[c[0], c[:-1]]
def nz(s): return np.nan_to_num(s.to_numpy() if hasattr(s, "to_numpy") else s, nan=0.0)
def recent(x, n): return pd.Series(x.astype(float)).rolling(n, min_periods=1).max().to_numpy() > 0
wt2 = nz(f.wt2); rsi7 = nz(f.rsi7); bb = nz(f.bb_pos); clv = nz(f.clv)
bull_bar = (c > cp) & (clv >= 0.5); bear_bar = (c < cp) & (clv <= 0.5)
def trend(tf, k): return nz(f[f"{tf}_trend"]) >= k, nz(f[f"{tf}_trend"]) <= -k
def osc(kind, lvl):
    if kind == "wt":  return recent(wt2 <= -lvl, 3), recent(wt2 >= lvl, 3)
    if kind == "rsi": return recent(rsi7 <= 50 - lvl, 3), recent(rsi7 >= 50 + lvl, 3)
    if kind == "bb":  return recent(bb <= -lvl, 3), recent(bb >= lvl, 3)
def build(tf, tk, kind, lvl, trig):
    if tf == "none": up = dn = np.ones(len(c), bool)
    else: up, dn = trend(tf, tk)
    os_, ob = osc(kind, lvl)
    tl = nz(f.wt_up).astype(bool) if trig == "wtcross" else bull_bar
    ts = nz(f.wt_dn).astype(bool) if trig == "wtcross" else bear_bar
    L = sess & up & os_ & tl; S = sess & dn & ob & ts
    sig = L | S; side = np.where(L, 1.0, -1.0)
    return sig, side
if __name__ == "__main__":
    rows = []
    GRID = list(itertools.product(["h4", "h1", "none"], [1, 2], ["wt", "rsi", "bb"], ["lo", "hi"], ["wtcross", "bar"], [(1.0, 1.0), (1.0, 1.5), (1.5, 1.5), (1.0, 2.0)], [12, 24]))
    LVL = {"wt": {"lo": 40, "hi": 60}, "rsi": {"lo": 20, "hi": 30}, "bb": {"lo": 1.0, "hi": 1.3}}
    for tf, tk, kind, lv, trig, (sk, tg), mb in GRID:
        if tf == "none" and tk == 2: continue
        sig, side = build(tf, tk, kind, LVL[kind][lv], trig)
        T = run(df, f, sig, side, sk, tg, mb, 0.30)
        r = {"tf": tf, "tk": tk, "osc": kind, "lvl": lv, "trig": trig, "stop": sk, "tgt": tg, "maxb": mb}
        for per, m in (("IS", T.date < "2020-01-01"), ("VAL", (T.date >= "2020-01-01") & (T.date < "2023-01-01")), ("OOS", T.date >= "2023-01-01")):
            s = stats(T[m]); r.update({f"{per}_{k}": v for k, v in s.items() if k in ("n", "per_day", "win", "avg_R", "pf")})
        rows.append(r)
    R = pd.DataFrame(rows); R.to_pickle("grid1.pkl")
    pd.set_option("display.width", 250); pd.set_option("display.max_rows", 60)
    print(R.sort_values("IS_pf", ascending=False).head(25).to_string(index=False))
    print(R.sort_values("OOS_pf", ascending=False).head(10).to_string(index=False))
