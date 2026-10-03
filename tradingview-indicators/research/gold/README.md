# Gold 5-minute research scripts

Python code behind [`../../GOLD_RESEARCH.md`](../../GOLD_RESEARCH.md).

```bash
pip install pandas numpy numba scikit-learn
python hd.py XAUUSD 2009 2026      # HistData.com 1-minute history (repeat for XAGUSD, EURUSD, USDJPY,
                                   #   GBPUSD, USDCAD, USDSEK, USDCHF, SPXUSD)
python build5m.py XAUUSD XAGUSD EURUSD USDJPY GBPUSD USDCAD USDSEK USDCHF SPXUSD   # -> bars/<PAIR>_5m.pkl (UTC)
python -c "import pandas as pd, gfeat; df=pd.read_pickle('bars/XAUUSD_5m.pkl'); gfeat.features(df).to_pickle('bars/XAUUSD_feat.pkl')"
python xfeat.py      # synthetic US Dollar Index, gold-vs-dollar residual, silver, S&P 500
python univ.py       # every feature vs the next 12 bars (rank correlation, deciles)
python grid1.py      # mean reversion with higher-timeframe trend filters
python costcheck.py  # same rules before costs; ATR by year
python grid2.py      # breakouts (Asian range, NY opening range), Supertrend, EMA pullbacks, time of day
python regime.py     # results split by volatility (ATR in $)
python grid3.py      # gold-vs-dollar divergence reversion (+ silver, + 4h trend)
python grid4.py      # volatility gate, cost sensitivity, year by year
python ml.py         # walk-forward gradient boosting on all ~75 features
python final.py      # the exact rules in gold-5m-scalper.pine (stop 1.5 / target 2 ATR)
python winrate.py    # exit shapes vs. win rate (writes sigL.npy / sigS.npy)
python winrate2.py   # extra entry filters vs. win rate
python winrate3.py   # robustness of the high-win-rate candidates
python rr2.py        # 1:2 risk:reward: stop size, hold time and filter search
python final2.py     # tested 1:2 alternative (stop 1.25 / target 2.5 ATR, 1h trend filter)
python tp12.py       # TP1 / TP2 partial exits, with and without moving the stop to entry
```

`glab.py` is the trade simulator (entry next bar open, stop checked before target,
one trade at a time, flat at session end, costs in $/oz). `dl.py` downloads
Dukascopy minute candles (used only for an abandoned bond-futures test; very slow).
