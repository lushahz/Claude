import json, time, urllib.request, csv, sys
UNIVERSE = {
 "crypto":   ["BTC-USD","ETH-USD","XRP-USD","LTC-USD","ADA-USD","SOL-USD","DOGE-USD","BNB-USD"],
 "forex":    ["EURUSD=X","GBPUSD=X","USDJPY=X","AUDUSD=X","USDCAD=X","USDCHF=X","NZDUSD=X","EURJPY=X"],
 "stocks":   ["AAPL","MSFT","AMZN","NVDA","TSLA","META","GOOGL","JPM","XOM","JNJ","WMT","BA","NFLX","AMD"],
 "cfd_index":["^GSPC","^NDX","^DJI","^RUT","^GDAXI","^FTSE","^N225","^HSI"],
 "cfd_commodity":["GC=F","SI=F","CL=F","NG=F","HG=F"],
 "exchanges":["CME","ICE","NDAQ","CBOE"],
}
def get(url):
    for a in range(6):
        try:
            return json.load(urllib.request.urlopen(urllib.request.Request(url,headers={"User-Agent":"Mozilla/5.0"}), timeout=30))
        except Exception as e:
            time.sleep(2*(a+1))
    raise RuntimeError(url)
meta=[]
for cls, syms in UNIVERSE.items():
    for s in syms:
        r=get(f"https://query1.finance.yahoo.com/v8/finance/chart/{urllib.request.quote(s)}?period1=1262304000&period2=1791200000&interval=1d")["chart"]["result"][0]
        q=r["indicators"]["quote"][0]; n=0
        fn=s.replace("^","IDX_").replace("=","_").replace("-","_")
        with open(f"{fn}.csv","w",newline="") as f:
            w=csv.writer(f); w.writerow(["t","o","h","l","c","v"])
            for i,t in enumerate(r["timestamp"]):
                o,h,l,c,v=q["open"][i],q["high"][i],q["low"][i],q["close"][i],q["volume"][i]
                if None in (o,h,l,c): continue
                w.writerow([t,o,h,l,c,v or 0]); n+=1
        meta.append((cls,s,fn,n,r["timestamp"][0]))
        print(cls,s,n,time.strftime("%Y-%m-%d",time.gmtime(r["timestamp"][0])),flush=True)
        time.sleep(0.3)
with open("universe.csv","w",newline="") as f:
    w=csv.writer(f); w.writerow(["cls","sym","file","bars","first"]); w.writerows(meta)
