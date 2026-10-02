# Reversal Dots Oscillator (TradingView, Pine Script v6)

A rebuild of the "green dot / red dot" reversal indicator used in the
[overkilltrading](https://www.tradingview.com/u/overkilltrading/) TradingView ideas.
Their indicator is a paid, closed-source product, so this is **not their code**.
It is written from scratch with public formulas so it looks and behaves like
the screenshots in their posts.

File: [`reversal-dots-oscillator.pine`](reversal-dots-oscillator.pine)

## Install

1. In TradingView, open **Pine Editor** at the bottom of the chart.
2. Click **Open → New indicator**, delete the template and paste the whole file in.
3. Click **Save**, then **Add to chart**.

The oscillator opens in its own pane. The 20/50/200 EMAs and the buy/sell
arrows are drawn on the price chart too.

## What you see

| Element | Meaning |
|---|---|
| Light blue edge + dark navy waves | WaveTrend oscillator (fast and slow line) |
| **Green dot** on the wave | Fast wave crossed above slow wave: momentum turning up |
| **Red dot** on the wave | Fast wave crossed below slow wave: momentum turning down |
| Small green dot near **-107** | **Big buy**: green dot printed from oversold (wave ≤ -53) |
| Small red dot near **+107** | **Big sell**: red dot printed from overbought (wave ≥ 53) |
| Yellow dot near -107 | **Gold buy**: big buy + very oversold (≤ -75) + recent bullish divergence |
| White area around zero | Money flow (smoothed candle-body strength): above 0 = buying pressure |
| Light blue line (0–100) | Stochastic RSI %K |
| White dotted line at 100 | Exit / take-profit line for the Stoch RSI |
| White lines at ±60 | Overbought / oversold bands |
| Red / green line between wave peaks | Bearish / bullish divergence (price makes a new high/low, the wave doesn't) |
| Orange / teal / blue on price | EMA 20 / 50 / 200 |

## Trading rules from the ideas

The posts all use the same playbook, mostly on the **weekly** chart:

- **Entry:** a big green dot after a long move down (bear → bull shift).
- **Exit:** when the light blue Stoch RSI line reaches the white dotted line,
  **or** a red dot prints, whichever comes first.
- Overbought weekly charts (Stoch RSI pinned at 100, waves high) are a place to
  take some profit and wait for the next green dot.

## Alerts

Right-click the pane → **Add alert** → pick the indicator and one of:
Green dot, Red dot, Big buy, Big sell, Gold buy, Bullish/Bearish divergence,
Stoch RSI at exit line, or **Exit (dotted line or red dot)**.
Use **Once per bar close**, because a dot can appear and disappear while a bar
is still open.

## Settings

All lengths, levels and colors can be changed in the indicator settings. Defaults:
WaveTrend 9 / 12 / 3, money flow 60 bars × 150, Stoch RSI 14 / 14 / 3 / 3
(log of price), divergence limits +45 / -65.

> This is for education only, not financial advice. Test it on your own
> markets and timeframes before you trade on it.
