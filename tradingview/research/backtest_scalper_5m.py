"""Backtest of RevDots Scalper 5m (Python port of tradingview/revdots-scalper-5m.pine).

Downloads Binance USDT-M perpetual 5m klines (data.binance.vision) and replays the indicator's
logic bar by bar: signal on the bar close, entry at the next open, TP / SL / time exit checked on
5m bars (stop first when both are touched), 0.08% round-trip cost.

    python3 backtest_scalper_5m.py            # BTCUSDT
    python3 backtest_scalper_5m.py ETHUSDT
"""
import io, sys, time, zipfile, datetime as dt, urllib.request
from concurrent.futures import ThreadPoolExecutor
import numpy as np, pandas as pd


def _get(url):
    for i in range(5):
        try:
            with urllib.request.urlopen(urllib.request.Request(url, headers={"User-Agent": "revscalp-backtest"}), timeout=60) as r:
                return r.read()
        except Exception as e:
            if getattr(e, "code", None) == 404:
                return None
            time.sleep(1 + 2 * i)
    return None


def _parse(b):
    if not b:
        return None
    z = zipfile.ZipFile(io.BytesIO(b))
    lines = [l for l in z.read(z.namelist()[0]).decode().splitlines() if l and l[0].isdigit()]
    return np.array([l.split(",")[:6] for l in lines], dtype=float)


def klines_5m(sym, start=(2020, 1)):
    base = f"https://data.binance.vision/data/futures/um"
    urls, (y, m), today = [], start, dt.date.today()
    while (y, m) < (today.year, today.month):
        urls.append(f"{base}/monthly/klines/{sym}/5m/{sym}-5m-{y}-{m:02d}.zip")
        y, m = (y + 1, 1) if m == 12 else (y, m + 1)
    d = dt.date(today.year, today.month, 1)
    while d < today:
        urls.append(f"{base}/daily/klines/{sym}/5m/{sym}-5m-{d}.zip")
        d += dt.timedelta(days=1)
    with ThreadPoolExecutor(8) as ex:
        parts = [p for p in ex.map(lambda u: _parse(_get(u)), urls) if p is not None]
    df = pd.DataFrame(np.vstack(parts), columns=["t", "o", "h", "l", "c", "v"])
    df["t"] = pd.to_datetime(df.t.astype("int64"), unit="ms")
    return df.drop_duplicates("t").sort_values("t").set_index("t")


def ema(x, n):
    a, out, s = 2 / (n + 1), np.empty(len(x)), np.nan
    for i, v in enumerate(x):
        s = v if np.isnan(s) else a * v + (1 - a) * s
        out[i] = s
    return out


def rma(x, n):
    out, s = np.full(len(x), np.nan), np.nan
    for i in range(n - 1, len(x)):
        s = np.mean(x[i - n + 1:i + 1]) if np.isnan(s) else (s * (n - 1) + x[i]) / n
        out[i] = s
    return out


def rsi(c, n=14):
    d = np.diff(c, prepend=np.nan)
    up, dn = rma(np.nan_to_num(np.maximum(d, 0)), n), rma(np.nan_to_num(np.maximum(-d, 0)), n)
    with np.errstate(divide="ignore", invalid="ignore"):
        return np.where(dn == 0, 100.0, 100 - 100 / (1 + up / dn))


def backtest(df, vwapDist=3.0, rsiMax=30, spike=0.7, days=30, trendLen=50, tpAtr=1.0, slAtr=10.0, hold=24, cost=0.08):
    o, h, l, c, v = (df[k].values for k in "ohlcv")
    tr = np.maximum(h - l, np.maximum(np.abs(h - np.roll(c, 1)), np.abs(l - np.roll(c, 1))))
    tr[0] = h[0] - l[0]
    atr, r = rma(tr, 14), rsi(c, 14)
    day = df.index.floor("D")
    vwap = (pd.Series((h + l + c) / 3 * v).groupby(day).cumsum() / pd.Series(v).groupby(day).cumsum()).values
    hb = df.resample("1h", label="left", closed="left").agg({"h": "max", "l": "min", "c": "last"}).dropna()
    hh, hl, hc = hb.h.values, hb.l.values, hb.c.values
    htr = np.maximum(hh - hl, np.maximum(np.abs(hh - np.roll(hc, 1)), np.abs(hl - np.roll(hc, 1))))
    htr[0] = hh[0] - hl[0]
    base = pd.Series(pd.Series(rma(htr, 14)).rolling(days * 24).mean().values, index=hb.index).shift(1)  # last closed 1h bar
    ratio = atr / base.reindex(df.index, method="ffill").values
    d = df.c.resample("1D").last().dropna()
    dUp = pd.Series(d.values > ema(d.values, trendLen), index=d.index).shift(1).reindex(day).fillna(False).values.astype(bool)
    setup = (ratio >= spike) & ((c - vwap) / atr <= -vwapDist) & (r < rsiMax) & dUp
    pos = pend = 0
    trades = []
    for i in range(len(df)):
        if pend and not pos:
            pos, ep, sl, eb = 1, o[i], pSl, i
            tp = ep + tpAtr / slAtr * (ep - pSl)
        pend, ex = 0, False
        if pos:
            if l[i] <= sl:
                ex, xp, why = True, min(o[i], sl), "SL"
            elif h[i] >= tp:
                ex, xp, why = True, max(o[i], tp), "TP"
            elif i - eb >= hold:
                ex, xp, why = True, c[i], "Time"
        was = pos == 1
        if ex:
            trades.append((df.index[eb], (xp / ep - 1) * 100 - cost, why))
            pos = 0
        if setup[i] and not pos and not pend and not ex and not was:
            pend, pSl = 1, c[i] - slAtr * atr[i]
    return pd.DataFrame(trades, columns=["entry", "pct", "exit"])


if __name__ == "__main__":
    sym = sys.argv[1] if len(sys.argv) > 1 else "BTCUSDT"
    df = klines_5m(sym)
    T = backtest(df)
    eq = T.pct.cumsum()
    print(f"{sym} 5m perp, {df.index[0].date()} - {df.index[-1].date()}")
    print(f"trades {len(T)} | won {100 * (T.pct > 0).mean():.1f}% | avg {T.pct.mean():+.3f}% | profit factor "
          f"{T.pct[T.pct > 0].sum() / -T.pct[T.pct < 0].sum():.2f} | total {T.pct.sum():+.1f}% | max DD {(eq.cummax() - eq).max():.1f}%")
    print(T.exit.value_counts().to_string())
    T["year"] = T.entry.dt.year
    print(T.groupby("year").pct.agg(trades="size", won=lambda x: round(100 * (x > 0).mean(), 1), avg_pct=lambda x: round(x.mean(), 3), total_pct=lambda x: round(x.sum(), 1)).T.to_string())
