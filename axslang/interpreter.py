"""Axs yorumlayicisi: AST'yi dolasarak calistirir."""

import os
import sys

from . import nodes as N
from .errors import AxsError, AxsNameError, AxsRuntimeError, AxsTypeError, AxsUserError
from .okuma import dosya_oku
from .parser import cozumle, cozumle_ifade
from .values import (Bagli, Gomulu, Gorev, Isim, Islev, cagrilabilir_mi,
                     dogru_mu, gosterim, metin, sayi_mi, tur)

UZANTILAR = (".axs", ".nyl")


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

    __slots__ = ("degerler", "ust", "sinir")

    def __init__(self, ust=None, degerler=None, sinir=False):
        self.degerler = dict(degerler or {})
        self.ust = ust
        # sinir=True: bu bir dosya/modul siniri. Atama bu noktanin otesine
        # gecmez; boylece bir kutuphanenin ic degiskeni disaridaki ayni adli
        # degiskeni ezemez.
        self.sinir = sinir

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
        """Ad bir ust kapsamda varsa orayi gunceller, yoksa burada acar.

        Arama modul sinirinda durur: bir dosyanin ici disaridaki degiskenleri
        kazara degistiremez."""
        k = self
        while k is not None:
            if ad in k.degerler:
                k.degerler[ad] = deger
                return
            if k.sinir:
                break
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
        # `use "komsu.axs"` cagiran dosyanin yanindan cozulur
        self.klasor_yigini = [self.kok]
        self.gorevler = []
        self._ifade_onbellek = {}
        self.cikti = cikti or (lambda s: (sys.stdout.write(s), sys.stdout.flush()))
        self.argv = list(argv or [])
        self.evren.yerel("_dosya", dosya or "")
        self.evren.yerel("_argv", self.argv)
        self._env_dosyasini_yukle()

    def _env_dosyasini_yukle(self):
        """Calisan dosyanin yaninda .env varsa kendiliginden okunur."""
        from .lib.cekirdek import DOSYA_ORTAMI, env_dosyasi_coz
        from .okuma import dosya_oku
        bakilacak = []
        for klasor in (self.kok, os.getcwd()):
            yol = os.path.join(klasor, ".env")
            if yol not in bakilacak:
                bakilacak.append(yol)
        for yol in bakilacak:
            if os.path.isfile(yol):
                try:
                    DOSYA_ORTAMI.update(env_dosyasi_coz(dosya_oku(yol)))
                except OSError:
                    pass

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
                    raise AxsTypeError("'repeat' bir sayi ister, %s verildi" % tur(sayi), d.line)
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
                except AxsError as e:
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
        except AxsError as e:
            if e.satir is None:
                e.satir = d.line
            if e.dosya is None:
                e.dosya = self.dosya
            raise
        raise AxsRuntimeError("Bilinmeyen deyim: %s" % t, d.line)

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
            raise AxsTypeError("'for' listede, haritada ya da metinde gezer; %s verildi"
                               % tur(kaynak), d.line)
        for oge in ogeler:
            if d.ikinci:
                if isinstance(oge, (tuple, list)) and len(oge) == 2:
                    kapsam.ata(d.ad, oge[0])
                    kapsam.ata(d.ikinci, oge[1])
                else:
                    raise AxsTypeError("Iki degiskenli 'for' icin ikili deger gerekir", d.line)
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
                    raise AxsNameError("'%s' adinda bir degisken yok" % hedef.ad, d.line)
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
                    raise AxsTypeError("Liste sirasi sayi olmali", d.line)
                i = int(anahtar)
                if i < 0:
                    i += len(nesne)
                if not 0 <= i < len(nesne):
                    raise AxsRuntimeError("Liste disinda sira: %s" % metin(anahtar), d.line)
                nesne[i] = deger
            else:
                raise AxsTypeError("%s icine deger konulamaz" % tur(nesne), d.line)
        elif isinstance(hedef, N.Uye):
            nesne = self.degerlendir(hedef.nesne, kapsam)
            if isinstance(nesne, dict):
                nesne[hedef.ad] = deger
            elif isinstance(nesne, Isim):
                nesne.uyeler[hedef.ad] = deger
            else:
                raise AxsTypeError("%s uzerine '%s' yazilamaz" % (tur(nesne), hedef.ad), d.line)
        else:
            raise AxsRuntimeError("Buraya deger atanamaz", d.line)
        return deger

    def _kullan(self, d, kapsam):
        kaynak = self.degerlendir(d.kaynak, kapsam)
        if not isinstance(kaynak, str):
            raise AxsTypeError("'use' bir ad ya da dosya yolu ister", d.line)
        kutuphane = self._kutuphane_yukle(self, kaynak)
        if kutuphane is not None:
            kapsam.ata(d.takma or kutuphane.ad, kutuphane)
            return kutuphane
        # `use jubb` gibi ciplak ad: Axs ile yazilmis kutuphanelerde de aranir
        ad_ile = isinstance(d.kaynak, N.Sabit)
        yol = self.dosya_bul(kaynak)
        if yol is None and ad_ile:
            yol = self.axs_kutuphanesi_bul(kaynak)
            if yol is not None and not d.takma:
                d = N.Kullan(d.kaynak, kaynak, line=d.line)
        if yol is None:
            raise AxsRuntimeError(
                "'%s' bulunamadi. Kutuphane adi ya da dosya yolu olmali." % kaynak, d.line)
        if yol in self.yuklenenler:
            modul = self.yuklenenler[yol]
        else:
            alt = Kapsam(self.evren, sinir=True)
            yeni = Isim(os.path.splitext(os.path.basename(yol))[0], {})
            yeni.kaynak = yol
            self.yuklenenler[yol] = yeni
            self.klasor_yigini.append(os.path.dirname(os.path.abspath(yol)))
            try:
                self.blok(cozumle(dosya_oku(yol), yol), alt)
            finally:
                self.klasor_yigini.pop()
            modul = self.yuklenenler[yol]
            modul.uyeler.update(alt.degerler)
        if d.takma:
            kapsam.ata(d.takma, modul)
        else:
            for k, v in modul.uyeler.items():
                if not k.startswith("_"):
                    kapsam.ata(k, v)
        return modul

    def kutuphane_yollari(self):
        """Axs ile yazilmis kutuphanelerin arandigi klasorler, oncelik sirasiyla.

        Once calisan dosyadan yukari dogru `kutuphaneler/` aranir: boylece bir
        projenin kendi kutuphaneleri, baska bir yere kurulmus Axs'in
        kutuphanelerini golgeler.
        """
        yollar = []
        cevre = os.environ.get("AXS_YOL")
        if cevre:
            yollar += [y for y in cevre.split(os.pathsep) if y]
        klasor = self.kok
        while True:
            yollar.append(os.path.join(klasor, "kutuphaneler"))
            ust = os.path.dirname(klasor)
            if ust == klasor:
                break
            klasor = ust
        paket_koku = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        yollar.append(os.path.join(paket_koku, "kutuphaneler"))
        yollar.append(os.path.join(os.path.expanduser("~"), ".axs", "kutuphaneler"))
        gorulen = []
        for y in yollar:
            if y not in gorulen:
                gorulen.append(y)
        return gorulen

    def axs_kutuphanesi_bul(self, ad):
        for klasor in self.kutuphane_yollari():
            for uzanti in UZANTILAR:
                aday = os.path.join(klasor, ad + uzanti)
                if os.path.isfile(aday):
                    return aday
        return None

    def su_anki_klasor(self):
        return self.klasor_yigini[-1] if self.klasor_yigini else self.kok

    def dosya_bul(self, ad, klasor=None):
        adaylar = []
        kok = klasor or self.su_anki_klasor()
        temel = ad if os.path.isabs(ad) else os.path.join(kok, ad)
        adaylar.append(temel)
        if not os.path.splitext(ad)[1]:
            adaylar += [temel + u for u in UZANTILAR]
        for a in adaylar:
            if os.path.isfile(a):
                return a
        # calisan dosyanin yaninda yoksa ana dosyanin yanina da bak
        if kok != self.kok and not os.path.isabs(ad):
            return self.dosya_bul(ad, self.kok)
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
                raise AxsNameError("'%s' adinda bir degisken yok" % e.ad, e.line, self.dosya)
        if t == "Metin":
            return self.metin_kur(e.parcalar, kapsam, e.line)
        if t == "Ad":
            # Ciplak ad once degiskenlere, sonra hazir islere bakar.
            if kapsam.var_mi(e.ad):
                return kapsam.bul(e.ad)
            if e.ad in self.gomulu:
                return self.gomulu[e.ad]
            raise AxsNameError("'%s' diye bir sey yok" % e.ad, e.line, self.dosya)
        if t == "Ikili":
            return self.ikili(e, kapsam)
        if t == "Tekli":
            deger = self.degerlendir(e.deger, kapsam)
            if e.islec == "not":
                return not dogru_mu(deger)
            if not sayi_mi(deger):
                raise AxsTypeError("'-' sadece sayilarda kullanilir", e.line)
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
        raise AxsRuntimeError("Bilinmeyen ifade: %s" % t, e.line)

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
            except AxsError as e:
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
                raise AxsNameError("'%s' adinda bir degisken yok" % ad, satir, self.dosya)
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
                raise AxsTypeError("Sira numarasi sayi olmali, %s verildi" % tur(anahtar), satir)
            i = int(anahtar)
            if i < 0:
                i += len(nesne)
            if not 0 <= i < len(nesne):
                raise AxsRuntimeError(
                    "%s icinde %s. sira yok (uzunluk %d)" % (tur(nesne), metin(anahtar), len(nesne)),
                    satir)
            return nesne[i]
        raise AxsTypeError("%s icinde sira ile erisim yok" % tur(nesne), satir)

    def uye(self, nesne, ad, satir):
        if isinstance(nesne, Isim):
            try:
                return nesne.get(ad)
            except AxsTypeError as e:
                e.satir = satir
                raise
        # Haritada kendi alani varsa o kazanir: veri, hazir yontemi golgeler.
        # (API verilerinde `type`, `count`, `values` gibi alan adlari yaygin)
        if isinstance(nesne, dict) and ad in nesne:
            return nesne[ad]
        yontem = self._yontem_bul(nesne, ad)
        if yontem is not None:
            return Bagli(ad, nesne, yontem)
        if isinstance(nesne, dict):
            return None
        if isinstance(nesne, Gorev) and ad in ("sonuc", "bitti", "hata"):
            if ad == "sonuc":
                return nesne.bekle()
            if ad == "bitti":
                return nesne.bitti
            return nesne.hata and str(nesne.hata)
        raise AxsTypeError("%s uzerinde '%s' yok" % (tur(nesne), ad), satir)

    # ------------------------------------------------------------ cagri
    def cagri_dugumu(self, e, kapsam):
        hedef = self.degerlendir(e.hedef, kapsam)
        # `ai = "groq"` gibi: ayni ad hem degisken hem hazir is olabilir.
        # Deger cagrilabilir degilse hazir ise dusulur.
        if (isinstance(e.hedef, N.Ad) and not cagrilabilir_mi(hedef)
                and not isinstance(hedef, Isim) and e.hedef.ad in self.gomulu):
            hedef = self.gomulu[e.hedef.ad]
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
            except AxsError:
                raise
            except TypeError as ex:
                raise self._cagri_hatasi(hedef.ad, ex, satir)
        if isinstance(hedef, Islev):
            return self.islev_cagir(hedef, args, isimli, satir)
        raise AxsTypeError("%s cagrilamaz" % tur(hedef), satir)

    def islev_cagir(self, islev, args, isimli=None, satir=None):
        isimli = dict(isimli or {})
        kapsam = Kapsam(islev.kapsam)
        adlar = [p[0] for p in islev.parametreler]
        if len(args) > len(adlar):
            raise AxsRuntimeError(
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
                raise AxsRuntimeError("'%s' icin '%s' degeri verilmedi" % (islev.ad, ad), satir)
        if isimli:
            raise AxsRuntimeError(
                "'%s' boyle bir deger almiyor: %s" % (islev.ad, ", ".join(isimli)), satir)
        try:
            self.blok(islev.govde, kapsam)
        except _Dondur as d:
            return d.deger
        return None

    def _cagri_hatasi(self, ad, ex, satir):
        return AxsRuntimeError("'%s' cagrisi hatali: %s" % (ad, ex), satir)

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
                raise AxsRuntimeError("Sifira bolunemez", satir)
            sonuc = sol / sag
            return int(sonuc) if isinstance(sol, int) and isinstance(sag, int) \
                and sonuc.is_integer() else sonuc
        if islec == "mod":
            _sayi_iste(islec, sol, sag, satir)
            if sag == 0:
                raise AxsRuntimeError("Sifira bolunemez", satir)
            return sol % sag
        if islec == "^":
            _sayi_iste(islec, sol, sag, satir)
            return sol ** sag
        raise AxsRuntimeError("Bilinmeyen islec: %s" % islec, satir)


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
        raise AxsTypeError("%s ile %s karsilastirilamaz" % (tur(a), tur(b)), satir)
    if islec == "<":
        return a < b
    if islec == ">":
        return a > b
    if islec == "<=":
        return a <= b
    return a >= b


def _sayi_iste(islec, a, b, satir):
    if not (sayi_mi(a) and sayi_mi(b)):
        raise AxsTypeError(
            "'%s' islemi %s ile %s arasinda yapilamaz" % (islec, tur(a), tur(b)), satir)
