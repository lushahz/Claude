import numpy as np, pandas as pd, warnings; warnings.filterwarnings("ignore")
from glab import run, stats, session_mask
from grid1 import build, df, f
cfgs = [("h4",1,"wt","lo","wtcross",1.5,1.5,24), ("h4",1,"rsi","hi","bar",1.5,1.5,24), ("none",1,"rsi","hi","bar",1.0,2.0,24)]
LVL = {"wt": {"lo": 40, "hi": 60}, "rsi": {"lo": 20, "hi": 30}, "bb": {"lo": 1.0, "hi": 1.3}}
for tf,tk,kind,lv,trig,sk,tg,mb in cfgs:
    sig, side = build(tf, tk, kind, LVL[kind][lv], trig)
    for cost in (0.0, 0.15, 0.30):
        T = run(df, f, sig, side, sk, tg, mb, cost)
        out = []
        for per, m in (("IS", T.date < "2020-01-01"), ("OOS", T.date >= "2023-01-01")):
            s = stats(T[m]); out.append(f"{per}: win {s['win']} pf {s['pf']} avg ${s['avg_$']}")
        print(tf, kind, lv, trig, f"cost {cost}", " | ".join(out))
# typical 5m ATR in $ by year
a = pd.Series(f.atr.to_numpy(), index=df.index)[session_mask(df.index)]
print((a.groupby(a.index.year).median()).round(2).to_dict())
