# Buyuk veri: dosya satir satir okunur, bellege sigmasi gerekmez.

save("satis.csv", """urun,adet,tutar
kalem,3,30
defter,1,45
silgi,10,20
kalem,2,20
defter,4,180
""")

v = data("satis.csv")

print: Satir sayisi : %(%v%.count())%
print: Toplam tutar : %(%v%.sum("tutar"))%
print: Ortalama adet: %(%v%.avg("adet"))%
print: En yuksek    : %(%v%.max("tutar"))%
print: Urun sayilari: %(%v%.group("urun"))%
print: Urun cirolari: %(%v%.totals("urun", "tutar"))%
print: En iyi 2     : %(%v%.top(2, "tutar"))%

buyuk = %v%.filter(func(s) -> %s.tutar% >= 45)
print: 45 ve ustu   : %(%buyuk%.column("urun"))%

%buyuk%.save("buyuk_satislar.json")
print: Kaydedildi -> buyuk_satislar.json

delete("satis.csv")
delete("buyuk_satislar.json")
