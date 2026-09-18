# Axs — Moderasyon ve Destek Botu

Jubbio sunucularını spam, reklam ve kötü içeriğe karşı korur; moderasyon ve
destek araçlarıyla yönetimi kolaylaştırır.

## Kurulum

```bash
cp .env.ornek .env
```

`.env` içine:

```
JUBB_TOKEN=bot_tokenin
JUBB_SUNUCU=sunucu_kimligin
```

```bash
axs bot.axs
```

Durdurmak için `Ctrl-C`. Ayarlar ve kayıtlar `axs.db` dosyasında tutulur.

Sunucuda ilk iş: **`/destek-ayarla`** ve **`/koruma`**.

---

## Destek (ticket) sistemi

`/destek-ayarla` → yalnızca sana görünen bir ayar paneli açılır:

| Seçim | Ne işe yarar |
|---|---|
| Ticket kategorisi | Talep kanalları bu kategorinin altında açılır |
| Yetkili rol | Talepleri görebilecek ve moderasyon yapabilecek rol |
| Kayıt kanalı | Bütün işlemlerin log'u buraya düşer |

Seçimleri yaptıktan sonra **Paneli Gönder** → bulunduğun kanala herkese açık
destek paneli düşer.

Akış:

1. Üye **Destek Talebi Oluştur** butonuna basar
2. Konu ve açıklama formu açılır
3. `destek-1`, `destek-2` … adıyla özel bir kanal açılır
   - `@everyone` göremez
   - Talebi açan kişi ve yetkili rol görebilir
4. Kanalda **Talebi Kapat** butonu vardır — onaylanınca kanal silinir, log düşer

Aynı anda bir kişinin yalnızca bir açık talebi olabilir.

---

## Koruma (otomatik moderasyon)

`/koruma` → butonlarla açıp kapatılan filtreler:

| Filtre | Yakaladığı |
|---|---|
| **reklam** | Bağlantı ve davet linkleri |
| **kufur** | Engelli kelimeler |
| **spam** | 7 saniyede 5 mesaj, ya da aynı mesajın 3 kez tekrarı |
| **caps** | Mesajın %70'inden fazlası büyük harf |
| **etiket** | Tek mesajda 5+ etiket |

Yakalanan mesaj silinir, kişiye yalnızca kendisinin göreceği bir uyarı gider,
uyarı kaydı tutulur ve log kanalına düşer. Uyarı sınırı (varsayılan 3) aşılınca
kişi otomatik 1 saat susturulur.

Mesaj yönetme yetkisi olanlar filtrelerden muaftır.

Engelli kelime listesini değiştirmek için veritabanındaki `engelli_kelimeler`
ayarını virgülle ayrılmış olarak yaz.

---

## Komutlar

**Herkes**

| Komut | Ne yapar |
|---|---|
| `/yardim` | Komut listesi |
| `/botbilgi` | Bot hakkında |
| `/sicil [kullanici]` | Üye kaydı ve uyarı sayısı |
| `/uyarilar [kullanici]` | Uyarı kayıtları |

**Moderasyon** (yetki gerekir)

| Komut | Gereken yetki |
|---|---|
| `/temizle adet` | Mesaj yönet |
| `/uyar kullanici [sebep]` | Mesaj yönet |
| `/uyari-sil kullanici` | Mesaj yönet |
| `/sustur kullanici [dakika] [sebep]` | Üye sustur |
| `/sustur-kaldir kullanici` | Üye sustur |
| `/at kullanici [sebep]` | Üye at |
| `/yasakla kullanici [sebep] [gun]` | Üye yasakla |
| `/yasak-kaldir kullanici` | Üye yasakla |
| `/rol kullanici rol [islem]` | Rol yönet |

**Ayarlar** (sunucu yönetme yetkisi)

`/destek-ayarla` · `/koruma`

Ayarlarda seçtiğin **yetkili rol** de bütün moderasyon komutlarını kullanabilir.

---

## Dosyalar

| Dosya | İçerik |
|---|---|
| `bot.axs` | Giriş: komut tanımları, olay yönlendirme |
| `ortak.axs` | Veritabanı, ayarlar, gömülü kutular, yetki, log |
| `ticket.axs` | Destek sistemi |
| `moderasyon.axs` | Moderasyon komutları |
| `koruma.axs` | Otomatik filtreler |

Yeni komut eklemek: `bot.axs` içindeki `KOMUTLAR` listesine tanımı, `slash_geldi`
işine de bir `elif` dalı ekle.

## Not

`.env` ve `axs.db` `.gitignore` içinde — token'ın ve kayıtların depoya gitmez.
