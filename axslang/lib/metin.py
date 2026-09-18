"""Metin isleri: hem hazir is hem yontem olarak kullanilir.

    %ad%.upper()      upper(%ad%)
"""

import re as _re

from ..errors import AxsTypeError
from ..values import metin as _metin, tur as _tur
from . import gomulu, hem


def _m(deger):
    if isinstance(deger, str):
        return deger
    return _metin(deger)


@hem("metin", "upper", "buyuk")
def buyuk(s):
    return _m(s).upper()


@hem("metin", "lower", "kucuk")
def kucuk(s):
    return _m(s).lower()


@hem("metin", "trim", "kirp")
def kirp(s, karakterler=None):
    return _m(s).strip(karakterler) if karakterler else _m(s).strip()


@hem("metin", "title", "basharf")
def basharf(s):
    return " ".join(p[:1].upper() + p[1:] for p in _m(s).split(" "))


@hem("metin", "split", "ayir")
def ayir(s, ayirac=None, adet=None):
    s = _m(s)
    if ayirac is None:
        return s.split()
    if adet is not None:
        return s.split(_m(ayirac), int(adet))
    return s.split(_m(ayirac))


@hem(["liste", "metin"], "join", "birlestir")
def birlestir(ogeler, ayirac=""):
    if isinstance(ogeler, str):
        ogeler, ayirac = ayirac, ogeler
    return _m(ayirac).join(_metin(o) for o in ogeler)


@hem("metin", "replace", "degistir")
def degistir(s, eski, yeni="", adet=None):
    if adet is None:
        return _m(s).replace(_m(eski), _m(yeni))
    return _m(s).replace(_m(eski), _m(yeni), int(adet))


@hem(["metin", "liste", "harita"], "contains", "icerir")
def icerir(kap, parca):
    if isinstance(kap, str):
        return _m(parca) in kap
    if isinstance(kap, dict):
        return _metin(parca) in kap
    if isinstance(kap, (list, tuple)):
        return parca in kap
    raise AxsTypeError("%s icinde arama yapilamaz" % _tur(kap))


@hem("metin", "starts", "ile_baslar")
def ile_baslar(s, parca):
    return _m(s).startswith(_m(parca))


@hem("metin", "ends", "ile_biter")
def ile_biter(s, parca):
    return _m(s).endswith(_m(parca))


@hem(["metin", "liste"], "find", "bul")
def bul(kap, parca):
    if isinstance(kap, str):
        return kap.find(_m(parca))
    try:
        return list(kap).index(parca)
    except ValueError:
        return -1


@hem(["metin", "liste"], "slice", "kes")
def kes(kap, bas=0, son=None):
    bas = int(bas)
    if son is None:
        return kap[bas:]
    return kap[bas:int(son)]


@hem(["metin", "liste"], "reverse", "ters")
def ters(kap):
    if isinstance(kap, str):
        return kap[::-1]
    return list(kap)[::-1]


@hem("metin", "repeat_text", "tekrarla_metin")
def tekrarla_metin(s, adet):
    return _m(s) * int(adet)


@hem("metin", "lines", "satirlar")
def satirlar(s):
    return _m(s).splitlines()


@hem(["metin", "liste"], "count", "adet")
def adet(kap, parca):
    if isinstance(kap, str):
        return kap.count(_m(parca))
    return list(kap).count(parca)


@hem("metin", "pad", "doldur")
def doldur(s, uzunluk, karakter=" ", sag=True):
    s = _m(s)
    k = _m(karakter)[:1] or " "
    return s.ljust(int(uzunluk), k) if sag else s.rjust(int(uzunluk), k)


@hem("metin", "match", "esles")
def esles(s, desen):
    m = _re.search(_m(desen), _m(s))
    if not m:
        return None
    return list(m.groups()) if m.groups() else m.group(0)


@hem("metin", "matches", "eslesenler")
def eslesenler(s, desen):
    return [list(m) if isinstance(m, tuple) else m
            for m in _re.findall(_m(desen), _m(s))]


@hem("metin", "clean", "temizle")
def temizle(s):
    return " ".join(_m(s).split())


@gomulu("chars", "karakterler")
def karakterler(s):
    return list(_m(s))


@gomulu("code", "kod")
def kod(karakter):
    return ord(_m(karakter)[0])


@gomulu("char", "karakter")
def karakter(sayi):
    return chr(int(sayi))
