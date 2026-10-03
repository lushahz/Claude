from persignal import *
def each_signal2(x, entry, exitsig, extra_exit=None, fail_atr=None, trend_exit=False, start=200):
    d = x["d"]; o, l, c = d.o.to_numpy(), d.l.to_numpy(), d.c.to_numpy(); a = x["f"].atr.to_numpy(); e200 = x["f"].e200.to_numpy(); n = len(c)
    ex = exitsig.copy()
    if extra_exit is not None: ex |= extra_exit
    out = []
    for i in np.flatnonzero(entry):
        if i < start or i + 1 >= n: continue
        fl = l[max(0, i - 4):i + 1].min() - fail_atr * a[i] if fail_atr is not None else -np.inf
        k = -1
        for j in range(i + 1, n):
            if ex[j] or c[j] < fl or (trend_exit and c[j] < e200[j]): k = j; break
        if k == -1 or k + 1 >= n: r = c[-1] / o[i + 1] - 1; hb = n - 1 - (i + 1)
        else: r = o[k + 1] / o[i + 1] - 1; hb = k + 1 - (i + 1)
        out.append((d.index[i], r - 2 * COST, hb))
    return out
def stat(T):
    yrs_is = sum(len(x["d"].index[200:][x["d"].index[200:] < SPLIT]) / 365 for x in data.values())
    yrs_oos = sum(len(x["d"].index[200:][x["d"].index[200:] >= SPLIT]) / 365 for x in data.values())
    out = {}
    for per, msk, yy in [("IS", T.date < SPLIT, yrs_is), ("OOS", T.date >= SPLIT, yrs_oos)]:
        g = T[msk]; w = g.ret[g.ret > 0].sum(); L = -g.ret[g.ret < 0].sum()
        out.update({f"{per}_sig_yr": round(len(g) / yy, 2), f"{per}_win": round((g.ret > 0).mean(), 2), f"{per}_avg%": round(g.ret.mean() * 100, 1),
                    f"{per}_p10%": round(g.ret.quantile(.1) * 100, 1), f"{per}_worst%": round(g.ret.min() * 100, 1), f"{per}_pf": round(w / L, 2) if L else np.inf,
                    f"{per}_hold": int(g.bars.median())})
    return out
def job(args):
    name, pbw, pbr, fail, trend, cyc = args; rows = []
    for cn, x in data.items():
        pb = pullback(x, cn, pbw, pbr)
        extra = bctx(x, "deathx").astype(bool) if cyc else None
        for e, r, hb in each_signal2(x, pb, take_profit(x, "std"), extra, fail, trend): rows.append((cn, e, r, hb))
    return {"variant": name, **stat(pd.DataFrame(rows, columns=["coin", "date", "ret", "bars"]))}
V = [("pullback (-20/50), TP + cycle exit", -20, 50, None, False, True),
     ("pullback (-20/50) + failed-dip exit 1 ATR", -20, 50, 1.0, False, True),
     ("pullback (-20/50) + exit on close below 200 EMA", -20, 50, None, True, True),
     ("pullback (-20/50) + both protective exits", -20, 50, 1.0, True, True),
     ("pullback (-30/45), TP + cycle exit", -30, 45, None, False, True),
     ("pullback (-30/45) + exit below 200 EMA", -30, 45, None, True, True)]
if __name__ == "__main__":
    with mp.Pool(4) as p: rows = p.map(job, V)
    R = pd.DataFrame(rows).set_index("variant"); pd.set_option("display.width", 320)
    print(R.to_string())
