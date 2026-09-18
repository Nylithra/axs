# Panel akisi: menu secimi, buton, form, izinli kanal acma
use jubbio

jubbio.giris("SAHTE_TOKEN")
jubbio.ag_ayarla(adres: env("SAHTE_GATEWAY"))
jubbio.ayarla(temel: env("SAHTE_REST"))

SUNUCU = 7
secilen_kategori = ""

func panel(sunucu)
  kanallar = jubbio.kanallar(sunucu)
  secenekler = []
  for k in kanallar
    if k.type == 4
      ekle(secenekler, {etiket: k.name, deger: metin(k.id)})
    end
  end
  return {baslik: "Ayarlar", aciklama: "kategori: " + secilen_kategori,
          renk: "#5865f2",
          bilesenler: [
            jubbio.satir([jubbio.menu("p_kategori", secenekler, yer_tutucu: "Sec")]),
            jubbio.satir([jubbio.buton("Ac", "p_ac", bicim: "yesil", emoji: "🎫")])
          ]}
end

func komut(e)
  print: komut: (jubbio.komut_adi(e));
  jubbio.cevapla(e, panel(SUNUCU), gizli: true)
end

func dugme(e)
  kimlik = jubbio.kimlik(e)
  print: dugme: kimlik;
  if kimlik == "p_kategori"
    secilen_kategori = jubbio.secilen(e)
    jubbio.guncelle(e, panel(SUNUCU))
  elif kimlik == "p_ac"
    jubbio.form_goster(e, "p_form", "Talep", [
      jubbio.metin_kutusu("konu", "Konu"),
      jubbio.metin_kutusu("aciklama", "Aciklama", uzun: true)
    ])
  end
end

func form(e)
  print: form: (jubbio.kimlik(e)); konu=(jubbio.form_degeri(e, "konu"));
  kisi = jubbio.kim(e)
  izinler = [
    jubbio.izin_kaydi(SUNUCU, [], ["kanali_gor"]),
    jubbio.izin_kaydi(kisi.id, ["kanali_gor", "mesaj_yolla", "gecmisi_oku"],
                    [], uye_mi: true)
  ]
  kanal = jubbio.kanal_ac(SUNUCU, {ad: "destek-1", kategori: secilen_kategori,
                                   izinler: izinler})
  jubbio.yolla(SUNUCU, kanal.id, {baslik: "Talep", aciklama: "acildi",
                                    renk: "#43b581",
                                    bilesenler: [jubbio.satir([
                                      jubbio.buton("Kapat", "p_kapat", bicim: "kirmizi")
                                    ])]})
  jubbio.cevapla(e, "kanal: " + kanal.id, gizli: true)
end

func katildi(veri)
  print: bot duruyor
  jubbio.dur()
end

jubbio.dinle("komut", komut)
jubbio.dinle("dugme", dugme)
jubbio.dinle("form", form)
jubbio.dinle("uye_katildi", katildi)
jubbio.calistir(["sunucular"], yeniden_baglan: false)
print: bitti
