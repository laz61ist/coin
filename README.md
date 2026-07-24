# coin — AI Destekli Trading Karar Sistemi

Araştırma ve planlama dokümanları (branch: `claude/trading-ai-decision-system-wturmo`):

| Doküman | İçerik |
|---|---|
| [docs/01-prompt-analizi.md](docs/01-prompt-analizi.md) | Viral "Kongre copy-trading" demosunun transkripsiyon + 10 zayıf nokta + geliştirilmiş üretim-kalitesi prompt |
| [docs/02-arastirma-kaynakca.md](docs/02-arastirma-kaynakca.md) | 25 GitHub repo (sayfadan doğrulanmış) + 23 akademik makale (derin pass: repo-doğrulamalı, çelişki haritalı) + TR regülasyon + veri ekosistemi |
| [docs/03-is-plani.md](docs/03-is-plani.md) | İki hatlı iş planı: Binance Futures AI karar sistemi (ana) + Kongre kopyalama Alpaca paper (yan); F0-F6 fazlar, GO/NO-GO kapısı, risk kaydı, maliyet |
| [docs/04-pine-inceleme.md](docs/04-pine-inceleme.md) | "Trader Club 5in1" Pine Script incelemesi: bug listesi, repaint riskleri, Python port tablosu, confluence iskeleti |

## Üç cümlelik özet

1. **Kongre kopyalama** literatürde para makinesi değil: STOCK Act (2012) sonrası agregat alfa yok, kopyalama ETF'leri (NANC/KRUZ) risk-ayarlı bazda piyasayı yenmiyor — hat, veri mühendisliği portfolyo projesi olarak kurgulandı.
2. **LLM'e emir yetkisi verilmez**: parlak LLM-trading rakamları bağımsız denetimlerde (FINSABER, Profit Mirage) çöküyor; LLM haber/rejim/rapor katmanında, kararı kurallı sinyal + risk motoru verir.
3. **Önce süreç, sonra sermaye**: walk-forward backtest → 8+ hafta testnet → yazılı GO/NO-GO kapısı → ancak ondan sonra mikro-sermaye.

Uyarı: Bu depo araştırma/plan dokümanıdır; yatırım tavsiyesi değildir. Kaldıraçlı kripto türevlerinde anapara tamamen kaybedilebilir.
