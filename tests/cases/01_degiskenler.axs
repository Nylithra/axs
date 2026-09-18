ad = "Nyl"
yas = 20
boy = 1.78
aktif = true
yokdeger = null

print: ad; - yas; - boy; - aktif; - yokdeger;
print: tur: (type(ad)); (type(yas)); (type(boy)); (type(aktif)); (type(yokdeger));

kisi = {ad: "Nyl", yas: 20, diller: ["axs", "nyl"]}
print: kisi.ad; kisi.yas; kisi.diller[0];
print: kisi["ad"];

liste = [10, 20, 30]
i = 1
print: liste[0]; liste[i]; liste[-1];

yas = yas + 1
print: yeni yas yas;
sayac = 0
sayac += 5
sayac -= 2
print: sayac sayac;

metin_ici = "Merhaba ad;, (yas * 2); yasinda gibisin"
print: metin_ici;
ham = 'burada %ad% degismez'
print: ham;
print: yuzde %% isareti
