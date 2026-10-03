import json, time, urllib.request, csv
COINS = ["BTC","ETH","XRP","LTC","ADA","SOL","DOGE","BNB","LINK","DOT","AVAX","XLM","TRX","BCH","ATOM","ETC","HBAR","NEAR","AAVE","ALGO","UNI","FIL","XMR","DASH","ZEC","EOS","XTZ","MANA","SAND","VET"]
def get(url):
    for a in range(6):
        try: return json.load(urllib.request.urlopen(urllib.request.Request(url,headers={"User-Agent":"Mozilla/5.0"}),timeout=30))
        except Exception: time.sleep(2*(a+1))
    raise RuntimeError(url)
meta=[]
for c in COINS:
    try:
        r=get(f"https://query1.finance.yahoo.com/v8/finance/chart/{c}-USD?period1=1262304000&period2=1791200000&interval=1d")["chart"]["result"][0]
    except Exception as e:
        print("FAIL",c,e); continue
    q=r["indicators"]["quote"][0]; n=0
    with open(f"{c}.csv","w",newline="") as f:
        w=csv.writer(f); w.writerow(["t","o","h","l","c","v"])
        for i,t in enumerate(r["timestamp"]):
            o,h,l,cl,v=q["open"][i],q["high"][i],q["low"][i],q["close"][i],q["volume"][i]
            if None in (o,h,l,cl) or cl<=0: continue
            w.writerow([t,o,h,l,cl,v or 0]); n+=1
    meta.append((c,n,time.strftime("%Y-%m-%d",time.gmtime(r["timestamp"][0]))))
    print(c,n,meta[-1][2],flush=True); time.sleep(0.3)
with open("coins.csv","w",newline="") as f:
    w=csv.writer(f); w.writerow(["coin","bars","first"]); w.writerows(meta)
