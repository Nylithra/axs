# Axs Dil Kılavuzu

Axs'un tamamı bu sayfada. Dilde toplam **14 anahtar kelime** var; gerisi hazır işlerdir.

---

## 1. Temel kural: düz ad, yazının içinde `ad;`

Bir değişkeni **tanımlarken de okurken de** düz adını yazarsın.

```axs
ad = "Nyl"
yas = 20

print(ad, yas)
```

Bir **yazının** içinde (şablonda ya da `"..."` içinde) değişkenin nerede
bittiğini söylemek gerekir; onun için sonuna `;` koyarsın:

```axs
print: Merhaba ad;, yaşın yas;.
```

```
Merhaba Nyl, yaşın 20.
```

Nokta ve köşeli parantez de `;`den önce gelebilir: `kisi.ad;` · `liste[0];`

Çıplak bir ad önce değişkenlere, sonra hazır işlere bakar:

```axs
topla(1, 2)     # topla bir iş
liste = topla   # değişkene atanmış olsaydı önce o bulunurdu
```

### Eski `%ad%` yazımı

`%ad%` hâlâ çalışır ve iki yerde gereklidir:

**1.** `ad;` yazımı, öncesinde harf/rakam ya da `. _ / : % \` varken okunmaz —
yol ve adreslerin bozulmaması için. Oralarda `%ad%` kullan:

```axs
kanal = "genel"
print: /%kanal%/mesaj        # -> /genel/mesaj
```

**2.** Adı anahtar kelimeyle çakışan değişkenler (`son`, `boş`, `dur` ...)
çıplak yazılamaz:

```axs
son = 5
print: %son%
```

---

## 2. Değerler

| Tür | Örnek |
|---|---|
| metin | `"merhaba"` · `'ham metin'` · `"""çok satırlı"""` |
| sayı | `42` · `-7` · `1_000_000` |
| ondalık | `3.14` |
| bool | `true` / `false` (`doğru` / `yanlış`) |
| boş | `null` (`boş`, `yok`) |
| liste | `[1, 2, 3]` |
| harita | `{ad: "Nyl", yas: 20}` |
| adres | `https://api.lanux.online` (tırnaksız yazılabilir) |

### Metin türleri

```axs
ad = "Nyl"

print("Merhaba ad;")     # -> Merhaba Nyl     (çift tırnak: değişken okur)
print('Merhaba ad;')     # -> Merhaba ad;    (tek tırnak: ham metin)

uzun = """
Birden çok
satır
"""
```

> `print:` şablonunda tırnaklar düz metindir — orada değişken her hâlükârda
> `ad;` ile okunur. Ham metin istiyorsan `print('...')` biçimini kullan.

Kaçışlar: `\n` `\t` `\\` `\"` `\%` `\;` — metinde tek `%` yazmak için `%%`,
değişkene dönüşmesin diye noktalı virgülden kaçmak için `\;`.

### Liste ve harita

```axs
liste = [10, 20, 30]
print: liste[0];      # 10
print: liste[-1];     # 30

kisi = {ad: "Nyl", yas: 20, diller: ["axs", "nyl"]}
print: kisi.ad;           # Nyl
print: kisi["yas"];       # 20
print: kisi.diller[1];    # nyl

kisi.set("şehir", "Ankara")
liste[0] = 99
```

---

## 3. Yazdırma

```axs
print: düz metin ve degisken;        # şablon biçimi
print("değer:", 42)                   # iş biçimi, virgülle ayırır
write("satır sonu yok")
```

Şablonun içinde hesap: `(ifade);`

```axs
print: Toplam (2 + 3); — büyük harf (upper(ad));
```

Genel kural: satır başında **`ad: metin`** yazarsan, o iş metinle çağrılır.
`print:` bunun bir örneğidir.

---

## 4. İşlemler

```
+   -   *   /   ^   mod        # toplama ... üs alma, kalan
==  !=  <   >   <=  >=         # karşılaştırma
and or  not                    # mantık  (ve / veya / değil)
```

- `+` metinlerde birleştirir: `"a" + 1` → `a1`
- `+` listelerde ve haritalarda birleştirir
- `*` metni tekrarlar: `"ab" * 3`
- `/` sıfıra bölmede hata verir
- `^` sağdan birleşir: `2 ^ 3 ^ 2` = 512

**Doğruluk kuralı:** boş olan her şey yanlıştır — `0`, `""`, `[]`, `{}`, `null`.

Kısa atama: `+=` `-=` `*=` `/=`

---

## 5. Koşullar

```axs
if puan >= 90
  print: AA
elif puan >= 70
  print: BB
else
  print: FF
end
```

---

## 6. Döngüler

```axs
repeat 3
  print: selam
end

repeat 5 as i           # i: 1, 2, 3, 4, 5
  print: i;
end

for oge in liste
  print: oge;
end

for anahtar, deger in harita
  print: anahtar; = deger;
end

while sayac < 10
  sayac += 1
end
```

`stop` döngüyü kırar, `skip` sıradakine geçer. (`dur` / `atla`)

---

## 7. İşler (fonksiyonlar)

```axs
func selamla(ad, selam = "Merhaba")
  return selam + ", " + ad
end

print: (selamla("Nyl"));
print: (selamla(selam: "Selam", ad: "Axs"));     # isimle çağırma
```

Tek satırlık iş:

```axs
func iki_kat(x) -> x * 2
```

İşler birer değerdir; başka işe verilebilir:

```axs
print(map([1, 2, 3], iki_kat))
print(filter([1, 2, 3, 4], func(x) -> x mod 2 == 0))
print(reduce([1, 2, 3], func(toplam, x) -> toplam + x, 0))
```

Bir işin içinde dışarıdaki değişkene yazarsan, dışarıdaki değişken değişir:

```axs
sayac = 0
func arttir()
  sayac += 1
end
```

---

## 8. Hatalar

```axs
try
  riskli_is()
catch mesaj
  print: hata oldu: mesaj;
end
```

`catch` adı yazılmazsa hata metni `hata` değişkenindedir.
Kendi hatanı fırlatmak için: `hata("mesaj")`

---

## 9. Başka dosyayı kullanma

```axs
use "yardimci.axs"        # içindeki her şey buraya gelir
use "yardimci" as yar     # ad altında toplanır -> yar.alan(2)
use web                   # kütüphane yükler
```

---

## 10. Anahtar kelimeler

| Axs | Türkçe karşılığı |
|---|---|
| `if` / `elif` / `else` | `eğer` / `yoksa` / `değilse` |
| `end` | `bitir` |
| `while` | `sürece` |
| `repeat` | `tekrar` |
| `for` / `in` | `her` / `içinde` |
| `func` | `iş`, `fonksiyon` |
| `return` | `döndür` |
| `stop` / `skip` | `dur` / `atla` |
| `try` / `catch` | `dene` / `yakala` |
| `use` | `kullan` |
| `and` / `or` / `not` | `ve` / `veya` / `değil` |
| `mod` | `kalan` |
| `true` / `false` / `null` | `doğru` / `yanlış` / `boş` |

İkisi de geçerlidir; istediğini kullan.

```axs
eğer yas > 18
  yaz: yetişkin
bitir
```

---

## 11. Yorumlar

```axs
# bu bir yorum
a = 1    # satır sonunda da olur
```

---

## 12. Sık düşülen üç tuzak

```axs
print: 2 + 3          # -> "2 + 3"   (print: düz metin yazar)
print: (2 + 3);      # -> 5         (yazının içinde hesap)

print(a)              # HATA: 'a' bir değişken; a yazmalısın
print(a)            # doğru

define("f", ["x"], "return x;")    # x burada hemen okunur -> hata
define("f", ["x"], 'return x')      # tek tırnak: kod ham kalır
```
