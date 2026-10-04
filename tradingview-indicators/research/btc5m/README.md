# BTC 5-minute research scripts

Python code behind [`../../BTC5M_RESEARCH.md`](../../BTC5M_RESEARCH.md).

```bash
pip install pandas numpy numba scikit-learn
./dl.sh            # Binance public archives: BTC/ETH spot 5m, BTC futures 5m, premium index, funding
python build.py    # merge into btc5m_raw.pkl
python feat.py     # 62 features -> btc5m_feat.pkl
python univ.py     # which features predict the next 1 / 3 hours, by period
python grid1.py    # reversal entries x exits x fees
python ml.py 2 1 36  # walk-forward gradient boosting filter
python volx.py     # results by volatility bucket and exit width
python tp3.py      # (module) TP1/TP2/TP3 simulator; run directly for the gated grid
python filt.py     # filters on the early-turn signal, year by year
python combo.py    # filter combinations
python holdout.py  # the one-time 2025-26 hold-out test of the two pre-registered candidates
python final_b.py  # TP structures chosen on 2020-24 only; per year / side
python final.py    # the exact defaults of btc-5m-reversal-dots.pine
```
