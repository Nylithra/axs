"""Matematik isleri."""

import math

from ..errors import TonRuntimeError
from ..values import sayi_mi
from . import gomulu


def _s(v, ad):
    if not sayi_mi(v):
        from .cekirdek import sayiya
        return sayiya(v)
    return v


@gomulu("abs", "mutlak")
def mutlak(x):
    return abs(_s(x, "mutlak"))


@gomulu("round", "yuvarla")
def yuvarla(x, basamak=0):
    x = _s(x, "yuvarla")
    sonuc = round(x, int(basamak))
    return int(sonuc) if int(basamak) <= 0 else sonuc


@gomulu("floor", "asagi")
def asagi(x):
    return math.floor(_s(x, "asagi"))


@gomulu("ceil", "yukari")
def yukari(x):
    return math.ceil(_s(x, "yukari"))


@gomulu("sqrt", "karekok")
def karekok(x):
    x = _s(x, "karekok")
    if x < 0:
        raise TonRuntimeError("Negatif sayinin karekoku alinamaz")
    return math.sqrt(x)


@gomulu("pow", "us")
def us(x, y):
    return _s(x, "us") ** _s(y, "us")


@gomulu("sin")
def _sin(x):
    return math.sin(_s(x, "sin"))


@gomulu("cos")
def _cos(x):
    return math.cos(_s(x, "cos"))


@gomulu("tan")
def _tan(x):
    return math.tan(_s(x, "tan"))


@gomulu("log")
def _log(x, taban=None):
    x = _s(x, "log")
    return math.log(x, _s(taban, "log")) if taban is not None else math.log(x)


@gomulu("pi")
def _pi():
    return math.pi


@gomulu("percent", "yuzde")
def yuzde(parca, butun):
    butun = _s(butun, "yuzde")
    if butun == 0:
        return 0
    return _s(parca, "yuzde") * 100.0 / butun


@gomulu("clamp", "sinirla")
def sinirla(x, alt, ust):
    return max(_s(alt, "sinirla"), min(_s(x, "sinirla"), _s(ust, "sinirla")))
