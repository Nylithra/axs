l = [3, 1, 2]
ekle(l, 4, 5)
print(l)
print(l.len(), l.sum(), l.avg(), min(l), max(l))
print(l.sort(), l.reverse(), l.unique())
print([1, 1, 2, 2].unique())
print(l.first(), l.last(), l.first(2), l.last(2))
print(l.contains(3), l.find(3))
print(range(5), range(2, 5), range(0, 10, 5))
print(zip([1, 2], ["a", "b"]))
print(flat([1, [2, [3]]]))

h = {ad: "Nyl", yas: 20}
print(h.keys(), h.values(), h.items())
print(h.has("ad"), h.get("yok", "varsayilan"))
h.set("sehir", "Ankara")
print(h)
h.remove("yas")
print(h)
print(merge({a: 1}, {b: 2}))

kisiler = [{ad: "a", yas: 30}, {ad: "b", yas: 20}, {ad: "c", yas: 30}]
print(sort(kisiler, "yas"))
print(group(kisiler, "ad"))
print(sum(kisiler, "yas"))
print(any([1, 2], func(x) -> x > 1), all([1, 2], func(x) -> x > 1))
print(shuffle([1]).len())
