import numpy as np, pandas as pd, pickle, itertools, multiprocessing as mp
from engine import data, COST, buy_sig, tp_sig
from lab import rmin, rmax, SPLIT
from regime import bctx
from macro import attach
from revdots import ema
YEARS = {c: (len(x["d"]) - 200) / 365 for c, x in data.items()}

def confirm_and_cool(x, setup, confirm=3, cool=10, rearm=True):
    d = x["d"]; o, h, l, c = d.o.to_numpy(), d.h.to_numpy(), d.l.to_numpy(), d.c.to_numpy()
    rng = h - l; clv = np.where(rng > 0, (c - l) / np.where(rng > 0, rng, 1), 0.0)
    n = len(c); cand = np.zeros(n, bool); ls = -99
    for i in range(1, n):
        if setup[i]: ls = i
        if i - ls <= confirm and c[i] > o[i] and c[i] > c[i - 1] and clv[i] >= 0.5: cand[i] = True; ls = -99
    sig = np.zeros(n, bool); last = -10**9; lastlow = np.inf
    for i in np.flatnonzero(cand):
        lw = l[max(0, i - 4):i + 1].min()
        if i - last > cool or (rearm and lw < lastlow): sig[i] = True; last = i; lastlow = lw
    return sig

def reversal(x, cn, wave=-53, rsi_=40, stretch=2.0, btc_rsi=40):
    f = x["f"]
    s = f.up.to_numpy() & (rmin(f.w2.to_numpy(), 3) <= wave) & (rmin(f.rsi.to_numpy(), 5) <= rsi_) & (rmin(f.d50.to_numpy(), 10) <= -stretch)
    if cn != "BTC" and btc_rsi is not None: s &= rmin(f.btc_rsi.to_numpy(), 10) <= btc_rsi
    return confirm_and_cool(x, s)

def pullback(x, cn, wave=-30, rsi_=45, need_btc_up=True):
    """Dip buy inside an uptrend: coin above its 200 EMA with 50>200, green dot from below zero after a mild dip."""
    f = x["f"]; c = x["d"].c.to_numpy()
    up = (c > f.e200.to_numpy()) & (f.e50.to_numpy() > f.e200.to_numpy())
    s = f.up.to_numpy() & up & (rmin(f.w2.to_numpy(), 3) <= wave) & (rmin(f.rsi.to_numpy(), 5) <= rsi_)
    if need_btc_up and cn != "BTC": s &= f.btc_above200.to_numpy() > 0
    return confirm_and_cool(x, s)

def take_profit(x, kind="std"):
    f = x["f"]; c = x["d"].c.to_numpy()
    if kind == "std": return tp_sig(x)
    if kind == "fast":   # overbought-lite then close below EMA10
        e = ema(c, 10); below = c < e; xd = below & ~np.r_[False, below[:-1]]
        return xd & (rmax(f.w2.to_numpy(), 10) >= 40) & (rmax(f.rsi.to_numpy(), 10) >= 62)
    if kind == "mid":
        e = ema(c, 20); below = c < e; xd = below & ~np.r_[False, below[:-1]]
        return xd & (rmax(f.w2.to_numpy(), 15) >= 45) & (rmax(f.rsi.to_numpy(), 15) >= 65)

def backtest(x, entry, exitsig, extra_exit=None, fail_exit=None, start=200):
    d = x["d"]; o, l, c = d.o.to_numpy(), d.l.to_numpy(), d.c.to_numpy(); a = x["f"].atr.to_numpy()
    n = len(c); tr = []; pos = None
    for i in range(start, n - 1):
        if pos is not None:
            ei, ep, fl = pos
            if exitsig[i] or (extra_exit is not None and extra_exit[i]) or (fl is not None and c[i] < fl):
                tr.append((d.index[ei], o[i + 1] / ep - 1 - 2 * COST, i + 1 - ei)); pos = None
        if pos is None and entry[i]:
            fl = (l[max(0, i - 4):i + 1].min() - fail_exit * a[i]) if fail_exit is not None else None
            pos = (i + 1, o[i + 1], fl)
    if pos is not None: tr.append((d.index[pos[0]], c[-1] / pos[1] - 1 - 2 * COST, n - 1 - pos[0]))
    return tr

def run(cfg):
    rows = []
    for cn, x in data.items():
        m = attach(x); A = lambda s: np.nan_to_num(s.to_numpy(), nan=0.0)
        rv = reversal(x, cn, cfg["wave"], cfg["rsi"], cfg["stretch"])
        if cfg["btcd"] and cn != "BTC": rv &= A(m.btcd) < A(m.btcd_e20)
        if cfg["guard"]:
            dd = bctx(x, "dd"); rv &= ~((dd <= -0.25) & (dd > -0.60))
        ent = rv
        if cfg["pullback"]: ent = ent | pullback(x, cn, cfg["pb_wave"], cfg["pb_rsi"])
        ex = take_profit(x, cfg["tp"])
        extra = bctx(x, "deathx").astype(bool) if cfg["cycle_exit"] else None
        for e, r, hb in backtest(x, ent, ex, extra, cfg.get("fail")): rows.append((cn, e, r, hb))
    T = pd.DataFrame(rows, columns=["coin", "date", "ret", "bars"]); out = dict(cfg)
    yrs_is = sum(min(len(x["d"].index[200:][x["d"].index[200:] < SPLIT]) / 365, 99) for x in data.values())
    yrs_oos = sum(len(x["d"].index[200:][x["d"].index[200:] >= SPLIT]) / 365 for x in data.values())
    for per, msk, yy in [("IS", T.date < SPLIT, yrs_is), ("OOS", T.date >= SPLIT, yrs_oos)]:
        g = T[msk]; w = g.ret[g.ret > 0].sum(); L = -g.ret[g.ret < 0].sum()
        out.update({f"{per}_per_yr": round(len(g) / yy, 2), f"{per}_win": round((g.ret > 0).mean(), 2), f"{per}_avg%": round(g.ret.mean() * 100, 1),
                    f"{per}_p10%": round(g.ret.quantile(.1) * 100, 1), f"{per}_worst%": round(g.ret.min() * 100, 1),
                    f"{per}_pf": round(w / L, 2) if L else np.inf, f"{per}_hold": int(g.bars.median()) if len(g) else 0})
    return out
