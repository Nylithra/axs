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

Gereken tek şey **Python 3.8+**. Başka hiçbir paket yok.

### Windows

```bat
cd C:\Users\adin\Downloads\ton
install.cmd
```

`install.cmd` dosyasına çift tıklamak da olur. Sonra **yeni bir komut istemi aç**
(eski pencere eski PATH'i kullanır) ve dene:

```bat
ton -s
ton main.ton
```

Kurmadan denemek istersen, klasörün içindeyken:

```bat
ton.cmd main.ton
```

Python yoksa: `winget install Python.Python.3.12` — ya da
[python.org/downloads](https://www.python.org/downloads/) (kurulumda
**"Add python.exe to PATH"** kutusunu işaretle).

### Linux / macOS

```bash
git clone https://github.com/nylithra/ton-language
cd ton-language
./ton main.ton

./install.sh          # ~/.local/bin/ton bağlantısı kurar
ton main.ton
```

> `install.sh` bir kabuk betiğidir, Windows'ta çalışmaz — orada `install.cmd` kullan.

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

Beş sağlayıcı, tek satırla seçilir:

```ton
ai = "groq"        # claude · chatgpt · gemini · grok · groq

print: %(ai("Bana bir fıkra anlat"))%

veri = ai_json("3 şehir ismini {sehirler: [...]} biçiminde ver")
print: %veri.sehirler%
```

Anahtar ortam değişkeninden gelir (`GROQ_API_KEY`, `OPENAI_API_KEY`, ...) ya da
`ai_setup(key: "...")` ile verilir. Her sağlayıcının anahtarı ayrı tutulur,
aralarında geçiş yapmak tek satır.

```ton
print: %(ai_saglayicilar())%     # beşinin durumu
print: %(ai_modeller())%         # sağlayıcının canlı model listesi
ai("soru", saglayici: "grok")    # sadece bu çağrı için
```

Ayrıntılar: [docs/zeka.md](docs/zeka.md)

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

## Tarayıcıda TON

Aynı dil tarayıcıda da çalışır. `ton` komutu TON'u JavaScript'e çevirir.

```ton
sayi = saklanan("sayi", 0)

func arttir(olay)
  sayi += 1
  yaz_metin("#sayi", %sayi%)
  sakla("sayi", %sayi%)
end

tikla("#arttir", arttir)
```

```bash
ton paket sayac.ton      # sayac.html — çift tıkla, açılır. Sunucu bile gerekmez.
```

Ağ işleri tarayıcıda da düz görünür; geri çağrı (callback) yok:

```ton
notlar = get("/api/notlar")             # arka planda fetch olur
sonuc = post("/api/ekle", {metin: %m%})
```

Sunucuyla birlikte çalıştırmak için:

```ton
web.uygulama("/", "uygulamam.ton")      # sayfa + derlenmiş kod, her istekte tazelenir
```

Ayrıntılar: [docs/tarayici.md](docs/tarayici.md)

---

## Komutlar

```bash
ton main.ton          # dosyayı çalıştır
ton                   # etkileşimli kabuk (REPL)
ton -e "print: selam" # tek satır çalıştır
ton kontrol main.ton  # sadece yazım denetimi
ton derle app.ton     # tarayıcı için JavaScript üret
ton paket app.ton     # tek dosyalık çalışır HTML üret
ton jston hesap.js    # JavaScript kodunu TON'a çevir
ton yeni projem       # yeni proje oluştur
ton isler             # bütün hazır işleri listele
ton -s                # sürüm
```

---

## Proje yapısı

```
ton               # çalıştırıcı (Linux/macOS)  ->  ton main.ton
ton.cmd           # çalıştırıcı (Windows)     ->  ton main.ton
install.sh        # kurulum (Linux/macOS)
install.cmd       # kurulum (Windows)
tonlang/          # ÇEKIRDEK (tnl core) - hiç ek gereksinim yok
  jston/            JavaScript -> TON çevirici
  lexer.py          sözcük çözümleyici
  parser.py         sözdizimi çözümleyici
  interpreter.py    yorumlayıcı
  lib/              hazır işler (metin, liste, dosya, ağ, veri, zekâ, meta...)
tonweb/           # web kütüphanesi (use web)
  sunucu.py         yollar, istekler, cevaplar
  html.py           HTML üretimi
  tarayici/ton.js   TARAYICI çalışma zamanı (hazır işler + DOM)
  paket.py          tek dosyalık HTML paketleme
kutuphaneler/     # TON ile yazılmış kütüphaneler (use jubb)
examples/         # örnekler
docs/             # dil kılavuzu
tests/            # test takımı
```

---

## Belgeler

- [docs/dil.md](docs/dil.md) — tam dil kılavuzu
- [docs/isler.md](docs/isler.md) — bütün hazır işler
- [docs/tonweb.md](docs/tonweb.md) — web kütüphanesi
- [docs/tarayici.md](docs/tarayici.md) — tarayıcıda TON
- [docs/zeka.md](docs/zeka.md) — yapay zekâ sağlayıcıları
- [docs/jston.md](docs/jston.md) — JavaScript'ten TON'a çevirme
- [docs/jubb.md](docs/jubb.md) — Jubbio bot kütüphanesi

## Hazır kütüphaneler

`kutuphaneler/` içindeki TON dosyaları `use <ad>` ile doğrudan yüklenir:

```ton
use jubb

jubb.giris("BOT_TOKEN")
jubb.yolla(%sunucu%, %kanal%, "Merhaba!")
```

`jubb` — [Jubbio](https://jubbio.com) bot kütüphanesi (mesaj, üye, rol, kanal,
komut, etkileşim). TON ile yazılmıştır, açıp okuyabilirsin:
[docs/jubb.md](docs/jubb.md)

Kendi kütüphaneni `kutuphaneler/` klasörüne ya da `TON_YOL` ile gösterdiğin bir
klasöre koyarsan `use <ad>` onu da bulur.

## JavaScript'ten TON'a

Elindeki JS kodunu TON'a çevirir:

```bash
ton jston hesap.js       # -> hesap.ton
```

```js
function topla(a, b = 2) { return a + b; }
const kare = (x) => x * x;
console.log(`sonuç: ${topla(3)}`);
```

```ton
func topla(a, b = 2)
  return (%a% + %b%)
end
func kare(x)
  return (%x% * %x%)
end
print("sonuç: %(topla(3))%")
```

Çevrilemeyen yerler çıktıda `# TODO:` olarak işaretlenir ve dosyanın başında
listelenir — sessizce yanlış kod üretilmez. Doğruluk ölçülür: test takımındaki
her JS programı hem `node` hem `ton` ile çalıştırılıp çıktıları karşılaştırılır.

Ayrıntılar: [docs/jston.md](docs/jston.md)

## Windows notları

- **Dosyalarını UTF-8 kaydet.** TON, Not Defteri'nin eklediği görünmez BOM
  işaretini ve CRLF satır sonlarını kendi temizler; ANSI (cp1254) kaydedilmiş
  dosyaları da okur. Yine de en temizi UTF-8'dir.
- **Türkçe karakterler** konsolda düzgün görünür; `ton.cmd` çıktıyı UTF-8'e ayarlar.
- **`web.serve(8080)`** ilk çalıştığında Windows Güvenlik Duvarı izin sorabilir.
  Sadece kendi bilgisayarında denemek için `web.serve(8080, adres: "127.0.0.1")` yaz.
- **PowerShell'de de** `ton main.ton` çalışır, ayrıca bir şey gerekmez.

## Testler

```bash
python3 tests/run_tests.py
```

## Lisans

MIT
