from engine2 import *
def each_signal(x, entry, exitsig, extra_exit=None, start=200):
    """Every signal is its own trade: next open -> first exit signal after it."""
    d = x["d"]; o, c = d.o.to_numpy(), d.c.to_numpy(); n = len(c)
    ex = exitsig.copy()
    if extra_exit is not None: ex |= extra_exit
    nxt = np.full(n + 1, -1); j = -1
    for i in range(n - 1, -1, -1):
        if ex[i]: j = i
        nxt[i] = j
    out = []
    for i in np.flatnonzero(entry):
        if i < start or i + 1 >= n: continue
        k = nxt[i + 1] if i + 1 < n else -1
        if k == -1 or k + 1 >= n: r = c[-1] / o[i + 1] - 1; hb = n - 1 - (i + 1)
        else: r = o[k + 1] / o[i + 1] - 1; hb = k + 1 - (i + 1)
        out.append((d.index[i], r - 2 * COST, hb))
    return out
def run_ps(cfg):
    rows = []
    for cn, x in data.items():
        m = attach(x); A = lambda s: np.nan_to_num(s.to_numpy(), nan=0.0)
        rv = reversal(x, cn, cfg["wave"], cfg["rsi"], cfg["stretch"])
        if cfg["btcd"] and cn != "BTC": rv &= A(m.btcd) < A(m.btcd_e20)
        if cfg["guard"]:
            dd = bctx(x, "dd"); rv &= ~((dd <= -0.25) & (dd > -0.60))
        ent = rv
        if cfg["pullback"]: ent = ent | pullback(x, cn, cfg["pb_wave"], cfg["pb_rsi"])
        extra = bctx(x, "deathx").astype(bool) if cfg["cycle_exit"] else None
        for e, r, hb in each_signal(x, ent, take_profit(x, "std"), extra): rows.append((cn, e, r, hb))
    T = pd.DataFrame(rows, columns=["coin", "date", "ret", "bars"]); out = dict(cfg)
    yrs_is = sum(len(x["d"].index[200:][x["d"].index[200:] < SPLIT]) / 365 for x in data.values())
    yrs_oos = sum(len(x["d"].index[200:][x["d"].index[200:] >= SPLIT]) / 365 for x in data.values())
    for per, msk, yy in [("IS", T.date < SPLIT, yrs_is), ("OOS", T.date >= SPLIT, yrs_oos)]:
        g = T[msk]; w = g.ret[g.ret > 0].sum(); L = -g.ret[g.ret < 0].sum()
        out.update({f"{per}_sig_yr": round(len(g) / yy, 2), f"{per}_win": round((g.ret > 0).mean(), 2), f"{per}_avg%": round(g.ret.mean() * 100, 1),
                    f"{per}_p10%": round(g.ret.quantile(.1) * 100, 1), f"{per}_worst%": round(g.ret.min() * 100, 1), f"{per}_pf": round(w / L, 2) if L else np.inf})
    return out
BASE = dict(wave=-53, rsi=40, stretch=2.0, btcd=True, guard=True, cycle_exit=True, pullback=False, pb_wave=-30, pb_rsi=45)
CFGS = []
def v(name, **k): c = dict(BASE); c.update(k); c["name"] = name; CFGS.append(c)
v("current crypto rules")
v("guard off", guard=False)
v("looser reversal (-45/45/1.5)", wave=-45, rsi=45, stretch=1.5)
v("looser reversal, guard off", wave=-45, rsi=45, stretch=1.5, guard=False)
v("looser reversal + pullbacks", wave=-45, rsi=45, stretch=1.5, pullback=True)
v("current + pullbacks", pullback=True)
v("current + pullbacks (-20/50)", pullback=True, pb_wave=-20, pb_rsi=50)
v("looser rev + pullbacks (-20/50)", wave=-45, rsi=45, stretch=1.5, pullback=True, pb_wave=-20, pb_rsi=50)
v("looser rev + pullbacks, no BTC.D filter", wave=-45, rsi=45, stretch=1.5, pullback=True, btcd=False)
v("looser rev + pullbacks (-20/50), no BTC.D", wave=-45, rsi=45, stretch=1.5, pullback=True, pb_wave=-20, pb_rsi=50, btcd=False)
if __name__ == "__main__":
    with mp.Pool(4) as p: rows = p.map(run_ps, CFGS)
    R = pd.DataFrame(rows).set_index("name"); pd.set_option("display.width", 320)
    print(R[[c for c in R.columns if c.startswith(("IS_", "OOS_"))]].to_string())
