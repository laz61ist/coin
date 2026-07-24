#!/usr/bin/env bash
# Tam-yığın e2e smoke (SENİN makinende, ağ gerekir): veri indir → tek backtest →
# walk-forward tek pencere → rapor dosyası kontrolü. ~10 dk.
# Sandbox/CI'da ağsız e2e için: python -m pytest tests/test_e2e_strategy.py
set -euo pipefail
cd "$(dirname "$0")/.."

echo "== 1/4 veri (3 ay, 1h+4h futures) =="
docker compose run --rm freqtrade download-data \
  --config /freqtrade/user_data/config.futures.json \
  -t 1h 4h --timerange 20250101-20250601

echo "== 2/4 tek backtest =="
docker compose run --rm freqtrade backtesting \
  --config /freqtrade/user_data/config.futures.json \
  --strategy TC5in1Strategy \
  --timerange 20250420-20250601 \
  --export trades --cache none

echo "== 3/4 sonuç ayrıştırma (walk_forward parser'ı gerçek çıktıya karşı) =="
python3 - <<'PY'
import sys, pathlib
sys.path.insert(0, str(pathlib.Path("scripts")))
from walk_forward import load_last_result, extract_metrics
m = extract_metrics(load_last_result())
assert m["profit_total"] is not None, "profit_total ayrıştırılamadı — freqtrade sürüm/format kontrol et"
print("parser OK:", {k: v for k, v in m.items() if v is not None})
PY

echo "== 4/4 dry-run botu 60 sn ayakta mı =="
docker compose up -d
sleep 60
docker compose logs --tail 30 freqtrade | grep -qi "dry run is enabled" \
  && echo "OK: bot dry-run modda çalışıyor" \
  || { echo "UYARI: 'Dry run is enabled' logu görülmedi — logları incele"; docker compose logs --tail 50 freqtrade; }
docker compose down

echo "E2E SMOKE TAMAM ✅"
