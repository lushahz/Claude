# AMD × Volume Profile — Crypto Edition

A TradingView toolkit for the **Accumulation → Manipulation → Distribution** model, with
the entry taken on the **volume-profile retest**. It's built for crypto: it reads the
whole market (TOTAL, TOTAL2, TOTAL3, BTC, BTC.D, USDT.D and ETH/BTC) plus open interest,
and its defaults come from a 2-year backtest on 20 liquid coins.

```
                                                 D · displacement
   A · accumulation (range + volume profile)          ▲
  ┌───────────────────────────┐                       █      ↺ retest   ▲ signal   ┌─ target 2.5R
  │ ▒▒▒▒▒▒▒       VAH ─ ─ ─ ─ │ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─█─ ─ ─ ─ ─ ─ ─ ╲╱ ─ ─ ─ ─ ─ ─┤  entry
  │ ███████████   POC ━━━━━━━ │ ━━━━━━━━━━━━━━━━━━━━━━━█━━━━━━━━━━━━━━━━━━━━━━━━━━━┤  stop below
  │ ▒▒▒▒▒         VAL ─ ─ ─ ─ │ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─█
  └───────────────────────────┘╲      ╱
                                ╲____╱  M · sweep: stops under the range get taken,
                                        then price closes back inside
```

## What's in this folder

| File | What it is |
|---|---|
| `pine/AMD_Volume_Profile_Crypto.pine` | **The indicator.** Draws the setup, signals, position boxes, market dashboard and alerts. |
| `pine/AMD_VP_5m_Clean.pine` | **5-minute clean edition** with exchange-aggregated volume and a 1h trend filter (see section 6). |
| `pine/AMD_Volume_Profile_Crypto_Strategy.pine` | The same engine as a **strategy**, so TradingView's Strategy Tester shows real results on any coin and timeframe. Generated from the indicator. |
| `watchlists/*.txt` | TradingView watchlists to import: market-context charts, majors and the current top movers. |
| `research/` | Python version of the exact same rules, the backtester, the parameter sweep and the coin scanner. |
| `research/results/REPORT.md` | Full backtest report: every number in this README comes from it. |
| `tools/` | Builds the strategy file from the indicator, and compiles both on TradingView's Pine compiler. |

Both Pine scripts compile with **0 errors and 0 warnings** on TradingView's Pine v6 compiler.

---

## 1 · Install (about 3 minutes)

1. Open TradingView → **Pine Editor** (bottom panel) → **Open** → **New blank indicator**.
2. Delete everything, paste the contents of `pine/AMD_Volume_Profile_Crypto.pine` and click **Save**, then **Add to chart**.
3. Optional: do the same with `pine/AMD_Volume_Profile_Crypto_Strategy.pine` (choose **New blank strategy**), then open
   the **Strategy Tester** tab to see results for the coin on screen.
4. Import the watchlists: right panel → watchlist menu → **Import list…** → choose a file from `watchlists/`.
   - `AMD_market_context.txt` holds the charts the dashboard reads, so you can open them yourself.
   - `AMD_top_movers.txt` holds the majors plus the 20 most-moving liquid coins (Binance perps).
   - `AMD_crypto_full.txt` contains both.
5. Use the **1-hour** chart. It's the only timeframe where the edge held up; 15m and 4h lost money (see section 6).

Use **Binance perpetual** symbols (`BINANCE:SOLUSDT.P`) when you can. The script then reads the matching open
interest (`…USDT.P_OI`) automatically. Spot charts work too: the script looks up the matching perpetual's open interest.

---

## 2 · How the model works

| Phase | Rule in the script | Why |
|---|---|---|
| **A · Accumulation** | 30 bars whose high − low ≤ 5 × ATR(100). A volume profile across the range gives **POC** (most-traded price) and the **value area** (VAH–VAL, 70 % of volume). | Big players build positions quietly. The profile shows where they did it. |
| **M · Manipulation** | Price trades beyond one side of the range, no further than 1 × the range height, and **closes back inside** within 8 bars. | Stop hunt: it takes out stops and pulls in breakout traders on the wrong side. If price keeps going, it was a real breakout and the setup is cancelled. |
| **D · Distribution** | A candle closes beyond the **opposite** side of the range with a body ≥ 1 × ATR and volume ≥ 1.5 × its 20-bar average, within 30 bars of the reclaim. | Displacement: real money moves price fast. Slow drifts don't qualify. |
| **↺ Pullback** | Price returns to within 0.25 ATR of **VAH** (longs) or **VAL** (shorts) within 40 bars. | The old value edge should now act as support (or resistance). |
| **▲▼ Signal** | Within 5 bars, a candle **closes back above VAH** and is green (longs), or back below VAL and red (shorts). | Confirmation. In testing, resting limit orders at the level lost money; waiting for this close made money. |
| **Stop** | Beyond the pullback's extreme + 0.3 ATR (minimum 0.5 ATR, trade skipped if wider than 4 ATR). | Below the level that should hold. |
| **Target** | 2.5 × risk. | 2–3R tested about equally well; 2.5R sits in the middle. |
| **Cut the loser** | 2 closes back through the POC → exit at market. | *Acceptance back inside value* means the idea is wrong. This is the rule the trader in the video ignored. |

Shorts are the mirror image: a sweep above the range, a displacement down, a retest of VAL from below.

The setup is cancelled (and erased from the chart unless *Keep cancelled setups* is on) when:
the range breaks both ways at once, the sweep goes too deep or lasts too long, no displacement comes,
no pullback comes, the pullback closes through the POC, or no confirmation candle appears.

---

## 3 · Reading the chart

- **Grey box:** the accumulation range. The **histogram** inside it is the volume profile: the red bar is the POC, orange bars are the value area.
- **Red solid line:** POC. **Orange dashed lines:** VAH and VAL. They extend right while the setup is alive.
- **Shaded box beyond the range plus an "M · sweep" label:** the manipulation. If open-interest data exists, the label shows how much OI changed during the sweep. A **negative change ("OI flush")** means positions were liquidated or closed into the sweep, which is the fuel you want.
- **"D · displacement":** the breakout candle.
- **Green/red boxes, as in the video:** the position (target zone and stop zone). The label shows entry, stop, target, grade and session.
- **✓ +2.5R / ✗ −1.0R:** how the trade ended, net of fees.
- **"× long skipped":** a valid setup the market filter or time filter blocked.

### The dashboard (top right)

| Row | Meaning |
|---|---|
| Phase | Where the current setup is: searching → A → M → D → waiting for confirmation → in trade. |
| Range / VAH · POC · VAL / Retest level | Levels of the live setup. Set alerts or limit orders off these. |
| TOTAL, TOTAL2, TOTAL3, BTC, BTC.D, USDT.D, ETH/BTC | Trend of each context chart on the 4h (EMA 21/55, last *closed* 4h bar, so it never repaints). Green means it helps longs; red means it helps shorts. BTC.D and USDT.D are colored inversely. |
| Grade if long / short | A = every relevant context chart agrees, B = most agree, C = most disagree. |
| Open interest Δ | Change in OI over the range length. Rising OI in a range means positions are building, which is the accumulation fingerprint. |
| Session | Asia / London / New York / overlap, and whether you're in a killzone. |
| This chart | Trades, win rate, total and average R and max drawdown for the coin and timeframe on screen, net of costs. |

---

## 4 · The crypto market context: what to watch and why

Altcoins don't move on their own. Most of the time they follow Bitcoin and overall market liquidity. The script grades
every signal against the charts that matter **for the asset you're trading**:

| Chart | What it measures | Good for **longs** when… | Used for |
|---|---|---|---|
| `CRYPTOCAP:TOTAL` | Total crypto market cap | trending up | every coin |
| `CRYPTOCAP:USDT.D` | Share of the market sitting in USDT | trending **down** (money leaving stablecoins for coins) | every coin |
| `CRYPTOCAP:TOTAL2` | Market cap ex-BTC | trending up | ETH |
| `BINANCE:ETHBTC` | ETH strength vs BTC | trending up | ETH |
| `CRYPTOCAP:TOTAL3` | Market cap ex-BTC & ETH: the altcoin market | trending up | altcoins |
| `BINANCE:BTCUSDT` | Bitcoin itself | trending up | altcoins |
| `CRYPTOCAP:BTC.D` | Bitcoin dominance | trending **down** (money rotating into alts) | altcoins |
| Open interest (`…USDT.P_OI`) | Leverage in the coin | drops during the sweep (a flush) | shown on the sweep label |

Also worth a glance on your context watchlist, though the script doesn't score them:
`CRYPTOCAP:OTHERS.D` (small caps' share, the memecoin-season gauge), `CRYPTOCAP:ETH.D`,
`TVC:DXY` (a strong dollar usually weighs on crypto) and `SP:SPX` (crypto trades as a risk asset).
Also check the **economic calendar**: avoid new entries in the hour before CPI, FOMC and NFP.

**Market filter defaults (and why):** *Block grade C* applied to *shorts only*. In the backtest, shorts taken
against Bitcoin's 4h trend lost money and shorts with it made money. Longs after a sweep worked in every regime.
Settings ⑦ let you change both.

---

## 5 · Which coins

`research/scan_movers.py` ranks Binance USDT pairs by **volatility × liquidity**: 30- and 90-day average daily range,
weighted by the log of median daily volume. Stablecoins, wrapped coins and tokenised stocks are excluded. Ranking as of 2026-10-06:

**Majors:** BTC, ETH, SOL, XRP, BNB
**Top movers:** ZEC, PUMP, NEAR, ENA, UNI, WLD, SUI, PEPE, ADA, DOGE, TAO, XPL, ONDO, TRUMP, AAVE, FET, LINK, AVAX, XLM, LTC

The list changes. Re-run `python research/scan_movers.py` every few weeks; it rewrites the watchlist files.
Memecoins trade as `1000PEPE`, `1000SHIB` and so on on Binance perps; the scanner handles that.

---

## 6 · Does it work? (honest backtest)

All tests use the exact rules above (`research/amd_engine.py`) on Binance data, closed bars only, with
**0.05 % fee + 0.02 % slippage per side** taken out of every trade. Results are in **R**: +1R means you made what you
risked. The full report with every table is in [`research/results/REPORT.md`](research/results/REPORT.md).

### 1-hour chart, 20 coins, 2 years (Oct 2024 → Oct 2026)

| | Trades | Win rate | Avg R per trade | Total R | Profit factor | Max drawdown |
|---|---|---|---|---|---|---|
| All signals | 202 | 41.6 % | **+0.36R** | +72R | 1.56 | 15R |
| First half of trades | 101 | 45.5 % | +0.51R | +52R | 1.88 | 6R |
| Second half of trades | 101 | 37.6 % | +0.20R | +20R | 1.29 | 15R |
| Longs | 125 | 48.8 % | +0.61R | +77R | 2.10 | 10R |
| Shorts | 77 | 29.9 % | −0.06R | −5R | 0.92 | 20R |
| Shorts with BTC's 4h trend | 23 | 39.1 % | +0.32R | +7R | 1.52 | |
| Shorts against BTC's 4h trend | 39 | 23.1 % | −0.32R | −12R | 0.63 | |
| **Default (shorts against the market skipped)** | **163** | **46.0 %** | **+0.52R** | **+85R** | **1.89** | 15R |

The last row uses BTC's 4h trend as a stand-in for the script's market grade, which also reads
TOTAL, USDT.D and other charts. Fourteen of the 20 coins finished positive. SOL was the worst (−9.7R over 12 trades) and ENA the best (+13.8R over 10 trades).

At 1 % risk per trade, +0.36R per trade is about +0.36 % of the account per trade on average. In the
test that came to about 100 trades a year across 20 coins, with a worst losing streak of about 15R (−15 %).

### Other timeframes: read this before using 15m or 4h

| Timeframe | Trades | Avg R before costs | Avg R after costs | Verdict |
|---|---|---|---|---|
| **1h** (20 coins, 2 y) | 202 | +0.46R | **+0.36R** | positive |
| 15m (8 coins, 1 y) | 213 | +0.03R | **−0.27R** | **loses**: stops are tiny (median 0.6 % of price), so fees eat 0.3R per trade |
| 4h (20 coins, 4 y) | 89 | −0.10R | **−0.14R** | **loses**: no edge even before costs |

Scaling the rules to the same clock time (for example 120 bars on 15m) didn't fix either one. **Use the 1-hour chart.**
The dashboard warns you on any other timeframe.

### How much to trust these numbers

- The 1h settings were **chosen on the same data** they're reported on. I picked the settings that did best in the
  *weaker* of the two halves to limit overfitting, but this still isn't a clean out-of-sample test. Expect live results to be lower;
  the second half (+0.20R) is a more realistic guide than the total.
- The edge is **concentrated in longs**, during a period when crypto mostly rose. In a long bear market, expect shorts to do
  the work and longs to struggle. The market filter is designed for that.
- Session and weekend differences didn't repeat across timeframes (weekends lost on 1h but won on 4h), so treat them as noise.
- About 10 trades per coin over 2 years is a small sample per coin. Don't trust a single coin's numbers.
- Run the **Strategy** version on your own coins before risking money, then trade small for a month and compare.

---

### 5-minute edition: `pine/AMD_VP_5m_Clean.pine`

A separate, cleaner indicator for the 5m chart:
- **Volume from 8 exchange feeds:** Binance spot and perp, Coinbase, Kraken, Bybit spot and perp, OKX spot and perp, plus the chart's own volume.
- **Only trades in the direction of the coin's own 1-hour trend.**
- **Skips trades whose stop is closer than 0.7 % of price.**
- **Minimal drawings and an 8-row dashboard.**

Test: 20 Binance USDT perps, 5m, Oct 2025 → Sep 2026, 0.07 % cost per side (`research/sweep5m.py`):

| 5m settings | Trades (1st half / 2nd half) | Avg R after costs (1st / 2nd half) | Avg R before costs |
|---|---|---|---|
| 1h defaults run on 5m | 795 / 758 | −0.38 / −0.55 | ≈ 0 |
| Best 5m settings: range ≤ 6 ATR, 2R target, stop ≥ 0.7 % | 184 / 133 | −0.03 / −0.06 | +0.10 |
| **Best 5m settings + 1h trend filter (default)** | **97 / 65** | **−0.01 / +0.06** | +0.17 |
| Same, if you pay maker fees (0.02 %) | 97 / 65 | +0.10 / +0.17 | +0.17 |

**On 5m the model is about breakeven after taker fees.** Fees are the deciding factor: use limit orders where you can,
and treat the signals as a filtered watch-list rather than an automatic system. Python can't fetch other exchanges'
data from here, so the backtest used Binance-only volume. The aggregated volume is untested.

---

## 7 · Trade checklist

Before you click buy or sell:

1. **Timeframe:** 1h chart, liquid coin from the watchlist.
2. **Signal on bar close.** Never enter on a candle that is still open: an intrabar signal can disappear.
3. **Grade:** A or B. A short on grade C is blocked by default. Think twice about a long on grade C.
4. Not in the hour before CPI, FOMC or NFP.
5. **Stop placed immediately**, exactly where the script drew it. Never widen it.
6. **Position size = account × 1 % ÷ stop distance.** Leverage only lets you post less margin; it must not make the position bigger.
   Check that your liquidation price is far beyond the stop.
7. **Correlation:** three altcoin longs at once are basically one big bet on the market. Count them that way, so risk no more than about 3 % across all open trades.
8. **Funding:** if funding is very positive (crowded longs), a long has to fight the crowd. Use smaller size or skip.
9. **Exit plan:** target at 2.5R, stop, or two closes back through the POC. Nothing else.

---

## 8 · Alerts

In TradingView: **Alerts → Create → Condition: AMD-VP**, then choose one of:

- **Any alert() function call**: one alert covers everything. You get a message for each displacement ("watch for the pullback to X"), each signal (entry, stop, target, grade) and each exit.
- **AMD long signal / AMD short signal**: signals only.
- **AMD setup forming**: a sweep or displacement just happened.

Set the alert on each coin in the watchlist. Alerts fire once per bar close.

---

## 9 · Settings worth knowing

| Setting | Default | Note |
|---|---|---|
| Range length | 30 | 20 and 45 both did worse. This is the most sensitive setting. |
| Max range height | 5 × ATR | 5–6 worked; 3 was too strict. |
| Require a sweep | on | Turn off to also trade plain profile breakouts and retests (untested). |
| Retest level | Value area edge | The only level positive in both halves of the data. |
| Entry type | Confirmation | Limit orders at the level lost money out-of-sample. |
| Target | 2.5R | |
| Breakeven | off | |
| Market filter | Block grade C, shorts only | See section 4. |
| Killzones / weekends | off | Results differed by timeframe (weekends lost on 1h, won on 4h): no reliable effect. |

**Repainting:** none. Every decision uses closed bars; context charts use their last *closed* 4h bar.
The range and profile of a setup that is still forming update until the range breaks, and that's intended.

---

## 10 · Reproduce the research

```bash
cd research
pip install pandas numpy
python scan_movers.py             # coin ranking + watchlists
python backtest.py --tf 1h        # per-coin results with the defaults
python sweep.py --tf 1h           # parameter sweep, first half vs second half
python report.py                  # regenerates results/REPORT.md
```

`amd_engine.py` follows the Pine script rule for rule. After changing the indicator, run
`python tools/build_strategy.py`, then `python tools/pine_check.py pine/*.pine` to compile both scripts.

---

*Educational tool, not financial advice. Backtests use historical data and simplified fills; live results will
be worse, because of slippage in fast markets, missed signals and human error. Trade small until your own forward results match.*
