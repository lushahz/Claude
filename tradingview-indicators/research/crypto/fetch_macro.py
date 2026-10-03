"""Download TOTAL and BTC dominance (CoinMarketCap) and USDT market cap (Coin Metrics); writes macro.csv."""
import json, urllib.request, time, pandas as pd
def get(url):
    for a in range(5):
        try: return json.load(urllib.request.urlopen(urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0", "Accept": "application/json"}), timeout=60))
        except Exception: time.sleep(3)
    raise RuntimeError(url)
q = []; t = 1367366400; end = int(time.time())
while t < end:
    te = min(t + 2000 * 86400, end)
    q += get(f"https://api.coinmarketcap.com/data-api/v3/global-metrics/quotes/historical?format=chart&interval=1d&timeStart={t}&timeEnd={te}")["data"]["quotes"]
    t = te; time.sleep(1)
rows = []; url = "https://community-api.coinmetrics.io/v4/timeseries/asset-metrics?assets=usdt&metrics=CapMrktCurUSD&frequency=1d&start_time=2014-10-01&page_size=10000"
while url:
    d = get(url); rows += d["data"]; url = d.get("next_page_url")
u = pd.Series({pd.Timestamp(r["time"][:10]): float(r["CapMrktCurUSD"]) for r in rows}).sort_index()
g = pd.DataFrame({"total": [x["quote"][0]["totalMarketCap"] for x in q], "btcd": [x["btcDominance"] for x in q]},
                 index=[pd.Timestamp(x["timestamp"][:10]) for x in q])
g = g[~g.index.duplicated(keep="last")].sort_index()
g["usdt"] = u.reindex(g.index).ffill(); g["usdtd"] = g.usdt / g.total * 100
g.to_csv("macro.csv")
