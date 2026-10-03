from fullbt import *
from fullbt2 import backtest2
import itertools
def buy_v(x, wave=-53, rsi_=35, rsi_or=None, stretch=2.0, confirm="dotbar", rearm=True, cool=10):
    f=x["f"]; d=x["d"]; o,h,l,c=d.o.to_numpy(),d.h.to_numpy(),d.l.to_numpy(),d.c.to_numpy()
    w2=f.w2.to_numpy(); r=f.rsi.to_numpy(); d50=f.d50.to_numpy(); up=f.up.to_numpy(); clv=f.clv.to_numpy()
    ovs=(rmin(w2,3)<=wave)
    if rsi_or is not None: ovs = ovs | (rmin(r,5)<=rsi_or)
    setup = up & ovs & (rmin(r,5)<=rsi_) & (rmin(d50,10)<=-stretch)
    n=len(c); sig=np.zeros(n,bool)
    if confirm=="none": cand=setup
    elif confirm=="dotbar": cand=setup&(clv>=0.5)
    else:  # confirm within 3 bars: bullish close above previous close, after a setup
        cand=np.zeros(n,bool); last_setup=-99
        for i in range(n):
            if setup[i]: last_setup=i
            if i-last_setup<=3 and c[i]>o[i] and c[i]>c[i-1] and clv[i]>=0.5: cand[i]=True; last_setup=-99
    last=-10**9; last_low=np.inf
    for i in np.flatnonzero(cand):
        lowest=min(l[max(0,i-4):i+1])
        if i-last>cool or (rearm and lowest<last_low):
            sig[i]=True; last=i; last_low=lowest
    return sig
def tp_sig(x):
    return signals_for(x)[1]
def score(kw):
    trades=[]; caught=[]; nsig=0; yrs=0
    for sym,x in data.items():
        b=buy_v(x,**kw); b[:250]=False; tp=tp_sig(x)
        nsig+=b.sum(); yrs+=(len(b)-250)/252
        for t in backtest2(x,b,tp,None): trades.append((x["cls"],)+t)
        c=x["d"].c.to_numpy(); piv=x["piv"]
        for k,(i,t) in enumerate(piv[:-1]):
            if t==-1 and i>=250: caught.append((abs(c[piv[k+1][0]]/c[i]-1), b[max(0,i-5):i+16].any(), x["cls"]))
    T=pd.DataFrame(trades,columns=["cls","date","ret","bars","how"]); C=pd.DataFrame(caught,columns=["mv","hit","cls"])
    big=C[C.groupby("cls").mv.rank(pct=True)>=0.8]
    res={}
    for per,m in [("IS",T.date<SPLIT),("OOS",T.date>=SPLIT)]:
        g=T[m]; w=g.ret[g.ret>0].sum(); L=-g.ret[g.ret<0].sum()
        res[per+"_pf"]=round(w/L,2); res[per+"_avg%"]=round(g.ret.mean()*100,2); res[per+"_win"]=round((g.ret>0).mean(),2); res[per+"_n"]=len(g)
    res["sig/mkt-yr"]=round(nsig/yrs,2); res["catch_all_bottoms"]=round(C.hit.mean(),2); res["catch_biggest20%"]=round(big.hit.mean(),2)
    return res
VARS=[]
for confirm,rearm,rsi_or,wave,rsi_ in itertools.product(["dotbar","within3","none"],[False,True],[None,30],[-53,-60],[35,40]):
    VARS.append(dict(confirm=confirm,rearm=rearm,rsi_or=rsi_or,wave=wave,rsi_=rsi_))
def job(kw): return {**kw, **score(kw)}
if __name__=="__main__":
    with mp.Pool(4) as p: rows=p.map(job,VARS)
    R=pd.DataFrame(rows); R.to_csv("round2.csv",index=False)
    pd.set_option("display.width",250); pd.set_option("display.max_rows",100)
    print(R.sort_values("IS_pf",ascending=False).to_string(index=False))
