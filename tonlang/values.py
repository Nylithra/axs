"""TON deger turleri ve bicimlendirme."""

from .errors import TonTypeError


class Isim:
    """Bir isim alani (namespace): web.serve(...) gibi kullanilir."""

    def __init__(self, ad, uyeler=None):
        self.ad = ad
        self.uyeler = dict(uyeler or {})

    def get(self, ad):
        if ad not in self.uyeler:
            raise TonTypeError("'%s' icinde '%s' yok" % (self.ad, ad))
        return self.uyeler[ad]

    def __repr__(self):
        return "<kutuphane %s>" % self.ad


class Islev:
    """Kullanicinin `func` ile tanimladigi is."""

    def __init__(self, ad, parametreler, govde, kapsam):
        self.ad = ad or "isimsiz"
        self.parametreler = parametreler
        self.govde = govde
        self.kapsam = kapsam

    def __repr__(self):
        return "<is %s>" % self.ad


class Gomulu:
    """Cekirdekle gelen hazir is."""

    def __init__(self, ad, fn, yorumlayici_ister=False):
        self.ad = ad
        self.fn = fn
        self.yorumlayici_ister = yorumlayici_ister

    def __repr__(self):
        return "<hazir is %s>" % self.ad


class Bagli:
    """Bir degere bagli yontem: %metin%.upper gibi."""

    def __init__(self, ad, nesne, fn):
        self.ad = ad
        self.nesne = nesne
        self.fn = fn

    def __repr__(self):
        return "<yontem %s>" % self.ad


class Gorev:
    """asyn(...) ile baslatilan arka plan isi."""

    def __init__(self, ad):
        self.ad = ad
        self.thread = None
        self.sonuc = None
        self.hata = None
        self.bitti = False

    def bekle(self, sure=None):
        if self.thread is not None:
            self.thread.join(sure)
        if self.hata is not None:
            raise self.hata
        return self.sonuc

    def __repr__(self):
        return "<gorev %s%s>" % (self.ad, " bitti" if self.bitti else " calisiyor")


def cagrilabilir_mi(v):
    return isinstance(v, (Islev, Gomulu, Bagli))


def dogru_mu(v):
    """TON dogruluk kurali: bos olan her sey yanlistir."""
    if v is None or v is False:
        return False
    if v is True:
        return True
    if isinstance(v, (int, float)):
        return v != 0
    if isinstance(v, (str, list, dict, tuple)):
        return len(v) > 0
    return True


def sayi_mi(v):
    return isinstance(v, (int, float)) and not isinstance(v, bool)


def _sayi_metni(v):
    if isinstance(v, float):
        if v != v:
            return "NaN"
        if v in (float("inf"), float("-inf")):
            return "sonsuz" if v > 0 else "-sonsuz"
        if v.is_integer() and abs(v) < 1e16:
            return str(int(v))
        return repr(round(v, 12)).rstrip("0").rstrip(".") if "." in repr(v) else repr(v)
    return str(v)


def metin(v):
    """Degeri ekrana yazilacak hale getirir."""
    if v is None:
        return "null"
    if v is True:
        return "true"
    if v is False:
        return "false"
    if isinstance(v, (int, float)):
        return _sayi_metni(v)
    if isinstance(v, str):
        return v
    if isinstance(v, list):
        return "[" + ", ".join(gosterim(x) for x in v) + "]"
    if isinstance(v, dict):
        return "{" + ", ".join("%s: %s" % (k, gosterim(d)) for k, d in v.items()) + "}"
    if isinstance(v, Isim):
        return "<kutuphane %s>" % v.ad
    if isinstance(v, (Islev, Gomulu, Bagli)):
        return "<is %s>" % v.ad
    if isinstance(v, Gorev):
        return repr(v)
    return str(v)


def gosterim(v):
    """Liste/harita icinde gosterim (metinler tirnakli)."""
    if isinstance(v, str):
        return '"%s"' % v.replace('"', '\\"')
    return metin(v)


def tur(v):
    if v is None:
        return "null"
    if isinstance(v, bool):
        return "bool"
    if isinstance(v, int):
        return "sayi"
    if isinstance(v, float):
        return "ondalik"
    if isinstance(v, str):
        return "metin"
    if isinstance(v, list):
        return "liste"
    if isinstance(v, dict):
        return "harita"
    if isinstance(v, Gorev):
        return "gorev"
    if isinstance(v, Isim):
        return "kutuphane"
    if cagrilabilir_mi(v):
        return "is"
    return type(v).__name__


def pythonlastir(v):
    """TON degerini duz python verisine cevirir (json vb. icin)."""
    if isinstance(v, dict):
        return {str(k): pythonlastir(d) for k, d in v.items()}
    if isinstance(v, (list, tuple)):
        return [pythonlastir(x) for x in v]
    if isinstance(v, (str, int, float, bool)) or v is None:
        return v
    return metin(v)


def tonlastir(v):
    """Python verisini TON degerine cevirir."""
    if isinstance(v, dict):
        return {str(k): tonlastir(d) for k, d in v.items()}
    if isinstance(v, (list, tuple, set)):
        return [tonlastir(x) for x in v]
    if isinstance(v, (str, int, float, bool)) or v is None:
        return v
    return metin(v)
