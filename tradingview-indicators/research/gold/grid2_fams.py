import numpy as np, pandas as pd, itertools, warnings; warnings.filterwarnings("ignore")
from glab import run, stats, session_mask
df = pd.read_pickle("bars/XAUUSD_5m.pkl"); f = pd.read_pickle("bars/XAUUSD_feat.pkl")
c = df.c.to_numpy(); h = df.h.to_numpy(); l = df.l.to_numpy(); n = len(c)
ny = f.ny_min.to_numpy(); hr = f.hour_utc.to_numpy(); tday = f.tday.to_numpy()
def nz(x): return np.nan_to_num(np.asarray(x, dtype=float), nan=0.0)
h4 = nz(f.h4_trend); h1 = nz(f.h1_trend)
# --- A. time-of-day drift (mean next-bar return in ATR by NY half-hour)
a = f.atr.to_numpy(); r1 = (np.r_[c[1:], c[-1]] - c) / a
slot = (ny // 30) * 30
T = pd.DataFrame({"slot": slot, "r": r1, "yr": df.index.year})
T = T[np.isfinite(T.r)]
prof = T.groupby([np.where(T.yr < 2020, "2009-19", np.where(T.yr < 2023, "2020-22", "2023-26")), "slot"]).r.mean().unstack(0) * 100
prof.index = [f"{s//60:02d}:{s%60:02d} NY" for s in prof.index]
#print("Mean next-5m return x100 (ATR units) by New York time:"); print(prof.round(2).loc[[i for i in prof.index if "03:00" <= i[:5] <= "12:00"]].to_string())
# --- breakout helpers
def first_break(level_hi, level_lo, window, buf):
    """first close above level_hi+buf (long) / below level_lo-buf (short) inside window, once per day per side"""
    L = np.zeros(n, bool); S = np.zeros(n, bool); doneL = {}; doneS = {}
    for i in np.flatnonzero(window):
        d = tday[i]
        if not np.isfinite(level_hi[i]) or not np.isfinite(level_lo[i]): continue
        if c[i] > level_hi[i] + buf[i] and d not in doneL: L[i] = True; doneL[d] = 1
        if c[i] < level_lo[i] - buf[i] and d not in doneS: S[i] = True; doneS[d] = 1
    return L, S
# Asian range = 17:00-03:00 NY; London window 03:00-06:00 NY
asia = (ny >= 17 * 60) | (ny < 3 * 60)
s = pd.Series(np.where(asia, h, np.nan)); ah = s.groupby(tday).cummax().groupby(tday).ffill().to_numpy()
s = pd.Series(np.where(asia, l, np.nan)); al = s.groupby(tday).cummin().groupby(tday).ffill().to_numpy()
# NY opening range 08:30-09:00 NY, breakout window 09:00-11:30
orw = (ny >= 510) & (ny < 540)
s = pd.Series(np.where(orw, h, np.nan)); oh = s.groupby(tday).cummax().groupby(tday).ffill().to_numpy()
s = pd.Series(np.where(orw, l, np.nan)); ol = s.groupby(tday).cummin().groupby(tday).ffill().to_numpy()
fams = {}
for buf_k in (0.0, 0.25):
    L, S = first_break(ah, al, (ny >= 180) & (ny < 360), buf_k * a)
    fams[f"London breaks Asian range (buf {buf_k} ATR)"] = (L, S)
    fams[f"London breaks Asian range + h4 trend (buf {buf_k})"] = (L & (h4 > 0), S & (h4 < 0))
    L, S = first_break(oh, ol, (ny >= 540) & (ny < 690), buf_k * a)
    fams[f"NY opening-range breakout (buf {buf_k})"] = (L, S)
    fams[f"NY opening-range breakout + h4 trend (buf {buf_k})"] = (L & (h4 > 0), S & (h4 < 0))
st = nz(f.st); stp = np.r_[st[0], st[:-1]]; adx = nz(f.adx)
sess = session_mask(df.index)
fams["Supertrend flip + h4 trend"] = (sess & (st > 0) & (stp < 0) & (h4 > 0), sess & (st < 0) & (stp > 0) & (h4 < 0))
fams["Supertrend flip + h4 trend + ADX>25"] = (sess & (st > 0) & (stp < 0) & (h4 > 0) & (adx > 25), sess & (st < 0) & (stp > 0) & (h4 < 0) & (adx > 25))
stack = nz(f.ema_stack); d21 = nz(f.d_ema21); clv = nz(f.clv); cp = np.r_[c[0], c[:-1]]
touchL = pd.Series(d21 <= 0.2).rolling(3, min_periods=1).max().to_numpy() > 0
touchS = pd.Series(d21 >= -0.2).rolling(3, min_periods=1).max().to_numpy() > 0
fams["EMA21 pullback in full EMA stack + h4"] = (sess & (stack == 3) & (h4 > 0) & touchL & (c > cp) & (clv > 0.6) & (d21 > 0),
                                               sess & (stack == -3) & (h4 < 0) & touchS & (c < cp) & (clv < 0.4) & (d21 < 0))
