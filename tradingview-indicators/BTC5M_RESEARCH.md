# BTC 5-minute reversal research (2020 - Aug 2026)

The study behind [`btc-5m-reversal-dots.pine`](btc-5m-reversal-dots.pine). Code: [`research/btc5m/`](research/btc5m/).

**Goal:** a Reversal-Dots-style indicator for BTC on the 5-minute chart with a win rate of at least 60%,
**and** profitable after fees (a high win rate alone is easy and meaningless).

**Result:** found. 66% wins over 1,001 trades. It was profitable before fees in every year from 2020 to 2026, and
it held up on 2025-26 data that was hidden during development (69% wins). The edge is thin, so **fees decide
everything**: profitable at up to about 0.06% round trip, break-even around 0.07%, losing at 0.08% and above.

## Data

Binance public archives, 700,818 five-minute bars, Jan 2020 - Aug 2026:
BTCUSDT spot candles (with taker-buy volume), ETHUSDT spot, BTCUSDT perpetual futures candles,
premium index and funding rate. 62 features per bar: WaveTrend, Stoch RSI, RSI, divergences, EMA distances,
Bollinger, candle shape, order flow (taker buy share, cumulative delta, spot and futures), daily VWAP, day and
prior-day highs/lows, basis, premium, funding, ETH relative strength, time of day, and 15m / 1h / 4h / 1D waves,
RSI and trend from completed bars only.

## Method

- Trades enter at the **next bar's open** after the signal bar closes. When stop and target fall in the same
  bar, the **stop counts** (pessimistic). One trade at a time.
- Costs as % round trip: 0, 0.02, 0.04, 0.06, 0.08, 0.10.
- Development data 2020-2024. **2025-26 was held out** and used once, for two candidates fixed in advance.

## What we found

1. **Short-term mean reversion is real on BTC 5m.** Every oscillator (RSI, Bollinger %B, distance from the
   20/50 EMA, WaveTrend) predicts the next hour with a negative sign, consistently in 2020-21, 2022-23 and
   2024-26 (rank correlation -0.04 to -0.08). Aggressive taker buying or selling also tends to reverse.
   Time of day showed no stable pattern.
2. **A 60%+ win rate is easy; profit is not.** With the stop wider than the target, reversal signals win
   65-80%, but the average 5m move (about 0.2% of price) is close to typical fees.
3. **Machine learning on all 62 features did not add a usable edge** (best 5% of picks: PF 1.04-1.25 before fees,
   below 1 at 0.04%).
4. **The early turn of the fast wave in deep oversold / overbought** (wt2 at or beyond +/-60) was the most robust signal.
   With SL 3 ATR / TP 1 ATR it was profitable before fees in all five development years.
5. Filters that helped **in every year**: **price near the UTC day's low (for buys) or high (for sells)**,
   order-flow exhaustion, and the 4-hour trend not being against the trade. A minimum volatility of **ATR >= 0.20%
   of price** keeps fees small relative to the move.

## Hold-out test (2025-26, run once)

| Candidate | Dev 2020-24 win / PF (0.04%) | **Hold-out 2025-26 win / PF (0.04%)** |
|---|---|---|
| A: early turn + order-flow exhaustion + 4h trend + premium extreme | 75% / 1.40 (151 trades) | 71% / 0.98 (42 trades) - dropped |
| **B: early turn near the day's low / high** | 74% / 1.09 (828 trades) | **78% / 1.24 (197 trades)** |

The TP1/TP2/TP3 split was then chosen on 2020-24 data only (best PF): **TP1 1.0 ATR (50%), TP2 1.5 ATR (25%),
TP3 2.5 ATR (25%), SL 4 ATR fixed**, close after 72 bars.

## The indicator's exact rules and results

- **BUY:** fast wave turns up below the slow wave, slow wave <= -60, close within 1 ATR of the UTC day's low,
  5m ATR >= 0.12% of price (default since Oct 2026; was 0.20%). **SELL:** the mirror image near the day's high.
- Entry next bar open, SL 4 ATR, TP1 1.0 / TP2 1.5 / TP3 2.5 ATR (50 / 25 / 25%), close after 72 bars.

| Round-trip cost | Win % | Profit factor 2020-24 | Profit factor 2025-26 (hold-out) |
|---|---|---|---|
| 0% | 66% | 1.24 | 1.32 |
| 0.02% | 66% | 1.17 | 1.22 |
| **0.04%** | **66%** | **1.10** | **1.13** |
| 0.06% | 66% | 1.03 | 1.04 |
| 0.08% | 65% | 0.97 | 0.96 |
| 0.10% | 65% | 0.91 | 0.88 |

At 0.04%, year by year: 2020 PF 1.14, 2021 1.26, 2022 0.90, 2023 1.10, 2024 1.03, 2025 0.98, 2026 (to Aug) 1.48.
Win rate was 63-72% in every year. Longs PF 1.15, shorts 1.06. About 2.9 trades a week. Average win +0.49%,
average loss -0.86% (per unit, before leverage). Longest losing streak: 6. TP1 is reached in 82% of trades.

## Honest reading

- **The win rate target is met** (66% overall, at least 63% in every year), but the profit per trade is small:
  about +0.03% at 0.04% fees.
- **Use the lowest fees you can get**: futures maker (limit) orders or a zero-fee BTC pair. With standard
  0.1% spot fees on each side (0.2% round trip) it loses money.
- Losses are larger than wins (0.86% vs 0.49%), so a short losing run hurts. Two of seven years were slightly
  negative at 0.04% fees.
- Signals were chosen from many tested combinations; the 2025-26 hold-out is the main protection against
  over-fitting, and it held. Live results can still be weaker. Test it on your own exchange in the Strategy
  Tester before trading real money.

## Update (Oct 2026): volatility minimum lowered to 0.12%

BTC was very calm in Aug-Sep 2026 (median 5m ATR 0.07-0.15% of price), so the 0.20% minimum blocked most
signals (0-2 a week). Lowering it barely changed the results (code: `research/btc5m/gate.py`):

| Min ATR | Signals/week 2025-26 | Win % 2025-26 | PF at 0.04%, 2020-24 / 2025-26 |
|---|---|---|---|
| 0.20% | 2.2 | 69% | 1.10 / 1.13 |
| **0.12% (default)** | 4.2 | 70% | 1.08 / 1.12 |
| 0.10% | 4.7 | 69% | 1.06 / 1.08 |
| off | 6.2 | 67% | 1.06 / 1.01 |
