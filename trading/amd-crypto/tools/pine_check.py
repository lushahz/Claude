"""Compile Pine scripts with TradingView's public pine-facade and print errors/warnings.

    python tools/pine_check.py pine/*.pine
Exit code 1 if any script has errors.
"""
import json
import subprocess
import sys

URL = ("https://pine-facade.tradingview.com/pine-facade/translate_light"
       "?user_name=Guest&pine_id=00000000-0000-0000-0000-000000000000")


def check(path: str) -> bool:
    out = subprocess.run(
        ["curl", "-sS", "-m", "60", "-X", "POST", URL, "-H", "Referer: https://www.tradingview.com/",
         "-F", f"source=<{path}"], capture_output=True, text=True, check=True).stdout
    data = json.loads(out)
    res = data.get("result") or {}
    errs = res.get("errors2") or res.get("errors") or []
    warns = res.get("warnings2") or res.get("warnings") or []
    ok = data.get("success") and not errs
    print(f"{'OK ' if ok else 'ERR'} {path}  ({len(errs)} errors, {len(warns)} warnings)")
    if not data.get("success"):
        print("   ", json.dumps(data)[:2000])
    for kind, items in (("error  ", errs), ("warning", warns)):
        for e in items:
            msg = e.get("message", "")
            for k, v in (e.get("ctx") or {}).items():
                msg = msg.replace("{" + k + "}", str(v))
            print(f"   {kind} L{e.get('start', {}).get('line')}: {msg}")
    return bool(ok)


if __name__ == "__main__":
    results = [check(p) for p in sys.argv[1:]]
    sys.exit(0 if all(results) else 1)
