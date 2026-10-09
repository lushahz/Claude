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
