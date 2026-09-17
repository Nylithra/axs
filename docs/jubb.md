# jubb — Jubbio bot kütüphanesi

```ton
use jubb

jubb.giris("BOT_TOKEN")
jubb.yolla(%sunucu%, %kanal%, "Merhaba!")
```

Bu kütüphane **TON ile yazılmıştır** — `kutuphaneler/jubb.ton` dosyasını açıp
okuyabilir, değiştirebilirsin. Çekirdeğin `request()` işinden başka bir şey
kullanmaz.

Hem REST (mesaj yollama, üye/rol/kanal işlemleri) hem de **gateway** (gerçek
zamanlı olay dinleme) hazır.

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

## Gerçek zamanlı: gateway

```ton
use jubb

jubb.giris(env("JUBB_TOKEN"))

func mesaj_geldi(m)
  if %m.kendim%
    return null              # kendi mesajımıza cevap vermeyelim
  end
  if %m.content% == "!selam"
    jubb.yolla(%m.guild_id%, %m.channel_id%, "Selam!")
  end
end

jubb.dinle("mesaj", mesaj_geldi)
jubb.calistir(["sunucular", "mesajlar", "icerik"])
```

`calistir()` bağlanır ve olaylar gelmeye başlar; `Ctrl-C`'ye kadar çalışır.
Bağlantı koparsa kendi kendine yeniden bağlanır (artan beklemeyle, en fazla
10 deneme).

### Olaylar

| TON adı | Gateway olayı |
|---|---|
| `hazir` | READY — bot bağlandı |
| `mesaj` | MESSAGE_CREATE |
| `mesaj_duzenlendi` · `mesaj_silindi` | MESSAGE_UPDATE / DELETE |
| `komut` · `etkilesim` | INTERACTION_CREATE (slash komutları) |
| `uye_katildi` · `uye_ayrildi` · `uye_guncellendi` | GUILD_MEMBER_* |
| `sunucu_eklendi` · `sunucu_guncellendi` · `sunucu_silindi` | GUILD_* |
| `kanal_acildi` · `kanal_guncellendi` · `kanal_silindi` | CHANNEL_* |
| `rol_acildi` · `rol_guncellendi` · `rol_silindi` | GUILD_ROLE_* |
| `yasaklandi` · `yasak_kalkti` | GUILD_BAN_* |
| `yaziyor` · `durum` · `davet` · `ses` | TYPING_START, PRESENCE_UPDATE, ... |
| `hata` · `ham` | bağlantı hatası · ham paket (hata ayıklama) |

Hepsini görmek için: `jubb.olaylar()`

Bir olaya birden çok iş bağlayabilirsin; hepsi sırayla çağrılır. Bir
dinleyicide hata çıkarsa bot durmaz, hata yazılır.

### Intent'ler

Hangi olayları almak istediğini söylersin:

```ton
jubb.calistir(["sunucular", "mesajlar", "icerik"])
jubb.calistir(33281)                 # sayı olarak da verebilirsin
```

`sunucular` `uyeler` `denetim` `emojiler` `entegrasyonlar` `webhooklar`
`davetler` `sesler` `durumlar` `mesajlar` `tepkiler` `yaziyor` `dm`
`dm_tepkileri` `dm_yaziyor` `icerik` `etkinlikler`

Hiçbir şey vermezsen varsayılan: sunucular + mesajlar + içerik.

### Bot bilgisi ve durdurma

```ton
jubb.ben()                # botun kendi kullanıcı bilgisi (READY sonrası)
jubb.benim_mi(%mesaj%)    # bu mesaj benden mi geldi?
jubb.dur()                # gateway'i kapat, calistir() geri döner
```

Her mesajda hazır gelen kolaylık: `%m.kendim%` — bot kendi mesajını görüyorsa
`true`. **Bunu kontrol etmezsen bot kendi kendine cevap verip sonsuz döngüye
girer.**

### Ayarlar

```ton
jubb.ag_ayarla(kayit: true)                        # bağlantı adımlarını yaz
jubb.ag_ayarla(adres: "ws://127.0.0.1:9000/ws")    # başka gateway
jubb.ag_ayarla(en_fazla_deneme: 3)
jubb.calistir(%intentler%, yeniden_baglan: false)  # kopunca yeniden deneme
```

Slash komutları için uygulama kimliği gerekir — READY paketiyle otomatik
geliyorsa elle vermene gerek yok.

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

## Çalışan bot örneği

`examples/bot/` klasöründe çalışır bir bot var:

```bash
cp examples/bot/.env.ornek examples/bot/.env    # token'ını yaz
ton examples/bot/bot.ton
```

## Neden `npm install @jubbio/core` çevrilmedi?

`ton jston` bir **sözdizimi** çeviricisi. `@jubbio/core` paketinin özü ise
TON'da olmayan çalışma zamanı şeyleri: izinler bit alanı (`1n << 0n`), gateway
bir WebSocket, API'nin şekli `class ... extends EventEmitter`, ve 72 tane
`require()`. Ölçtük: 41 dosyanın 17'si çözümlenemiyor, kalanında 378 uyarı
çıkıyor.

Bu yüzden paketi çevirmek yerine, altındaki HTTP API'yi TON'a doğrudan yazdık —
sonuç hem çalışıyor hem okunuyor.
