from evaluate import *
from common import ema
import multiprocessing as mp
COMM = {"crypto": 0.001, "forex": 0.0002, "stocks": 0.0005, "cfd_index": 0.0003, "cfd_commodity": 0.0005, "exchanges": 0.0005}

def signals_for(x, stretch=2.0, wave=-53, rsi_=35):
    f = x["f"]; d = x["d"]; c = d.c.to_numpy()
    p = {"wave": wave, "rsi": rsi_, "rsi_look": 5, "stretch": stretch, "div": False, "candle": True, "cool": 10}
    buy = build(x, +1, p)
    w2 = f.w2.to_numpy(); r = f.rsi.to_numpy(); e20 = ema(c, 20)
    below20 = c < e20; x20 = below20 & ~np.r_[False, below20[:-1]]
    tp = cooldown(x20 & (rmax(w2, 15) >= 53) & (rmax(r, 15) >= 70), 10)
    big_buy = f.up.to_numpy() & (w2 <= -53)
    big_sell = f.dn.to_numpy() & (w2 >= 53)
    k = f.k.to_numpy(); kx = (k >= 99) & (np.r_[0, k[:-1]] < 99)
    return buy, tp, big_buy, big_sell, kx

def backtest(x, entry, exitsig, stop_mode=None, maxhold=None):
    d = x["d"]; o, h, l, c = d.o.to_numpy(), d.h.to_numpy(), d.l.to_numpy(), d.c.to_numpy()
    a = x["f"].atr.to_numpy(); n = len(d); comm = COMM[x["cls"]]
    tr = []; pos = None
    for i in range(250, n - 1):
        if pos is not None:
            ei, ep, sp = pos
            if sp is not None and l[i] <= sp and i >= ei:
                px = min(o[i], sp) if o[i] < sp else sp
                tr.append((d.index[ei], px / ep - 1 - 2 * comm, i - ei, "stop")); pos = None; continue
            if exitsig[i] or (maxhold and i - ei >= maxhold):
                tr.append((d.index[ei], o[i + 1] / ep - 1 - 2 * comm, i + 1 - ei, "exit")); pos = None
        if pos is None and entry[i]:
            ep = o[i + 1]
            sp = None
            if stop_mode == "swing": sp = min(l[max(0, i - 4):i + 1]) - 0.5 * a[i]
            if stop_mode == "3atr": sp = ep - 3 * a[i]
            pos = (i + 1, ep, sp)
    if pos is not None:
        ei, ep, _ = pos; tr.append((d.index[ei], c[-1] / ep - 1 - 2 * comm, n - 1 - ei, "open"))
    return tr

CONFIGS = {
 "OLD: big buy -> Stoch line or big sell": lambda s: (s[2], s[4] | s[3], None, None),
 "NEW entry -> Stoch line or big sell": lambda s: (s[0], s[4] | s[3], None, None),
 "NEW entry -> take-profit trigger": lambda s: (s[0], s[1], None, None),
 "NEW entry -> take-profit trigger or big sell": lambda s: (s[0], s[1] | s[3], None, None),
 "NEW entry -> TP trigger or big sell, swing stop": lambda s: (s[0], s[1] | s[3], "swing", None),
 "NEW entry -> TP trigger or big sell, 3 ATR stop": lambda s: (s[0], s[1] | s[3], "3atr", None),
}
def job(name):
    rows = []
    for sym, x in data.items():
        s = signals_for(x)
        en, ex, st, mh = CONFIGS[name](s)
        for t in backtest(x, en, ex, st, mh):
            rows.append((name, x["cls"], sym) + t)
    return rows
if __name__ == "__main__":
    with mp.Pool(4) as p: out = sum(p.map(job, list(CONFIGS)), [])
    T = pd.DataFrame(out, columns=["cfg", "cls", "sym", "date", "ret", "bars", "how"])
    T["period"] = np.where(T.date < SPLIT, "2010-18", "2019-26")
    T.to_pickle("trades.pkl")
    def agg(g):
        w = g.ret[g.ret > 0].sum(); L = -g.ret[g.ret < 0].sum()
        return pd.Series(dict(trades=len(g), win=(g.ret > 0).mean(), avg=g.ret.mean() * 100, med=g.ret.median() * 100,
                              pf=w / L if L else np.inf, hold=g.bars.median()))
    pd.set_option("display.width", 250)
    print(T.groupby(["cfg", "period"]).apply(agg).round(2).to_string())
