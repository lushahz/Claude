# Crypto reversal research (2014-2026)

This study is the basis for **`reversal-dots-crypto.pine`**. It starts from the
general daily triggers in [`REVERSAL_RESEARCH.md`](REVERSAL_RESEARCH.md) and
asks what's different about crypto, including whether **TOTAL, BTC dominance
and USDT dominance** help.

Not financial advice. Past results don't predict future results.

## 1. Data

- **29 coins**, daily, from listing to October 2026 (Yahoo Finance): BTC, ETH,
  XRP, LTC, ADA, SOL, DOGE, BNB, LINK, DOT, AVAX, XLM, TRX, BCH, ATOM, ETC,
  HBAR, NEAR, AAVE, ALGO, FIL, XMR, DASH, ZEC, EOS, XTZ, MANA, SAND, VET. This
  includes coins that later faded (EOS, DASH, XTZ, ETC), so the results don't
  rely only on winners.
- **TOTAL and BTC dominance**: CoinMarketCap daily global metrics, 2013-2026
  (the source behind TradingView's `CRYPTOCAP` series; TOTAL on Oct 3, 2026 =
  $2.87T).
- **USDT dominance**: USDT market cap (Coin Metrics) / TOTAL.
- In-sample **2014-2021**, out-of-sample **2022-2026**. Costs 0.15% per side
  (fee + slippage). Long only, enter on the next day's open.

## 2. What's different about crypto bottoms and tops

From 328 major crypto bottoms and 311 tops (swings of 27-62% depending on the
coin):

| | Crypto bottoms | Ordinary days |
|---|---|---|
| RSI <= 30 | 55% | 4% |
| Slow wave <= -60 | 72% | - |
| Close >= 3 ATRs below the 50 EMA | 80% | 12% |
| Volume spike (z > 2) | **14%** | 19% |

| Altcoin bottoms | Share | Ordinary days |
|---|---|---|
| Bitcoin RSI <= 40 | **74%** | 18% |
| Bitcoin slow wave <= 0 | 83% | 47% |
| Bitcoin below its 200 EMA | 87% | 42% |

- **Altcoins bottom when Bitcoin is weak.** Bitcoin's RSI was at or below 40
  at 74% of altcoin bottoms, a 4x enrichment over ordinary days.
- **Crypto bottoms are quiet, tops are loud.** Volume spikes are *rarer* than
  normal at bottoms but common at tops (median volume z-score +2.4 at tops), the
  opposite of stocks.
- **Crypto bottoms are more stretched**: a median of 4 ATRs below the 50 EMA
  (3.6 across all markets).

## 3. Where the general daily rules lose money in crypto

General daily rules (BUY -> TAKE-PROFIT) on the 29 coins:

| Period | Trades | Win rate | Avg trade | Worst trade | Profit factor |
|---|---|---|---|---|---|
| 2014-21 | 159 | 58% | +25% | -84% | 2.89 |
| 2022-26 | 199 | 54% | +15% | -87% | 1.99 |

The losses cluster in **bear-market years**: 2018 (profit factor 0.36) and
2022 (0.13). Almost every -70% to -85% trade bought the **first dip after a
cycle top** (May 2018, Dec 2021 to Jan 2022, Oct 2025) and then held for 1-2
years as the coin kept falling.

**Stops don't fix this.** On 2022-2026, trailing stops of 3-6 ATRs gave
profit factors of 0.6-1.1, and a fixed 3-ATR stop gave 1.45. They cut real
reversals early, and the next buy usually came lower.

## 4. Testing TOTAL, BTC dominance and USDT dominance

All on top of the general rules plus "altcoins need Bitcoin RSI <= 40".
Profit factor, in-sample / out-of-sample:

| Idea | 2014-21 | 2022-26 | Verdict |
|---|---|---|---|
| Baseline | 3.13 | 2.19 | |
| **Altcoins only when BTC.D is below its 20 EMA** | 2.97 | **3.01** | Helps, smaller losses in both periods |
| Altcoins only when BTC.D RSI <= 60 | 3.51 | 2.31 | Small help |
| Buy only after a USDT.D fear spike (RSI >= 65 / 70) | 3.61 / 4.98 | 1.69 / 1.96 | Fails out of sample |
| Buy only while USDT.D is above its 50 EMA | 3.28 | 1.69 | Fails out of sample |
| Buy only when TOTAL RSI <= 35 | 3.99 | 1.76 | Fails out of sample |
| Cycle guard on TOTAL instead of Bitcoin | 1.23 | 2.09 | Worse |
| Exit when USDT.D crosses above its 200 EMA (with the guard's skip zone) | 4.28 | 1.24 | Fails out of sample |
| Exit when USDT.D 50 EMA crosses above its 200 EMA (with the guard's skip zone) | 3.21 | 1.76 | Fails out of sample |
| Extra take-profit on USDT.D greed (RSI <= 30) | 2.79 | 2.12 | Slightly worse |

- **BTC dominance helps.** Buying altcoins only while BTC.D is falling (money
  rotating into alts) improved results on the unseen 2022-2026 data and
  reduced the worst losses.
- **USDT dominance and TOTAL looked great on 2014-2021 but failed on
  2022-2026.** In the 2022 bear market, USDT.D spiked again and again while
  prices kept falling, so "fear spikes" weren't bottoms. USDT.D also drifts
  up over time as USDT grows (0.6% in 2018 to about 7% in 2026), which makes
  fixed levels unreliable.
- The indicator still **shows TOTAL and USDT.D in the market panel** as
  context. They just don't change any signal.

## 5. Cycle guard

Two Bitcoin-based rules that target the "first dip after a top" trap:

1. **Pause new buys while Bitcoin is 25-60% below its 365-day high.** A pullback
   of less than 25% is a normal bull-market dip, and more than 60% is late-bear
   capitulation. Both are fine to buy. The zone in between is where most of the
   worst trades started.
2. **Cycle exit:** end the trade when Bitcoin's 50 EMA crosses below its
   200 EMA.

Sensitivity check (guard zone start 15-30%, end 50-70%, all with the cycle
exit): 2022-26 profit factor was 2.2-4.3 in every setting versus 2.19 without
it, and the worst 10% of trades improved from -50% to between -29% and -39%. 2014-21 was
noisier (1.1-6.8) because of the small number of trades, so the guard is mainly
a **risk** tool, not a profit booster.

## 6. Final crypto rules

**BUY:**
1. General daily trigger: green dot, slow wave <= -53 (last 3 days),
   RSI <= 40 (last 5 days), close >= 2 ATRs below the 50 EMA (last 10 days),
   bullish confirming close within 3 days, re-arm on a lower low.
2. Altcoins only: Bitcoin RSI <= 40 in the last 10 days.
3. Altcoins only: BTC dominance below its 20 EMA.
4. Cycle guard: Bitcoin not 25-60% below its 365-day high.

**TAKE-PROFIT:** overbought (slow wave >= 53 and RSI >= 70) in the last 15 days,
then the first close below the 20 EMA.

**CYCLE EXIT:** Bitcoin 50 EMA crosses below its 200 EMA.

## 7. Results (29 coins, after costs)

| Rules | Period | Trades | Win rate | Avg trade | Worst 10% | Worst | Profit factor |
|---|---|---|---|---|---|---|---|
| General daily | 2014-21 | 159 | 58% | +25.2% | -53% | -84% | 2.89 |
| General daily | 2022-26 | 199 | 54% | +15.0% | -48% | -87% | 1.99 |
| **Crypto** | 2014-21 | 46 | 65% | +34.7% | -35% | -49% | **4.83** |
| **Crypto** | 2022-26 | 117 | 50% | +23.8% | -30% | -54% | **3.44** |

| Crypto rules | Period | Trades | Profit factor |
|---|---|---|---|
| Bitcoin | 2014-21 | 8 | 8.4 |
| Bitcoin | 2022-26 | 5 | 2.8 |
| Altcoins | 2014-21 | 38 | 4.4 |
| Altcoins | 2022-26 | 112 | 3.5 |

About **0.7 trades per coin per year**.

Recent signals to check against your chart (Yahoo data; TradingView feeds
can shift a day):

| Coin | Signals |
|---|---|
| BTC | BUY 2024-06-27 -> TAKE-PROFIT 2024-11-04; BUY 2025-03-01 -> TAKE-PROFIT 2025-05-30; BUY 2025-11-09 -> CYCLE EXIT 2025-11-17 |
| ETH | BUY 2024-07-08 -> TAKE-PROFIT 2024-12-18; BUY 2025-03-02 -> TAKE-PROFIT 2025-08-01 |
| XRP | BUY 2024-06-30 ($0.48) -> TAKE-PROFIT 2024-12-21 ($2.24) |
| SOL | BUY 2024-06-24 -> TAKE-PROFIT 2024-08-01; BUY 2025-02-28 -> TAKE-PROFIT 2025-07-30 |

## 8. More signals: pullback buys (3-5 per year)

Major bottoms only happen about 2-3 times a year per coin, and with one trade
at a time (~3-month holds) the reversal rules give about 0.7 trades per coin
per year. Ways to reach 3-5, tested the same way:

| Approach | Signals per coin-year (2014-21 / 2022-26) | Profit factor (2014-21 / 2022-26) | Verdict |
|---|---|---|---|
| Current reversal buys only, every signal counted | 0.7 / 1.5 | 4.45 / 2.63 | Too few |
| Turn the cycle guard off | 1.8 / 2.6 | 2.91 / 1.74 | Worst trade -78% |
| Looser reversal (waves -45, RSI 45, 1.5 ATR) | 1.0 / 2.2 | 2.27 / 2.15 | Still too few |
| Faster take-profit (EMA 10 / lighter overbought) | ~2 | 0.7-1.1 out of sample | Loses money |
| Stops on pullback buys (below the dip or the 200 EMA) | - | 0.8-1.1 out of sample | Loses money |
| **Reversal + pullback buys, every signal counted** | **4.4 / 3.9** | **3.38 / 2.09** | **Chosen** |

**Pullback BUY** (light green): coin above its 200 EMA with the 50 EMA above the
200 EMA, a green dot after the slow wave dipped to -20 or lower and RSI to 50
or lower, then a bullish confirming close within 3 days. Altcoins also need
Bitcoin above its 200 EMA. It uses the same take-profit and cycle exit.

| Signal | Period | Signals | Win rate | Avg | Worst 10% | Worst | Profit factor |
|---|---|---|---|---|---|---|---|
| Reversal buy | 2014-21 | 62 | 66% | +29.0% | -33% | -49% | 4.45 |
| Reversal buy | 2022-26 | 200 | 50% | +15.5% | -30% | -54% | 2.63 |
| Pullback buy | 2014-21 | 324 | 62% | +31.8% | -49% | -72% | 3.26 |
| Pullback buy | 2022-26 | 343 | 52% | +10.5% | -40% | -67% | 1.85 |

- **Median of 4 signals per coin per year.** 76% of coin-years get 3 or
  more; almost none get zero.
- Every buy is shown, also while a trade is open. Each one is counted as its
  own entry (like adding to a position). The strategy does the same with up to
  5 entries of 20% each.
- **Weak spots:** 2019 and 2023 lost money overall (profit factors 0.71 and
  0.52). Late 2025 had a cluster of losing pullback buys on ETH and SOL near
  the cycle top (-23% to -39%). Pullbacks are the weaker signal, so they get the
  lighter arrow.

## 8. Honest caveats

- **Only about 3 full crypto cycles** are in the data. The guard and the BTC.D
  filter fit those cycles; the next one can be different.
- **The guard skips some good bounces.** After the October 2025 top it paused
  BTC buys, so it skipped the June-July 2026 bottom, which then rallied about 45%. It
  resumes when Bitcoin gets within 25% of its 1-year high or falls more than
  60% below it.
- **Bad years still happen:** 2021 and 2023 had whipsaws (profit factors 0.12
  and 0.19).
- **Bitcoin itself has few trades** (13 in 12 years). Most of the statistics
  come from altcoins.
- **Coin list bias**: coins that died completely aren't in the data, so real
  altcoin results would be somewhat worse.
- **Data sources**: rebuilt USDT.D and the Yahoo / CoinMarketCap feeds can
  differ slightly from TradingView's.


## Trade levels on the oscillator: which timeframe? (Entry / SL / TP1 / TP2 / TP3)

`reversal-dots-oscillator.pine` can draw a trade for each signal: entry at the next bar's open,
SL below the lowest low of the last 10 bars minus 0.25 ATR, and TP1 / TP2 / TP3 at 1x / 2x / 3x the risk,
closing one third at each. Tested on Binance spot data for 12 coins (BTC, ETH, SOL, BNB, XRP, ADA, DOGE,
LINK, AVAX, LTC, DOT, TRX), 2020 to Sep 2026, with 0.1% round-trip costs. Code: `research/crypto/tftest.py`.

| Chart (panel HTF) | Longs, big buys, SL to entry after TP1 | Win % | Profit factor | Trades per coin per year |
|---|---|---|---|---|
| **1D (weekly)** | 2020-22: PF 1.42, 2023-26: PF 1.53 | **59%** | **1.48** | about 4 |
| 4H (daily) | 2020-22: 1.09, 2023-26: 1.09 | 53% | 1.09 (1.03 at 0.2% costs) | about 25 |
| 1H (4H) | 2020-22: 0.92, 2023-26: 0.79 | 48% | 0.83 | about 200 |

- **The daily chart worked best**, with 10 of 12 coins net positive (DOGE and AVAX were the losers). At 0.2% costs it still had PF 1.45.
- Without moving the SL to entry after TP1: 43% wins but PF 1.62 (all 12 coins positive).
- Confirmation buys on 1D: 55% wins, PF 1.38. Setup arrows (HTF filtered): 57%, PF 1.32.
- **Shorts lost money on every timeframe** (best 1D short PF 0.88), so the trade levels default to longs only.
- 1H and below lose to fees; 4H is roughly break-even after realistic costs.
