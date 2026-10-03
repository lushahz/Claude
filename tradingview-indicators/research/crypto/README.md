# Crypto research scripts

Python code behind [`../../CRYPTO_RESEARCH.md`](../../CRYPTO_RESEARCH.md).

```bash
pip install pandas numpy
python fetch_crypto.py   # 29 coins, daily, from Yahoo Finance
python fetch_macro.py    # TOTAL, BTC.D (CoinMarketCap) and USDT.D (Coin Metrics)
python lab.py            # features + Bitcoin context -> cdata.pkl
python engine.py         # (module) buy / take-profit rules and backtester
python regime.py         # cycle guard and dead-money exits
python macrotest.py      # TOTAL / BTC.D / USDT.D filters and exits
python macro2.py         # combined guards
python final.py          # final crypto rules, yearly breakdown, recent signals
```
