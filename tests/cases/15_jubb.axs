# jubb kutuphanesi: her cagrinin dogru yontem/yol/govde urettigini dogrular.
# Gercek Jubbio'ya cikmadan, yerel sahte sunucuyla sinanir.

use web
use jubbio

func yanki(istek)
  return {yontem: %istek.yontem%, yol: %istek.yol%,
          sorgu: %istek.sorgu%, govde: %istek.govde%}
end

func yetkisiz(istek)
  return web.json({error: "bad token"}, 401)
end

web.api("/yanki/*", yanki)
web.api("/kizgin/*", yetkisiz)
web.start(8155)
wait(0.3)

jubbio.giris("GIZLI_TOKEN", "UYG1")
jubbio.ayarla(temel: "http://127.0.0.1:8155/yanki")

func g(cevap)
  satir = %cevap.yontem% + " " + %cevap.yol%
  if len(%cevap.sorgu%) > 0
    satir = %satir% + " ?" + tojson(%cevap.sorgu%)
  end
  if %cevap.govde% != ""
    satir = %satir% + " " + %cevap.govde%
  end
  print: %satir%
end

print: --- mesajlar ---
g(jubbio.yolla(7, 9, "Merhaba!"))
g(jubbio.yolla(7, 9, {baslik: "Basluk", aciklama: "Aciklama", renk: "#2f6fed"}))
g(jubbio.gizli_yolla(7, 9, 42, "sadece sen"))
g(jubbio.dm(3, "ozel"))
g(jubbio.duzenle(7, 9, 100, "yeni"))
g(jubbio.mesaj_sil(7, 9, 100))
g(jubbio.toplu_sil(7, 9, [1, 2]))
g(jubbio.mesajlar(7, 9, 5))
g(jubbio.tepki_ekle(7, 9, 100, "👍"))
g(jubbio.tepki_sil(7, 9, 100, "👍"))
g(jubbio.sabitle(7, 9, 100))

print: --- uyeler ---
g(jubbio.uye(7, 42))
g(jubbio.uyeler(7, 10))
g(jubbio.at(7, 42, "kural ihlali"))
g(jubbio.yasakla(7, 42, "spam", 1))
g(jubbio.yasak_kaldir(7, 42))
g(jubbio.susturma_kaldir(7, 42, "affedildi"))
# sustur: bitis zamani her calisista degisir, sadece alan adlarina bakiyoruz
sonuc = jubbio.sustur(7, 42, 600, "sakin ol")
print: %sonuc.yontem% %sonuc.yol% alanlar=%(join(keys(json(%sonuc.govde%)), ","))%
g(jubbio.rol_ver(7, 42, 5))
g(jubbio.rol_al(7, 42, 5))
g(jubbio.uye_duzenle(7, 42, {nick: "yeni ad"}))

print: --- sunucu ---
g(jubbio.sunucu(7))
g(jubbio.kanallar(7))
g(jubbio.kanal_ac(7, {name: "genel"}))
g(jubbio.kanal_sil(7, 9))
g(jubbio.roller(7))
g(jubbio.rol_ac(7, {name: "uye"}))
g(jubbio.rol_sil(7, 5))

print: --- komutlar ---
g(jubbio.komut_ekle({name: "selam", description: "Selam verir"}))
g(jubbio.komut_ekle({name: "selam"}, 7))
g(jubbio.komutlar())
g(jubbio.komutlari_ayarla([{name: "a"}]))
g(jubbio.komut_sil(11, 7))

print: --- etkilesim ---
etkilesim = {id: 55, token: "TKN"}
g(jubbio.cevapla(%etkilesim%, "cevap"))
g(jubbio.cevapla(%etkilesim%, "gizli cevap", gizli: true))
g(jubbio.dusun(%etkilesim%))
g(jubbio.cevap_duzenle(%etkilesim%, "duzeltildi"))
g(jubbio.ek_cevap(%etkilesim%, "ek"))

print: --- hatalar ---
jubbio.ayarla(temel: "http://127.0.0.1:8155/kizgin")
try
  jubbio.yolla(7, 9, "olmaz")
catch m
  print: %m%
end

jubbio.giris("")
try
  jubbio.sunucu(7)
catch m
  print: %m%
end

web.stop()
