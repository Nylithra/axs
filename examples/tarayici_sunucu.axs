# Tarayici tarafi + sunucu birlikte.
#   axs examples/tarayici_sunucu.axs   ->  http://localhost:8080

use web

# Sunucudaki veri
notlar = ["Axs'i dene", "axsweb ile site yap"]

func liste(istek)
  return notlar
end

func yeni_not(istek)
  metin = istek.veri.metin
  if metin
    ekle(notlar, metin)
  end
  return notlar
end

web.api("/api/notlar", liste)
web.post("/api/ekle", yeni_not)

# Tarayicida calisan Axs uygulamasi
web.uygulama("/", "tarayici/yapilacaklar.axs", baslik: "Axs Yapilacaklar")

web.serve(8080)
