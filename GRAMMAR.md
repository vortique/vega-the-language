# Vega Dilinin Grameri

## Veri Tipleri

**Sayısal/Integer** = `sayisal`

**Dize/String** = `dize`

**Boolean** = `bool`

Boolean değerleri `dogru` ve `yanlis` olarak yazılır.

---

## Değişkenler

**Değişken oluşturma/tanımlama**:

```vtl
sayisal sayim = 10

dize dizem = "Merhaba, dünya!"

bool dogruDeger = dogru
bool yanlisDeger = yanlis
```

---

## Yerleşik Fonksiyonlar

### Yorum Ekleme

```vtl
# Bu bir yorumdur
```

### Ekrana Veri Yazdırma

```vtl
yazdir "Merhaba, dünya!"
```

### Kullanıcıdan Veri Alma

```vtl
dize isim = veri "İsminiz?"
```

### Karakter Sayısını Hesaplama

```vtl
uzunluk "Merhaba, dünya!"
```

### Mutlak Değer Alma

```vtl
sayisal on = mutlak -10
```

### Liste Oluşturma

```vtl
liste myList = liste.yeni 1,abc,3.14
```

### Listeye Eleman Ekleme

```vtl
myList.ekle "Abc"
myList.ekle 314
myList.ekle "abc",3.14
```

---

## Şartlar (`if/elif/else`)

Girintiler şart bloklarını belirler. `eger` ve `ikincil` satırlarında iki nokta
isteğe bağlıdır; `degilse` satırında zorunludur.

```vtl
sayisal verim = veri "Sayı gir: "

eger verim > 10
    yazdir "No 1"
ikincil verim < 0
    yazdir "No 2"
degilse:
    yazdir "No 3"
```

---

## Fonksiyon Tanımlama ve Çağırma

Fonksiyon gövdesi girintiyle belirtilir. Parametreler `/` karakterleri arasında
tip ve isimleriyle tanımlanır.

```vtl
belirle MerhabaDunya/dize mesaj, dize aciklama/
    yazdir mesaj
    yazdir aciklama

MerhabaDunya/"Merhaba, dünya!", "Vega'dan selamlar!"/

# Alternatif çağırma biçimi
MerhabaDunya "Merhaba, dünya!", "Vega'dan selamlar!"
```

---

## Hata Yakalama

`dene` bloğunda oluşan çalışma zamanı hataları `yakala` bloğunu çalıştırır.

```vtl
dene:
    x = "Hello World!"
yakala:
    yazdir "Hata!"
```

---

## Çok Yakında Eklenecek

### Sürüm Bilgisini Öğrenme

```vtl
yazdir surum
```
