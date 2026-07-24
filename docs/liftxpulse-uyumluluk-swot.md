# LiftXPulse — Otis Patent Değerlendirmesi, KONE Araştırması, Uyumluluk + SWOT

Tarih: 2026-07-24
Girdi: `otkssensor.pdf` (US 10,547,917 B2 tam metni, 14 sayfa, USPTO)

---

## 0. Durum notu (dürüstlük beyanı)

- **LiftXPulse kodu bu repoda yok.** `coin` repo'sunda README dışında tek içerik trading-AI branch'i. Hesabındaki repo listesinde de `liftxpulse` adlı repo görünmüyor. Bu analiz, LiftXPulse'un **"akıllı telefon sensörleriyle (ivmeölçer/barometre/mikrofon) asansör sürüş kalitesi ölçümü ve tanılama uygulaması"** olduğu varsayımına dayanıyor `[DOĞRULANMASI GEREKİYOR — kod hangi repodaysa söyle, ekleyince kod seviyesinde güncellerim]`.
- Patent analizi hukuki görüş değildir; başvuru/FTO kararı öncesi patent vekili şart.

## 1. Ekteki PDF: US 10,547,917 B2 analizi

### 1.1 Kimlik

| Alan | Değer |
|---|---|
| Patent no | US 10,547,917 B2 |
| Başlık | Ride Quality Mobile Terminal Device Application |
| Sahip (assignee) | Otis Elevator Company, Farmington CT |
| Buluşçular | George Scott Copeland, Jinho Song |
| Başvuru | 12 Mayıs 2017 (Appl. 15/593,707) |
| Ön yayın | US 2018/0332368 A1 (15 Kasım 2018) |
| Tescil | 28 Ocak 2020 |
| İstem sayısı | 19 (3 bağımsız: 1=sistem, 8=cihaz, 14=yöntem) |
| Süre uzatması | 35 U.S.C. 154(b) ile +25 gün |

### 1.2 Ne anlatıyor

Servis sağlayıcılar arızayı çoğunlukla kullanıcı şikâyetiyle öğreniyor; teşhis için asansörü servis dışına alıp panel arkasındaki donanıma erişmek gerekiyor. Patentin çözümü: teknisyenin **akıllı telefonu** (kamera + mikrofon + hoparlör + tek/çok eksenli ivmeölçer) sürüş kalitesi verisini toplar, **bulut** üzerindeki teşhis algoritması sonucu üretir, telefon sonucu bileşen bazında gösterir.

Tanımlı teşhis operasyonları: **Door Cycle** (kapı çevrimi — telefonu göğüs hizasında kapıya dönük tut), **Floor-to-Floor** (kat arası seyir), **Machine Diagnostic** (makine dairesi ses karşılaştırma); yürüyen merdiven için Step Run / Handrail / Braking teşhisleri. Sonuç ekranı: bileşen listesi + yeşil/sarı/kırmızı durum göstergesi + kayıtlı sesi dinletme + beklenen çalışma videosuyla karşılaştırma + şema/bakım talimatı gösterimi.

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

İstem 8 (cihaz) ve 14 (yöntem) de aynı çekirdeği taşıyor: bulutta saklanan algoritma + iki modlu GUI + otomatik bileşen belirleme.

### 1.4 Kapsam değerlendirmesi — ne kapsıyor, ne kapsamıyor

- İstemler **dar ve çok unsurlu**: telefonla asansör titreşimi ölçme fikri tek başına kapsam içinde DEĞİL; korunan şey "bulutta koşan algoritma + iki modlu rehberli GUI + otomatik bileşen eşleme" kombinasyonu.
- Patentin kendi atıfları da fikrin tek başına yeni olmadığını gösteriyor: arXiv:1607.00363 (telefonla asansör hız ölçümü, 2016), Kleemann "Lift Tester" (ELEVCON 2012), Play Store "Elevator Speed" uygulaması examiner önünde prior art olarak listelenmiş.
- Coğrafi kapsam: US tescili yalnız ABD'de hüküm doğurur. EP başvurusu 18172185.3 dosyada geçiyor — akıbeti (tescil/ret/geri çekilme) aşağıda §6'da `[ARAŞTIRMA SONUCU EKLENECEK]`.

## 2. KONE tarafı: "DT6" tespiti ve KONE'nin karşılık gelen uygulamaları

`[ARAŞTIRMA SONUCU EKLENECEK]`

## 3. Akademik literatür özeti

`[ARAŞTIRMA SONUCU EKLENECEK]`

## 4. Standart çerçevesi: ISO 18738 ve ölçüm gereksinimleri

`[ARAŞTIRMA SONUCU EKLENECEK]`

## 5. Ticari rakip haritası

`[ARAŞTIRMA SONUCU EKLENECEK]`

## 6. Patent çakışma riski ve design-around

`[ARAŞTIRMA SONUCU EKLENECEK]`

## 7. LiftXPulse uyumluluk değerlendirmesi

`[ARAŞTIRMA SONUCU EKLENECEK]`

## 8. SWOT

`[ARAŞTIRMA SONUCU EKLENECEK]`

## 9. Kaynakça

`[ARAŞTIRMA SONUCU EKLENECEK — tam okunan / yalnızca özet okunan ayrımıyla]`
