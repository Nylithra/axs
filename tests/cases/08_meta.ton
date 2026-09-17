meta('gizli = 7')
print: %gizli%

meta('''
func ikikat(x)
  return %x% * 2
end
''')
print(ikikat(21))

define("uckat", ["x"], 'return %x% * 3')
print(uckat(5))

print(defined("uckat"), defined("olmayan"))
set_var("dinamik", 99)
print(get_var("dinamik"), get_var("yok", "varsayilan"))
print(call("uckat", [4]))
print(template('Merhaba %ad%, %(%yas% + 1)% yasina girdin', {ad: "Nyl", yas: 19}))
print(params(uckat))

kodlar = ["a = 1", "b = 2"]
for k in %kodlar%
  meta(%k%)
end
print(%a% + %b%)
