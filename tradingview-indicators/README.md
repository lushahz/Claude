# Reversal Dots Oscillator (TradingView, Pine Script v6)

A rebuild of the "green dot / red dot" reversal indicator used in the
[overkilltrading](https://www.tradingview.com/u/overkilltrading/) TradingView ideas.
Their indicator is a paid, closed-source product, so this is **not their code**.
It is written from scratch with public formulas so it looks and behaves like
the screenshots in their posts.

Files:
- [`reversal-dots-daily.pine`](reversal-dots-daily.pine): **refined daily-only
  version**, with only BUY and TAKE-PROFIT triggers (recommended, see below)
- [`reversal-dots-daily-strategy.pine`](reversal-dots-daily-strategy.pine): backtest of the daily version
- [`REVERSAL_RESEARCH.md`](REVERSAL_RESEARCH.md): the 47-market, 2010-2026 study behind it
- [`reversal-dots-crypto.pine`](reversal-dots-crypto.pine): **crypto specialist** daily version
  with Bitcoin / BTC dominance filters, a cycle guard and a TOTAL / BTC.D / USDT.D market panel
- [`reversal-dots-crypto-strategy.pine`](reversal-dots-crypto-strategy.pine): backtest of the crypto version
- [`CRYPTO_RESEARCH.md`](CRYPTO_RESEARCH.md): the 29-coin study behind it
- [`gold-5m-scalper.pine`](gold-5m-scalper.pine): **gold 5-minute scalper** (XAUUSD, London + New York),
  with buy/sell arrows, stop/target lines and a live scorecard
- [`gold-5m-scalper-strategy.pine`](gold-5m-scalper-strategy.pine): backtest of the gold scalper
- [`GOLD_RESEARCH.md`](GOLD_RESEARCH.md): the 2009-2026 study of 1.2 million 5-minute gold bars behind it
- [`reversal-dots-oscillator.pine`](reversal-dots-oscillator.pine): the original multi-timeframe indicator
- [`reversal-dots-strategy.pine`](reversal-dots-strategy.pine): its strategy version

## Gold 5-minute scalper

[`gold-5m-scalper.pine`](gold-5m-scalper.pine) is for **XAUUSD on the 5-minute chart**,
07:00-16:00 UTC. It has two setups:
- **Divergence snap:** gold moved much further than the US Dollar Index explains, silver agrees,
  and a reversal candle forms. It needs `TVC:DXY` and `OANDA:XAGUSD`, both editable in the settings.
- **London break:** the first close beyond the Asian range during the London open, in the
  4-hour trend direction.

Signals appear only when the 5m ATR is at least $2 (costs eat small moves).
- Big green up arrow = buy; big red down arrow = sell, and the signal candle is highlighted.
  Hover an arrow to see the setup (divergence snap or London break) and the stop and target.
- Dashed lines show the stop (1.5 ATR) and target (2 ATR). Trades close after 36 bars or at the session end.
- The dashboard shows the session, ATR, 4h trend, the gold-vs-dollar and silver readings,
  and a **scorecard** replaying every signal on your chart after your cost setting.

Read [`GOLD_RESEARCH.md`](GOLD_RESEARCH.md) first. The tests found no 5-minute gold setup
that reliably beats trading costs. These rules lost before 2020. They were slightly profitable
from 2020 on (profit factor about 1.04-1.10 at $0.30/oz), and results vary a lot from year to year.

## Crypto version

`reversal-dots-crypto.pine` is the daily version tuned for crypto (1D chart):

- **Altcoins** only get a BUY when Bitcoin is oversold too (RSI <= 40 in the
  last 10 days) and BTC dominance is below its 20 EMA (money rotating into alts).
- **Cycle guard:** no new buys while Bitcoin is 25-60% below its 1-year high,
  the "first dip after a cycle top" zone where most of the -70% to -85%
  trades started.
- **Cycle exit (orange arrow):** Bitcoin's 50 EMA crosses below its 200 EMA.
- **Pullback buys (light green, on by default):** dips inside an uptrend, for
  a median of **4 buy signals per coin per year** in total (profit factor
  3.38 / 2.09). Reversal buys (bright green) remain the stronger signal.
- **Market panel:** trade status, cycle guard, Bitcoin, BTC.D, TOTAL and USDT.D.

On 29 coins, the profit factor went from 2.89 / 1.99 (general rules,
2014-21 / 2022-26) to **4.83 / 3.44**, and the worst trade from about -85% to
about -50%. TOTAL and USDT.D didn't improve the triggers out of sample, so they're
shown as context only. Details and caveats in
[CRYPTO_RESEARCH.md](CRYPTO_RESEARCH.md).

## Daily version (recommended)

`reversal-dots-daily.pine` is built for the **1D chart only**. Instead of a dot
on every wave cross (about 25 per market per year), it shows:

| Mark | Meaning |
|---|---|
| Green up arrow + green dot at the pane bottom | **BUY**: green dot with waves <= -53, RSI <= 40 and price stretched >= 2 ATRs below the 50 EMA, confirmed by a bullish close within 3 days |
| Red down arrow + red dot at the pane top | **TAKE-PROFIT**: overbought (waves >= 53, RSI >= 70) in the last 15 days, then the first close below the 20 EMA |
| Small yellow x | **Failed reversal**: closed more than 1 ATR below the low before the buy |

It tracks one trade at a time, so you see about **1 BUY and 1 TAKE-PROFIT per
market per year**. The status panel shows whether you're LONG (with the entry
date and P/L) or FLAT, and whether a setup is forming.

In the study it caught about 2/3 of major bottoms (79% in indices, 78% in
crypto, 37% in forex). BUY -> TAKE-PROFIT had a profit factor of about 3.8 in
both 2010-2018 and 2019-2026. Read
[the caveats](REVERSAL_RESEARCH.md#7-honest-caveats) before trading it.

Install it like the original: Pine Editor → create a new indicator → clear the
template → paste → Save → Add to chart. The strategy goes in its own new
strategy script.

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
| Green arrow below / red arrow above the candle | **Early buy / early sell warning**: fast wave turned before the cross (often 1-2 bars before the green / red dot, but fails more often) |
| Green up arrow on price | **Setup buy**: big buy on this chart while the higher timeframe is in its buy zone (HTF waves below 0) |
| Red down arrow on price | **Setup sell**: big sell on this chart while the higher timeframe is in its sell zone (HTF waves above 0) |
| Green diamond below / red diamond above the candle | **Confirmation buy / sell**: green dot below zero with price above the 50 EMA (or red dot above zero with price below it). Later entries that catch breakouts after a long sideways stretch |
| Light blue line (0-100) | Stochastic RSI %K |
| Magenta line | RSI (turns green under 30, red over 70) |
| White dotted line at 100 | Exit / take-profit line for the Stoch RSI |
| White lines at 60 / 0 / -40 | Upper band, zero line, lower band |
| Red / green line between wave peaks | Bearish / bullish divergence (price makes a new high/low, the wave doesn't) |
| Orange / grey / blue on price | EMA 20 / 50 / 200 |
| White area around zero (off by default) | Money flow (smoothed candle-body strength) |

The MACD pane under the oscillator in the reference charts is TradingView's
built-in **MACD** indicator. Add it from **Indicators** if you want it.

## Higher-timeframe panel

The table in the top-right corner shows the higher timeframe (auto: 15m -> 1H,
1H -> 4H, 4H -> D, D -> W, W -> M; or pick one in settings):

| Row | Meaning |
|---|---|
| Waves | Slow wave value and zone (Oversold <= -40, Overbought >= 60) |
| Direction | Fast wave rising or falling |
| Last dot | Last green / red dot on the higher timeframe and how many HTF bars ago |
| Stoch RSI | Higher-timeframe Stoch RSI (red when at the exit line) |
| Bias | **BUY ZONE** (HTF slow wave below 0) or **SELL ZONE** (above 0), with "turning up / down" when the HTF wave confirms the direction |

By default the panel uses the last **closed** higher-timeframe bar, so it never
repaints. Turn on "Use the still-forming HTF bar" to see the turn earlier, but
it can change until that bar closes.

## Getting earlier signals

Use the higher timeframe for direction and the chart timeframe for timing:

- **Stocks:** daily chart (the panel shows the weekly)
- **Crypto:** 4H chart (the panel shows the daily)

Take chart buys only when the panel says **BUY ZONE**. The green arrow on the
price chart marks exactly that, and the red arrow marks big sells in the
**SELL ZONE**. "Arrows on price chart" in settings switches between setup arrows,
all big signals, strong signals only, or off. Early-warning arrows (green up / red down) come
before the dots; use them as a heads-up, not as an entry on their own.

## Trading rules from the ideas

The posts all use the same playbook, mostly on the **weekly** chart:

- **Entry:** a big green dot after a long move down (bear → bull shift).
- **Exit:** when the light blue Stoch RSI line reaches the white dotted line,
  **or** a red dot prints, whichever comes first.
- Overbought weekly charts (Stoch RSI pinned at 100, waves high) are a place to
  take some profit and wait for the next green dot.

## Alerts

Right-click the pane → **Add alert** → pick the indicator and one of:
Green dot, Red dot, Early buy/sell warning, Big buy, Big sell, Strong buy,
Strong sell, **Setup buy / Setup sell**, Bullish/Bearish divergence,
Stoch RSI at exit line, or **Exit (dotted line or red dot)**.
Use **Once per bar close**, because a dot can appear and disappear while a bar
is still open.

## Backtesting (strategy version)

1. In the Pine Editor create a **new** script (Create new -> Strategy), paste
   `reversal-dots-strategy.pine`, then **Save** and **Add to chart**.
2. Open the **Strategy Tester** tab under the chart to see net profit, win rate,
   drawdown and the list of trades.
3. Switch the chart timeframe (W, D, 4H) and the ticker, and compare results.
4. In settings, try different rules:
   - **Entry:** Any green dot / Early warning / Big buy / Strong buy only /
     Confirmation / Big buy or confirmation
   - **Only buy when the higher timeframe is in its buy zone** (on / off)
   - **Exit:** Stoch line or big sell (default) / Big sell only (holds longer) /
     Stoch line or any red dot (the posts' rule) / Any red dot / Stoch line only
   - Optional stop loss %, start date

Entries show as green up arrows and exits as red down arrows. To hide
TradingView's own order flags, open the strategy settings → **Style** and
untick **Signal labels**.

It's long only. It invests 100% of equity per trade with 0.1% commission, and
orders fill on the next bar's open. The higher-timeframe filter uses closed
bars only, so the backtest doesn't look ahead.

### What the tests showed

I recreated the strategy in Python and ran it on daily data since 2016 for BTC,
ETH, SOL, TSLA, NVDA, AAPL, SPY, PL and RIVN (Big buy entry):

- **Weekly beats daily per trade.** Weekly big buys won about 60-85% of the time
  with average trades of +13-19%. Daily ones won 45-70% with average trades of
  +1-3%. The catch is that weekly big buys are rare (BTC has had 4 since 2016).
- **Exit on "Stoch line or big sell", not on any red dot.** Exiting on every red
  dot cut winners short: the win rate dropped from about 70% to about 45%.
- **The HTF filter (HTF waves below 0) helps.** On BTC weekly it skipped the
  2018 (-42%) and 2025 (-7%) big buys and kept 2022 (+14%).
- Requiring the HTF waves to also be *rising* blocked almost every trade (0 on
  BTC weekly), so that's now an optional setting, off by default.

- **Big buys come early, at the bottom.** On BTC daily in 2026 the June 30 big
  buy came at about $60k, then price went sideways for 7 weeks before breaking
  out in August. The optional confirmation buy fired at the breakout (Aug 18,
  about $64.5k), but it also bought May 25 at about $77k (-14%). Across all 9
  tickers, confirmation buys won 69% of the time with +2.3% average trades,
  vs 73% and +3.0% for big buys. To hold through a sideways stretch, try the
  **Big sell only** exit.

### 1-hour chart / day trading

I tested 2 years of 1-hour data for BTC, ETH, SOL, TSLA, NVDA, SPY, AAPL, QQQ
and PL, with long and short, VWAP filters, ATR stops and targets, and
flat-by-the-close exits:

- **True day trading (flat by the close) had no real edge.** The best stock
  version won 48% of the time with +0.15% average trades, about break-even
  after costs.
- **Crypto on 1H lost money after 0.1% fees** in almost every version.
- **Shorts lost money** on both crypto and stocks.
- **What worked on 1H: stock longs held for days.** Big buys on the 1H chart,
  with the HTF set to **1D** (daily waves below 0) and exiting on a 1H big
  sell, won about 70% of the time with +1.7% average trades. 5 of 6 stocks
  were positive. The median hold was about 10 days, so this is short-term
  swing trading timed on the 1H chart, not day trading.

To use it: indicator settings → Higher timeframe → **1D**. Strategy settings →
Exit → **Big sell only**.

These are past results on a handful of tickers, not a promise. Check your own
tickers in the Strategy Tester.

## Settings

All lengths, levels and colors can be changed in the indicator settings. Defaults:
WaveTrend 9 / 12 / 3, Stoch RSI 14 / 14 / 3 / 3 (log of price), RSI 14,
levels 100 / 60 / 0 / -40, divergence limits +45 / -40, strong-signal window 6 bars.

> This is for education only, not financial advice. Test it on your own
> markets and timeframes before you trade on it.
