# Vega Dilinin Gramarı

## Veri Tipleri

**Sayısal/Integer** = `sayisal`

**Dize/String** = `dize`

---

## Değişkenler

**Değişken oluşturma/tanımlama**:

```vtl
sayisal x = 10

dize y = "Merhaba, dünya!"
```

---

## Built-in Fonksiyonlar

```vtl

# Yorum ekleme

## Ekrana veri yazdırma

yazdir "Merhaba, dünya!"

## Kullanıcıdan veri alma

x = veri "İsminiz?"

## Karakter Hesaplama

uzunluk "Merhaba, dünya!"

## Listeleme Yapmak

liste myList = liste.yeni 1,abc,3.14

## Listeye Eleman Ekleme

myList.ekle "Abc"
myList.ekle 314
myList.ekle "abc",3.14
```

---

## Çok Yakında Ekelencek

#Mutlak Değer Alma

mutlak(-10)

#Şartlar

eger a = b
    yazdir "No 1"
ikincil a = c
    yazdir "No 2"
degilse:
    yazdir "No 3"

#Fonksiyon 

ata MerhabaDunya/
    yazdir "Hello World!"

MerhabaDunya/


#Hata Yakalama

tekrarla:
        x = "Hello World!"
hata:
    yazdir "Hata!"

#Sürüm Öğrenme

yazdir surum


