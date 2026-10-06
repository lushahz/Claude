"""Reference implementation of the AMD + Volume Profile model.

This is a bar-by-bar port of the state machine in ../pine/AMD_Volume_Profile_Crypto.pine.
Keep the two in sync: every rule here has a matching block in the Pine file, so
results from this backtester describe what the TradingView script draws.

Long setup (shorts are the mirror image):
  1. ACCUMULATION  a tight range: `range_len` bars whose high-low <= `range_max_atr` x ATR(100).
                   A volume profile over the range gives POC / VAH / VAL.
  2. MANIPULATION  price trades below the range low (a sweep), no deeper than
                   `sweep_max_depth` x range height, and closes back inside within
                   `max_manip_bars` bars.
  3. DISTRIBUTION  a displacement candle closes above the breakout level (range high by
                   default) with body >= `disp_body_atr` x ATR and volume >=
                   `disp_vol_mult` x its 20-bar average.
  4. PULLBACK      price comes back to the entry level (VAH by default).
  5. SIGNAL        a bullish candle closes back above the entry level (confirmation mode),
                   or a resting limit at the level fills (limit mode).
  Stop below the pullback low (confirmation) or the next value level (limit); target at
  `tp_r` x risk; optional exit when price is accepted back inside value.
"""
from __future__ import annotations

from dataclasses import dataclass, field

import numpy as np

SEARCH, RANGE, MANIP, DISP_WAIT, DISPLACED, TOUCHED, IN_TRADE = range(7)
STATE_NAMES = ["Searching", "Range", "Manipulation", "Waiting displacement",
               "Waiting pullback", "Waiting confirmation", "In trade"]


@dataclass
class Params:
    range_len: int = 30
    range_max_atr: float = 5.0
    atr_long_len: int = 100
    atr_len: int = 14
    vp_rows: int = 40
    va_pct: float = 70.0
    max_range_bars: int = 200
    sweep_max_depth: float = 1.0      # x range height
    max_manip_bars: int = 8
    max_disp_bars: int = 30
    require_manip: bool = True
    break_level: str = "Range edge"   # "Range edge" | "Value area edge"
    disp_body_atr: float = 1.0
    disp_vol_mult: float = 1.5        # 0 disables the volume check
    entry_level: str = "Value area edge"  # "Value area edge" | "POC" | "Range edge"
    entry_mode: str = "Confirmation"  # "Confirmation" | "Limit"
    touch_tol_atr: float = 0.25
    max_pullback_bars: int = 40
    confirm_bars: int = 5
    stop_buffer_atr: float = 0.3
    min_risk_atr: float = 0.5
    max_risk_atr: float = 4.0
    tp_r: float = 2.5
    be_at_r: float = 0.0              # 0 = off
    accept_exit_bars: int = 2         # 0 = off
    direction: str = "Both"           # "Both" | "Long" | "Short"
    fee_pct: float = 0.05             # per side, % of notional (Binance futures taker)
    slip_pct: float = 0.02            # per side


@dataclass
class Trade:
    direction: int
    range_start: int
    range_end: int
    entry_bar: int
    entry: float
    stop: float
    target: float
    exit_bar: int = -1
    exit: float = np.nan
    reason: str = ""
    r_gross: float = np.nan
    r_net: float = np.nan


@dataclass
class Result:
    trades: list[Trade] = field(default_factory=list)
    setups: int = 0          # ranges that got a valid manipulation + displacement


def atr(high, low, close, n):
    prev = np.concatenate([[np.nan], close[:-1]])
    tr = np.where(np.isnan(prev), high - low,
                  np.maximum(high, prev) - np.minimum(low, prev))
    out = np.full_like(close, np.nan)
    if len(close) < n:
        return out
    out[n - 1] = tr[:n].mean()
    a = 1.0 / n
    for i in range(n, len(close)):
        out[i] = out[i - 1] + a * (tr[i] - out[i - 1])
    return out


def sma(x, n):
    out = np.full_like(x, np.nan)
    if len(x) >= n:
        c = np.cumsum(np.insert(x, 0, 0.0))
        out[n - 1:] = (c[n:] - c[:-n]) / n
    return out


def profile_add(rows, bot, top, h, l, v):
    """Distribute bar volume across profile rows in proportion to price overlap."""
    n = len(rows)
    step = (top - bot) / n
    if step <= 0:
        return
    if h - l <= 0:
        idx = min(n - 1, max(0, int((h - bot) / step)))
        rows[idx] += v
        return
    lo_edges = bot + step * np.arange(n)
    ov = np.clip(np.minimum(h, lo_edges + step) - np.maximum(l, lo_edges), 0, None)
    tot = ov.sum()
    if tot > 0:
        rows += v * ov / tot


def value_area(rows, bot, top, va_pct):
    n = len(rows)
    step = (top - bot) / n
    poc_i = int(np.argmax(rows))
    total = rows.sum()
    lo = hi = poc_i
    acc = rows[poc_i]
    target = total * va_pct / 100.0
    while acc < target and (lo > 0 or hi < n - 1):
        up = rows[hi + 1] if hi < n - 1 else -1.0
        dn = rows[lo - 1] if lo > 0 else -1.0
        if up >= dn:
            hi += 1
            acc += up
        else:
            lo -= 1
            acc += dn
    poc = bot + step * (poc_i + 0.5)
    return poc, bot + step * (hi + 1), bot + step * lo   # poc, vah, val


def run(o, h, l, c, v, p: Params) -> Result:
    n = len(c)
    atr_s = atr(h, l, c, p.atr_len)
    atr_l = atr(h, l, c, p.atr_long_len)
    vol_ma = sma(v, 20)
    res = Result()

    state = SEARCH
    search_from = 0
    top = bot = height = poc = vah = val = np.nan
    r_start = r_end = 0
    rows = np.zeros(p.vp_rows)
    d = 0                                  # +1 long, -1 short
    manip_start = reclaim_bar = disp_bar = touch_bar = 0
    manip_ext = pb_ext = np.nan
    entry_lvl = deep_lvl = np.nan
    trade: Trade | None = None
    accept_cnt = 0
    risk = np.nan
    allow_long = p.direction in ("Both", "Long")
    allow_short = p.direction in ("Both", "Short")

    def reset(t):
        nonlocal state, search_from, d
        state, search_from, d = SEARCH, t + 1, 0

    def levels_for(direction):
        # entry level and the "deeper" value level that invalidates the idea
        if direction == 1:
            if p.entry_level == "Range edge":
                return top, vah
            if p.entry_level == "POC":
                return poc, val
            return vah, poc
        if p.entry_level == "Range edge":
            return bot, val
        if p.entry_level == "POC":
            return poc, vah
        return val, poc

    def is_displacement(t, direction):
        a = atr_s[t - 1] if t > 0 else np.nan
        if np.isnan(a):
            return False
        lvl_up = top if p.break_level == "Range edge" else vah
        lvl_dn = bot if p.break_level == "Range edge" else val
        body = abs(c[t] - o[t])
        vol_ok = p.disp_vol_mult <= 0 or (not np.isnan(vol_ma[t - 1]) and v[t] >= p.disp_vol_mult * vol_ma[t - 1])
        if direction == 1:
            return c[t] > lvl_up and c[t] > o[t] and body >= p.disp_body_atr * a and vol_ok
        return c[t] < lvl_dn and c[t] < o[t] and body >= p.disp_body_atr * a and vol_ok

    def open_trade(t, entry, stop, direction, a):
        nonlocal state, trade, accept_cnt, risk
        r = (entry - stop) * direction
        if r < p.min_risk_atr * a:
            stop = entry - direction * p.min_risk_atr * a
            r = p.min_risk_atr * a
        if r > p.max_risk_atr * a or r <= 0:
            reset(t)
            return False
        risk = r
        trade = Trade(direction, r_start, r_end, t, entry, stop, entry + direction * p.tp_r * r)
        accept_cnt = 0
        state = IN_TRADE
        return True

    def close_trade(t, px, reason):
        nonlocal trade
        tr = trade
        tr.exit_bar, tr.exit, tr.reason = t, px, reason
        tr.r_gross = (px - tr.entry) * tr.direction / risk
        cost = (p.fee_pct + p.slip_pct) / 100.0 * (tr.entry + px)
        tr.r_net = tr.r_gross - cost / risk
        res.trades.append(tr)
        trade = None
        reset(t)

    for t in range(n):
        if np.isnan(atr_l[t]) or np.isnan(atr_s[t]):
            continue
        a = atr_s[t]

        # ---- SEARCH: look for a fresh, tight range ------------------------------
        if state == SEARCH:
            s0 = t - p.range_len + 1
            if s0 >= search_from and s0 >= 0:
                hh = h[s0:t + 1].max()
                ll = l[s0:t + 1].min()
                if hh - ll <= p.range_max_atr * atr_l[t] and hh > ll:
                    top, bot, height = hh, ll, hh - ll
                    r_start, r_end = s0, t
                    rows = np.zeros(p.vp_rows)
                    for i in range(s0, t + 1):
                        profile_add(rows, bot, top, h[i], l[i], v[i])
                    poc, vah, val = value_area(rows, bot, top, p.va_pct)
                    state = RANGE
            continue

        # ---- RANGE: extend while inside, otherwise classify the break ------------
        if state == RANGE:
            if h[t] <= top and l[t] >= bot:
                if t - r_start + 1 > p.max_range_bars:
                    state, search_from = SEARCH, t - p.range_len + 2
                    continue
                r_end = t
                profile_add(rows, bot, top, h[t], l[t], v[t])
                poc, vah, val = value_area(rows, bot, top, p.va_pct)
                continue
            if h[t] > top and l[t] < bot:
                reset(t)
                continue
            if not p.require_manip:
                if allow_long and is_displacement(t, 1):
                    d, disp_bar, manip_ext = 1, t, bot
                    entry_lvl, deep_lvl = levels_for(1)
                    state = DISPLACED
                    res.setups += 1
                    continue
                if allow_short and is_displacement(t, -1):
                    d, disp_bar, manip_ext = -1, t, top
                    entry_lvl, deep_lvl = levels_for(-1)
                    state = DISPLACED
                    res.setups += 1
                    continue
            d = 1 if l[t] < bot else -1      # sweep below -> long idea, above -> short idea
            if (d == 1 and not allow_long) or (d == -1 and not allow_short):
                reset(t)
                continue
            manip_start = t
            manip_ext = l[t] if d == 1 else h[t]
            state = MANIP
            # fall through: the sweep bar itself may already close back inside

        # ---- MANIPULATION: sweep must stay shallow and get reclaimed -------------
        if state == MANIP:
            if d == 1:
                manip_ext = min(manip_ext, l[t])
                depth = bot - manip_ext
                back_in = c[t] > bot
            else:
                manip_ext = max(manip_ext, h[t])
                depth = manip_ext - top
                back_in = c[t] < top
            if depth > p.sweep_max_depth * height:
                reset(t)
                continue
            if back_in:
                reclaim_bar = t
                state = DISP_WAIT
                # fall through: the reclaim bar can also be the displacement
            elif t - manip_start + 1 >= p.max_manip_bars:
                reset(t)
                continue
            else:
                continue

        # ---- WAITING DISPLACEMENT ------------------------------------------------
        if state == DISP_WAIT:
            outside = c[t] < bot if d == 1 else c[t] > top
            if outside and t > reclaim_bar:      # lost the range again -> back to manipulation
                manip_ext = min(manip_ext, l[t]) if d == 1 else max(manip_ext, h[t])
                depth = (bot - manip_ext) if d == 1 else (manip_ext - top)
                if depth > p.sweep_max_depth * height:
                    reset(t)
                    continue
                manip_start = t
                state = MANIP
                continue
            manip_ext = min(manip_ext, l[t]) if d == 1 else max(manip_ext, h[t])
            if is_displacement(t, d):
                disp_bar = t
                entry_lvl, deep_lvl = levels_for(d)
                state = DISPLACED
                res.setups += 1
                continue
            if t - reclaim_bar >= p.max_disp_bars:
                reset(t)
            continue

        # ---- WAITING PULLBACK ----------------------------------------------------
        if state == DISPLACED:
            if t - disp_bar > p.max_pullback_bars:
                reset(t)
                continue
            a_prev = atr_s[t - 1]           # known before the bar opens (limit price)
            touched = t > disp_bar and ((l[t] <= entry_lvl + p.touch_tol_atr * a_prev) if d == 1 else
                                        (h[t] >= entry_lvl - p.touch_tol_atr * a_prev))
            if touched and p.entry_mode == "Limit":
                lim = entry_lvl + d * p.touch_tol_atr * a_prev
                fill = min(o[t], lim) if d == 1 else max(o[t], lim)
                stop = deep_lvl - d * p.stop_buffer_atr * a_prev
                if not open_trade(t, fill, stop, d, a_prev):
                    continue
                # conservative: a stop touched on the fill bar counts as a loss
                if (d == 1 and l[t] <= trade.stop) or (d == -1 and h[t] >= trade.stop):
                    close_trade(t, trade.stop, "stop")
                continue
            if (d == 1 and c[t] < deep_lvl) or (d == -1 and c[t] > deep_lvl):
                reset(t)
                continue
            if not touched:
                continue
            touch_bar = t
            pb_ext = l[t] if d == 1 else h[t]
            state = TOUCHED
            # fall through: the touch bar can be the confirmation candle

        # ---- WAITING CONFIRMATION ------------------------------------------------
        if state == TOUCHED:
            pb_ext = min(pb_ext, l[t]) if d == 1 else max(pb_ext, h[t])
            if (d == 1 and c[t] < deep_lvl) or (d == -1 and c[t] > deep_lvl):
                reset(t)
                continue
            confirmed = (c[t] > entry_lvl and c[t] > o[t]) if d == 1 else \
                        (c[t] < entry_lvl and c[t] < o[t])
            if confirmed:
                stop = pb_ext - d * p.stop_buffer_atr * a
                open_trade(t, c[t], stop, d, a)
                continue          # confirmation entries fill at the close; manage from next bar
            if t - touch_bar >= p.confirm_bars:
                reset(t)
            continue

        # ---- IN TRADE --------------------------------------------------------------
        if state == IN_TRADE:
            tr = trade
            if d == 1:
                if l[t] <= tr.stop:
                    close_trade(t, min(o[t], tr.stop), "stop" if tr.stop < tr.entry else "breakeven")
                    continue
                if h[t] >= tr.target:
                    close_trade(t, max(o[t], tr.target), "target")
                    continue
            else:
                if h[t] >= tr.stop:
                    close_trade(t, max(o[t], tr.stop), "stop" if tr.stop > tr.entry else "breakeven")
                    continue
                if l[t] <= tr.target:
                    close_trade(t, min(o[t], tr.target), "target")
                    continue
            if p.accept_exit_bars > 0:
                inside = c[t] < deep_lvl if d == 1 else c[t] > deep_lvl
                accept_cnt = accept_cnt + 1 if inside else 0
                if accept_cnt >= p.accept_exit_bars:
                    close_trade(t, c[t], "accepted back in value")
                    continue
            if p.be_at_r > 0:
                if (d == 1 and h[t] >= tr.entry + p.be_at_r * risk) or \
                   (d == -1 and l[t] <= tr.entry - p.be_at_r * risk):
                    tr.stop = tr.entry
    return res


def stats(trades: list[Trade]) -> dict:
    if not trades:
        return {"trades": 0}
    r = np.array([t.r_net for t in trades])
    eq = np.cumsum(r)
    dd = (np.maximum.accumulate(np.concatenate([[0], eq]))[1:] - eq).max()
    wins = r[r > 0].sum()
    losses = -r[r < 0].sum()
    return {
        "trades": len(r),
        "win_rate": (r > 0).mean() * 100,
        "avg_r": r.mean(),
        "total_r": r.sum(),
        "profit_factor": wins / losses if losses > 0 else np.inf,
        "max_dd_r": dd,
        "longs": sum(t.direction == 1 for t in trades),
        "shorts": sum(t.direction == -1 for t in trades),
    }
