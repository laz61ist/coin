#!/usr/bin/env bash
# F2 veri indirme — Binance USDT-M futures, 1h + 4h (strateji + rejim filtresi).
# Futures modunda freqtrade funding/mark verisini de otomatik indirir (backtest için şart).
set -euo pipefail
cd "$(dirname "$0")/.."

# Varsayılan 2020-06: walk-forward 2021-01'den başlar, öndeki ~7 ay startup_candle_count
# (2500 mum ≈ 104 gün) payıdır — yoksa freqtrade ilk pencereyi sessizce kırpar.
TIMERANGE="${1:-20200601-}"

docker compose run --rm freqtrade download-data \
  --config /freqtrade/user_data/config.futures.json \
  -t 1h 4h \
  --timerange "${TIMERANGE}"

echo "OK: veri user_data/data/binance altında. Walk-forward için: python3 scripts/walk_forward.py"
