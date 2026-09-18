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

NOT: Fonksiyonlar `yazdir/"merhaba"/` veya `yazdir "merhaba"` şeklinde
çağrılabilir. Çağrılarda `/` karakterleri isteğe bağlıdır; fonksiyon
tanımlarındaki parametrelerde ise zorunludur.

### Yorum Ekleme

```vtl
# Bu bir yorumdur
```

### Ekrana Veri Yazdırma

`yazdir/dize str/`

```vtl
yazdir "Merhaba, dünya!"
yazdir/"Merhaba, dünya!"/
```

### Kullanıcıdan Veri Alma

`veri/dize mesaj/`

```vtl
dize isim = veri "İsminiz?"
dize soyisim = veri/"Soyisminiz?"/
```

### Karakter Sayısını Hesaplama

`uzunluk`

```vtl
uzunluk "Merhaba, dünya!"
uzunluk/"Merhaba, dünya!"/
```

### Mutlak Değer Alma

`mutlak/sayisal sayi/`

```vtl
sayisal on = mutlak -10
sayisal yirmi = mutlak/-20/
```

### Liste Oluşturma

```vtl
sayisal abc = 10

liste myList = liste.yeni 1,abc,3.14
liste digerListe = liste.yeni/1,abc,3.14/
```

### Listeye Eleman Ekleme

```vtl
myList.ekle "Abc"
myList.ekle/314/
myList.ekle/314,"selam"/
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

## Matematik ve Aralık İşlemleri

### Matematiksel İşlemler

```vtl
sayisal toplama = 5 + 5
sayisal cikartma = 5 - 5
sayisal carpma = 5 * 5
sayisal bolme = 5 / 5
```

### Artır/Azalt

```vtl
sayisal x = 10

x artir # x = 11
x azalt # x = 10
```

### Aralık Oluşturma (Range)

`aralik/sayisal min, sayisal max/`

`min`, `max` değerinden küçük olmalıdır. Üretilen liste alt sınırı içermez,
üst sınırı içerir.

```vtl
liste araligim = aralik 0, 10
# 1, 2, 3, 4, ..., 10

liste ikinciAralik = aralik/10, 20/
```

## Eklenilmesi Şu Anlık Düşünülmüyor

### Sürüm Bilgisini Öğrenme

```vtl
yazdir surum
```
