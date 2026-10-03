import numpy as np, pandas as pd, pickle
from lab import rmin, rmax, SPLIT
from revdots import ema
data = pickle.load(open("cdata.pkl", "rb"))
COST = 0.0015  # per side: 0.10% fee + 0.05% slippage

def buy_sig(x, wave=-53, rsi_=40, stretch=2.0, confirm=3, rearm=True, cool=10, btc=None):
    f = x["f"]; d = x["d"]; o, h, l, c = d.o.to_numpy(), d.h.to_numpy(), d.l.to_numpy(), d.c.to_numpy()
    w2 = f.w2.to_numpy(); r = f.rsi.to_numpy(); d50 = f.d50.to_numpy(); up = f.up.to_numpy()
    rng = h - l; clv = np.where(rng > 0, (c - l) / np.where(rng > 0, rng, 1), 0.0)
    setup = up & (rmin(w2, 3) <= wave) & (rmin(r, 5) <= rsi_) & (rmin(d50, 10) <= -stretch)
    if btc is not None:
        kind, lvl = btc
        if kind == "rsi": setup &= rmin(f.btc_rsi.to_numpy(), 10) <= lvl
        if kind == "wave": setup &= rmin(f.btc_w2.to_numpy(), 10) <= lvl
    n = len(c); cand = np.zeros(n, bool); ls = -99
    for i in range(1, n):
        if setup[i]: ls = i
        if i - ls <= confirm and c[i] > o[i] and c[i] > c[i - 1] and clv[i] >= 0.5: cand[i] = True; ls = -99
    sig = np.zeros(n, bool); last = -10**9; lastlow = np.inf
    for i in np.flatnonzero(cand):
        lw = l[max(0, i - 4):i + 1].min()
        if i - last > cool or (rearm and lw < lastlow): sig[i] = True; last = i; lastlow = lw
    return sig

def tp_sig(x, wave=53, rsi_=70, look=15, ema_len=20, vol=None, cool=10):
    f = x["f"]; c = x["d"].c.to_numpy()
    e = ema(c, ema_len); below = c < e; xd = below & ~np.r_[False, below[:-1]]
    cond = xd & (rmax(f.w2.to_numpy(), look) >= wave) & (rmax(f.rsi.to_numpy(), look) >= rsi_)
    if vol is not None: cond &= rmax(np.nan_to_num(f.volz.to_numpy(), nan=0), look) >= vol
    out = np.zeros(len(c), bool); last = -10**9
    for i in np.flatnonzero(cond):
        if i - last > cool: out[i] = True; last = i
    return out

def backtest(x, entry, exitsig, trail=None, fail=None, hard=None, start=200):
    d = x["d"]; o, h, l, c = d.o.to_numpy(), d.h.to_numpy(), d.l.to_numpy(), d.c.to_numpy()
    a = x["f"].atr.to_numpy(); n = len(c); tr = []; pos = None
    for i in range(start, n - 1):
        if pos is not None:
            ei, ep, fl, hs, best = pos
            best = max(best, c[i]); pos = (ei, ep, fl, hs, best)
            stop = -np.inf
            if trail is not None: stop = max(stop, best - trail * a[i])
            if hs is not None: stop = max(stop, hs)
            if l[i] <= stop and i > ei:     # intrabar stop (trailing / hard)
                px = min(o[i], stop); tr.append((d.index[ei], px / ep - 1 - 2 * COST, i - ei)); pos = None; continue
            if exitsig[i] or (fl is not None and c[i] < fl):
                tr.append((d.index[ei], o[i + 1] / ep - 1 - 2 * COST, i + 1 - ei)); pos = None
        if pos is None and entry[i]:
            ep = o[i + 1]
            fl = (l[max(0, i - 4):i + 1].min() - fail * a[i]) if fail is not None else None
            hs = (ep - hard * a[i]) if hard is not None else None
            pos = (i + 1, ep, fl, hs, ep)
    if pos is not None:
        tr.append((d.index[pos[0]], c[-1] / pos[1] - 1 - 2 * COST, n - 1 - pos[0]))
    return tr

def evaluate(bkw={}, tkw={}, bt={}, coins=None, alts_btc=None):
    rows = []
    for cn, x in data.items():
        if coins and cn not in coins: continue
        kw = dict(bkw)
        if alts_btc and cn != "BTC": kw["btc"] = alts_btc
        b = buy_sig(x, **kw); t = tp_sig(x, **tkw)
        for e, r, hb in backtest(x, b, t, **bt): rows.append((cn, e, r, hb))
    T = pd.DataFrame(rows, columns=["coin", "date", "ret", "bars"])
    out = {}
    for per, m in [("IS", T.date < SPLIT), ("OOS", T.date >= SPLIT)]:
        g = T[m]
        if len(g) == 0: continue
        w = g.ret[g.ret > 0].sum(); L = -g.ret[g.ret < 0].sum()
        out.update({f"{per}_n": len(g), f"{per}_win": round((g.ret > 0).mean(), 2), f"{per}_avg%": round(g.ret.mean() * 100, 1),
                    f"{per}_med%": round(g.ret.median() * 100, 1), f"{per}_p10%": round(g.ret.quantile(.1) * 100, 1),
                    f"{per}_worst%": round(g.ret.min() * 100, 1), f"{per}_pf": round(w / L, 2) if L else np.inf,
                    f"{per}_hold": int(g.bars.median())})
    return out, T
