# Axs'e hosgeldin!  Calistirmak icin:  axs examples/main.axs

ad = "Dunya"

print: Merhaba ad;!

# --- yazi icinde degisken okumak icin  ad;  ---
sayi = 42
ondalik = 3.14
liste = ["axs", "nyl"]
kisi = {ad: "Nyl", yas: 20}

print: Sayi: sayi;, ondalik: ondalik;
print: Uzantilar: liste;
print: Kisi: kisi.ad; (kisi.yas;)

# --- yazi icinde hesap yapmak icin  (ifade);  ---
print: Iki kati: (sayi * 2);

# --- kosullar ---
if sayi > 40
  print: Sayi buyuk
else
  print: Sayi kucuk
end

# --- donguler ---
repeat 3 as i
  print: i;. tekrar
end

for uzanti in liste
  print: ("." + uzanti); dosyalari calisir
end

# --- isler ---
func selamla(kisi, selam = "Merhaba")
  return selam + ", " + kisi + "!"
end

print: (selamla("Axs"));
print: (selamla("Nyl", "Selam"));
