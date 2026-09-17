# Hazır İşler

Hepsi her zaman elinin altında — `use` yazmana gerek yok.
Çoğunun hem İngilizce hem Türkçe adı vardır; ikisi de aynı şeyi yapar.

Bir işi hem doğrudan hem nokta ile çağırabilirsin:

```ton
print(upper(%ad%))
print(%ad%.upper())
```

Bütün listeyi görmek için: `ton isler`

---

## Yazdırma ve okuma

| İş | Türkçe | Ne yapar |
|---|---|---|
| `print(...)` | `yaz` | Ekrana yazar, alt satıra geçer |
| `write(...)` | `yazdir` | Alt satıra geçmeden yazar |
| `ask(soru)` | `sor` | Kullanıcıdan cevap alır |

```ton
print: Merhaba %ad%
print("a", "b")
ad = ask("Adın ne? ")
```

## Tür ve dönüşüm

| İş | Türkçe | Ne yapar |
|---|---|---|
| `type(x)` | `tur` | Türünü verir: metin, sayi, ondalik, bool, liste, harita, null, is, gorev |
| `text(x, basamak)` | `metin` | Metne çevirir |
| `number(x, varsayilan)` | `sayi` | Sayıya çevirir |
| `int(x)` | `tam` | Tam sayıya çevirir |
| `bool(x)` | `mantik` | Doğru/yanlış değerine çevirir |
| `liste(x)` / `harita(x)` | | Listeye / haritaya çevirir |
| `len(x)` | `uzunluk` | Uzunluk |
| `copy(x)` | `kopya` | Kopyasını verir |
| `is_empty(x)` | `bos_mu` | Boş mu |

## Metin

`upper` `lower` `trim` `title` `split` `join` `replace` `contains` `starts` `ends`
`find` `slice` `reverse` `lines` `count` `pad` `match` `matches` `clean`
`chars` `code` `char` `repeat_text`

Türkçeleri: `buyuk` `kucuk` `kirp` `basharf` `ayir` `birlestir` `degistir` `icerir`
`ile_baslar` `ile_biter` `bul` `kes` `ters` `satirlar` `adet` `doldur` `esles`
`eslesenler` `temizle` `karakterler` `kod` `karakter`

```ton
print(%m%.trim().lower().split(" "))
print("a,b".split(","))
print(join(["a", "b"], "-"))
print("tel: 0555".matches("[0-9]+"))
```

## Liste

`push` `pop` `insert` `remove` `first` `last` `unique` `sum` `avg` `min` `max`
`sort` `reverse` `contains` `find` `range` `zip` `flat` `merge`
`map` `filter` `reduce` `each` `group` `any` `all`

Türkçeleri: `ekle` `cikar_son` `araya_ekle` `sil` `ilk` `son_oge` `benzersiz`
`topla` `ortalama` `enkucuk` `enbuyuk` `sirala` `ters` `icerir` `bul` `aralik`
`esle` `duzlestir` `kaynastir` `donustur` `sec` `indirge` `hepsi` `grupla`
`herhangi` `hepsi_dogru`

```ton
ekle(%liste%, 4)
print(%liste%.sort(tersten: true))
print(sort(%kisiler%, "yas"))
print(group(%kisiler%, "sehir"))
print(map([1, 2, 3], func(x) -> %x% * 2))
```

## Harita

`keys` `values` `items` `has` `al` `set` `remove` `merge`
(`anahtarlar` `degerler` `ciftler` `var_mi` `al` `koy` `sil` `kaynastir`)

```ton
print(%kisi%.keys())
print(%kisi%.get("yas", 0))
%kisi%.set("sehir", "Ankara")
```

## Matematik

`abs` `round` `floor` `ceil` `sqrt` `pow` `sin` `cos` `tan` `log` `pi`
`percent` `clamp` `random` `pick` `shuffle`

```ton
print(round(3.14159, 2))
print(random(1, 6))
print(percent(30, 200))
```

## Dosya

| İş | Türkçe |
|---|---|
| `read(dosya, varsayilan)` | `oku` |
| `save(dosya, icerik)` | `kaydet` |
| `append(dosya, icerik)` | `dosya_ekle` |
| `file_exists(dosya)` | `dosya_var` |
| `delete(dosya)` | `dosya_sil` |
| `files(klasor, desen)` | `dosyalar` |
| `folder(yol)` | `klasor` |
| `size(dosya)` | `boyut` |

## Ağ ve bağlantı

| İş | Ne yapar |
|---|---|
| `connect(adres)` | Bağlantı kurar (http ya da veritabanı) |
| `get(adres, parametreler)` | Tek seferlik GET |
| `post(adres, veri)` | Tek seferlik POST |
| `request(adres, yontem, veri)` | Ayrıntılı istek: `{durum, basarili, veri, basliklar}` |
| `download(adres, dosya)` | Dosya indirir |
| `encode(metin)` | Adres için güvenli hâle getirir |

HTTP bağlantısı: `.get(yol)` `.post(yol, veri)` `.put` `.patch` `.delete` `.ping()` `.durum` `.adres`
Veritabanı bağlantısı: `.run(sql, degerler)` `.all(sql)` `.one(sql)` `.tables()` `.close()`

## Eş zamanlı

| İş | Ne yapar |
|---|---|
| `asyn(is/adres, ...)` | Arka planda başlatır, görev döndürür |
| `wait(x)` | Sayıysa uyur, görevse bitmesini bekler |
| `waitall(gorevler)` | Hepsini bekler |
| `parallel([isler], ...)` | Hepsini aynı anda çalıştırır |
| `after(saniye, is)` | Sonra çalıştırır |
| `every(saniye, is, adet)` | Aralıklarla tekrarlar |
| `timeout(saniye, is, ...)` | Süre aşılırsa hata verir |

## Büyük veri

`data(dosya)` → `.count()` `.sum(alan)` `.avg(alan)` `.min` `.max` `.group(alan)`
`.totals(alan, deger)` `.top(n, alan)` `.bottom(n, alan)` `.sort(alan)` `.filter(is)`
`.map(is)` `.select(alanlar)` `.column(alan)` `.head(n)` `.rows()` `.each(is)` `.save(dosya)`

## Yapay zekâ

`ai(soru)` · `ai_setup(key:, model:, url:, kisilik:)` · `ai_json(soru)` ·
`ai_chat(gecmis, soru)` · `ai_ready()`

## Üstprogramlama

`meta(kod, degiskenler)` · `define(ad, parametreler, kod)` · `defined(ad)` ·
`get_var(ad)` · `set_var(ad, deger)` · `names()` · `builtins()` · `call(ad, argumanlar)` ·
`template(metin, degerler)` · `params(is)` · `eval_ton(ifade)`

## Zaman ve diğer

`now(bicim)` · `timestamp()` · `json(metin)` · `tojson(deger, guzel)` ·
`error(mesaj)` · `exit(kod)` · `show(deger)`
