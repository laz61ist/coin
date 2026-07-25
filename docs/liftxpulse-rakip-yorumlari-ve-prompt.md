# Rakip Uygulama Kullanıcı Yorumları + LiftXPulse Geliştirme Prompt'u

Tarih: 2026-07-25
Kapsam: `liftxpulse-uyumluluk-swot.md` §5 tablosundaki telefon tabanlı uygulamalar (Lift Tester, LiftCheck, EleMeter, Elevator Speed).

## Dürüstlük notu — "eksiksiz" kısıtı

Bu ortamın ağ politikası Play Store / App Store / AppBrain / APKPure sayfalarına doğrudan erişimi engelliyor (403). Aşağıdaki yorumlar, arama sonucu özetlerinde yüzeye çıkan **erişilebilir tüm yorum içerikleridir** — mağazalardaki tam yorum dökümü DEĞİLDİR. Tam döküm için §4'teki URL'ler tarayıcıdan açılıp paylaşılmalı; paylaşılırsa bu dosya güncellenir.

## 1. Uygulama bazında yorum dökümü

### 1.1 Kleemann Lift Tester (iOS id490950875 / Android com.kleemann.lifttester)

Puan durumu (çelişkili ve az oylu — düşük güven):
- Google Play: **henüz puan yok** (AppBrain), ~5.000 indirme, son 30 günde 260 indirme
- iOS App Store: resmi puan snippet'lerde görünmedi `[bulunamadı]`; üçüncü taraf bir platformda 1 oy / 1,5 puan; UpdateStar'da 5/5
- AppGrooves: 13 yorum listeleniyor (tam metinleri sayfa engeli nedeniyle alınamadı)

Olumlu yorumlar (erişilebilenler):
- "Asansör meraklıları için en iyi araç" — hız, ivme, mesafe ve **jerk** ölçümü + grafik gösterimi + testleri kaydedip sonra bakabilme övülmüş.
- "Gördüğüm en iyi tasarım" (arayüz övgüsü).
- Farklı traksiyon teknolojilerini karşılaştırmak ve **aynı asansörün sürüş kalitesinin zaman içindeki gidişatını izlemek** için iyi bulunmuş.

Olumsuz yorumlar / istekler (erişilebilenler):
1. **Çökme:** Samsung S24 Ultra'da "kayıtlı testler" sayfası her açılışta uygulamayı çökertiyor; test koşmak çalışıyor; yeniden kurulum çözmemiş.
2. **Eksik metrik:** "Ölçümler doğru ama ortalama ve maksimum hız, seyir süresi, tahmini kat (estimated run) gibi ek veriler gerekli."
3. **Birim seçeneği:** hız için **ft/min** opsiyonu istenmiş; bir başka yorumda ft/s dışında birim olmaması eleştirilmiş ("hesabı elle yapmak zor değil ama olmalıydı").
4. Üretici feragati (yorum değil ama konum belirleyici): "özel ölçüm cihazlarının yerine geçmez, profesyonel ölçüm için uzmana danışın."

### 1.2 EleMeter (Android jp.figix.elemeter)

Puan durumu: **~3,6–3,8 yıldız** (AppBrain, iki farklı görünümde farklı değer), 10.000+ indirme.

Olumlu: kolay ve hassas kalibrasyon, kullanışlı özellikler, kolay arayüz, CSV dışa aktarım, hız/yükseklik/düşey G gösterimi.

Olumsuz:
1. **Sarsıntıda çökme:** asansör sarsıldığında veya hızlı ivmelendiğinde uygulama çöküyor.
2. **Başlamama:** bazen cihaz yerleştirildiğinde ölçüm hiç başlamıyor.
3. **Hız aralığı:** çok yavaş veya çok hızlı asansörlerde iyi çalışmıyor.

### 1.3 Elevator Speed (Android com.phonegap.elevatorspeed — yayından kalkmış)

Puan durumu: **3,2 yıldız / 190 oy**, 10.000–22.000 indirme (AppBrain); v1.0, son güncelleme 02.08.2011.

Yorum metinleri arama özetlerinde **bulunamadı**. Mağaza açıklamasından bilinen tek kısıt aynı zamanda muhtemel düşük puan nedeni: **kalibrasyondan sonra cihaz kımıldatılırsa hız tamamen yanlış çıkıyor** (elle sabit tutma zorunluluğu).

### 1.4 DEKRA LIFT Check (iOS id1572280427 / Android com.dekra.digital.liftcheck)

Kamuya açık **kullanıcı yorumu bulunamadı**; Play puanı snippet'lerde görünmüyor (kurumsal/B2B kullanım, düşük tüketici yorumu doğal). Yorum yerine mimari bilgiler (üretici beyanı):
- TK Elevator ile ORTAK geliştirilmiş; Rottweil test kulesinde test + 4 kıtada ~500 ölçümlük pilot.
- Rapor + **FFT titreşim analizi** dashboard'da; **kullanıcı yönetimi** ile ekip erişimi.
- Analiz sunucuda, rapor **e-posta ile** dakikalar içinde.

Yorumsuz zayıflık analizi (mimariden çıkarım, yorum değil): sunucu bağımlılığı (offline çalışmaz), rapor teslimi e-posta dolaylı, tüketici görünürlüğü yok.

## 2. Yorumlardan çıkan eksik haritası → LiftXPulse gereksinimi

| # | Kaynak yorum/kısıt | LiftXPulse gereksinimi |
|---|---|---|
| G1 | Lift Tester: kayıtlı testler sayfası çöküyor | Geçmiş/kayıt ekranı: sayfalama + tembel yükleme + bozuk kayıt toleransı + crash raporlama |
| G2 | Lift Tester: ort./maks. hız, seyir süresi, kat tahmini yok | Sefer raporu: V_ort, V_maks (V95), seyir süresi, mesafe, kat tahmini, jerk, Max PP + A95 (ISO 8100-34 dili) |
| G3 | Lift Tester: birim seçeneği yok | Birim sistemi: m/s ↔ ft/s ↔ ft/min, m ↔ ft; ayarlardan kalıcı seçim |
| G4 | EleMeter: sarsıntıda çökme | Sensör hattı UI'dan bağımsız; tampon + taşma/clipping toleransı; sert darbede veri işaretlenir, uygulama ÇÖKMEZ |
| G5 | EleMeter: ölçüm bazen başlamıyor | Otomatik sefer algılama (auto start/stop) + başlamadıysa kullanıcıya görünür durum/gerekçe |
| G6 | EleMeter: çok yavaş/hızlı asansörde kötü | 0,15 m/s (platform) – 2,5+ m/s aralığı; yavaş hızda barometre füzyonu (ivme integrasyonu yetmez) |
| G7 | Elevator Speed: kalibrasyon sonrası kımıldama = yanlış sonuç | Kalibrasyonda hareket algılama + otomatik yeniden kalibrasyon + ölçüm sırasında hareket bozulması tespiti ve etiketleme |
| G8 | DEKRA: sunucu bağımlı, rapor e-postayla | On-device analiz + anında yerel PDF/CSV rapor; internet yokken tam işlev (patent design-around ile de uyumlu, bkz. SWOT raporu §6.2) |
| G9 | DEKRA'da var, telefon app'lerinde yok | FFT spektrum görünümü + ekip/rapor paylaşımı (faz-2) |
| G10 | Kleemann feragati / hukuki konum | Rapor ve ekranlarda "ISO 8100-34'e DAYALI gösterge ölçümü" ibaresi; kalibrasyonlu cihaz yerine geçmez uyarısı |

## 3. Cursor/IDE Prompt'u (kopyala-yapıştır)

```markdown
# GÖREV: Rakip uygulama yorumlarından türetilen 10 gereksinimi (G1-G10) LiftXPulse'a uygula

## PROJE BAĞLAMI
- Konum: [LiftXPulse repo kök yolu — DOLDUR]
- Stack: [Flutter/Kotlin/Swift — mevcut stack neyse — DOLDUR]
- Kurallar dosyası: [.cursor/rules/*.mdc varsa — DOLDUR]
- Referans doküman: docs/liftxpulse-rakip-yorumlari-ve-prompt.md (bu dosya) + docs/liftxpulse-uyumluluk-swot.md §4-§6
- Tetikleyici: rakip analizi sonucu ürün sertleştirme turu

## DOSYALAR
- [oku] Mevcut sensör okuma servisi ve sefer kayıt modeli
- [güncelle] Sefer rapor üretici (metrik seti genişleyecek)
- [güncelle] Ayarlar ekranı (birim sistemi)
- [oluştur] Kalibrasyon durum makinesi (hareket algılamalı)
- [oluştur] Geçmiş ekranı sayfalama + bozuk kayıt toleransı katmanı

## ADIMLAR
1. G4 (kararlılık): Sensör örnekleme hattını UI thread'inden ayır; ring-buffer'a yaz;
   ivme sensörü satürasyonunda (clipping) veriyi "doygun" etiketle, işlemeye devam et.
   Uygulama hiçbir sensör olayında çökmemeli — global hata yakalama + crash log.
2. G1 (geçmiş ekranı): Kayıt listesini sayfalı yükle (20'şer); tek bozuk kayıt tüm
   listeyi düşürmesin — parse hatasında o kaydı "onarılamadı" kartıyla göster, atla.
3. G2 (metrik seti): Sefer raporuna ekle: V_ort, V_maks, seyir süresi, toplam mesafe,
   tahmini kat sayısı, jerk (10 Hz filtreli z-ivmesinden 0,5 s kayan LSQ eğimi),
   Max peak-to-peak ve A95 peak-to-peak titreşim. Metrik adları ISO 8100-34
   terminolojisiyle; rapor altbilgisine G10 ibaresini koy.
4. G3 (birimler): Ayarlara birim seçimi ekle (m/s, ft/s, ft/min; m, ft). Seçim kalıcı;
   tüm ekran ve PDF/CSV çıktılarına uygulanır. Dahili hesap her zaman SI, dönüşüm
   yalnız sunum katmanında.
5. G5+G7 (otomatik sefer + kalibrasyon): Kalibrasyon sırasında hareket algılanırsa
   otomatik yeniden başlat ve kullanıcıya tek satır bilgi ver. Sefer başlangıcını
   ivme+barometre imzasından otomatik algıla; 10 sn içinde başlamazsa nedenini
   gösteren durum satırı ("cihaz titreşimli", "sensör izni yok" vb.).
6. G6 (hız aralığı): Hız kestirimini ivme-integrasyon + barometre füzyonuyla yap;
   0,15 m/s ve 2,5 m/s senaryolarını ayrı test et. Yavaş asansörde integrasyon
   sürüklenmesini barometreyle sıfırla.
7. G8 (offline): Analiz ve PDF/CSV üretimi tamamen cihazda; internet yokken uçtan uca
   çalıştığını test et. Buluta gönderim varsa yalnız arşiv amaçlı ve opsiyonel kalsın
   (patent design-around: teşhis SONUCU cihazda üretilir — SWOT raporu §6.2).
8. G9 (faz-2, ayrı commit): Sefer detayına FFT spektrum grafiği ekle (z-ekseni,
   0-80 Hz). Ekip paylaşımı BU TURDA YOK — sadece TODO olarak işaretle.

## KESİN KURALLAR
- Mevcut çalışan koda dokunma; yeni katmanları mevcut isimlendirme ve klasör
  düzeniyle ekle (Consistency First).
- Sensör hattında bloklayan çağrı yasak; tüm işleme arka plan iş parçacığında.
- Dahili birim SI; UI metinleri Türkçe [mevcut dil neyse ona uy], hata mesajları kullanıcı dilinde.
- "ISO uyumlu/sertifikalı" ifadesi HİÇBİR yerde kullanılmayacak; yalnız
  "ISO 8100-34'e dayalı gösterge ölçümü" (G10).
- Test etiketli sahte veriyle çalış; gerçek firma/müşteri verisi commit'e girmez.

## KABUL KRİTERLERİ
- [ ] Sert sarsıntı simülasyonunda (sensör satürasyonu) uygulama çökmüyor, veri etiketleniyor
- [ ] 500+ kayıtlı ve 1 bozuk kayıtlı geçmiş listesi açılıyor, bozuk kayıt izole
- [ ] Rapor G2'deki tüm metrikleri içeriyor; jerk hesabı birim testte doğrulanmış
- [ ] Birim değişimi tüm ekran + PDF/CSV çıktısına yansıyor
- [ ] Kalibrasyon sırasında telefon oynatılınca otomatik yeniden kalibrasyon tetikleniyor
- [ ] 0,15 m/s ve 2,5 m/s sentetik profillerde hız hatası kabul sınırında [sınırı DOLDUR]
- [ ] Uçak modunda uçtan uca ölçüm + rapor üretimi çalışıyor
- [ ] Tüm rapor çıktılarında G10 ibaresi var

## ÖNCE/SONRA RAPORLAMA
Diff çıkar; her gereksinim (G1-G10) için "uygulandı/kısmen/ertelendi" tablosu ver.
```

## 4. Tam yorum dökümü için açılacak URL'ler

1. https://apps.apple.com/us/app/lift-tester/id490950875 (+ /gb ve /in vitrinleri)
2. https://appgrooves.com/ios/490950875/lift-tester/kleemann-hellas-incorporated-industrial-commercial-company-for-mechanical-constructions-sa/ (13 yorum)
3. https://play.google.com/store/apps/details?id=com.kleemann.lifttester&hl=en-US
4. https://play.google.com/store/apps/details?id=jp.figix.elemeter&hl=en
5. https://m.apkpure.com/elemeter/jp.figix.elemeter (yorum sekmesi)
6. https://www.appbrain.com/app/elevator-speed/com.phonegap.elevatorspeed (190 oyun dağılımı)
7. https://play.google.com/store/apps/details?id=com.dekra.digital.liftcheck
8. https://apps.apple.com/us/app/lift-check/id1572280427
9. https://www.appbrain.com/app/lift-check/com.dekra.digital.liftcheck
