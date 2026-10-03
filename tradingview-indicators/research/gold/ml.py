"""Walk-forward gradient boosting on every gold feature (+ cross-asset). Labels = triple-barrier trade outcome
in R after costs, separately for long and short. Retrained each year on all prior years, tested on the next year only."""
import numpy as np, pandas as pd, sys, warnings, time; warnings.filterwarnings("ignore")
from numba import njit
from sklearn.ensemble import HistGradientBoostingRegressor
from glab import run, stats, session_mask, session_end_flags

STOP, TGT, MAXB, COST = 1.5, 2.0, 36, 0.30

@njit(cache=True)
def label(o, h, l, c, a, se, side, stop_k, tgt_k, max_bars, cost):
    n = len(c); out = np.full(n, np.nan)
    for i in range(n - 1):
        if not np.isfinite(a[i]) or a[i] <= 0: continue
        e = i + 1; ep = o[e]; risk = stop_k * a[i]; st = ep - side * risk; tg = ep + side * tgt_k * a[i]
        xp = np.nan; j = e
        while j < n:
            if side > 0:
                if l[j] <= st: xp = min(o[j], st); break
                if h[j] >= tg: xp = max(o[j], tg); break
            else:
                if h[j] >= st: xp = max(o[j], st); break
                if l[j] <= tg: xp = min(o[j], tg); break
            if j - e + 1 >= max_bars or se[j] or j == n - 1: xp = c[j]; break
            j += 1
        out[i] = (side * (xp - ep) - cost) / risk
    return out

if __name__ == "__main__":
    t0 = time.time()
    df = pd.read_pickle("bars/XAUUSD_5m.pkl"); f = pd.read_pickle("bars/XAUUSD_feat.pkl")
    try:
        X2 = pd.read_pickle("bars/XAUUSD_xfeat.pkl"); f = pd.concat([f, X2], axis=1); print("cross-asset cols:", list(X2.columns))
    except FileNotFoundError: print("no cross-asset features")
    o, h, l, c = (df[k].to_numpy() for k in "ohlc"); a = f.atr.to_numpy()
    se = session_end_flags(df.index); sess = session_mask(df.index)
    yL = label(o, h, l, c, a, se, 1.0, STOP, TGT, MAXB, COST)
    yS = label(o, h, l, c, a, se, -1.0, STOP, TGT, MAXB, COST)
    F = f.drop(columns=["atr", "tday"]).astype(float)
    F["cost_atr"] = COST / a                         # how big costs are vs. current volatility
    F["wt_up"] = F.wt_up.astype(float); F["wt_dn"] = F.wt_dn.astype(float)
    cols = list(F.columns); Xa = F.to_numpy(np.float32)
    yr = df.index.year.to_numpy()
    print(f"labels done {time.time()-t0:.0f}s; mean R long {np.nanmean(yL[sess]):.3f} short {np.nanmean(yS[sess]):.3f}")
    predL = np.full(len(c), np.nan); predS = np.full(len(c), np.nan); imp = []
    for Y in range(2013, 2027):
        tr = sess & (yr < Y) & np.isfinite(yL) & np.isfinite(yS); tr[::2] = False   # thin the overlapping samples
        te = sess & (yr == Y)
        for y, P in ((yL, predL), (yS, predS)):
            m = HistGradientBoostingRegressor(max_iter=300, learning_rate=0.05, max_leaf_nodes=31, min_samples_leaf=1000,
                                              l2_regularization=1.0, early_stopping=True, validation_fraction=0.15,
                                              n_iter_no_change=20, random_state=0)
            m.fit(Xa[tr], np.clip(y[tr], -1.5, 1.5))
            P[te] = m.predict(Xa[te])
        print(f"{Y}: trained on {tr.sum()} rows, {time.time()-t0:.0f}s", flush=True)
    np.save("bars/ml_predL.npy", predL); np.save("bars/ml_predS.npy", predS)
    # information content: correlation and top-decile realised R by test year
    rows = []
    for Y in range(2013, 2027):
        m = sess & (yr == Y) & np.isfinite(predL) & np.isfinite(yL) & np.isfinite(yS)
        r = {"year": Y}
        for nm, P, y in (("L", predL, yL), ("S", predS, yS)):
            p, t = P[m], y[m]
            r[f"{nm}_ic"] = round(pd.Series(p).corr(pd.Series(t), method="spearman"), 3)
            q = np.quantile(p, 0.98); r[f"{nm}_top2%R"] = round(t[p >= q].mean(), 3); r[f"{nm}_allR"] = round(t.mean(), 3)
        rows.append(r)
    print(pd.DataFrame(rows).to_string(index=False))
    # tradeable: one position at a time, entries where predicted R exceeds a threshold
    out = []
    for thr in (0.0, 0.05, 0.10, 0.15, 0.20, 0.30):
        L = sess & (predL > thr) & (predL >= predS); S = sess & (predS > thr) & (predS > predL)
        for cost in (0.20, 0.30, 0.50):
            T = run(df, f, L | S, np.where(L, 1.0, -1.0), stop_k=STOP, tgt_k=TGT, max_bars=MAXB, cost=cost)
            r = {"thr": thr, "cost": cost}
            for per, mm in (("13-19", T.date < "2020"), ("20-22", (T.date >= "2020") & (T.date < "2023")), ("23-26", T.date >= "2023"), ("25-26", T.date >= "2025")):
                s_ = stats(T[mm]); r.update({f"{per}_{k}": v for k, v in s_.items() if k in ("n", "win", "pf")})
            out.append(r)
    pd.set_option("display.width", 250); print(pd.DataFrame(out).to_string(index=False))
