"""Does the recent edge come from volatility (costs small vs ATR) rather than calendar? Split trades by ATR($) at entry."""
import numpy as np, pandas as pd, warnings; warnings.filterwarnings("ignore")
import grid2_fams as G
from glab import run, stats
df, f, fams = G.df, G.f, G.fams
a = f.atr.to_numpy()
rows = []
for name, (L, S) in fams.items():
    sig = L | S; side = np.where(L, 1.0, -1.0)
    for en, kw in (("s1.5/t2/36", dict(stop_k=1.5, tgt_k=2.0, max_bars=36)), ("s1.5/trail2/72", dict(stop_k=1.5, tgt_k=50, max_bars=72, trail_k=2.0))):
        T = run(df, f, sig, side, cost=0.30, **kw)
        ea = pd.Series(a, index=df.index).shift(1).reindex(T.date).to_numpy()
        r = {"family": name[:42], "exit": en}
        for lo, hi in ((0, 1.0), (1.0, 1.5), (1.5, 2.5), (2.5, 99)):
            m = (ea >= lo) & (ea < hi); s_ = stats(T[m])
            r[f"atr{lo}-{hi}_n"] = s_["n"]; r[f"atr{lo}-{hi}_pf"] = s_.get("pf")
        # pre-2020 high vol only (out of the recent regime) as a check
        m = (ea >= 1.5) & (T.date < "2020"); s_ = stats(T[m]); r["pre20_atr>1.5_n"] = s_["n"]; r["pre20_atr>1.5_pf"] = s_.get("pf")
        rows.append(r)
pd.set_option("display.width", 260); print(pd.DataFrame(rows).to_string(index=False))
