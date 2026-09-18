# Jubbio bot ornegi (REST tarafi).
#   JUBB_TOKEN=... ton examples/jubb_bot.ton
#   ton examples/jubb_bot.ton BOT_TOKEN UYGULAMA_ID
#
# Gercek zamanli olay dinleme (gateway) WebSocket ister; o ayri gelecek.
# Buradaki her sey bugun calisir.

use jubbio

token = al(_argv, 0, env("JUBB_TOKEN"))
if token == ""
  print: Kullanim: ton examples/jubb_bot.ton BOT_TOKEN [UYGULAMA_ID]
  print: (ya da sunucu/kanal kimliklerini asagidan degistir)
  exit(0)
end

uygulama = al(_argv, 1, env("JUBB_UYGULAMA"))

# Yerel sahte sunucuyla denemek icin:  JUBB_TEMEL=http://127.0.0.1:8080/api
temel = env("JUBB_TEMEL")
if temel != ""
  jubbio.ayarla(temel: temel)
end

jubbio.giris(token, uygulama)
jubbio.ayarla(kayit: true)        # her istegi ekrana yaz

SUNUCU = 1
KANAL = 1

# --- duz mesaj ---
jubbio.yolla(SUNUCU, KANAL, "Merhaba! Ben TON ile yazildim.")

# --- gomulu (embed) mesaj ---
jubbio.yolla(SUNUCU, KANAL, {
  baslik: "TON Dili",
  aciklama: "Bu mesaji yollayan bot TON ile yazildi.",
  renk: "#2f6fed",
  alt_yazi: "tonjubb"
})

# --- son mesaji oku ---
son_mesajlar = jubbio.mesajlar(SUNUCU, KANAL, 5)
print: Son (len(son_mesajlar)); mesaj alindi

# --- sunucu bilgisi ---
kanallar = jubbio.kanallar(SUNUCU)
print: Kanal sayisi: (len(kanallar));

# --- slash komutu kaydet (uygulama kimligi gerekir) ---
if uygulama != ""
  jubbio.komutlari_ayarla([
    {name: "selam", description: "Selam verir"},
    {name: "zar", description: "Zar atar"}
  ], SUNUCU)
  print: Komutlar kaydedildi
end

# --- basit bir komut isleyici (gateway gelince dogrudan baglanacak) ---
func komut_islet(etkilesim)
  ad = etkilesim.data.name
  if ad == "selam"
    jubbio.cevapla(etkilesim, "Selam " + jubbio.bahset(etkilesim.user.id) + "!")
  elif ad == "zar"
    jubbio.cevapla(etkilesim, "Zar: " + random(1, 6))
  else
    jubbio.cevapla(etkilesim, "Bilmedigim bir komut", gizli: true)
  end
end

print: Hazir.
