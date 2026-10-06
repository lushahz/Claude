"""Rank liquid Binance USDT pairs by how much they move.

"Mover score" = 30-day average daily range (ATR%) weighted by liquidity, so a coin
needs BOTH volatility and enough volume to absorb stops without heavy slippage.

    python scan_movers.py            # print the ranking, write ../watchlists/*.txt
"""
from __future__ import annotations

import os

import numpy as np
import pandas as pd

from data import klines, tickers_24h

# Stablecoins, wrapped / pegged assets and tokenised gold: they don't "move".
EXCLUDE = {
    "USDC", "FDUSD", "TUSD", "USDP", "DAI", "USD1", "RLUSD", "USDE", "PYUSD", "EUR", "EURI",
    "AEUR", "XUSD", "U", "BFUSD", "XAUT", "PAXG", "WBTC", "WBETH", "BNSOL",
    "SPCXB", "SNDKB", "CRCLB",  # tokenised stocks
}
MIN_MEDIAN_QV = 8e6       # at least $8M median daily spot volume on Binance
CANDIDATES = 120          # how many of the top-volume pairs to inspect
HERE = os.path.dirname(__file__)
# Binance perps quote tiny-priced memecoins per 1000 units.
PERP_ALIAS = {"PEPE": "1000PEPE", "SHIB": "1000SHIB", "BONK": "1000BONK", "FLOKI": "1000FLOKI",
              "SATS": "1000SATS", "LUNC": "1000LUNC", "XEC": "1000XEC", "CAT": "1000CAT"}


def perp(base: str) -> str:
    return f"BINANCE:{PERP_ALIAS.get(base, base)}USDT.P"


def scan() -> pd.DataFrame:
    tick = [t for t in tickers_24h()
            if t["symbol"].endswith("USDT") and t["symbol"].isascii() and t["symbol"].isalnum()]
    tick.sort(key=lambda t: -float(t["quoteVolume"]))
    out = []
    for t in tick[: CANDIDATES + len(EXCLUDE)]:
        sym = t["symbol"]
        base = sym[:-4]
        if base in EXCLUDE:
            continue
        d = klines(sym, "1d", 120)
        if len(d) < 90:            # skip fresh listings: not enough history to judge
            continue
        last = d.tail(90)
        prev_close = d["close"].shift(1)
        tr = np.maximum(d["high"], prev_close) - np.minimum(d["low"], prev_close)
        atr_pct_30 = (tr / d["close"]).tail(30).mean() * 100
        atr_pct_90 = (tr / d["close"]).tail(90).mean() * 100
        med_qv = last["quote_volume"].median()
        out.append({
            "symbol": sym, "base": base,
            "atr_pct_30d": atr_pct_30, "atr_pct_90d": atr_pct_90,
            "median_qv_m": med_qv / 1e6,
            "ret_90d_pct": (last["close"].iloc[-1] / last["close"].iloc[0] - 1) * 100,
        })
        if len(out) >= CANDIDATES:
            break
    df = pd.DataFrame(out)
    df = df[df["median_qv_m"] * 1e6 >= MIN_MEDIAN_QV].copy()
    # log-liquidity weighting: $8M -> 0.73, $15M -> 1.0, $150M -> 2.0, $1.5B -> 3.0
    df["liq_weight"] = np.log10(df["median_qv_m"] / 1.5)
    df["mover_score"] = (0.6 * df["atr_pct_30d"] + 0.4 * df["atr_pct_90d"]) * df["liq_weight"]
    return df.sort_values("mover_score", ascending=False).reset_index(drop=True)


def write_watchlists(df: pd.DataFrame) -> None:
    wl = os.path.join(HERE, "..", "watchlists")
    os.makedirs(wl, exist_ok=True)
    majors = ["BTC", "ETH", "SOL", "XRP", "BNB"]
    movers = [b for b in df["base"] if b not in majors][:20]

    context = [
        "###MARKET CONTEXT", "CRYPTOCAP:TOTAL", "CRYPTOCAP:TOTAL2", "CRYPTOCAP:TOTAL3",
        "CRYPTOCAP:OTHERS", "CRYPTOCAP:BTC.D", "CRYPTOCAP:ETH.D", "CRYPTOCAP:USDT.D",
        "CRYPTOCAP:OTHERS.D", "BINANCE:ETHBTC", "TVC:DXY", "SP:SPX",
    ]
    core = ["###MAJORS"] + [perp(b) for b in majors]
    alts = ["###TOP MOVERS"] + [perp(b) for b in movers]
    with open(os.path.join(wl, "AMD_crypto_full.txt"), "w") as f:
        f.write(",".join(context + core + alts) + "\n")
    with open(os.path.join(wl, "AMD_market_context.txt"), "w") as f:
        f.write(",".join(context) + "\n")
    with open(os.path.join(wl, "AMD_top_movers.txt"), "w") as f:
        f.write(",".join(core + alts) + "\n")


if __name__ == "__main__":
    pd.set_option("display.width", 160)
    res = scan()
    print(res.head(35).to_string(float_format=lambda x: f"{x:,.2f}"))
    res.to_csv(os.path.join(HERE, "movers_ranking.csv"), index=False, float_format="%.3f")
    write_watchlists(res)
