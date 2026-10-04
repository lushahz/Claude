"""BTC 5m research dataset: spot candles + order flow, ETH, futures basis/premium, funding, and ~60 features.
Every feature uses only information available at the close of its bar."""
import numpy as np, pandas as pd, glob, zipfile, io, warnings; warnings.filterwarnings("ignore")

def read_dir(pattern, cols):
    fr = []
    for fn in sorted(glob.glob(pattern)):
        z = zipfile.ZipFile(fn); raw = z.read(z.namelist()[0])
        d = pd.read_csv(io.BytesIO(raw), header=None)
        if isinstance(d.iloc[0, 0], str) and not str(d.iloc[0, 0]).isdigit():   # some futures files have a header row
            d = d.iloc[1:]
        fr.append(d)
    d = pd.concat(fr).iloc[:, :len(cols)]; d.columns = cols
    t = pd.to_numeric(d[cols[0]]).astype("int64"); t = np.where(t > 1e14, t // 1000, t)
    d.index = pd.to_datetime(t, unit="ms"); d = d[~d.index.duplicated()].sort_index()
    return d.drop(columns=cols[0]).apply(pd.to_numeric, errors="coerce")

K = ["t", "o", "h", "l", "c", "v", "ct", "qv", "n", "tbv", "tbq"]
btc = read_dir("spot/BTCUSDT-5m-*.zip", K)
eth = read_dir("spot/ETHUSDT-5m-*.zip", K)[["c"]].rename(columns={"c": "eth"})
fut = read_dir("fut/BTCUSDT-5m-*.zip", K)[["c", "tbv", "v"]].rename(columns={"c": "fc", "tbv": "ftbv", "v": "fv"})
prem = read_dir("prem/BTCUSDT-5m-*.zip", K[:6])[["c"]].rename(columns={"c": "prem"})
fr = []
for fn in sorted(glob.glob("fund/*.zip")):
    z = zipfile.ZipFile(fn); d = pd.read_csv(io.BytesIO(z.read(z.namelist()[0])))
    fr.append(d)
fund = pd.concat(fr); fund.columns = [c.lower() for c in fund.columns]
tcol = [c for c in fund.columns if "time" in c][0]; rcol = [c for c in fund.columns if "rate" in c][0]
ft = pd.to_numeric(fund[tcol]).astype("int64"); ft = np.where(ft > 1e14, ft // 1000, ft)
fund = pd.Series(pd.to_numeric(fund[rcol]).values, index=pd.to_datetime(ft, unit="ms")).sort_index()
fund = fund[~fund.index.duplicated()]
df = btc[["o", "h", "l", "c", "v", "n", "tbv"]].join([eth, fut, prem], how="left")
# funding: last settled rate (known after its timestamp), forward-filled
df["fund"] = fund.reindex(df.index, method="ffill").values
df = df[df.index >= "2020-01-01"]
df.to_pickle("btc5m_raw.pkl")
print(df.shape, df.index[0], df.index[-1]); print(df.isna().mean().round(3).to_string())
