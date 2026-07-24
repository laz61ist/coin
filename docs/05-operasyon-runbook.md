# Operasyon Runbook — F3 Dry-Run Maratonu ve Günlük İşletim

Bu doküman kodun **nasıl çalıştırılacağı ve izleneceği** içindir. Kod referansı: `README.md`. Plan bağlamı: `docs/03-is-plani.md` (F3, F4 kapısı). Bu bir işletim kılavuzudur, yatırım tavsiyesi değildir.

## 0. Ön koşullar (bir kez)

```bash
git clone <repo> && cd coin
cp .env.example .env          # dry-run için anahtarlar boş kalabilir
docker --version              # compose v2 gerekli
pip install pandas numpy pytest freqtrade   # yerel testler için (opsiyonel)
python -m pytest tests/ -q    # 66+ test yeşil olmalı — değilse başlama
```

Doğrulama zinciri (sırayla, her biri yeşil olmadan sonrakine geçme):
1. `python -m pytest tests/ -q` → tüm birim testler
2. `./scripts/e2e_smoke.sh` → veri + backtest + parser + 60sn dry-run (ağ + docker gerekir, ~10 dk)

## 1. Hat B — Binance Futures dry-run maratonu (F3)

### Başlatma
```bash
docker compose up -d
docker compose logs -f freqtrade | grep -i "dry run is enabled"   # KİLİT: bu satırı görmeden bırakma
```
`Dry run is enabled` logunu görmüyorsan **DUR** — config veya `.env` yanlış; canlı hesap riski. `docker compose down` yapıp incele.

### Günlük kontrol listesi (her sabah ~5 dk)
- [ ] Konteyner ayakta mı: `docker compose ps` → `Up` durumda
- [ ] "Dry run is enabled" logu hâlâ geçerli mi (yeniden başlatma sonrası tekrar kontrol)
- [ ] NaN uyarısı var mı: `docker compose logs --since 24h freqtrade | grep -i "NaN kolonlar"` → **varsa** startup_candle_count/veri geçmişi yetersiz, sinyal üretilmiyor demektir (sessiz susma bug'ının canlı bekçisi)
- [ ] Web arayüzü (açtıysan): http://127.0.0.1:8080 — açık pozisyonlar, dry-run cüzdan
- [ ] Hata/exception yığını: `docker compose logs --since 24h freqtrade | grep -iE "error|traceback|exception"`

### Haftalık (F4 kapısına veri toplama)
- [ ] `docker compose exec freqtrade freqtrade profit` benzeri özet (dry-run P&L)
- [ ] O haftanın işlemlerini not al: sayı, kazanan/kaybeden oranı, max drawdown
- [ ] Kill-switch tetiklendi mi (MaxDrawdown koruması loglarda) — tetiklendiyse **neden** araştır

### Kill-switch tatbikatı (F3 kabulü — bir kez, kasıtlı)
Simüle -%15 drawdown'da botun durduğunu doğrula. Yöntem: test paketinde `test_kill_switch_liquidates_and_stays_halted` (Kongre hattı) bunu kodla kanıtlıyor; freqtrade tarafında `MaxDrawdown` protection'ı config'te (`max_allowed_drawdown: 0.15`). Tatbikat: kısa bir geçmiş dilimde yapay zarar üreten bir backtest koşup protection'ın devreye girdiğini logdan doğrula.

## 2. F2 — Walk-forward raporu üretimi (F3 öncesi/paralel)

```bash
./scripts/download_data.sh 20200601-              # 1h+4h futures veri (funding dahil)
python3 scripts/walk_forward.py                   # reports/walk_forward_YYYYMMDD.md
python3 scripts/walk_forward.py --mode sensitivity   # PMax cliff taraması (yalnız ilk train penceresi)
```
Rapor **KALDI** damgası basıyorsa: strateji bu sembol/dönemde eşiği geçmiyor. F3'e geçmeden en az 3 sembol + 2 rejimde **GEÇTİ** iste. `--cache none` zaten zorunlu (sensitivity sahteciliği önlemi).

## 3. F4 — LLM shadow katmanı (F3 ile paralel)

Shadow mod: LLM görüşü **hiçbir emri etkilemez**, yalnız `logs/llm_advisor/*.jsonl`'a yazılır.
```bash
# Ağsız duman testi (API key gerekmez):
python3 -m llm_advisor.cli veto --input llm_advisor/examples/sinyal_ornek.json --mock
# Gerçek: .env'e ANTHROPIC_API_KEY
python3 -m llm_advisor.cli veto --input <sinyal.json>
```
F4 kabulü: shadow log biriktikçe "LLM vetosu gerçek getiriye katkı sağladı mı?" ölçülür. Katkı yoksa katman rapor moduna düşer (dürüstlük: katkıyı varsayma, ölç).

## 4. Hat A — Kongre kopyalama (Alpaca paper, bağımsız)

```bash
# Keysiz simülasyon önizleme:
python3 -m congress.run --data data/all_transactions.json --prices-json data/prices.json --fake-equity 1000
# Gerçek paper (ALPACA_* + URL 'paper' içermeli):
python3 -m congress.run --data data/all_transactions.json --approve
```
Rapor `reports/congress_YYYY-MM-DD.md`; her koşuda 45-gün şerhi, elenen-kayıt sayacı, sıralama, emirler. Kill-switch tetiklenirse `data/congress_state.json`'da `halted:true` kalır — devam için **manuel** `halted:false`.

## 5. Hata kurtarma

| Belirti | Olası neden | Aksiyon |
|---|---|---|
| "Dry run is enabled" logu yok | config/env yanlış | `docker compose down`, `.env` + config'i incele, ASLA canlıya bırakma |
| "NaN kolonlar" uyarısı | veri geçmişi < startup_candle_count | daha uzun `--timerange` ile veri indir |
| Konteyner sürekli restart | strateji import hatası / bağımlılık | `docker compose logs` → traceback; `python -m pytest` yerelde |
| Disk dolu ("no space left") | eski backtest/veri | `user_data/data/`, `user_data/backtest_results/` temizle (bkz. environment notu) |
| Kongre kill-switch takıldı | -%15 drawdown | state.json'da `halted` sebebini araştır, manuel reset kararı |
| Alpaca `ShortSellBlockedError` | state/broker senkron kaybı | `data/congress_state.json` sil, temiz koşu (broker gerçeğinden yeniden okur) |

## 6. F4 GO/NO-GO kapısı (F3 sonrası — canlıdan önce zorunlu)

8+ hafta dry-run/testnet sonunda yazılı karar:
- **Girdi:** F3 raporu (Sharpe, MDD, profit factor, BTC B&H kıyası) + walk-forward GEÇTİ/KALDI + TR regülasyon güncel durumu (docs/03 §9) + LLM shadow katkı ölçümü.
- **Karar:** GO (mikro-sermaye, ≤3x, yazılı risk sözleşmesi) / paper'a devam / stratejiyi değiştir.
- **Kural:** Bu kapıdan yazılı GO çıkmadan canlı API anahtarı ÜRETİLMEZ. config'teki F4 kontrol listesi (stoploss_on_exchange, api_server env, image pin, --dry-run kaldırma) tek tek uygulanır.
