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
| Small dark-green dot at the bottom (-107) | **Big buy**: green dot printed from oversold (wave <= -53) |
| Small dark-red dot at the top (+107) | **Big sell**: red dot printed from overbought (wave >= 53) |
| Large bright-green dot at the bottom | **Strong buy**: big buy + bullish divergence |
| Large bright-red dot at the top | **Strong sell**: big sell + bearish divergence |
| Light blue line (0-100) | Stochastic RSI %K |
| Magenta line | RSI (turns green under 30, red over 70) |
| White dotted line at 100 | Exit / take-profit line for the Stoch RSI |
| White lines at 60 / 0 / -40 | Upper band, zero line, lower band |
| Red / green line between wave peaks | Bearish / bullish divergence (price makes a new high/low, the wave doesn't) |
| Orange / grey / blue on price | EMA 20 / 50 / 200 |
| White area around zero (off by default) | Money flow (smoothed candle-body strength) |

The MACD pane under the oscillator in the reference charts is TradingView's
built-in **MACD** indicator. Add it from **Indicators** if you want it.

## Trading rules from the ideas

The posts all use the same playbook, mostly on the **weekly** chart:

- **Entry:** a big green dot after a long move down (bear → bull shift).
- **Exit:** when the light blue Stoch RSI line reaches the white dotted line,
  **or** a red dot prints, whichever comes first.
- Overbought weekly charts (Stoch RSI pinned at 100, waves high) are a place to
  take some profit and wait for the next green dot.

## Alerts

Right-click the pane → **Add alert** → pick the indicator and one of:
Green dot, Red dot, Big buy, Big sell, Strong buy, Strong sell, Bullish/Bearish divergence,
Stoch RSI at exit line, or **Exit (dotted line or red dot)**.
Use **Once per bar close**, because a dot can appear and disappear while a bar
is still open.

## Settings

All lengths, levels and colors can be changed in the indicator settings. Defaults:
WaveTrend 9 / 12 / 3, Stoch RSI 14 / 14 / 3 / 3 (log of price), RSI 14,
levels 100 / 60 / 0 / -40, divergence limits +45 / -40, strong-signal window 6 bars.

> This is for education only, not financial advice. Test it on your own
> markets and timeframes before you trade on it.
