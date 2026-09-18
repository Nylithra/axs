# Slash komutlari: kayit + secenek okuma + cevap bicimleri
use jubbio

jubbio.giris("SAHTE_TOKEN")
jubbio.ag_ayarla(adres: env("SAHTE_GATEWAY"))
jubbio.ayarla(temel: env("SAHTE_REST"))

KOMUTLAR = [
  jubbio.komut("selam", "Selam verir"),
  jubbio.komut("topla", "Toplar", [
    {ad: "bir", aciklama: "Birinci", tur: "sayi", zorunlu: true},
    {ad: "iki", aciklama: "Ikinci", tur: "sayi", zorunlu: true}
  ]),
  jubbio.komut("yanki", "Geri soyler", [
    {ad: "metin", aciklama: "Yazi", tur: "metin", zorunlu: true}
  ])
]

func hazir(veri)
  print: HAZIR: %veri.user.username% / uygulama %(jubbio.ayar().uygulama)%
  jubbio.komutlari_ayarla(%KOMUTLAR%, 7)
  print: %(len(%KOMUTLAR%))% komut kaydedildi
end

func slash(e)
  ad = jubbio.komut_adi(%e%)
  kisi = jubbio.kim(%e%)
  print: /%ad% <- %kisi.username%

  if %ad% == "selam"
    jubbio.cevapla(%e%, "Selam " + jubbio.bahset(%kisi.id%) + "!")
  elif %ad% == "topla"
    bir = jubbio.secenek(%e%, "bir", 0)
    iki = jubbio.secenek(%e%, "iki", 0)
    jubbio.cevapla(%e%, %bir% + " + " + %iki% + " = " + (%bir% + %iki%))
  elif %ad% == "yanki"
    jubbio.cevapla(%e%, {baslik: "Yanki", aciklama: jubbio.secenek(%e%, "metin", ""),
                       renk: "#2f6fed"})
  else
    jubbio.cevapla(%e%, "bilmiyorum", gizli: true)
  end
  return null
end

func katildi(veri)
  print: bot duruyor
  jubbio.dur()
end

jubbio.dinle("hazir", hazir)
jubbio.dinle("komut", slash)
jubbio.dinle("uye_katildi", katildi)

jubbio.calistir(["sunucular"], yeniden_baglan: false)
print: bitti
