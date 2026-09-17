# TON Dil Kılavuzu

TON'un tamamı bu sayfada. Dilde toplam **14 anahtar kelime** var; gerisi hazır işlerdir.

---

## 1. Temel kural: `%ad%`

Bir değişkeni **tanımlarken** düz adını, **okurken** `%ad%` yazarsın.

```ton
ad = "Nyl"
yas = 20

print: %ad% %yas%
```

Bu kural sayesinde karışıklık olmaz: çıplak bir ad her zaman bir **iş**tir,
`%ad%` her zaman bir **değişken**dir.

```ton
topla(1, 2)     # topla bir iş
%topla%         # topla adında bir değişken
```

Anahtar kelimeye benzeyen adları da değişken yapabilirsin, çünkü okurken zaten `%...%` var:

```ton
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

```ton
ad = "Nyl"

print: "Merhaba %ad%"      # -> Merhaba Nyl      (çift tırnak: değişken okur)
print: 'Merhaba %ad%'      # -> Merhaba %ad%     (tek tırnak: ham metin)

uzun = """
Birden çok
satır
"""
```

Kaçışlar: `\n` `\t` `\\` `\"` `\%` — metinde tek `%` yazmak için `%%`.

### Liste ve harita

```ton
liste = [10, 20, 30]
print: %liste[0]%      # 10
print: %liste[-1]%     # 30

kisi = {ad: "Nyl", yas: 20, diller: ["ton", "tnl"]}
print: %kisi.ad%           # Nyl
print: %kisi["yas"]%       # 20
print: %kisi.diller[1]%    # tnl

%kisi%.set("şehir", "Ankara")
liste[0] = 99
```

---

## 3. Yazdırma

```ton
print: düz metin ve %degisken%        # şablon biçimi
print("değer:", 42)                   # iş biçimi, virgülle ayırır
write("satır sonu yok")
```

Şablonun içinde hesap: `%( ... )%`

```ton
print: Toplam %(2 + 3)% — büyük harf %(upper(%ad%))%
```

Genel kural: satır başında **`ad: metin`** yazarsan, o iş metinle çağrılır.
`print:` bunun bir örneğidir.

---

## 4. İşlemler

```ton
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

```ton
if %puan% >= 90
  print: AA
elif %puan% >= 70
  print: BB
else
  print: FF
end
```

---

## 6. Döngüler

```ton
repeat 3
  print: selam
end

repeat 5 as i           # i: 1, 2, 3, 4, 5
  print: %i%
end

for oge in %liste%
  print: %oge%
end

for anahtar, deger in %harita%
  print: %anahtar% = %deger%
end

while %sayac% < 10
  sayac += 1
end
```

`stop` döngüyü kırar, `skip` sıradakine geçer. (`dur` / `atla`)

---

## 7. İşler (fonksiyonlar)

```ton
func selamla(ad, selam = "Merhaba")
  return %selam% + ", " + %ad%
end

print: %(selamla("Nyl"))%
print: %(selamla(selam: "Selam", ad: "TON"))%     # isimle çağırma
```

Tek satırlık iş:

```ton
func iki_kat(x) -> %x% * 2
```

İşler birer değerdir; başka işe verilebilir:

```ton
print(map([1, 2, 3], iki_kat))
print(filter([1, 2, 3, 4], func(x) -> %x% mod 2 == 0))
print(reduce([1, 2, 3], func(toplam, x) -> %toplam% + %x%, 0))
```

Bir işin içinde dışarıdaki değişkene yazarsan, dışarıdaki değişken değişir:

```ton
sayac = 0
func arttir()
  sayac += 1
end
```

---

## 8. Hatalar

```ton
try
  riskli_is()
catch mesaj
  print: hata oldu: %mesaj%
end
```

`catch` adı yazılmazsa hata metni `%hata%` değişkenindedir.
Kendi hatanı fırlatmak için: `hata("mesaj")`

---

## 9. Başka dosyayı kullanma

```ton
use "yardimci.ton"        # içindeki her şey buraya gelir
use "yardimci" as yar     # ad altında toplanır -> yar.alan(2)
use web                   # kütüphane yükler
```

---

## 10. Anahtar kelimeler

| TON | Türkçe karşılığı |
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

```ton
eğer %yas% > 18
  yaz: yetişkin
bitir
```

---

## 11. Yorumlar

```ton
# bu bir yorum
a = 1    # satır sonunda da olur
```

---

## 12. Sık düşülen üç tuzak

```ton
print: 2 + 3          # -> "2 + 3"   (print: düz metin yazar)
print: %(2 + 3)%      # -> 5         (hesap için %( )% kullan)

print(a)              # HATA: 'a' bir değişken; %a% yazmalısın
print(%a%)            # doğru

define("f", ["x"], "return %x%")    # %x% burada hemen okunur -> hata
define("f", ["x"], 'return %x%')    # tek tırnak: kod ham kalır
```
