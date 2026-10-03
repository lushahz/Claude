from engine import *
import multiprocessing as mp
btc = data["BTC"]; bc = btc["d"].c.to_numpy()
be50 = ema(bc, 50); be200 = ema(bc, 200)
hi365 = pd.Series(btc["d"].h.to_numpy()).rolling(365, min_periods=100).max().to_numpy()
ctx = pd.DataFrame({"golden": be50 > be200, "e200_up": be200 > np.r_[np.full(20, np.nan), be200[:-20]],
                    "dd": bc / hi365 - 1, "deathx": (be50 < be200) & np.r_[False, (be50 >= be200)[:-1]]}, index=btc["d"].index)
def bctx(x, col):
    return ctx[col].reindex(x["d"].index).ffill().fillna(False if col != "dd" else 0).to_numpy()

def backtest2(x, entry, exitsig, timestop=None, ts_min=0.0, extra_exit=None, start=200):
    d = x["d"]; o, c = d.o.to_numpy(), d.c.to_numpy(); n = len(c); tr = []; pos = None
    for i in range(start, n - 1):
        if pos is not None:
            ei, ep = pos
            dead = timestop is not None and i - ei >= timestop and c[i] / ep - 1 < ts_min
            if exitsig[i] or dead or (extra_exit is not None and extra_exit[i]):
                tr.append((d.index[ei], o[i + 1] / ep - 1 - 2 * COST, i + 1 - ei)); pos = None
        if pos is None and entry[i]: pos = (i + 1, o[i + 1])
    if pos is not None: tr.append((d.index[pos[0]], c[-1] / pos[1] - 1 - 2 * COST, n - 1 - pos[0]))
    return tr

def run(name, regime=None, timestop=None, ts_min=0.0, deathx_exit=False, dd_band=None):
    rows = []
    for cn, x in data.items():
        b = buy_sig(x, btc=None if cn == "BTC" else ("rsi", 40)); t = tp_sig(x)
        if regime: b &= bctx(x, regime).astype(bool)
        if dd_band is not None:
            dd = bctx(x, "dd"); lo, hi = dd_band; b &= ~((dd <= -lo) & (dd > -hi))   # skip "first leg down" zone
        ex = bctx(x, "deathx").astype(bool) if deathx_exit else None
        for e, r, hb in backtest2(x, b, t, timestop, ts_min, ex): rows.append((cn, e, r, hb))
    T = pd.DataFrame(rows, columns=["coin", "date", "ret", "bars"]); out = {"variant": name}
    for per, m in [("IS", T.date < SPLIT), ("OOS", T.date >= SPLIT)]:
        g = T[m]; w = g.ret[g.ret > 0].sum(); L = -g.ret[g.ret < 0].sum()
        out.update({f"{per}_n": len(g), f"{per}_win": round((g.ret > 0).mean(), 2), f"{per}_avg%": round(g.ret.mean() * 100, 1),
                    f"{per}_p10%": round(g.ret.quantile(.1) * 100, 1), f"{per}_worst%": round(g.ret.min() * 100, 1),
                    f"{per}_pf": round(w / L, 2) if L else np.inf, f"{per}_hold": int(g.bars.median())})
    return out
V = [("C baseline", {}),
     ("BTC golden cross regime", dict(regime="golden")),
     ("BTC 200 EMA rising", dict(regime="e200_up")),
     ("skip BTC drawdown 20-60% zone", dict(dd_band=(0.20, 0.60))),
     ("skip BTC drawdown 25-55% zone", dict(dd_band=(0.25, 0.55))),
     ("exit on BTC death cross", dict(deathx_exit=True)),
     ("time stop: 60 bars & still losing", dict(timestop=60)),
     ("time stop: 90 bars & still losing", dict(timestop=90)),
     ("time stop: 120 bars & still losing", dict(timestop=120)),
     ("time stop 90 + exit on BTC death cross", dict(timestop=90, deathx_exit=True)),
     ("skip dd 20-60% + time stop 90", dict(dd_band=(0.20, 0.60), timestop=90)),
     ("skip dd 20-60% + BTC death-cross exit", dict(dd_band=(0.20, 0.60), deathx_exit=True)),
]
def job(v): return run(v[0], **v[1])
if __name__ == "__main__":
    with mp.Pool(4) as p: rows = p.map(job, V)
    R = pd.DataFrame(rows).set_index("variant"); pd.set_option("display.width", 300); pd.set_option("display.max_columns", 30)
    print(R[[c for c in R.columns if c.startswith("IS")]].to_string()); print()
    print(R[[c for c in R.columns if c.startswith("OOS")]].to_string())
