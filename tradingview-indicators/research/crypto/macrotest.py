from engine import *
from regime import backtest2, bctx
from macro import attach, rmin, rmax
import multiprocessing as mp
def run(name, buyf=None, tpf=None, guard=None, exitf=None):
    rows = []
    for cn, x in data.items():
        m = attach(x)
        b = buy_sig(x, btc=None if cn == "BTC" else ("rsi", 40)); t = tp_sig(x)
        if buyf: b &= buyf(m, cn, x)
        if tpf: t = tpf(m, t, x)
        if guard: b &= guard(m, x)
        ex = exitf(m, x) if exitf else None
        for e, r, hb in backtest2(x, b, t, None, 0, ex): rows.append((cn, e, r, hb))
    T = pd.DataFrame(rows, columns=["coin", "date", "ret", "bars"]); out = {"variant": name}
    for per, msk in [("IS", T.date < SPLIT), ("OOS", T.date >= SPLIT)]:
        gg = T[msk]; w = gg.ret[gg.ret > 0].sum(); L = -gg.ret[gg.ret < 0].sum()
        out.update({f"{per}_n": len(gg), f"{per}_win": round((gg.ret > 0).mean(), 2), f"{per}_avg%": round(gg.ret.mean() * 100, 1),
                    f"{per}_p10%": round(gg.ret.quantile(.1) * 100, 1), f"{per}_worst%": round(gg.ret.min() * 100, 1),
                    f"{per}_pf": round(w / L, 2) if L else np.inf})
    return out
A = lambda s: np.nan_to_num(s.to_numpy(), nan=0.0)
BTCG = lambda m, x: ~((bctx(x, "dd") <= -0.25) & (bctx(x, "dd") > -0.60))
BTCX = lambda m, x: bctx(x, "deathx").astype(bool)
V = {
 "C baseline": {},
 "USDT.D RSI>=65 in last 10d (fear spike)": dict(buyf=lambda m, c, x: rmax(A(m.usdtd_rsi), 10) >= 65),
 "USDT.D RSI>=70 in last 10d": dict(buyf=lambda m, c, x: rmax(A(m.usdtd_rsi), 10) >= 70),
 "USDT.D above its 50 EMA (risk-off)": dict(buyf=lambda m, c, x: A(m.usdtd) > A(m.usdtd_e50)),
 "USDT.D turning down (below 3 days ago)": dict(buyf=lambda m, c, x: A(m.usdtd) < np.r_[np.zeros(3), A(m.usdtd)[:-3]]),
 "TOTAL RSI<=35 in last 10d": dict(buyf=lambda m, c, x: rmin(np.where(np.isnan(m.total_rsi), 99, m.total_rsi), 10) <= 35),
 "Alts: BTC.D below its 20 EMA": dict(buyf=lambda m, c, x: (A(m.btcd) < A(m.btcd_e20)) | (c == "BTC")),
 "Alts: BTC.D RSI<=60": dict(buyf=lambda m, c, x: (A(m.btcd_rsi) <= 60) | (c == "BTC")),
 "Guard: BTC skip dd 25-60% + BTC death-cross exit": dict(guard=BTCG, exitf=BTCX),
 "Guard: TOTAL skip dd 25-60% + TOTAL death-cross exit": dict(guard=lambda m, x: ~((A(m.total_dd) <= -0.25) & (A(m.total_dd) > -0.60)), exitf=lambda m, x: m.total_deathx.fillna(False).to_numpy().astype(bool)),
 "TP also on USDT.D greed (RSI<=30 in 15d) + close<EMA20": dict(tpf=lambda m, t, x: t | ((rmin(np.where(np.isnan(m.usdtd_rsi), 99, m.usdtd_rsi), 15) <= 30) & (x["d"].c.to_numpy() < ema(x["d"].c.to_numpy(), 20)) & ~np.r_[False, (x["d"].c.to_numpy() < ema(x["d"].c.to_numpy(), 20))[:-1]])),
 "USDT.D RSI>=65 + BTC guard": dict(buyf=lambda m, c, x: rmax(A(m.usdtd_rsi), 10) >= 65, guard=BTCG, exitf=BTCX),
 "USDT.D RSI>=65 + TOTAL guard": dict(buyf=lambda m, c, x: rmax(A(m.usdtd_rsi), 10) >= 65, guard=lambda m, x: ~((A(m.total_dd) <= -0.25) & (A(m.total_dd) > -0.60)), exitf=lambda m, x: m.total_deathx.fillna(False).to_numpy().astype(bool)),
}
def job(k): return run(k, **V[k])
if __name__ == "__main__":
    with mp.Pool(4) as p: rows = p.map(job, list(V))
    R = pd.DataFrame(rows).set_index("variant"); pd.set_option("display.width", 300); pd.set_option("display.max_columns", 30)
    print(R[[c for c in R.columns if c.startswith("IS")]].to_string()); print()
    print(R[[c for c in R.columns if c.startswith("OOS")]].to_string())
