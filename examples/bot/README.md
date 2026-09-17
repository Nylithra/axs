# TON Jubbio Botu

Hem yazılı komutlara (`!selam`) hem **slash komutlarına** (`/selam`) cevap verir.
Slash komutları açılışta kendiliğinden kaydedilir.

## Çalıştırma

```bash
cp examples/bot/.env.ornek examples/bot/.env
```

`.env` içine:

```
JUBB_TOKEN=bot_tokenin
JUBB_SUNUCU=sunucu_kimligin
```

```bash
ton examples/bot/bot.ton
```

Durdurmak için `Ctrl-C`.

> `JUBB_SUNUCU` verirsen slash komutları **anında** görünür. Boş bırakırsan
> genel (global) kaydedilir ve görünmesi zaman alabilir.

## Slash komutları

| Komut | Ne yapar |
|---|---|
| `/selam` | Selam verir |
| `/zar [yuz]` | Zar atar (varsayılan 6 yüzlü) |
| `/topla bir iki` | İki sayıyı toplar |
| `/yanki metin` | Yazdığını geri söyler |
| `/bilgi` | Gömülü kutuda bot bilgisi |
| `/gizli` | Sadece sana görünen cevap |

## Yazılı komutlar

`!selam` · `!zar` · `!topla 1 2 3` · `!yardim`

## Kendi komutunu eklemek

1. `KOMUTLAR` listesine tanımı ekle:

```ton
jubb.komut("hava", "Hava durumu", [
  {ad: "sehir", aciklama: "Sehir adi", tur: "metin", zorunlu: true}
])
```

2. `slash_geldi` işine dalı ekle:

```ton
elif %ad% == "hava"
  sehir = jubb.secenek(%e%, "sehir", "")
  jubb.cevapla(%e%, %sehir% + " icin hava: guzel")
```

Seçenek türleri: `metin` `sayi` `mantik` `kullanici` `kanal` `rol` `ondalik`

## Not

`.env` dosyası `.gitignore` içinde — token'ın depoya gitmez.
