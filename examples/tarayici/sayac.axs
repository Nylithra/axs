# Tarayicida calisan sayac.
#   ton paket examples/tarayici/sayac.ton
# Yanindaki sayac.govde.html sayfanin govdesi olur.

sayi = saklanan("sayi", 0)

func goster()
  yaz_metin("#sayi", sayi)
  sakla("sayi", sayi)
end

func arttir(olay)
  sayi += 1
  goster()
end

func azalt(olay)
  sayi -= 1
  goster()
end

func sifirla(olay)
  sayi = 0
  goster()
  print: sayac sifirlandi
end

tikla("#arttir", arttir)
tikla("#azalt", azalt)
tikla("#sifirla", sifirla)
goster()

print: Sayac hazir. Baslangic degeri: sayi;
