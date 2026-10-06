"""Robustness sweep: tune on the first half of history, check on the second half.

A setting only counts as good if it holds up out-of-sample (OOS) and across many coins;
the best in-sample number on its own is just curve fitting.

    python sweep.py --tf 1h --days 730
"""
from __future__ import annotations

import argparse
import itertools
from concurrent.futures import ProcessPoolExecutor

import numpy as np
import pandas as pd

from amd_engine import Params, run
from backtest import UNIVERSE
from data import klines, to_arrays

GRID = {
    "entry_level": ["Value area edge", "POC", "Range edge"],
    "entry_mode": ["Confirmation", "Limit"],
    "tp_r": [2.0, 3.0],
    "disp_vol_mult": [0.0, 1.5],
    "range_max_atr": [3.0, 4.0, 5.0],
}

DATA = {}


def _load(tf, days):
    for s in UNIVERSE:
        df = klines(s, tf, days)
        DATA[s] = (to_arrays(df), df["time"].to_numpy())


def _eval(args):
    combo, split = args
    p = Params(**combo)
    r_is, r_oos, coins_pos = [], [], 0
    for s, (a, times) in DATA.items():
        res = run(a["open"], a["high"], a["low"], a["close"], a["volume"], p)
        rs = [(times[t.entry_bar], t.r_net) for t in res.trades]
        coin_r = sum(r for _, r in rs)
        coins_pos += coin_r > 0
        r_is += [r for tm, r in rs if tm < split]
        r_oos += [r for tm, r in rs if tm >= split]

    def m(x):
        x = np.array(x)
        return (len(x), x.mean() if len(x) else np.nan, x.sum())
    n1, a1, t1 = m(r_is)
    n2, a2, t2 = m(r_oos)
    return {**combo, "IS_n": n1, "IS_avgR": a1, "IS_R": t1, "OOS_n": n2, "OOS_avgR": a2,
            "OOS_R": t2, "coins_pos": coins_pos}


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--tf", default="1h")
    ap.add_argument("--days", type=int, default=730)
    args = ap.parse_args()
    _load(args.tf, args.days)
    all_times = np.concatenate([t for _, t in DATA.values()])
    split = np.sort(all_times)[len(all_times) // 2]
    keys = list(GRID)
    combos = [dict(zip(keys, vals)) for vals in itertools.product(*GRID.values())]
    with ProcessPoolExecutor() as ex:
        out = list(ex.map(_eval, [(c, split) for c in combos]))
    df = pd.DataFrame(out).sort_values("IS_avgR", ascending=False)
    pd.set_option("display.width", 200)
    print(f"split at {pd.Timestamp(split)}  |  {len(combos)} combos\n")
    print(df.to_string(index=False, float_format=lambda x: f"{x:.3f}"))
    df.to_csv(f"results/sweep_{args.tf}.csv", index=False)
