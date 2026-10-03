import os, sys, time, random, datetime as dt, urllib.request, threading
from concurrent.futures import ThreadPoolExecutor
inst = sys.argv[1]; start = dt.date.fromisoformat(sys.argv[2]); end = dt.date.fromisoformat(sys.argv[3]); workers = int(sys.argv[4]) if len(sys.argv) > 4 else 3
os.makedirs(f"raw/{inst}", exist_ok=True)
days = [start + dt.timedelta(d) for d in range((end - start).days + 1)]
days = [d for d in days if d.weekday() != 5]            # skip Saturdays (no trading)
lock = threading.Lock(); stats = {"ok": 0, "empty": 0, "fail": 0}
def fetch(d):
    fn = f"raw/{inst}/{d.isoformat()}.bi5"
    if os.path.exists(fn): return
    url = f"https://datafeed.dukascopy.com/datafeed/{inst}/{d.year}/{d.month-1:02d}/{d.day:02d}/BID_candles_min_1.bi5"
    for a in range(10):
        try:
            r = urllib.request.urlopen(urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"}), timeout=30)
            data = r.read()
            with open(fn, "wb") as f: f.write(data)
            with lock: stats["ok" if data else "empty"] += 1
            return
        except urllib.error.HTTPError as e:
            if e.code == 404:
                open(fn, "wb").close(); 
                with lock: stats["empty"] += 1
                return
        except Exception:
            pass
        time.sleep(min(60, 2 ** a) + random.random())
    with lock: stats["fail"] += 1
with ThreadPoolExecutor(workers) as ex:
    for i, _ in enumerate(ex.map(fetch, days)):
        if i % 200 == 0: print(inst, i, len(days), stats, flush=True)
print("DONE", inst, stats, flush=True)
