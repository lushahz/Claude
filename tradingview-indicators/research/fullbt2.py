from fullbt import *
def backtest2(x, entry, exitsig, fail_atr=None):
    """Close-based 'failed reversal' exit: close below (signal swing low - fail_atr*ATR)."""
    d = x["d"]; o, h, l, c = d.o.to_numpy(), d.h.to_numpy(), d.l.to_numpy(), d.c.to_numpy()
    a = x["f"].atr.to_numpy(); n = len(d); comm = COMM[x["cls"]]
    tr = []; pos = None
    for i in range(250, n - 1):
        if pos is not None:
            ei, ep, fl = pos
            failed = fl is not None and c[i] < fl
            if exitsig[i] or failed:
                tr.append((d.index[ei], o[i + 1] / ep - 1 - 2 * comm, i + 1 - ei, "fail" if failed and not exitsig[i] else "exit")); pos = None
        if pos is None and entry[i]:
            fl = (min(l[max(0, i - 4):i + 1]) - fail_atr * a[i]) if fail_atr is not None else None
            pos = (i + 1, o[i + 1], fl)
    if pos is not None:
        ei, ep, _ = pos; tr.append((d.index[ei], c[-1] / ep - 1 - 2 * comm, n - 1 - ei, "open"))
    return tr
CF = {
 "TP trigger only (no protection)": (None, False),
 "TP trigger + failed-reversal exit (close < swing low)": (0.0, False),
 "TP trigger + failed-reversal exit (close < swing low - 1 ATR)": (1.0, False),
 "TP or big sell + failed-reversal exit (close < swing low - 1 ATR)": (1.0, True),
}
def job(name):
    fa, withbig = CF[name]; rows = []
    for sym, x in data.items():
        s = signals_for(x)
        ex = s[1] | s[3] if withbig else s[1]
        for t in backtest2(x, s[0], ex, fa): rows.append((name, x["cls"], sym) + t)
    return rows
if __name__ == "__main__":
    with mp.Pool(4) as p: out = sum(p.map(job, list(CF)), [])
    T = pd.DataFrame(out, columns=["cfg", "cls", "sym", "date", "ret", "bars", "how"])
    T["period"] = np.where(T.date < SPLIT, "2010-18", "2019-26")
    T.to_pickle("trades2.pkl")
    def agg(g):
        w = g.ret[g.ret > 0].sum(); L = -g.ret[g.ret < 0].sum()
        return pd.Series(dict(trades=len(g), win=(g.ret > 0).mean(), avg=g.ret.mean()*100, worst=g.ret.min()*100,
                              p10=g.ret.quantile(.1)*100, pf=w/L if L else np.inf, hold=g.bars.median(), maxhold=g.bars.max()))
    pd.set_option("display.width", 250)
    print(T.groupby(["cfg","period"]).apply(agg).round(2).to_string())
    best = "TP trigger + failed-reversal exit (close < swing low - 1 ATR)"
    print("\nBy asset class (", best, ")")
    print(T[T.cfg==best].groupby(["cls"]).apply(agg).round(2).to_string())
