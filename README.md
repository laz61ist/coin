# coin — AI Destekli Trading Karar Sistemi

Araştırma ve planlama dokümanları (branch: `claude/trading-ai-decision-system-wturmo`):

| Doküman | İçerik |
|---|---|
| [docs/01-prompt-analizi.md](docs/01-prompt-analizi.md) | Viral "Kongre copy-trading" demosunun transkripsiyon + 10 zayıf nokta + geliştirilmiş üretim-kalitesi prompt |
| [docs/02-arastirma-kaynakca.md](docs/02-arastirma-kaynakca.md) | 25 GitHub repo (sayfadan doğrulanmış) + 23 akademik makale (derin pass: repo-doğrulamalı, çelişki haritalı) + TR regülasyon + veri ekosistemi |
| [docs/03-is-plani.md](docs/03-is-plani.md) | İki hatlı iş planı: Binance Futures AI karar sistemi (ana) + Kongre kopyalama Alpaca paper (yan); F0-F6 fazlar, GO/NO-GO kapısı, risk kaydı, maliyet |
| [docs/04-pine-inceleme.md](docs/04-pine-inceleme.md) | "Trader Club 5in1" Pine Script incelemesi: bug listesi, repaint riskleri, Python port tablosu, confluence iskeleti |
| [docs/05-operasyon-runbook.md](docs/05-operasyon-runbook.md) | F3 dry-run maratonu işletim kılavuzu: başlatma kilidi, günlük/haftalık kontrol listesi, kill-switch tatbikatı, hata kurtarma tablosu, GO/NO-GO kapısı |

## Üç cümlelik özet

1. **Kongre kopyalama** literatürde para makinesi değil: STOCK Act (2012) sonrası agregat alfa yok, kopyalama ETF'leri (NANC/KRUZ) risk-ayarlı bazda piyasayı yenmiyor — hat, veri mühendisliği portfolyo projesi olarak kurgulandı.
2. **LLM'e emir yetkisi verilmez**: parlak LLM-trading rakamları bağımsız denetimlerde (FINSABER, Profit Mirage) çöküyor; LLM haber/rejim/rapor katmanında, kararı kurallı sinyal + risk motoru verir.
3. **Önce süreç, sonra sermaye**: walk-forward backtest → 8+ hafta testnet → yazılı GO/NO-GO kapısı → ancak ondan sonra mikro-sermaye.

## Hızlı başlangıç (F0 — dry-run, API key gerekmez)

```bash
cp .env.example .env          # anahtarlar boş kalabilir; dry-run public veriyle çalışır
docker compose up -d          # bot: TC5in1Strategy, Binance USDT-M, sahte 1000 USDT
docker compose logs -f freqtrade
```

Sinyal kütüphanesi testleri (freqtrade gerekmez):

```bash
pip install pandas numpy pytest
python -m pytest tests/ -q    # 7 test: davranış + no-lookahead (repaint) sözleşmesi
```

Kod haritası: `user_data/strategies/tc_indicators.py` (Pine 5in1 portu — Mavilim, PMax, NW-endpoint, Linreg-endpoint), `user_data/strategies/TC5in1Strategy.py` (confluence: 4h EMA200 rejim → PMax tetik → Mavilim teyit → NW veto; MaxDrawdown %15 kill-switch; kaldıraç 2x sabit), `user_data/config.futures.json` (dry-run zorunlu).

## F2 — Backtest disiplini

```bash
./scripts/download_data.sh 20210101-        # 1h+4h futures verisi (funding dahil)
python3 scripts/walk_forward.py             # train 6ay / test 2ay kaydırmalı; reports/ altına Markdown rapor
python3 scripts/walk_forward.py --mode sensitivity   # PMax parametre ızgarası + cliff uyarısı
```

Rapor kuralları: pozitif test penceresi ≥ %50 ve pencere MDD ≤ %20 değilse **KALDI** damgası; train kârlı + test zararda pencereler ⚠️ ile işaretlenir (overfit/rejim bağımlılığı işareti). Kabul için ayrıca ≥3 sembol + ≥2 rejim şartı geçerli (docs/03 §4 F2). Hassasiyet taraması bilinçli olarak yalnız İLK train penceresinde koşar (data snooping önlemi) ve tüm backtest'ler `--cache none` ile çalışır.

## F4 — LLM karar destek (shadow mode)

```bash
# Ağsız duman testi (API key gerekmez):
python3 -m llm_advisor.cli veto --input llm_advisor/examples/sinyal_ornek.json --mock

# Gerçek çağrı (.env'e ANTHROPIC_API_KEY yaz):
python3 -m llm_advisor.cli veto --input llm_advisor/examples/sinyal_ornek.json
python3 -m llm_advisor.cli brief --input durum.json
```

Kurallar: LLM'in **emir yetkisi yok** — görüşü (`destek/notr/veto`) sadece `logs/llm_advisor/*.jsonl`'a yazılır; F4 kabulünde katkısı bu logla ölçülür, katkı yoksa katman "sadece rapor" moduna düşer (docs/03 §4). Haber başlıkları `<veri>` bloğunda veri olarak gider; içine gömülü talimatlar uygulanmaz, `injection_suspected` bayrağıyla işaretlenir. Model kademesi: brief=Haiku 4.5, veto=Sonnet 5, haftalık derin review=Opus 4.8 (`TC_LLM_*_MODEL` env'leriyle değiştirilebilir).

## F6 — Kongre kopyalama hattı (Alpaca paper)

```bash
# Veri indir (senate-stock-watcher aggregate, ~50MB):
curl -L -o data/all_transactions.json \
  https://raw.githubusercontent.com/timothycarambat/senate-stock-watcher-data/master/aggregate/all_transactions.json

# Keysiz/ağsız simülasyon önizlemesi (--fake-equity ile sahte hesap):
python3 -m congress.run --data data/all_transactions.json --prices-json data/prices.json --fake-equity 1000

# DRY-RUN — GERÇEK paper hesabı OKUR (equity/pozisyon), emir GÖNDERMEZ (.env'de ALPACA_* gerekir):
pip install yfinance requests
python3 -m congress.run --data data/all_transactions.json

# Paper emirleri gönder (URL 'paper' içermezse bot çalışmayı reddeder):
python3 -m congress.run --data data/all_transactions.json --approve

# F6b lider-filtre deneyi (satır başına bir üye adı):
python3 -m congress.run --data data/all_transactions.json --leader-filter data/leaders.txt
```

Kapsam: **yalnızca Senato** (veri şeması gereği; House ayrı parser ister). Metodoloji dürüstlüğü kodda ve testte kilitli: getiriler **açıklama-tarihli** + **FIFO lot eşleme** ile hesaplanır (kısmi satış tüm pozisyonu kapatmaz; işlem tarihi + 26 gün medyan gecikme, `--assumed-lag-days`); `Sale (Full)` pozisyonu sıfırlar (phantom pozisyon yok); min_trades yalnız son 12 aya bakar; hedef portföyde ticker başına %10 tavan + %20 nakit + water-filling (yatırılamayan bakiye raporlanır); delta broker'ın **gerçek** pozisyonlarından hesaplanır (lider değişince eski pozisyon otomatik satılır); **kill switch pozisyonları fiilen tasfiye eder ve kalıcı `halted` olur** (equity toparlansa bile manuel reset şart); short-sell guard yalnız-long kuralını korur. Her raporda 45-gün STOCK Act şerhi zorunlu. Bu hat portfolyo/deney projesidir — kaynakça §6: genel kopyalamada risk-ayarlı alfa yok.

## E2E testler

İki katman:

```bash
# Katman 1 — ağsız, strateji zinciri gerçek freqtrade API'siyle (CI'da da koşar):
pip install freqtrade pytest && python -m pytest tests/ -q
# freqtrade kurulu değilse e2e otomatik atlanır, 22 birim test yine koşar

# Katman 2 — tam yığın (senin makinende, ağ + docker gerekir, ~10 dk):
./scripts/e2e_smoke.sh   # veri indir → backtest → parser doğrulama → 60sn dry-run
```

Katman 1'in içerdiği sözleşmeler: ısınma sonrası kritik kolonlarda NaN yok (canlıda sessiz-susma bug'ının regresyon kilidi), her iki rejimde sinyal üretimi, giriş maskesi = dokümante confluence mantığı, strateji-seviyesi no-lookahead (seri kısaltılınca kapanmış barların sinyalleri değişmiyor).

Uyarı: Bu depo araştırma/plan dokümanıdır; yatırım tavsiyesi değildir. Kaldıraçlı kripto türevlerinde anapara tamamen kaybedilebilir. `dry_run:false` yapmak F4 GO/NO-GO kapısından yazılı karar gerektirir (docs/03 §4).
