# TON'a hosgeldin!  Calistirmak icin:  ton examples/main.ton

ad = "Dunya"

print: Merhaba ad;!

# --- degiskenler her zaman ad ile okunur ---
sayi = 42
ondalik = 3.14
liste = ["ton", "tn", "nyl", "tnl"]
kisi = {ad: "Nyl", yas: 20}

print: Sayi: sayi;, ondalik: ondalik;
print: Uzantilar: liste;
print: Kisi: kisi.ad; (kisi.yas;)

# --- hesap yapmak icin %( ... )% ---
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
  print: .%uzanti% dosyalari calisir
end

# --- isler ---
func selamla(kisi, selam = "Merhaba")
  return selam + ", " + kisi + "!"
end

print: (selamla("TON"));
print: (selamla("Nyl", "Selam"));
