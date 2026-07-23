# Pine Script İnceleme — "Trader Club 5in1" (v5)

Kapsam: HTF EMA200 + Linreg kanalı + MavilimW + PMax + Nadaraya-Watson Envelope tek overlay'de. İnceleme; bug, repaint riski, performans ve bot projesine taşınabilirlik açısından yapıldı.

## 1. Genel tespit

"5in1" **görsel** birleştirme; sinyal birleştirme (confluence) yok. 6 `alertcondition`'ın tamamı PMax'tan geliyor — EMA200, Linreg, Mavilim ve NW hiçbir sinyale katılmıyor. Bot'a taşınacaksa asıl eksik parça bu: göstergeler var, **karar mantığı yok**.

Kaynak/atıf: PMax ve MavilimW, Kıvanç Özbilgiç'in halka açık scriptleri; Nadaraya-Watson Envelope LuxAlgo yayını (LuxAlgo scriptleri genelde CC BY-NC-SA lisanslıdır `[DOĞRULANMASI GEREKİYOR — ilgili yayının lisans satırına bak]`); Linreg kanalı TradingView'in resmî Linear Regression Channel koduyla neredeyse aynı. Kişisel kullanım serbest; **yeniden yayınlarsan atıf ve lisans şartlarına dikkat**.

## 2. Bug'lar (önem sırasıyla)

### B1 — Linreg toggle'ı kapatınca kanal gizlenmiyor
Çizgiler `var line` ile bir kez yaratılıyor; `showLinreg` sadece İLK yaratmayı engelliyor. Çizgi bir kez oluştuktan sonra `else` dalındaki `line.set_xy1/xy2` her bar **koşulsuz** çalışıyor → checkbox'ı kapatsan da kanal ekranda kalır ve güncellenmeye devam eder.
**Fix:** set çağrılarını da `showLinreg` koşuluna bağla; kapatıldığında `line.delete`.

### B2 — `mav` düz `input()` string
`input(title="Moving Average Type", defval="EMA")` serbest metin. Kullanıcı "ema" (küçük harf) ya da "Ema" yazarsa `getMA()` hiçbir dala girmez, `ma = 0.0` döner → PMax tüm hesabı 0 üzerinden yapar, **sessizce saçmalar**.
**Fix:** `input.string(defval="EMA", options=["SMA","EMA","WMA","TMA","VAR","WWMA","ZLEMA","TSF"])`.

### B3 — Linreg alt bant rengi yanlış değişkenden
`lower := line.new(..., color=color.new(colorUpper, 0))` — alt çizgi üst bandın rengiyle çiziliyor. `colorLower` olmalıydı. (Kozmetik ama input'taki "Linreg Renk" ayrımını işlevsiz kılıyor.)

### B4 — `linefill.new` her bar çağrılıyor
Global scope'ta her bar iki yeni linefill objesi yaratılıyor. Aynı çizgi çiftine tekrar tekrar fill bağlamak obje bütçesi israfı.
**Fix:** `var linefill` ile bir kez yarat.

### B5 — PMax VAR/CMO penceresi sabit 9
`vUD = math.sum(vud1, 9)` — CMO penceresi `length` input'una değil, hardcoded 9'a bağlı. `length=20` seçsen de VAR 9'luk CMO ile hesaplanır. (Not: bu sabit Kıvanç'ın orijinal kodunda da var; "orijinale sadakat" ile "parametre tutarlılığı" çelişiyor — bilinçli tercih ise yorum satırıyla belgelenmeli.)

### B6 — Ölü kod ve bütçe işgali
- Baştaki `ma(source, length, type)` fonksiyonu hiç çağrılmıyor.
- Mavilim'de `M12..M52, MAVW2` hesaplanıyor, hiçbir yerde kullanılmıyor; `mavilimold` input'u işlevsiz (eski versiyon kalıntısı).
- NW repaint modunda `ln` array'ine ilk barda 500 boş line push'lanıyor ve **hiç kullanılmıyor** — `max_lines_count=500` iken NW'nin `islast`'ta çizdiği ~500 çizgiyle aynı bütçeyi paylaşıyor; en eski çizgilerin sessizce silinmesine yol açabilir.

## 3. Repaint riskleri (bot/backtest açısından kritik)

### R1 — Nadaraya-Watson `repaint=true` (default)
`barstate.islast`'ta son 500 barın zarfı **her güncellemede yeniden** hesaplanıyor; ▲▼ işaretleri geriye dönük çiziliyor. Bu sinyaller canlıda o anda oluşmaz — geçmişe bakınca mükemmel görünür, canlıda kayar/yer değiştirir. Dashboard'daki "Repainting Mode Enabled" uyarısı tam da bu.
**Kural:** repaint modundaki NW sinyali backtest'e ve otomatik karara **giremez**; sadece görsel teyit katmanıdır. Non-repaint (endpoint) modu kullanılabilir ama karakteri tamamen farklıdır.

### R2 — HTF EMA200 çağrısı doğru idiom, ama `gaps_on`
`request.security(..., out200[1], barmerge.gaps_on, barmerge.lookahead_on)` — `[1] + lookahead_on` kombinasyonu klasik **non-repaint** idiom'dur, bu kısım doğru. Ancak `gaps_on` yüzünden seri sadece HTF bar kapanışında değer alır, aradaki barlarda `na` → çizgi kesik kesik görünür. Sürekli çizgi için `barmerge.gaps_off`.

### R3 — Linreg kanalı tanımı gereği repaint
`calcSlope` sadece `barstate.islast`'ta hesaplanıyor; kanal her yeni barda geçmişe yeniden oturtulur. Görsel araç olarak normal, sinyal kaynağı olarak yanıltıcı.

### R4 — NW non-repaint dalında kirli ama patlamayan hesap
`repaint=true` iken `den` hiç doldurulmaz (0 kalır) → `out /= den` 0'a bölme → Pine'da `na` döner, hata fırlatmaz; `mae` de na olur. Çalışır ama gereksiz hesap + okunabilirlik sorunu. **Fix:** `out`/`mae` hesabını `not repaint` koşuluna al.

## 4. Performans

- NW repaint modu: `islast`'ta 500×500 iç içe döngü ≈ 250k `gauss()` çağrısı, her fiyat güncellemesinde. Ağır; düşük TF'de chart'ı yorar.
- `calcSlope` içinde `max_bars_back(source, 5000)` — bellek maliyeti yüksek; `lengthInput` maks 5000'e izin veriliyor ama pratik üst sınır çok daha düşük tutulmalı.

## 5. Bot projesine taşınabilirlik (iş planı bağlantısı)

| Gösterge | Python portu | Not |
|---|---|---|
| EMA200 (HTF) | trivial (`pandas`/`pandas-ta`) | HTF resample + shift(1) ile non-repaint birebir kurulur |
| MavilimW | trivial | İç içe 6 WMA zinciri (3,5,8,13,21,34 Fibonacci uzunlukları) |
| PMax | kolay | Supertrend varyantı: MA ± ATR×mult trailing stop; supertrend kodundan uyarlanır. B5'teki sabit-9 kararını portta netleştir |
| Linreg kanalı | kolay | `numpy.polyfit` + std bandı; ama rolling pencereyle bar-kapanışı versiyonu kullanılmalı (R3) |
| NW Envelope | dikkat | SADECE endpoint (non-repaint) versiyonu port edilir; repaint versiyonu backtest'te yasak (R1) |

**Altın kural:** Backtest'e giren her sinyal, sinyal barının kapanışında kesinleşmiş olmalı. Bu scriptteki 5 göstergeden bu şartı hazır sağlayanlar: EMA200 (R2 idiom'u sayesinde), MavilimW, PMax. Linreg ve NW ancak yeniden formüle edilerek girer.

## 6. Önerilen confluence iskeleti (bot karar katmanı için taslak)

```
trend_filter  = close > ema200_htf            # rejim: sadece long tarafı (ters için simetrik)
signal        = pmax_crossover(MAvg, PMax)     # tetik
slope_confirm = mavilim_rising                 # eğim teyidi
stretch_veto  = close > nw_upper_endpoint      # aşırı uzamada girme (veto)
enter_long    = trend_filter and signal and slope_confirm and not stretch_veto
```
Ağırlıklar/parametreler backtest'te optimize edilir — walk-forward ile, tek dönem optimizasyonu overfit üretir (detay: iş planı, docs/03).
