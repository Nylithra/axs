"""Liste ve harita isleri."""

from ..errors import AxsRuntimeError, AxsTypeError
from ..values import dogru_mu, metin as _metin, sayi_mi, tur as _tur
from . import gomulu, hem, yontem


def _liste(v, ad="bu is"):
    if isinstance(v, list):
        return v
    if isinstance(v, (tuple, set)):
        return list(v)
    if isinstance(v, dict):
        return list(v.keys())
    if isinstance(v, str):
        return list(v)
    raise AxsTypeError("%s bir liste ister, %s verildi" % (ad, _tur(v)))


@hem("liste", "push", "ekle")
def ekle(liste, *degerler):
    if not isinstance(liste, list):
        raise AxsTypeError("ekle() bir liste ister, %s verildi" % _tur(liste))
    liste.extend(degerler)
    return liste


@hem("liste", "pop", "cikar_son")
def cikar_son(liste, sira=None):
    if not liste:
        return None
    return liste.pop(int(sira) if sira is not None else -1)


@hem("liste", "insert", "araya_ekle")
def araya_ekle(liste, sira, deger):
    liste.insert(int(sira), deger)
    return liste


@hem(["liste", "harita"], "remove", "sil")
def sil(kap, anahtar):
    if isinstance(kap, dict):
        kap.pop(_metin(anahtar), None)
        return kap
    if anahtar in kap:
        kap.remove(anahtar)
    return kap


@hem(["liste", "harita", "metin"], "first", "ilk")
def ilk(kap, adet=None):
    ogeler = _liste(kap, "ilk()")
    if adet is None:
        return ogeler[0] if ogeler else None
    return ogeler[:int(adet)]


@hem(["liste", "harita", "metin"], "last", "son_oge")
def son_oge(kap, adet=None):
    ogeler = _liste(kap, "son_oge()")
    if adet is None:
        return ogeler[-1] if ogeler else None
    return ogeler[-int(adet):]


@hem("liste", "unique", "benzersiz")
def benzersiz(liste):
    cikti = []
    for oge in _liste(liste, "benzersiz()"):
        if oge not in cikti:
            cikti.append(oge)
    return cikti


@hem("liste", "sum", "topla")
def topla(liste, alan=None):
    toplam = 0
    for oge in _liste(liste, "topla()"):
        deger = oge.get(_metin(alan)) if alan is not None and isinstance(oge, dict) else oge
        if sayi_mi(deger):
            toplam += deger
    return toplam


@hem("liste", "avg", "ortalama")
def ortalama(liste, alan=None):
    ogeler = [o.get(_metin(alan)) if alan is not None and isinstance(o, dict) else o
              for o in _liste(liste, "ortalama()")]
    sayilar = [o for o in ogeler if sayi_mi(o)]
    if not sayilar:
        return 0
    return sum(sayilar) / len(sayilar)


@gomulu("min", "enkucuk")
def enkucuk(*degerler):
    ogeler = _yaygin(degerler)
    return min(ogeler) if ogeler else None


@gomulu("max", "enbuyuk")
def enbuyuk(*degerler):
    ogeler = _yaygin(degerler)
    return max(ogeler) if ogeler else None


def _yaygin(degerler):
    if len(degerler) == 1 and isinstance(degerler[0], (list, tuple)):
        return list(degerler[0])
    return list(degerler)


@hem("harita", "keys", "anahtarlar")
def anahtarlar(harita):
    if not isinstance(harita, dict):
        raise AxsTypeError("anahtarlar() bir harita ister, %s verildi" % _tur(harita))
    return list(harita.keys())


@hem("harita", "values", "degerler")
def degerler(harita):
    if not isinstance(harita, dict):
        raise AxsTypeError("degerler() bir harita ister, %s verildi" % _tur(harita))
    return list(harita.values())


@hem("harita", "items", "ciftler")
def ciftler(harita):
    return [[k, v] for k, v in harita.items()]


@hem("harita", "has", "var_mi")
def var_mi(harita, anahtar):
    if isinstance(harita, dict):
        return _metin(anahtar) in harita
    return anahtar in harita


@gomulu("al")
def al(harita, anahtar, varsayilan=None):
    """Haritadan deger okur. `get` adi ag kutuphanesine ayrilmistir (bkz. get(adres))."""
    if isinstance(harita, dict):
        return harita.get(_metin(anahtar), varsayilan)
    if isinstance(harita, (list, str)):
        i = int(anahtar)
        return harita[i] if -len(harita) <= i < len(harita) else varsayilan
    return varsayilan


@yontem("harita", "get", "al")
def _harita_al(y, harita, anahtar, varsayilan=None):
    return al(harita, anahtar, varsayilan)


@hem("harita", "set", "koy")
def koy(harita, anahtar, deger):
    harita[_metin(anahtar)] = deger
    return harita


@hem(["harita", "liste"], "merge", "kaynastir")
def kaynastir(a, b):
    if isinstance(a, dict):
        yeni = dict(a)
        yeni.update(b)
        return yeni
    return list(a) + list(b)


@gomulu("range", "aralik")
def aralik(bas, son=None, adim=1):
    if son is None:
        bas, son = 1, bas
    bas, son, adim = int(bas), int(son), int(adim)
    if adim == 0:
        raise AxsRuntimeError("aralik adimi 0 olamaz")
    return list(range(bas, son + (1 if adim > 0 else -1), adim))


@gomulu("zip", "esle")
def esle(*listeler):
    return [list(t) for t in zip(*[_liste(l, "esle()") for l in listeler])]


@gomulu("flat", "duzlestir")
def duzlestir(liste):
    cikti = []
    for oge in _liste(liste, "duzlestir()"):
        if isinstance(oge, list):
            cikti.extend(duzlestir(oge))
        else:
            cikti.append(oge)
    return cikti


# ---------------------------------------------------------- is alan isler
def _kac_parametre(is_):
    """Verilen is kac deger aliyor? (sira numarasi gerekli mi diye bakilir)"""
    from ..values import Islev
    if isinstance(is_, Islev):
        return len(is_.parametreler)
    return 1


def _oge_args(is_, oge, sira):
    """Is ikinci bir deger aliyorsa sira numarasini da verir."""
    return [oge, sira] if _kac_parametre(is_) >= 2 else [oge]


@hem("liste", "map", "donustur", yorumlayici=True)
def donustur(y, liste, is_):
    return [y.cagir(is_, _oge_args(is_, oge, i))
            for i, oge in enumerate(_liste(liste, "donustur()"))]


@hem("liste", "filter", "sec", yorumlayici=True)
def sec(y, liste, is_):
    return [oge for i, oge in enumerate(_liste(liste, "sec()"))
            if dogru_mu(y.cagir(is_, _oge_args(is_, oge, i)))]


@hem("liste", "reduce", "indirge", yorumlayici=True)
def indirge(y, liste, is_, baslangic=None):
    ogeler = _liste(liste, "indirge()")
    if baslangic is None:
        if not ogeler:
            return None
        toplam, ogeler = ogeler[0], ogeler[1:]
    else:
        toplam = baslangic
    ek = _kac_parametre(is_) >= 3
    for i, oge in enumerate(ogeler):
        toplam = y.cagir(is_, [toplam, oge, i] if ek else [toplam, oge])
    return toplam


@hem(["liste", "harita"], "each", "hepsi", yorumlayici=True)
def hepsi(y, kap, is_):
    if isinstance(kap, dict):
        for k, v in list(kap.items()):
            y.cagir(is_, [k, v])
    else:
        for i, oge in enumerate(_liste(kap, "hepsi()")):
            y.cagir(is_, _oge_args(is_, oge, i))
    return kap


@hem("liste", "sort", "sirala", yorumlayici=True)
def sirala(y, liste, anahtar=None, tersten=False):
    ogeler = list(_liste(liste, "sirala()"))
    if anahtar is None:
        anahtar_fn = None
    elif isinstance(anahtar, str):
        anahtar_fn = lambda o: o.get(anahtar) if isinstance(o, dict) else o  # noqa: E731
    else:
        anahtar_fn = lambda o: y.cagir(anahtar, [o])  # noqa: E731
    try:
        ogeler.sort(key=anahtar_fn, reverse=dogru_mu(tersten))
    except TypeError:
        ogeler.sort(key=lambda o: _metin(anahtar_fn(o) if anahtar_fn else o),
                    reverse=dogru_mu(tersten))
    return ogeler


@hem("liste", "group", "grupla", yorumlayici=True)
def grupla(y, liste, anahtar):
    cikti = {}
    for oge in _liste(liste, "grupla()"):
        if isinstance(anahtar, str):
            k = oge.get(anahtar) if isinstance(oge, dict) else oge
        else:
            k = y.cagir(anahtar, [oge])
        cikti.setdefault(_metin(k), []).append(oge)
    return cikti


@hem("liste", "any", "herhangi", yorumlayici=True)
def herhangi(y, liste, is_=None):
    for oge in _liste(liste, "herhangi()"):
        if dogru_mu(y.cagir(is_, [oge]) if is_ is not None else oge):
            return True
    return False


@hem("liste", "all", "hepsi_dogru", yorumlayici=True)
def hepsi_dogru(y, liste, is_=None):
    for oge in _liste(liste, "hepsi_dogru()"):
        if not dogru_mu(y.cagir(is_, [oge]) if is_ is not None else oge):
            return False
    return True
