"""Cross-asset features for gold 5m: synthetic DXY (ICE weights), silver, S&P 500. Only completed-bar data."""
import numpy as np, pandas as pd, os

DXY_W = {"EURUSD": -0.576, "USDJPY": 0.136, "GBPUSD": -0.119, "USDCAD": 0.091, "USDSEK": 0.042, "USDCHF": 0.036}

def load_close(pair, idx):
    fn = f"bars/{pair}_5m.pkl"
    if not os.path.exists(fn): return None
    b = pd.read_pickle(fn)
    # forward-fill across at most 3 missing bars, otherwise NaN
    return b.c.reindex(idx).ffill(limit=3)

def zret(x, n, vol_n=288):
    r = np.log(x).diff(n)
    sd = np.log(x).diff().rolling(vol_n, min_periods=100).std() * np.sqrt(n)
    return (r / sd).to_numpy()

def xfeatures(df):
    idx = df.index; g = df.c
    X = pd.DataFrame(index=idx)
    logd = 0.0; ok = True
    for p, w in DXY_W.items():
        s = load_close(p, idx)
        if s is None: ok = False; break
        logd = logd + w * np.log(s)
    if ok:
        dxy = np.exp(logd) * 50.14348112
        for n in (1, 3, 12, 48): X[f"dxy_z{n}"] = zret(dxy, n)
        # gold vs dollar: rolling beta of gold returns on DXY returns (1 day), residual of last 12 bars
        rg = np.log(g).diff(); rd = np.log(dxy).diff()
        cov = (rg * rd).rolling(288, min_periods=100).mean() - rg.rolling(288, min_periods=100).mean() * rd.rolling(288, min_periods=100).mean()
        beta = cov / rd.rolling(288, min_periods=100).var(ddof=0)
        res = rg - beta.shift(1) * rd
        sd = res.rolling(288, min_periods=100).std()
        X["gd_beta"] = beta.to_numpy()
        X["gd_res12"] = (res.rolling(12).sum() / (sd * np.sqrt(12))).to_numpy()
        X["gd_res48"] = (res.rolling(48).sum() / (sd * np.sqrt(48))).to_numpy()
    for p, tag in (("XAGUSD", "xag"), ("SPXUSD", "spx"), ("WTIUSD", "wti")):
        s = load_close(p, idx)
        if s is None: continue
        for n in (3, 12, 48): X[f"{tag}_z{n}"] = zret(s, n)
        if tag == "xag":
            ratio = np.log(g / s)
            X["gsr_z"] = ((ratio - ratio.rolling(288, min_periods=100).mean()) / ratio.rolling(288, min_periods=100).std()).to_numpy()
            # gold lagging silver: silver move minus gold move over 12 bars (z units)
            X["xag_lead12"] = X["xag_z12"] - zret(g, 12)
    return X

if __name__ == "__main__":
    df = pd.read_pickle("bars/XAUUSD_5m.pkl")
    X = xfeatures(df); X.to_pickle("bars/XAUUSD_xfeat.pkl")
    print(X.describe().T[["count", "mean", "std"]].round(3).to_string())
