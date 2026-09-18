# ============================================================
#  TON  —  Jubbio moderasyon ve destek botu
#
#  Kurulum:
#    1. .env dosyasi olustur:
#         JUBB_TOKEN=bot_tokenin
#         JUBB_SUNUCU=sunucu_kimligin
#    2. ton bot.ton
#    3. Sunucuda /destek-ayarla ve /koruma ile ayarla
# ============================================================

use jubbio
use "ortak.axs"
use "ticket.axs"
use "moderasyon.axs"
use "koruma.axs"

token = env("JUBB_TOKEN")
if %token% == ""
  print: Token bulunamadi.
  print:
  print: .env dosyasi olustur, icine su satirlari yaz:
  print:   JUBB_TOKEN=bot_tokenin
  print:   JUBB_SUNUCU=sunucu_kimligin
  exit(1)
end

SUNUCU = env("JUBB_SUNUCU")

jubbio.giris(%token%, env("JUBB_UYGULAMA"))
jubbio.ag_ayarla(kayit: env("TON_KAYIT") == "1")

if env("JUBB_TEMEL") != ""
  jubbio.ayarla(temel: env("JUBB_TEMEL"))
end
if env("JUBB_GATEWAY") != ""
  jubbio.ag_ayarla(adres: env("JUBB_GATEWAY"))
end

veritabanini_kur()

# ============================================================
#  Komutlar
# ============================================================

KISI = {ad: "kullanici", aciklama: "Hedef kullanici", tur: "kullanici",
        zorunlu: true}
SEBEP = {ad: "sebep", aciklama: "Islemin sebebi", tur: "metin"}

KOMUTLAR = [
  jubbio.komut("yardim", "Butun komutlari gosterir"),
  jubbio.komut("botbilgi", "Bot hakkinda bilgi"),
  jubbio.komut("destek-ayarla", "Destek sistemini kurar ve panel gonderir"),
  jubbio.komut("koruma", "Otomatik koruma ayarlarini acar"),

  jubbio.komut("temizle", "Kanaldaki mesajlari toplu siler", [
    {ad: "adet", aciklama: "Kac mesaj (1-100)", tur: "sayi", zorunlu: true}
  ]),
  jubbio.komut("sustur", "Uyeyi belirli sure susturur", [
    %KISI%,
    {ad: "dakika", aciklama: "Kac dakika", tur: "sayi"},
    %SEBEP%
  ]),
  jubbio.komut("sustur-kaldir", "Susturmayi kaldirir", [%KISI%, %SEBEP%]),
  jubbio.komut("at", "Uyeyi sunucudan atar", [%KISI%, %SEBEP%]),
  jubbio.komut("yasakla", "Uyeyi yasaklar", [
    %KISI%, %SEBEP%,
    {ad: "gun", aciklama: "Kac gunluk mesaji silinsin", tur: "sayi"}
  ]),
  jubbio.komut("yasak-kaldir", "Yasagi kaldirir", [%KISI%, %SEBEP%]),
  jubbio.komut("uyar", "Uyeyi uyarir", [%KISI%, %SEBEP%]),
  jubbio.komut("uyarilar", "Uyari kayitlarini gosterir", [
    {ad: "kullanici", aciklama: "Hedef kullanici", tur: "kullanici"}
  ]),
  jubbio.komut("uyari-sil", "Uyenin uyarilarini siler", [%KISI%]),
  jubbio.komut("rol", "Rol verir ya da alir", [
    %KISI%,
    {ad: "rol", aciklama: "Rol", tur: "rol", zorunlu: true},
    {ad: "islem", aciklama: "ver / al", tur: "metin"}
  ]),
  jubbio.komut("sicil", "Uyenin kaydini gosterir", [
    {ad: "kullanici", aciklama: "Hedef kullanici", tur: "kullanici"}
  ])
]

# ============================================================
#  Bilgi komutlari
# ============================================================

func komut_yardim(e)
  genel = "`/yardim` — bu yazi\n"
        + "`/botbilgi` — bot hakkinda\n"
        + "`/sicil` — uye kaydi\n"
        + "`/uyarilar` — uyarilarini gor\n"
  destek = "`/destek-ayarla` — destek panelini kur\n"
  moderasyon = "`/temizle` — toplu mesaj sil\n"
             + "`/uyar` · `/uyari-sil` — uyari islemleri\n"
             + "`/sustur` · `/sustur-kaldir` — susturma\n"
             + "`/at` · `/yasakla` · `/yasak-kaldir` — uzaklastirma\n"
             + "`/rol` — rol ver / al\n"
  koruma = "`/koruma` — reklam, kufur, spam, caps ve etiket filtreleri\n"

  jubbio.cevapla(%e%, {
    baslik: "📖 " + %MARKA% + " Komutlari",
    aciklama: "**Herkes**\n" + %genel%
            + "\n**Destek**\n" + %destek%
            + "\n**Moderasyon** _(yetki gerekir)_\n" + %moderasyon%
            + "\n**Koruma** _(yetki gerekir)_\n" + %koruma%,
    renk: %RENK%
  }, gizli: true)
  return null
end

func komut_botbilgi(e)
  jubbio.cevapla(%e%, {
    baslik: "🤖 " + %MARKA% + " Bot",
    aciklama: "**" + %MARKA% + " bot**, *nylithra* tarafindan gelistirilmistir.\n\n"
            + "*lanux* tarafindan gelistirilen **Axs** dili ile kodlanmistir.\n\n"
            + "Sunucunu spam, reklam ve kotu icerige karsi korur; "
            + "moderasyon ve destek araclariyla yonetimi kolaylastirir.",
    renk: %RENK%
  })
  return null
end

# ============================================================
#  Olay yonlendirme
# ============================================================

func hazir(veri)
  print:
  print: ============================================
  print:  %MARKA% hazir  —  %veri.user.username%
  print: ============================================
  if jubbio.ayar().uygulama == ""
    print: [!] Uygulama kimligi gelmedi, komutlar kaydedilemiyor.
    print:     .env icine JUBB_UYGULAMA=... yazabilirsin.
    return null
  end
  try
    if %SUNUCU% != ""
      jubbio.komutlari_ayarla(%KOMUTLAR%, %SUNUCU%)
      print: %(len(%KOMUTLAR%))% komut sunucuya kaydedildi
    else
      jubbio.komutlari_ayarla(%KOMUTLAR%)
      print: %(len(%KOMUTLAR%))% komut genel kaydedildi (gorunmesi zaman alabilir)
    end
  catch mesaj
    print: [!] Komutlar kaydedilemedi: %mesaj%
  end
  print:
  return null
end

func slash_geldi(e)
  ad = jubbio.komut_adi(%e%)
  kisi = jubbio.kim(%e%)
  print: [/%ad%] %(al(%kisi%, "username", "?"))%

  try
    if %ad% == "yardim"
      komut_yardim(%e%)
    elif %ad% == "botbilgi"
      komut_botbilgi(%e%)
    elif %ad% == "destek-ayarla"
      destek_ayar_paneli(%e%)
    elif %ad% == "koruma"
      koruma_paneli(%e%)
    elif %ad% == "temizle"
      komut_temizle(%e%)
    elif %ad% == "sustur"
      komut_sustur(%e%)
    elif %ad% == "sustur-kaldir"
      komut_sustur_kaldir(%e%)
    elif %ad% == "at"
      komut_at(%e%)
    elif %ad% == "yasakla"
      komut_yasakla(%e%)
    elif %ad% == "yasak-kaldir"
      komut_yasak_kaldir(%e%)
    elif %ad% == "uyar"
      komut_uyar(%e%)
    elif %ad% == "uyarilar"
      komut_uyarilar(%e%)
    elif %ad% == "uyari-sil"
      komut_uyari_sil(%e%)
    elif %ad% == "rol"
      komut_rol(%e%)
    elif %ad% == "sicil"
      komut_sicil(%e%)
    else
      jubbio.cevapla(%e%, hata_kutusu("Bilinmeyen komut: /" + %ad%), gizli: true)
    end
  catch mesaj
    print: [hata] /%ad% -> %mesaj%
    try
      jubbio.cevapla(%e%, hata_kutusu("Bir sorun cikti: " + %mesaj%), gizli: true)
    catch
      print: [hata] cevap da gonderilemedi
    end
  end
  return null
end

func dugme_basildi(e)
  kimlik = jubbio.kimlik(%e%)
  print: [dugme] %kimlik%
  try
    if %kimlik% == "t_ac"
      ticket_ac_basildi(%e%)
    elif %kimlik% == "t_kapat"
      ticket_kapat_basildi(%e%)
    elif %kimlik% == "t_kapat_onay"
      ticket_kapat_onaylandi(%e%)
    elif %kimlik% == "t_iptal"
      ticket_iptal(%e%)
    elif starts(%kimlik%, "t_")
      destek_ayar_islemi(%e%, %kimlik%)
    elif starts(%kimlik%, "k_")
      koruma_dugmesi(%e%, %kimlik%)
    end
  catch mesaj
    print: [hata] dugme %kimlik% -> %mesaj%
  end
  return null
end

func form_geldi(e)
  kimlik = jubbio.kimlik(%e%)
  print: [form] %kimlik%
  try
    if %kimlik% == "t_form"
      ticket_formu_gonderildi(%e%)
    end
  catch mesaj
    print: [hata] form %kimlik% -> %mesaj%
  end
  return null
end

func mesaj_geldi(m)
  if %m.kendim%
    return null
  end
  try
    mesaj_denetle(%m%)
  catch mesaj
    print: [koruma] %mesaj%
  end
  return null
end

func uye_katildi(veri)
  sunucu = al(%veri%, "guild_id", null)
  kullanici = al(%veri%, "user", {})
  kayit(%sunucu%, "📥 Uye katildi",
        jubbio.bahset(al(%kullanici%, "id", 0)) + " ("
        + al(%kullanici%, "username", "?") + ")", %RENK_YESIL%)
  return null
end

func uye_ayrildi(veri)
  sunucu = al(%veri%, "guild_id", null)
  kullanici = al(%veri%, "user", {})
  kayit(%sunucu%, "📤 Uye ayrildi",
        al(%kullanici%, "username", "?"), %RENK_GRI%)
  return null
end

func baglanti_hatasi(mesaj)
  print: [ag] %mesaj%
end

# ============================================================
#  Baslat
# ============================================================

jubbio.dinle("hazir", hazir)
jubbio.dinle("komut", slash_geldi)
jubbio.dinle("dugme", dugme_basildi)
jubbio.dinle("form", form_geldi)
jubbio.dinle("mesaj", mesaj_geldi)
jubbio.dinle("uye_katildi", uye_katildi)
jubbio.dinle("uye_ayrildi", uye_ayrildi)
jubbio.dinle("hata", baglanti_hatasi)

print: %MARKA% baglaniyor...

jubbio.calistir(["sunucular", "mesajlar", "icerik", "uyeler", "denetim"])
