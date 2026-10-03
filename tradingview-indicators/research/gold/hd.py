import re, sys, time, subprocess, os, zipfile, io
def get(pair, year, month=None):
    page = f"https://www.histdata.com/download-free-forex-historical-data/?/ascii/1-minute-bar-quotes/{pair.lower()}/{year}" + (f"/{month}" if month else "")
    html = subprocess.run(["curl", "-sS", "-m", "60", "-A", "Mozilla/5.0", "-c", "cj.txt", page], capture_output=True, text=True).stdout
    tk = re.search(r'name="tk" id="tk" value="([^"]+)"', html)
    dm = re.search(r'name="datemonth" id="datemonth" value="([^"]+)"', html)
    if not tk: return None
    out = f"hd/{pair}_{year}{'_'+str(month) if month else ''}.zip"
    subprocess.run(["curl", "-sS", "-m", "300", "-A", "Mozilla/5.0", "-b", "cj.txt", "-e", page, "-X", "POST",
                    "-d", f"tk={tk.group(1)}&date={year}&datemonth={dm.group(1)}&platform=ASCII&timeframe=M1&fxpair={pair}",
                    "https://www.histdata.com/get.php", "-o", out])
    return out
pair = sys.argv[1]
for y in range(int(sys.argv[2]), int(sys.argv[3]) + 1):
    out = get(pair, y)
    ok = out and zipfile.is_zipfile(out)
    if not ok:   # current year: per month
        for m in range(1, 13):
            o = get(pair, y, m)
            print(pair, y, m, o and zipfile.is_zipfile(o), flush=True)
    else:
        print(pair, y, os.path.getsize(out), flush=True)
    time.sleep(1)
