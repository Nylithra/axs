func selamla(ad, selam = "Merhaba")
  return %selam% + ", " + %ad% + "!"
end
print(selamla("Nyl"))
print(selamla("TON", "Selam"))
print(selamla(selam: "Hey", ad: "Dil"))

func faktoriyel(n)
  if %n% <= 1
    return 1
  end
  return %n% * faktoriyel(%n% - 1)
end
print(faktoriyel(10))

# is degeri olarak
func iki_kat(x) -> %x% * 2
print(map([1, 2, 3], iki_kat))
print(map([1, 2, 3], func(x) -> %x% + 100))
print(filter([1, 2, 3, 4, 5], func(x) -> %x% mod 2 == 1))
print(reduce([1, 2, 3, 4], func(t, x) -> %t% + %x%, 0))
print(sort([3, 1, 2]), sort([3, 1, 2], tersten: true))
print(sort([{ad: "b", n: 2}, {ad: "a", n: 1}], "ad"))

# kapsam
sayac = 0
func arttir()
  sayac += 1
  return %sayac%
end
arttir()
arttir()
print: sayac %sayac%

# deger dondurmeyen is
func sessiz()
  x = 1
end
print(sessiz())
