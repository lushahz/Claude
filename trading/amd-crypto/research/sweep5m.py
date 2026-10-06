"""5-minute study on Binance USDT perps (12 months, 20 coins): first half vs second half."""
from __future__ import annotations

import itertools
import sys
from concurrent.futures import ProcessPoolExecutor

import numpy as np
import pandas as pd

from amd_engine import Params, htf_trend, run
from backtest import UNIVERSE
from data import bulk_klines, to_arrays

MONTHS = [f"{y}-{m:02d}" for y, m in [(2025, 10), (2025, 11), (2025, 12)] + [(2026, i) for i in range(1, 10)]]
SYMS = [s if s != "PEPEUSDT" else "1000PEPEUSDT" for s in UNIVERSE]
DATA = {}


def load():
    for s in SYMS:
        df = bulk_klines(s, "5m", MONTHS)
        times = df["time"].dt.tz_localize(None).to_numpy()
        DATA[s] = (to_arrays(df), times, htf_trend(times, df["close"].to_numpy()))


def evaluate(combo, split):
    p = Params(**combo)
    out = {"IS": [], "OOS": []}
    coin_tot = {}
    for s, (a, times, htf) in DATA.items():
        res = run(a["open"], a["high"], a["low"], a["close"], a["volume"], p, htf)
        coin_tot[s] = sum(t.r_net for t in res.trades)
        for t in res.trades:
            out["IS" if times[t.entry_bar] < split else "OOS"].append((t.r_net, t.r_gross))
    row = dict(combo)
    for k in ("IS", "OOS"):
        x = np.array(out[k]) if out[k] else np.zeros((0, 2))
        row[f"{k}_n"] = len(x)
        row[f"{k}_avgR"] = x[:, 0].mean() if len(x) else np.nan
        row[f"{k}_gross"] = x[:, 1].mean() if len(x) else np.nan
    row["coins_pos"] = sum(v > 0 for v in coin_tot.values())
    row["min_avgR"] = min(row["IS_avgR"], row["OOS_avgR"])
    return row


def _job(args):
    return evaluate(*args)


def sweep(grid, base=None):
    base = base or {}
    split = np.datetime64("2026-04-01")
    keys = list(grid)
    combos = [{**base, **dict(zip(keys, v))} for v in itertools.product(*grid.values())]
    with ProcessPoolExecutor() as ex:
        rows = list(ex.map(_job, [(c, split) for c in combos]))
    return pd.DataFrame(rows).sort_values("min_avgR", ascending=False)


if __name__ == "__main__":
    load()
    pd.set_option("display.width", 220)
    grid = {
        "range_len": [30, 60],
        "range_max_atr": [4.0, 5.0, 6.0],
        "tp_r": [2.0, 3.0],
        "min_risk_pct": [0.0, 0.4, 0.7],
    }
    df = sweep(grid)
    print(df.to_string(index=False, float_format=lambda x: f"{x:.3f}"))
    df.to_csv("results/sweep_5m.csv", index=False)
