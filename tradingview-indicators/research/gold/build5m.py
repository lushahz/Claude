"""HistData M1 (EST, UTC-5 fixed) -> UTC 1m -> 5m OHLC. Saves bars/<PAIR>_5m.pkl"""
import zipfile, glob, io, sys, pandas as pd, numpy as np
def load_pair(pair):
    frames = []
    for fn in sorted(glob.glob(f"hd/{pair}_*.zip")):
        try: z = zipfile.ZipFile(fn)
        except zipfile.BadZipFile: continue
        csv = [n for n in z.namelist() if n.endswith(".csv")][0]
        df = pd.read_csv(io.BytesIO(z.read(csv)), sep=";", header=None, names=["t", "o", "h", "l", "c", "v"],
                         dtype={"t": str})
        frames.append(df)
    d = pd.concat(frames, ignore_index=True)
    d.index = pd.to_datetime(d.t, format="%Y%m%d %H%M%S") + pd.Timedelta(hours=5)   # EST -> UTC
    d = d[~d.index.duplicated(keep="last")].sort_index()[["o", "h", "l", "c"]].astype(float)
    return d
def to5m(d):
    g = d.resample("5min", label="left", closed="left")
    out = pd.DataFrame({"o": g.o.first(), "h": g.h.max(), "l": g.l.min(), "c": g.c.last(), "n": g.c.count()}).dropna()
    return out
if __name__ == "__main__":
    for pair in sys.argv[1:]:
        d = load_pair(pair); b = to5m(d)
        b.to_pickle(f"bars/{pair}_5m.pkl")
        print(pair, "1m rows", len(d), "5m bars", len(b), b.index[0], b.index[-1], flush=True)
