# Araştırma Kaynakçası — Trading AI Karar Sistemi

## 0. Metodoloji ve dürüstlük notu (önce bunu oku)

Araştırma iki pass'te yürütüldü:

**Pass 1 (genişlik):** 3 GitHub repo tarayıcı + 3 akademik makale tarayıcı + TR regülasyon + ekosistem ajanı (paralel).
**Pass 2 (derinlik):** 23 makale 5 derin-okuma ajanına paylaştırıldı — makale başına ≥4 farklı arama açısı (metodoloji / somut metrikler / eleştiri-replikasyon / resmî kod reposu) + makalelerin GitHub repolarının TAM okunması (README, config, kod). TR regülasyonu tek ajan + iddia başına çift-kaynak çapraz kontrolle yeniden araştırıldı (ilk pass'in 2 adversarial doğrulayıcısı container yeniden başlatmasında öldü).

**Ağ kısıtı (kritik):** Ortamın ağ politikası github.com ve raw.githubusercontent.com dışındaki siteleri engelliyor (arxiv, sciencedirect, springer, mdpi, ssrn, doi.org, spk.gov.tr dahil — CONNECT-403, bizzat doğrulandı). Sonuçları:

- GitHub verileri (yıldız, lisans, commit, README, config dosyaları) **tam okundu** — güvenilir.
- Makale gövdeleri (bir istisnayla) tam okunamadı. Anayasa §5.2 dürüst sayım: **tam okunan makale 1/23** (Eggers & Hainmueller 2013 — GitHub mirror PDF'inden 17 sayfa tam okuma); kalan 22'si "çok kaynaklı snippet + repo tam okuması" düzeyinde. Her sayısal metrik, kaç bağımsız kaynakta görüldüğüne göre `[çapraz]` veya `[DOĞRULANMASI GEREKİYOR]` etiketli.
- Derin pass iki arama-özetleyici halüsinasyonu yakalayıp AYIKLADI: (a) "%8,8 hedge getirisi" Belmont'a değil Cherry-Heitz-Jens (SSRN 2905309) çalışmasına aitti; (b) "NANC=Nanoco Group, KRUZ=Cruise LLC" uydurması. İkisi de rapora alınmadı.
- DOI'ler script ile doğrulanamadı (doi.org engelli); arama ile teyit edilen DOI'ler ayrıca işaretlendi.
- Tam-metin pass'i için: environment network policy genişletilmeli veya tarama claude.ai üzerinden tekrarlanmalı.

## 1. GitHub — Kongre copy-trading repoları

| Repo | ★ | Dil | Lisans | Son aktivite | Değerlendirme |
|---|---|---|---|---|---|
| [kadoa-org/congress-trading-monitor](https://github.com/kadoa-org/congress-trading-monitor) | 112 | JS | MIT | 2026-07-23 (günlük otomatik yenileme) | En güncel veri kaynağı adayı; dashboard+dataset, emir katmanı yok |
| [neelsomani/senator-filings](https://github.com/neelsomani/senator-filings) | 414 | Python | MIT | 2022-01 | Alanın en yıldızlısı; eFD parser tasarımı için referans, bakımsız |
| [timothycarambat/senate-stock-watcher-data](https://github.com/timothycarambat/senate-stock-watcher-data) | 96 | — | — | 2021-03 | Hazır JSON tarihsel veri — backtest için; taranmış-PDF boşlukları belgelenmiş |
| [johnisanerd/Apify-Congressional-Trading-Data-Scraper](https://github.com/johnisanerd/Apify-Congressional-Trading-Data-Scraper) | 9 | Python | MIT | 2026-07-22 | Aktif, MCP entegrasyonlu; Apify'a (ücretli servis) bağımlı |
| [heils/congress-watcher](https://github.com/heils/congress-watcher) | 0 | Python | — | 2026-06-23 | "Yeni işlem tespit → tetik" kalıbı; kişisel proje, üretime alma |
| [MajesticBison/pelosi-trade-tracker](https://github.com/MajesticBison/pelosi-trade-tracker) | 1 | Python | MIT | 2025-09 | House Clerk PDF parse hattı örneği |
| [TommasoAmici/capitoltrades](https://github.com/TommasoAmici/capitoltrades) | 2 | Rust | MIT | 2024-04 | capitoltrades.com gayriresmî API client'ı; kırılganlık riski |
| [xSurus/rusty_trader](https://github.com/xSurus/rusty_trader) | 2 | Rust | — | 2022-12 | "Kongre → kopyala" birebir kavram kanıtı; ölü proje, mimari referans |
| [jeremiak/us-senate-financial-disclosure-scraper](https://github.com/jeremiak/us-senate-financial-disclosure-scraper) | 23 | JS | — | 2022-07 | HTML+taranmış PDF işleme referansı |
| [P-H-B-D/CapitolTradesScraper](https://github.com/P-H-B-D/CapitolTradesScraper) | 3 | Python | — | 2022-01 | README'si bizzat 2iQ ToS ihlal riskine dikkat çekiyor (README tam okundu) |

**Sonuç:** Hazır üretim kalitesinde Kongre-kopyalama botu YOK. Aktif olanlar veri katmanı; emir/risk katmanı bize kalıyor (iş planı F6).

## 2. GitHub — Binance Futures bot framework'leri

| Repo | ★ | Lisans | Son aktivite | Binance Futures | Değerlendirme |
|---|---|---|---|---|---|
| [freqtrade/freqtrade](https://github.com/freqtrade/freqtrade) | 52.6k | GPL-3.0 | 2026-07-23 | ✅ USDT-M | Backtest+hyperopt+dry-run+canlı; FreqAI ML katmanı; en olgun topluluk |
| [ccxt/ccxt](https://github.com/ccxt/ccxt) | 43.4k | MIT | 2026-07-23 | ✅ binanceusdm sertifikalı | Bot değil, borsa API katmanı; her botun altında |
| [nautechsystems/nautilus_trader](https://github.com/nautechsystems/nautilus_trader) | 24.9k | LGPL-3.0 | 2026-07-23 | ✅ USDT-M + COIN-M "stable" | Rust çekirdek, nanosaniye backtest; öğrenme eğrisi dik |
| [hummingbot/hummingbot](https://github.com/hummingbot/hummingbot) | 19.2k | Apache-2.0 | 2026-06-16 | ✅ binance_perpetual | Odak market-making/HFT; klasik backtest zayıf |
| [jesse-ai/jesse](https://github.com/jesse-ai/jesse) | 8.2k | MIT | 2026-07-13 | ✅ perpetual (docs — confidence: medium) | Temiz strateji API'si, iyi backtest; topluluk orta |
| [Drakkar-Software/OctoBot](https://github.com/Drakkar-Software/OctoBot) | 6.3k | GPL-3.0 | 2026-07-17 | ✅ futures (README) | Web arayüzlü, başlangıç dostu |
| [binance/binance-futures-connector-python](https://github.com/binance/binance-futures-connector-python) | 1.2k | MIT | 2025-07-18 | ✅ /fapi resmi | DEPRECATED — yeni projede kullanma |

**Sonuç:** Hat-B çekirdeği birincil aday **freqtrade**, ileri seviye alternatif **nautilus_trader**. Gerekçe iş planında.

## 3. GitHub — AI/LLM/RL trading repoları

| Repo | ★ | Lisans | Son aktivite | Değerlendirme |
|---|---|---|---|---|
| [TauricResearch/TradingAgents](https://github.com/TauricResearch/TradingAgents) | 94.3k | Apache-2.0 | 2026-07-18 | Çok-ajanlı LLM; SİMÜLE emir — canlı trade yok, "research purposes" disclaimer'lı |
| [virattt/ai-hedge-fund](https://github.com/virattt/ai-hedge-fund) | 62.4k | MIT | 2026-07-23 | Persona-bazlı LLM analiz; "gerçek trade yapmaz" — eğitim amaçlı |
| [microsoft/qlib](https://github.com/microsoft/qlib) | 46.6k | MIT | 2026-07-23 | Kurumsal kalite quant altyapı + RD-Agent; kripto odaklı değil |
| [AI4Finance-Foundation/FinGPT](https://github.com/AI4Finance-Foundation/FinGPT) | 20.9k | MIT | 2026-07-23 | Finansal LLM altyapısı; sentiment/haber katmanı, karar motoru değil |
| [AI4Finance-Foundation/FinRL](https://github.com/AI4Finance-Foundation/FinRL) | 15.8k | MIT | 2026-07-13 | RL pipeline; Binance/CCXT veri + Alpaca paper deploy örnekleri; "araştırma" konumlaması |
| [AI4Finance-Foundation/FinRobot](https://github.com/AI4Finance-Foundation/FinRobot) | 7.6k | Apache-2.0 | 2026-07-07 | LLM yatırım araştırma otomasyonu; "sayılar kodla, anlatı LLM'le" prensibi |
| [AI4Finance-Foundation/FinRL-Meta](https://github.com/AI4Finance-Foundation/FinRL-Meta) | 1.9k | MIT | 2026-07-13 | RL benchmark ortamları (Binance/CCXT); spot odaklı |
| [pipiku915/FinMem-LLM-StockTrading](https://github.com/pipiku915/FinMem-LLM-StockTrading) | 928 | MIT | 2024-08 (bakımsız) | Katmanlı bellekli LLM ajan referans kodu; sadece backtest |

**Kritik gözlem:** En yıldızlı LLM-trading repoları bile canlı emir vermiyor. Derin pass bunu güçlendirdi (aşağıda §5): TradingAgents repo'su makale konfigürasyonundan kopmuş, FinAgent repo'su fiilen yarım, FinMem proprietary veri duvarında. Üretim olgunluğu klasik framework'lerde (freqtrade/nautilus).

## 4. Akademik — RL/ML ile kripto/futures trading (derin pass işlendi)

Etiketler: `[çapraz]` = ≥2 bağımsız kaynakta aynı değer; `[tek kaynak]` = tek snippet zinciri; tümü yazar beyanı (bağımsız ölçüm ayrıca belirtildi).

1. **Gort ve ark. (2022/23)** — *Practical Approach to Address Backtest Overfitting.* arXiv:2209.05559 (AAAI 2023 Bridge). PBO hipotez testi; CPCV vs KCV vs WF. **Repo config'i tam okundu** (berendgort/FinRL_Crypto): Binance 5m, 10 USDT paritesi, train 20000 + val 5000 mum, test 2022-04-30→06-27 (~2 ay, LUNA çöküşü dahil), H_TRIALS=50. Az-overfit ajan endeksi geçiyor `[çapraz]` ama sayısal Sharpe tablosu erişilemedi; "%46 overfitting azaltımı" yalnız yazar kaynaklarında. Config'de işlem ücreti parametresi YOK. Ders: CPCV yaklaşımı F2'ye alınacak; rakamlarına değil yöntemine güven.
2. **Borrageiro ve ark. (2022)** — *Recurrent RL Crypto Agent.* IEEE Access, doi:10.1109/ACCESS.2022.3166599 (arama ile teyitli). BitMEX XBTUSD perpetual, ~5 yıl, maliyet-sonrası **%350 toplam getiri; kârın %71'i funding'den; IR 1.46** `[çapraz — üç bağımsız veritabanı]`. Tek varlık/borsa; resmî kod yok; bağımsız replikasyon yok. **Planın en değerli dersi: perpetual'da funding, yön tahmininden daha güvenilir kâr kaynağı olabilir.**
3. **Qin ve ark. (2025)** — *FineFT.* arXiv:2512.23773, KDD '26 kabul. Ensemble TD + VAE "yetkinlik sınırı" + konservatif politika. **Ortam kodu tam okundu** (qinmoelei/FineFT_code_space/base_env.py): komisyon 2bps, kaldıraç [5x], funding mark-price üzerinden. 12 baseline'ı geçme + riski >%40 azaltma `[çapraz]`; test ~7 ay `[tek kaynak]`. Replikasyon bariyeri: Tardis verisi ücretli, ~800 GB/parite.
4. **Chun & Lee (2025)** — *Crypto Futures Portfolio Trading Using RL.* Applied Sciences, doi:10.3390/app15179400 (arama teyitli). A2C, Binance Futures 18 kripto. Eğitim: HF %16-17 vs günlük %6-7 `[çapraz]`; test 2023H2: düşük frekans %43.06 vs HF %5.68 `[tek kaynak]`. **Kendi beyanı: Sharpe/MDD yok** — volatil piyasada kritik eksik; eğitim/test rejim farkı bulgularını şüpheli kılıyor.
5. **Wang & Klabjan (2023)** — *Ensemble DRL for Crypto.* arXiv:2309.00626; IEEE 10634436. Mixture-distribution policy + periyodik yeniden eğitim. Rakamlar (ensemble yıllık 0.93/Sharpe 1.07 vs B&H 0.76/0.81) `[DOĞRULANMASI GEREKİYOR — tek snippet, ikinci aramada teyit edilemedi]`. **Resmî kod YOK** (yazar GitHub'ı boş — doğrulandı) → replikasyon fiilen engelli; 2020-21 boğa bağımlılığı kendi kabulü.
6. **Sadighian (2019)** — *DRL in Crypto Market Making.* arXiv:1911.08647 (preprint, dergi yayını yok). **Repo tam okundu** (sadighian/crypto-rl): reward.py makaledeki trade_completion ödülünü birebir içeriyor (ücret açıkça modelli) ama makalenin A2C/PPO ajanları repoda YOK (repo DQN); "Research only, no live-trading"; TF 1.13 — bugün çalıştırmak zor. Sayısal performans tablosu hiçbir kaynaktan çıkarılamadı.
7. **Jiang, Xu, Liang (2017)** — *DRL Framework for Portfolio Management.* arXiv:1706.10059. **Resmî config tam okundu** (PGPortfolio/net_config.json): Poloniex 30dk, 11 coin, komisyon %0.25, sıfır slippage/likidite modeli. Abstract: 50 günde ≥4x `[çapraz]`. **README itirafları:** v2'de test süresi ~%30 kısa yazılmış "teknik hata"; kod makaleden ileride. **Replikasyon karnesi karışık:** wassname bağımsız implementasyonu "eğitimdeki kazanç test verisinde kayboldu, replike edemedim"; akaniklaus "poor results"; Li (2024, arXiv:2409.08426) resmî ayarlarla replike ettiğini raporluyor. Net: kod-backtest üretilebilir, **ekonomik sonuç genellenemedi.**
8. **Pippas ve ark. (2024/25)** — *Evolution of RL in Quant Finance: Survey.* arXiv:2408.10932; **ACM Computing Surveys 57(11) Art.295, DOI 10.1145/3733714 arama ile doğrulandı**; Warwick WRAP açık erişim. 167 yayın `[çapraz]`. Alanın kusur listesi (snippet-doğrulanan): temsil imkânsızlığı → öznel feature engineering, overfitting, keşif-maliyet gerilimi, sim-to-real boşluğu, yorumlanabilirlik/regülasyon.

**Derin pass sonrası sentez:** RL-kripto pozitif sonuçlarının hiçbirinde bağımsız replikasyon başarısı yok; alanın klasiği (Jiang 2017) bağımsız implementasyonlarda üretilemedi. En sağlam iki taşınabilir ders: (a) CPCV/PBO tarzı overfitting kontrolü (Gort), (b) funding'in kâr kalemi olarak ciddiye alınması (Borrageiro — kârın %71'i). İkisi de iş planına işlendi.

## 5. Akademik — LLM trading ajanları (derin pass işlendi)

1. **TradingAgents (2024)** — arXiv:2412.20138 (AAAI'25 WS + ICML'25 poster). AAPL %26.62 / Sharpe 8.21, GOOGL %24.36/6.39, AMZN %23.21/5.60 `[çapraz]` — AMA: 3 aylık tek boğa penceresi (2024Q1; sürümler arası dönem tutarsızlığı var), 3-5 mega-cap, **net-of-cost YOK** (arXiv:2603.27539 bu yüzden eleştiriyor: "5 minimum değerlendirme standardından 1'i; elverişli rejimde trend takibi, alpha değil"). **Repo tam okundu:** "research purposes" disclaimer; canlı trade yok (simulated exchange); default_config bugün başka modelde — **makale deneyi güncel kodla yeniden üretilemez.**
2. **FinMem (2023)** — arXiv:2311.13743 (ICLR'24 WS + AAAI-SS). TSLA Sharpe 2.68 `[tek kaynak]`; test dönemi GPT-4 eğitim verisiyle çakışık → leakage riski yüksek. **FINSABER yeniden koştu: boğada Sharpe -0.19, ayıda -0.97; B&H çoğu sembolde eşit/üstün.** arXiv:2603.27539: MSFT +%23.26 bulgusu başka eşit-savunulabilir pencerede maliyetle **-%22.04'e dönüyor.** Repo: proprietary Refinitiv verisi + eksik dosyalar → birebir replikasyon duvarda; disclaimer yok.
3. **FinGPT (2023)** — arXiv:2306.06031 (FinLLM WS @ IJCAI). Trading backtest iddiası YOK — framework makalesi. **Repo README tam okundu:** sentiment W-F1 FPB 0.882 (GPT-4: 0.833); fine-tune maliyeti v3.3 $17.25 `[kendi beyanı, çapraz]`. Eleştiri (arXiv:2507.08015): finansal QA EM %28 vs GPT-4 %76; hisse yön tahmini %45-53 (yazı-tura); "sürekli hold" eğilimi. Dördü içinde en yeniden-üretilebilir repo.
4. **FinAgent (2024)** — **KDD 2024, DOI 10.1145/3637528.3671801 arama ile doğrulandı.** Multimodal + reflection + tool use; ort. >%36 iyileşme `[çapraz]`; ETHUSD'de FinMem'in gerisinde (kripto genellemesi zayıf — kendi kabulü). **FINSABER yeniden koştu: boğa 0.12 (pasifin altında), ayı -0.38.** **Repo tam okundu:** 7 commit, kritik issue'lar çözümsüz, README'de makale atıfı yok — deneyler uçtan uca yeniden üretilemez.
5. **Lopez-Lira & Tang (2023-25)** — arXiv:2304.07619 v6; **JFE yayını (2026) `[DOĞRULANMASI GEREKİYOR — iki bağımsız arama özeti, DOI dizgisi görülmedi]`**. ~4.123 hisse, >134k başlık, Eki 2021→May 2024 — örneklem model cutoff'undan SONRA (referans tasarım). ~%90 isabet **non-tradable ilk tepki için**; işlem yapılabilir kısım maliyet-öncesi drift (Sharpe ~3.8 `[tek ikincil kaynak]`). **Yazarların kendi bulgusu: LLM yaygınlaştıkça strateji getirisi eriyor.**
6. **Glasserman & Lin (2023/24)** — arXiv:2309.17322; **JFDS 6(1):25-42; SSRN DOI 10.2139/ssrn.4586726 doğrulandı.** 129k+182k başlıkta anonimleştirme deneyi. **Sürpriz ana bulgu `[çapraz]`: anonimleştirilmiş başlıklar orijinalden DAHA İYİ performans veriyor → distraction effect > look-ahead bias.** Tablo düzeyi rakamlar erişilemedi (dürüst boş). Sonraki literatür: anonimleştirme tek başına yetmez, memorizasyon ayrıca test edilmeli (Look-Ahead-Bench, MemGuard-Alpha).
7. **FINSABER (2025)** — arXiv:2505.07078; **KDD 2026 ORAL, DOI 10.1145/3770854.3785702 doğrulandı; repo tam okundu** (waylonli/FINSABER, Apache-2.0, kod+veri açık). 2004-2024, 100+ sembol, delist dahil; next_open execution, %2.5 ADV likidite tavanı, slippage, LLM maliyet muhasebesi. **Ana bulgu `[çapraz]`: LLM timing stratejileri uzun vadede anlamlı alfa üretemiyor; boğada aşırı temkinli, ayıda aşırı agresif.** Önerisi planımızla birebir: karmaşıklık yerine trend tespiti + rejim-farkındalıklı risk kontrolü. FinMem/FinAgent yazarlarından rebuttal bulunamadı.
8. **Ding ve ark. (2024/26)** — *LLM Agent in Financial Trading: Survey.* arXiv:2408.06361 v2. Literatürdeki %15-30 getiri farkı iddiaları orijinal makalelerin kendi beyanı. Alan kusurları `[çapraz]`: ABD/Çin dar evreni, kısa dönem, maliyetsiz simülasyon, temporal leakage; arXiv:2606.08285: yalnız küçük azınlık çalışmada zaman-tutarlı train/test + açık maliyet modeli + survivorship kontrolü.

**Derin pass sonrası sentez (planın LLM kararının kanıt tabanı):** Parlak LLM-trading rakamları üç bağımsız denetimde çöküyor — FINSABER (uzun dönem/geniş evren), Profit Mirage arXiv:2510.07920 (pretraining leakage: cutoff sonrası getiriler istatistiksel sıfır), 2603.27539 (pencere seçimi + maliyet). En sağlam pozitif bulgu bile (Lopez-Lira & Tang, JFE) işlem yapılamaz ilk tepkide yoğunlaşıyor ve yazarlarca "eriyor" raporlanıyor. **Sonuç: LLM'e emir yetkisi verilmez; haber/rejim/rapor katmanı + ölçülen veto. Bu artık tercih değil, literatür bulgusu.**

## 6. Akademik — Kongre üyesi işlemleri ve kopyalama (derin pass işlendi; E&H TAM okundu)

1. **Ziobrowski ve ark. (2004)** — *U.S. Senate.* JFQA 39(4), DOI 10.1017/S0022109000003161 (arama teyitli). 1993-98: alım portföyü +85bp/ay `[çapraz]`. **E&H tam metninden eleştirisi:** meşhur "%12/yıl" 8 spesifikasyondan yalnızca 1'inde; en fazla 3/8 anlamlı; **4 senatör tüm işlemlerin ~yarısı**; yazarlar veriyi paylaşmayı reddetti. Kıdemsizler kıdemlilerden iyi (sonraki literatürle çelişen ayrıntı).
2. **Ziobrowski ve ark. (2011)** — *U.S. House.* Business and Politics 13(1), DOI 10.2202/1469-3569.1308 (arama teyitli). 1985-2001 (tek yıllar): alım +55bp/ay `[çapraz]`. **E&H'nin öldürücü tespiti: SATILAN hisseler de alınanlar kadar iyi performans göstermiş → hedge ≈ 0; "bilgili işlem kanıtı aslında yok"** — manşet bulgu makalenin kendi tablolarıyla çelişiyor; hedge getirisi hiç raporlanmamış.
3. **Eggers & Hainmueller (2013)** — *Capitol Losses.* J. Politics 75(2), DOI 10.1017/S0022381613000194. **TAM METİN OKUNDU** (17 sayfa, GitHub mirror). 2004-08, 422 üye, 48.309 işlem; literatürde İLK **gerçek portföy rekonstrüksiyonu** (sentetik değil). Bulgular: Carhart alfa **-0,23%/ay (p≤.02) ≈ -%2,76/yıl**; $100 → $69 vs piyasa $80; **88 alt-grup alfasının SIFIRI pozitif-anlamlı** (güç komiteleri ve liderler dahil; House liderleri -%6,12/yıl); medyan portföy deviri %23/yıl → üyeler hisseyi sentetik 12-ay varsayımından çok daha uzun tutuyor, yani Ziobrowski rakamları üyelerin gerçek kazancını ölçmüyor.
4. **Belmont ve ark. (2022)** — *Evidence from the STOCK Act.* J. Public Economics 207 (PII S0047272722000044 teyitli). 2012-2020 PTR verisi: senatör alımları 1/3/6 ayda -11/-28/-17bp; House alım -26bp, satım -11bp `[çapraz]`; **95. ve 99. persantil bile rastgele seçimle tutarlı; komite-sektör avantajı yok.** Veri hijyeni: bir arama özetinin Belmont'a atfettiği "%8,8 hedge getirisi" aslında Cherry-Heitz-Jens'e ait çıktı — ayıklandı.
5. **Karadas (2019)** — *Trading on Private Information.* Financial Review 54(1), DOI 10.1111/fire.12180 (teyitli). 61.998 işlem, 2004-10. Güçlü Cumhuriyetçilerin al-eksi-sat portföyü >%35/yıl `[çapraz]` — **ama 1 HAFTALIK tutma ufkunda**; tecrübesizlerde yoğun; **2012 sonrası kayboluyor** `[çapraz]`. 45 günlük açıklama gecikmesi bu ufku tanım gereği kaçırır: bu alfa dışarıdan hiçbir zaman kopyalanabilir değildi.
6. **Baulkaran & Jain (2025)** — *A case of NANC and KRUZ.* Economics Letters 250, DOI 10.1016/j.econlet.2025.112263 (RePEc teyitli). **Gecikmeli kopyalamanın tek gerçek-dünya testi** (ETF'ler fiilen PTR gecikmesiyle kopyalıyor): NANC ~%27 / KRUZ ~%13 ham getiri `[çapraz]` ama **Sharpe bazında ikisi de piyasayı yenemiyor** `[çapraz]`; NANC-S&P korelasyonu 0,95 `[tek kaynak]` — portföyler büyük ölçüde piyasanın kendisi. Sınır: 12 aylık tek boğa yılı.
7. **Wei & Zhou (2025)** — *"Captain Gains".* NBER WP 34524 (numara teyitli; hakemsiz working paper). Liderliğe yükselen **~20 üye** yükselme sonrası eşlerini **+47 puan/yıl** geçiyor `[5+ kaynak çapraz]`; mekanizma ufku 3-12 ay (satışlar düzenleyici eylemlerden önce; alımlar ihale/parti-destekli şirketlerde). N=20 → Z2004'teki "4 senatör" problemiyle aynı yapısal risk; **gecikmeli lider-kopyası hiçbir çalışmada test edilmedi** `[DOĞRULANMASI GEREKİYOR]`.

**Çelişki haritası (derin pass):** (a) *Dönem ekseni:* alfa iddiaları pre-2012'ye ait; post-2012 null. (b) *Yöntem ekseni:* sentetik işlem portföyü vs gerçek holding (yalnız E&H); kısa-ufuk zamanlama becerisi ile uzun-ufuk servet farklı şeyler ölçer — Karadas ile E&H aynı yıllarda zıt anlatı kurup ikisi de "doğru" olabilir, ama kopyalanabilirlik için belirleyici olan E&H sonucudur. (c) *Alt-grup ekseni:* avantaj her bulunduğunda dar bir grupta ama grup çalışmadan çalışmaya değişiyor (kıdemsizler → güçlü Cumhuriyetçiler → liderler) — alt-grup iddiaları birbirini DOĞRULAMIYOR ve E&H 88 alt-grubun sıfırında pozitif-anlamlı alfa bulmuş durumda. Açık çelişki: E&H (liderler negatif, 2004-08) ⟂ Wei-Zhou (liderler +47pp, 1995-2021) — çözülmemiş.

**Net karar ("45 gün gecikmeli kopyalama işe yarar mı?"):** Genel strateji için **HAYIR** — kopyalanacak alfa post-2012 agregatta yok (Belmont), pre-2012 alfa ya ağırlıklandırma artefaktı (E&H yeniden-yorumu) ya 1-haftalık ufukta (Karadas), gecikmeli kopyanın tek gerçek testi risk-ayarlı sıfır (NANC/KRUZ). Tek açık kapı **lider-filtreli gecikmiş kopya** (Wei-Zhou mekanizma ufku 45 günü aşabilir) — ama bu **test edilmemiş bir hipotez**; yatırım kararı değil, olsa olsa Hat A'da paper-trading deneyi olur.

## 7. Türkiye regülasyonu ve veri ekosistemi (derin pass — iddia başına çift-kaynak çapraz kontrol)

> Yöntem notu: resmî siteler (spk.gov.tr, resmigazete.gov.tr) ağ kısıtıyla doğrudan açılamadı; bulgular çok kaynaklı arama çapraz kontrolüyle derlendi. Yüksek riskli tekil iddialar `[DOĞRULANMASI GEREKİYOR]` etiketli. **Hiçbiri hukuki/vergisel danışmanlık değildir.**

### 7.1 Türkiye regülasyonu (Temmuz 2026 durumu)

| # | Bulgu | Güven |
|---|---|---|
| 1 | **7518 sayılı Kanun** (RG 2.7.2024, 32590): kripto varlık hizmet sağlayıcıları (KVHS) SPK düzenleme ve denetiminde; faaliyet izni + MASAK kimlik tespiti zorunlu | Yüksek, çapraz |
| 2 | İkincil mevzuat: **III-35/B.1 ve III-35/B.2 tebliğleri** (RG 13.3.2025); platformlara 150M TL sermaye şartı raporlanıyor | Yüksek, çapraz |
| 3 | Lisanslama geçiş rejiminde: "Faaliyette Bulunanlar Listesi" ~76-80 şirket; **liste ≠ yetkilendirme** (SPK'nın kendi uyarısı); yetki belgesi takvimi 30.6.2026 idi, SPK Mart 2026'da süre uzattı; nihai lisanslı liste teyit edilemedi | Orta `[DOĞRULANMASI GEREKİYOR]` |
| 4 | **Binance TR faal** ve listede; Şubat 2025 KYC sıkılaştırması; Temmuz 2025'ten beri çekimlerde 72 saat bekleme | Yüksek |
| 5 | **Global Binance** Türkiye'den erişilebilir, bireysel kullanım suç değil; Türkçe destek/pazarlama kaldırıldı (99/A uyumu); **TRY pariteleri Kasım 2025'te Binance TR'ye taşındı** | Orta, çapraz |
| 6 | **SPK lisanslı TR platformlarında kaldıraç/türev/açığa satış YASAK** → Türkiye'de yasal kripto futures ürünü YOK; futures ancak yurt dışı platformda | Yüksek, çapraz |
| 7 | Yurt dışı platformda **kendi hesabına** işlem yapan bireye ceza öngören hüküm yok; yaptırımlar TR'yi hedefleyen izinsiz sağlayıcılara (3-5 yıl). Riskler: hukuki korumasızlık + SPK erişim engelleri (HTX, Bitmart vb. engellendi) | Orta, çapraz |
| 8 | **VERGİ:** Temmuz 2026 itibarıyla kriptoya özel vergi **YÜRÜRLÜKTE DEĞİL**. Mart 2026 teklifi (%10 stopaj + işlem vergisi) tepkiler üzerine **geri çekildi**; yeniden gelmesi bekleniyor, tarih belirsiz. İşlem vergisi oranında kaynak çelişkisi (on binde 3 vs binde 3) `[DOĞRULANMASI GEREKİYOR]`. Şimdilik GVK genel hükümleri (yorumu tartışmalı) | Yüksek (geri çekilme), çapraz |
| 9 | **Alpaca:** paper trading ücretsiz ve küresel (sadece e-posta, KYC yok). Canlı hesapta Alpaca kendi sayfasında Türkiye'yi destekliyor görünüyor — tek yayıncı kaynaklı `[DOĞRULANMASI GEREKİYOR]` | Paper: yüksek / Canlı: orta |
| 10 | **Sinyal satışı / başkasının parasını yönetmek** SPK lisanssız yapılırsa suç (izinsiz sermaye piyasası faaliyeti / izinsiz KVHS; 2-5 / 3-5 yıl aralıkları raporlanıyor). **Kendi hesabına algo-trading serbest** | Orta, çapraz |

### 7.2 Veri ekosistemi (Kongre hattı)

| Kaynak | Durum | Not |
|---|---|---|
| **STOCK Act süresi** | 30 gün (öğrenmeden) / maks 45 gün (işlemden); ceza $200 ve sık affediliyor | Yüksek, çapraz |
| **Pratik gecikme** | Medyan **26 gün**, ortalama **52.5 gün** (~29.776 işlem, Signal Congress çalışması) | Orta `[tek çalışma]` |
| **House Clerk** | `YYYYFD.zip` + XML indeks + PTR PDF'leri; günlük yenileme; 2008'den beri — **en makine-dostu ücretsiz resmî kaynak** | Yüksek |
| **Senate eFD** | Resmî API yok; CSRF + Akamai bot koruması; taranmış-PDF boşlukları var | Yüksek |
| **QuiverQuant** | Tek pratik ucuz resmî API (~$30/ay'dan; insider $75/ay) — rakamlar 3. taraf `[DOĞRULANMASI GEREKİYOR]` | Orta |
| **Unusual Whales** | ToS scraping'i ve yeniden dağıtımı AÇIKÇA yasaklıyor; congressional API erişimi çelişkili raporlandı | Orta |
| **capitoltrades.com** | Public API yok (2iQ ürünü); scraping ToS riski (topluluk scraper README'si bizzat uyarıyor) | Yüksek |
| **NANC/KRUZ** | Kuruluş 7.2.2023; ER %0.75/%0.83. NANC 2024 +%26.82, 2025 +%18.54; kuruluştan ~%67 vs S&P ~%55 (tarihe bağlı, her dönemde değil — son 1 yılda SPY önde). KRUZ hem NANC hem S&P'nin belirgin altında; bir kaynaktaki -%2.22/yıl verisi anomali `[DOĞRULANMASI GEREKİYOR]` | Orta, çelişkiler raporlu |

**Plan çıkarımları:** (1) Hat A veri omurgası: House Clerk ZIP+XML + eFD; kolaylık katmanı QuiverQuant API; Unusual Whales/capitoltrades scraping'i YOK (ToS). (2) Hat A tamamen Alpaca paper üzerinde TR'den yasal ve ücretsiz yürür. (3) Hat B yurt dışı platform gerektirir — bireysel kullanım suç değil ama hukuki koruma yok; vergi düzenlemesi her an gelebilir, F4 kapısında yeniden kontrol şart. (4) Sinyal satışı fikri kesin kırmızı çizgi (lisans suçu).
