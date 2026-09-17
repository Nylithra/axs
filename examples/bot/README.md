# TON Jubbio Botu

## Çalıştırma

```bash
cp examples/bot/.env.ornek examples/bot/.env
# .env içine kendi token'ını yaz
ton examples/bot/bot.ton
```

Durdurmak için `Ctrl-C`.

## Komutlar

| Komut | Ne yapar |
|---|---|
| `!selam` | Selam verir |
| `!zar` | Zar atar |
| `!ping` | Yaşıyor mu bakar |
| `!topla 1 2 3` | Sayıları toplar |
| `!sunucu` | Sunucu bilgisini gömülü kutuda gösterir |
| `!yardim` | Komut listesi |

Slash komutları (`/selam`, `/zar`) da çalışır — önce kaydetmen gerekir:

```ton
jubb.komutlari_ayarla([
  {name: "selam", description: "Selam verir"},
  {name: "zar", description: "Zar atar"}
], %sunucu_kimligi%)
```

## Not

`.env` dosyası `.gitignore` içinde — token'ın depoya gitmez.
