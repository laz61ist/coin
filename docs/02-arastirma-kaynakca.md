# Araştırma Kaynakçası — Trading AI Karar Sistemi

## 0. Metodoloji ve dürüstlük notu (önce bunu oku)

Araştırma paralel subagent'larla yürütüldü: 3 GitHub repo tarayıcı, 3 akademik makale tarayıcı, 1 Türkiye regülasyon ajanı (+2 bağımsız adversarial doğrulayıcı), 1 veri ekosistemi ajanı, 1 kapsam kritiği.

**Ağ kısıtı (kritik):** Bu çalışma ortamının ağ politikası github.com dışındaki dış sitelere erişimi engelliyor (arxiv.org, sciencedirect.com, springer.com, mdpi.com, ssrn.com, doi.org dahil — proxy CONNECT-403, bizzat doğrulandı). Sonuçları:

- GitHub repo verileri (yıldız, lisans, son commit, README özellikleri) **sayfadan doğrulandı** — güvenilir.
- Akademik makaleler **yalnızca arama snippet'i/abstract düzeyinde** okunabildi. Anayasa §5.2 dürüst sayım: **tam okunan makale sayısı 0/23**. Tüm makaleler `[yalnızca özet okundu]` statüsündedir ve aşağıdaki bulgular bu düzeyin güvenilirliğiyle sınırlıdır.
- DOI'ler script ile doğrulanamadı (doi.org engelli) → tüm DOI/künyeler `[DOĞRULANMASI GEREKİYOR]`.
- Derin okuma passı için: environment ayarlarından network policy genişletilmeli ya da bu tarama claude.ai sohbetinde tekrarlanmalı.

## 1. GitHub — Kongre copy-trading repoları

| Repo | ★ | Dil | Lisans | Son aktivite | Değerlendirme |
|---|---|---|---|---|---|
| [kadoa-org/congress-trading-monitor](https://github.com/kadoa-org/congress-trading-monitor) | 112 | JS | MIT | 2026-07-23 (günlük otomatik yenileme) | En güncel veri kaynağı adayı; dashboard+dataset, emir katmanı yok |
| [neelsomani/senator-filings](https://github.com/neelsomani/senator-filings) | 414 | Python | MIT | 2022-01 | Alanın en yıldızlısı; eFD parser tasarımı için referans, bakımsız |
| [timothycarambat/senate-stock-watcher-data](https://github.com/timothycarambat/senate-stock-watcher-data) | 96 | — | — | 2021-03 | Hazır JSON tarihsel veri — backtest için |
| [johnisanerd/Apify-Congressional-Trading-Data-Scraper](https://github.com/johnisanerd/Apify-Congressional-Trading-Data-Scraper) | 9 | Python | MIT | 2026-07-22 | Aktif, MCP entegrasyonlu; Apify'a (ücretli servis) bağımlı |
| [heils/congress-watcher](https://github.com/heils/congress-watcher) | 0 | Python | — | 2026-06-23 | "Yeni işlem tespit → tetik" kalıbı; kişisel proje, üretime alma |
| [MajesticBison/pelosi-trade-tracker](https://github.com/MajesticBison/pelosi-trade-tracker) | 1 | Python | MIT | 2025-09 | House Clerk PDF parse hattı örneği |
| [TommasoAmici/capitoltrades](https://github.com/TommasoAmici/capitoltrades) | 2 | Rust | MIT | 2024-04 | capitoltrades.com gayriresmî API client'ı; kırılganlık riski |
| [xSurus/rusty_trader](https://github.com/xSurus/rusty_trader) | 2 | Rust | — | 2022-12 | "Kongre → kopyala" birebir kavram kanıtı; ölü proje, mimari referans |
| [jeremiak/us-senate-financial-disclosure-scraper](https://github.com/jeremiak/us-senate-financial-disclosure-scraper) | 23 | JS | — | 2022-07 | HTML+taranmış PDF işleme referansı |
| [P-H-B-D/CapitolTradesScraper](https://github.com/P-H-B-D/CapitolTradesScraper) | 3 | Python | — | 2022-01 | Yazarı bizzat ToS ihlal riskine dikkat çekiyor — hukuki nota bak |

**Sonuç:** Hazır "kur-çalıştır" üretim kalitesinde Kongre-kopyalama botu YOK. Aktif olanlar veri katmanı; emir/risk katmanını kendimiz yazacağız. Bu, iş planındaki Faz-5 tasarımını belirledi.

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

**Sonuç:** Hat-B çekirdeği için birincil aday **freqtrade** (futures + backtest + dry-run + FreqAI bir arada), ileri seviye alternatif **nautilus_trader**. Gerekçe iş planında.

## 3. GitHub — AI/LLM/RL trading repoları

| Repo | ★ | Lisans | Son aktivite | Değerlendirme |
|---|---|---|---|---|
| [TauricResearch/TradingAgents](https://github.com/TauricResearch/TradingAgents) | 94.3k | Apache-2.0 | 2026-07-18 | Çok-ajanlı LLM (analist/debate/trader/risk); SİMÜLE emir — canlı trade yok, araştırma amaçlı |
| [virattt/ai-hedge-fund](https://github.com/virattt/ai-hedge-fund) | 62.4k | MIT | 2026-07-23 | Persona-bazlı LLM analiz; "gerçek trade yapmaz" — eğitim amaçlı |
| [microsoft/qlib](https://github.com/microsoft/qlib) | 46.6k | MIT | 2026-07-23 | Kurumsal kalite quant altyapı + RD-Agent; kripto odaklı değil |
| [AI4Finance-Foundation/FinGPT](https://github.com/AI4Finance-Foundation/FinGPT) | 20.9k | MIT | 2026-07-23 | Finansal LLM altyapısı; sentiment/haber katmanı, karar motoru değil |
| [AI4Finance-Foundation/FinRL](https://github.com/AI4Finance-Foundation/FinRL) | 15.8k | MIT | 2026-07-13 | RL pipeline; Binance/CCXT veri + Alpaca paper deploy örnekleri; kendini "araştırma" konumluyor |
| [AI4Finance-Foundation/FinRobot](https://github.com/AI4Finance-Foundation/FinRobot) | 7.6k | Apache-2.0 | 2026-07-07 | LLM yatırım araştırma otomasyonu; "sayılar kodla, anlatı LLM'le" prensibi dikkate değer |
| [AI4Finance-Foundation/FinRL-Meta](https://github.com/AI4Finance-Foundation/FinRL-Meta) | 1.9k | MIT | 2026-07-13 | RL benchmark ortamları (Binance/CCXT); spot odaklı |
| [pipiku915/FinMem-LLM-StockTrading](https://github.com/pipiku915/FinMem-LLM-StockTrading) | 928 | MIT | 2024-08 (bakımsız) | Katmanlı bellekli LLM ajan referans kodu; sadece backtest |

**Kritik gözlem:** En yıldızlı LLM-trading repoları bile (TradingAgents 94.3k, ai-hedge-fund 62.4k) **canlı emir vermiyor** ve kendilerini araştırma/eğitim olarak konumluyor. Canlı futures botu dünyasında üretim olgunluğu LLM'de değil, klasik framework'lerde (freqtrade/nautilus). Bu, mimarideki "LLM karar destek, emir yetkisi yok" kararının ana gerekçesi.

## 4. Akademik — RL/ML ile kripto/futures trading `[tümü: yalnızca özet okundu]`

1. **Gort, Liu, Sun, Zhang ve ark. (2022/2023)** — *Deep RL for Cryptocurrency Trading: Practical Approach to Address Backtest Overfitting.* arXiv:2209.05559. Overfitting tespitini hipotez testi yapıyor; en az overfit PPO ajanı 2022 çöküş döneminde endeksi geçiyor (~%0.3 maliyet dahil). Zayıflık: ~2 aylık test penceresi. `[DOĞRULANMASI GEREKİYOR]`
2. **Borrageiro, Firoozye, Barucca (2022)** — *The Recurrent RL Crypto Agent.* IEEE Access 10:38590-38599, doi:10.1109/ACCESS.2022.3166599. **Perpetual'a en doğrudan bulgu:** BitMEX XBTUSD'de ~5 yılda maliyet sonrası ~%350 getiri; **kârın %71'i funding'den** — yön tahmini değil. `[DOĞRULANMASI GEREKİYOR]`
3. **Qin, Xia, Cai ve ark. (2025)** — *FineFT: Efficient and Risk-Aware Ensemble RL for Futures Trading.* arXiv:2512.23773. 125x kaldıraç + funding fee'li ortam; kaldıracın ödül varyansını şişirmesi ve "yetkinlik sınırı" problemi; ensemble + VAE + muhafazakar politika. `[DOĞRULANMASI GEREKİYOR]`
4. **Chun & Lee (2025)** — *Cryptocurrency Futures Portfolio Trading System Using RL.* Applied Sciences 15(17):9400, doi:10.3390/app15179400. A2C, Binance Futures 18 kripto; öne çıkan rakamlar EĞİTİM dönemine ait — OOS teyitsiz. `[DOĞRULANMASI GEREKİYOR]`
5. **Wang & Klabjan (2023)** — *An Ensemble Method of DRL for Automated Cryptocurrency Trading.* arXiv:2309.00626. OOS iyileşmeyi açık hedef yapıyor; somut OOS rakamları snippet'ten teyitsiz.
6. **Sadighian (2019)** — *DRL in Cryptocurrency Market Making.* arXiv:1911.08647. MM problemi; yön stratejisi değil.
7. **Jiang, Xu, Liang (2017)** — *A DRL Framework for the Financial Portfolio Management Problem.* arXiv:1706.10059. Alanın klasiği (EIIE); zero-slippage varsayımı eleştirisi yaygın.
8. **Pippas, Ludvig, Turkay (2024/2025)** — *The Evolution of RL in Quantitative Finance: A Survey.* arXiv:2408.10932 (ACM Computing Surveys kabul). 167 yayın; overfitting/maliyet ihmali alanın yaygın kusuru.

**Sentez:** RL kripto-futures'ta pozitif sonuçların tamamı yazarların kendi backtest'i (`selfReported`); bağımsız replikasyon yok denecek kadar az. En sağlam iki ders: (a) backtest overfitting ana düşman, (b) perpetual'da funding mekanizması yön tahmininden daha güvenilir kâr kaynağı olabilir.

## 5. Akademik — LLM trading ajanları `[tümü: yalnızca özet okundu]`

1. **Xiao, Sun, Luo, Wang (2024)** — *TradingAgents: Multi-Agents LLM Financial Trading Framework.* arXiv:2412.20138. Rol-ayrımlı çoklu ajan + bull/bear debate. Raporlanan Sharpe 5.6-8.2 — ama 3 aylık pencere, 3 hisse; güvenilirlik düşük.
2. **Yu, Li, Chen ve ark. (2023)** — *FinMem: LLM Trading Agent with Layered Memory.* arXiv:2311.13743 (AAAI-SS 2024). Katmanlı bellek; TSLA'da +%61.78 vs B&H -%18.63 — tek hisse, seçilmiş dönem.
3. **Yang, Liu, Wang (2023)** — *FinGPT: Open-Source Financial LLMs.* arXiv:2306.06031. Altyapı makalesi; LoRA adaptasyon ~300 USD iddiası (kendi rakamı).
4. **Zhang, Zhao, Xia ve ark. (2024)** — *FinAgent: Multimodal Foundation Agent for Financial Trading.* KDD 2024, doi:10.1145/3637528.3671801. Multimodal + reflection + tool use; %36+ iyileşme iddiası (kendi rakamı). `[DOĞRULANMASI GEREKİYOR]`
5. **Lopez-Lira & Tang (2023)** — *Can ChatGPT Forecast Stock Price Movements?* arXiv:2304.07619 / SSRN 4412788. Referans tasarım: örneklem model bilgi kesiminden SONRA başlıyor (leakage kontrolü). GPT-4 haber skorları kısa vadeli öngörü gücü taşıyor.
6. **Glasserman & Lin (2023)** — *Assessing Look-Ahead Bias in Stock Return Predictions by GPT.* arXiv:2309.17322. **LLM backtest'lerinin çekirdek eleştirisi:** eğitim dönemi ile backtest çakışırsa look-ahead bias + distraction effect; anonimleştirme deneyi farkı gösteriyor.
7. **Li, Kim, Cucuringu, Ma (2025)** — *Can LLM-based Financial Investing Strategies Outperform the Market in Long Run?* (FINSABER) arXiv:2505.07078. **En önemli soğuk duş:** ~20 yıl, 100+ sembolde önceden raporlanan LLM avantajları büyük ölçüde kayboluyor; dar pencere + survivorship bias ana suçlu. `[DOĞRULANMASI GEREKİYOR]`
8. **Ding, Li, Wang, Chen (2024/2026)** — *LLM Agent in Financial Trading: A Survey.* arXiv:2408.06361. Alanın taksonomisi; kısa backtest/benchmark tutarsızlığı ortak kusur.

**Sentez:** LLM-ajan makalelerinin parlak rakamları (Sharpe 8 vb.) kısa pencere + az sembol + muhtemel look-ahead bias üçlüsüyle şişkin. Uzun vadeli, geniş evrenli testte (FINSABER) avantaj eriyor. **Tasarım dersi:** LLM'i fiyat tahmincisi değil; haber/sentiment özetleyici, rejim yorumlayıcı ve risk anlatıcısı olarak kullan — emir kararını kurallı/istatistiksel katman versin.

## 6. Akademik — Kongre üyesi işlemleri ve kopyalama `[tümü: yalnızca özet okundu]`

1. **Ziobrowski, Cheng, Boyd, Ziobrowski (2004)** — *Abnormal Returns from the Common Stock Investments of the U.S. Senate.* JFQA 39(4). 1993-1998: senatör ALIMLARI piyasayı ~85bp/ay yeniyor. Literatürün "Kongre yeniyor" tezinin kaynağı.
2. **Ziobrowski ve ark. (2011)** — *...Members of the U.S. House.* Business and Politics 13(1). 1985-2001: Meclis alımları ~55bp/ay (+~%6/yıl).
3. **Eggers & Hainmueller (2013)** — *Capitol Losses.* Journal of Politics 75(2), doi:10.1017/s0022381613000194. **Karşı-kanıt:** 2004-2008'de Kongre portföyleri piyasanın yılda %2-3 ALTINDA; bilgiye dayalı işlem kanıtı yok.
4. **Belmont, Sacerdote, Sehgal, Van Hoek (2022)** — *Do senators and house members beat the stock market? Evidence from the STOCK Act.* J. Public Economics 207, doi:10.1016/j.jpubeco.2022.104602. **STOCK Act sonrası en kapsamlı çalışma: üstün performans kanıtı YOK**; alınan hisseler 6 ayda ~26bp düşük performans.
5. **Karadas (2019)** — *Trading on Private Information: Evidence from Members of Congress.* Financial Review 54(1), doi:10.1111/fire.12180. Outperformance homojen değil: "güçlü" üye alt-gruplarında büyük anormal getiri; **STOCK Act (2012) sonrası kayboluyor**.
6. **Baulkaran & Jain (2025)** — *U.S Congress members' trading activities: A case of NANC and KRUZ.* Economics Letters 250. Kopyalama ETF'leri: NANC ~%27, KRUZ ~%13 yıllık getiri; **risk-düzeltilmiş bazda hiçbiri piyasayı anlamlı yenmiyor**; NANC farkı tech eğiliminden. `[DOĞRULANMASI GEREKİYOR]`
7. **Wei & Zhou (2025)** — *"Captain Gains" on Capitol Hill.* NBER WP 34524. En güncel karşı-yönlü bulgu: liderliğe yükselen üyeler yükseldikten sonra peer'larını belirgin geçiyor — bilgi/etki kanalı hâlâ canlı olabilir, ama bu genel kopyalama stratejisini değil dar bir alt-grubu destekler. `[DOĞRULANMASI GEREKİYOR]`

**Sentez (iş planının temel taşı):** Literatür NET DEĞİL ve zaman içinde kötüleşiyor: 1990'lar verisinde büyük avantaj (Ziobrowski), 2004+ döneminde yok (Eggers-Hainmueller), STOCK Act sonrası yok (Belmont ve ark.; Karadas'ta avantaj 2012'de bitiyor), kopyalama ETF'lerinde risk-ayarlı avantaj yok (Baulkaran-Jain). Üstüne 45 güne varan açıklama gecikmesi kopyalayanı daha da geriye atar. **Kongre kopyalama hattı "para makinesi" değil; veri mühendisliği + otomasyon portfolyo projesi olarak değerlidir.** Alfa arayan tek akademik destekli daraltma: güç pozisyonundaki üyelerin işlemlerine filtreleme (Karadas, Wei-Zhou) — o da spekülatif.

## 7. Türkiye regülasyonu ve veri ekosistemi

> Bu bölümün workflow doğrulaması (2 bağımsız adversarial ajan) henüz tamamlanmadı — sonuçlar geldiğinde bu dosya güncellenecek. `[BEKLEMEDE]`
