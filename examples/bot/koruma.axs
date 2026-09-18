# Otomatik koruma: reklam, kufur, spam, caps ve etiket yagmuru
use jubbio
use "ortak.axs"

# Sunucu yoneticisi bu listeyi degistirebilir (veritabanindaki "engelli_kelimeler")
VARSAYILAN_KELIMELER = ["amk", "aq", "oc", "piç", "orospu", "yarrak", "sikerim",
                        "siktir", "gavat", "ananı", "anan"]

KORUMALAR = {
  reklam: "Reklam / baglanti engeli",
  kufur: "Kufur engeli",
  spam: "Spam engeli",
  caps: "Buyuk harf engeli",
  etiket: "Toplu etiket engeli"
}

_son_mesajlar = {}

# ---------------------------------------------------------------- /koruma
func koruma_paneli(e)
  if not yetkili_mi(e, ["sunucu_yonet"])
    return yetkisiz_cevap(e)
  end
  jubbio.cevapla(e, _panel(e.guild_id), gizli: true)
  return null
end

func _panel(sunucu)
  satirlar = ""
  butonlar = []
  for anahtar, baslik in KORUMALAR
    acik = ayar_acik_mi(sunucu, "koruma_" + anahtar)
    isaret = "🔴 kapali"
    bicim = "gri"
    if acik
      isaret = "🟢 acik"
      bicim = "yesil"
    end
    satirlar = satirlar + "**" + baslik + ":** " + isaret + "\n"
    if len(butonlar) < 5
      ekle(butonlar, jubbio.buton(anahtar, "k_" + anahtar, bicim: bicim))
    end
  end
  sinir = ayar_oku(sunucu, "uyari_siniri", "3")
  satirlar = satirlar + "\n**Otomatik ceza:** " + sinir
           + " uyaridan sonra 1 saat susturma"
  return {baslik: "🛡️ Koruma Ayarlari",
          aciklama: satirlar + "\n\nButona basarak acip kapatabilirsin.",
          renk: RENK,
          bilesenler: [jubbio.satir(butonlar)]}
end

func koruma_dugmesi(e, kimlik)
  if not yetkili_mi(e, ["sunucu_yonet"])
    return yetkisiz_cevap(e)
  end
  sunucu = e.guild_id
  anahtar = replace(kimlik, "k_", "", 1)
  if not has(KORUMALAR, anahtar)
    return null
  end
  yeni = "1"
  if ayar_acik_mi(sunucu, "koruma_" + anahtar)
    yeni = "0"
  end
  ayar_yaz(sunucu, "koruma_" + anahtar, yeni)
  jubbio.guncelle(e, _panel(sunucu))
  return null
end

# ---------------------------------------------------------------- denetim
# Mesaji denetler. Islem yapildiysa true doner.
func mesaj_denetle(m)
  sunucu = al(m, "guild_id", null)
  if sunucu == null
    return false
  end
  uye = al(m, "member", null)
  if uye != null
    if jubbio.izni_var(uye, ["mesaj_yonet"])
      return false
    end
  end

  icerik = al(m, "content", "")
  if icerik == ""
    return false
  end

  if ayar_acik_mi(sunucu, "koruma_reklam")
    if _reklam_mi(icerik)
      return _ceza(m, "Reklam / baglanti paylasimi")
    end
  end
  if ayar_acik_mi(sunucu, "koruma_kufur")
    if _kufur_mu(sunucu, icerik)
      return _ceza(m, "Kufur")
    end
  end
  if ayar_acik_mi(sunucu, "koruma_etiket")
    if adet(icerik, "<@") >= 5
      return _ceza(m, "Toplu etiket")
    end
  end
  if ayar_acik_mi(sunucu, "koruma_caps")
    if _buyuk_oran(icerik) > 0.7
      return _ceza(m, "Asiri buyuk harf")
    end
  end
  if ayar_acik_mi(sunucu, "koruma_spam")
    if _spam_mi(m)
      return _ceza(m, "Spam")
    end
  end
  return false
end

func _reklam_mi(icerik)
  kucuk = lower(icerik)
  for parca in ["http://", "https://", "www.", "discord.gg", "jubbio.com/invite",
                ".com/invite", "t.me/"]
    if contains(kucuk, parca)
      return true
    end
  end
  return false
end

func _kufur_mu(sunucu, icerik)
  ham = ayar_oku(sunucu, "engelli_kelimeler", "")
  kelimeler = VARSAYILAN_KELIMELER
  if ham != ""
    kelimeler = split(ham, ",")
  end
  kucuk = lower(icerik)
  for k in kelimeler
    temiz = trim(k)
    if temiz != ""
      if contains(kucuk, temiz)
        return true
      end
    end
  end
  return false
end

func _buyuk_oran(yazi)
  toplam = 0
  buyuk = 0
  for harf in yazi
    if lower(harf) != upper(harf)
      toplam += 1
      if harf == upper(harf)
        buyuk += 1
      end
    end
  end
  if toplam < 8
    return 0
  end
  return buyuk / toplam
end

func _spam_mi(m)
  anahtar = metin(m.guild_id) + ":" + metin(al(al(m, "author", {}), "id", 0))
  simdi = zaman()
  gecmis = al(_son_mesajlar, anahtar, [])
  yeni = []
  for kayit_satiri in gecmis
    if simdi - kayit_satiri.zaman < 7
      ekle(yeni, kayit_satiri)
    end
  end
  ekle(yeni, {zaman: simdi, yazi: lower(trim(al(m, "content", "")))})
  _son_mesajlar[anahtar] = yeni

  if len(yeni) >= 5
    return true
  end
  # ayni mesaji ust uste yazma
  son_yazi = yeni[-1].yazi
  ayni = 0
  for kayit_satiri in yeni
    if kayit_satiri.yazi == son_yazi
      ayni += 1
    end
  end
  return ayni >= 3
end

func _ceza(m, sebep)
  sunucu = m.guild_id
  kanal = m.channel_id
  yazar = al(m, "author", {})
  kisi = al(yazar, "id", 0)

  try
    jubbio.mesaj_sil(sunucu, kanal, al(m, "id", 0))
  catch mesaj
    print: [koruma] mesaj silinemedi: mesaj;
  end

  toplam = uyari_ekle(sunucu, kisi, "Otomatik: " + sebep, "sistem")
  try
    jubbio.gizli_yolla(sunucu, kanal, kisi,
                     uyari_kutusu("Mesajin silindi.\n**Sebep:** " + sebep
                                  + "\n**Uyari:** " + toplam))
  catch
    print: [koruma] uyari mesaji gonderilemedi
  end

  kayit(sunucu, "🛡️ Otomatik islem",
        "**Kisi:** " + jubbio.bahset(kisi) + "\n**Sebep:** " + sebep + "\n"
        + "**Uyari:** " + toplam + "\n**Kanal:** <#" + kanal + ">", RENK_SARI)

  sinir = number(ayar_oku(sunucu, "uyari_siniri", "3"), 3)
  if toplam >= sinir
    try
      jubbio.sustur(sunucu, kisi, 3600, "Otomatik: uyari siniri asildi")
      kayit(sunucu, "🔇 Otomatik susturma",
            jubbio.bahset(kisi) + " 1 saat susturuldu (" + toplam + " uyari)",
            RENK_KIRMIZI)
    catch mesaj
      print: [koruma] susturma olmadi: mesaj;
    end
  end
  return true
end
