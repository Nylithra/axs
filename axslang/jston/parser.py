"""JavaScript sozdizimi cozumleyicisi (ES5 + yaygin ES6+ ozellikleri)."""

from ..errors import AxsSyntaxError
from .lexer import coz

# ikili islec oncelikleri
ONCELIK = {
    "??": 1, "||": 2, "&&": 3, "|": 4, "^": 5, "&": 6,
    "==": 7, "!=": 7, "===": 7, "!==": 7,
    "<": 8, ">": 8, "<=": 8, ">=": 8, "instanceof": 8, "in": 8,
    "<<": 9, ">>": 9, ">>>": 9,
    "+": 10, "-": 10,
    "*": 11, "/": 11, "%": 11,
    "**": 12,
}
MANTIK = {"&&", "||", "??"}
ATAMA = {"=", "+=", "-=", "*=", "/=", "%=", "**=", "<<=", ">>=", ">>>=",
         "&=", "|=", "^=", "&&=", "||=", "??="}
TEKLI = {"!", "~", "+", "-", "typeof", "void", "delete", "await"}


def d(t, **alanlar):
    alanlar["t"] = t
    return alanlar


class Parser:
    def __init__(self, tokenlar, dosya=None):
        self.t = tokenlar
        self.i = 0
        self.dosya = dosya

    # -------------------------------------------------------------- yardimci
    def bak(self, k=0):
        return self.t[min(self.i + k, len(self.t) - 1)]

    def al(self):
        t = self.t[self.i]
        if t.kind != "EOF":
            self.i += 1
        return t

    def hata(self, mesaj, token=None):
        token = token or self.bak()
        gorunen = "dosya sonu" if token.kind == "EOF" else repr(token.value)
        return AxsSyntaxError("%s (bulunan: %s)" % (mesaj, gorunen), token.line, self.dosya)

    def isaret(self, *degerler):
        t = self.bak()
        return t.kind == "PUNCT" and t.value in degerler

    def kelime(self, *degerler):
        t = self.bak()
        return t.kind == "NAME" and t.value in degerler

    def yut(self, *degerler):
        if self.isaret(*degerler):
            return self.al().value
        return None

    def yut_kelime(self, *degerler):
        if self.kelime(*degerler):
            return self.al().value
        return None

    def bekle(self, deger):
        if not self.isaret(deger):
            raise self.hata("'%s' bekleniyordu" % deger)
        return self.al()

    def bekle_ad(self):
        t = self.bak()
        if t.kind != "NAME":
            raise self.hata("Ad bekleniyordu")
        return self.al().value

    def noktali_virgul(self):
        """Noktali virgul ya da otomatik satir sonu (ASI)."""
        if self.yut(";"):
            return
        if self.isaret("}") or self.bak().kind == "EOF" or self.bak().satir_basi:
            return
        raise self.hata("';' bekleniyordu")

    # -------------------------------------------------------------- program
    def program(self):
        govde = []
        while self.bak().kind != "EOF":
            govde.append(self.deyim())
        return govde

    def blok(self):
        self.bekle("{")
        govde = []
        while not self.isaret("}") and self.bak().kind != "EOF":
            govde.append(self.deyim())
        self.bekle("}")
        return govde

    def govde_ya_da_deyim(self):
        if self.isaret("{"):
            return self.blok()
        return [self.deyim()]

    # -------------------------------------------------------------- deyimler
    def deyim(self):
        t = self.bak()
        satir = t.line

        if self.isaret("{"):
            return d("Blok", govde=self.blok(), satir=satir)
        if self.yut(";"):
            return d("Bos", satir=satir)

        if t.kind == "NAME":
            k = t.value
            if k in ("var", "let", "const"):
                # `let` bir degisken adi da olabilir
                if self.bak(1).kind == "NAME" or self.bak(1).kind == "PUNCT" \
                        and self.bak(1).value in ("[", "{"):
                    dugum = self.degisken_bildirimi()
                    self.noktali_virgul()
                    return dugum
            if k == "function":
                return self.is_bildirimi()
            if k == "async" and self.bak(1).kind == "NAME" and self.bak(1).value == "function":
                return self.is_bildirimi()
            if k == "class":
                return self.sinif()
            if k == "if":
                return self.eger()
            if k == "for":
                return self.dongu_for()
            if k == "while":
                self.al()
                self.bekle("(")
                kosul = self.ifade()
                self.bekle(")")
                return d("Surece", kosul=kosul, govde=self.govde_ya_da_deyim(), satir=satir)
            if k == "do":
                self.al()
                govde = self.govde_ya_da_deyim()
                if not self.yut_kelime("while"):
                    raise self.hata("'while' bekleniyordu")
                self.bekle("(")
                kosul = self.ifade()
                self.bekle(")")
                self.noktali_virgul()
                return d("YapSurece", kosul=kosul, govde=govde, satir=satir)
            if k == "switch":
                return self.secim()
            if k in ("return", "break", "continue", "throw"):
                self.al()
                deger = None
                if not (self.isaret(";", "}") or self.bak().kind == "EOF"
                        or self.bak().satir_basi):
                    deger = self.ifade()
                self.noktali_virgul()
                ad = {"return": "Dondur", "break": "Kir", "continue": "Devam",
                      "throw": "Firlat"}[k]
                return d(ad, deger=deger, satir=satir)
            if k == "try":
                return self.dene()
            if k in ("import", "export"):
                return self.modul()

        # etiket:  ad:
        if t.kind == "NAME" and self.bak(1).kind == "PUNCT" and self.bak(1).value == ":" \
                and t.value not in ("default", "case"):
            ad = self.al().value
            self.al()
            return d("Etiket", ad=ad, govde=self.deyim(), satir=satir)

        ifade = self.ifade()
        self.noktali_virgul()
        return d("IfadeDeyimi", ifade=ifade, satir=satir)

    def degisken_bildirimi(self):
        satir = self.bak().line
        tur = self.al().value
        bildirimler = []
        while True:
            hedef = self.baglama_hedefi()
            baslangic = self.atama_ifadesi() if self.yut("=") else None
            bildirimler.append((hedef, baslangic))
            if not self.yut(","):
                break
        return d("Degiskenler", tur=tur, bildirimler=bildirimler, satir=satir)

    def baglama_hedefi(self):
        if self.isaret("[", "{"):
            return self.birincil()
        return d("Ad", ad=self.bekle_ad(), satir=self.bak().line)

    def is_bildirimi(self):
        satir = self.bak().line
        asenkron = bool(self.yut_kelime("async"))
        self.yut_kelime("function")
        uretici = bool(self.yut("*"))
        ad = self.bekle_ad() if self.bak().kind == "NAME" else None
        params = self.parametreler()
        govde = self.blok()
        return d("Is", ad=ad, params=params, govde=govde, ok=False,
                 asenkron=asenkron, uretici=uretici, satir=satir)

    def parametreler(self):
        self.bekle("(")
        params = []
        while not self.isaret(")"):
            if self.yut("..."):
                params.append(("kalan", self.bekle_ad(), None))
            else:
                hedef = self.baglama_hedefi()
                varsayilan = self.atama_ifadesi() if self.yut("=") else None
                params.append(("duz", hedef, varsayilan))
            if not self.yut(","):
                break
        self.bekle(")")
        return params

    def sinif(self):
        satir = self.bak().line
        self.yut_kelime("class")
        ad = self.bekle_ad() if self.bak().kind == "NAME" and not self.kelime("extends") \
            else None
        ata = None
        if self.yut_kelime("extends"):
            ata = self.sonek(self.birincil())
        self.bekle("{")
        uyeler = []
        while not self.isaret("}") and self.bak().kind != "EOF":
            if self.yut(";"):
                continue
            durağan = bool(self.kelime("static") and self.bak(1).kind == "NAME")
            if durağan:
                self.al()
            asenkron = bool(self.kelime("async") and self.bak(1).kind == "NAME")
            if asenkron:
                self.al()
            self.yut("*")
            uye_adi = self.al().value
            if self.isaret("("):
                params = self.parametreler()
                govde = self.blok()
                uyeler.append(("yontem", uye_adi,
                               d("Is", ad=uye_adi, params=params, govde=govde, ok=False,
                                 asenkron=asenkron, uretici=False, satir=satir), durağan))
            else:
                deger = self.atama_ifadesi() if self.yut("=") else None
                self.noktali_virgul()
                uyeler.append(("alan", uye_adi, deger, durağan))
        self.bekle("}")
        return d("Sinif", ad=ad, ata=ata, uyeler=uyeler, satir=satir)

    def eger(self):
        satir = self.bak().line
        self.yut_kelime("if")
        self.bekle("(")
        kosul = self.ifade()
        self.bekle(")")
        govde = self.govde_ya_da_deyim()
        digeri = None
        if self.yut_kelime("else"):
            digeri = self.govde_ya_da_deyim()
        return d("Eger", kosul=kosul, govde=govde, digeri=digeri, satir=satir)

    def dongu_for(self):
        satir = self.bak().line
        self.yut_kelime("for")
        self.yut_kelime("await")
        self.bekle("(")
        baslangic = None
        if self.isaret(";"):
            self.al()
        else:
            if self.kelime("var", "let", "const"):
                baslangic = self.degisken_bildirimi()
            else:
                baslangic = d("IfadeDeyimi", ifade=self.ifade(izin_in=False), satir=satir)
            if self.kelime("of", "in"):
                tur = self.al().value
                kaynak = self.atama_ifadesi()
                self.bekle(")")
                govde = self.govde_ya_da_deyim()
                return d("ForIcinde" if tur == "of" else "ForAnahtar",
                         hedef=baslangic, kaynak=kaynak, govde=govde, satir=satir)
            self.bekle(";")
        kosul = None if self.isaret(";") else self.ifade()
        self.bekle(";")
        adim = None if self.isaret(")") else self.ifade()
        self.bekle(")")
        return d("For", baslangic=baslangic, kosul=kosul, adim=adim,
                 govde=self.govde_ya_da_deyim(), satir=satir)

    def secim(self):
        satir = self.bak().line
        self.yut_kelime("switch")
        self.bekle("(")
        deger = self.ifade()
        self.bekle(")")
        self.bekle("{")
        dallar = []
        while not self.isaret("}") and self.bak().kind != "EOF":
            if self.yut_kelime("case"):
                durum = self.ifade()
            elif self.yut_kelime("default"):
                durum = None
            else:
                raise self.hata("'case' ya da 'default' bekleniyordu")
            self.bekle(":")
            govde = []
            while not (self.isaret("}") or self.kelime("case", "default")) \
                    and self.bak().kind != "EOF":
                govde.append(self.deyim())
            dallar.append((durum, govde))
        self.bekle("}")
        return d("Secim", deger=deger, dallar=dallar, satir=satir)

    def dene(self):
        satir = self.bak().line
        self.yut_kelime("try")
        govde = self.blok()
        hata_adi = None
        yakala = None
        sonunda = None
        if self.yut_kelime("catch"):
            if self.yut("("):
                hata_adi = self.baglama_hedefi()
                self.bekle(")")
            yakala = self.blok()
        if self.yut_kelime("finally"):
            sonunda = self.blok()
        return d("Dene", govde=govde, hata_adi=hata_adi, yakala=yakala,
                 sonunda=sonunda, satir=satir)

    def modul(self):
        """import/export: Axs'te karsiligi yok, oldugu gibi tasinir."""
        satir = self.bak().line
        tur = self.al().value
        if tur == "export" and (self.kelime("function", "class", "const", "let", "var",
                                            "async")):
            return d("Disari", govde=self.deyim(), satir=satir)
        parcalar = []
        while not (self.isaret(";") or self.bak().kind == "EOF" or self.bak().satir_basi):
            parcalar.append(str(self.al().value))
        self.noktali_virgul()
        return d("Modul", tur=tur, metin=" ".join(parcalar), satir=satir)

    # -------------------------------------------------------------- ifadeler
    def ifade(self, izin_in=True):
        ilk = self.atama_ifadesi(izin_in)
        if self.isaret(","):
            ogeler = [ilk]
            while self.yut(","):
                ogeler.append(self.atama_ifadesi(izin_in))
            return d("Sira", ogeler=ogeler, satir=ilk.get("satir", 0))
        return ilk

    def atama_ifadesi(self, izin_in=True):
        ok = self.ok_isi_dene()
        if ok is not None:
            return ok
        sol = self.kosul_ifadesi(izin_in)
        if self.bak().kind == "PUNCT" and self.bak().value in ATAMA:
            islec = self.al().value
            sag = self.atama_ifadesi(izin_in)
            return d("Atama", islec=islec, hedef=sol, deger=sag,
                     satir=sol.get("satir", 0))
        return sol

    def ok_isi_dene(self):
        """(a, b) => ... ya da a => ... bicimini dener."""
        bas = self.i
        asenkron = False
        if self.kelime("async") and not self.bak(1).satir_basi and \
                (self.bak(1).kind == "NAME" or (self.bak(1).kind == "PUNCT"
                                                and self.bak(1).value == "(")):
            asenkron = True
            self.al()
        satir = self.bak().line
        params = None
        if self.bak().kind == "NAME" and self.bak().value not in ("function", "class") \
                and self.bak(1).kind == "PUNCT" and self.bak(1).value == "=>":
            params = [("duz", d("Ad", ad=self.al().value, satir=satir), None)]
        elif self.isaret("("):
            try:
                params = self.parametreler()
            except AxsSyntaxError:
                self.i = bas
                return None
            if not self.isaret("=>"):
                self.i = bas
                return None
        else:
            self.i = bas
            return None
        if not self.yut("=>"):
            self.i = bas
            return None
        if self.isaret("{"):
            govde = self.blok()
            tek_ifade = False
        else:
            govde = [d("Dondur", deger=self.atama_ifadesi(), satir=satir)]
            tek_ifade = True
        return d("Is", ad=None, params=params, govde=govde, ok=True,
                 asenkron=asenkron, uretici=False, tek_ifade=tek_ifade, satir=satir)

    def kosul_ifadesi(self, izin_in=True):
        kosul = self.ikili(0, izin_in)
        if self.yut("?"):
            evet = self.atama_ifadesi()
            self.bekle(":")
            hayir = self.atama_ifadesi(izin_in)
            return d("Kosul", kosul=kosul, evet=evet, hayir=hayir,
                     satir=kosul.get("satir", 0))
        return kosul

    def ikili(self, en_az, izin_in=True):
        sol = self.tekli()
        while True:
            t = self.bak()
            islec = None
            if t.kind == "PUNCT" and t.value in ONCELIK:
                islec = t.value
            elif t.kind == "NAME" and t.value in ("instanceof", "in"):
                if t.value == "in" and not izin_in:
                    break
                islec = t.value
            if islec is None or ONCELIK[islec] < en_az:
                break
            self.al()
            sag_en_az = ONCELIK[islec] if islec == "**" else ONCELIK[islec] + 1
            sag = self.ikili(sag_en_az, izin_in)
            tur = "Mantik" if islec in MANTIK else "Ikili"
            sol = d(tur, islec=islec, sol=sol, sag=sag, satir=t.line)
        return sol

    def tekli(self):
        t = self.bak()
        if (t.kind == "PUNCT" and t.value in ("!", "~", "+", "-")) or \
                (t.kind == "NAME" and t.value in ("typeof", "void", "delete", "await")):
            self.al()
            return d("Tekli", islec=t.value, deger=self.tekli(), satir=t.line)
        if t.kind == "PUNCT" and t.value in ("++", "--"):
            self.al()
            return d("Guncelle", islec=t.value, deger=self.tekli(), onek=True, satir=t.line)
        dugum = self.sonek(self.birincil())
        t = self.bak()
        if t.kind == "PUNCT" and t.value in ("++", "--") and not t.satir_basi:
            self.al()
            return d("Guncelle", islec=t.value, deger=dugum, onek=False, satir=t.line)
        return dugum

    def sonek(self, dugum):
        while True:
            t = self.bak()
            if self.isaret("("):
                dugum = d("Cagri", hedef=dugum, args=self.argumanlar(),
                          opsiyonel=False, satir=t.line)
            elif self.isaret("."):
                self.al()
                dugum = d("Uye", nesne=dugum, ad=self.al().value, hesapli=False,
                          opsiyonel=False, satir=t.line)
            elif self.isaret("?."):
                self.al()
                if self.isaret("("):
                    dugum = d("Cagri", hedef=dugum, args=self.argumanlar(),
                              opsiyonel=True, satir=t.line)
                elif self.isaret("["):
                    self.al()
                    anahtar = self.ifade()
                    self.bekle("]")
                    dugum = d("Uye", nesne=dugum, ad=anahtar, hesapli=True,
                              opsiyonel=True, satir=t.line)
                else:
                    dugum = d("Uye", nesne=dugum, ad=self.al().value, hesapli=False,
                              opsiyonel=True, satir=t.line)
            elif self.isaret("["):
                self.al()
                anahtar = self.ifade()
                self.bekle("]")
                dugum = d("Uye", nesne=dugum, ad=anahtar, hesapli=True,
                          opsiyonel=False, satir=t.line)
            elif self.bak().kind == "TEMPLATE":
                dugum = d("EtiketliSablon", hedef=dugum, sablon=self.al().value,
                          satir=t.line)
            else:
                return dugum

    def argumanlar(self):
        self.bekle("(")
        args = []
        while not self.isaret(")"):
            if self.yut("..."):
                args.append(d("Yayilim", deger=self.atama_ifadesi(), satir=self.bak().line))
            else:
                args.append(self.atama_ifadesi())
            if not self.yut(","):
                break
        self.bekle(")")
        return args

    def birincil(self):
        t = self.bak()
        satir = t.line
        if t.kind == "NUM":
            self.al()
            return d("Sayi", deger=t.value, satir=satir)
        if t.kind == "STR":
            self.al()
            return d("Metin", deger=t.value, satir=satir)
        if t.kind == "TEMPLATE":
            self.al()
            parcalar = []
            for tur, deger in t.value:
                if tur == "text":
                    parcalar.append(("text", deger))
                else:
                    parcalar.append(("expr", Parser(coz(deger, self.dosya),
                                                    self.dosya).ifade()))
            return d("Sablon", parcalar=parcalar, satir=satir)
        if t.kind == "REGEX":
            self.al()
            return d("Duzenli", desen=t.value[0], bayrak=t.value[1], satir=satir)
        if t.kind == "PUNCT":
            if t.value == "(":
                self.al()
                ic = self.ifade()
                self.bekle(")")
                return ic
            if t.value == "[":
                self.al()
                ogeler = []
                while not self.isaret("]"):
                    if self.isaret(","):
                        self.al()
                        ogeler.append(d("Bos", satir=satir))
                        continue
                    if self.yut("..."):
                        ogeler.append(d("Yayilim", deger=self.atama_ifadesi(), satir=satir))
                    else:
                        ogeler.append(self.atama_ifadesi())
                    if not self.yut(","):
                        break
                self.bekle("]")
                return d("Dizi", ogeler=ogeler, satir=satir)
            if t.value == "{":
                return self.nesne()
        if t.kind == "NAME":
            k = t.value
            if k in ("function",) or (k == "async" and self.bak(1).kind == "NAME"
                                      and self.bak(1).value == "function"):
                return self.is_bildirimi()
            if k == "class":
                return self.sinif()
            if k == "new":
                self.al()
                if self.isaret("."):          # new.target
                    self.al()
                    self.al()
                    return d("Ad", ad="new_target", satir=satir)
                hedef = self.birincil()
                while self.isaret(".", "["):
                    if self.yut("."):
                        hedef = d("Uye", nesne=hedef, ad=self.al().value, hesapli=False,
                                  opsiyonel=False, satir=satir)
                    else:
                        self.al()
                        anahtar = self.ifade()
                        self.bekle("]")
                        hedef = d("Uye", nesne=hedef, ad=anahtar, hesapli=True,
                                  opsiyonel=False, satir=satir)
                args = self.argumanlar() if self.isaret("(") else []
                return d("Yeni", hedef=hedef, args=args, satir=satir)
            self.al()
            if k == "this":
                return d("Bu", satir=satir)
            if k == "super":
                return d("Ust", satir=satir)
            if k == "null":
                return d("Bos", satir=satir)
            if k == "undefined":
                return d("Bos", satir=satir)
            if k in ("true", "false"):
                return d("Dogruluk", deger=(k == "true"), satir=satir)
            return d("Ad", ad=k, satir=satir)
        raise self.hata("Beklenmeyen belirtec")

    def nesne(self):
        satir = self.bak().line
        self.bekle("{")
        ciftler = []
        while not self.isaret("}") and self.bak().kind != "EOF":
            if self.yut("..."):
                ciftler.append(("yayilim", None, self.atama_ifadesi()))
                self.yut(",")
                continue
            hesapli = False
            t = self.bak()
            if self.isaret("["):
                self.al()
                anahtar = self.ifade()
                self.bekle("]")
                hesapli = True
            elif t.kind in ("STR", "NUM"):
                self.al()
                anahtar = d("Metin", deger=str(t.value), satir=satir)
            else:
                anahtar = d("Metin", deger=self.al().value, satir=satir)
            if self.isaret("("):                       # kisa yontem
                params = self.parametreler()
                govde = self.blok()
                deger = d("Is", ad=None, params=params, govde=govde, ok=False,
                          asenkron=False, uretici=False, satir=satir)
            elif self.yut(":"):
                deger = self.atama_ifadesi()
            else:                                       # kisa yazim {a}
                deger = d("Ad", ad=anahtar["deger"], satir=satir)
            ciftler.append(("hesapli" if hesapli else "duz", anahtar, deger))
            if not self.yut(","):
                break
        self.bekle("}")
        return d("Nesne", ciftler=ciftler, satir=satir)


def cozumle(kaynak, dosya=None):
    return Parser(coz(kaynak, dosya), dosya).program()
