# jubb — Jubbio bot kütüphanesi

```axs
use jubbio

jubbio.giris("BOT_TOKEN")
jubbio.yolla(sunucu, kanal, "Merhaba!")
```

Bu kütüphane **Axs ile yazılmıştır** — `kutuphaneler/jubbio.axs` dosyasını açıp
okuyabilir, değiştirebilirsin. Çekirdeğin `request()` işinden başka bir şey
kullanmaz.

Hem REST (mesaj yollama, üye/rol/kanal işlemleri) hem de **gateway** (gerçek
zamanlı olay dinleme) hazır.

---

## Kurulum

```axs
jubbio.giris("BOT_TOKEN")                  # sadece token
jubbio.giris("BOT_TOKEN", "UYGULAMA_ID")   # slash komutları için uygulama kimliği

jubbio.ayarla(kayit: true)                 # her isteği ekrana yaz
jubbio.ayarla(temel: "http://localhost:8080/api/v1")   # başka sunucu
```

## Mesajlar

```axs
jubbio.yolla(sunucu, kanal, "Merhaba!")

jubbio.yolla(sunucu, kanal, {
  baslik: "Başlık",
  aciklama: "Açıklama",
  renk: "#2f6fed",
  resim: "https://...",
  alt_yazi: "footer"
})

jubbio.gizli_yolla(sunucu, kanal, kullanici, "sadece sen görüyorsun")
jubbio.dm(kanal, "özel mesaj")

jubbio.duzenle(sunucu, kanal, mesaj, "yeni içerik")
jubbio.mesaj_sil(sunucu, kanal, mesaj)
jubbio.toplu_sil(sunucu, kanal, [m1, m2])

mesajlar = jubbio.mesajlar(sunucu, kanal, 20)

jubbio.tepki_ekle(sunucu, kanal, mesaj, "👍")
jubbio.tepki_sil(sunucu, kanal, mesaj, "👍")
jubbio.sabitle(sunucu, kanal, mesaj)
```

Metin verirsen düz mesaj, harita verirsen gömülü (embed) kutu olur. API'nin
kendi alan adlarını (`content`, `embeds`) yazarsan olduğu gibi geçer.

## Üyeler

```axs
jubbio.uye(sunucu, kullanici)
jubbio.uyeler(sunucu, 100)

jubbio.at(sunucu, kullanici, "sebep")              # kick
jubbio.yasakla(sunucu, kullanici, "sebep", 1)      # ban (1 günlük mesaj siler)
jubbio.yasak_kaldir(sunucu, kullanici)
jubbio.sustur(sunucu, kullanici, 600, "sakin ol")  # 600 saniye
jubbio.susturma_kaldir(sunucu, kullanici)

jubbio.rol_ver(sunucu, kullanici, rol)
jubbio.rol_al(sunucu, kullanici, rol)
jubbio.uye_duzenle(sunucu, kullanici, {nick: "yeni ad"})
```

## Sunucu, kanal, rol

```axs
jubbio.sunucu(kimlik)
jubbio.kanallar(sunucu)
jubbio.kanal_ac(sunucu, {name: "genel"})
jubbio.kanal_sil(sunucu, kanal)
jubbio.roller(sunucu)
jubbio.rol_ac(sunucu, {name: "üye"})
jubbio.rol_sil(sunucu, rol)
```

## Slash komutları

Uygulama kimliği gerekir: `jubbio.giris(token, uygulama_id)`

```axs
jubbio.komut_ekle({name: "selam", description: "Selam verir"})        # global
jubbio.komut_ekle({name: "selam", description: "..."}, sunucu)      # sunucuya özel
jubbio.komutlari_ayarla([{name: "a"}, {name: "b"}], sunucu)         # hepsini değiştir
jubbio.komutlar(sunucu)
jubbio.komut_sil(komut, sunucu)
```

## Slash komutları

Komutu tanımla, kaydet, gelen etkileşimi yanıtla:

```axs
KOMUTLAR = [
  jubbio.komut("selam", "Selam verir"),
  jubbio.komut("zar", "Zar atar", [
    {ad: "yuz", aciklama: "Kac yuzlu", tur: "sayi"}
  ]),
  jubbio.komut("yanki", "Geri soyler", [
    {ad: "metin", aciklama: "Yazi", tur: "metin", zorunlu: true}
  ])
]

func hazir(veri)
  jubbio.komutlari_ayarla(KOMUTLAR, SUNUCU)   # sunucuya özel: anında görünür
end

func slash_geldi(e)
  ad = jubbio.komut_adi(e)
  kisi = jubbio.kim(e)

  if ad == "zar"
    yuz = jubbio.secenek(e, "yuz", 6)
    jubbio.cevapla(e, "Zar: " + random(1, yuz))
  end
end

jubbio.dinle("hazir", hazir)
jubbio.dinle("komut", slash_geldi)
```

| İş | Ne yapar |
|---|---|
| `jubbio.komut(ad, aciklama, secenekler)` | Komut tanımı üretir |
| `jubbio.komut_adi(e)` | Hangi komut çağrıldı |
| `jubbio.secenek(e, ad, varsayilan)` | Komuta verilen değeri okur |
| `jubbio.kim(e)` | Komutu yazan kullanıcı |

Seçenek türleri: `metin` `sayi` `mantik` `kullanici` `kanal` `rol` `ondalik`
(`zorunlu: true` ile zorunlu yapılır).

Uygulama kimliği bağlantı sırasında (READY) kendiliğinden gelir; gelmezse
`jubbio.giris(token, uygulama_kimligi)` ile verirsin.

## Etkileşime cevap

```axs
jubbio.cevapla(etkilesim, "Merhaba!")
jubbio.cevapla(etkilesim, "sadece sen görürsün", gizli: true)

jubbio.dusun(etkilesim)                      # "düşünüyor..." göster
jubbio.cevap_duzenle(etkilesim, "sonuç")     # sonra cevabı yaz
jubbio.ek_cevap(etkilesim, "bir de bu")
```

## Gerçek zamanlı: gateway

```axs
use jubbio

jubbio.giris(env("JUBB_TOKEN"))

func mesaj_geldi(m)
  if m.kendim
    return null              # kendi mesajımıza cevap vermeyelim
  end
  if m.content == "!selam"
    jubbio.yolla(m.guild_id, m.channel_id, "Selam!")
  end
end

jubbio.dinle("mesaj", mesaj_geldi)
jubbio.calistir(["sunucular", "mesajlar", "icerik"])
```

`calistir()` bağlanır ve olaylar gelmeye başlar; `Ctrl-C`'ye kadar çalışır.
Bağlantı koparsa kendi kendine yeniden bağlanır (artan beklemeyle, en fazla
10 deneme).

### Olaylar

| Axs adı | Gateway olayı |
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

Hepsini görmek için: `jubbio.olaylar()`

Bir olaya birden çok iş bağlayabilirsin; hepsi sırayla çağrılır. Bir
dinleyicide hata çıkarsa bot durmaz, hata yazılır.

### Intent'ler

Hangi olayları almak istediğini söylersin:

```axs
jubbio.calistir(["sunucular", "mesajlar", "icerik"])
jubbio.calistir(33281)                 # sayı olarak da verebilirsin
```

`sunucular` `uyeler` `denetim` `emojiler` `entegrasyonlar` `webhooklar`
`davetler` `sesler` `durumlar` `mesajlar` `tepkiler` `yaziyor` `dm`
`dm_tepkileri` `dm_yaziyor` `icerik` `etkinlikler`

Hiçbir şey vermezsen varsayılan: sunucular + mesajlar + içerik.

### Bot bilgisi ve durdurma

```axs
jubbio.ben()                # botun kendi kullanıcı bilgisi (READY sonrası)
jubbio.benim_mi(mesaj)    # bu mesaj benden mi geldi?
jubbio.dur()                # gateway'i kapat, calistir() geri döner
```

Her mesajda hazır gelen kolaylık: `m.kendim` — bot kendi mesajını görüyorsa
`true`. **Bunu kontrol etmezsen bot kendi kendine cevap verip sonsuz döngüye
girer.**

### Ayarlar

```axs
jubbio.ag_ayarla(kayit: true)                        # bağlantı adımlarını yaz
jubbio.ag_ayarla(adres: "ws://127.0.0.1:9000/ws")    # başka gateway
jubbio.ag_ayarla(en_fazla_deneme: 3)
jubbio.calistir(intentler, yeniden_baglan: false)  # kopunca yeniden deneme
```

Slash komutları için uygulama kimliği gerekir — READY paketiyle otomatik
geliyorsa elle vermene gerek yok.

## Yardımcılar

```axs
jubbio.bahset(kullanici)      # <@123>
jubbio.gomulu({baslik: "...", renk: "#ff0000"})   # embed haritası üretir
jubbio.ayar()                   # şu anki ayarlar
```

## Hatalar

API hata dönerse Axs hatası fırlar; `try/catch` ile yakalarsın:

```axs
try
  jubbio.yolla(sunucu, kanal, "deneme")
catch mesaj
  print: gönderilemedi: mesaj;
end
```

```
Jubbio hatası (401) POST /bot/guilds/7/channels/9/messages: {error: "bad token"}
```

## Çalışan bot örneği

`examples/bot/` klasöründe çalışır bir bot var:

```bash
cp examples/bot/.env.ornek examples/bot/.env    # token'ını yaz
axs examples/bot/bot.axs
```

## Neden `npm install @jubbio/core` çevrilmedi?

`axs cevir` bir **sözdizimi** çeviricisi. `@jubbio/core` paketinin özü ise
Axs'da olmayan çalışma zamanı şeyleri: izinler bit alanı (`1n << 0n`), gateway
bir WebSocket, API'nin şekli `class ... extends EventEmitter`, ve 72 tane
`require()`. Ölçtük: 41 dosyanın 17'si çözümlenemiyor, kalanında 378 uyarı
çıkıyor.

Bu yüzden paketi çevirmek yerine, altındaki HTTP API'yi Axs'a doğrudan yazdık —
sonuç hem çalışıyor hem okunuyor.
