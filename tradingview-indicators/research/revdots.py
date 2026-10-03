"""Python port of reversal-dots-strategy.pine (Pine semantics for ema/sma/rsi/stoch)."""
import numpy as np, pandas as pd

def sma(x, n):
    return pd.Series(x).rolling(n, min_periods=n).mean().to_numpy()

def ema(x, n):
    x = np.asarray(x, float); out = np.full(len(x), np.nan); a = 2 / (n + 1)
    s = sma(x, n)
    for i in range(len(x)):
        prev = out[i-1] if i else np.nan
        if np.isnan(prev):
            out[i] = s[i]
        else:
            out[i] = a * x[i] + (1 - a) * prev if not np.isnan(x[i]) else prev
    return out

def rma(x, n):
    x = np.asarray(x, float); out = np.full(len(x), np.nan); a = 1 / n
    s = sma(x, n)
    for i in range(len(x)):
        prev = out[i-1] if i else np.nan
        out[i] = s[i] if np.isnan(prev) else a * x[i] + (1 - a) * prev
    return out

def rsi(x, n):
    x = np.asarray(x, float); ch = np.diff(x, prepend=np.nan)
    up = rma(np.where(np.isnan(ch), np.nan, np.maximum(ch, 0)), n)
    dn = rma(np.where(np.isnan(ch), np.nan, -np.minimum(ch, 0)), n)
    with np.errstate(all="ignore"):
        r = np.where(dn == 0, 100, np.where(up == 0, 0, 100 - 100 / (1 + up / dn)))
    return np.where(np.isnan(up) | np.isnan(dn), np.nan, r)

def stoch(x, n):
    s = pd.Series(x); lo = s.rolling(n, min_periods=n).min(); hi = s.rolling(n, min_periods=n).max()
    with np.errstate(all="ignore"):
        return (100 * (s - lo) / (hi - lo)).replace([np.inf, -np.inf], np.nan).to_numpy()

def waves(df, ch=9, avg=12, ma=3):
    src = ((df.h + df.l + df.c) / 3).to_numpy()
    esa = ema(src, ch); de = ema(np.abs(src - esa), ch)
    with np.errstate(all="ignore"):
        ci = np.where(de == 0, 0.0, (src - esa) / (0.015 * de))
    ci = np.where(np.isnan(de), np.nan, ci)
    w1 = ema(ci, avg); w2 = sma(w1, ma)
    return w1, w2

def cross_over(a, b):
    a1 = np.roll(a, 1); b1 = np.roll(b, 1); r = (a > b) & (a1 <= b1); r[0] = False
    return r & ~np.isnan(a1) & ~np.isnan(b1)

def resample(daily, rule):
    d = daily.copy()
    g = d.resample(rule, label="left", closed="left")
    return pd.DataFrame({"o": g.o.first(), "h": g.h.max(), "l": g.l.min(), "c": g.c.last()}).dropna()

def signals(df, os=-53.0, ob=53.0, exit_level=99.0, div_bot=-40.0, div_look=60, strong_bars=6):
    w1, w2 = waves(df)
    up = cross_over(w1, w2); dn = cross_over(w2, w1)
    big_buy = up & (w2 <= os); big_sell = dn & (w2 >= ob)
    # early warning
    early = np.zeros(len(df), bool); done = False
    for i in range(2, len(df)):
        if up[i] or dn[i]: done = False
        e = (not done) and w1[i] > w1[i-1] and w1[i-1] <= w1[i-2] and w1[i] < w2[i] and w2[i] <= os
        if e: early[i] = True; done = True
    k = sma(stoch(rsi(np.log(df.c.to_numpy()), 14), 14), 3)
    k1 = np.roll(k, 1); kexit = (k >= exit_level) & (k1 < exit_level); kexit[0] = False
    # bullish divergence + strong buy
    lo = df.l.to_numpy(); bull = np.zeros(len(df), bool)
    pw = pp = pb = None
    for i in range(4, len(df)):
        if w2[i-4] > w2[i-2] and w2[i-3] > w2[i-2] and w2[i-2] < w2[i-1] and w2[i-2] < w2[i] and w2[i-2] <= div_bot:
            piv = i - 2
            if pw is not None and piv - pb <= div_look and w2[i-2] > pw and lo[i-2] < pp: bull[i] = True
            pw, pp, pb = w2[i-2], lo[i-2], piv
    strong = np.zeros(len(df), bool); lbb = lbd = lsb = None
    for i in range(len(df)):
        if big_buy[i]: lbb = i
        if bull[i]: lbd = i
        if (big_buy[i] or bull[i]) and lbb is not None and lbd is not None and abs(lbb - lbd) <= strong_bars and lbb != lsb:
            strong[i] = True; lsb = lbb
    return dict(w1=w1, w2=w2, up=up, dn=dn, big_buy=big_buy, big_sell=big_sell, early=early, kexit=kexit, strong=strong)

def htf_bull_on(df, htf, buy_max=0.0):
    """request.security(htf, [w1[1], w2[1], w1[2]], lookahead_on) mapped onto df bars."""
    w1, w2 = waves(htf)
    h = pd.DataFrame({"w1": pd.Series(w1).shift(1).to_numpy(), "w2": pd.Series(w2).shift(1).to_numpy(),
                      "w1p": pd.Series(w1).shift(2).to_numpy()}, index=htf.index)
    m = h.reindex(df.index, method="ffill")
    ready = m.notna().all(axis=1).to_numpy()
    bull = ready & (m.w1 > m.w1p).to_numpy() & (m.w2 <= buy_max).to_numpy()
    return ready, bull

def backtest(df, sig, entry="Big buy", exit_="Stoch line or any red dot", use_htf=True, htf=None, start=None, comm=0.001):
    ent = {"Any green dot": sig["up"], "Early warning": sig["early"], "Strong buy only": sig["strong"]}.get(entry, sig["big_buy"])
    ex = {"Stoch line or big sell": sig["kexit"] | sig["big_sell"], "Any red dot": sig["dn"],
          "Stoch line only": sig["kexit"]}.get(exit_, sig["kexit"] | sig["dn"])
    if use_htf:
        ready, bull = htf
        ok = ~ready | bull
    else:
        ok = np.ones(len(df), bool)
    inr = np.ones(len(df), bool) if start is None else (df.index >= pd.Timestamp(start)).to_numpy()
    o = df.o.to_numpy(); trades = []; pos = None
    for i in range(len(df) - 1):
        if pos is None and ent[i] and ok[i] and inr[i]:
            pos = (i + 1, o[i + 1])
        elif pos is not None and ex[i] and i >= pos[0]:
            trades.append((df.index[pos[0]], pos[1], df.index[i + 1], o[i + 1]))
            pos = None
    open_tr = None
    if pos is not None:
        open_tr = (df.index[pos[0]], pos[1], df.index[-1], df.c.iloc[-1])
    return trades, open_tr

def summarize(trades, open_tr, comm=0.001):
    allt = trades + ([open_tr] if open_tr else [])
    rets = [(x / e) * (1 - comm) ** 2 - 1 for _, e, _, x in allt]
    eq = float(np.prod([1 + r for r in rets])) if rets else 1.0
    wins = sum(r > 0 for r in rets[:len(trades)])
    return dict(n=len(trades), open=bool(open_tr), win=(wins / len(trades) if trades else float("nan")),
                avg=(np.mean(rets) if rets else float("nan")), total=eq - 1)
