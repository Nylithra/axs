"""Axs cekirdek kutuphanesi: hazir isler, yontemler ve modul yukleyici."""

from ..values import Gomulu, Isim, tur

KAYIT = {}
YONTEMLER = {"metin": {}, "liste": {}, "harita": {}, "gorev": {}, "sayi": {}, "ondalik": {}}
KUTUPHANELER = {}


def gomulu(ad, *takma, yorumlayici=False):
    """Hazir bir isi kaydeder."""
    def sar(fn):
        b = Gomulu(ad, fn, yorumlayici)
        KAYIT[ad] = b
        for t in takma:
            KAYIT[t] = b
        return fn
    return sar


def yontem(turler, ad, *takma):
    """Bir deger turune yontem ekler: %metin%.upper() gibi."""
    if isinstance(turler, str):
        turler = [turler]

    def sar(fn):
        for t in turler:
            YONTEMLER.setdefault(t, {})[ad] = fn
            for k in takma:
                YONTEMLER[t][k] = fn
        return fn
    return sar


def kutuphane(ad, *takma):
    """Bir kutuphane yukleyicisi kaydeder: use web"""
    def sar(fn):
        KUTUPHANELER[ad] = fn
        for t in takma:
            KUTUPHANELER[t] = fn
        return fn
    return sar


def isim_alani(ad, uyeler, yorumlayici_isteyenler=()):
    """Python sozlugunden Axs kutuphane nesnesi uretir."""
    cikti = {}
    for k, v in uyeler.items():
        if callable(v) and not isinstance(v, (Gomulu, Isim)):
            cikti[k] = Gomulu("%s.%s" % (ad, k), v, k in yorumlayici_isteyenler)
        else:
            cikti[k] = v
    return Isim(ad, cikti)


def yontem_bul(nesne, ad):
    return YONTEMLER.get(tur(nesne), {}).get(ad)


# Cekirdek disi kutuphaneler: `use web` dendiginde bulunup yuklenir
DIS_KUTUPHANELER = {"web": "axsweb", "axsweb": "axsweb"}


def kutuphane_yukle(yorumlayici, ad):
    yukleyici = KUTUPHANELER.get(ad)
    if yukleyici is None and ad in DIS_KUTUPHANELER:
        try:
            __import__(DIS_KUTUPHANELER[ad])
        except ImportError:
            return None
        yukleyici = KUTUPHANELER.get(ad)
    if yukleyici is None:
        return None
    return yukleyici(yorumlayici)


def gomululeri_yukle():
    from . import (ag, cekirdek, dosya, esyamanli, koleksiyon, matematik,  # noqa: F401
                   meta, metin, soket, veri, zeka)
    return dict(KAYIT)


def hem(turler, ad, *takma, yorumlayici=False):
    """Bir isi hem hazir is hem de yontem olarak kaydeder.

    fn imzasi: (nesne, *args)  ya da yorumlayici=True ise (y, nesne, *args)
    """
    def sar(fn):
        gomulu(ad, *takma, yorumlayici=yorumlayici)(fn)
        if yorumlayici:
            yontem(turler, ad, *takma)(fn)
        else:
            def yontem_sarmal(y, nesne, *a, **kw):
                return fn(nesne, *a, **kw)
            yontem_sarmal.__name__ = ad
            yontem(turler, ad, *takma)(yontem_sarmal)
        return fn
    return sar
