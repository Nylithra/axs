# axsweb — Axs Web Kütüphanesi

```axs
use web
```

Çekirdek gibi bu da hiçbir ek pakete ihtiyaç duymaz.

---

## En küçük site

```axs
use web

func anasayfa(istek)
  return "<h1>Merhaba Axs</h1>"
end

web.page("/", anasayfa)
web.serve(8080)
```

```bash
axs site.axs
# Axs web sunucusu hazır -> http://localhost:8080
```

---

## Yollar

```axs
web.page("/hakkinda", hakkinda)          # GET
web.post("/kaydet", kaydet)              # POST
web.api("/api/veri", veri)               # her yöntem
web.route("/sil", sil, yontem: "DELETE")
web.static("dosyalar", "/statik")        # klasörü yayınla
web.routes()                             # tanımlı yolları verir
```

Yol içinde değişken — `:ad`, sonunda `*` ile geri kalanı yakalar:

```axs
func kullanici(istek)
  return "Merhaba " + istek.parametreler.ad
end

web.page("/kullanici/:ad", kullanici)
```

## İstek

Her işin aldığı `istek` bir haritadır:

| Alan | İçerik |
|---|---|
| `istek.yol` | `/kullanici/nyl` |
| `istek.yontem` | `GET`, `POST` ... |
| `istek.parametreler` | Yoldaki değişkenler → `{ad: "nyl"}` |
| `istek.sorgu` | `?a=1` → `{a: "1"}` |
| `istek.veri` | JSON ya da form gövdesi (harita) |
| `istek.govde` | Ham gövde metni |
| `istek.basliklar` | İstek başlıkları |
| `istek.cerezler` | Çerezler |
| `istek.ip` | İstemci adresi |

## Cevap

İşin döndürdüğü şey cevaptır:

| Döndürdüğün | Sonuç |
|---|---|
| metin | HTML sayfa |
| harita / liste | JSON |
| `web.json(x, durum)` | JSON, istediğin durum koduyla |
| `web.text(x)` | Düz metin |
| `web.redirect(adres)` | Yönlendirme |
| `web.file("resim.png")` | Dosya gönderir |
| `web.status(404, "yok")` | Durum kodu ile |
| `web.cookie(cevap, "ad", "deger")` | Çerez ekler |

## HTML üretme

```axs
web.html(baslik: "Sayfam", govde: "<h1>Selam</h1>", stil: "", betik: "")
web.tag("p", "merhaba", class: "kutu")     # <p class="kutu">merhaba</p>
web.table(satirlar)                      # harita listesinden tablo
web.list(["a", "b"])                       # <ul>
web.link("/yol", "Tıkla")
web.escape("<script>")                     # güvenli hâle getirir
web.render("sablon.html", degerler)      # dosyadaki ad yerlerini doldurur
```

`web.html` hazır, karanlık moda uyumlu bir CSS ile gelir. Kendi CSS'ini
vermek için `stil:` değerini yaz.

## Sunucu

```axs
web.serve(8080)                  # burada durur ve çalışır
web.start(8080)                  # arka planda başlatır
web.stop()                       # durdurur
web.serve(8080, sessiz: true)    # istek kayıtlarını yazma
web.on_error(hata_isi)           # hata sayfasını değiştir
web.on_missing(yok_isi)          # 404 sayfasını değiştir
```

---

## Veritabanlı örnek

```axs
use web

db = connect("notlar.db")
db.run("create table if not exists notlar (metin text)")

func anasayfa(istek)
  satirlar = db.all("select rowid, metin from notlar")
  return web.html(baslik: "Notlar", govde: web.table(satirlar))
end

func ekle(istek)
  db.run("insert into notlar values (?)", [istek.veri.metin])
  return web.redirect("/")
end

web.page("/", anasayfa)
web.post("/ekle", ekle)
web.serve(8080)
```
