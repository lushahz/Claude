"""Walk-forward gradient boosting on reversal candidates (BTC 5m). Label = trade wins after costs for a fixed exit.
Train on all years before Y, test on Y (2022, 2023, 2024). 2025-26 untouched."""
import numpy as np, pandas as pd, warnings, sys; warnings.filterwarnings("ignore")
from numba import njit
from sklearn.ensemble import HistGradientBoostingClassifier
df = pd.read_pickle("btc5m_raw.pkl"); F = pd.read_pickle("btc5m_feat.pkl")
o, h, l, c = (df[k].to_numpy() for k in "ohlc"); a = F.atr.to_numpy()
def nz(x): return np.nan_to_num(np.asarray(x, dtype=float))
w1, w2 = nz(F.wt1), nz(F.wt2)
cu, cd, tu, td = (F[k].to_numpy(bool) for k in ("cross_up", "cross_dn", "turn_up", "turn_dn"))
candL = (cu & (w2 <= -40)) | (tu & (w1 < w2) & (w2 <= -50))
candS = (cd & (w2 >= 40)) | (td & (w1 > w2) & (w2 >= 50))

@njit(cache=True)
def label(o, h, l, c, a, idx, side, sl_k, tp_k, mb):
    out = np.full(len(idx), np.nan)
    for q in range(len(idx)):
        i = idx[q]; s = side[q]; e = i + 1
        if e >= len(c): continue
        ep = o[e]; st = ep - s * sl_k * a[i]; tg = ep + s * tp_k * a[i]; xp = np.nan
        for j in range(e, len(c)):
            if s > 0:
                if l[j] <= st: xp = min(o[j], st); break
                if h[j] >= tg: xp = max(o[j], tg); break
            else:
                if h[j] >= st: xp = max(o[j], st); break
                if l[j] <= tg: xp = min(o[j], tg); break
            if j - e + 1 >= mb: xp = c[j]; break
        out[q] = s * (xp - ep) / ep * 100          # gross % move
    return out

idx = np.r_[np.flatnonzero(candL), np.flatnonzero(candS & ~candL)]
side = np.r_[np.ones(candL.sum()), -np.ones((candS & ~candL).sum())]
order = np.argsort(idx); idx, side = idx[order], side[order]
if __name__ == "__main__":
    SLK, TPK, MB = float(sys.argv[1]) if len(sys.argv) > 1 else 2.0, float(sys.argv[2]) if len(sys.argv) > 2 else 1.0, int(sys.argv[3]) if len(sys.argv) > 3 else 36
    gross = label(o, h, l, c, a, idx, side, SLK, TPK, MB)
    # side-normalised features: directional ones flipped for shorts so one model serves both sides
    DIR = ["wt1", "wt2", "stk", "rsi", "rsi7", "d_ema20", "d_ema50", "d_ema200", "bb", "ret1", "ret3", "ret12", "ret48", "clv", "body",
           "tbr", "cvd3", "cvd12", "fcvd12", "d_vwap", "basis", "prem_z", "fund", "eth_rel12",
           "m15_wt2", "m15_rsi", "m15_trend", "m15_e50", "h1_wt2", "h1_rsi", "h1_trend", "h1_e50", "h4_wt2", "h4_rsi", "h4_trend", "h4_e50",
           "d1_wt2", "d1_rsi", "d1_trend", "d1_e50"]
    X = F.iloc[idx].copy().drop(columns=["atr", "cross_up", "cross_dn", "turn_up", "turn_dn"])
    for col in DIR:
        v = X[col].to_numpy(dtype=float)
        if col in ("stk", "rsi", "rsi7", "m15_rsi", "h1_rsi", "h4_rsi", "d1_rsi"): v = v - 50
        if col == "tbr": v = v - 0.5
        if col == "clv": v = v - 0.5
        X[col] = v * side
    # wick that matters: lower wick for longs, upper for shorts; divergences on the trade side
    X["wick_with"] = np.where(side > 0, X.wick_dn, X.wick_up); X["wick_against"] = np.where(side > 0, X.wick_up, X.wick_dn)
    X["div_with"] = np.where(side > 0, X.bull_div6, X.bear_div6).astype(float); X["div_against"] = np.where(side > 0, X.bear_div6, X.bull_div6).astype(float)
    X = X.drop(columns=["wick_dn", "wick_up", "bull_div", "bear_div", "bull_div6", "bear_div6"]).astype(float)
    X["side"] = side; X["is_cross"] = np.where(side > 0, cu[idx], cd[idx]).astype(float)
    dates = df.index[idx]; yr = dates.year.to_numpy(); atrp = F.atr_pct.to_numpy()[idx]
    COST = 0.04
    y = (gross - COST > 0).astype(int)
    print(f"candidates {len(idx)}, exit SL{SLK} TP{TPK} {MB} bars; base win at {COST}% cost: {y[yr<2025].mean():.3f}")
    P = np.full(len(idx), np.nan); imps = []
    for Y in (2022, 2023, 2024):
        tr = (yr < Y) & np.isfinite(gross); te = (yr == Y) & np.isfinite(gross)
        m = HistGradientBoostingClassifier(max_iter=400, learning_rate=0.04, max_leaf_nodes=31, min_samples_leaf=200, l2_regularization=1.0,
                                           early_stopping=True, validation_fraction=0.15, n_iter_no_change=30, random_state=0)
        m.fit(X[tr], y[tr]); P[te] = m.predict_proba(X[te])[:, 1]
    np.save(f"mlP_{SLK}_{TPK}_{MB}.npy", P); np.save("ml_idx.npy", idx); np.save("ml_side.npy", side); X.to_pickle("ml_X.pkl")
    pd.to_pickle(gross, f"ml_gross_{SLK}_{TPK}_{MB}.pkl")
    rows = []
    for Y in (2022, 2023, 2024):
        mm = yr == Y
        for q in (0.0, 0.5, 0.7, 0.8, 0.9, 0.95):
            thr = np.nanquantile(P[mm], q); s = mm & (P >= thr)
            for cost in (0.0, 0.02, 0.04, 0.08):
                pnl = gross[s] - cost; w = pnl[pnl > 0].sum(); ls = -pnl[pnl < 0].sum()
                rows.append({"year": Y, "top%": int(round(100 * (1 - q))), "cost": cost, "n": int(s.sum()), "win%": round(100 * (pnl > 0).mean(), 1), "PF": round(w / ls, 2) if ls else np.inf, "avg%": round(pnl.mean(), 3)})
    R = pd.DataFrame(rows); pd.set_option("display.width", 200); pd.set_option("display.max_rows", 300)
    print(R.pivot_table(index=["top%", "cost"], columns="year", values=["win%", "PF"]).round(2).to_string())
