"""TON yorumlayicisi: AST'yi dolasarak calistirir."""

import os
import sys

from . import nodes as N
from .errors import TonError, TonNameError, TonRuntimeError, TonTypeError, TonUserError
from .okuma import dosya_oku
from .parser import cozumle, cozumle_ifade
from .values import (Bagli, Gomulu, Gorev, Isim, Islev, cagrilabilir_mi,
                     dogru_mu, gosterim, metin, sayi_mi, tur)

UZANTILAR = (".ton", ".tn", ".nyl", ".tnl")


# ---------------------------------------------------------------- sinyaller
class _Dondur(Exception):
    def __init__(self, deger):
        self.deger = deger


class _Durdur(Exception):
    pass


class _Atla(Exception):
    pass


class Kapsam:
    """Degiskenlerin tutuldugu alan."""

    __slots__ = ("degerler", "ust")

    def __init__(self, ust=None, degerler=None):
        self.degerler = dict(degerler or {})
        self.ust = ust

    def bul(self, ad):
        k = self
        while k is not None:
            if ad in k.degerler:
                return k.degerler[ad]
            k = k.ust
        raise KeyError(ad)

    def var_mi(self, ad):
        k = self
        while k is not None:
            if ad in k.degerler:
                return True
            k = k.ust
        return False

    def ata(self, ad, deger):
        """Ad zaten bir ust kapsamda varsa orayi gunceller, yoksa burada acar."""
        k = self
        while k is not None:
            if ad in k.degerler:
                k.degerler[ad] = deger
                return
            k = k.ust
        self.degerler[ad] = deger

    def yerel(self, ad, deger):
        self.degerler[ad] = deger


class Yorumlayici:
    def __init__(self, dosya=None, cikti=None, argv=None):
        from .lib import gomululeri_yukle, yontem_bul, kutuphane_yukle

        self.dosya = dosya
        self.kok = os.path.dirname(os.path.abspath(dosya)) if dosya else os.getcwd()
        self.gomulu = gomululeri_yukle()
        self._yontem_bul = yontem_bul
        self._kutuphane_yukle = kutuphane_yukle
        self.evren = Kapsam()
        self.yuklenenler = {}
        self.gorevler = []
        self._ifade_onbellek = {}
        self.cikti = cikti or (lambda s: (sys.stdout.write(s), sys.stdout.flush()))
        self.argv = list(argv or [])
        self.evren.yerel("_dosya", dosya or "")
        self.evren.yerel("_argv", self.argv)

    # ------------------------------------------------------------ giris
    def calistir_kaynak(self, kaynak, dosya=None, kapsam=None):
        if "\r" in kaynak:
            kaynak = kaynak.replace("\r\n", "\n").replace("\r", "\n")
        program = cozumle(kaynak, dosya or self.dosya)
        return self.blok(program, kapsam or self.evren)

    def calistir_dosya(self, yol):
        return self.calistir_kaynak(dosya_oku(yol), yol)

    # ------------------------------------------------------------ deyimler
    def blok(self, deyimler, kapsam):
        son = None
        for d in deyimler:
            son = self.deyim(d, kapsam)
        return son

    def deyim(self, d, kapsam):
        t = d.tur
        try:
            if t == "IfadeDeyimi":
                return self.degerlendir(d.ifade, kapsam)
            if t == "Ata":
                return self._ata(d, kapsam)
            if t == "Eger":
                for kosul, govde in d.dallar:
                    if dogru_mu(self.degerlendir(kosul, kapsam)):
                        return self.blok(govde, kapsam)
                if d.digeri is not None:
                    return self.blok(d.digeri, kapsam)
                return None
            if t == "Surece":
                while dogru_mu(self.degerlendir(d.kosul, kapsam)):
                    try:
                        self.blok(d.govde, kapsam)
                    except _Durdur:
                        break
                    except _Atla:
                        continue
                return None
            if t == "Tekrarla":
                sayi = self.degerlendir(d.sayi, kapsam)
                if not sayi_mi(sayi):
                    raise TonTypeError("'repeat' bir sayi ister, %s verildi" % tur(sayi), d.line)
                for i in range(int(sayi)):
                    if d.sayac:
                        kapsam.ata(d.sayac, i + 1)
                    try:
                        self.blok(d.govde, kapsam)
                    except _Durdur:
                        break
                    except _Atla:
                        continue
                return None
            if t == "Her":
                return self._her(d, kapsam)
            if t == "IsTanimi":
                islev = Islev(d.ad, d.parametreler, d.govde, kapsam)
                kapsam.ata(d.ad, islev)
                return islev
            if t == "Dondur":
                raise _Dondur(self.degerlendir(d.deger, kapsam) if d.deger is not None else None)
            if t == "Durdur":
                raise _Durdur()
            if t == "Atla":
                raise _Atla()
            if t == "Dene":
                try:
                    self.blok(d.govde, kapsam)
                except (_Dondur, _Durdur, _Atla):
                    raise
                except TonError as e:
                    if d.hata_adi:
                        kapsam.ata(d.hata_adi, e.mesaj)
                    kapsam.ata("hata", e.mesaj)
                    self.blok(d.yakala_govde, kapsam)
                except (OSError, ValueError, ZeroDivisionError) as e:
                    if d.hata_adi:
                        kapsam.ata(d.hata_adi, str(e))
                    kapsam.ata("hata", str(e))
                    self.blok(d.yakala_govde, kapsam)
                return None
            if t == "Kullan":
                return self._kullan(d, kapsam)
        except TonError as e:
            if e.satir is None:
                e.satir = d.line
            if e.dosya is None:
                e.dosya = self.dosya
            raise
        raise TonRuntimeError("Bilinmeyen deyim: %s" % t, d.line)

    def _her(self, d, kapsam):
        kaynak = self.degerlendir(d.kaynak, kapsam)
        if isinstance(kaynak, dict):
            ogeler = list(kaynak.items())
        elif isinstance(kaynak, str):
            ogeler = list(kaynak)
        elif isinstance(kaynak, (list, tuple)):
            ogeler = list(kaynak)
        elif hasattr(kaynak, "__iter__"):
            ogeler = kaynak
        else:
            raise TonTypeError("'for' listede, haritada ya da metinde gezer; %s verildi"
                               % tur(kaynak), d.line)
        for oge in ogeler:
            if d.ikinci:
                if isinstance(oge, (tuple, list)) and len(oge) == 2:
                    kapsam.ata(d.ad, oge[0])
                    kapsam.ata(d.ikinci, oge[1])
                else:
                    raise TonTypeError("Iki degiskenli 'for' icin ikili deger gerekir", d.line)
            else:
                kapsam.ata(d.ad, list(oge) if isinstance(oge, tuple) else oge)
            try:
                self.blok(d.govde, kapsam)
            except _Durdur:
                break
            except _Atla:
                continue
        return None

    def _ata(self, d, kapsam):
        deger = self.degerlendir(d.deger, kapsam)
        hedef = d.hedef
        if d.islec != "=":
            if isinstance(hedef, N.Ad):
                try:
                    onceki = kapsam.bul(hedef.ad)
                except KeyError:
                    raise TonNameError("'%s' adinda bir degisken yok" % hedef.ad, d.line)
            else:
                onceki = self.degerlendir(hedef, kapsam)
            deger = self.islem(d.islec[0], onceki, deger, d.line)
        if isinstance(hedef, N.Ad):
            kapsam.ata(hedef.ad, deger)
        elif isinstance(hedef, N.Degisken):
            kapsam.ata(hedef.ad, deger)
        elif isinstance(hedef, N.Dizin):
            nesne = self.degerlendir(hedef.nesne, kapsam)
            anahtar = self.degerlendir(hedef.anahtar, kapsam)
            if isinstance(nesne, dict):
                nesne[anahtar if isinstance(anahtar, str) else metin(anahtar)] = deger
            elif isinstance(nesne, list):
                if not sayi_mi(anahtar):
                    raise TonTypeError("Liste sirasi sayi olmali", d.line)
                i = int(anahtar)
                if i < 0:
                    i += len(nesne)
                if not 0 <= i < len(nesne):
                    raise TonRuntimeError("Liste disinda sira: %s" % metin(anahtar), d.line)
                nesne[i] = deger
            else:
                raise TonTypeError("%s icine deger konulamaz" % tur(nesne), d.line)
        elif isinstance(hedef, N.Uye):
            nesne = self.degerlendir(hedef.nesne, kapsam)
            if isinstance(nesne, dict):
                nesne[hedef.ad] = deger
            elif isinstance(nesne, Isim):
                nesne.uyeler[hedef.ad] = deger
            else:
                raise TonTypeError("%s uzerine '%s' yazilamaz" % (tur(nesne), hedef.ad), d.line)
        else:
            raise TonRuntimeError("Buraya deger atanamaz", d.line)
        return deger

    def _kullan(self, d, kapsam):
        kaynak = self.degerlendir(d.kaynak, kapsam)
        if not isinstance(kaynak, str):
            raise TonTypeError("'use' bir ad ya da dosya yolu ister", d.line)
        kutuphane = self._kutuphane_yukle(self, kaynak)
        if kutuphane is not None:
            kapsam.ata(d.takma or kutuphane.ad, kutuphane)
            return kutuphane
        yol = self.dosya_bul(kaynak)
        if yol is None:
            raise TonRuntimeError(
                "'%s' bulunamadi. Kutuphane adi ya da dosya yolu olmali." % kaynak, d.line)
        if yol in self.yuklenenler:
            modul = self.yuklenenler[yol]
        else:
            alt = Kapsam(self.evren)
            self.yuklenenler[yol] = Isim(os.path.splitext(os.path.basename(yol))[0], {})
            self.blok(cozumle(dosya_oku(yol), yol), alt)
            modul = self.yuklenenler[yol]
            modul.uyeler.update(alt.degerler)
        if d.takma:
            kapsam.ata(d.takma, modul)
        else:
            for k, v in modul.uyeler.items():
                if not k.startswith("_"):
                    kapsam.ata(k, v)
        return modul

    def dosya_bul(self, ad):
        adaylar = []
        temel = ad if os.path.isabs(ad) else os.path.join(self.kok, ad)
        adaylar.append(temel)
        if not os.path.splitext(ad)[1]:
            adaylar += [temel + u for u in UZANTILAR]
        for a in adaylar:
            if os.path.isfile(a):
                return a
        return None

    # ------------------------------------------------------------ ifadeler
    def degerlendir(self, e, kapsam):
        t = e.tur
        if t == "Sabit":
            return e.deger
        if t == "Degisken":
            try:
                return kapsam.bul(e.ad)
            except KeyError:
                if e.ad in self.gomulu:
                    return self.gomulu[e.ad]
                raise TonNameError("'%s' adinda bir degisken yok" % e.ad, e.line, self.dosya)
        if t == "Metin":
            return self.metin_kur(e.parcalar, kapsam, e.line)
        if t == "Ad":
            # once kullanicinin tanimi, sonra hazir isler (kullanici golgeleyebilir)
            if kapsam.var_mi(e.ad):
                deger = kapsam.bul(e.ad)
                if cagrilabilir_mi(deger) or isinstance(deger, Isim):
                    return deger
                if e.ad in self.gomulu:
                    return self.gomulu[e.ad]
                raise TonNameError(
                    "'%s' bir degisken; %%%s%% seklinde yazmalisin" % (e.ad, e.ad),
                    e.line, self.dosya)
            if e.ad in self.gomulu:
                return self.gomulu[e.ad]
            raise TonNameError("'%s' adinda bir is yok" % e.ad, e.line, self.dosya)
        if t == "Ikili":
            return self.ikili(e, kapsam)
        if t == "Tekli":
            deger = self.degerlendir(e.deger, kapsam)
            if e.islec == "not":
                return not dogru_mu(deger)
            if not sayi_mi(deger):
                raise TonTypeError("'-' sadece sayilarda kullanilir", e.line)
            return -deger
        if t == "Liste":
            return [self.degerlendir(x, kapsam) for x in e.ogeler]
        if t == "Harita":
            cikti = {}
            for a, d in e.ciftler:
                anahtar = self.degerlendir(a, kapsam)
                cikti[anahtar if isinstance(anahtar, str) else metin(anahtar)] = \
                    self.degerlendir(d, kapsam)
            return cikti
        if t == "Cagri":
            return self.cagri_dugumu(e, kapsam)
        if t == "Dizin":
            return self.dizin(self.degerlendir(e.nesne, kapsam),
                              self.degerlendir(e.anahtar, kapsam), e.line)
        if t == "Uye":
            return self.uye(self.degerlendir(e.nesne, kapsam), e.ad, e.line)
        if t == "IsTanimi":
            islev = Islev(e.ad, e.parametreler, e.govde, kapsam)
            if e.ad:
                kapsam.ata(e.ad, islev)
            return islev
        raise TonRuntimeError("Bilinmeyen ifade: %s" % t, e.line)

    def metin_kur(self, parcalar, kapsam, satir):
        cikti = []
        for p in parcalar:
            if p[0] == "text":
                cikti.append(p[1])
            elif p[0] == "expr":
                cikti.append(metin(self.degerlendir(self._ifade_derle(p[1], satir), kapsam)))
            else:
                deger = self.degisken_yolu(p[1], p[2], kapsam, satir)
                cikti.append(metin(deger))
        return "".join(cikti)

    def _ifade_derle(self, kod, satir):
        """Sablon icindeki %(ifade)% parcasini cozumler ve saklar."""
        dugum = self._ifade_onbellek.get(kod)
        if dugum is None:
            try:
                dugum = cozumle_ifade(kod, self.dosya)
            except TonError as e:
                if e.satir is None:
                    e.satir = satir
                raise
            self._ifade_onbellek[kod] = dugum
        return dugum

    def degisken_yolu(self, ad, erisimler, kapsam, satir):
        try:
            deger = kapsam.bul(ad)
        except KeyError:
            if ad in self.gomulu:
                deger = self.gomulu[ad]
            else:
                raise TonNameError("'%s' adinda bir degisken yok" % ad, satir, self.dosya)
        for tip, anahtar in erisimler:
            if tip == "attr":
                deger = self.uye(deger, anahtar, satir)
            elif tip == "index":
                deger = self.dizin(deger, anahtar, satir)
            else:
                deger = self.dizin(deger, kapsam.bul(anahtar), satir)
        return deger

    def dizin(self, nesne, anahtar, satir):
        if isinstance(nesne, dict):
            k = anahtar if isinstance(anahtar, str) else metin(anahtar)
            if k not in nesne:
                return None
            return nesne[k]
        if isinstance(nesne, (list, str)):
            if not sayi_mi(anahtar):
                raise TonTypeError("Sira numarasi sayi olmali, %s verildi" % tur(anahtar), satir)
            i = int(anahtar)
            if i < 0:
                i += len(nesne)
            if not 0 <= i < len(nesne):
                raise TonRuntimeError(
                    "%s icinde %s. sira yok (uzunluk %d)" % (tur(nesne), metin(anahtar), len(nesne)),
                    satir)
            return nesne[i]
        raise TonTypeError("%s icinde sira ile erisim yok" % tur(nesne), satir)

    def uye(self, nesne, ad, satir):
        if isinstance(nesne, Isim):
            try:
                return nesne.get(ad)
            except TonTypeError as e:
                e.satir = satir
                raise
        yontem = self._yontem_bul(nesne, ad)
        if yontem is not None:
            return Bagli(ad, nesne, yontem)
        if isinstance(nesne, dict):
            return nesne.get(ad)
        if isinstance(nesne, Gorev) and ad in ("sonuc", "bitti", "hata"):
            if ad == "sonuc":
                return nesne.bekle()
            if ad == "bitti":
                return nesne.bitti
            return nesne.hata and str(nesne.hata)
        raise TonTypeError("%s uzerinde '%s' yok" % (tur(nesne), ad), satir)

    # ------------------------------------------------------------ cagri
    def cagri_dugumu(self, e, kapsam):
        hedef = self.degerlendir(e.hedef, kapsam)
        args = [self.degerlendir(a, kapsam) for a in e.argumanlar]
        isimli = {k: self.degerlendir(v, kapsam) for k, v in e.isimli.items()}
        return self.cagir(hedef, args, isimli, e.line)

    def cagir(self, hedef, args, isimli=None, satir=None):
        isimli = isimli or {}
        if isinstance(hedef, Bagli):
            try:
                return hedef.fn(self, hedef.nesne, *args, **isimli)
            except TypeError as ex:
                raise self._cagri_hatasi(hedef.ad, ex, satir)
        if isinstance(hedef, Gomulu):
            try:
                if hedef.yorumlayici_ister:
                    return hedef.fn(self, *args, **isimli)
                return hedef.fn(*args, **isimli)
            except TonError:
                raise
            except TypeError as ex:
                raise self._cagri_hatasi(hedef.ad, ex, satir)
        if isinstance(hedef, Islev):
            return self.islev_cagir(hedef, args, isimli, satir)
        raise TonTypeError("%s cagrilamaz" % tur(hedef), satir)

    def islev_cagir(self, islev, args, isimli=None, satir=None):
        isimli = dict(isimli or {})
        kapsam = Kapsam(islev.kapsam)
        adlar = [p[0] for p in islev.parametreler]
        if len(args) > len(adlar):
            raise TonRuntimeError(
                "'%s' en fazla %d deger alir, %d verildi" % (islev.ad, len(adlar), len(args)),
                satir)
        for i, (ad, varsayilan) in enumerate(islev.parametreler):
            if i < len(args):
                kapsam.yerel(ad, args[i])
            elif ad in isimli:
                kapsam.yerel(ad, isimli.pop(ad))
            elif varsayilan is not None:
                kapsam.yerel(ad, self.degerlendir(varsayilan, kapsam))
            else:
                raise TonRuntimeError("'%s' icin '%s' degeri verilmedi" % (islev.ad, ad), satir)
        if isimli:
            raise TonRuntimeError(
                "'%s' boyle bir deger almiyor: %s" % (islev.ad, ", ".join(isimli)), satir)
        try:
            self.blok(islev.govde, kapsam)
        except _Dondur as d:
            return d.deger
        return None

    def _cagri_hatasi(self, ad, ex, satir):
        return TonRuntimeError("'%s' cagrisi hatali: %s" % (ad, ex), satir)

    # ------------------------------------------------------------ islemler
    def ikili(self, e, kapsam):
        if e.islec == "and":
            sol = self.degerlendir(e.sol, kapsam)
            return self.degerlendir(e.sag, kapsam) if dogru_mu(sol) else sol
        if e.islec == "or":
            sol = self.degerlendir(e.sol, kapsam)
            return sol if dogru_mu(sol) else self.degerlendir(e.sag, kapsam)
        sol = self.degerlendir(e.sol, kapsam)
        sag = self.degerlendir(e.sag, kapsam)
        return self.islem(e.islec, sol, sag, e.line)

    def islem(self, islec, sol, sag, satir):
        if islec == "==":
            return _esit(sol, sag)
        if islec == "!=":
            return not _esit(sol, sag)
        if islec in ("<", ">", "<=", ">="):
            return _sirala(islec, sol, sag, satir)
        if islec == "+":
            if isinstance(sol, str) or isinstance(sag, str):
                return metin(sol) + metin(sag)
            if isinstance(sol, list) and isinstance(sag, list):
                return sol + sag
            if isinstance(sol, dict) and isinstance(sag, dict):
                yeni = dict(sol)
                yeni.update(sag)
                return yeni
            _sayi_iste(islec, sol, sag, satir)
            return sol + sag
        if islec == "*":
            if isinstance(sol, str) and sayi_mi(sag):
                return sol * int(sag)
            if isinstance(sol, list) and sayi_mi(sag):
                return sol * int(sag)
            _sayi_iste(islec, sol, sag, satir)
            return sol * sag
        if islec == "-":
            _sayi_iste(islec, sol, sag, satir)
            return sol - sag
        if islec == "/":
            _sayi_iste(islec, sol, sag, satir)
            if sag == 0:
                raise TonRuntimeError("Sifira bolunemez", satir)
            sonuc = sol / sag
            return int(sonuc) if isinstance(sol, int) and isinstance(sag, int) \
                and sonuc.is_integer() else sonuc
        if islec == "mod":
            _sayi_iste(islec, sol, sag, satir)
            if sag == 0:
                raise TonRuntimeError("Sifira bolunemez", satir)
            return sol % sag
        if islec == "^":
            _sayi_iste(islec, sol, sag, satir)
            return sol ** sag
        raise TonRuntimeError("Bilinmeyen islec: %s" % islec, satir)


def _esit(a, b):
    if sayi_mi(a) and sayi_mi(b):
        return a == b
    if type(a) is not type(b) and not (isinstance(a, type(b)) or isinstance(b, type(a))):
        return False
    return a == b


def _sirala(islec, a, b, satir):
    if isinstance(a, str) and isinstance(b, str):
        pass
    elif sayi_mi(a) and sayi_mi(b):
        pass
    elif isinstance(a, (list, dict)) and isinstance(b, (list, dict)):
        a, b = len(a), len(b)
    else:
        raise TonTypeError("%s ile %s karsilastirilamaz" % (tur(a), tur(b)), satir)
    if islec == "<":
        return a < b
    if islec == ">":
        return a > b
    if islec == "<=":
        return a <= b
    return a >= b


def _sayi_iste(islec, a, b, satir):
    if not (sayi_mi(a) and sayi_mi(b)):
        raise TonTypeError(
            "'%s' islemi %s ile %s arasinda yapilamaz" % (islec, tur(a), tur(b)), satir)
