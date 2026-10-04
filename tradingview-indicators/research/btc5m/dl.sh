#!/bin/bash
# Binance public archives: spot 5m BTC/ETH, futures UM 5m BTC klines, premium index 5m, funding rate
B=https://data.binance.vision/data
mkdir -p spot fut prem fund
for y in 2020 2021 2022 2023 2024 2025 2026; do for m in 01 02 03 04 05 06 07 08 09 10 11 12; do
  for s in BTCUSDT ETHUSDT; do echo "$B/spot/monthly/klines/$s/5m/$s-5m-$y-$m.zip spot/$s-5m-$y-$m.zip"; done
  echo "$B/futures/um/monthly/klines/BTCUSDT/5m/BTCUSDT-5m-$y-$m.zip fut/BTCUSDT-5m-$y-$m.zip"
  echo "$B/futures/um/monthly/premiumIndexKlines/BTCUSDT/5m/BTCUSDT-5m-$y-$m.zip prem/BTCUSDT-5m-$y-$m.zip"
  echo "$B/futures/um/monthly/fundingRate/BTCUSDT/BTCUSDT-fundingRate-$y-$m.zip fund/BTCUSDT-fundingRate-$y-$m.zip"
done; done | xargs -P 8 -n 2 sh -c '[ -s "$1" ] || curl -s -f -m 180 -o "$1" "$0" || rm -f "$1"'
for d in spot fut prem fund; do echo $d $(ls $d | wc -l); done; du -sh .
