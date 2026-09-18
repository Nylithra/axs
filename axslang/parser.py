"""Axs sozdizimi cozumleyicisi (parser)."""

from . import nodes as N
from .errors import TonSyntaxError
from .lexer import anahtar, coz

BITIRICILER = {"end", "else", "elif", "catch"}

ISLEC_KELIMELERI = {"and", "or", "not", "mod", "in", "func"}

KARSILASTIRMA = {"==", "!=", "<", ">", "<=", ">="}
TOPLAMA = {"+", "-"}
CARPMA = {"*", "/"}
ATAMA = {"=", "+=", "-=", "*=", "/="}


class Parser:
    def __init__(self, tokenlar, dosya=None):
        self.t = tokenlar
        self.i = 0
        self.dosya = dosya

    # ------------------------------------------------------------ yardimcilar
    def bak(self, k=0):
        j = min(self.i + k, len(self.t) - 1)
        return self.t[j]

    def al(self):
        t = self.t[self.i]
        if t.kind != "EOF":
            self.i += 1
        return t

    def hata(self, mesaj, token=None):
        token = token or self.bak()
        return TonSyntaxError(mesaj, token.line, self.dosya)

    def esit(self, kind, value=None):
        t = self.bak()
        return t.kind == kind and (value is None or t.value == value)

    def kelime(self, *kelimeler):
        t = self.bak()
        return t.kind == "NAME" and anahtar(t.value) in kelimeler

    def yut(self, kind, value=None):
        if self.esit(kind, value):
            self.al()
            return True
        return False

    def yut_kelime(self, *kelimeler):
        if self.kelime(*kelimeler):
            return anahtar(self.al().value)
        return None

    def bekle(self, kind, value=None, ne=None):
        if not self.esit(kind, value):
            bulunan = self.bak()
            raise self.hata(
                "%s bekleniyordu, %s bulundu"
                % (ne or (value or kind), _goster(bulunan))
            )
        return self.al()

    def bekle_kelime(self, *kelimeler):
        k = self.yut_kelime(*kelimeler)
        if k is None:
            raise self.hata("'%s' bekleniyordu, %s bulundu" % (kelimeler[0], _goster(self.bak())))
        return k

    def blok_bitti(self):
        """Blok burada bitiyor mu?

        `son = 5` gibi bir satir blok bitisi degil, atamadir: anahtar kelimeye
        benzeyen adlar da degisken olabilir."""
        if not self.kelime(*BITIRICILER):
            return False
        if self.bak(1).kind == "OP" and self.bak(1).value in ATAMA:
            return False
        return True

    def satir_sonu(self):
        """Deyim sonu: satir sonu, dosya sonu ya da bir blok bitirici."""
        if self.yut("NL"):
            while self.yut("NL"):
                pass
            return
        if self.esit("EOF") or self.kelime(*BITIRICILER):
            return
        raise self.hata("Satir sonu bekleniyordu, %s bulundu" % _goster(self.bak()))

    def bosluklari_gec(self):
        while self.yut("NL"):
            pass

    # ------------------------------------------------------------ program
    def program(self):
        govde = []
        self.bosluklari_gec()
        while not self.esit("EOF"):
            govde.append(self.deyim())
            self.bosluklari_gec()
        return govde

    def govde(self):
        """Bir blogun govdesini, bitirici kelimeye kadar okur."""
        cikti = []
        self.bosluklari_gec()
        while not self.esit("EOF") and not self.blok_bitti():
            cikti.append(self.deyim())
            self.bosluklari_gec()
        return cikti

    # ------------------------------------------------------------ deyimler
    def deyim(self):
        t = self.bak()
        k = anahtar(t.value) if t.kind == "NAME" else None

        # `son = 5` gibi: anahtar kelimeye benzeyen adlar da degisken olabilir,
        # cunku degiskenler her zaman %ad% ile okunur; karisiklik olmaz.
        if k is not None and self.bak(1).kind == "OP" and self.bak(1).value in ATAMA:
            self.al()
            islec = self.al().value
            deger = self.ifade()
            self.satir_sonu()
            return N.Ata(N.Ad(t.value, line=t.line), deger, islec, line=t.line)

        if k == "if":
            return self.eger()
        if k == "while":
            return self.surece()
        if k == "repeat":
            return self.tekrarla()
        if k == "for":
            return self.her()
        if k == "func":
            return self.is_tanimi()
        if k == "return":
            self.al()
            deger = None
            if not (self.esit("NL") or self.esit("EOF") or self.kelime(*BITIRICILER)):
                deger = self.ifade()
            self.satir_sonu()
            return N.Dondur(deger, line=t.line)
        if k == "stop":
            self.al()
            self.satir_sonu()
            return N.Durdur(line=t.line)
        if k == "skip":
            self.al()
            self.satir_sonu()
            return N.Atla(line=t.line)
        if k == "try":
            return self.dene()
        if k == "use":
            return self.kullan()
        if k in BITIRICILER:
            raise self.hata("Beklenmeyen '%s'" % t.value)

        # sablon cagrisi:  print: merhaba %ad%
        if t.kind == "NAME" and self.bak(1).kind == "OP" and self.bak(1).value == ":" \
                and self.bak(2).kind == "TEMPLATE":
            self.al(); self.al()
            sablon = self.al()
            dugum = N.Cagri(N.Ad(t.value, line=t.line),
                            [N.Metin(sablon.value, line=t.line)], {}, line=t.line)
            self.satir_sonu()
            return N.IfadeDeyimi(dugum, line=t.line)

        # atama ya da ifade
        ifade = self.ifade()
        if self.esit("OP") and self.bak().value in ATAMA:
            islec = self.al().value
            deger = self.ifade()
            if not isinstance(ifade, (N.Ad, N.Degisken, N.Dizin, N.Uye)):
                raise self.hata("Buraya deger atanamaz", t)
            self.satir_sonu()
            return N.Ata(ifade, deger, islec, line=t.line)
        self.satir_sonu()
        return N.IfadeDeyimi(ifade, line=t.line)

    def eger(self):
        satir = self.bak().line
        self.bekle_kelime("if")
        dallar = []
        kosul = self.ifade()
        govde = self.govde()
        dallar.append((kosul, govde))
        digeri = None
        while True:
            k = self.yut_kelime("elif", "else", "end")
            if k == "elif":
                dallar.append((self.ifade(), self.govde()))
                continue
            if k == "else":
                digeri = self.govde()
                self.bekle_kelime("end")
            elif k != "end":
                raise self.hata("'end' bekleniyordu")
            break
        return N.Eger(dallar, digeri, line=satir)

    def surece(self):
        satir = self.bak().line
        self.bekle_kelime("while")
        kosul = self.ifade()
        govde = self.govde()
        self.bekle_kelime("end")
        return N.Surece(kosul, govde, line=satir)

    def tekrarla(self):
        satir = self.bak().line
        self.bekle_kelime("repeat")
        sayi = self.ifade()
        sayac = None
        if self.esit("NAME") and self.bak().value in ("as", "olarak"):
            self.al()
            sayac = self.bekle("NAME", ne="sayac adi").value
        govde = self.govde()
        self.bekle_kelime("end")
        return N.Tekrarla(sayi, govde, sayac, line=satir)

    def her(self):
        satir = self.bak().line
        self.bekle_kelime("for")
        ad = self.bekle("NAME", ne="degisken adi").value
        ikinci = None
        if self.yut("OP", ","):
            ikinci = self.bekle("NAME", ne="ikinci degisken adi").value
        self.bekle_kelime("in")
        kaynak = self.ifade()
        govde = self.govde()
        self.bekle_kelime("end")
        return N.Her(ad, ikinci, kaynak, govde, line=satir)

    def parametreler(self):
        self.bekle("OP", "(")
        params = []
        while not self.esit("OP", ")"):
            ad = self.bekle("NAME", ne="parametre adi").value
            varsayilan = None
            if self.yut("OP", "=") or self.yut("OP", ":"):
                varsayilan = self.ifade()
            params.append((ad, varsayilan))
            if not self.yut("OP", ","):
                break
        self.bekle("OP", ")")
        return params

    def is_tanimi(self, ifade_olarak=False):
        satir = self.bak().line
        self.bekle_kelime("func")
        ad = None
        if self.esit("NAME") and not self.esit("OP", "("):
            ad = self.al().value
        params = self.parametreler()
        if self.yut("OP", "->"):
            govde = [N.Dondur(self.ifade(), line=satir)]
        else:
            govde = self.govde()
            self.bekle_kelime("end")
        return N.IsTanimi(ad, params, govde, line=satir)

    def dene(self):
        satir = self.bak().line
        self.bekle_kelime("try")
        govde = self.govde()
        hata_adi = None
        yakala = []
        if self.yut_kelime("catch"):
            if self.esit("NAME") and anahtar(self.bak().value) is None:
                hata_adi = self.al().value
            yakala = self.govde()
        self.bekle_kelime("end")
        return N.Dene(govde, hata_adi, yakala, line=satir)

    def kullan(self):
        satir = self.bak().line
        self.bekle_kelime("use")
        t = self.bak()
        if t.kind == "STR":
            kaynak = self.al()
            kaynak = N.Metin(kaynak.value, line=satir)
        elif t.kind == "NAME":
            kaynak = N.Sabit(self.al().value, line=satir)
        else:
            raise self.hata("'use' sonrasinda kutuphane adi ya da \"dosya\" bekleniyor")
        takma = None
        if self.esit("NAME") and self.bak().value in ("as", "olarak"):
            self.al()
            takma = self.bekle("NAME", ne="takma ad").value
        self.satir_sonu()
        return N.Kullan(kaynak, takma, line=satir)

    # ------------------------------------------------------------ ifadeler
    def ifade(self):
        return self.veya()

    def veya(self):
        sol = self.ve()
        while self.kelime("or"):
            satir = self.al().line
            sol = N.Ikili("or", sol, self.ve(), line=satir)
        return sol

    def ve(self):
        sol = self.degil()
        while self.kelime("and"):
            satir = self.al().line
            sol = N.Ikili("and", sol, self.degil(), line=satir)
        return sol

    def degil(self):
        if self.kelime("not"):
            satir = self.al().line
            return N.Tekli("not", self.degil(), line=satir)
        return self.karsilastir()

    def karsilastir(self):
        sol = self.topla()
        while self.esit("OP") and self.bak().value in KARSILASTIRMA:
            t = self.al()
            sol = N.Ikili(t.value, sol, self.topla(), line=t.line)
        return sol

    def topla(self):
        sol = self.carp()
        while self.esit("OP") and self.bak().value in TOPLAMA:
            t = self.al()
            sol = N.Ikili(t.value, sol, self.carp(), line=t.line)
        return sol

    def carp(self):
        sol = self.us()
        while (self.esit("OP") and self.bak().value in CARPMA) or self.kelime("mod"):
            t = self.al()
            islec = "mod" if t.kind == "NAME" else t.value
            sol = N.Ikili(islec, sol, self.us(), line=t.line)
        return sol

    def us(self):
        sol = self.tekli()
        if self.esit("OP", "^"):
            t = self.al()
            return N.Ikili("^", sol, self.us(), line=t.line)
        return sol

    def tekli(self):
        if self.esit("OP", "-"):
            t = self.al()
            return N.Tekli("-", self.tekli(), line=t.line)
        if self.esit("OP", "+"):
            self.al()
            return self.tekli()
        return self.sonek()

    def sonek(self):
        dugum = self.birincil()
        while True:
            if self.esit("OP", "("):
                dugum = self.cagri(dugum)
            elif self.esit("OP", "["):
                t = self.al()
                anahtar_ifade = self.ifade()
                self.bekle("OP", "]")
                dugum = N.Dizin(dugum, anahtar_ifade, line=t.line)
            elif self.esit("OP", ".") and self.bak(1).kind == "NAME":
                t = self.al()
                dugum = N.Uye(dugum, self.al().value, line=t.line)
            else:
                return dugum

    def cagri(self, hedef):
        t = self.bekle("OP", "(")
        args, isimli = [], {}
        while not self.esit("OP", ")"):
            if (self.esit("NAME") and self.bak(1).kind == "OP"
                    and self.bak(1).value == ":"):
                ad = self.al().value
                self.al()
                isimli[ad] = self.ifade()
            else:
                if isimli:
                    raise self.hata("Isimli argumanlardan sonra duz arguman olmaz")
                args.append(self.ifade())
            if not self.yut("OP", ","):
                break
        self.bekle("OP", ")")
        return N.Cagri(hedef, args, isimli, line=t.line)

    def birincil(self):
        t = self.bak()
        if t.kind == "NUM":
            self.al()
            return N.Sabit(t.value, line=t.line)
        if t.kind == "STR":
            self.al()
            if len(t.value) == 1 and t.value[0][0] == "text":
                return N.Sabit(t.value[0][1], line=t.line)
            return N.Metin(t.value, line=t.line)
        if t.kind == "VAR":
            self.al()
            return self._degisken(t)
        if t.kind == "NAME":
            k = anahtar(t.value)
            # `son(1)`, `yok(2)` gibi: ardindan `(` geliyorsa bu bir is adidir.
            # Islec gibi davranan kelimeler haric: `not (%a%)` bir cagri degildir.
            if k not in ISLEC_KELIMELERI and self.bak(1).kind == "OP" \
                    and self.bak(1).value == "(":
                self.al()
                return N.Ad(t.value, line=t.line)
            if k in ("true", "false", "null"):
                self.al()
                return N.Sabit({"true": True, "false": False}.get(k), line=t.line)
            if k == "func":
                return self.is_tanimi(ifade_olarak=True)
            if k is not None:
                raise self.hata("'%s' burada kullanilamaz" % t.value)
            self.al()
            return N.Ad(t.value, line=t.line)
        if t.kind == "OP":
            if t.value == "(":
                self.al()
                ic = self.ifade()
                self.bekle("OP", ")")
                return ic
            if t.value == "[":
                self.al()
                ogeler = []
                while not self.esit("OP", "]"):
                    ogeler.append(self.ifade())
                    if not self.yut("OP", ","):
                        break
                self.bekle("OP", "]")
                return N.Liste(ogeler, line=t.line)
            if t.value == "{":
                self.al()
                ciftler = []
                while not self.esit("OP", "}"):
                    if self.esit("NAME") and self.bak(1).kind == "OP" and self.bak(1).value == ":":
                        anah = N.Sabit(self.al().value, line=t.line)
                    else:
                        anah = self.ifade()
                    self.bekle("OP", ":")
                    ciftler.append((anah, self.ifade()))
                    if not self.yut("OP", ","):
                        break
                self.bekle("OP", "}")
                return N.Harita(ciftler, line=t.line)
        raise self.hata("Beklenmeyen %s" % _goster(t))

    def _degisken(self, t):
        ad, erisimler = t.value
        dugum = N.Degisken(ad, [], line=t.line)
        for tur, deger in erisimler:
            if tur == "attr":
                dugum = N.Uye(dugum, deger, line=t.line)
            elif tur == "index":
                dugum = N.Dizin(dugum, N.Sabit(deger, line=t.line), line=t.line)
            else:
                dugum = N.Dizin(dugum, N.Degisken(deger, [], line=t.line), line=t.line)
        return dugum


def _goster(token):
    if token.kind == "NL":
        return "satir sonu"
    if token.kind == "EOF":
        return "dosya sonu"
    if token.kind == "TEMPLATE":
        return "metin"
    return "'%s'" % (token.value,)


def cozumle(kaynak, dosya=None):
    """Kaynak metni deyim listesine cevirir."""
    return Parser(coz(kaynak, dosya), dosya).program()


def cozumle_ifade(kaynak, dosya=None):
    """Tek bir ifadeyi cozumler (sablon icindeki %(...)%) icin."""
    p = Parser(coz(kaynak, dosya), dosya)
    dugum = p.ifade()
    if not (p.esit("EOF") or p.esit("NL")):
        raise p.hata("Ifade sonunda beklenmeyen %s" % _goster(p.bak()))
    return dugum
