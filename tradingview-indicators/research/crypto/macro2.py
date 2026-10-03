from macrotest import *
def xabove(a, b):
    ab = a > b; return ab & ~np.r_[False, ab[:-1]]
BDF = lambda m, c, x: (A(m.btcd) < A(m.btcd_e20)) | (c == "BTC")
V2 = {
 "C baseline": {},
 "BTC guard": dict(guard=BTCG, exitf=BTCX),
 "BTC guard + alts BTC.D < 20 EMA": dict(guard=BTCG, exitf=BTCX, buyf=BDF),
 "BTC guard + alts BTC.D RSI<=60": dict(guard=BTCG, exitf=BTCX, buyf=lambda m, c, x: (A(m.btcd_rsi) <= 60) | (c == "BTC")),
 "BTC skip-zone + exit when USDT.D crosses above its 200 EMA": dict(guard=BTCG, exitf=lambda m, x: xabove(A(m.usdtd), A(m.usdtd_e200))),
 "BTC skip-zone + exit when USDT.D 50 EMA crosses above 200 EMA": dict(guard=BTCG, exitf=lambda m, x: xabove(A(m.usdtd_e50), A(m.usdtd_e200))),
 "BTC skip-zone + exit when TOTAL death cross": dict(guard=BTCG, exitf=lambda m, x: m.total_deathx.fillna(False).to_numpy().astype(bool)),
 "BTC guard + exit also on USDT.D 50/200 cross up": dict(guard=BTCG, exitf=lambda m, x: BTCX(m, x) | xabove(A(m.usdtd_e50), A(m.usdtd_e200))),
 "BTC guard + alts BTC.D<20EMA + USDT.D 50/200 exit": dict(guard=BTCG, buyf=BDF, exitf=lambda m, x: BTCX(m, x) | xabove(A(m.usdtd_e50), A(m.usdtd_e200))),
}
def job2(k): return run(k, **V2[k])
if __name__ == "__main__":
    with mp.Pool(4) as p: rows = p.map(job2, list(V2))
    R = pd.DataFrame(rows).set_index("variant"); pd.set_option("display.width", 300); pd.set_option("display.max_columns", 30)
    print(R[[c for c in R.columns if c.startswith("IS")]].to_string()); print()
    print(R[[c for c in R.columns if c.startswith("OOS")]].to_string())
