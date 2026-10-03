# Daily reversal research (2010-2026)

This study is the basis for **`reversal-dots-daily.pine`**. It looks at what
markets looked like at every major daily reversal across 47 markets and turns
that into a few strict triggers instead of a dot on every wave cross.

Not financial advice. Past results don't predict future results.

## 1. Data

Daily OHLCV from Yahoo Finance, January 2010 to October 2026 (crypto from its
listing date): about 190,000 daily bars.

| Class | Markets | From |
|---|---|---|
| Crypto | BTC, ETH, XRP, LTC, ADA, SOL, DOGE, BNB | 2014 (BTC, LTC), 2017 (others), 2020 (SOL) |
| Forex | EURUSD, GBPUSD, USDJPY, AUDUSD, USDCAD, USDCHF, NZDUSD, EURJPY | 2010 |
| Stocks | AAPL, MSFT, AMZN, NVDA, TSLA, META, GOOGL, JPM, XOM, JNJ, WMT, BA, NFLX, AMD | 2010 (META 2012) |
| Index CFDs | S&P 500, Nasdaq 100, Dow, Russell 2000, DAX, FTSE 100, Nikkei 225, Hang Seng | 2010 |
| Commodity CFDs | Gold, Silver, WTI crude, Natural gas, Copper (front-month futures) | 2010 |
| Exchange operators | CME Group, ICE, Nasdaq Inc, Cboe | 2010 |

## 2. Method

1. **Major reversals.** A swing detector on daily closes, scaled to each
   market's volatility (7x its median daily ATR, at least 4%). That's about a 6%
   swing for forex, 7-10% for indices, 13-30% for stocks and 27-50% for crypto.
   Result: **882 major bottoms and 873 major tops**, about 2-3 per market per
   year.
2. **Profile.** What the waves, RSI, distance from the 50/200 EMA, volume and
   candles looked like at those turns, compared with all other days.
3. **Rules.** Candidate triggers were designed on **2010-2018** only, then
   checked on **2019-2026**, which they never saw.
4. **Trades.** Long only, enter on the next day's open, with costs (0.10%
   crypto, 0.05% stocks and commodities, 0.03% indices, 0.02% forex per side).

## 3. What markets look like at major reversals

| Condition | At major bottoms | On ordinary days |
|---|---|---|
| RSI(14) <= 30 within +-3 days | **50%** | 3% |
| Slow wave <= -53 within +-3 days | 79% | 11% |
| Close >= 2.9 ATRs below the 50 EMA | 75% | 7% |
| Below the 200 EMA | 92% | 36% |
| Volume spike (z > 2) in the last 5 days (not forex) | 34% | 18% |
| Bullish wave divergence within 10 days | 28% | - |

Tops are the mirror image: RSI >= 70 in 52% of tops (8% of days), slow wave
>= 53 in 75% (19% of days), price ~3.7 ATRs above the 50 EMA.

The same profile shows up in every asset class (median at bottoms):

| Class | Wave | RSI | Drawdown from 1-year high |
|---|---|---|---|
| Crypto | -69 | 28 | 22 ATRs |
| Forex | -64 | 30 | 12 ATRs |
| Stocks | -63 | 31 | 10 ATRs |
| Index CFDs | -67 | 30 | 9 ATRs |
| Commodities | -65 | 31 | 14 ATRs |
| Exchanges | -69 | 28 | 11 ATRs |

**Key finding: bottoms and tops behave differently.** Bottoms are panics:
oversold, stretched far below the averages, often with a volume spike and a
fast V-turn, which makes them easy to measure. Tops are usually slow: price
rolls over from a less extreme state, and every short-selling rule tested lost
money. So the indicator buys reversals and uses its sell trigger only to take
profit, never to go short.

## 4. Why the big reversals happened

The largest turning points in key markets and the event behind each. The
right-hand column shows what the new daily triggers did. Turns marked
"technical" had no single clear news catalyst that I could confirm.

### Bottoms

| Market | Bottom | Then | What happened | New BUY trigger |
|---|---|---|---|---|
| S&P 500 | 2010-07-02 | +33% | Euro debt crisis (Greece) and the May flash crash; Fed hinted at QE2 in August | 2010-07-07 |
| S&P 500 | 2012-11-15 | +49% | US "fiscal cliff" fears after the election; Fed QE3/QE4 | 2012-11-19 |
| S&P 500 | 2016-02-11 | +57% | Oil crash to $26 and China slowdown fears; oil bottomed the same day | missed (waves -51, just short) |
| S&P 500 | 2018-12-24 | +44% | Fed hikes and QT "on autopilot", trade war, government shutdown; Fed turned "patient" Jan 4, 2019 | 2018-12-26 |
| S&P 500 | 2020-03-23 | +60% | COVID crash; Fed announced unlimited QE on Mar 23 | 2020-03-17 (6 days early) |
| S&P 500 | 2022-10-12 | +17% (120 days) | Inflation peak and 75bp Fed hikes; softer CPI on Nov 10 | 2022-09-28 and 10-03 (early) |
| S&P 500 | 2023-10-27 | +38% | 10-year Treasury yield hit 5%; Fed paused and turned dovish | 2023-10-31 |
| S&P 500 | 2025-04-08 | +40% | "Liberation Day" tariffs (Apr 2); 90-day pause announced Apr 9 | 2025-04-09 |
| Nasdaq 100 | 2019-06-03 | +39% | US-China tariff escalation in May; Powell signaled cuts on Jun 4 | 2019-06-04 |
| DAX | 2012-06-05 | +43% | Euro crisis peak; Draghi's "whatever it takes" in July | 2012-05-22 and 06-06 |
| DAX | 2016-06-27 | +46% | Brexit vote (Jun 23) | 2016-06-20 (early, before the vote) |
| DAX | 2022-09-29 | +38% | European energy crisis, Nord Stream sabotage, UK gilt crisis | 2022-09-30 |
| Nikkei 225 | 2014-10-17 | +44% | Global growth scare; BoJ surprise QE expansion Oct 31 | 2014-10-20 |
| Nikkei 225 | 2024-08-05 | +28% (120 days) | BoJ hike plus a weak US jobs report forced a yen carry-trade unwind (-12% in one day) | 2024-08-07 |
| Nikkei 225 | 2025-04-07 | +89% | Tariff shock | 2025-04-10 |
| BTC | 2015-08-24 | +264% | Global "Black Monday" selloff led by China; end of the 2014-15 bear market | 2015-08-26 |
| BTC | 2017-09-14 | +518% | China banned ICOs and closed local exchanges; the rally ran to $19.7k | 2017-09-18 |
| BTC | 2018-12-15 | +302% | Crypto-winter capitulation after the Bitcoin Cash "hash war" | 2018-12-09 and 12-17 |
| BTC | 2020-03-12 | +1,178% | COVID "Black Thursday" crash and mass liquidations | 2020-03-17 |
| BTC | 2021-07-20 | +127% | China mining ban; Tesla stopped accepting BTC | 2021-07-21 |
| BTC | 2022-11-21 | +572% | FTX collapse | missed (waves only -46) |
| BTC | 2026-06-30 | +48% so far | Technical | 2026-06-29 and 07-01 |
| Gold | 2015-12-17 | +30% | The day after the Fed's first hike since 2006 | missed (waves only -23) |
| Gold | 2018-08-16 | +42% | Strong dollar, Turkish lira crisis | 2018-08-08 and 08-21 (re-arm) |
| Gold | 2023-10-05 | +138% | Bond-yield peak, then safe-haven demand after Oct 7 and record central-bank buying | 2023-10-06 |
| WTI crude | 2016-02-11 | +96% | OPEC price war bottom; output-freeze talks began Feb 16 | missed (waves -50, just short) |
| WTI crude | 2020-04-21 | +586% | Storage full and May futures went negative; OPEC+ record cut | 2020-04-23 |
| WTI crude | 2021-12-01 | +89% | Omicron fears and a US reserve release; then Russia invaded Ukraine | 2021-12-06 |
| EURUSD | 2016-12-21 | +20% | Fed hike and post-election dollar rally | 2016-12-27 |
| EURUSD | 2022-09-27 | +17% | Fed 75bp hikes, energy crisis, UK gilt crisis | missed (no bullish close in time) |
| USDJPY | 2012-09-27 | +33% | Before Abenomics (Abe elected Dec 2012, BoJ QQE Apr 2013) | 2012-09-17 (early) |
| USDJPY | 2025-04-21 | +16% | Tariff turmoil and broad dollar selling | missed (no bullish close in time) |
| NVDA | 2016-02-08 | +1,047% | Market low; start of the gaming, data-center and AI run | 2016-02-12 |
| NVDA | 2022-10-14 | +1,108% | US chip export controls (Oct 7) and peak inflation; ChatGPT launched Nov 30 | 2022-10-03 (early) |
| TSLA | 2023-01-03 | +171% | Twitter-sale overhang, price cuts, delivery miss | 2022-12-29 |
| AAPL | 2016-05-12 | +157% | First-ever iPhone sales decline | 2016-05-03 and 05-16 (re-arm) |
| AAPL | 2020-03-23 | +139% | COVID crash | 2020-03-24 |
| CME | 2020-03-23 | +38% | COVID crash (exchanges then earned record volumes) | 2020-03-20 |

Most big bottoms came at **peak fear plus a policy response**: a Fed or ECB
pivot, QE, a tariff pause, a BoJ move. The indicator can't see news, but the
same thing shows up on the chart: deeply oversold waves and RSI, price
stretched far below the 50 EMA, then a strong bullish close.

### Tops

| Market | Top | Then | What happened | TAKE-PROFIT trigger |
|---|---|---|---|---|
| S&P 500 | 2020-02-19 | -34% | COVID crash began from a calm market | missed (not overbought) |
| S&P 500 | 2022-01-03 | -24% | Fed turned hawkish on inflation | missed (slow rollover) |
| S&P 500 | 2025-02-19 | -19% | Tariff fears built up | missed (slow rollover) |
| Nasdaq 100 | 2021-11-19 | -28% | Fed taper and hawkish turn | 2021-11-26 (-3% from top) |
| BTC | 2017-12-16 | -66% | CME futures launch at the height of the mania | 2017-12-22 (-29%) |
| BTC | 2021-11-08 | -48% | CPI 6.2% and the Fed taper | missed |
| BTC | 2025-10-06 | -38% | Record $126k; the Oct 10 tariff threat set off record liquidations | 2025-10-10 (-9%) |
| Gold | 2020-08-06 | -14% | Record high on negative real yields | 2020-08-20 (-6%) |
| WTI crude | 2022-03-08 | -30% | Spike after Russia invaded Ukraine | 2022-03-14 (-17%) |
| USDJPY | 2015-06-05 | -6% | Kuroda said the yen was unlikely to weaken further | 2015-06-10 (-2%) |
| USDJPY | 2022-10-20 | -15% | BoJ intervened at 151.9 | 2022-10-26 (-3%) |
| USDJPY | 2024-07-03 | -13% | BoJ hike and carry-trade unwind | 2024-07-11 (-2%) |
| Nikkei 225 | 2024-07-11 | -26% | Same carry-trade unwind | 2024-07-18 (-5%) |
| TSLA | 2021-11-04 | -38% | Musk's Twitter poll and share sales | 2021-11-09 (-17%) |
| NVDA | 2018-10-01 | -56% | Crypto-mining chip glut | missed |

The take-profit trigger catches **spike tops** (blow-offs, interventions,
manias) within a few days. It misses **slow rollovers and crashes that start
from a calm market**. Use your own risk management for those, such as the
failed-reversal warning or a stop.

## 5. The refined triggers

**BUY** (all must be true):

1. Green dot: the fast wave crosses above the slow wave
2. Slow wave <= -53 in the last 3 days
3. RSI(14) <= 40 in the last 5 days
4. Close at least 2 ATRs below the 50 EMA at some point in the last 10 days
5. Confirmation within 3 days: a bullish close (close > open, close > the
   previous close, close in the upper half of the day's range)
6. At most one buy per 10 days, unless price makes a lower low than the
   previous buy. That re-arm catches the real bottom after an early signal.

**TAKE-PROFIT:** slow wave >= 53 and RSI >= 70 within the last 15 days, then
the first close below the 20 EMA.

**FAILED-REVERSAL warning:** after a buy, a close below the lowest low of the
5 days before the buy minus 1 ATR.

Why not the simpler rules: the confirmation window and the re-arm were added
after checking misses. An early signal in a crash used to block the real
bottom a week later (DAX and AAPL), and panic-bottom days often still close
weak (BTC in March 2020 and December 2018, gold in August 2018).

## 6. Results

**Signal count:** every wave cross gave about **25 dots per market per year**.
The refined buy fires about **3 times per market per year** before
filtering. With one trade at a time, the chart shows about **1 BUY and 1
TAKE-PROFIT per market per year**.

**Major bottoms caught** (a BUY within 5 days before to 15 days after):

| Class | Bottoms caught | Tops caught by TAKE-PROFIT (within 30 days) |
|---|---|---|
| Index CFDs | 79% | 43% |
| Exchange operators | 80% | 44% |
| Crypto | 78% | 69% |
| Stocks | 68% | 54% |
| Commodities | 68% | 54% |
| Forex | 37% | 61% |

**Trades** (47 markets, long only, after costs):

| Entry -> exit | Period | Trades | Win rate | Avg trade | Profit factor | Median hold |
|---|---|---|---|---|---|---|
| Old big buy -> Stoch line or big sell | 2010-18 | 869 | 71% | +1.4% | 1.71 | 18 days |
| Old big buy -> Stoch line or big sell | 2019-26 | 994 | 68% | +1.5% | 1.52 | 19 days |
| **New BUY -> TAKE-PROFIT** | 2010-18 | 340 | 76% | +7.9% | **3.80** | 106 days |
| **New BUY -> TAKE-PROFIT** | 2019-26 | 399 | 73% | +12.7% | **3.75** | 95 days |
| New BUY -> Stoch line or big sell | 2019-26 | 740 | 71% | +2.3% | 1.84 | 16 days |

New BUY -> TAKE-PROFIT by class:

| Class | Period | Trades | Win rate | Avg trade | Profit factor |
|---|---|---|---|---|---|
| Index CFDs | 2019-26 | 76 | 78% | +6.8% | 5.0 |
| Exchange operators | 2019-26 | 33 | 79% | +8.4% | 6.5 |
| Stocks | 2019-26 | 115 | 76% | +14.9% | 4.8 |
| Commodities | 2019-26 | 43 | 74% | +10.4% | 4.9 |
| Crypto | 2019-26 | 91 | 60% | +22.8% | 3.0 |
| Forex | 2019-26 | 41 | 78% | +1.4% | 2.4 |
| Commodities | 2010-18 | 46 | 59% | -0.3% | 0.94 |
| Forex | 2010-18 | 51 | 65% | -0.1% | 0.97 |

## 7. Honest caveats

- **Most of the gain comes from the exit.** Holding until "overbought, then a
  close below the 20 EMA" works because most of these markets rose from 2010
  to 2026. With that exit, even every green dot does about as well
  (profit factor 3.6-3.9). The new entry's real value is fewer, cleaner
  signals that still catch about 2/3 of major bottoms. With the same short
  exit, it improves profit factor from about 1.6 to 1.8.
- **Worst cases are large without a stop.** The worst trade was -63% (2010-18)
  and -75% (2019-26), in crypto. "End the trade on a failed reversal" limits
  that, but lowered the overall profit factor to about 2.4 in the tests.
- **Forex and commodities are weakest.** Both were about break-even in
  2010-2018. Indices, exchange operators and stocks were the most consistent.
- **Slow tops are missed** (see the tops table).
- **Data differences.** Yahoo daily data can differ slightly from your
  TradingView feed (exchange, session, futures roll), so dates can shift by a
  day.
