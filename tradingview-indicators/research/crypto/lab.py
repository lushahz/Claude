import numpy as np, pandas as pd, pickle, os, sys
sys.path.insert(0, ".")
from common import load, atr, zigzag
from features import features, divergences
from revdots import ema, sma
SPLIT = pd.Timestamp("2022-01-01")
COINS = pd.read_csv("coins.csv").coin.tolist()

def rmin(x, n): return pd.Series(x).rolling(n, min_periods=1).min().to_numpy()
def rmax(x, n): return pd.Series(x).rolling(n, min_periods=1).max().to_numpy()

def build_all():
    out = {}
    for c in COINS:
        d = load(c); f = features(d)
        bull, bear = divergences(f.w2.to_numpy(), d.l.to_numpy(), d.h.to_numpy()); f["bull_div"], f["bear_div"] = bull, bear
        f["e20"] = ema(d.c.to_numpy(), 20); f["e50"] = ema(d.c.to_numpy(), 50); f["e200"] = ema(d.c.to_numpy(), 200)
        thr = max(0.04, 7 * np.nanmedian(f.atrp))
        out[c] = dict(d=d, f=f, piv=zigzag(d.c.to_numpy(), thr), thr=thr)
    # BTC context aligned by date (uses BTC values known at the same daily close)
    b = out["BTC"]; bf = b["f"]; bd = b["d"]
    ctx = pd.DataFrame({"btc_w2": bf.w2, "btc_rsi": bf.rsi, "btc_above200": (bd.c > bf.e200).astype(float),
                        "btc_d50": bf.d50, "btc_up": bf.up.astype(float)}, index=bd.index)
    for c, x in out.items():
        m = ctx.reindex(x["d"].index).ffill()
        for col in m.columns: x["f"][col] = m[col].to_numpy()
    return out

if __name__ == "__main__":
    data = build_all(); pickle.dump(data, open("cdata.pkl", "wb"))
    for c, x in data.items():
        print(f"{c:5s} bars {len(x['d'])} swing {x['thr']*100:5.1f}% bottoms {sum(1 for p in x['piv'] if p[1]==-1)}")
