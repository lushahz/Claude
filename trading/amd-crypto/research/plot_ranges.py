"""Draw candles + every detected accumulation range, to eyeball the detector.

    python plot_ranges.py ALGOUSDT 2026-09-20 2026-09-23 out.png
"""
import sys

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
from matplotlib.patches import Rectangle

from amd_engine import Params, htf_trend, run
from data import bulk_klines


def plot(sym, start, end, out, p=None, title=""):
    df = bulk_klines(sym, "5m", ["2026-08", "2026-09"])
    times = df["time"].dt.tz_localize(None).to_numpy()
    a = {k: df[k].to_numpy(float) for k in ("open", "high", "low", "close", "volume")}
    res = run(a["open"], a["high"], a["low"], a["close"], a["volume"], p or Params(range_len=30, range_max_atr=6.0), htf_trend(times, a["close"]))
    i0 = np.searchsorted(times, np.datetime64(start))
    i1 = np.searchsorted(times, np.datetime64(end))
    fig, ax = plt.subplots(figsize=(22, 7), dpi=80)
    fig.patch.set_facecolor("#131722"); ax.set_facecolor("#131722")
    for i in range(i0, i1):
        o, h, l, c = a["open"][i], a["high"][i], a["low"][i], a["close"][i]
        col = "#26a69a" if c >= o else "#ef5350"
        ax.plot([i, i], [l, h], color=col, lw=0.7)
        ax.add_patch(Rectangle((i - 0.35, min(o, c)), 0.7, max(abs(c - o), 1e-12), color=col))
    for (s, e, top, bot, poc, vah, val) in res.ranges:
        if e < i0 or s > i1:
            continue
        ax.add_patch(Rectangle((s, bot), e - s + 1, top - bot, fill=False, ec="#ffeb3b", lw=1.2))
        ax.plot([s, e + 1], [poc, poc], color="#ff1744", lw=1)
    for t in res.trades:
        if i0 <= t.entry_bar <= i1:
            ax.scatter([t.entry_bar], [t.entry], marker="^" if t.direction == 1 else "v", s=120, color="#00e5ff", zorder=5)
    ax.set_xlim(i0, i1); ax.set_ylim(a["low"][i0:i1].min() * 0.998, a["high"][i0:i1].max() * 1.002)
    ax.tick_params(colors="#b2b5be"); ax.set_title(f"{sym} 5m {start} → {end}  {title}", color="white")
    step = max(1, (i1 - i0) // 12)
    ax.set_xticks(range(i0, i1, step)); ax.set_xticklabels([str(times[i])[5:16] for i in range(i0, i1, step)], fontsize=8)
    fig.tight_layout(); fig.savefig(out); print("saved", out, "ranges in view:", sum(1 for r in res.ranges if not (r[1] < i0 or r[0] > i1)))


if __name__ == "__main__":
    plot(*sys.argv[1:5])
