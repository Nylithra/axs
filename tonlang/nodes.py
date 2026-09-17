"""TON soyut sozdizimi agaci (AST) dugumleri."""


class Node:
    __slots__ = ("line",)


def _dugum(ad, alanlar):
    alan_listesi = alanlar.split()

    class D(Node):
        __slots__ = tuple(alan_listesi)
        tur = ad

        def __init__(self, *deger, line=0):
            for k, v in zip(alan_listesi, deger):
                setattr(self, k, v)
            self.line = line

        def __repr__(self):
            ic = ", ".join("%s=%r" % (k, getattr(self, k, None)) for k in alan_listesi)
            return "%s(%s)" % (ad, ic)

    D.__name__ = ad
    D.alanlar = tuple(alan_listesi)
    return D


# --- ifadeler ---
Sabit = _dugum("Sabit", "deger")                 # 5, true, null
Metin = _dugum("Metin", "parcalar")              # "merhaba %ad%"
Degisken = _dugum("Degisken", "ad erisimler")    # %ad%, %kisi.yas%
Ad = _dugum("Ad", "ad")                          # ciplak ad -> fonksiyon
Cagri = _dugum("Cagri", "hedef argumanlar isimli")
Dizin = _dugum("Dizin", "nesne anahtar")         # %l%[0]
Uye = _dugum("Uye", "nesne ad")                  # %m%.ad
Ikili = _dugum("Ikili", "islec sol sag")
Tekli = _dugum("Tekli", "islec deger")
Liste = _dugum("Liste", "ogeler")
Harita = _dugum("Harita", "ciftler")

# --- deyimler ---
Ata = _dugum("Ata", "hedef deger islec")
IfadeDeyimi = _dugum("IfadeDeyimi", "ifade")
Eger = _dugum("Eger", "dallar digeri")           # dallar: [(kosul, govde)]
Surece = _dugum("Surece", "kosul govde")
Tekrarla = _dugum("Tekrarla", "sayi govde sayac")
Her = _dugum("Her", "ad ikinci kaynak govde")
IsTanimi = _dugum("IsTanimi", "ad parametreler govde")
Dondur = _dugum("Dondur", "deger")
Durdur = _dugum("Durdur", "")
Atla = _dugum("Atla", "")
Dene = _dugum("Dene", "govde hata_adi yakala_govde")
Kullan = _dugum("Kullan", "kaynak takma")
