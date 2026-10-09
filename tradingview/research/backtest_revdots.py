"""Backtest of the Reversal Dots Oscillator trade logic (Python port of the Pine script).

Downloads public Binance data (spot klines + USDT-M perpetual klines for the premium
filter), rebuilds the WaveTrend waves, the weekly HTF state and the trade engine
(Entry next open, swing stop + 0.25 ATR, TP1/TP2/TP3 at 1R/2R/3R one third each,
stop to entry after TP1, 0.10% round-trip cost), then compares the old defaults with
the new trend setups.

    python3 backtest_revdots.py                 # BTCUSDT, 1d chart, weekly HTF
    python3 backtest_revdots.py ETHUSDT 1d
    python3 backtest_revdots.py BTCUSDT 12h

Needs pandas and numpy. Data comes from data-api.binance.vision / data.binance.vision.
"""
import io, json, sys, time, zipfile, datetime as dt, urllib.request
import numpy as np, pandas as pd

UA = {"User-Agent": "revdots-backtest"}


def _get(url):
    for i in range(5):
        try:
            with urllib.request.urlopen(urllib.request.Request(url, headers=UA), timeout=30) as r:
                return r.read()
        except Exception as e:
            if getattr(e, "code", None) == 404:
                return None
            time.sleep(1 + 2 * i)
    raise RuntimeError(url)


def spot_klines(sym, iv):
    out, start = [], int(dt.datetime(2017, 1, 1).timestamp() * 1000)
    while True:
        js = json.loads(_get(f"https://data-api.binance.vision/api/v3/klines?symbol={sym}&interval={iv}&startTime={start}&limit=1000"))
        out += js
        if len(js) < 1000:
            break
        start = js[-1][0] + 1
    df = pd.DataFrame([r[:6] for r in out], columns=["t", "o", "h", "l", "c", "v"]).astype(float)
    df["t"] = pd.to_datetime(df.t, unit="ms")
    return df.set_index("t")


def perp_closes(sym, iv):
    rows, today = [], dt.date.today()
    y, m = 2019, 9
    while (y, m) < (today.year, today.month):
        b = _get(f"https://data.binance.vision/data/futures/um/monthly/klines/{sym}/{iv}/{sym}-{iv}-{y}-{m:02d}.zip")
        if b:
            z = zipfile.ZipFile(io.BytesIO(b))
            for ln in z.read(z.namelist()[0]).decode().splitlines():
                p = ln.split(",")
                if p[0].isdigit():
                    rows.append((int(p[0]), float(p[4])))
        m += 1
        if m == 13:
            y, m = y + 1, 1
    d = dt.date(today.year, today.month, 1)
    while d < today:
        b = _get(f"https://data.binance.vision/data/futures/um/daily/klines/{sym}/{iv}/{sym}-{iv}-{d}.zip")
        if b:
            z = zipfile.ZipFile(io.BytesIO(b))
            for ln in z.read(z.namelist()[0]).decode().splitlines():
                p = ln.split(",")
                if p[0].isdigit():
                    rows.append((int(p[0]), float(p[4])))
        d += dt.timedelta(days=1)
    s = pd.Series(dict(rows)).sort_index()
    s.index = pd.to_datetime(s.index, unit="ms")
    return s[~s.index.duplicated()]


# --- Pine built-ins -----------------------------------------------------------
def ema(x, n):
    a, out, s = 2 / (n + 1), np.full(len(x), np.nan), np.nan
    for i, v in enumerate(x):
        if not np.isnan(v):
            s = v if np.isnan(s) else a * v + (1 - a) * s
        out[i] = s
    return out


def rma(x, n):
    out, s, buf = np.full(len(x), np.nan), np.nan, []
    for i, v in enumerate(x):
        if np.isnan(v):
            continue
        if np.isnan(s):
            buf.append(v)
            if len(buf) == n:
                s = np.mean(buf)
                out[i] = s
        else:
            s = (s * (n - 1) + v) / n
            out[i] = s
    return out


def waves(src, ch=9, avg=12, ma=3):
    esa = ema(src, ch)
    de = ema(np.abs(src - esa), ch)
    deF = np.maximum(np.nan_to_num(de), np.abs(np.nan_to_num(esa)) * 1e-4)
    ci = np.where(deF == 0, 0.0, (src - esa) / (0.015 * deF))
    w1 = ema(ci, avg)
    return w1, pd.Series(w1).rolling(ma).mean().values


def cross(a, b, up):
    a, b = pd.Series(a), pd.Series(b)
    return (((a > b) & (a.shift() <= b.shift())) if up else ((a < b) & (a.shift() >= b.shift()))).values


# --- signals ------------------------------------------------------------------
def signals(df, perp=None):
    h, l, c = df.h.values, df.l.values, df.c.values
    w1, w2 = waves((h + l + c) / 3)
    s = pd.DataFrame(index=df.index)
    s["w2"], s["cu"], s["cd"] = w2, cross(w1, w2, True), cross(w1, w2, False)
    s["bigBuy"] = s.cu & (s.w2 <= -53)
    s["bigSell"] = s.cd & (s.w2 >= 53)
    tr = np.maximum(h - l, np.maximum(np.abs(h - np.roll(c, 1)), np.abs(l - np.roll(c, 1))))
    tr[0] = h[0] - l[0]
    s["atr"] = rma(tr, 14)
    # weekly HTF, last closed week (request.security + lookahead_on + [1])
    wk = df.resample("W-MON", label="left", closed="left").agg({"h": "max", "l": "min", "c": "last"}).dropna()
    hw1, hw2 = waves(((wk.h + wk.l + wk.c) / 3).values)
    st = pd.DataFrame({"hW1": hw1, "hW2": hw2, "hW1p": pd.Series(hw1).shift().values}, index=wk.index).shift()
    s = s.join(st.reindex(df.index, method="ffill"))
    s["htfBull"] = s.hW2 <= 0
    s["htfBear"] = s.hW2 >= 0
    rising, falling = s.hW1 > s.hW1p, s.hW1 < s.hW1p
    s["trendBuy"] = s.cu & (s.w2 <= 0) & rising & (s.hW2 <= 20)
    prem_ok = np.ones(len(s), bool)
    if perp is not None:
        prem = (perp.reindex(df.index) / df.c - 1) * 100
        chg = (prem.rolling(3).mean() - prem.rolling(30).mean()).values
        prem_ok = np.isnan(chg) | (chg >= 0)
    s["trendSell"] = s.cd & (s.w2 >= -100) & falling & (s.hW2 >= -20) & prem_ok
    return s


# --- trade engine (same order of checks as the Pine script) ---------------------
def backtest(df, s, trigL, trigS, flip=False, swing=10, buf=0.25, tps=(1, 2, 3), be=True, cost=0.10, warm=50):
    o, h, l, c, atr = df.o.values, df.h.values, df.l.values, df.c.values, s.atr.values
    swLo, swHi = df.l.rolling(swing).min().values, df.h.rolling(swing).max().values
    side = pend = 0
    trades = []
    for i in range(len(df)):
        exit_, flip_to = False, 0
        if pend and not side:
            side, ep = pend, o[i]
            stp = pSwLo - buf * pAtr if side > 0 else pSwHi + buf * pAtr
            rk = side * (ep - stp)
            if rk < 0.2 * pAtr:
                rk = 0.2 * pAtr
                stp = ep - side * rk
            st, T, got, pnl, ent = stp, [ep + side * t * rk for t in tps], 0, 0.0, i
        pend = 0
        if side:
            if (l[i] <= st) if side > 0 else (h[i] >= st):
                xp = min(o[i], st) if side > 0 else max(o[i], st)
                pnl += (3 - got) / 3 * side * (xp - ep)
                exit_ = True
            else:
                for j in range(3):
                    if got == j and ((h[i] >= T[j]) if side > 0 else (l[i] <= T[j])):
                        got, pnl = j + 1, pnl + side * (T[j] - ep) / 3
                        if j == 0 and be:
                            st = ep
                exit_ = got == 3
                if not exit_ and flip and i >= warm and (trigS[i] if side > 0 else trigL[i]):
                    pnl += (3 - got) / 3 * side * (c[i] - ep)
                    exit_, flip_to = True, -side
        active = side != 0
        if exit_:
            trades.append(dict(entry=df.index[ent], side=side, R=(pnl - cost / 100 * ep) / rk, got=got))
            side = 0
        can_open = not side and not exit_ and not active and i >= warm
        newL = trigL[i] and (can_open or flip_to == 1)
        newS = trigS[i] and (can_open or flip_to == -1) and not newL
        if newL or newS:
            pend, pSwLo, pSwHi, pAtr = (1 if newL else -1), swLo[i], swHi[i], atr[i]
    return pd.DataFrame(trades)


def report(t, name):
    if t.empty:
        return dict(setup=name, trades=0)
    w, L = t.R[t.R > 0].sum(), -t.R[t.R < 0].sum()
    eq = t.R.cumsum()
    lo, sh = t[t.side > 0], t[t.side < 0]
    return dict(setup=name, trades=len(t), win_pct=round(100 * (t.R > 0).mean(), 1), pf=round(w / L, 2) if L else np.inf,
                net_R=round(t.R.sum(), 1), max_dd_R=round((eq.cummax() - eq).max(), 1),
                longs=len(lo), long_R=round(lo.R.sum(), 1), shorts=len(sh), short_R=round(sh.R.sum(), 1),
                short_win_pct=round(100 * (sh.R > 0).mean(), 1) if len(sh) else np.nan)


if __name__ == "__main__":
    sym = sys.argv[1] if len(sys.argv) > 1 else "BTCUSDT"
    iv = sys.argv[2] if len(sys.argv) > 2 else "1d"
    df = spot_klines(sym, iv)
    try:
        perp = perp_closes(sym, iv)
    except Exception as e:
        print("no perp data:", e)
        perp = None
    s = signals(df, perp)
    s0 = signals(df, None)
    z = np.zeros(len(s), bool)
    B, S = s.bigBuy.values, s.bigSell.values
    rows = [
        report(backtest(df, s, B, z), "OLD default: big buys, longs only"),
        report(backtest(df, s, B, S), "OLD big signals, longs + shorts"),
        report(backtest(df, s, B & s.htfBull.values, S & s.htfBear.values), "OLD setup arrows, longs + shorts"),
        report(backtest(df, s0, s0.trendBuy.values, s0.trendSell.values), "NEW trend setups, no flip, no premium filter"),
        report(backtest(df, s0, s0.trendBuy.values, s0.trendSell.values, flip=True), "NEW trend setups + flip"),
        report(backtest(df, s, s.trendBuy.values, s.trendSell.values, flip=True), "NEW trend setups + flip + premium (default)"),
        report(backtest(df, s, s.trendBuy.values | B, s.trendSell.values, flip=True), "NEW trend setups + big buys + flip + premium"),
    ]
    pd.set_option("display.width", 200)
    print(f"{sym} {iv}, weekly HTF, {df.index[0].date()} - {df.index[-1].date()}")
    print(pd.DataFrame(rows).to_string(index=False))
