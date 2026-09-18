# jubbio - Jubbio bot kutuphanesi
#
#   use jubbio
#
#   jubbio.giris("BOT_TOKEN")
#   jubbio.yolla(sunucu, kanal, "Merhaba!")
#
# Bu kutuphane Axs ile yazilmistir; acip okuyabilir, degistirebilirsin.
# Su an REST tarafini kapsar (mesaj, uye, rol, kanal, komut, etkilesim).
# Gercek zamanli olay dinleme (gateway) WebSocket ister, o ayri gelecek.

_ayar = {
  temel: "https://gateway.jubbio.com/api/v1",
  token: "",
  uygulama: "",
  kayit: false
}

# ---------------------------------------------------------------- kurulum
func giris(token, uygulama = "")
  _ayar.token = token
  if uygulama != ""
    _ayar.uygulama = uygulama
  end
  return true
end

func ayarla(temel = "", uygulama = "", kayit = null)
  if temel != ""
    _ayar.temel = temel
  end
  if uygulama != ""
    _ayar.uygulama = uygulama
  end
  if kayit != null
    _ayar.kayit = kayit
  end
  return _ayar
end

func ayar()
  return _ayar
end

# ---------------------------------------------------------------- istek
func _istek(yontem, yol, veri = null)
  if _ayar.token == ""
    hata("Once jubbio.giris(\"BOT_TOKEN\") yazmalisin")
  end
  adres = _ayar.temel + yol
  basliklar = {
    Authorization: "Bot " + _ayar.token,
    "Content-Type": "application/json"
  }
  if _ayar.kayit
    print: [jubb] yontem; adres;
  end
  cevap = request(adres, yontem, veri, basliklar)
  if not cevap.basarili
    ayrinti = metin(cevap.veri)
    if len(ayrinti) > 200
      ayrinti = kes(ayrinti, 0, 200) + "..."
    end
    hata("Jubbio hatasi (" + cevap.durum + ") " + yontem + " " + yol + ": " + ayrinti)
  end
  return cevap.veri
end

func _sunucu_yolu(sunucu)
  return "/bot/guilds/" + sunucu
end

func _kanal_yolu(sunucu, kanal)
  return _sunucu_yolu(sunucu) + "/channels/" + kanal
end

# Mesaj icerigini API govdesine cevirir.
# Metin verirsen duz mesaj, harita verirsen gomulu (embed) olur.
func _mesaj_govdesi(icerik)
  if type(icerik) == "metin"
    return {content: icerik}
  end
  if type(icerik) != "harita"
    return {content: metin(icerik)}
  end

  govde = {}
  # butonlar / menuler
  bilesenler = al(icerik, "bilesenler", al(icerik, "components", null))
  if bilesenler != null
    govde.components = bilesenler
  end
  # duz yazi
  yazi = al(icerik, "yazi", al(icerik, "content", null))
  if yazi != null
    govde.content = yazi
  end
  # API alanlari oldugu gibi gecer
  if has(icerik, "embeds")
    govde.embeds = icerik.embeds
    return govde
  end
  # gomulu kutu alanlari
  kutu = gomulu(icerik)
  if len(keys(kutu)) > 0
    govde.embeds = [kutu]
  end
  if len(keys(govde)) == 0
    return {content: metin(icerik)}
  end
  return govde
end

# ---------------------------------------------------------------- bilesenler
_BUTON_BICIMLERI = {
  mavi: 1, birincil: 1,
  gri: 2, ikincil: 2,
  yesil: 3, onay: 3,
  kirmizi: 4, tehlike: 4,
  baglanti: 5, link: 5
}

# Buton uretir.
#   jubbio.buton("Destek Ac", "ticket_ac", bicim: "yesil", emoji: "🎫")
func buton(etiket, kimlik = "", bicim = "gri", emoji = "", adres = "", kapali = false)
  bicim_no = al(_BUTON_BICIMLERI, bicim, 0)
  if bicim_no == 0
    hata("Bilinmeyen buton bicimi: " + bicim + " - secenekler: "
         + join(keys(_BUTON_BICIMLERI), ", "))
  end
  b = {type: 2, style: bicim_no, label: etiket}
  if adres != ""
    b.style = 5
    b.url = adres
  else
    b.custom_id = kimlik
  end
  if emoji != ""
    b.emoji = {name: emoji}
  end
  if kapali
    b.disabled = true
  end
  return b
end

# Bilesen satiri (en fazla 5 buton)
func satir(bilesenler)
  return {type: 1, components: bilesenler}
end

# Acilir menu.
#   jubbio.menu("sebep", [{etiket: "Spam", deger: "spam"}], yer_tutucu: "Sec")
func menu(kimlik, secenekler, yer_tutucu = "Sec...", en_az = 1, en_cok = 1)
  liste = []
  for s in secenekler
    oge = {label: al(s, "etiket", al(s, "label", "")),
           value: metin(al(s, "deger", al(s, "value", "")))}
    aciklama = al(s, "aciklama", "")
    if aciklama != ""
      oge.description = aciklama
    end
    emoji = al(s, "emoji", "")
    if emoji != ""
      oge.emoji = {name: emoji}
    end
    ekle(liste, oge)
  end
  return {type: 3, custom_id: kimlik, options: liste,
          placeholder: yer_tutucu, min_values: en_az, max_values: en_cok}
end

# Form icin metin kutusu
func metin_kutusu(kimlik, etiket, uzun = false, zorunlu = true, yer_tutucu = "")
  k = {type: 4, custom_id: kimlik, label: etiket, required: zorunlu}
  if uzun
    k.style = 2
  else
    k.style = 1
  end
  if yer_tutucu != ""
    k.placeholder = yer_tutucu
  end
  return {type: 1, components: [k]}
end

# ---------------------------------------------------------------- yardimcilar
# Gomulu (embed) kutusu yapar. Turkce alan adlarini API adlarina cevirir.
func gomulu(veri)
  kutu = {}
  if has(veri, "baslik")
    kutu.title = veri.baslik
  end
  if has(veri, "aciklama")
    kutu.description = veri.aciklama
  end
  if has(veri, "renk")
    kutu.color = _renk(veri.renk)
  end
  if has(veri, "resim")
    kutu.image = {url: veri.resim}
  end
  if has(veri, "kucuk_resim")
    kutu.thumbnail = {url: veri.kucuk_resim}
  end
  if has(veri, "alt_yazi")
    kutu.footer = {text: veri.alt_yazi}
  end
  if has(veri, "yazar")
    kutu.author = {name: veri.yazar}
  end
  if has(veri, "adres")
    kutu.url = veri.adres
  end
  if has(veri, "alanlar")
    kutu.fields = veri.alanlar
  end
  # API adlariyla verilenler oldugu gibi gecer
  for anahtar, deger in veri
    if not has(kutu, anahtar)
      if contains(["title", "description", "color", "image", "thumbnail", "footer", "author", "url", "fields", "timestamp"], anahtar)
        kutu[anahtar] = deger
      end
    end
  end
  return kutu
end

func _renk(deger)
  if type(deger) == "metin"
    ham = replace(deger, "#", "")
    return _onaltilik(ham)
  end
  return deger
end

func _onaltilik(ham)
  basamaklar = "0123456789abcdef"
  toplam = 0
  for harf in lower(ham)
    yer = find(basamaklar, harf)
    if yer < 0
      hata("Renk onaltilik olmali: " + ham)
    end
    toplam = toplam * 16 + yer
  end
  return toplam
end

# <@123> biciminde bahsetme
func bahset(kullanici)
  return "<@" + kullanici + ">"
end

# ---------------------------------------------------------------- mesajlar
func yolla(sunucu, kanal, icerik)
  return _istek("POST", _kanal_yolu(sunucu, kanal) + "/messages", _mesaj_govdesi(icerik))
end

# Sadece bir kisinin gordugu mesaj
func gizli_yolla(sunucu, kanal, kullanici, icerik)
  govde = _mesaj_govdesi(icerik)
  govde.flags = 64
  govde.target_user_id = kullanici
  return _istek("POST", _kanal_yolu(sunucu, kanal) + "/messages", govde)
end

func dm(kanal, icerik)
  return _istek("POST", "/bot/dm/" + kanal, _mesaj_govdesi(icerik))
end

func duzenle(sunucu, kanal, mesaj, icerik)
  return _istek("PATCH", _kanal_yolu(sunucu, kanal) + "/messages/" + mesaj,
                _mesaj_govdesi(icerik))
end

func mesaj_sil(sunucu, kanal, mesaj)
  return _istek("DELETE", _kanal_yolu(sunucu, kanal) + "/messages/" + mesaj)
end

func toplu_sil(sunucu, kanal, mesajlar)
  return _istek("POST", _kanal_yolu(sunucu, kanal) + "/messages/bulk-delete",
                {messages: mesajlar})
end

func mesajlar(sunucu, kanal, adet = 50)
  cevap = _istek("GET", _kanal_yolu(sunucu, kanal) + "/messages?limit=" + adet)
  if type(cevap) == "harita" and has(cevap, "messages")
    return cevap.messages
  end
  return cevap
end

func tepki_ekle(sunucu, kanal, mesaj, emoji)
  return _istek("PUT", _kanal_yolu(sunucu, kanal) + "/messages/" + mesaj
                + "/reactions/" + encode(emoji))
end

func tepki_sil(sunucu, kanal, mesaj, emoji)
  return _istek("DELETE", _kanal_yolu(sunucu, kanal) + "/messages/" + mesaj
                + "/reactions/" + encode(emoji))
end

func sabitle(sunucu, kanal, mesaj)
  return _istek("PUT", _kanal_yolu(sunucu, kanal) + "/pins/" + mesaj)
end

func sabit_kaldir(sunucu, kanal, mesaj)
  return _istek("DELETE", _kanal_yolu(sunucu, kanal) + "/pins/" + mesaj)
end

# ---------------------------------------------------------------- uyeler
func uye(sunucu, kullanici)
  return _istek("GET", _sunucu_yolu(sunucu) + "/members/" + kullanici)
end

func uyeler(sunucu, adet = 100)
  return _istek("GET", _sunucu_yolu(sunucu) + "/members?flat=true&limit=" + adet)
end

func at(sunucu, kullanici, sebep = "")
  yol = _sunucu_yolu(sunucu) + "/members/" + kullanici
  if sebep != ""
    yol = yol + "?reason=" + encode(sebep)
  end
  return _istek("DELETE", yol)
end

func yasakla(sunucu, kullanici, sebep = "", gun = 0)
  return _istek("PUT", _sunucu_yolu(sunucu) + "/bans/" + kullanici,
                {reason: sebep, delete_message_days: gun})
end

func yasak_kaldir(sunucu, kullanici, sebep = "")
  yol = _sunucu_yolu(sunucu) + "/bans/" + kullanici
  if sebep != ""
    yol = yol + "?reason=" + encode(sebep)
  end
  return _istek("DELETE", yol)
end

# saniye kadar susturur
func sustur(sunucu, kullanici, saniye, sebep = "")
  bitis = tarih(zaman() + saniye)
  return _istek("POST", _sunucu_yolu(sunucu) + "/members/" + kullanici + "/timeout",
                {until: bitis, reason: sebep})
end

func susturma_kaldir(sunucu, kullanici, sebep = "")
  return _istek("POST",
                _sunucu_yolu(sunucu) + "/members/" + kullanici + "/timeout/clear",
                {reason: sebep})
end

func rol_ver(sunucu, kullanici, rol)
  return _istek("PUT",
                _sunucu_yolu(sunucu) + "/members/" + kullanici + "/roles/" + rol)
end

func rol_al(sunucu, kullanici, rol)
  return _istek("DELETE",
                _sunucu_yolu(sunucu) + "/members/" + kullanici + "/roles/" + rol)
end

func uye_duzenle(sunucu, kullanici, veri)
  return _istek("PATCH", _sunucu_yolu(sunucu) + "/members/" + kullanici, veri)
end

# ---------------------------------------------------------------- sunucu
func sunucu(kimlik)
  return _istek("GET", _sunucu_yolu(kimlik))
end

func kanallar(sunucu)
  return _istek("GET", _sunucu_yolu(sunucu) + "/channels")
end

# Kanal acar.
#   jubbio.kanal_ac(sunucu, {ad: "destek-1", kategori: kat, izinler: [...]})
func kanal_ac(sunucu, veri)
  govde = {}
  ad = al(veri, "ad", al(veri, "name", ""))
  if ad != ""
    govde.name = ad
  end
  govde.type = al(veri, "tur", al(veri, "type", 0))
  kategori = al(veri, "kategori", al(veri, "category_id", null))
  if kategori != null
    govde.category_id = kategori
  end
  izinler = al(veri, "izinler", al(veri, "permission_overwrites", null))
  if izinler != null
    govde.permission_overwrites = izinler
  end
  return _istek("POST", _sunucu_yolu(sunucu) + "/channels", govde)
end

# Kanal acarken verilecek izin kaydi uretir
func izin_kaydi(kimlik_no, ver = null, engelle = null, uye_mi = false)
  tur_no = 0
  if uye_mi
    tur_no = 1
  end
  return {id: metin(kimlik_no), type: tur_no,
          allow: metin(izin(ver or [])), deny: metin(izin(engelle or []))}
end

func kanal_sil(sunucu, kanal)
  return _istek("DELETE", _kanal_yolu(sunucu, kanal))
end

func roller(sunucu)
  return _istek("GET", _sunucu_yolu(sunucu) + "/roles")
end

func rol_ac(sunucu, veri)
  return _istek("POST", _sunucu_yolu(sunucu) + "/roles", veri)
end

func rol_sil(sunucu, rol)
  return _istek("DELETE", _sunucu_yolu(sunucu) + "/roles/" + rol)
end

# ---------------------------------------------------------------- izinler
# Izin degerleri ikinin kuvvetleri; toplamak "veya" ile ayni sonucu verir.
IZINLER = {
  davet: 1,
  uye_at: 2,
  uye_yasakla: 4,
  yonetici: 8,
  kanal_yonet: 16,
  sunucu_yonet: 32,
  tepki_ekle: 64,
  kayit_gor: 128,
  kanali_gor: 1024,
  mesaj_yolla: 2048,
  mesaj_yonet: 8192,
  baglanti: 16384,
  dosya: 32768,
  gecmisi_oku: 65536,
  bahset: 524288,
  ses_baglan: 1048576,
  konus: 2097152,
  uye_sustur: 1099511627776,
  rol_yonet: 2199023255552
}

func izin(adlar)
  if type(adlar) != "liste"
    return adlar
  end
  toplam = 0
  for ad in adlar
    deger = al(IZINLER, ad, 0)
    if deger == 0
      hata("Bilinmeyen izin: " + ad + " - secenekler: " + join(keys(IZINLER), ", "))
    end
    toplam = toplam + deger
  end
  return toplam
end

# Uyenin izni var mi? (uye.permissions alanina bakar)
#   jubbio.izni_var(e.member, ["uye_at", "uye_yasakla"])
func izni_var(uye, adlar)
  ham = al(uye, "permissions", null)
  if ham == null
    return false
  end
  sahip = number(ham, 0)
  # yonetici her seyi yapabilir
  if _bit_var(sahip, 8)
    return true
  end
  if type(adlar) != "liste"
    return _bit_var(sahip, adlar)
  end
  # her izni ayri ayri kontrol et (birlesik maske yanlis sonuc verir)
  for ad in adlar
    if not _bit_var(sahip, al(IZINLER, ad, 0))
      return false
    end
  end
  return true
end

# TON'da bit isleci yok; bolme ile bakiyoruz
func _bit_var(deger, bit)
  if bit == 0
    return true
  end
  return (deger / bit) mod 2 >= 1
end

# Kanal izni ekler/degistirir.
#   jubbio.kanal_izni(kanal, rol, ver: ["kanali_gor"], engelle: [])
func kanal_izni(kanal, kimlik_no, ver = null, engelle = null, uye_mi = false)
  tur_no = 0
  if uye_mi
    tur_no = 1
  end
  return _istek("PUT", "/bot/channels/" + kanal + "/permissions/" + kimlik_no,
                {type: tur_no, allow: metin(izin(ver or [])),
                 deny: metin(izin(engelle or []))})
end

# ---------------------------------------------------------------- komutlar
func _uygulama_yolu(sunucu)
  if _ayar.uygulama == ""
    hata("Once uygulama kimligini ver: jubbio.giris(\"TOKEN\", \"UYGULAMA_ID\")")
  end
  yol = "/applications/" + _ayar.uygulama
  if sunucu != ""
    yol = yol + "/guilds/" + sunucu
  end
  return yol + "/commands"
end

func komut_ekle(komut, sunucu = "")
  return _istek("POST", _uygulama_yolu(sunucu), komut)
end

func komutlari_ayarla(komutlar, sunucu = "")
  return _istek("PUT", _uygulama_yolu(sunucu), komutlar)
end

func komutlar(sunucu = "")
  return _istek("GET", _uygulama_yolu(sunucu))
end

func komut_sil(komut, sunucu = "")
  return _istek("DELETE", _uygulama_yolu(sunucu) + "/" + komut)
end

# ---------------------------------------------------------------- slash komutlari
_SECENEK_TURLERI = {
  metin: 3,
  yazi: 3,
  sayi: 4,
  tam: 4,
  mantik: 5,
  kullanici: 6,
  kanal: 7,
  rol: 8,
  ondalik: 10
}

# Slash komutu tanimi uretir.
#   jubbio.komut("zar", "Zar atar", [{ad: "yuz", aciklama: "Kac yuzlu", tur: "sayi"}])
func komut(ad, aciklama, secenekler = null)
  tanim = {name: ad, description: aciklama, type: 1}
  if secenekler != null
    liste = []
    for s in secenekler
      tur_adi = al(s, "tur", "metin")
      tur_no = al(_SECENEK_TURLERI, tur_adi, 0)
      if tur_no == 0
        hata("Bilinmeyen secenek turu: " + tur_adi + " - secenekler: "
             + join(keys(_SECENEK_TURLERI), ", "))
      end
      ekle(liste, {
        name: s.ad,
        description: al(s, "aciklama", s.ad),
        type: tur_no,
        required: al(s, "zorunlu", false)
      })
    end
    tanim.options = liste
  end
  return tanim
end

# Etkilesimden komut adini alir
func komut_adi(etkilesim)
  return al(al(etkilesim, "data", {}), "name", "")
end

# Komuta verilen secenegi okur:  jubbio.secenek(e, "yuz", 6)
func secenek(etkilesim, ad, varsayilan = null)
  veri = al(etkilesim, "data", {})
  for s in al(veri, "options", [])
    if al(s, "name", "") == ad
      return al(s, "value", varsayilan)
    end
  end
  return varsayilan
end

# Etkilesim turu: "komut" | "dugme" | "form" | "otomatik"
func etkilesim_turu(etkilesim)
  tur_no = al(etkilesim, "type", 2)
  if tur_no == 3
    return "dugme"
  elif tur_no == 5
    return "form"
  elif tur_no == 4
    return "otomatik"
  end
  return "komut"
end

# Butona/menuye basildiginda: hangi kimlik?
func kimlik(etkilesim)
  return al(al(etkilesim, "data", {}), "custom_id", "")
end

# Menuden secilenler (liste)
func secilenler(etkilesim)
  return al(al(etkilesim, "data", {}), "values", [])
end

# Menuden secilen tek deger
func secilen(etkilesim, varsayilan = "")
  degerler = secilenler(etkilesim)
  if len(degerler) == 0
    return varsayilan
  end
  return degerler[0]
end

# Formdan gelen alan degeri
func form_degeri(etkilesim, kimlik_adi, varsayilan = "")
  veri = al(etkilesim, "data", {})
  for satir_ogesi in al(veri, "components", [])
    for alan in al(satir_ogesi, "components", [])
      if al(alan, "custom_id", "") == kimlik_adi
        return al(alan, "value", varsayilan)
      end
    end
  end
  return varsayilan
end

# Komutu kimin yazdigi
func kim(etkilesim)
  uye = al(etkilesim, "member", null)
  if uye != null
    kullanici = al(uye, "user", null)
    if kullanici != null
      return kullanici
    end
  end
  return al(etkilesim, "user", {})
end

# ---------------------------------------------------------------- etkilesim
# Slash komutuna cevap verir.
func cevapla(etkilesim, icerik, gizli = false)
  govde = _mesaj_govdesi(icerik)
  if gizli
    govde.flags = 64
  end
  return _istek("POST",
                "/interactions/" + etkilesim.id + "/" + etkilesim.token + "/callback",
                {type: 4, data: govde})
end

# "dusunuyor..." der, cevabi sonra duzenlersin
func dusun(etkilesim, gizli = false)
  govde = {}
  if gizli
    govde = {flags: 64}
  end
  return _istek("POST",
                "/interactions/" + etkilesim.id + "/" + etkilesim.token + "/callback",
                {type: 5, data: govde})
end

func cevap_duzenle(etkilesim, icerik)
  return _istek("PATCH",
                "/webhooks/" + _ayar.uygulama + "/" + etkilesim.token + "/messages/@original",
                _mesaj_govdesi(icerik))
end

# Butona basilan mesaji degistirir (yeni mesaj atmaz)
func guncelle(etkilesim, icerik)
  return _istek("POST",
                "/interactions/" + etkilesim.id + "/" + etkilesim.token + "/callback",
                {type: 7, data: _mesaj_govdesi(icerik)})
end

# Kullaniciya form (modal) gosterir
func form_goster(etkilesim, kimlik_adi, baslik, alanlar)
  return _istek("POST",
                "/interactions/" + etkilesim.id + "/" + etkilesim.token + "/callback",
                {type: 9, data: {custom_id: kimlik_adi, title: baslik,
                                 components: alanlar}})
end

func ek_cevap(etkilesim, icerik)
  return _istek("POST", "/webhooks/" + _ayar.uygulama + "/" + etkilesim.token,
                _mesaj_govdesi(icerik))
end

# ================================================================ gateway
# Gercek zamanli olaylar. WebSocket uzerinden calisir.
#
#   jubbio.dinle("mesaj", mesaj_gelince)
#   jubbio.calistir(["sunucular", "mesajlar", "icerik"])

_ag = {
  adres: "wss://realtime.jubbio.com/ws/bot",
  soket: null,
  sira: null,
  oturum: null,
  aralik: 30,
  calisiyor: false,
  ben: null,
  kayit: false,
  deneme: 0,
  en_fazla_deneme: 10
}

_dinleyiciler = {}

# TON adi -> gateway olay adi
_OLAYLAR = {
  hazir: "READY",
  mesaj: "MESSAGE_CREATE",
  mesaj_duzenlendi: "MESSAGE_UPDATE",
  mesaj_silindi: "MESSAGE_DELETE",
  mesajlar_silindi: "MESSAGE_DELETE_BULK",
  komut: "INTERACTION_CREATE",
  etkilesim: "_ETKILESIM",
  dugme: "_DUGME",
  form: "_FORM",
  sunucu_eklendi: "GUILD_CREATE",
  sunucu_guncellendi: "GUILD_UPDATE",
  sunucu_silindi: "GUILD_DELETE",
  uye_katildi: "GUILD_MEMBER_ADD",
  uye_ayrildi: "GUILD_MEMBER_REMOVE",
  uye_guncellendi: "GUILD_MEMBER_UPDATE",
  yasaklandi: "GUILD_BAN_ADD",
  yasak_kalkti: "GUILD_BAN_REMOVE",
  kanal_acildi: "CHANNEL_CREATE",
  kanal_guncellendi: "CHANNEL_UPDATE",
  kanal_silindi: "CHANNEL_DELETE",
  rol_acildi: "GUILD_ROLE_CREATE",
  rol_guncellendi: "GUILD_ROLE_UPDATE",
  rol_silindi: "GUILD_ROLE_DELETE",
  yaziyor: "TYPING_START",
  durum: "PRESENCE_UPDATE",
  davet: "INVITE_CREATE",
  ses: "VOICE_STATE_UPDATE",
  kapandi: "_KAPANDI",
  hata: "_HATA",
  ham: "_HAM"
}

_INTENTLER = {
  sunucular: 1,
  uyeler: 2,
  denetim: 4,
  emojiler: 8,
  entegrasyonlar: 16,
  webhooklar: 32,
  davetler: 64,
  sesler: 128,
  durumlar: 256,
  mesajlar: 512,
  tepkiler: 1024,
  yaziyor: 2048,
  dm: 4096,
  dm_tepkileri: 8192,
  dm_yaziyor: 16384,
  icerik: 32768,
  etkinlikler: 65536
}

# Bir olayi dinlemeye basla
func dinle(olay, is_)
  ad = al(_OLAYLAR, olay, "")
  if ad == ""
    ad = upper(olay)
  end
  if not has(_dinleyiciler, ad)
    _dinleyiciler[ad] = []
  end
  ekle(_dinleyiciler[ad], is_)
  return true
end

func olaylar()
  return keys(_OLAYLAR)
end

func intentler()
  return _INTENTLER
end

func _intent_hesapla(deger)
  if deger == null
    return 33281
  end
  if type(deger) != "liste"
    return deger
  end
  # Intent degerleri ikinin kuvvetleri oldugu icin toplamak "veya" ile aynidir
  toplam = 0
  for ad in deger
    bit = al(_INTENTLER, ad, 0)
    if bit == 0
      hata("Bilinmeyen intent: " + ad + " - secenekler: " + join(keys(_INTENTLER), ", "))
    end
    toplam = toplam + bit
  end
  return toplam
end

func _duyur(ad, veri)
  isler = al(_dinleyiciler, ad, [])
  for is_ in isler
    try
      is_(veri)
    catch mesaj
      print: [jubb] dinleyici hatasi (ad;): mesaj;
    end
  end
  return len(isler)
end

func _paket_isle(paket)
  # Sunucu tek cercevede birden cok JSON yollayabiliyor
  if type(paket) == "metin"
    for satir in split(paket, "\n")
      if trim(satir) != ""
        try
          _paket_isle(json(satir))
        catch
          _duyur("_HAM", satir)
        end
      end
    end
    return null
  end
  if type(paket) != "harita"
    return null
  end
  _duyur("_HAM", paket)
  if has(paket, "s")
    if paket.s != null
      _ag.sira = paket.s
    end
  end
  op = al(paket, "op", -1)
  if op == 0
    olay = al(paket, "t", "")
    veri = al(paket, "d", {})
    if olay == "READY"
      _ag.oturum = al(veri, "session_id", null)
      _ag.ben = al(veri, "user", null)
      _ag.deneme = 0
      # uygulama kimligi READY ile geliyorsa elle vermeye gerek yok
      uygulama = al(veri, "application", null)
      if uygulama != null and _ayar.uygulama == ""
        _ayar.uygulama = metin(al(uygulama, "id", ""))
      end
    end
    if olay == "MESSAGE_CREATE"
      veri = _mesaj_duzelt(veri)
    end
    if olay == "INTERACTION_CREATE"
      _duyur("_ETKILESIM", veri)
      alt_tur = etkilesim_turu(veri)
      if alt_tur == "dugme"
        _duyur("_DUGME", veri)
        return null
      elif alt_tur == "form"
        _duyur("_FORM", veri)
        return null
      end
    end
    _duyur(olay, veri)
  elif op == 10
    _ag.aralik = al(paket.d, "heartbeat_interval", 30000) / 1000
  elif op == 9
    if _ag.kayit
      print: [jubb] oturum gecersiz, yeniden kimlik gonderiliyor
    end
    wait(2)
    _kimlik_gonder()
  elif op == 7
    if _ag.kayit
      print: [jubb] sunucu yeniden baglanmamizi istedi
    end
    _ag.soket.kapat()
  end
  return null
end

# Sunucu yazari bazen ayri alanda yolluyor; tek bicime getirir.
func _mesaj_duzelt(m)
  yazar = al(m, "author", null)
  if yazar == null
    yazar = {}
    m.author = yazar
  end
  if al(yazar, "id", null) == null
    kimlik = al(m, "user_id", null)
    if kimlik != null
      yazar.id = kimlik
    end
  end
  m.kendim = benim_mi(m)
  return m
end

# Mesaj botun kendisinden mi geldi?  (sonsuz donguye girmemek icin)
func benim_mi(mesaj)
  if _ag.ben == null
    return false
  end
  yazar = al(mesaj, "author", null)
  if yazar == null
    return false
  end
  if al(yazar, "bot", false)
    return true
  end
  return metin(al(yazar, "id", "")) == metin(al(_ag.ben, "id", ""))
end

func _kimlik_gonder()
  _ag.soket.yolla({
    op: 2,
    d: {
      token: "Bot " + _ayar.token,
      intents: _ag.intents,
      shard: [0, 1]
    }
  })
  return true
end

func _kalp_dongusu()
  while _ag.calisiyor
    wait(_ag.aralik)
    if _ag.calisiyor
      try
        _ag.soket.yolla({op: 1, d: _ag.sira})
      catch
        return null
      end
    end
  end
  return null
end

# Gateway'e baglanir ve olaylari dinlemeye baslar.
# intentler: sayi ya da ad listesi -> ["sunucular", "mesajlar", "icerik"]
func calistir(intentler = null, yeniden_baglan = true)
  if _ayar.token == ""
    hata("Once jubbio.giris(\"BOT_TOKEN\") yazmalisin")
  end
  _ag.intents = _intent_hesapla(intentler)
  _ag.calisiyor = true

  while _ag.calisiyor
    try
      _bir_oturum()
    catch mesaj
      _duyur("_HATA", mesaj)
      if _ag.kayit
        print: [jubb] baglanti hatasi: mesaj;
      end
    end
    if not yeniden_baglan
      _ag.calisiyor = false
    end
    if _ag.calisiyor
      _ag.deneme += 1
      if _ag.deneme > _ag.en_fazla_deneme
        _ag.calisiyor = false
        hata("Gateway'e " + _ag.en_fazla_deneme + " denemede baglanilamadi")
      end
      gecikme = enkucuk(30, 2 ^ _ag.deneme)
      if _ag.kayit
        print: [jubb] gecikme; saniye sonra yeniden baglanilacak (_ag.deneme;)
      end
      wait(gecikme)
    end
  end
  return true
end

func _bir_oturum()
  if _ag.kayit
    print: [jubb] baglaniliyor: _ag.adres;
  end
  _ag.soket = connect(_ag.adres)

  # ilk paket Hello olmali
  ilk = _ag.soket.al(30)
  if ilk == null
    hata("Gateway 30 saniyede Hello yollamadi")
  end
  _paket_isle(ilk)
  _kimlik_gonder()
  asyn(_kalp_dongusu)

  while _ag.calisiyor
    paket = _ag.soket.al(60)
    if paket != null
      _paket_isle(paket)
    end
  end
  return true
end

# Botu durdurur
func dur()
  _ag.calisiyor = false
  if _ag.soket != null
    try
      _ag.soket.kapat()
    catch
      print: [jubb] soket zaten kapali
    end
  end
  return true
end

# Botun kendi kullanici bilgisi (READY sonrasi dolar)
func ben()
  return _ag.ben
end

func ag_ayarla(adres = "", kayit = null, en_fazla_deneme = null)
  if adres != ""
    _ag.adres = adres
  end
  if kayit != null
    _ag.kayit = kayit
  end
  if en_fazla_deneme != null
    _ag.en_fazla_deneme = en_fazla_deneme
  end
  return _ag
end
