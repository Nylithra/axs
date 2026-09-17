# TON Tarayıcıda

Aynı TON kodu tarayıcıda da çalışır. `ton` komutu TON'u JavaScript'e çevirir,
`ton.js` de dilin hazır işlerini tarayıcıda sağlar. Ek hiçbir araç gerekmez —
npm yok, derleme kurulumu yok.

```ton
sayi = saklanan("sayi", 0)

func arttir(olay)
  sayi += 1
  yaz_metin("#sayi", %sayi%)
  sakla("sayi", %sayi%)
end

tikla("#arttir", arttir)
```

---

## Üç çalıştırma yolu

### 1. Tek dosya — `ton paket`

```bash
ton paket sayac.ton
```

`sayac.html` çıkar: içinde çalışma zamanı da derlenmiş kod da gömülüdür.
Çift tıkla, açılır. Sunucu bile gerekmez.

Yanında `<ad>.govde.html` varsa, onun içeriği sayfanın gövdesi olur:

```
sayac.ton            <- kod
sayac.govde.html     <- sayfanın HTML gövdesi (isteğe bağlı)
sayac.html           <- `ton paket` çıktısı
```

### 2. Sunucuyla — `web.uygulama`

```ton
use web

func liste(istek)
  return ["bir", "iki"]
end

web.api("/api/liste", liste)
web.uygulama("/", "tarayici/uygulamam.ton")

web.serve(8080)
```

Her istekte yeniden derlenir: dosyayı kaydet, sayfayı yenile, yeter.

### 3. Sadece JavaScript — `ton derle`

```bash
ton derle uygulamam.ton -o uygulamam.js
```

Kendi HTML'ine koyacaksan:

```html
<script src="ton.js"></script>
<script src="uygulamam.js"></script>
```

`ton.js` dosyası `tonweb/tarayici/ton.js` içindedir.

---

## Tek fark: her şey beklenebilir

Tarayıcıda ağ işleri normalde geri çağrı (callback) ister. TON'da istemez:

```ton
notlar = get("/api/notlar")        # düz görünür, arka planda fetch olur
sonuc = post("/api/ekle", {metin: "selam"})
wait(2)                            # 2 saniye bekler
```

Derleyici her işi `async`, her çağrıyı `await` yapar; sen bunu hiç görmezsin.
Yani çekirdekte yazdığın kod tarayıcıda da aynı sırayla akar.

---

## Sayfa işleri

### Seçme

```ton
kutu = oge("#kutu")            # tek öge (yoksa null)
satirlar = ogeler(".satir")    # hepsi, liste olarak
```

> `bul()` metin/liste araması yapar (çekirdekteki gibi); sayfadan öge
> seçmek için `oge()` kullanılır.

### Yazma ve okuma

| İş | Ne yapar |
|---|---|
| `yaz_ic(secici, html)` | İçeriği HTML olarak yazar |
| `yaz_metin(secici, metin)` | İçeriği düz metin olarak yazar |
| `oku_ic(secici)` / `oku_metin(secici)` | İçeriği okur |
| `deger(secici)` / `deger(secici, yeni)` | Form alanını okur / yazar |
| `ozellik(secici, ad, deger)` | HTML özelliği |
| `stil(secici, ozellik, deger)` | CSS |
| `ekle_oge(secici, icerik)` | Sona ekler |
| `sil_oge(secici)` · `temizle_ic(secici)` | Siler / boşaltır |
| `olustur(etiket, icerik, ozellikler)` | Yeni öge yapar |
| `ekle_sinif` · `sil_sinif` · `degistir_sinif` | Sınıflar |
| `gorunur(secici, true/false)` · `odak(secici)` | Görünürlük / odak |

### Olaylar

```ton
func tiklandi(olay)
  print: tiklandi: %olay.hedef%
end

tikla("#dugme", tiklandi)
gonderim("#form", gonder)      # form gönderimi (sayfa yenilenmez)
tus("#arama", yazilinca)       # klavye
olay("#kutu", "mouseover", is) # herhangi bir olay
sayfa_hazir(basla)             # sayfa yüklenince
```

Olay işine gelen harita: `%olay.tur%`, `%olay.deger%`, `%olay.tus%`,
`%olay.hedef%` ve ögedeki `data-...` değerleri.

### Saklama ve sayfa

```ton
sakla("ad", %deger%)              # localStorage
deger = saklanan("ad", varsayilan)
sakli_sil("ad")

git("/baska-sayfa")
sayfa_basligi("Yeni başlık")
uyari("dikkat")  ·  onay("emin misin?")  ·  sor("adın ne?")
form_verisi("#form")              # bütün alanları harita olarak verir
```

### `print:` nereye yazar?

Konsola yazar; sayfada `id="ton-cikti"` olan bir öge varsa oraya da ekler.
`ton paket` ile üretilen sayfada bu öge hazır gelir (boşken görünmez).

---

## Çekirdekte olup tarayıcıda olmayanlar

| Yok | Neden / yerine |
|---|---|
| `read` `save` `delete` `files` ... | Tarayıcı dosya sistemine giremez → `get`/`post` |
| `connect()` | Veritabanı bağlantısı sunucuda kalır → sunucuda uç aç |
| `meta` `define` `get_var` `set_var` | Derlenmiş kodda dinamik ortam yok |

Bunları tarayıcı kodunda kullanırsan **derlerken** anlaşılır bir hata alırsın,
çalışırken sürpriz olmaz.

`ai()` tarayıcıda çalışır ama isteği kendi sunucuna gönderir — anahtarın
tarayıcıya inmesin diye:

```ton
# sunucu tarafı
ai_setup(saglayici: "groq", key: "gsk_...")
web.ai_ucu("/api/ai")      # anahtar sunucuda kalır
```

```ton
# tarayıcı tarafı
ai = "groq"                # sağlayıcı seçimi sunucuya iletilir
cevap = ai("merhaba")
```

## İki küçük davranış farkı

1. **Olmayan değişken**: çekirdekte çalışırken hata verir, tarayıcıda
   **derlenirken** hata verir. Yani yazım hataları daha erken yakalanır.
2. **Sayı gibi görünen harita anahtarları**: JavaScript bunları küçükten
   büyüğe sıralar. `group(%liste%, "yas")` sonucunun sırası tarayıcıda
   farklı olabilir. Sıra önemliyse anahtarı metne çevir.

---

## Örnekler

```bash
ton paket examples/tarayici/sayac.ton      # tek dosyalık sayaç
ton examples/tarayici_sunucu.ton           # sunucu + tarayıcı birlikte
```
