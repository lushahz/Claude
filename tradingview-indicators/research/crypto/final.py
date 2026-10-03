from macrotest import *
BDF = lambda m, c, x: (A(m.btcd) < A(m.btcd_e20)) | (c == "BTC")
def final_signals(cn, x):
    m = attach(x)
    b = buy_sig(x, btc=None if cn == "BTC" else ("rsi", 40)) & BDF(m, cn, x) & BTCG(m, x)
    return b, tp_sig(x), BTCX(m, x)
def base_signals(cn, x):
    return buy_sig(x), tp_sig(x), None
def trades(fn):
    rows = []
    for cn, x in data.items():
        b, t, ex = fn(cn, x)
        for e, r, hb in backtest2(x, b, t, None, 0, ex): rows.append((cn, e, r, hb))
    return pd.DataFrame(rows, columns=["coin", "date", "ret", "bars"])
def agg(g):
    w = g.ret[g.ret > 0].sum(); L = -g.ret[g.ret < 0].sum()
    return pd.Series(dict(trades=len(g), win=(g.ret > 0).mean(), avg=g.ret.mean() * 100, med=g.ret.median() * 100,
                          p10=g.ret.quantile(.1) * 100, worst=g.ret.min() * 100, pf=w / L if L else np.inf, hold=g.bars.median()))
if __name__ == "__main__":
    pd.set_option("display.width", 250)
    out = {}
    for name, fn in [("General daily rules", base_signals), ("CRYPTO rules", final_signals)]:
        T = trades(fn); T["period"] = np.where(T.date < SPLIT, "2014-21", "2022-26"); T["kind"] = np.where(T.coin == "BTC", "BTC", "alts")
        print("=====", name); print(T.groupby("period").apply(agg).round(2).to_string()); print(T.groupby(["kind", "period"]).apply(agg).round(2).to_string())
        T["year"] = T.date.dt.year; print(T.groupby("year").apply(agg)[["trades", "win", "avg", "pf"]].round(2).T.to_string())
        out[name] = T
    # visible marks per coin-year
    yrs = sum((len(x["d"]) - 200) / 365 for x in data.values())
    print("CRYPTO trades per coin-year:", round(len(out["CRYPTO rules"]) / yrs, 2), " general:", round(len(out["General daily rules"]) / yrs, 2))
    for cn in ["BTC", "ETH", "SOL", "XRP", "LINK"]:
        x = data[cn]; d = x["d"]; b, t, ex = final_signals(cn, x); c = d.c.to_numpy()
        inT = False; ev = []
        for i in range(200, len(d)):
            if inT and (t[i] or ex[i]): ev.append((str(d.index[i].date()), "TAKE-PROFIT" if t[i] else "CYCLE EXIT", round(c[i], 4))); inT = False
            if not inT and b[i]: ev.append((str(d.index[i].date()), "BUY", round(c[i], 4))); inT = True
        print(cn, ev[-8:])
