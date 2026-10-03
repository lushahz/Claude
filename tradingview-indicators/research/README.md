# Research scripts

Python code behind [`../REVERSAL_RESEARCH.md`](../REVERSAL_RESEARCH.md).

```bash
pip install pandas numpy
python fetch_daily.py   # downloads daily data for the 47 markets into this folder
python -c "import pickle, features; pickle.dump(features.all_data(), open('data.pkl', 'wb'))"
python profile.py       # indicator readings at major bottoms / tops vs all days
python round2.py        # buy-trigger variants: in-sample 2010-18 vs out-of-sample 2019-26
python fullbt.py        # long-only backtests with different exits
```

- `revdots.py`: Pine-equivalent EMA / RMA / RSI / Stoch and WaveTrend.
- `features.py`: features and the volatility-scaled swing detector.
- `round2.py`: `buy_v()` is the final BUY rule (`confirm="within3", rearm=True, wave=-53, rsi_=40`).
- `fullbt.py`: `signals_for()[1]` is the TAKE-PROFIT rule.
