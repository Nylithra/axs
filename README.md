# Axs Language

**Aşırı basit** bir programlama dili. Çekirdeği hiçbir ek gereksinim
istemez — Python 3.8+ dışında kurulum yoktur, indir ve çalıştır.

```axs
a = "merhaba"

print: a;
```

```
merhaba
```

---

## Kurulum

Gereken tek şey **Python 3.8+**. Başka hiçbir paket yok.

### Windows — tek dosya (önerilen)

[**axs-kur.bat**](axs-kur.bat) dosyasını indir, çift tıkla. Kaynak kodun
tamamını indirmene gerek yok; kurucu yalnızca çalışma zamanını
(`%LOCALAPPDATA%\Axs`, ~350 KB) kurar ve PATH'e ekler.

Sonra **yeni bir komut istemi aç** (eski pencere eski PATH'i kullanır):

```bat
axs -s
axs -e "print: merhaba"
axs install jubbio
```

Python yoksa kurucu sana söyler: `winget install Python.Python.3.12` — ya da
[python.org/downloads](https://www.python.org/downloads/) (kurulumda
**"Add python.exe to PATH"** kutusunu işaretle).

### Windows — depoyu klonladıysan

```bat
cd C:\Users\adin\Downloads\axs
axs-yerel-kur.cmd
```

Kurmadan denemek istersen, klasörün içindeyken:

```bat
axs.cmd main.axs
```

### Linux / macOS

```bash
git clone https://github.com/nylithra/ton-language
cd ton-language
./axs main.axs

./install.sh          # ~/.local/bin/axs bağlantısı kurar
axs main.axs
```

> `install.sh` bir kabuk betiğidir, Windows'ta çalışmaz — orada `axs-kur.bat`
> ya da `axs-yerel-kur.cmd` kullan.

---

## Dosya uzantıları

`.axs` &nbsp;·&nbsp; `.nyl` — ikisi de aynı şekilde çalışır.

```bash
axs main.axs
axs main.nyl
axs main          # uzantıyı yazmasan da bulur
```

---

## Üç altın kural

**1. Değişkeni düz adıyla yaz, düz adıyla oku.**

```axs
ad = "Nyl"            # yazarken
print(ad)             # kodun içinde okurken
```

Tür belirtmezsin; metin de olsa sayı da olsa aynı şekilde kullanılır.

**2. `print:` yazdığın şeyi aynen yazar; yazının içindeki değişkeni `ad;`
ile okursun.**

```axs
print: Merhaba ad;, hoş geldin!
```

```
Merhaba Nyl, hoş geldin!
```

Noktalı virgül değişkenin nerede bittiğini söyler — bu yüzden `ad;,` yazıp
hemen ardından virgül koyabilirsin. Nokta ve köşeli parantez de çalışır:
`kisi.ad;` · `liste[0];`

**3. Yazının içinde hesap yapmak için `(ifade);`.**

```axs
print: Toplam: (3 * 14);
print: Büyük harf: (upper(ad));
```

```
Toplam: 42
Büyük harf: NYL
```

> Eski `%ad%` yazımı hâlâ çalışır. Adres ya da yol gibi `ad;` yazımının
> okunamadığı yerlerde (`/%kanal%/mesaj`) veya adı anahtar kelimeyle çakışan
> değişkenlerde (`%son%`) onu kullan.

---

## Hızlı tur

```axs
# Değişkenler
ad = "Nyl"
yas = 20
liste = [1, 2, 3]
kisi = {ad: "Nyl", yas: 20}

print: kisi.ad; - liste[0];

# Koşul
if yas >= 18
  print: yetişkin
elif yas >= 13
  print: genç
else
  print: çocuk
end

# Döngü
repeat 3 as i
  print: i;. tekrar
end

for oge in liste
  print: oge;
end

while yas < 21
  yas += 1
end

# İş (fonksiyon)
func selamla(kisi, selam = "Merhaba")
  return selam + ", " + kisi + "!"
end

print: (selamla("Axs"));

# Hata yakalama
try
  hata("bir şeyler ters gitti")
catch mesaj
  print: mesaj;
end
```

---

## En karmaşık şeyler, en basit hâlleriyle

### Bağlantı — `connect()`

İnternet, WebSocket ve veritabanı — hepsi aynı kelimeyle:

```axs
api = connect(https://api.lanux.online)
sonuc = api.get("/kullanicilar")
print: sonuc;

db = connect("kayitlar.db")
db.run("insert into kisiler values (?, ?)", ["Nyl", 20])
print: (db.all("select * from kisiler"));

soket = connect(wss://ornek.com/ws)     # WebSocket
soket.yolla({selam: "dunya"})
print: (soket.al(5));
```

Tek seferlik: `get(adres)` · `post(adres, veri)` · `download(adres, "dosya.zip")`

### Eş zamanlı (asenkron) — `asyn()`

```axs
gorev = asyn(https://api.lanux.online)   # arka planda getir
baska = asyn(uzun_is, 5)                 # arka planda çalıştır

print: (wait(gorev));                 # bitmesini bekle
print: (parallel([is1, is2, is3]));     # hepsini aynı anda çalıştır
wait(2)                                  # 2 saniye bekle
```

### Büyük veri — `data()`

Dosya satır satır okunur; 10 GB'lık dosya da belleğe sığmadan işlenir.

```axs
v = data("satislar.csv")

print: (v.count());
print: (v.sum("tutar"));
print: (v.group("urun"));
print: (v.top(5, "tutar"));

v.filter(func(s) -> s.tutar > 1000).save("buyukler.json")
```

`.csv` `.tsv` `.json` `.jsonl` `.txt` desteklenir.

### Yapay zekâ — `ai()`

Beş sağlayıcı, tek satırla seçilir:

```axs
ai = "groq"        # claude · chatgpt · gemini · grok · groq

print: (ai("Bana bir fıkra anlat"));

veri = ai_json("3 şehir ismini {sehirler: [...]} biçiminde ver")
print: veri.sehirler;
```

Anahtar ortam değişkeninden gelir (`GROQ_API_KEY`, `OPENAI_API_KEY`, ...) ya da
`ai_setup(key: "...")` ile verilir. Her sağlayıcının anahtarı ayrı tutulur,
aralarında geçiş yapmak tek satır.

```axs
print: (ai_saglayicilar());     # beşinin durumu
print: (ai_modeller());         # sağlayıcının canlı model listesi
ai("soru", saglayici: "grok")    # sadece bu çağrı için
```

Ayrıntılar: [docs/zeka.md](docs/zeka.md)

### Üstprogramlama — `meta()`

Kod, kendi kodunu yazar:

```axs
meta('gizli = 7')
print: gizli;

define("iki_kat", ["x"], 'return x * 2')
print: (iki_kat(21));

print: (template('Sayın isim', {isim: "Nyl"}));
```

> Not: `"..."` içindeki `ad;` hemen değerini alır. Kodun ham kalması için
> `'...'` (tek tırnak) kullan. Çok satırlı metin için `'''...'''`.

---

## axsweb — web kütüphanesi

```axs
use web

func anasayfa(istek)
  return web.html(baslik: "Axs", govde: "<h1>Merhaba Axs</h1>")
end

func kullanici(istek)
  return {ad: istek.parametreler.ad}     # harita döndürünce JSON olur
end

web.page("/", anasayfa)
web.page("/kullanici/:ad", kullanici)
web.serve(8080)
```

```
Axs web sunucusu hazır -> http://localhost:8080
```

Ayrıntılar: [docs/axsweb.md](docs/axsweb.md)

---

## Tarayıcıda Axs

Aynı dil tarayıcıda da çalışır. `axs` komutu Axs'u JavaScript'e çevirir.

```axs
sayi = saklanan("sayi", 0)

func arttir(olay)
  sayi += 1
  yaz_metin("#sayi", sayi)
  sakla("sayi", sayi)
end

tikla("#arttir", arttir)
```

```bash
axs paket sayac.axs      # sayac.html — çift tıkla, açılır. Sunucu bile gerekmez.
```

Ağ işleri tarayıcıda da düz görünür; geri çağrı (callback) yok:

```axs
notlar = get("/api/notlar")             # arka planda fetch olur
sonuc = post("/api/ekle", {metin: m})
```

Sunucuyla birlikte çalıştırmak için:

```axs
web.uygulama("/", "uygulamam.axs")      # sayfa + derlenmiş kod, her istekte tazelenir
```

Ayrıntılar: [docs/tarayici.md](docs/tarayici.md)

---

## Komutlar

```bash
axs main.axs          # dosyayı çalıştır
axs                   # etkileşimli kabuk (REPL)
axs -e "print: selam" # tek satır çalıştır
axs kontrol main.axs  # sadece yazım denetimi
axs derle app.axs     # tarayıcı için JavaScript üret
axs paket app.axs     # tek dosyalık çalışır HTML üret
axs cevir hesap.js    # JavaScript kodunu Axs'a çevir
axs yeni projem       # yeni proje oluştur
axs isler             # bütün hazır işleri listele
axs -s                # sürüm
```

---

## Proje yapısı

```
axs               # çalıştırıcı (Linux/macOS)  ->  axs main.axs
axs.cmd           # çalıştırıcı (Windows)     ->  axs main.axs
axs-kur.bat       # tek dosyalik Windows kurucusu
axs-yerel-kur.cmd # depoyu klonlayanlar icin Windows kurulumu
install.sh        # kurulum (Linux/macOS)
axslang/          # ÇEKIRDEK - hiç ek gereksinim yok
  jston/            JavaScript -> Axs çevirici
  lexer.py          sözcük çözümleyici
  parser.py         sözdizimi çözümleyici
  interpreter.py    yorumlayıcı
  lib/              hazır işler (metin, liste, dosya, ağ, veri, zekâ, meta...)
axsweb/           # web kütüphanesi (use web)
  sunucu.py         yollar, istekler, cevaplar
  html.py           HTML üretimi
  tarayici/axs.js   TARAYICI çalışma zamanı (hazır işler + DOM)
  paket.py          tek dosyalık HTML paketleme
kutuphaneler/     # Axs ile yazılmış kütüphaneler (use jubb)
examples/         # örnekler
docs/             # dil kılavuzu
tests/            # test takımı
```

---

## Belgeler

- [docs/dil.md](docs/dil.md) — tam dil kılavuzu
- [docs/isler.md](docs/isler.md) — bütün hazır işler
- [docs/axsweb.md](docs/axsweb.md) — web kütüphanesi
- [docs/tarayici.md](docs/tarayici.md) — tarayıcıda Axs
- [docs/zeka.md](docs/zeka.md) — yapay zekâ sağlayıcıları
- [docs/jston.md](docs/jston.md) — JavaScript'ten Axs'a çevirme
- [docs/jubbio.md](docs/jubbio.md) — Jubbio bot kütüphanesi

## Hazır kütüphaneler

`kutuphaneler/` içindeki Axs dosyaları `use <ad>` ile doğrudan yüklenir:

```axs
use jubbio

jubbio.giris("BOT_TOKEN")
jubbio.yolla(sunucu, kanal, "Merhaba!")
```

`jubb` — [Jubbio](https://jubbio.com) bot kütüphanesi: REST (mesaj, üye, rol,
kanal, komut) **ve** gerçek zamanlı gateway. Axs ile yazılmıştır, açıp
okuyabilirsin: [docs/jubbio.md](docs/jubbio.md)

```axs
func mesaj_geldi(m)
  if m.content == "!selam"
    jubbio.yolla(m.guild_id, m.channel_id, "Selam!")
  end
end

jubbio.dinle("mesaj", mesaj_geldi)
jubbio.calistir(["sunucular", "mesajlar", "icerik"])
```

Çalışır bot örneği: [examples/bot/](examples/bot/)

Kendi kütüphaneni `kutuphaneler/` klasörüne ya da `AXS_YOL` ile gösterdiğin bir
klasöre koyarsan `use <ad>` onu da bulur.

## JavaScript'ten Axs'a

Elindeki JS kodunu Axs'a çevirir:

```bash
axs cevir hesap.js       # -> hesap.axs
```

```js
function topla(a, b = 2) { return a + b; }
const kare = (x) => x * x;
console.log(`sonuç: ${topla(3)}`);
```

```axs
func topla(a, b = 2)
  return (a + b)
end
func kare(x)
  return (x * x)
end
print("sonuç: (topla(3));")
```

Çevrilemeyen yerler çıktıda `# TODO:` olarak işaretlenir ve dosyanın başında
listelenir — sessizce yanlış kod üretilmez. Doğruluk ölçülür: test takımındaki
her JS programı hem `node` hem `axs` ile çalıştırılıp çıktıları karşılaştırılır.

Ayrıntılar: [docs/jston.md](docs/jston.md)

## Windows notları

- **Dosyalarını UTF-8 kaydet.** Axs, Not Defteri'nin eklediği görünmez BOM
  işaretini ve CRLF satır sonlarını kendi temizler; ANSI (cp1254) kaydedilmiş
  dosyaları da okur. Yine de en temizi UTF-8'dir.
- **Türkçe karakterler** konsolda düzgün görünür; `axs.cmd` çıktıyı UTF-8'e ayarlar.
- **`web.serve(8080)`** ilk çalıştığında Windows Güvenlik Duvarı izin sorabilir.
  Sadece kendi bilgisayarında denemek için `web.serve(8080, adres: "127.0.0.1")` yaz.
- **PowerShell'de de** `axs main.axs` çalışır, ayrıca bir şey gerekmez.

## Testler

```bash
python3 tests/run_tests.py
```

## Lisans

MIT
