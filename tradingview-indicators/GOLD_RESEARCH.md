# Gold 5-minute scalping research (XAUUSD, 2009-2026)

The study behind [`gold-5m-scalper.pine`](gold-5m-scalper.pine). Code: [`research/gold/`](research/gold/).

**Short version: after trading costs, no 5-minute gold setup made money reliably across 2009-2026.**
Every indicator we tried carries a little information. That edge is about the
size of the spread, and costs remove it. The indicator uses the two setups that held
up best: they lost money before 2020 and made a small profit from 2020 on. Results swing
widely from year to year. Treat the indicator as a filter and a source of ideas, not
as a money machine. Test it on your broker's prices and spread before risking money.

## Data

| Market | Source | 5m bars | From |
|---|---|---|---|
| XAUUSD (spot gold) | HistData.com 1-minute, converted to UTC | 1,237,617 | Mar 2009 |
| XAGUSD (silver) | HistData.com | 1,218,050 | May 2009 |
| EURUSD, USDJPY, GBPUSD, USDCAD, USDSEK, USDCHF | HistData.com | ~1.31 million each | Jan 2009 |
| SPXUSD (S&P 500 CFD) | HistData.com | 1,063,290 | Nov 2010 |

The six currency pairs are combined with the official ICE weights into a
**synthetic US Dollar Index (DXY)**. Data ends 25 Sep 2026.

## How every test was scored

- Session: London + New York, **07:00-16:00 UTC** (as requested), both long and short
- Entry at the **next bar's open** after the signal bar closes (no look-ahead)
- Exit: ATR-based stop and target, a time limit, and flat at the session end. When the stop
  and target fall in the same bar, the stop counts (pessimistic).
- One trade at a time
- Costs: **$0.30/oz round trip** (typical spread + commission), also tested at $0.20 and $0.50
- Periods: 2009-2019 (in-sample), 2020-2022 (validation), 2023-2026 (out-of-sample), 2025-2026 (recent)
- PF = profit factor (gross wins / gross losses). Above 1 = profitable.

## Features tested (about 75)

- **Trend:** EMA 9/21/50/200 distance and stack, MACD, ADX/DI, Supertrend
- **Oscillators:** RSI 14/7, Stochastic, WaveTrend, CCI
- **Bands and channels:** Bollinger, Keltner, Donchian
- **Candles:** close location, body, wicks, range, momentum (3 and 12 bars)
- **Volatility:** ATR, ATR vs. its daily average, shock bars (news proxy)
- **Levels:** session TWAP, prior-day high/low/close, pivot, day high/low so far,
  Asian-session range, $10 and $50 round numbers
- **Time:** UTC hour, New York time (daylight-saving aware), weekday
- **Higher timeframes:** 15m, 1h and 4h trend, distance from the 50 EMA, RSI and WaveTrend
  (completed bars only)
- **Cross-asset:** US Dollar Index moves; gold-vs-dollar rolling beta and residual; silver
  moves, gold/silver ratio and silver lead; S&P 500 moves

## What we found

### 1. Each indicator alone barely predicts the next hour

The rank correlation of any single feature with the next 12 bars is at most 0.04.

- **Oscillators** (WaveTrend, RSI, Bollinger %B, CCI, distance from EMA21) show mild
  **mean reversion**: stretched up tends to drift down. The sign is the same in every period,
  but the effect is weaker after 2020.
- **The 4-hour trend** helps a little (positive before 2020, weaker after).
- **Gold vs. the dollar** is the most stable cross-asset effect. When gold moves more than the
  dollar explains, it tends to snap back (-0.035 / -0.028 / -0.018 for the three periods).
  When silver has moved and gold has not, gold tends to follow (+0.020 / +0.009 / +0.009).
- **The S&P 500 and the raw dollar move** carry no stable information for gold at 5 minutes.

### 2. Time of day

The average next-5-minute move by New York time shows two consistent effects:
- **05:00-06:59 NY** (London morning) drifts **down** in every period.
- **11:00 NY** (the London close / London PM fix area) drifts **up** in every period.

Both effects are far smaller than the spread.

### 3. Rule families after $0.30 costs (stop 1.5 ATR, target 2 ATR, 36 bars)

| Family | 2009-19 PF | 2020-22 PF | 2023-26 PF | 2025-26 PF |
|---|---|---|---|---|
| Mean reversion (oscillator extreme + trigger, with/without HTF trend) | 0.65-0.80 | - | 0.72-0.93 | - |
| London breaks Asian range + 4h trend | <1 | 0.92 | 1.09 | 1.33 (108 trades) |
| NY opening-range breakout (trailing stop) | <1 | - | 1.03 | 1.06 |
| Supertrend flip + 4h trend | <1 | - | 0.98 | 1.02 |
| EMA21 pullback in full EMA stack + 4h | <1 | - | - | 1.00 |
| **Gold-vs-dollar divergence + silver + 4h** (2.5 sigma) | 0.83 | 0.93 | 1.02 | 1.05 |

**Before costs**, most families sit at a PF of 0.95-1.12. Costs cut about 0.2-0.3 off the
PF when gold's 5m ATR is around $1.

### 4. Why the recent years look better: volatility, not a new edge

Gold's median 5-minute ATR by year ($):

| 2009 | 2012 | 2015 | 2017 | 2019 | 2020 | 2022 | 2024 | 2025 | 2026 |
|---|---|---|---|---|---|---|---|---|---|
| 0.86 | 1.11 | 0.78 | 0.61 | 0.73 | 1.62 | 1.40 | 1.66 | 2.96 | 5.38 |

The cost is fixed in dollars, so it shrinks relative to each move when ATR is high. Split
by ATR at entry (instead of by year), every family's PF rises with ATR. Below about $1.5 ATR,
every family lost money. So the "edge" in 2025-26 is mostly the cost becoming small,
not the setups getting smarter.

### 5. Machine learning on everything

We trained gradient-boosted trees on all ~75 features, with walk-forward testing: retrain each
year on all earlier years, then test on the next year only (2013-2026). The models predict
long and short trade outcomes in R after costs.

- The ranking information is real (rank correlation 0.07-0.30 by year). But it mostly learns
  **which bars lose less**: low volatility means costs hurt more.
- The model's **top 2% of picks still lost money on average in 10 of 14 years for longs and 11 of 14 for shorts**.
- Trading the model with any threshold: PF 0.80-0.93 (2013-19) and 0.88-0.97 (2020-22).
  For 2023-26 it was 0.85-1.02, and never reliably above 1.

Even a model that sees everything does not find a reliable 5-minute gold edge after costs.

## The indicator's rules (best of what survived)

1. **Divergence snap.** In the last 3 bars, gold's 12-bar move not explained by the dollar
   (residual from a rolling 1-day beta) went beyond **2.5 sigma**. Silver agrees: silver
   lead > 0 for a buy, < 0 for a sell. The 4-hour trend is not against the trade.
   Then a reversal candle closes in the top 40% (buy) or bottom 40% (sell) of its range.
2. **London break.** The first close above the Asian high (17:00-03:00 NY) between 03:00 and
   06:00 NY, with the 4-hour trend up. Mirror for sells.
3. **Filters:** 07:00-16:00 UTC session, and 5m **ATR at least $2.0** (the volatility gate).
4. **Exit:** stop 1.5 ATR, target 2 ATR, at most 36 bars (3 hours), flat at session end.

### Backtest of exactly these rules

| Costs | 2009-19 | 2020-22 | 2023-26 | 2025-26 |
|---|---|---|---|---|
| $0.20 | PF 0.88 (303 trades) | **1.09** (324) | **1.13** (417) | **1.15** (286) |
| $0.30 | 0.83 | **1.04** | **1.10** | **1.13** |
| $0.50 | 0.75 | 0.95 | **1.05** | **1.08** |

Win rate is 44-48%; the average winner is about 1.25x the average loser.
About 1.3-1.6 signals per active day, and none on quiet days.

Year by year at $0.30 (net $ per 1 oz per trade summed):

| 2020 | 2021 | 2022 | 2023 | 2024 | 2025 | 2026 (to Sep) |
|---|---|---|---|---|---|---|
| +30 (PF 1.10) | -79 (0.67) | +75 (1.52) | -5 (0.91) | +2 (1.01) | **-164 (0.79)** | **+320 (1.71)** |

Without the volatility gate, 2009-2019 is PF 0.78 at $0.30 over 2,120 trades.

**Honest reading:** this is close to breakeven, with long losing streaks. 2025 lost
money, and most of the recent profit comes from 2026's very large moves. Nothing here
reliably beats costs, so trade it small or use it as a filter for your own discretion.

## What to do with it

- Use it on a **5-minute XAUUSD chart** during London and New York.
- Check the **dashboard scorecard**. It replays every signal on your chart's history with
  your cost setting. If it shows PF < 1 on your broker's feed, don't trade it.
- Lower spread matters more than any setting: at $0.20 round trip every recent
  period is profitable; at $0.50 most are not.
- Not financial advice.
