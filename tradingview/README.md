# Reversal Dots Oscillator

`reversal-dots-oscillator.pine` is a TradingView Pine v6 indicator. To use it, paste it into the Pine editor and add it to a **BTC 1D** chart (12H also works).

## Why it gave no sell trades

1. The trade direction defaulted to **Longs only**.
2. The sell signals it could trade (big sells, setup sells) lost money. On BTC 1D, 2017-2026, big sells as shorts made 65 trades, 37% won, -12R. They only checked how high the waves were, and in a bull market a red dot at +53 is usually a pause, not a top.

## The fix: trend setups

The sells that work are the ones where the **weekly fast wave is falling**.

| Signal | Rule (1D chart, weekly HTF) |
|---|---|
| Trend buy | Green dot at or below 0, weekly fast wave rising, weekly slow wave ≤ +20 |
| Trend sell | Any red dot, weekly fast wave falling, weekly slow wave ≥ -20, Binance perp premium above its 30-bar average |

Other changes:

- **Flip**: an opposite setup closes the open trade at the bar close and enters the new one at the next open.
- **Perp premium filter**: takes Binance `BTCUSDT.P` / `BTCUSDT` - 1 and only allows sells when it is above its 30-bar average, meaning longs are crowded. When there is no perp data, the filter is skipped.
- **Panels**: the HTF panel now shows "LONGS / SHORTS / Wait" and the perp premium. The trade panel splits the results into longs and shorts.
- **Alerts**: new "Trend buy" and "Trend sell" alerts. The trade alert says "close the short/long now" on a flip.

## Results

Test conditions: Binance BTCUSDT 1D, Aug 2017 - Oct 2026, entry at the next open, 0.10% round-trip cost.

| Setup | Trades | Win % | PF | Net R | Max DD |
|---|---|---|---|---|---|
| Old default (big buys, longs only) | 51 | 69 | 2.33 | +21.8 | 6.8R |
| Old big signals, longs + shorts | 105 | 49 | 1.04 | +2.2 | 15.5R |
| **New default** (trend setups + flip + premium) | 48 | 71 | 3.38 | +31.2 | 2.1R |
| New, trend setups + big buys | 92 | 69 | 2.78 | +44.8 | 4.5R |

In the new default, shorts made 25 trades with 72% won and +18.0R. Longs made 23 trades with 70% won and +13.2R. Every year from 2017 to 2026 was positive.

Cross-checks with the same rules:

- **BTC 12H**: PF 1.5, +29R.
- **Coinbase BTC-USD 1D, 2015-2026**: PF 1.7.
- **ETH 1D**: PF 1.6.
- **4H and lower**: no reliable edge for either the old or the new version.

### Data that was tested and left out

- **Funding rate**: no consistent effect on the new setups.
- **Coinbase premium**: helped on 1D, hurt on 12H.
- **Open interest, long/short ratios and taker volume** (Binance, 2021+): inconsistent between 1D and 12H, and mostly not available inside TradingView.
- **Fear & Greed**: shorts did better when it was below its median, but TradingView has no Fear & Greed feed.

## Reproduce

```
python3 research/backtest_revdots.py BTCUSDT 1d
```

This downloads public Binance data and prints the table above.

Not financial advice. Past results don't guarantee future ones, and small samples (about 5 trades a year on 1D) can mislead.

---

# RevDots Scalper 5m

`revdots-scalper-5m.pine` is a separate overlay indicator for the **5-minute chart** of BTCUSDT or ETHUSDT perpetuals. It is long-only.

## Signal

All four conditions must hold on the close of a 5-minute bar:

1. **Volatility spike:** 5m ATR(14) is at least 0.7x the 30-day average of the 1-hour ATR(14). That is about 2.5x the usual 5m ATR. The baseline comes from the 1h chart, so it works however many 5m bars your TradingView plan loads.
2. **Deep dip:** price is at least 3 ATR below the daily VWAP.
3. **Oversold:** RSI(14) is below 30.
4. **Uptrend:** the last daily close is above the daily EMA 50.

## Trade

- Entry at the next bar's open.
- Take profit at +1 ATR.
- Emergency stop at -10 ATR.
- Otherwise, exit at the close after 24 bars (2 hours).

## What the 5m research found

Data: Binance perps Jan 2020 - Oct 2026, stops and targets checked on 1-minute data, 0.08% round-trip cost. Models were trained on 2020-22 and checked on 2023 and 2024-26.

- **The 1D logic does not carry over to 5m.** WaveTrend green/red dots on 5m won about 50% of the time before costs and lost after costs, with or without higher-timeframe filters.
- **Most intraday effects are smaller than costs.** Hour of day, opening-range breakouts and plain VWAP distance all move about 1-5 bps, against 8 bps of costs.
- **A model found a long-only edge.** A gradient-boosting model using every feature found an edge for longs only, on unseen years, on both BTC and ETH: buy deep, volatile dips in an uptrend. It found no edge for shorts. The rules above are the transparent version of that model.

| | Trades | Won | Avg/trade | PF | Total (1x) | Max DD |
|---|---|---|---|---|---|---|
| BTCUSDT | 192 | 79.7% | +0.19% | 1.59 | +37% | 16.5% |
| ETHUSDT | 238 | 84.5% | +0.29% | 1.73 | +69% | 25.5% |

BTC average per trade by period: 2020-22 +0.18%, 2023 +0.24%, 2024-26 +0.18% (81% won).

## Risks

- **Losses are large compared with wins.** The average win is about +0.65% and the average loss about -1.6%. The worst trade was -10% on BTC and -25% on ETH, in a flash crash.
- **Losing and flat years.** 2022 lost (BTC: 5 trades, 1 winner, -16.5%). 2025 was flat.
- **Few signals.** There are about 2-3 a month, in bursts, and sometimes none for months. BTC had only 3 so far in 2026.
- **Tuning matters.** Weaker settings (spike 0.6, RSI 35, stops of 6-8 ATR) cut the edge sharply.

## Reproduce

```
python3 research/backtest_scalper_5m.py BTCUSDT
```

---

# RevDots Scalp Scanner (frequent signals)

`revdots-scalp-scanner.pine` applies the scalper rules to **9 coins at once** from one 5-minute chart: BTC, ETH, SOL, XRP, BNB, DOGE, ADA, AVAX and LINK, as Binance perps. It shows a status table and sends one alert per signal with entry, TP and SL. It allows at most **5 trades open** at a time, as a crash guard.

## Why a scanner

One coin cannot give frequent signals and stay profitable after costs. On a single coin the edge shrinks as frequency rises:

| BTC signals/week | Net per trade after 0.08% |
|---|---|
| about 0.2 (Strict) | +0.18% |
| 1-2 (Active) | +0.03% to +0.07% |
| more than 4 | nothing stayed positive in every period |

Running the same rule on 9 coins gives frequency without loosening it. The 7 altcoins were not used to pick the rules, and every one was profitable in 2024-26.

## Results

Active mode, max 5 open, bar-by-bar replay of the script, Jan 2020 - Oct 2026, 0.08% round-trip cost:

- **Trades:** 6,204, 83.7% won, +0.19% per trade.
- **2025-26:** about 13 signals a week (1-2 a day), +0.07% per trade, or +0.11% with 0.04% limit-order fees.
- **Every year was positive:** 2020 +0.25%, 2021 +0.43%, 2022 +0.05%, 2023 +0.13%, 2024 +0.09%, 2025 +0.08%, 2026 +0.05%.
- **Basket with each trade at 1/9 of the account:** total +133%, max drawdown 7.6%, worst day -6.3%. Without the max-open limit, the worst day was -12% (May 2021 crash).

## Risk

- **The edge per trade is thin in 2025-26.** Fees decide whether it is worth trading, so use limit orders where you can.
- **The rare loss is large.** The worst single trade was -30%, in the May 2021 crash.

## Reproduce

```
python3 research/backtest_scanner_5m.py Active 5
```
