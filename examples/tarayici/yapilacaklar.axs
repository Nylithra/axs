# Tarayicida calisir; verileri sunucudan alir.
# get()/post() burada fetch'e donusur ama kod yine duz ve senkron gorunur.

func ciz(ogeler)
  satirlar = ""
  for oge in ogeler
    satirlar = satirlar + "<li>" + oge + "</li>"
  end
  yaz_ic("#liste", satirlar)
  yaz_metin("#durum", "Toplam " + len(ogeler) + " is")
end

func yenile()
  ciz(get("/api/notlar"))
end

func gonder(olay)
  metin = deger("#metin")
  if metin == ""
    return null
  end
  ogeler = post("/api/ekle", {metin: metin})
  deger("#metin", "")
  ciz(ogeler)
end

gonderim("#form", gonder)
yenile()

print: Uygulama hazir
