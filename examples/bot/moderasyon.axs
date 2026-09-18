# Moderasyon komutlari
use jubbio
use "ortak.axs"

func _hedef(e, alan = "kullanici")
  return metin(jubbio.secenek(%e%, %alan%, ""))
end

func _sebep(e)
  return jubbio.secenek(%e%, "sebep", "Sebep belirtilmedi")
end

# ---------------------------------------------------------------- /temizle
func komut_temizle(e)
  if not yetkili_mi(%e%, ["mesaj_yonet"])
    return yetkisiz_cevap(%e%)
  end
  adet = number(jubbio.secenek(%e%, "adet", 10), 10)
  if %adet% < 1 or %adet% > 100
    jubbio.cevapla(%e%, hata_kutusu("1 ile 100 arasi bir sayi ver."), gizli: true)
    return null
  end
  sunucu = %e.guild_id%
  kanal = %e.channel_id%
  mesajlar = jubbio.mesajlar(%sunucu%, %kanal%, %adet%)
  kimlikler = []
  for m in %mesajlar%
    ekle(%kimlikler%, metin(al(%m%, "id", 0)))
  end
  if len(%kimlikler%) == 0
    jubbio.cevapla(%e%, uyari_kutusu("Silinecek mesaj bulunamadi."), gizli: true)
    return null
  end
  try
    jubbio.toplu_sil(%sunucu%, %kanal%, %kimlikler%)
  catch mesaj
    jubbio.cevapla(%e%, hata_kutusu("Silinemedi: " + %mesaj%), gizli: true)
    return null
  end
  jubbio.cevapla(%e%, basarili(len(%kimlikler%) + " mesaj silindi."), gizli: true)
  kayit(%sunucu%, "🧹 Mesaj temizlendi",
        "<#" + %kanal% + "> kanalinda " + len(%kimlikler%) + " mesaj\n"
        + "**Yetkili:** " + jubbio.bahset(jubbio.kim(%e%).id), %RENK_SARI%)
  return null
end

# ---------------------------------------------------------------- /sustur
func komut_sustur(e)
  if not yetkili_mi(%e%, ["uye_sustur"])
    return yetkisiz_cevap(%e%)
  end
  hedef = _hedef(%e%)
  dakika = number(jubbio.secenek(%e%, "dakika", 10), 10)
  sebep = _sebep(%e%)
  if %hedef% == ""
    jubbio.cevapla(%e%, hata_kutusu("Bir kullanici sec."), gizli: true)
    return null
  end
  try
    jubbio.sustur(%e.guild_id%, %hedef%, %dakika% * 60, %sebep%)
  catch mesaj
    jubbio.cevapla(%e%, hata_kutusu("Susturulamadi: " + %mesaj%), gizli: true)
    return null
  end
  jubbio.cevapla(%e%, basarili(jubbio.bahset(%hedef%) + " " + %dakika%
                             + " dakika susturuldu.\n**Sebep:** " + %sebep%))
  kayit(%e.guild_id%, "🔇 Susturma",
        "**Kisi:** " + jubbio.bahset(%hedef%) + "\n**Sure:** " + %dakika% + " dk\n"
        + "**Sebep:** " + %sebep% + "\n"
        + "**Yetkili:** " + jubbio.bahset(jubbio.kim(%e%).id), %RENK_SARI%)
  return null
end

func komut_sustur_kaldir(e)
  if not yetkili_mi(%e%, ["uye_sustur"])
    return yetkisiz_cevap(%e%)
  end
  hedef = _hedef(%e%)
  try
    jubbio.susturma_kaldir(%e.guild_id%, %hedef%, _sebep(%e%))
  catch mesaj
    jubbio.cevapla(%e%, hata_kutusu("Olmadi: " + %mesaj%), gizli: true)
    return null
  end
  jubbio.cevapla(%e%, basarili(jubbio.bahset(%hedef%) + " artik konusabilir."))
  kayit(%e.guild_id%, "🔊 Susturma kaldirildi",
        jubbio.bahset(%hedef%) + " - " + jubbio.bahset(jubbio.kim(%e%).id), %RENK_YESIL%)
  return null
end

# ---------------------------------------------------------------- /at  /yasakla
func komut_at(e)
  if not yetkili_mi(%e%, ["uye_at"])
    return yetkisiz_cevap(%e%)
  end
  hedef = _hedef(%e%)
  sebep = _sebep(%e%)
  try
    jubbio.at(%e.guild_id%, %hedef%, %sebep%)
  catch mesaj
    jubbio.cevapla(%e%, hata_kutusu("Atilamadi: " + %mesaj%), gizli: true)
    return null
  end
  jubbio.cevapla(%e%, basarili(jubbio.bahset(%hedef%) + " sunucudan atildi.\n**Sebep:** "
                             + %sebep%))
  kayit(%e.guild_id%, "👢 Sunucudan atildi",
        "**Kisi:** " + jubbio.bahset(%hedef%) + "\n**Sebep:** " + %sebep% + "\n"
        + "**Yetkili:** " + jubbio.bahset(jubbio.kim(%e%).id), %RENK_KIRMIZI%)
  return null
end

func komut_yasakla(e)
  if not yetkili_mi(%e%, ["uye_yasakla"])
    return yetkisiz_cevap(%e%)
  end
  hedef = _hedef(%e%)
  sebep = _sebep(%e%)
  gun = number(jubbio.secenek(%e%, "gun", 0), 0)
  try
    jubbio.yasakla(%e.guild_id%, %hedef%, %sebep%, %gun%)
  catch mesaj
    jubbio.cevapla(%e%, hata_kutusu("Yasaklanamadi: " + %mesaj%), gizli: true)
    return null
  end
  jubbio.cevapla(%e%, basarili(jubbio.bahset(%hedef%) + " yasaklandi.\n**Sebep:** "
                             + %sebep%))
  kayit(%e.guild_id%, "🔨 Yasaklandi",
        "**Kisi:** " + jubbio.bahset(%hedef%) + "\n**Sebep:** " + %sebep% + "\n"
        + "**Yetkili:** " + jubbio.bahset(jubbio.kim(%e%).id), %RENK_KIRMIZI%)
  return null
end

func komut_yasak_kaldir(e)
  if not yetkili_mi(%e%, ["uye_yasakla"])
    return yetkisiz_cevap(%e%)
  end
  hedef = _hedef(%e%)
  try
    jubbio.yasak_kaldir(%e.guild_id%, %hedef%, _sebep(%e%))
  catch mesaj
    jubbio.cevapla(%e%, hata_kutusu("Olmadi: " + %mesaj%), gizli: true)
    return null
  end
  jubbio.cevapla(%e%, basarili("Yasak kaldirildi."))
  kayit(%e.guild_id%, "♻️ Yasak kaldirildi",
        jubbio.bahset(%hedef%) + " - " + jubbio.bahset(jubbio.kim(%e%).id), %RENK_YESIL%)
  return null
end

# ---------------------------------------------------------------- uyarilar
func komut_uyar(e)
  if not yetkili_mi(%e%, ["mesaj_yonet"])
    return yetkisiz_cevap(%e%)
  end
  hedef = _hedef(%e%)
  sebep = _sebep(%e%)
  sunucu = %e.guild_id%
  yetkili = jubbio.kim(%e%).id
  toplam = uyari_ekle(%sunucu%, %hedef%, %sebep%, %yetkili%)

  jubbio.cevapla(%e%, basarili(jubbio.bahset(%hedef%) + " uyarildi. (" + %toplam%
                             + ". uyari)\n**Sebep:** " + %sebep%))
  kayit(%sunucu%, "⚠️ Uyari",
        "**Kisi:** " + jubbio.bahset(%hedef%) + "\n**Sebep:** " + %sebep% + "\n"
        + "**Toplam:** " + %toplam% + "\n"
        + "**Yetkili:** " + jubbio.bahset(%yetkili%), %RENK_SARI%)

  # otomatik ceza basamaklari
  sinir = number(ayar_oku(%sunucu%, "uyari_siniri", "3"), 3)
  if %toplam% >= %sinir%
    try
      jubbio.sustur(%sunucu%, %hedef%, 3600, "Uyari siniri asildi")
      kayit(%sunucu%, "🔇 Otomatik susturma",
            jubbio.bahset(%hedef%) + " " + %toplam% + " uyari ile 1 saat susturuldu",
            %RENK_KIRMIZI%)
    catch mesaj
      print: [moderasyon] otomatik susturma olmadi: %mesaj%
    end
  end
  return null
end

func komut_uyarilar(e)
  hedef = _hedef(%e%)
  if %hedef% == ""
    hedef = metin(jubbio.kim(%e%).id)
  end
  sunucu = %e.guild_id%
  kayitlar = uyari_listesi(%sunucu%, %hedef%)
  if len(%kayitlar%) == 0
    jubbio.cevapla(%e%, kutu("📋 Uyari kaydi",
                           jubbio.bahset(%hedef%) + " icin uyari yok.", %RENK_YESIL%),
                 gizli: true)
    return null
  end
  satirlar = ""
  for k in %kayitlar%
    satirlar = %satirlar% + "`#" + %k.id% + "` " + %k.sebep%
             + "  —  " + kes(metin(%k.zaman%), 0, 10) + "\n"
  end
  jubbio.cevapla(%e%, kutu("📋 " + len(%kayitlar%) + " uyari",
                         jubbio.bahset(%hedef%) + "\n\n" + %satirlar%, %RENK_SARI%),
               gizli: true)
  return null
end

func komut_uyari_sil(e)
  if not yetkili_mi(%e%, ["mesaj_yonet"])
    return yetkisiz_cevap(%e%)
  end
  hedef = _hedef(%e%)
  uyari_sil(%e.guild_id%, %hedef%)
  jubbio.cevapla(%e%, basarili(jubbio.bahset(%hedef%) + " kisisinin uyarilari silindi."))
  return null
end

# ---------------------------------------------------------------- roller
func komut_rol(e)
  if not yetkili_mi(%e%, ["rol_yonet"])
    return yetkisiz_cevap(%e%)
  end
  hedef = _hedef(%e%)
  rol = metin(jubbio.secenek(%e%, "rol", ""))
  islem = jubbio.secenek(%e%, "islem", "ver")
  try
    if %islem% == "al"
      jubbio.rol_al(%e.guild_id%, %hedef%, %rol%)
      jubbio.cevapla(%e%, basarili("<@&" + %rol% + "> rolu alindi."))
    else
      jubbio.rol_ver(%e.guild_id%, %hedef%, %rol%)
      jubbio.cevapla(%e%, basarili("<@&" + %rol% + "> rolu verildi."))
    end
  catch mesaj
    jubbio.cevapla(%e%, hata_kutusu("Olmadi: " + %mesaj%), gizli: true)
    return null
  end
  kayit(%e.guild_id%, "🎭 Rol islemi",
        jubbio.bahset(%hedef%) + " -> <@&" + %rol% + "> (" + %islem% + ")", %RENK%)
  return null
end

# ---------------------------------------------------------------- /sicil
func komut_sicil(e)
  hedef = _hedef(%e%)
  if %hedef% == ""
    hedef = metin(jubbio.kim(%e%).id)
  end
  sunucu = %e.guild_id%
  uyari_adedi = uyari_sayisi(%sunucu%, %hedef%)
  bilgi = "Bilgi alinamadi"
  try
    uye = jubbio.uye(%sunucu%, %hedef%)
    kullanici = al(%uye%, "user", %uye%)
    bilgi = "**Kullanici:** " + al(%kullanici%, "username", "?") + "\n"
          + "**Kimlik:** `" + %hedef% + "`\n"
          + "**Rol sayisi:** " + len(al(%uye%, "roles", []))
  catch
    bilgi = "**Kimlik:** `" + %hedef% + "`"
  end
  jubbio.cevapla(%e%, kutu("👤 Sicil",
                         %bilgi% + "\n**Uyari:** " + %uyari_adedi%, %RENK%))
  return null
end
