# LiftXPulse — Otis Patent Değerlendirmesi, KONE DT6 Araştırması, Uyumluluk + SWOT

Tarih: 2026-07-24
Girdi: `otkssensor.pdf` (US 10,547,917 B2 tam metni, 14 sayfa, USPTO)
Araştırma: 9 paralel ajan, ~40 kaynak tarandı.

---

## 0. Durum ve dürüstlük beyanı

- **LiftXPulse kodu bu repoda yok.** `coin` repo'sunda README dışında tek içerik trading-AI branch'i; hesaptaki repo listesinde `liftxpulse` adlı repo görünmüyor. Bu analiz, LiftXPulse'un **"akıllı telefon sensörleriyle (ivmeölçer/barometre/mikrofon) asansör sürüş kalitesi ölçümü ve tanılama uygulaması"** olduğu varsayımına dayanıyor `[DOĞRULANMASI GEREKİYOR — kod hangi repodaysa bildirin]`.
- **Ağ kısıtı:** Bu oturumun ağ politikası dış sitelere erişimi engelledi (WebFetch/curl → 403). Tek tam okunmuş kaynak, kullanıcının yüklediği **patent PDF'inin kendisi**; diğer tüm bilgiler arama sonucu özetlerinden (snippet) derlendi ve kaynakçada böyle etiketlendi. Anayasa §5.2 gereği tam-okuma sayısı şişirilmedi: **1/15**. §9.3'te manuel indirme için öncelikli URL listesi var.
- Patent analizi hukuki görüş değildir; başvuru/FTO (freedom-to-operate) kararı öncesi patent vekili şart.

## 1. Ekteki PDF: US 10,547,917 B2 analizi (tam okundu — birincil kaynak)

### 1.1 Kimlik

| Alan | Değer |
|---|---|
| Patent no | US 10,547,917 B2 |
| Başlık | Ride Quality Mobile Terminal Device Application |
| Sahip (assignee) | Otis Elevator Company, Farmington CT |
| Buluşçular | George Scott Copeland, Jinho Song |
| Başvuru | 12 Mayıs 2017 (Appl. 15/593,707) |
| Ön yayın | US 2018/0332368 A1 (15 Kasım 2018) |
| Tescil | 28 Ocak 2020 (+25 gün 154(b) uzatması) |
| İstem sayısı | 19 (3 bağımsız: 1=sistem, 8=cihaz, 14=yöntem) |
| EP izi | EP başvuru 18172185.3 (dosyada Extended European Search Report, 27.03.2019 tarihli, dosyalama 14.05.2018) |

### 1.2 Ne anlatıyor

Servis sağlayıcılar arızayı çoğunlukla kullanıcı şikâyetiyle öğreniyor; teşhis için asansörü servis dışına alıp panel arkasındaki donanıma erişmek gerekiyor. Patentin çözümü: teknisyenin **akıllı telefonu** (kamera + mikrofon + hoparlör + tek/çok eksenli ivmeölçer) sürüş kalitesi verisini toplar, **bulut** üzerindeki teşhis algoritması sonucu üretir, telefon sonucu bileşen bazında gösterir.

Tanımlı teşhis operasyonları: **Door Cycle** (kapı çevrimi — "telefonu göğüs hizasında, kapıya dönük tut"), **Floor-to-Floor** (kat arası seyir), **Machine Diagnostic** (makine dairesi ses karşılaştırma); yürüyen merdiven için Step Run / Handrail / Braking teşhisleri. Sonuç ekranı: bileşen listesi + yeşil/sarı/kırmızı durum göstergesi + kayıtlı sesi dinletme + beklenen çalışma videosuyla karşılaştırma + şema/bakım talimatı gösterimi.

### 1.3 Bağımsız istem 1'in zorunlu unsurları (all-elements kuralı)

ABD'de ihlal için istemin **tüm** unsurlarının üründe bulunması gerekir:

1. Teşhis algoritmasını saklayan **bulut bilişim ağı**
2. Bulutla haberleşen **mobil terminal**
3. Mobil cihazın sürüş kalitesi verisini **belirlemesi**
4. Verinin bulutla **değiş tokuşu**
5. Teşhis sonucunun **bulutta üretilmesi** ve mobilde gösterilmesi
6. **Birinci mod GUI**: teşhis operasyonu seçimi + kullanım talimatı gösterimi
7. **İkinci mod GUI**: bileşen bazında teşhis sonucu gösterimi
8. Teşhis edilecek bileşenlerin seçilen operasyona göre **otomatik belirlenmesi**

İstem 8 (cihaz) ve 14 (yöntem) aynı çekirdeği taşıyor: bulutta saklanan algoritma + iki modlu GUI + otomatik bileşen belirleme.

### 1.4 Kapsam değerlendirmesi

- İstemler **dar ve çok unsurlu**: telefonla asansör titreşimi ölçme fikri tek başına kapsam içinde DEĞİL; korunan şey yukarıdaki 8 unsurun kombinasyonu.
- Patentin kendi atıfları fikrin tek başına yeni olmadığını gösteriyor (PDF'ten doğrulandı): arXiv:1607.00363 (Monteiro — telefonla asansör hız ölçümü, 2016), Kleemann "Lift Tester" (ELEVCON 2012), Play Store "Elevator Speed" uygulaması examiner önünde prior art olarak listelenmiş.
- Coğrafi kapsam: US tescili yalnız ABD'de hüküm doğurur. EP 18172185.3'ün akıbeti (tescil/ret/geri çekilme) bu oturumda **doğrulanamadı** `[DOĞRULANMASI GEREKİYOR — EPO Register kontrolü şart]`. Bir snippet EP karşılığını **EP3401263** olarak veriyor `[DOĞRULANMASI GEREKİYOR]`. Türkiye'de yürürlükte karşılığa dair hiçbir iz bulunamadı — ancak kanıt yokluğu, yokluk kanıtı değildir; TÜRKPATENT sorgusu yapılmalı.
- Hukuki durum (aktif mi, idame ücretleri ödendi mi) doğrulanamadı. Nominal süre sonu: 12.05.2037 + PTA `[hesaplama, kaynak verisi değil]`. 7,5 yıllık idame ücreti penceresi 28.01.2027'de açılıyor — o tarihten sonra durum yeniden kontrol edilmeli (Otis ücreti ödemezse patent düşer).
- İlişkili Otis patentleri (snippet düzeyi): **US 10,723,588 B2** "System and method of measuring and diagnosing ride quality of an elevator system" (aynı çekirdek ekip — Copeland/Song + Borthakur/Rush), **US 9,556,002 B2** "Elevator noise monitoring" (taşınabilir cihaz "cep telefonu mikrofonu olabilir" — ses tabanlı mobil ölçüm), US 12,110,210 B2 (ride quality takibi), US 10,997,873 (ride quality simülatörü `[DOĞRULANMASI GEREKİYOR]`), US 10,954,102 (yürüyen merdiven teşhis adımı).

## 2. KONE tarafı: DT6 tespiti ve KONE'nin dijital araçları

### 2.1 DT6 nedir — tespit edildi (snippet düzeyi)

**DT6 bir mobil uygulama değil, KONE'nin kendi bakım personelinin kullandığı sürüş konforu ölçüm CİHAZI** ("KONE DT-6 Elevator Ride Comfort Analyzer"):

- Asansöre **üç temas noktasından** doğrudan bağlanıp en küçük titreşimleri ve çalışma seslerini kaydediyor; standartlaştırılmış sürüş kalitesi verisi topluyor (Red Dot Design Award proje sayfası + tasarımcı Jouni Junes portföyü — snippet).
- Öncülü **DT-5** doğrulandı (Scribd'de kullanım talimatı, yedek parça sitesinde "ANALYZER, RIDE COMFORT, MODEL DT-5" kaydı). Yani DT serisi KONE'nin analizör ailesi.
- KONE kataloğunda satılmıyor — şirket içi saha aracı; ikinci el piyasada (eBay) dolaşıyor.
- Bulunamadı: çıkış yılı, teknik özellikler (örnekleme frekansı, ISO 18738 uyumu), eşlik eden yazılım, DT-7 halefi olup olmadığı, DT6'ya özgü patent kaydı.
- Üretim yeri çelişkili (bir kaynak Finlandiya, eBay özeti Almanya) — çözülemedi.

**LiftXPulse açısından anlamı:** KONE'nin DT6'sı EVA-625 sınıfı **özel donanım**. LiftXPulse telefon tabanlıysa DT6 ile aynı işi donanımsız yapmaya çalışıyor demektir — bu birebir rakiplik değil, farklı katman (bkz. §5).

### 2.2 KONE'nin bağlantılı servisleri (snippet düzeyi)

- **KONE 24/7 Connected Services**: Şubat 2016 KONE-IBM Watson IoT anlaşması, Şubat 2017 lansman; sonrasında AWS IoT'ye geçiş (1,6M ekipman hedefi — satıcı beyanı). Ölçülenler: kapı hareketleri, kalkış sayısı, sıcaklık, durma/seviyeleme hassasiyeti; sektör basınına göre ~200 parametre (satıcı kaynaklı rakam). Performans iddiaları (%70 proaktif tespit, %40 daha az tamir çağrısı vb.) tümüyle **satıcı beyanı**.
- **KONE Mobile** (2016, bakım müşterilerine yönelik) ve **Technician Assistant** (AWS üzerinde AI destekli teknisyen uygulaması — satıcı beyanı).
- KONE her kurulumda devir-teslim öncesi kabin içi gürültü/titreşim ölçümü yapıldığını beyan ediyor — DT6 bu sürecin cihazı olmaya en yakın aday (yorum).

### 2.3 KONE'nin akademik/patent ayak izi

- **Akademik ayak izi zayıf:** KONE'yi doğrudan inceleyen belirgin tek hakemli yayın Emerald IJOPM 2019 servitizasyon vaka çalışması (Rajala ve ark., DOI 10.1108/IJOPM-04-2018-0195 `[DOĞRULANMASI GEREKİYOR]`). Onun dışında KONE'ye değinen tezler (TU Wien 2022) ve KONE'ye özgü olmayan IEEE yayınları var. DT6'nın veya 24/7 CS'nin kendisini konu alan akademik makale **bulunamadı**.
- **Patentler sabit sensör mimarisinde:** US7823706B2 (kabin üstü ünite + ivme sensörü, ~2026'da süre sonu `[hesap]`), US7434666B2 (durma hassasiyeti), US9604818B2 (frekans bileşeni izleme), EP2872432B1 (ray düzgünlüğü ölçümü), US11795034B2 (sabit ses toplayıcı — yürüyen merdiven), US6863161B2 (otomatik test sürüşüyle tele-izleme), US20240199374A1 (kabin üstü ivmeölçer + ML, henüz başvuru).
- **KRİTİK:** KONE'ye ait, **telefonun dahili sensörleriyle ölçüm yapan patent bulunamadı.** Mobil-sensör çakışma riski KONE'den değil **Otis'ten** kaynaklanıyor. (Kanıt yokluğu notu: yayımlanmamış/FI-yalnız başvurular taramada görünmemiş olabilir.)

## 3. Akademik literatür özeti (snippet düzeyi)

### 3.1 Telefonla asansör ölçümü — fizibilite literatürde kanıtlı

- **Monteiro & Martí** (arXiv:1607.00363; Physics Education 52(1):015010, 2017, DOI 10.1088/1361-6552/52/1/015010): telefon **barometresi** + hidrostatik yaklaşımla dikey hız; yazar beyanı: basınç verisi, ivmeölçer integrasyonundan belirgin daha az gürültülü. Otis patentinde atıflı (PDF'ten doğrulandı). **LiftXPulse için doğrudan özellik fikri: barometre ile hız/kat tespiti.**
- **Zhao grubu** (Mechanical Systems and Signal Processing 105:377-390, 2018, DOI 10.1016/j.ymssp.2017.12.005 `[DOĞRULANMASI GEREKİYOR]`): telefon 3 eksenli ivmeölçeri + Orion-CC uygulaması; ISO 2631-1997 tabanlı konfor değerlendirmesi; **sarsma tablasında piezoelektrik ivmeölçere karşı doğrulama**, 3 binada saha validasyonu (yazar beyanı: "hassasiyet mühendislik gereksinimlerini karşılıyor"). Öncülü: SPIE 10168:101683C (2017), DOI 10.1117/12.2259771.
- **Kuhn, Vogt & Müller** (The Physics Teacher 52(1):55-56, 2014): ivmeölçerle kabin salınımı analizi (eğitim bağlamı).
- **Li ve ark.** (Emerald JIMSE 3(2):156-172, 2022, DOI 10.1108/JIMSE-09-2022-0018, açık erişim): ISO 18738-1 ile ISO 2631-4 konfor sonuçları tutarlı; ISO 2631-4 daha hassas nicel tanım (yazar beyanı). IoT tabanlı ölçüm (telefon değil).
- **Capuano ve ark.** (MDPI Sensors 23(17):7609, 2023, DOI 10.3390/s23177609): telefon MEMS IMU hataları **telefon modeline güçlü bağımlı** — LiftXPulse'ta cihaz bazlı kalibrasyon zorunluluğunun akademik gerekçesi.

### 3.2 Kestirimci bakım literatürü — tema haritası

- **Sensör yerleşimi tipolojisi:** kabin üstü ivmeölçer / makine yatağı + ray MEMS / kapı sürücüsü test düzeneği / kapı SES sinyali / telefon. Gerçek binada saha verisiyle çalıştığı anlaşılan tek hat telefon tabanlı konfor izleme (MSSP 2018).
- **ML spektrumu:** autoencoder+RF (Mishra & Huhtala, App.Sci. 9(15):2990, 2019), transfer learning ile kapı RUL (Sensors 24(7):2135), GARN (Electronics 14(11):2308), hafif Transformer + edge (Micromachines 17(4):401), digital twin + PINN (Sci.Rep. 14:30713, DOI 10.1038/s41598-024-78784-7).
- **Doğruluk beyanları %90-100 bandında ama çoğu laboratuvar/simülasyon** — yazar beyanı, bağımsız doğrulama yok; Mishra & Huhtala'nın iki yayını arasında %100 vs >%90 çelişkisi var (gizlenmedi).
- **Alanın ana problemi arıza verisi kıtlığı** → transfer learning, sentetik veri (PINN), few-shot yaklaşımları. **Kapı arızaları ayrı bir alt literatür** (ses/titreşim/akım tabanlı ≥5 çalışma) — kapı, arızanın en sık kaynağı olduğu için LiftXPulse'un ilk hedef teşhisi kapı olmalı (yorum).

## 4. Standart çerçevesi: ISO 18738 → ISO 8100-34

- **Soyağacı:** ISO 18738:2003 → ISO 18738-1:2012 → **GERİ ÇEKİLDİ**, yerine **ISO 8100-34:2021** ("minor revision"). Güncel atıf ISO 8100-34'e yapılmalı. (ISO 18738-2 yürüyen merdivenler için ayrı.)
- **Standart sınır koymaz:** yalnızca ölçüm/işleme/raporlama metodolojisi tanımlar; kabul/ret eşiği yok.
- **Metrikler:** 3 eksenli ivme; V95 hız; **jerk** = 10 Hz filtreli z-ekseni ivmesinden 0,5 s kayan en küçük kareler doğrusunun eğimi; frekans-ağırlıklı titreşimde **Max peak-to-peak + A95 peak-to-peak** ikilisi; ses: dB(A) ref 20 µPa, LAeq + LApk,max. Ölçüm sınırları: kalkış −0,5 s / kalkış +500 mm / duruş −500 mm / duruş +0,5 s.
- **Cihaz gereksinimi:** titreşim zinciri **ISO 8041** kalibrasyonlu olmalı (8 Hz + 0,1–80 Hz'de ≥5 frekans sinüzoidal doğrulama, anti-aliasing, sıkıştırılmamış veri); ses kanalı **IEC 61672 Class 2**. Tipik telefon bunları fabrika halinde **karşılamaz**.
- **Sektör dili buna göre şekillenmiş:** DEKRA LiftCheck "ride quality **based on** ISO 18738" diyor, "compliant" demiyor; Henning "evaluation **to** ISO 18738" diyor ama **harici kalibre sensör** satıyor; PMT EVA-625 "ISO 18738 ile tutarlı sonuç ayarı" diyor (hepsi satıcı beyanı).
- **LiftXPulse kuralı:** pazarlama ve raporlarda **"ISO 8100-34'e dayalı ölçüm"** ifadesi kullanılmalı, "uyumlu/sertifikalı" ASLA — ta ki harici kalibre sensör opsiyonu eklenene kadar. Resmi/periyodik muayene amaçlı ölçümlerde telefon verisi tek başına delil kabul edilmeyebilir; rapor şablonuna "gösterge niteliğinde tarama ölçümü" ibaresi konmalı (yorum + sektör pratiği).

## 5. Ticari rakip haritası (snippet düzeyi; fiyatlar bayi/satıcı beyanı)

| Katman | Ürün | Üretici | Donanım | ISO iddiası | Fiyat sinyali |
|---|---|---|---|---|---|
| Profesyonel donanım | EVA-625 | PMT (ABD) | Özel cihaz (±1,5 g, DC-400 Hz, 256/512 SPS, mikrofon) | "ISO 18738 ile tutarlı" (satıcı) | ~₹425.000 ≈ 5.000-5.500 USD (bayi) |
| Profesyonel donanım | QS3 / RIDEanalyzer | Henning (DE) | Harici 3D ivmeölçer (+laptop veya bağımsız gövde) | "to ISO 18738 + GB/T 10058" (satıcı) | bulunamadı |
| OEM içi donanım | **DT-6 (DT-5 halefi)** | KONE | Özel analizör, 3 temas noktası | bulunamadı | satılmıyor (şirket içi) |
| Telefon + bulut | **LiftCheck** | DEKRA (DE) | Telefon (zemine konur) + sunucu analizi + e-posta rapor | "**based on** ISO 18738" | bulunamadı |
| Telefon | Lift Tester | Kleemann (GR) | Telefon (iOS+Android, ELEVCON 2012'den beri) | yok | ücretsiz görünüyor |
| Telefon | EleMeter | figix (JP) | Telefon; hız/yükseklik/ivme, CSV export | yok | ücretsiz görünüyor |
| Telefon (ölü) | Elevator Speed | "Beno" | Telefon; 2011, artık yayında değil | yok | ücretsizdi |

Okuma: pazar iki katmanlı — 5.000$+ tam donanım ile ücretsiz "oyuncak" uygulamalar arasında, **DEKRA dışında ciddi telefon tabanlı profesyonel çözüm yok**. LiftXPulse'un doğal konumu bu boşluk: profesyonel raporlama + telefon maliyeti.

## 6. Patent çakışma riski ve design-around

### 6.1 Risk tablosu

| Patent | Sahip | Kapsadığı alan | LiftXPulse riski |
|---|---|---|---|
| US 10,547,917 B2 | Otis | Telefon + **bulutta teşhis** + iki modlu rehberli GUI + otomatik bileşen eşleme | **Birincil risk (ABD'de).** Aşağıdaki design-around ile yönetilebilir |
| US 9,556,002 B2 | Otis | Taşınabilir cihaz/telefon **mikrofonuyla** ses kaydı → uzak bakım sistemine gönderme, zaman içi değişim analizi | Ses özelliği + buluta gönderme birlikteyse risk `[istem metni doğrulanmalı]` |
| US 10,723,588 B2 | Otis | Mobil cihazla veri toplama + **harici bilgisayarda** ride quality teşhisi | US10547917'nin kardeşi; birlikte değerlendirilmeli `[istem metni doğrulanmalı]` |
| US 11,524,869 B2 | Inventio (Schindler) | **Yolcunun** telefonunun kabinde otomatik ölçüm toplaması (kat kapısı algılamalı) → merkezi değerlendirme | Crowd-sourcing / yolcu-pasif-ölçüm özelliği planlanırsa risk |
| US 11,745,979 | Mitsubishi `[DOĞRULANMASI GEREKİYOR]` | Kabine geçici takılan ivme+kamera cihazı, kameradan yönelim tespiti | Telefon kamerayla yönelim düzeltmesi yapılırsa bakılmalı |
| US 7,073,633 B2 | Inventio | GSM/mobil terminalle uzaktan bakım (2003) | **Süresi doldu (01.06.2024 `[DOĞRULANMASI GEREKİYOR]`) — temel yaklaşım artık serbest** |
| KONE portföyü | KONE | Sabit sensör mimarileri | Telefon tabanlı LiftXPulse ile **çakışma bulunamadı** |

### 6.2 Design-around önerileri (US 10,547,917'ye karşı)

All-elements kuralı gereği istemden TEK unsuru düşürmek ihlali ortadan kaldırır (ABD hukuku; doctrine of equivalents riski için vekil görüşü şart):

1. **Teşhisi telefonda çalıştır (edge/on-device).** İstem "algoritmanın bulutta saklanması + sonucun bulutta üretilmesi"ni şart koşuyor. On-device analiz hem istemi boşa düşürür hem KVKK/veri maliyeti avantajı sağlar. Bulut yalnız arşiv/raporlama için kullanılabilir — "teşhis sonucu üretme"nin nerede olduğu net dokümante edilmeli.
2. **İki modlu GUI kalıbından kaçın.** "Operasyon seç → talimat göster" + "bileşen bazlı sonuç ekranı + otomatik bileşen belirleme" akışını birebir kopyalama; örn. tek akışlı sürekli kayıt + sefer bazlı rapor üret.
3. **Bileşen eşlemeyi otomatik yapma** ya da hiç bileşen bazlı sonuç GUI'si kurma — metrik bazlı (jerk, A95, dB) rapor ver, bileşen çıkarımını yorum katmanında bırak.
4. **Coğrafya:** Türkiye pazarında ABD patenti hüküm doğurmaz. ABD/AB pazarına çıkmadan önce: EPO Register'da 18172185.3 / EP3401263 akıbeti + Espacenet aile taraması + vekil FTO görüşü.

Not: DEKRA LiftCheck'in mimarisi (telefon + sunucu analizi) Otis isteminin desenine yakın görünüyor ve piyasada duruyor — bu, patentin uygulanmadığı/dar yorumlandığı anlamına gelebilir ama hukuki güvence değildir (yorum).

### 6.3 Görece boş patent alanları (taramanın sınırları içinde; kesin FTO değil)

- Telefonun kendi IMU'suyla, harici donanımsız, **ISO 8100-34 referanslı kalibre ride-quality ölçümü** — üç büyük OEM'den patent çıkmadı.
- **Telefon mikrofonuyla akustik teşhis** (kapı/halat/makine sesi sınıflandırma) — OEM patenti bulunamadı (Otis US9556002 sınırı gözetilmeli).
- **Barometre ile kat/konum tespiti tabanlı teşhis** — yalnız sahibi belirsiz US10112801'de altimetre görüldü.

Bu üç boşluk, LiftXPulse'un hem ürün farklılaşması hem de (istenirse) kendi patent/faydalı model başvurusu için aday alanlar.

## 7. LiftXPulse uyumluluk değerlendirmesi

"Uyumluluk" iki eksende değerlendirildi: (a) patent/rakip ortamıyla çatışmadan yaşayabilirlik, (b) sektör standartları ve literatürle teknik uyum.

1. **Otis patentiyle uyumluluk:** LiftXPulse'un mevcut mimarisi bilinmiyor `[kod erişimi yok]`. Analiz telefonda yapılıyorsa ABD'de bile çakışma yok; bulutta yapılıyorsa §6.2'deki design-around uygulanmalı. **Türkiye pazarı için bugün itibarıyla bilinen engel yok** (EP/TR doğrulaması şartıyla).
2. **KONE DT6 ile ilişki:** DT6 rakip değil, referans model — KONE'nin şirket içi cihazla yaptığını LiftXPulse telefonla bağımsız pazara açıyor. KONE DT6'yı satmadığı için bağımsız servis firmaları ve A tipi muayene ekosistemi bu yeteneğe erişemiyor; LiftXPulse tam bu boşluğa oturuyor.
3. **Literatürle uyum:** Telefonla titreşim/konfor ölçümünün fizibilitesi hakemli literatürde sarsma-tablası doğrulamasıyla gösterilmiş (MSSP 2018). Barometre hattı (Monteiro 2017) hız/kat tespiti için ivme integrasyonundan daha kararlı — LiftXPulse'a eklenmeli. MEMS hatalarının cihaz-modeline bağımlılığı (Sensors 2023) nedeniyle **cihaz bazlı kalibrasyon prosedürü** (örn. bilinen referans asansörde ilk-kurulum kalibrasyonu) şart.
4. **Standartla uyum:** Metrik seti ISO 8100-34 terminolojisiyle kurulmalı (Max PP, A95, jerk, V95, LAeq/LApk,max, sınır 0-3 segmentasyonu) — raporun sektörde ciddiye alınmasının ön şartı bu dil. İddia seviyesi "based on" olmalı (§4).
5. **MontajTakip sinerjisi:** COM aşamaları ve devir-teslim akışına "sürüş kalitesi ölçüm raporu" adımı eklenebilir — KONE'nin handover ölçüm pratiğinin (§2.2) bağımsız karşılığı. `[MontajTakip entegrasyonu ayrıca tasarlanmalı]`

## 8. SWOT — LiftXPulse

Varsayım: telefon tabanlı sürüş kalitesi ölçüm/tanılama uygulaması `[DOĞRULANMASI GEREKİYOR]`.

### Güçlü yönler (S)
- **Donanım maliyeti sıfır:** rakip profesyonel katman 5.000$+ (EVA-625) veya hiç satılmıyor (DT6); LiftXPulse mevcut telefonla çalışır.
- **OEM bağımsız:** her marka asansörde kullanılabilir; OEM platform kilidi (KONE 24/7, MAX, Ahead) dışında kalan geniş bağımsız servis pazarına hitap eder.
- **Fizibilite hakemli literatürle destekli** (MSSP 2018 sarsma tablası doğrulaması; Monteiro 2017 barometre).
- **Alan uzmanlığı:** EN 81-20/İSO 8100 bilgisi + denetim/muayene pratiği üründe metodoloji derinliği sağlar — uygulama mağazasındaki "oyuncak" ölçüm app'lerinden temel fark.
- **Design-around alanı net:** birincil patent riski (Otis) tek mimari kararla (on-device analiz) yönetilebilir.

### Zayıf yönler (W)
- **Telefon MEMS'i ISO 8041 kalibrasyon zincirini sağlayamaz** → "ISO uyumlu" iddiası imkânsız; resmi muayenede delil değeri sınırlı, "gösterge ölçümü" konumunda kalır.
- **Cihaz modeline bağımlı doğruluk** (Sensors 2023) → kalibrasyon prosedürü ve cihaz beyaz listesi yükü.
- **Etiketli arıza verisi yok** (literatürün de ana problemi) → teşhis modellerinin eğitimi zaman ister; ilk sürüm metrik raporlayıcı olmalı, "arıza teşhisi" iddiası sonraya bırakılmalı.
- **Kurulu taban ve marka yok;** DEKRA gibi kurumsal güven veren bir rakip aynı katmanda mevcut.
- Kod tabanının durumu bu analizde görülemedi `[repo erişimi yok]` — teknik borç/olgunluk bilinmiyor.

### Fırsatlar (O)
- **Pazar boşluğu:** 5.000$ donanım ile ücretsiz app arasındaki profesyonel-telefon katmanında DEKRA dışında oyuncu yok; Türkiye'de hiç yok `[yerel rakip taraması yapılmadı — doğrulanmalı]`.
- **Türkiye periyodik muayene ekosistemi:** A tipi muayene kuruluşları ve bağımsız servisler için düşük maliyetli ön-tarama aracı; yıllık zorunlu muayene hacmi hazır talep tabanı.
- **Görece boş patent alanları** (§6.3): barometre-tabanlı tespit + telefon-mikrofon akustik analiz + kalibre IMU ölçümü — hem ürün farklılaşması hem kendi başvuru fırsatı.
- **Akademik yayın potansiyeli:** Türkiye sahasından gerçek veriyle telefon-tabanlı ölçüm validasyonu makalesi (Emerald JIMSE / MDPI hattı) — ürün güvenilirliğini ve kişisel akademik hattı aynı anda besler; alanda saha-verisi çalışması azlığı yayın şansını artırır.
- **Süresi dolan patentler:** Inventio 2003 (teknisyen-mobil uzaktan bakım temeli) serbest; KONE'nin erken sabit-sensör patentleri de süre sonunda.
- **MontajTakip entegrasyonu:** devir-teslim ölçüm raporu modülü olarak çapraz satış.

### Tehditler (T)
- **Otis patent ailesi** (US10547917 + US10723588 + US9556002): ABD/AB pazarına açılımda FTO riski; EP akıbeti hâlâ bilinmiyor `[DOĞRULANMASI GEREKİYOR]`.
- **Schindler US11524869B2:** yolcu-telefonu crowd-sensing yönüne genişleme kapalı (aktif patent).
- **OEM platform kapatması:** KONE 24/7 / TKE MAX / Schindler Ahead sözleşmeleri servis pazarını OEM'e kilitledikçe bağımsız ölçüm aracının alanı daralır.
- **DEKRA'nın ölçeklenmesi:** aynı katmandaki kurumsal rakip pazarı hızla kaplayabilir; Çin tarafında telefon+bulut bakım patenti/ürünü yoğunluğu var.
- **Ücretsiz app algısı:** mağazadaki bedava ölçüm uygulamaları fiyat algısını aşağı çeker; farklılaşma "rapor + metodoloji + standart dili" üzerinden kurulmalı.
- **Regülasyon:** kalibrasyonsuz ölçümün resmi süreçlerde reddedilmesi; ileride standartların mobil ölçüme açık kısıt getirmesi ihtimali.

## 9. Kaynakça ve doğrulama durumu

### 9.1 Tam okunan (1)
1. US 10,547,917 B2 tam metni — USPTO PDF (kullanıcı yüklemesi, 14 sayfa, istemler dahil okundu).

### 9.2 Yalnızca özet/snippet düzeyi okunanlar (seçki — tümü `tam_okundu: false`)
Patentler: US10723588, US9556002, US12110210, US10954102 (Otis); US7823706, US7434666, US9604818, EP2872432, US11795034, US6863161, US20240199374 (KONE); US11524869, US7073633 (Inventio); WO2021157086/US11745979, JP2022184498A (Mitsubishi); US10112801 (sahibi belirsiz).
Akademik: arXiv:1607.00363 / Phys.Educ. 2017 (10.1088/1361-6552/52/1/015010); MSSP 105:377-390 (10.1016/j.ymssp.2017.12.005); SPIE 10168 (10.1117/12.2259771); Phys.Teach. 52(1) 2014; Emerald JIMSE 3(2) 2022 (10.1108/JIMSE-09-2022-0018); Emerald IJOPM 39(5) 2019 (10.1108/IJOPM-04-2018-0195); MDPI Sensors 23(17):7609, 24(7):2135, 25(1):101; App.Sci. 9(15):2990, 15(13):7017; Electronics 14(11):2308; Micromachines 17(4):401; Sci.Rep. 14:30713; IEEE Potentials 40(1) 2021.
Standart/sektör: ISO 18738:2003, ISO 18738-1:2012 (geri çekildi), ISO 8100-34:2021, ISO 8041-1:2017, IEC 61672; PMT EVA-625, Henning QS3/RIDEanalyzer, DEKRA LiftCheck, Kleemann Lift Tester, EleMeter; KONE 24/7 CS / KONE Mobile / AWS vaka sayfaları; Red Dot DT6 sayfası; TKE MAX ve Schindler Ahead bültenleri.

### 9.3 Manuel indirme öncelik listesi (ağ engeli nedeniyle tam metni alınamayanlar)
Sıra önem sırasıdır; indirilip paylaşılırsa rapor güncellenir:
1. https://patents.google.com/patent/US10547917B2/en — hukuki durum + aile + Cited By
2. https://register.epo.org/application?number=EP18172185 — EP akıbeti (KRİTİK)
3. https://patents.google.com/patent/EP3401263A1/en — EP karşılığı iddiasının teyidi
4. https://patents.google.com/patent/US10723588B2/en — kardeş patent istemleri
5. https://patents.google.com/patent/US9556002B2/en — ses tabanlı mobil ölçüm istemleri
6. https://patents.google.com/patent/US11524869B2/en — Schindler yolcu-telefonu patenti
7. https://arxiv.org/pdf/1607.00363 — barometre yöntemi tam metin
8. https://doi.org/10.1016/j.ymssp.2017.12.005 — MSSP 2018 (paywall olabilir; abstract yeterli)
9. https://www.emerald.com/insight/content/doi/10.1108/jimse-09-2022-0018/full/html — ISO 18738 vs 2631-4 (açık erişim)
10. https://www.iso.org/standard/73086.html — ISO 8100-34:2021 künye
11. https://www.dekra.com/en/lift-check-app/ — rakip mimari
12. https://henning-gmbh.de/wp-content/uploads/2025/11/User-Manual_RIDEanalyzer_en_19.pdf — rakip cihaz kılavuzu
13. https://www.pmtvib.com/eva-625 — EVA-625 spec
14. https://www.red-dot.org/project/kone-dt6-34166 — DT6 resmi tanım

### 9.4 Açık doğrulama maddeleri
- EP 18172185.3 / EP3401263 akıbeti; ABD idame ücreti durumu (28.01.2027 penceresi)
- TÜRKPATENT'te Otis ride-quality aile taraması
- MSSP 2018 DOI/yazar listesi; Emerald IJOPM yazar listesi
- KONE DT6 teknik özellikleri ve patent bağlantısı
- US10112801, US11745979 assignee'leri
- Türkiye'de yerel rakip uygulama taraması (hiç yapılmadı)
