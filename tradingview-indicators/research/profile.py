import pickle, numpy as np, pandas as pd
from features import recent
data = pickle.load(open("data.pkl","rb"))
cols = ["w2","rsi","k","d200","d50","dd252","ru252","volz5","clv","ret5"]
B=[]; T=[]; ALL=[]
for s,x in data.items():
    f=x["f"].copy(); f["cls"]=x["cls"]
    f["bull_div10"]=recent(f.bull_div.to_numpy(),10); f["bear_div10"]=recent(f.bear_div.to_numpy(),10)
    ALL.append(f.iloc[250:])
    for i,t in x["piv"]:
        if i<250: continue
        row=f.iloc[i].copy()
        # min wave & rsi within +-3 bars of the pivot (oscillators lag a little)
        lo,hi=max(0,i-3),min(len(f),i+4)
        row["w2_ext"]=f.w2.iloc[lo:hi].min() if t==-1 else f.w2.iloc[lo:hi].max()
        row["rsi_ext"]=f.rsi.iloc[lo:hi].min() if t==-1 else f.rsi.iloc[lo:hi].max()
        # divergence confirmed within 10 bars after the pivot
        row["div_after"]=(f.bull_div if t==-1 else f.bear_div).iloc[i:i+11].any()
        (B if t==-1 else T).append(row)
B=pd.DataFrame(B); T=pd.DataFrame(T); A=pd.concat(ALL)
def pct(series, base):
    return series.quantile([.25,.5,.75]).round(2).tolist(), base.quantile([.25,.5,.75]).round(2).tolist()
print("BOTTOMS n=",len(B),"  TOPS n=",len(T),"  all bars n=",len(A))
for c in ["w2_ext","rsi_ext","d200","d50","dd252","volz5","clv","ret5"]:
    base = A[c.replace("_ext","")] if c.endswith("_ext") else A[c]
    print(f"{c:8s} bottoms q25/50/75 {B[c].quantile([.25,.5,.75]).round(2).tolist()}  tops {T[c].quantile([.25,.5,.75]).round(2).tolist()}  all-days {base.quantile([.25,.5,.75]).round(2).tolist()}")
print("share of bottoms with wave <= -53 within +-3 bars:", (B.w2_ext<=-53).mean().round(3), " all days w2<=-53:", (A.w2<=-53).mean().round(3))
print("share of bottoms with wave <= -60:", (B.w2_ext<=-60).mean().round(3), "  <= -75:", (B.w2_ext<=-75).mean().round(3))
print("share of tops with wave >= 53:", (T.w2_ext>=53).mean().round(3), " all days w2>=53:", (A.w2>=53).mean().round(3))
print("bottoms with RSI<=30 within +-3:", (B.rsi_ext<=30).mean().round(3), " all days:", (A.rsi<=30).mean().round(3))
print("tops with RSI>=70 within +-3:", (T.rsi_ext>=70).mean().round(3), " all days:", (A.rsi>=70).mean().round(3))
print("bottoms followed by bull divergence within 10 bars:", B.div_after.mean().round(3))
print("tops followed by bear divergence within 10 bars:", T.div_after.mean().round(3))
print("bottoms below EMA200:", (B.d200<0).mean().round(3), " tops above EMA200:", (T.d200>0).mean().round(3))
print("bottoms with volume spike (z>2 in last 5 bars, excl FX):", (B[B.cls!='forex'].volz5>2).mean().round(3), " all days:", (A[A.cls!='forex'].volz5>2).mean().round(3))
print("\nBy asset class, bottoms: median wave / RSI / dd252(ATR) ; tops median wave / RSI")
for cls in B.cls.unique():
    b=B[B.cls==cls]; t=T[T.cls==cls]
    print(f"  {cls:14s} n={len(b):3d} wave {b.w2_ext.median():6.1f} rsi {b.rsi_ext.median():5.1f} dd {b.dd252.median():6.1f} | tops wave {t.w2_ext.median():6.1f} rsi {t.rsi_ext.median():5.1f}")
B.to_pickle("bottoms.pkl"); T.to_pickle("tops.pkl")
