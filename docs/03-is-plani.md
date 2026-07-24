# İş Planı — AI Destekli Trading Karar Sistemi

Dayanaklar: `docs/01-prompt-analizi.md` (hedef sistemin prompt'u), `docs/02-arastirma-kaynakca.md` (25 repo + 23 makale), `docs/04-pine-inceleme.md` (mevcut gösterge seti).

## 0. Dürüst çerçeve (yönetici özeti)

İki ürün hattı:

- **Hat B (ana hat): Binance Futures AI-destekli karar sistemi.** Kurallı sinyal + risk motoru emir verir; LLM karar DESTEK katmanıdır (haber/rejim/rapor), emir yetkisi yoktur.
- **Hat A (yan hat): Kongre copy-trading, Alpaca paper.** Literatür kopyalama alfasını desteklemiyor (kaynakça §6): STOCK Act sonrası dönemde üstün performans kanıtı yok, 45 güne varan açıklama gecikmesi var, kopyalama ETF'leri (NANC/KRUZ) risk-ayarlı bazda piyasayı yenmiyor. Bu hat **veri mühendisliği + otomasyon portfolyo projesi** olarak değerli; para kazanma iddiasıyla değil.

**Beklenti çıpası:** Literatürdeki parlak AI-trading rakamları ağırlıkla yazarların kendi kısa-pencere backtest'leri; uzun vadeli geniş testte avantaj eriyor (FINSABER). Plan bu yüzden "önce süreç güvenilirliği, sonra küçük sermaye" sırasıyla kurgulandı. Kaldıraçlı kripto türevlerinde anapara tamamen kaybedilebilir — hiçbir faz "kesin kazanç" vaat etmez.

## 1. Ölçülebilir hedefler

| # | Hedef | Ölçüt | Zaman |
|---|---|---|---|
| H1 | Repaint'siz sinyal kütüphanesi (Pine 5in1 portu) | Python sinyalleri ile TradingView değerleri ±%0.1 uyum (NW hariç) | F1 sonu |
| H2 | Güvenilir backtest hattı | Walk-forward, maliyet+funding dahil; aynı config iki koşuda aynı sonuç | F2 sonu |
| H3 | 8+ hafta kesintisiz paper/testnet çalışma | Uptime ≥ %99, sıfır çift-emir, günlük rapor aksamadan | F3 sonu |
| H4 | Go/No-Go kararı verecek veri | Paper dönemi Sharpe, MDD, profit factor raporu vs. BTC buy&hold | F4 kapısı |
| H5 | (Opsiyonel) Canlı mikro-sermaye | Önceden yazılmış risk sözleşmesine %100 uyum | F5 |

## 2. Mimari (katmanlar)

```
[Veri katmanı]      ccxt/borsa WS: OHLCV, funding, open interest │ haber/API
      ↓
[Sinyal katmanı]    Pine 5in1 portu (EMA200-HTF, PMax, Mavilim, Linreg-EP, NW-EP)
                    + FreqAI/istatistiksel model (opsiyonel, F4+)
      ↓
[AI karar destek]   LLM servisi: haber/sentiment özeti, rejim yorumu, günlük brief
                    ⚠ EMİR YETKİSİ YOK — çıktısı sinyal katmanına veto/onay girdisi
      ↓
[Risk motoru]       position sizing, kaldıraç limiti, likidasyon tamponu,
                    kill switch (HWM'den -X%), günlük işlem limiti
      ↓
[Yürütme]           freqtrade (dry-run → testnet → canlı) │ Hat A: Alpaca paper
      ↓
[İzleme/rapor]      log + state dosyaları, Telegram/e-posta özeti, haftalık review
```

Prompt injection kuralı mimariye gömülü: haber/web içeriği LLM'e VERİ olarak gider, içindeki talimatlar yok sayılır; LLM çıktısı da emir API'sine değil risk motoruna gider.

## 3. Teknoloji seçimi ve gerekçe

| Bileşen | Seçim | Gerekçe (kaynakça referanslı) |
|---|---|---|
| Bot çekirdeği | **freqtrade** | 52.6k★, aktif (2026-07), USDT-M futures, backtest+hyperopt+dry-run+canlı tek pakette, FreqAI ML entegre (§2 tablo). GPL-3.0: kendi sunucunda çalıştırmada sorun yok; kodu ürün olarak dağıtırsan copyleft yükümlülüğü. |
| İleri alternatif | nautilus_trader | Nanosaniye backtest, Rust çekirdek; öğrenme eğrisi dik — F6'da yeniden değerlendir |
| Borsa API | ccxt (freqtrade içinde) | binanceusdm sertifikalı; borsa değişikliğinde taşınabilirlik |
| LLM altyapı deseni | TradingAgents/FinRobot'tan DESEN, kod değil | 94.3k★'lık repo bile canlı emir vermiyor (§3 kritik gözlem); rol-ayrımı + debate deseni alınır, emir simülasyonu alınmaz |
| LLM model kademesi | Günlük özet: Haiku/lokal · sinyal-günü analiz: Sonnet · haftalık derin review: Opus | Anayasa §2.1a maliyet disiplini |
| Hat A veri | kadoa-org/congress-trading-monitor (güncel) + resmî eFD/Clerk | Tek aktif günlük-yenilenen kaynak (§1 tablo); resmî kaynak fallback |
| Hat A yürütme | Alpaca paper API | Ücretsiz paper; TR'den hesap durumu §9'a bağlı |

## 4. Fazlar

### F0 — Altyapı ve güvenlik temeli (1 hafta)
Çıktılar: VPS/lokal Docker; freqtrade kurulu; `.env` düzeni; Binance **testnet** anahtarları (withdraw yetkisi olmayan, IP kısıtlı); git repo + bu dokümanlar.
Kabul: dry-run modda bot ayağa kalkıyor; anahtarlar hiçbir dosyada/logda görünmüyor.

### F1 — Sinyal kütüphanesi: Pine 5in1 portu (1-2 hafta)
`docs/04-pine-inceleme.md` §5 tablosuna göre: EMA200-HTF (shift ile non-repaint), MavilimW, PMax (sabit-9 kararı belgelenmiş), Linreg ve NW yalnız endpoint (bar-kapanış) versiyonları. Birim testleri: bilinen veri üzerinde TradingView ile karşılaştırma.
Kabul: H1 ölçütü; repaint testi — sinyal, bar kapandıktan sonra asla değişmiyor.

### F2 — Backtest disiplini (2 hafta)
Confluence iskeleti (04 §6) freqtrade stratejisi olarak; komisyon + funding + slippage modelli; **walk-forward** (örn. 6 ay train / 2 ay test kaydırmalı); en az 3 sembol (BTC, ETH + 1 alt), en az 2 rejim (trend + yatay) dönemi.
Kabul: H2; tek-dönem optimize edilmiş parametrelerin komşu dönemde çökmediği gösterilmiş (overfit raporu, Gort ve ark. dersi).
**Araç durumu:** `scripts/walk_forward.py` hazır (pencere üretimi + koşu + Markdown rapor + GEÇTİ/KALDI eşikleri) ve `--mode sensitivity` ile PMax parametre-ızgara/cliff taraması; pencere-başına hyperopt (gerçek WFO) F2b olarak ayrıldı.

### F3 — Testnet/dry-run maratonu (8+ hafta, paralel geliştirmeyle)
Binance Futures testnet'te kesintisiz çalışma; state dosyası + idempotency; Telegram/e-posta günlük özet ("değişiklik yok" günü tek satır).
Kabul: H3; ayrıca kill switch tatbikatı — simüle -%15'te pozisyonlar kapanıyor, bot duruyor, bildirim geliyor.

### F4 — AI karar destek katmanı (2-3 hafta, F3 ile paralel başlayabilir)
**Araç durumu:** `llm_advisor/` paketi hazır — shadow-mode veto + günlük brief CLI'ı (`python3 -m llm_advisor.cli`), structured-output şemalı Anthropic SDK entegrasyonu, prompt-injection savunması (sabit sistem prompt + `<veri>` bloğu + injection_suspected bayrağı), jsonl shadow log. Katkı ölçümü (aşağıdaki kabul) log üzerinden yapılacak.
LLM servisi ayrı süreç: (a) günlük piyasa brief'i, (b) sinyal geldiğinde haber taraması → "veto/nötr/destek" etiketi + tek paragraf gerekçe, (c) haftalık performans anlatısı. Look-ahead bias dersi (Glasserman-Lin): LLM'e yalnız sinyal anına kadarki bilgi verilir; geçmiş test yaparken model bilgi-kesim tarihi sonrası dönem kullanılır (Lopez-Lira & Tang deseni).
Kabul: veto mekanizması backtest'te ölçülmüş — LLM vetosu net katkı sağlamıyorsa katman "sadece rapor" moduna düşürülür (dürüstlük: katkıyı varsayma, ölç).

### F4 kapısı — GO/NO-GO
Girdi: F3 raporu (Sharpe, MDD, profit factor, BTC B&H kıyası) + §9 regülasyon durumu. Karar: canlıya mikro-sermayeyle geç / paper'a devam / stratejiyi değiştir. **Bu kapıdan yazılı karar çıkmadan canlı hesap anahtarı üretilmez.**

### F5 — (Koşullu) Canlı mikro-sermaye
Kaybı tamamen göze alınan tutar; kaldıraç ≤ 3x; pozisyon başına risk ≤ sermayenin %1'i; likidasyon fiyatına ≥ %30 tampon; funding maliyeti pozisyon raporunda ayrı satır (Borrageiro bulgusu: perpetual'da funding, kâr/zararın ana kalemi olabilir).
Kabul: 4 hafta boyunca risk sözleşmesinden sıfır sapma; sapma = otomatik F3'e dönüş.

### F6 — Hat A: Kongre kopyalama (Alpaca paper) (2 hafta, bağımsız)
**Araç durumu:** `congress/` paketi hazır ve adversarial review'dan geçti (6 kritik + 5 yüksek bulgu düzeltildi). Kapsam: **şu an yalnızca Senato** (senate-stock-watcher şemasında yalnız `senator` alanı var; House Clerk ZIP+XML için ayrı `normalize_house()` gerekir — F6 kapsam notu). Özellikler: FIFO lot eşleme (kısmi satış tüm pozisyonu kapatmaz), Sale(Full)→pozisyon sıfırlama (phantom pozisyon önlemi), açıklama-tarihli sıralama (`--assumed-lag-days`, varsayılan 26), pencere-filtreli min_trades (yalnız son 12 ay), water-filling'li hedef portföy (+%10 tavan/%20 nakit, yatırılamayan bakiye raporlanır), broker-gerçekliğinden okunan delta (lider değişiminde eski pozisyon otomatik satılır), **kill switch fiili tasfiye + kalıcı halted bayrağı** (toparlansa bile manuel reset gerekir), yalnız-long short-sell guard, retry/backoff'lu Alpaca istemcisi, paper-URL bekçisi, elenen-kayıt sayacı, `--leader-filter` (F6b) ve `--fake-equity` (keysiz simülasyon) bayrakları. docs/01 §3'ün 4 kabul kriteri + tüm kritik bulgular test paketinde kilitli (24 test).
`docs/01-prompt-analizi.md`'deki geliştirilmiş prompt uygulanır: veri = House Clerk ZIP+XML (en makine-dostu resmî kaynak) + Senate eFD; kolaylık katmanı congress-trading-monitor/QuiverQuant; sıralama metodolojisi açıklama-tarihli; delta-emir idempotency; her raporda 45-gün gecikme şerhi (pratik medyan ~26 gün).
Kabul: 01 §3'teki 4 kabul kriteri; ek: NANC/SPY kıyas satırı raporda.
**F6b (opsiyonel araştırma deneyi):** Literatürdeki tek test edilmemiş açık kapıyı paper'da dene — genel kopyalama yerine **lider-filtreli kopya** (yalnız parti liderliği pozisyonundaki üyelerin işlemleri; Wei-Zhou 2025 mekanizma ufku 3-12 ay olduğundan 45 günlük gecikmeyi aşabilir). Bu, para beklentisi değil yayınlanabilir bir deney: sonuç ne çıkarsa çıksın değerli (kaynakça §6 net karar).

## 5. Güvenlik ve operasyon (anayasa §1 uygulaması)

- API anahtarları: yalnız `.env`; Binance'te withdraw yetkisi ASLA açılmaz; IP whitelist; testnet/canlı anahtarları ayrı; 90 günde rotasyon.
- Otomatik görevler read-only raporlar; para hareketi içeren her adım (canlıya geçiş, sermaye artışı) insan onayı ister.
- Loglar: her emir öncesi karar gerekçesi (hangi sinyal, hangi risk kontrolü) satır satır — denetlenebilirlik.
- Yedek: state + config günlük off-site; VPS çökerse bot "flat" (pozisyonsuz) başlar, pozisyon devralma manueldir.

## 6. Maliyet tahmini (aylık, USD)

| Kalem | Tutar | Not |
|---|---|---|
| VPS (2 vCPU/4GB) | 5-15 | Hetzner/DO sınıfı |
| Piyasa verisi | 0 | Borsa API ücretsiz katman yeterli |
| Kongre verisi | 0 | GitHub dataset + resmî kaynak; QuiverQuant API'ye geçilirse ~10-75 `[DOĞRULANMASI GEREKİYOR — güncel fiyat]` |
| LLM API | 5-25 | Kademeli model kullanımı (§3); rutin özet lokal modele kaydırılabilir |
| **Toplam** | **~10-40** | Canlı sermaye ve vergi hariç |

## 7. Risk kaydı (uç noktalar)

| Risk | Etki | Önlem |
|---|---|---|
| Backtest overfitting | Canlıda zarar | Walk-forward, OOS zorunlu, parametre-hassasiyet raporu |
| Repaint'li sinyal | Sahte başarı algısı | F1 repaint testi; NW yalnız endpoint |
| Likidasyon (kaldıraç) | Anapara sıfırlanır | ≤3x, %30 tampon, izole margin |
| Borsa riski (erişim/kural değişikliği) | Operasyon durur | ccxt ile borsa taşınabilirliği; flat-start kuralı |
| Regülasyon değişikliği (TR) | Hukuki risk | §9 takibi; şüphede işlem durdurma + danışman |
| Veri kaynağı ToS ihlali (scraping) | Hesap/hukuk riski | Resmî kaynak önceliği; ToS'a saygı (kaynakça §1 notu) |
| LLM halüsinasyonu | Yanlış veto/onay | LLM asla tek başına karar vermez; katkısı ölçülür (F4 kabulü) |
| Anahtar sızıntısı | Fon kaybı | Withdraw kapalı + IP kilidi → sızsa bile para çekilemez |

## 8. Zaman çizelgesi (özet)

```
Hafta:  1    2  3    4  5    6 ... 13   14        15+
        F0 → F1 ───→ F2 ───→ F3 (8 hf) ─→ GO/NO-GO → F5?
                              └ F4 (paralel)
        F6 bağımsız: herhangi bir 2 haftalık boşlukta
```

## 9. Türkiye regülasyon durumu (Temmuz 2026 — detay ve kaynaklar: kaynakça §7)

**Hiçbiri hukuki/vergisel danışmanlık değildir; canlıya geçiş (F4 kapısı) öncesi güncel mevzuat + mali müşavir kontrolü şarttır.**

Plan kararlarını etkileyen beş bulgu:

1. **TR'de yasal kripto futures ürünü yok.** SPK lisanslı platformlarda kaldıraç/türev/açığa satış yasak (7518 + III-35/B tebliğleri). Hat B zorunlu olarak yurt dışı platformda (global Binance) çalışır; kendi hesabına işlem yapan bireye ceza öngören hüküm yok, ama hukuki koruma da yok ve SPK uyumsuz platformlara erişim engeli uygulayabiliyor. → Plana eklenen kural: **borsa-taşınabilirlik (ccxt) baştan mimaride** ve VPN'siz erişilebilirlik F3 izleme metriğine dahil.
2. **TRY giriş-çıkışı Binance TR üzerinden** (Kasım 2025'te TRY pariteleri oraya taşındı; çekimlerde 72 saat bekleme var). Fonlama akışı: TR bankası → Binance TR (spot, TRY→USDT) → global hesaba transfer. 72 saat kuralı acil çekim senaryosuna eklendi (risk kaydı).
3. **Vergi belirsiz ama gelmesi muhtemel.** Temmuz 2026 itibarıyla kriptoya özel vergi yürürlükte değil; Mart 2026'daki %10 stopaj + işlem vergisi teklifi geri çekildi, yeniden gelmesi bekleniyor. → GO/NO-GO kararında getiri hedefi **%10 stopaj senaryosuyla** stres-testlenir; işlem kayıtları vergi beyanına hazır formatta tutulur (zaten loglanıyor).
4. **Hat A (Alpaca paper) TR'den tamamen yasal ve ücretsiz** — paper hesap KYC'siz, sadece e-posta. Canlı ABD hisse hesabı istenirse Alpaca'nın Türkiye uygunluğu tek kaynaklı `[DOĞRULANMASI GEREKİYOR]`; alternatif TR aracı kurumları üzerinden ABD piyasası erişimi.
5. **Sinyal satışı / başkasının parasını yönetmek kırmızı çizgi:** SPK lisansı olmadan suç (izinsiz sermaye piyasası faaliyeti / izinsiz KVHS). Kendi hesabına algo-trading serbest. Proje çıktısı hiçbir aşamada üçüncü kişiye sinyal/yönetim hizmetine dönüştürülmez.
