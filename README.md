# TON Language

**Aşırı basit** bir programlama dili. Çekirdeği (`tnl core`) hiçbir ek gereksinim
istemez — Python 3.8+ dışında kurulum yoktur, indir ve çalıştır.

```ton
a = "merhaba"

print: %a%
```

```
merhaba
```

---

## Kurulum

```bash
git clone https://github.com/nylithra/ton-language
cd ton-language
./ton main.ton
```

Her yerden çalıştırmak için:

```bash
./install.sh          # ~/.local/bin/ton bağlantısı kurar
ton main.ton
```

Gereken tek şey Python 3.8+. Başka hiçbir paket yok.

---

## Dosya uzantıları

`.ton` &nbsp;·&nbsp; `.tn` &nbsp;·&nbsp; `.nyl` &nbsp;·&nbsp; `.tnl` — hepsi aynı şekilde çalışır.

```bash
ton main.ton
ton main.tn
ton main          # uzantıyı yazmasan da bulur
```

---

## Üç altın kural

**1. Değişkeni yazarken düz ad, okurken `%ad%`.**

```ton
ad = "Nyl"          # yazarken
print: Merhaba %ad% # okurken
```

Tür belirtmezsin; metin de olsa sayı da olsa aynı şekilde kullanılır.

**2. `print:` yazdığın şeyi aynen yazar.**

```ton
print: Merhaba %ad%, hoş geldin!
```

**3. Hesap yapmak için `%( ... )%`.**

```ton
print: Toplam: %(3 * 14)%
print: Büyük harf: %(upper(%ad%))%
```

---

## Hızlı tur

```ton
# Değişkenler
ad = "Nyl"
yas = 20
liste = [1, 2, 3]
kisi = {ad: "Nyl", yas: 20}

print: %kisi.ad% - %liste[0]%

# Koşul
if %yas% >= 18
  print: yetişkin
elif %yas% >= 13
  print: genç
else
  print: çocuk
end

# Döngü
repeat 3 as i
  print: %i%. tekrar
end

for oge in %liste%
  print: %oge%
end

while %yas% < 21
  yas += 1
end

# İş (fonksiyon)
func selamla(kisi, selam = "Merhaba")
  return %selam% + ", " + %kisi% + "!"
end

print: %(selamla("TON"))%

# Hata yakalama
try
  hata("bir şeyler ters gitti")
catch mesaj
  print: %mesaj%
end
```

---

## En karmaşık şeyler, en basit hâlleriyle

### Bağlantı — `connect()`

İnternet de veritabanı da aynı kelimeyle:

```ton
api = connect(https://api.lanux.online)
sonuc = %api%.get("/kullanicilar")
print: %sonuc%

db = connect("kayitlar.db")
%db%.run("insert into kisiler values (?, ?)", ["Nyl", 20])
print: %(%db%.all("select * from kisiler"))%
```

Tek seferlik: `get(adres)` · `post(adres, %veri%)` · `download(adres, "dosya.zip")`

### Eş zamanlı (asenkron) — `asyn()`

```ton
gorev = asyn(https://api.lanux.online)   # arka planda getir
baska = asyn(uzun_is, 5)                 # arka planda çalıştır

print: %(wait(%gorev%))%                 # bitmesini bekle
print: %(parallel([is1, is2, is3]))%     # hepsini aynı anda çalıştır
wait(2)                                  # 2 saniye bekle
```

### Büyük veri — `data()`

Dosya satır satır okunur; 10 GB'lık dosya da belleğe sığmadan işlenir.

```ton
v = data("satislar.csv")

print: %(%v%.count())%
print: %(%v%.sum("tutar"))%
print: %(%v%.group("urun"))%
print: %(%v%.top(5, "tutar"))%

%v%.filter(func(s) -> %s.tutar% > 1000).save("buyukler.json")
```

`.csv` `.tsv` `.json` `.jsonl` `.txt` desteklenir.

### Yapay zekâ — `ai()`

```ton
ai_setup(key: "...")          # ya da TON_AI_KEY ortam değişkeni

print: %(ai("Bana bir fıkra anlat"))%

veri = ai_json("3 şehir ismini {sehirler: [...]} biçiminde ver")
print: %veri.sehirler%
```

### Üstprogramlama — `meta()`

Kod, kendi kodunu yazar:

```ton
meta('gizli = 7')
print: %gizli%

define("iki_kat", ["x"], 'return %x% * 2')
print: %(iki_kat(21))%

print: %(template('Sayın %isim%', {isim: "Nyl"}))%
```

> Not: `"..."` içindeki `%ad%` hemen değerini alır. Kodun ham kalması için
> `'...'` (tek tırnak) kullan. Çok satırlı metin için `'''...'''`.

---

## tonweb — web kütüphanesi

```ton
use web

func anasayfa(istek)
  return web.html(baslik: "TON", govde: "<h1>Merhaba TON</h1>")
end

func kullanici(istek)
  return {ad: %istek.parametreler.ad%}     # harita döndürünce JSON olur
end

web.page("/", anasayfa)
web.page("/kullanici/:ad", kullanici)
web.serve(8080)
```

```
TON web sunucusu hazır -> http://localhost:8080
```

Ayrıntılar: [docs/tonweb.md](docs/tonweb.md)

---

## Komutlar

```bash
ton main.ton          # dosyayı çalıştır
ton                   # etkileşimli kabuk (REPL)
ton -e "print: selam" # tek satır çalıştır
ton kontrol main.ton  # sadece yazım denetimi
ton yeni projem       # yeni proje oluştur
ton isler             # bütün hazır işleri listele
ton -s                # sürüm
```

---

## Proje yapısı

```
ton               # çalıştırıcı  ->  ton main.ton
tonlang/          # ÇEKIRDEK (tnl core) - hiç ek gereksinim yok
  lexer.py          sözcük çözümleyici
  parser.py         sözdizimi çözümleyici
  interpreter.py    yorumlayıcı
  lib/              hazır işler (metin, liste, dosya, ağ, veri, zekâ, meta...)
tonweb/           # web kütüphanesi (use web)
examples/         # örnekler
docs/             # dil kılavuzu
tests/            # test takımı
```

---

## Belgeler

- [docs/dil.md](docs/dil.md) — tam dil kılavuzu
- [docs/isler.md](docs/isler.md) — bütün hazır işler
- [docs/tonweb.md](docs/tonweb.md) — web kütüphanesi

## Testler

```bash
python3 tests/run_tests.py
```

## Lisans

MIT
