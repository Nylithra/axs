# Destek (ticket) sistemi: ayar paneli, genel panel, kanal acma/kapatma
use jubbio
use "ortak.axs"

# ---------------------------------------------------------------- /destek-ayarla
func destek_ayar_paneli(e)
  if not yetkili_mi(%e%, ["sunucu_yonet"])
    return yetkisiz_cevap(%e%)
  end
  sunucu = %e.guild_id%
  jubbio.cevapla(%e%, _ayar_paneli(%sunucu%), gizli: true)
  return null
end

func _ayar_paneli(sunucu)
  kategori = ayar_oku(%sunucu%, "ticket_kategori", "")
  yetkili = ayar_oku(%sunucu%, "yetkili_rol", "")
  kayit_kanali = ayar_oku(%sunucu%, "kayit_kanali", "")

  durum = "**Kategori:** " + _gosterim(%kategori%, "kanal") + "\n"
        + "**Yetkili rol:** " + _gosterim(%yetkili%, "rol") + "\n"
        + "**Kayit kanali:** " + _gosterim(%kayit_kanali%, "kanal") + "\n\n"
        + "Asagidan sec, sonra **Paneli Gonder**'e bas."

  kanallar = jubbio.kanallar(%sunucu%)
  roller = jubbio.roller(%sunucu%)

  satirlar = [
    jubbio.satir([jubbio.menu("t_kategori", _kanal_secenekleri(%kanallar%, 4),
                          yer_tutucu: "Ticket kategorisi sec")]),
    jubbio.satir([jubbio.menu("t_yetkili", _rol_secenekleri(%roller%),
                          yer_tutucu: "Yetkili rolu sec")]),
    jubbio.satir([jubbio.menu("t_kayit", _kanal_secenekleri(%kanallar%, 0),
                          yer_tutucu: "Kayit kanalini sec")]),
    jubbio.satir([
      jubbio.buton("Paneli Gonder", "t_panel", bicim: "yesil", emoji: "📨"),
      jubbio.buton("Yenile", "t_yenile", bicim: "gri", emoji: "🔄")
    ])
  ]

  return {baslik: "🎫 Destek Sistemi Ayarlari", aciklama: %durum%, renk: %RENK%,
          bilesenler: %satirlar%}
end

func _gosterim(deger, tur)
  if %deger% == ""
    return "_secilmedi_"
  end
  if %tur% == "rol"
    return "<@&" + %deger% + ">"
  end
  return "<#" + %deger% + ">"
end

func _kanal_secenekleri(kanallar, tur)
  liste = []
  for k in %kanallar%
    if al(%k%, "type", 0) == %tur%
      if len(%liste%) < 25
        ekle(%liste%, {etiket: kes(al(%k%, "name", "kanal"), 0, 90),
                       deger: metin(al(%k%, "id", 0))})
      end
    end
  end
  if len(%liste%) == 0
    ekle(%liste%, {etiket: "(uygun kanal yok)", deger: "0"})
  end
  return %liste%
end

func _rol_secenekleri(roller)
  liste = []
  for r in %roller%
    ad = al(%r%, "name", "rol")
    if %ad% != "@everyone"
      if len(%liste%) < 25
        ekle(%liste%, {etiket: kes(%ad%, 0, 90), deger: metin(al(%r%, "id", 0))})
      end
    end
  end
  if len(%liste%) == 0
    ekle(%liste%, {etiket: "(rol yok)", deger: "0"})
  end
  return %liste%
end

# ---------------------------------------------------------------- ayar butonlari
func destek_ayar_islemi(e, kimlik)
  sunucu = %e.guild_id%
  if not yetkili_mi(%e%, ["sunucu_yonet"])
    return yetkisiz_cevap(%e%)
  end

  if %kimlik% == "t_kategori"
    ayar_yaz(%sunucu%, "ticket_kategori", jubbio.secilen(%e%))
    jubbio.guncelle(%e%, _ayar_paneli(%sunucu%))

  elif %kimlik% == "t_yetkili"
    ayar_yaz(%sunucu%, "yetkili_rol", jubbio.secilen(%e%))
    jubbio.guncelle(%e%, _ayar_paneli(%sunucu%))

  elif %kimlik% == "t_kayit"
    ayar_yaz(%sunucu%, "kayit_kanali", jubbio.secilen(%e%))
    jubbio.guncelle(%e%, _ayar_paneli(%sunucu%))

  elif %kimlik% == "t_yenile"
    jubbio.guncelle(%e%, _ayar_paneli(%sunucu%))

  elif %kimlik% == "t_panel"
    if ayar_oku(%sunucu%, "ticket_kategori", "") == ""
      jubbio.cevapla(%e%, hata_kutusu("Once bir ticket kategorisi sec."), gizli: true)
      return null
    end
    genel_panel_gonder(%sunucu%, %e.channel_id%)
    jubbio.cevapla(%e%, basarili("Destek paneli bu kanala gonderildi."), gizli: true)
  end
  return null
end

# ---------------------------------------------------------------- genel panel
func genel_panel_gonder(sunucu, kanal)
  govde = "Bir sorunun mu var? Asagidaki butona basarak destek talebi olustur.\n\n"
        + "• Sadece sen ve yetkililer talebini gorebilir\n"
        + "• Isin bitince talebi kapatabilirsin\n"
        + "• Ayni anda tek bir acik talebin olabilir"
  return jubbio.yolla(%sunucu%, %kanal%, {
    baslik: "🎫 Destek Merkezi",
    aciklama: %govde%,
    renk: %RENK%,
    bilesenler: [jubbio.satir([
      jubbio.buton("Destek Talebi Olustur", "t_ac", bicim: "yesil", emoji: "🎫")
    ])]
  })
end

# ---------------------------------------------------------------- talep acma
func ticket_ac_basildi(e)
  sunucu = %e.guild_id%
  kisi = jubbio.kim(%e%)
  varolan = acik_ticket(%sunucu%, al(%kisi%, "id", 0))
  if %varolan% != null
    jubbio.cevapla(%e%, uyari_kutusu("Zaten acik bir talebin var: <#"
                                   + %varolan.kanal% + ">"), gizli: true)
    return null
  end
  jubbio.form_goster(%e%, "t_form", "Destek Talebi", [
    jubbio.metin_kutusu("konu", "Konu", yer_tutucu: "Kisaca konu basligi"),
    jubbio.metin_kutusu("aciklama", "Aciklama", uzun: true,
                      yer_tutucu: "Sorunu detayli anlat")
  ])
  return null
end

func ticket_formu_gonderildi(e)
  sunucu = %e.guild_id%
  kisi = jubbio.kim(%e%)
  sahip = al(%kisi%, "id", 0)
  konu = jubbio.form_degeri(%e%, "konu", "Destek")
  aciklama = jubbio.form_degeri(%e%, "aciklama", "-")

  kategori = ayar_oku(%sunucu%, "ticket_kategori", "")
  yetkili_rol = ayar_oku(%sunucu%, "yetkili_rol", "")
  no = ticket_sayisi(%sunucu%) + 1

  izinler = [
    jubbio.izin_kaydi(%sunucu%, [], ["kanali_gor"]),
    jubbio.izin_kaydi(%sahip%, ["kanali_gor", "mesaj_yolla", "gecmisi_oku", "dosya"],
                    [], uye_mi: true)
  ]
  if %yetkili_rol% != ""
    ekle(%izinler%, jubbio.izin_kaydi(%yetkili_rol%,
                                    ["kanali_gor", "mesaj_yolla", "gecmisi_oku",
                                     "mesaj_yonet", "dosya"]))
  end

  try
    kanal = jubbio.kanal_ac(%sunucu%, {
      ad: "destek-" + %no%,
      kategori: %kategori%,
      izinler: %izinler%
    })
  catch mesaj
    jubbio.cevapla(%e%, hata_kutusu("Kanal acilamadi: " + %mesaj%), gizli: true)
    return null
  end

  kanal_no = al(%kanal%, "id", null)
  if %kanal_no% == null
    jubbio.cevapla(%e%, hata_kutusu("Kanal acildi ama kimligi alinamadi."), gizli: true)
    return null
  end

  ticket_yaz(%kanal_no%, %sunucu%, %sahip%, %konu%)

  karsilama = jubbio.bahset(%sahip%) + " talebini olusturdu.\n\n"
            + "**Konu:** " + %konu% + "\n"
            + "**Aciklama:** " + %aciklama% + "\n\n"
  if %yetkili_rol% != ""
    karsilama = %karsilama% + "<@&" + %yetkili_rol% + "> en kisa surede ilgilenecek."
  else
    karsilama = %karsilama% + "Yetkililer en kisa surede ilgilenecek."
  end

  jubbio.yolla(%sunucu%, %kanal_no%, {
    baslik: "🎫 Talep #" + %no%,
    aciklama: %karsilama%,
    renk: %RENK%,
    bilesenler: [jubbio.satir([
      jubbio.buton("Talebi Kapat", "t_kapat", bicim: "kirmizi", emoji: "🔒")
    ])]
  })

  jubbio.cevapla(%e%, basarili("Talebin olusturuldu: <#" + %kanal_no% + ">"), gizli: true)
  kayit(%sunucu%, "🎫 Talep acildi",
        jubbio.bahset(%sahip%) + " -> <#" + %kanal_no% + ">\n**Konu:** " + %konu%,
        %RENK_YESIL%)
  return null
end

# ---------------------------------------------------------------- talep kapatma
func ticket_kapat_basildi(e)
  kayit_satiri = ticket_oku(%e.channel_id%)
  if %kayit_satiri% == null
    jubbio.cevapla(%e%, hata_kutusu("Burasi bir destek kanali degil."), gizli: true)
    return null
  end
  jubbio.cevapla(%e%, {
    baslik: "Emin misin?",
    aciklama: "Bu talep kapatilacak ve kanal silinecek.",
    renk: %RENK_SARI%,
    bilesenler: [jubbio.satir([
      jubbio.buton("Evet, kapat", "t_kapat_onay", bicim: "kirmizi"),
      jubbio.buton("Vazgec", "t_iptal", bicim: "gri")
    ])]
  }, gizli: true)
  return null
end

func ticket_kapat_onaylandi(e)
  sunucu = %e.guild_id%
  kanal = %e.channel_id%
  kayit_satiri = ticket_oku(%kanal%)
  if %kayit_satiri% == null
    jubbio.cevapla(%e%, hata_kutusu("Bu kanal kayitli degil."), gizli: true)
    return null
  end
  kisi = jubbio.kim(%e%)
  ticket_kapat_kaydi(%kanal%)
  kayit(%sunucu%, "🔒 Talep kapatildi",
        "**Konu:** " + al(%kayit_satiri%, "konu", "-") + "\n"
        + "**Acan:** " + jubbio.bahset(al(%kayit_satiri%, "sahip", 0)) + "\n"
        + "**Kapatan:** " + jubbio.bahset(al(%kisi%, "id", 0)),
        %RENK_KIRMIZI%)
  jubbio.cevapla(%e%, basarili("Talep kapatiliyor, kanal birazdan silinecek."),
               gizli: true)
  wait(3)
  try
    jubbio.kanal_sil(%sunucu%, %kanal%)
  catch mesaj
    print: [ticket] kanal silinemedi: %mesaj%
  end
  return null
end

func ticket_iptal(e)
  jubbio.guncelle(%e%, {baslik: "Vazgecildi", aciklama: "Talep acik kaldi.",
                      renk: %RENK_GRI%, bilesenler: []})
  return null
end
