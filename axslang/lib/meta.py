"""Ustprogramlama (metaprogramlama): kodun kendini yazmasi.

    meta("print: merhaba")             # metni kod olarak calistir
    define("iki_kat", ["x"], "return %x% * 2")
    print: iki_kat(21)
"""

from ..errors import TonRuntimeError, TonTypeError
from ..values import Islev, cagrilabilir_mi, metin as _metin, tur as _tur
from . import gomulu


@gomulu("meta", "kodu_calistir", yorumlayici=True)
def kodu_calistir(y, kod, degiskenler=None):
    from ..interpreter import Kapsam
    kapsam = y.evren
    if degiskenler:
        if not isinstance(degiskenler, dict):
            raise TonTypeError("meta() ikinci deger olarak harita ister")
        kapsam = Kapsam(y.evren, {str(k): v for k, v in degiskenler.items()})
    return y.calistir_kaynak(_metin(kod), "<meta>", kapsam)


@gomulu("eval_ton", "degerini_bul", yorumlayici=True)
def degerini_bul(y, ifade, degiskenler=None):
    return kodu_calistir(y, "_meta_sonuc = " + _metin(ifade), degiskenler) or \
        y.evren.bul("_meta_sonuc")


@gomulu("define", "tanimla", yorumlayici=True)
def tanimla(y, ad, parametreler=None, kod=""):
    from ..parser import cozumle
    adlar = [_metin(p) for p in (parametreler or [])]
    govde = cozumle(_metin(kod), "<tanimla:%s>" % _metin(ad))
    islev = Islev(_metin(ad), [(p, None) for p in adlar], govde, y.evren)
    y.evren.yerel(_metin(ad), islev)
    return islev


@gomulu("defined", "tanimli_mi", yorumlayici=True)
def tanimli_mi(y, ad):
    ad = _metin(ad)
    return y.evren.var_mi(ad) or ad in y.gomulu


@gomulu("get_var", "degeri", yorumlayici=True)
def degeri(y, ad, varsayilan=None):
    ad = _metin(ad)
    try:
        return y.evren.bul(ad)
    except KeyError:
        return y.gomulu.get(ad, varsayilan)


@gomulu("set_var", "degeri_ayarla", yorumlayici=True)
def degeri_ayarla(y, ad, deger):
    y.evren.ata(_metin(ad), deger)
    return deger


@gomulu("names", "adlar", yorumlayici=True)
def adlar(y, tur_suzgeci=None):
    cikti = []
    for ad, deger in y.evren.degerler.items():
        if ad.startswith("_"):
            continue
        if tur_suzgeci is None or _tur(deger) == _metin(tur_suzgeci):
            cikti.append(ad)
    return sorted(cikti)


@gomulu("builtins", "hazir_isler", yorumlayici=True)
def hazir_isler(y):
    return sorted(y.gomulu.keys())


@gomulu("call", "cagir", yorumlayici=True)
def cagir(y, hedef, argumanlar=None):
    if isinstance(hedef, str):
        bulunan = degeri(y, hedef)
        if bulunan is None:
            raise TonRuntimeError("'%s' adinda bir is yok" % hedef)
        hedef = bulunan
    if not cagrilabilir_mi(hedef):
        raise TonTypeError("%s cagrilamaz" % _tur(hedef))
    return y.cagir(hedef, list(argumanlar or []))


@gomulu("template", "sablon", yorumlayici=True)
def sablon(y, metin_sablonu, degerler=None):
    """Metindeki %ad% yerlerini haritadaki degerlerle doldurur."""
    from ..interpreter import Kapsam
    from ..lexer import metin_parcala
    kapsam = Kapsam(y.evren, {str(k): v for k, v in (degerler or {}).items()})
    return y.metin_kur(metin_parcala(_metin(metin_sablonu), 0), kapsam, 0)


@gomulu("params", "parametreleri")
def parametreleri(islev):
    if isinstance(islev, Islev):
        return [p[0] for p in islev.parametreler]
    return []
