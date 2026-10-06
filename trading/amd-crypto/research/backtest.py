"""Backtest the AMD + Volume Profile model on Binance data.

    python backtest.py                       # default params, default universe
    python backtest.py --tf 1h --days 730    # other timeframe / history
"""
from __future__ import annotations

import argparse
import dataclasses
import os

import numpy as np
import pandas as pd

from amd_engine import Params, run, stats
from data import klines, to_arrays

UNIVERSE = ["BTCUSDT", "ETHUSDT", "SOLUSDT", "XRPUSDT", "BNBUSDT", "DOGEUSDT", "ADAUSDT",
            "SUIUSDT", "NEARUSDT", "LINKUSDT", "AVAXUSDT", "PEPEUSDT", "ENAUSDT", "UNIUSDT",
            "ZECUSDT", "WLDUSDT", "LTCUSDT", "AAVEUSDT", "TAOUSDT", "FETUSDT"]


def backtest(symbols, tf, days, p: Params, verbose=False):
    rows, all_trades = [], []
    for s in symbols:
        df = klines(s, tf, days)
        a = to_arrays(df)
        res = run(a["open"], a["high"], a["low"], a["close"], a["volume"], p)
        st = stats(res.trades)
        st.update(symbol=s, setups=res.setups, bars=len(df))
        rows.append(st)
        for tr in res.trades:
            all_trades.append({**dataclasses.asdict(tr), "symbol": s,
                               "entry_time": df["time"].iloc[tr.entry_bar]})
    per = pd.DataFrame(rows)
    trades = pd.DataFrame(all_trades)
    if verbose:
        cols = ["symbol", "bars", "setups", "trades", "win_rate", "avg_r", "total_r", "profit_factor", "max_dd_r"]
        print(per.reindex(columns=cols).to_string(index=False, float_format=lambda x: f"{x:.2f}"))
    return per, trades


def summary(trades: pd.DataFrame) -> dict:
    if trades.empty:
        return {"trades": 0}
    trades = trades.sort_values("entry_time")
    r = trades["r_net"].to_numpy()
    eq = np.cumsum(r)
    dd = (np.maximum.accumulate(np.concatenate([[0], eq]))[1:] - eq).max()
    return {
        "trades": len(r),
        "win%": round((r > 0).mean() * 100, 1),
        "avgR": round(r.mean(), 3),
        "totalR": round(r.sum(), 1),
        "PF": round(r[r > 0].sum() / -r[r < 0].sum(), 2) if (r < 0).any() else np.inf,
        "maxDD_R": round(dd, 1),
        "exits": trades["reason"].value_counts().to_dict(),
    }


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--tf", default="1h")
    ap.add_argument("--days", type=int, default=730)
    ap.add_argument("--symbols", nargs="*", default=UNIVERSE)
    args = ap.parse_args()
    per, trades = backtest(args.symbols, args.tf, args.days, Params(), verbose=True)
    print("\nPORTFOLIO:", summary(trades))
    os.makedirs("results", exist_ok=True)
    trades.to_csv(f"results/trades_{args.tf}.csv", index=False)
