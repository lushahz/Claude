#!/bin/bash
# Binance spot 1h klines, monthly archives
mkdir -p zips
for s in BTCUSDT ETHUSDT SOLUSDT BNBUSDT XRPUSDT ADAUSDT DOGEUSDT LINKUSDT AVAXUSDT LTCUSDT DOTUSDT TRXUSDT; do
  for y in 2019 2020 2021 2022 2023 2024 2025 2026; do for m in 01 02 03 04 05 06 07 08 09 10 11 12; do
    f=zips/$s-1h-$y-$m.zip
    [ -s $f ] && continue
    echo "https://data.binance.vision/data/spot/monthly/klines/$s/1h/$s-1h-$y-$m.zip $f"
  done; done
done | xargs -P 8 -n 2 sh -c 'curl -s -f -m 60 -o "$1" "$0" || rm -f "$1"'
ls zips | wc -l
