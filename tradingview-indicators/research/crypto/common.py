import numpy as np, pandas as pd, sys, warnings
warnings.filterwarnings("ignore")
sys.path.insert(0, ".")
from revdots import sma, ema, rma, rsi, stoch

U = None

def load(fn):
    d = pd.read_csv(f"{fn}.csv")
    d.index = pd.to_datetime(d.t, unit="s").dt.normalize()
    d = d[~d.index.duplicated(keep="last")][["o", "h", "l", "c", "v"]].astype(float)
    # drop zero/negative-range glitches
    d = d[(d.h >= d.l) & (d.c > -1e9)]
    return d

def atr(df, n=14):
    h, l, c = df.h.to_numpy(), df.l.to_numpy(), df.c.to_numpy()
    pc = np.r_[np.nan, c[:-1]]
    tr = np.nanmax(np.vstack([h - l, np.abs(h - pc), np.abs(l - pc)]), axis=0)
    return rma(tr, n)

def zigzag(c, thr):
    """Pivot indices on close with relative threshold thr (fraction). Returns list of (idx, +1 top / -1 bottom)."""
    piv = []; n = len(c)
    trend = 0; ext_i = 0
    for i in range(1, n):
        if trend >= 0:
            if c[i] > c[ext_i] or trend == 0 and c[i] > c[ext_i]:
                ext_i = i if trend == 1 or c[i] > c[ext_i] else ext_i
            if trend == 0:
                # initialise on first move of thr
                lo = np.argmin(c[:i + 1]); hi = np.argmax(c[:i + 1])
                if c[i] >= c[lo] * (1 + thr): trend = 1; piv.append((lo, -1)); ext_i = i
                elif c[i] <= c[hi] * (1 - thr): trend = -1; piv.append((hi, 1)); ext_i = i
                continue
            if c[i] > c[ext_i]: ext_i = i
            if c[i] <= c[ext_i] * (1 - thr):
                piv.append((ext_i, 1)); trend = -1; ext_i = i
        else:
            if c[i] < c[ext_i]: ext_i = i
            if c[i] >= c[ext_i] * (1 + thr):
                piv.append((ext_i, -1)); trend = 1; ext_i = i
    return piv
