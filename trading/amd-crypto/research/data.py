"""Binance spot kline downloader with a local CSV cache.

Uses the public market-data mirror (data-api.binance.vision), which needs no API key.
"""
from __future__ import annotations

import json
import os
import time
import urllib.request

import numpy as np
import pandas as pd

BASE = "https://data-api.binance.vision/api/v3"
CACHE = os.path.join(os.path.dirname(__file__), ".cache")

INTERVAL_MS = {
    "5m": 300_000, "15m": 900_000, "30m": 1_800_000, "1h": 3_600_000,
    "2h": 7_200_000, "4h": 14_400_000, "1d": 86_400_000,
}


def _get(url: str, retries: int = 4):
    for i in range(retries):
        try:
            with urllib.request.urlopen(url, timeout=30) as r:
                return json.loads(r.read())
        except Exception:  # network hiccup -> back off and retry
            if i == retries - 1:
                raise
            time.sleep(2 ** (i + 1))


def klines(symbol: str, interval: str, days: int) -> pd.DataFrame:
    """Return OHLCV for the last `days` days, cached per (symbol, interval, days, date)."""
    os.makedirs(CACHE, exist_ok=True)
    stamp = time.strftime("%Y%m%d")
    path = os.path.join(CACHE, f"{symbol}_{interval}_{days}_{stamp}.csv")
    if os.path.exists(path):
        return pd.read_csv(path, parse_dates=["time"])

    step = INTERVAL_MS[interval]
    end = int(time.time() * 1000)
    start = end - days * 86_400_000
    rows = []
    cur = start
    while cur < end:
        batch = _get(f"{BASE}/klines?symbol={symbol}&interval={interval}&startTime={cur}&limit=1000")
        if not batch:
            break
        rows.extend(batch)
        cur = batch[-1][0] + step
        if len(batch) < 1000:
            break
    df = pd.DataFrame(rows, columns=[
        "open_time", "open", "high", "low", "close", "volume", "close_time",
        "quote_volume", "trades", "tb_base", "tb_quote", "ignore"])
    df = df[["open_time", "open", "high", "low", "close", "volume", "quote_volume"]].astype(float)
    df["time"] = pd.to_datetime(df["open_time"], unit="ms", utc=True)
    df = df.drop(columns="open_time")
    # Drop the still-forming last candle so results match closed-bar logic.
    if len(df) and df["time"].iloc[-1].value // 1_000_000 + step > end:
        df = df.iloc[:-1]
    df.to_csv(path, index=False)
    return df


def is_cached(symbol: str, interval: str, days: int) -> bool:
    stamp = time.strftime("%Y%m%d")
    return os.path.exists(os.path.join(CACHE, f"{symbol}_{interval}_{days}_{stamp}.csv"))


def tickers_24h() -> list[dict]:
    return _get(f"{BASE}/ticker/24hr")


def to_arrays(df: pd.DataFrame) -> dict[str, np.ndarray]:
    return {k: df[k].to_numpy(dtype=float) for k in ("open", "high", "low", "close", "volume")}
