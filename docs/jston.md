# jston — JavaScript'ten Axs'a

Elindeki JavaScript kodunu Axs kaynağına çevirir.

```bash
axs cevir hesap.js              # -> hesap.axs
axs cevir hesap.js -o yeni.axs
axs cevir hesap.js -o -         # ekrana yaz
```

```js
// hesap.js
function topla(a, b = 2) {
  return a + b;
}
const kare = (x) => x * x;
console.log(`sonuç: ${topla(3)} ve ${kare(5)}`);
```

```axs
# hesap.axs
func topla(a, b = 2)
  return (a + b)
end
func kare(x)
  return (x * x)
end
print("sonuç: (topla(3)); ve (kare(5));")
```

---

## Ne çevriliyor

| JavaScript | Axs |
|---|---|
| `var` · `let` · `const` | doğrudan atama |
| `function f(a, b = 1)` | `func f(a, b = 1)` |
| `(x) => x * 2` | `func(x) -> x * 2` |
| çok satırlı ok işi | kullanıldığı yerin üstüne ayrı `func` |
| `class` | nesne üreten iş (`_bu` haritası) |
| `new Foo(x)` | `Foo(x)` |
| `if / else if / else` | `if / elif / else` |
| `for (let i=0; i<n; i++)` | `for i in range(0, n - 1)` |
| `for (const x of l)` | `for x in l` |
| `for (const k in o)` | `for k in keys(o)` |
| `while` · `do...while` | `while` · `while true` + `stop` |
| `break` · `continue` | `stop` · `skip` |
| `switch` | `if / elif / else` zinciri |
| `try / catch / finally` | `try / catch` (finally sonrasına taşınır) |
| `throw new Error(m)` | `hata(m)` |
| `a ? b : c` | `_ucluk(a, func() -> b, func() -> c)` (tembel) |
| `` `a ${b}` `` | `"a (b);"` |
| `&&` `\|\|` `!` `%` `**` | `and` `or` `not` `mod` `^` |
| `===` `!==` | `==` `!=` |
| `const [a, b] = l` | `a = l[0]` · `b = l[1]` |
| `const {a} = o` | `a = o.a` |
| `a = b = 5` | iki ayrı satır |

**Hazır işler:** `console.log` → `print`, `Math.*` → `asagi/yukari/yuvarla/...`,
`JSON.stringify/parse` → `tojson/json`, `Object.keys/values/entries` →
`keys/values/items`, `parseInt/Number/String` → `tam/sayi/metin`,
`setTimeout` → `after`, `fetch` → `get`, `document.querySelector` → `oge`.

**Yöntemler:** `.length` → `len(...)`, `.push/.pop/.slice/.join/.includes/.indexOf/
.map/.filter/.reduce/.forEach/.toUpperCase/.trim/.split/.replace/.startsWith` hepsi
Axs karşılıklarına gider.

---

## Dikkat edilen üç ince nokta

**1. `a ? b : c` tembel çevrilir.** İki dal da iş içine sarılır, sadece seçilen dal
çalışır. Yoksa `n <= 1 ? 1 : n * fakt(n-1)` sonsuz özyinelemeye girerdi.

**2. `reverse()` ve `sort()` yerinde değiştirir.** JavaScript'te bu ikisi listenin
kendisini değiştirir, Axs'da yeni liste döner. Çevirici `_yerinde_koy()` yardımcısıyla
JS davranışını korur. `sort((a,b) => a-b)` ve `sort((a,b) => b.x-a.x)` gibi yaygın
karşılaştırıcılar Axs'un `sort(liste, "alan", tersten: true)` biçimine çevrilir.

**3. `replace()` sadece ilk eşleşmeyi değiştirir.** Axs'un `replace`'i hepsini
değiştirdiği için çeviride `, 1` eklenir. `replaceAll` olduğu gibi kalır.

---

## Çevrilemeyenler

Çevrilemeyen her yer çıktıda `# TODO:` satırı olur ve dosyanın başında listelenir:

```
# ------------------------------------------------------------
# jston: 2 yer elle gozden gecirilmeli:
#   - satir 12: bit islemi '&' Axs'da yok
#   - satir 31: 'extends' (kalitim) Axs'da yok
# ------------------------------------------------------------
```

| Çevrilmeyen | Neden |
|---|---|
| Bit işlemleri `& \| ^ << >> ~` | Axs'da yok (`^` üs almadır) |
| `class ... extends` | Axs'da kalıtım yok |
| `...` (yayılım, kalan parametre) | Axs'da yok |
| `Map` · `Set` · `Symbol` · üreteçler | Axs'da yok |
| Düzenli ifadeler | desen metne çevrilir, `match`/`matches` ile kullanılır |
| `import` · `export` · `require` | yorum satırı olur; Axs'da `use "dosya.axs"` |
| Etiketler (`dis:` `break dis`) | Axs'da yok |
| `instanceof` | Axs'da yok, `type()` ile karşılaştır |

**Anlamı değişenler:**

- `typeof x` → `type(x)`; tür adları Axs'da Türkçe (`metin`, `sayi`, `bool`,
  `liste`, `harita`, `null`).
- `??` → `or`; JavaScript sadece `null`/`undefined`'da sağa geçer, Axs boş olan
  her değerde.
- `switch` içinde alt dala düşme (fallthrough) yoktur; `break`siz dal uyarı verir.

---

## Doğruluk nasıl sınanıyor

`tests/jston/` içindeki her JavaScript programı hem `node` ile hem de Axs'a
çevrilip `axs` ile çalıştırılır; **çıktıların bayt bayt aynı olması** beklenir.

```bash
python3 tests/run_tests.py
```

Bu yüzden çevirinin doğruluğu iddia değil, ölçülen bir şeydir.
