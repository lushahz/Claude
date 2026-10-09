"""Backtest of RevDots Scalp Scanner (Python replay of tradingview/revdots-scalp-scanner.pine).

Downloads Binance USDT-M perpetual 5m klines for the 9 default coins and replays the scanner bar by bar:
all coins are checked on each 5m bar in list order, one trade per coin, at most MAX_OPEN trades open in
total, entry at the next open, TP +1 ATR / SL -10 ATR / time exit after 24 bars, 0.08% round-trip cost.

    python3 backtest_scanner_5m.py                # Active mode, max 5 open
    python3 backtest_scanner_5m.py Balanced 5
"""
import sys
import numpy as np, pandas as pd
from backtest_scalper_5m import klines_5m, rma, ema, rsi

COINS = ["BTCUSDT", "ETHUSDT", "SOLUSDT", "XRPUSDT", "BNBUSDT", "DOGEUSDT", "ADAUSDT", "AVAXUSDT", "LINKUSDT"]
MODES = {"Active": (0.45, 2.0, 30), "Balanced": (0.7, 2.0, 40), "Strict": (0.7, 3.0, 30)}


def coin_arrays(df, spike, vwapDist, rsiMax):
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
    base = pd.Series(pd.Series(rma(htr, 14)).rolling(720).mean().values, index=hb.index).shift(1)
    ratio = atr / base.reindex(df.index, method="ffill").values
    d = df.c.resample("1D").last().dropna()
    up = pd.Series(d.values > ema(d.values, 50), index=d.index).shift(1).reindex(day).fillna(False).values.astype(bool)
    setup = (ratio >= spike) & ((c - vwap) / atr <= -vwapDist) & (r < rsiMax) & up
    return pd.DataFrame({"o": o, "h": h, "l": l, "c": c, "a": atr, "s": setup}, index=df.index)


def replay(frames, max_open=5, tpA=1.0, slA=10.0, hold=24, cost=0.08):
    idx = frames[0].index
    X = [f.reindex(idx, method="ffill") for f in frames]
    O, H, L, C, A = (np.vstack([x[k].values for x in X]) for k in "ohlca")
    S = np.vstack([f.s.reindex(idx).fillna(False).values.astype(bool) for f in frames])
    K, N = O.shape
    pos, pend, eb = np.zeros(K, int), np.zeros(K, int), np.zeros(K, int)
    ep, sl, tp, pSl, pTp = (np.zeros(K) for _ in range(5))
    out = []
    for i in range(N):
        for k in range(K):
            o, h, l, c = O[k, i], H[k, i], L[k, i], C[k, i]
            if pend[k] and not pos[k] and not np.isnan(o):
                pos[k], ep[k], sl[k], tp[k], eb[k] = 1, o, pSl[k], o + pTp[k], i
            pend[k] = 0
            ex = False
            if pos[k] and not np.isnan(c):
                if l <= sl[k]:
                    ex, xp = True, min(o, sl[k])
                elif h >= tp[k]:
                    ex, xp = True, max(o, tp[k])
                elif i - eb[k] >= hold:
                    ex, xp = True, c
            was = pos[k] == 1
            if ex:
                out.append((idx[eb[k]], k, (xp / ep[k] - 1) * 100 - cost))
                pos[k] = 0
            if S[k, i] and not pos[k] and not ex and not was and pos.sum() + pend.sum() < max_open:
                pend[k], pSl[k], pTp[k] = 1, c - slA * A[k, i], tpA * A[k, i]
    return pd.DataFrame(out, columns=["entry", "coin", "pct"]).sort_values("entry")


if __name__ == "__main__":
    mode = sys.argv[1] if len(sys.argv) > 1 else "Active"
    max_open = int(sys.argv[2]) if len(sys.argv) > 2 else 5
    frames = [coin_arrays(klines_5m(s), *MODES[mode]) for s in COINS]
    T = replay(frames, max_open)
    T["coin"] = [COINS[k] for k in T.coin]
    daily = T.groupby(T.entry.dt.floor("D")).pct.sum() / len(COINS)
    eq = daily.cumsum()
    recent = T[T.entry >= "2025-01-01"]
    weeks = (T.entry.max() - pd.Timestamp("2025-01-01")).days / 7
    print(f"{mode} mode, max {max_open} open, {len(COINS)} coins")
    print(f"trades {len(T)} | won {100 * (T.pct > 0).mean():.1f}% | avg {T.pct.mean():+.3f}% | 2025-26: {len(recent) / weeks:.1f} a week, avg {recent.pct.mean():+.3f}%")
    print(f"basket (1/{len(COINS)} of equity per trade): total {eq.iloc[-1]:+.1f}% | max DD {(eq.cummax() - eq).max():.1f}% | worst day {daily.min():.1f}%")
    T["year"] = T.entry.dt.year
    print(T.groupby("year").pct.agg(trades="size", won=lambda x: round(100 * (x > 0).mean(), 1), avg_pct=lambda x: round(x.mean(), 3)).T.to_string())
    print(T.groupby("coin").pct.agg(trades="size", won=lambda x: round(100 * (x > 0).mean(), 1), avg_pct=lambda x: round(x.mean(), 3)).T.to_string())
