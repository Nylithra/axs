# Es zamanli calisma: asyn() baslatir, wait() bekler.

func uzun_is(ad, sure)
  wait(sure)
  return ad + " bitti"
end

baslangic = timestamp()

g1 = asyn(uzun_is, "birinci", 0.3)
g2 = asyn(uzun_is, "ikinci", 0.3)
g3 = asyn(uzun_is, "ucuncu", 0.3)

print: Uc is ayni anda basladi...

print: (wait(g1));
print: (wait(g2));
print: (wait(g3));

gecen = timestamp() - baslangic
print: Toplam sure: (round(gecen, 2)); saniye (sirayla olsaydi 0.9 olurdu)

# adresleri ayni anda cekmek:
# gorevler = [asyn(https://ornek.com/1), asyn(https://ornek.com/2)]
# print(waitall(gorevler))
