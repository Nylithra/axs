# jubb — Jubbio bot kütüphanesi

```ton
use jubb

jubb.giris("BOT_TOKEN")
jubb.yolla(%sunucu%, %kanal%, "Merhaba!")
```

Bu kütüphane **TON ile yazılmıştır** — `kutuphaneler/jubb.ton` dosyasını açıp
okuyabilir, değiştirebilirsin. Çekirdeğin `request()` işinden başka bir şey
kullanmaz.

> **Durum:** REST tarafı (mesaj, üye, rol, kanal, komut, etkileşim) hazır.
> Gerçek zamanlı olay dinleme (gateway) WebSocket ister; çekirdeğe WebSocket
> eklenince gelecek.

---

## Kurulum

```ton
jubb.giris("BOT_TOKEN")                  # sadece token
jubb.giris("BOT_TOKEN", "UYGULAMA_ID")   # slash komutları için uygulama kimliği

jubb.ayarla(kayit: true)                 # her isteği ekrana yaz
jubb.ayarla(temel: "http://localhost:8080/api/v1")   # başka sunucu
```

## Mesajlar

```ton
jubb.yolla(%sunucu%, %kanal%, "Merhaba!")

jubb.yolla(%sunucu%, %kanal%, {
  baslik: "Başlık",
  aciklama: "Açıklama",
  renk: "#2f6fed",
  resim: "https://...",
  alt_yazi: "footer"
})

jubb.gizli_yolla(%sunucu%, %kanal%, %kullanici%, "sadece sen görüyorsun")
jubb.dm(%kanal%, "özel mesaj")

jubb.duzenle(%sunucu%, %kanal%, %mesaj%, "yeni içerik")
jubb.mesaj_sil(%sunucu%, %kanal%, %mesaj%)
jubb.toplu_sil(%sunucu%, %kanal%, [%m1%, %m2%])

mesajlar = jubb.mesajlar(%sunucu%, %kanal%, 20)

jubb.tepki_ekle(%sunucu%, %kanal%, %mesaj%, "👍")
jubb.tepki_sil(%sunucu%, %kanal%, %mesaj%, "👍")
jubb.sabitle(%sunucu%, %kanal%, %mesaj%)
```

Metin verirsen düz mesaj, harita verirsen gömülü (embed) kutu olur. API'nin
kendi alan adlarını (`content`, `embeds`) yazarsan olduğu gibi geçer.

## Üyeler

```ton
jubb.uye(%sunucu%, %kullanici%)
jubb.uyeler(%sunucu%, 100)

jubb.at(%sunucu%, %kullanici%, "sebep")              # kick
jubb.yasakla(%sunucu%, %kullanici%, "sebep", 1)      # ban (1 günlük mesaj siler)
jubb.yasak_kaldir(%sunucu%, %kullanici%)
jubb.sustur(%sunucu%, %kullanici%, 600, "sakin ol")  # 600 saniye
jubb.susturma_kaldir(%sunucu%, %kullanici%)

jubb.rol_ver(%sunucu%, %kullanici%, %rol%)
jubb.rol_al(%sunucu%, %kullanici%, %rol%)
jubb.uye_duzenle(%sunucu%, %kullanici%, {nick: "yeni ad"})
```

## Sunucu, kanal, rol

```ton
jubb.sunucu(%kimlik%)
jubb.kanallar(%sunucu%)
jubb.kanal_ac(%sunucu%, {name: "genel"})
jubb.kanal_sil(%sunucu%, %kanal%)
jubb.roller(%sunucu%)
jubb.rol_ac(%sunucu%, {name: "üye"})
jubb.rol_sil(%sunucu%, %rol%)
```

## Slash komutları

Uygulama kimliği gerekir: `jubb.giris(token, uygulama_id)`

```ton
jubb.komut_ekle({name: "selam", description: "Selam verir"})        # global
jubb.komut_ekle({name: "selam", description: "..."}, %sunucu%)      # sunucuya özel
jubb.komutlari_ayarla([{name: "a"}, {name: "b"}], %sunucu%)         # hepsini değiştir
jubb.komutlar(%sunucu%)
jubb.komut_sil(%komut%, %sunucu%)
```

## Etkileşime cevap

```ton
jubb.cevapla(%etkilesim%, "Merhaba!")
jubb.cevapla(%etkilesim%, "sadece sen görürsün", gizli: true)

jubb.dusun(%etkilesim%)                      # "düşünüyor..." göster
jubb.cevap_duzenle(%etkilesim%, "sonuç")     # sonra cevabı yaz
jubb.ek_cevap(%etkilesim%, "bir de bu")
```

## Yardımcılar

```ton
jubb.bahset(%kullanici%)      # <@123>
jubb.gomulu({baslik: "...", renk: "#ff0000"})   # embed haritası üretir
jubb.ayar()                   # şu anki ayarlar
```

## Hatalar

API hata dönerse TON hatası fırlar; `try/catch` ile yakalarsın:

```ton
try
  jubb.yolla(%sunucu%, %kanal%, "deneme")
catch mesaj
  print: gönderilemedi: %mesaj%
end
```

```
Jubbio hatası (401) POST /bot/guilds/7/channels/9/messages: {error: "bad token"}
```

## Neden `npm install @jubbio/core` çevrilmedi?

`ton jston` bir **sözdizimi** çeviricisi. `@jubbio/core` paketinin özü ise
TON'da olmayan çalışma zamanı şeyleri: izinler bit alanı (`1n << 0n`), gateway
bir WebSocket, API'nin şekli `class ... extends EventEmitter`, ve 72 tane
`require()`. Ölçtük: 41 dosyanın 17'si çözümlenemiyor, kalanında 378 uyarı
çıkıyor.

Bu yüzden paketi çevirmek yerine, altındaki HTTP API'yi TON'a doğrudan yazdık —
sonuç hem çalışıyor hem okunuyor.
