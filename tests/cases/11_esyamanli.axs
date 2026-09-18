func yavas(n)
  wait(0.05)
  return %n% * 10
end

g = asyn(yavas, 5)
print: gorev basladi
print(wait(%g%))
print(%g%.done())

gorevler = [asyn(yavas, 1), asyn(yavas, 2)]
print(waitall(%gorevler%))
print(parallel([yavas, yavas], 3))

sayac = 0
func arttir()
  sayac += 1
end
g2 = after(0.05, arttir)
wait(%g2%)
print: sayac %sayac%

print(timeout(2, yavas, 7))
try
  timeout(0.01, yavas, 1)
catch mesaj
  print: %mesaj%
end
