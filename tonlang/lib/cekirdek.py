"""Cekirdek hazir isler: yazdirma, sorma, donusum, tur bilgisi."""

import datetime
import json as _json
import random as _random
import sys
import time

from ..errors import TonRuntimeError, TonTypeError, TonUserError
from ..values import (dogru_mu, gosterim, metin as _metin, pythonlastir, sayi_mi,
                      tonlastir, tur as _tur)
from . import gomulu, hem


@gomulu("print", "yaz", "say", "goster", yorumlayici=True)
def yazdir(y, *degerler, ayirac=" ", son="\n"):
    y.cikti(ayirac.join(_metin(d) for d in degerler) + son)


@gomulu("write", "yazdir", yorumlayici=True)
def yaz_satirsiz(y, *degerler):
    y.cikti("".join(_metin(d) for d in degerler))


@gomulu("ask", "sor", yorumlayici=True)
def sor(y, soru="", varsayilan=None):
    if soru:
        y.cikti(_metin(soru) + (" " if not soru.endswith(" ") else ""))
    try:
        cevap = sys.stdin.readline()
    except (EOFError, KeyboardInterrupt):
        cevap = ""
    if cevap == "":
        return varsayilan if varsayilan is not None else ""
    cevap = cevap.rstrip("\n")
    return cevap if cevap != "" or varsayilan is None else varsayilan


@hem(["metin", "liste", "harita"], "len", "uzunluk", "say_adet")
def uzunluk(deger):
    if deger is None:
        return 0
    if isinstance(deger, (str, list, dict, tuple)):
        return len(deger)
    raise TonTypeError("%s icin uzunluk yok" % _tur(deger))


@hem(["metin", "liste", "harita", "sayi", "ondalik", "gorev"], "type", "tur")
def turu(deger):
    return _tur(deger)


@gomulu("text", "metin", "str")
def metne(deger, basamak=None):
    if basamak is not None and sayi_mi(deger):
        return ("%%.%df" % int(basamak)) % float(deger)
    return _metin(deger)


@gomulu("number", "sayi", "num")
def sayiya(deger, varsayilan=None):
    if sayi_mi(deger):
        return deger
    if isinstance(deger, bool):
        return 1 if deger else 0
    if isinstance(deger, str):
        ham = deger.strip().replace(",", ".")
        try:
            return int(ham)
        except ValueError:
            try:
                return float(ham)
            except ValueError:
                pass
    if varsayilan is not None:
        return varsayilan
    raise TonTypeError("'%s' sayiya cevrilemedi" % _metin(deger))


@gomulu("int", "tam")
def tama(deger):
    return int(sayiya(deger))


@gomulu("bool", "mantik")
def mantiga(deger):
    return dogru_mu(deger)


@gomulu("liste", "tolist")
def listeye(deger=None):
    if deger is None:
        return []
    if isinstance(deger, list):
        return list(deger)
    if isinstance(deger, dict):
        return list(deger.keys())
    if isinstance(deger, str):
        return list(deger)
    if isinstance(deger, tuple):
        return list(deger)
    return [deger]


@gomulu("harita", "tomap")
def haritaya(deger=None):
    if deger is None:
        return {}
    if isinstance(deger, dict):
        return dict(deger)
    if isinstance(deger, list):
        cikti = {}
        for oge in deger:
            if isinstance(oge, (list, tuple)) and len(oge) == 2:
                cikti[_metin(oge[0])] = oge[1]
            else:
                raise TonTypeError("Haritaya cevirmek icin [anahtar, deger] ciftleri gerekir")
        return cikti
    raise TonTypeError("%s haritaya cevrilemez" % _tur(deger))


@hem(["liste", "harita"], "copy", "kopya")
def kopyala(deger):
    if isinstance(deger, list):
        return list(deger)
    if isinstance(deger, dict):
        return dict(deger)
    return deger


@gomulu("is_empty", "bos_mu")
def bos_mu(deger):
    return not dogru_mu(deger)


@gomulu("error", "hata")
def hata_firlat(mesaj="Hata"):
    raise TonUserError(_metin(mesaj))


@gomulu("exit", "cik")
def cik(kod=0):
    raise SystemExit(int(kod) if sayi_mi(kod) else 0)


@gomulu("json", "jsonoku")
def json_oku(ham):
    if isinstance(ham, (dict, list)):
        return ham
    try:
        return tonlastir(_json.loads(ham))
    except (ValueError, TypeError) as e:
        raise TonRuntimeError("JSON okunamadi: %s" % e)


@hem(["liste", "harita", "metin"], "tojson", "jsonyaz")
def json_yaz(deger, guzel=False):
    # Bosluksuz bicim: JavaScript'in JSON.stringify ciktisiyla ayni olsun
    if dogru_mu(guzel):
        return _json.dumps(pythonlastir(deger), ensure_ascii=False, indent=2)
    return _json.dumps(pythonlastir(deger), ensure_ascii=False,
                       separators=(",", ":"))


@gomulu("now", "simdi")
def simdi(bicim=None):
    an = datetime.datetime.now()
    if bicim:
        return an.strftime(_metin(bicim))
    return {
        "yil": an.year, "ay": an.month, "gun": an.day,
        "saat": an.hour, "dakika": an.minute, "saniye": an.second,
        "metin": an.strftime("%Y-%m-%d %H:%M:%S"),
        "zaman": time.time(),
    }


@gomulu("timestamp", "zaman")
def zaman():
    return time.time()


@gomulu("random", "rastgele")
def rastgele(alt=None, ust=None):
    if alt is None:
        return _random.random()
    if ust is None:
        alt, ust = 1, alt
    if not (sayi_mi(alt) and sayi_mi(ust)):
        raise TonTypeError("rastgele(alt, ust) sayi ister")
    if isinstance(alt, int) and isinstance(ust, int):
        return _random.randint(alt, ust)
    return _random.uniform(alt, ust)


@gomulu("pick", "sec_rastgele")
def sec_rastgele(liste):
    if not liste:
        raise TonRuntimeError("Bos listeden secim yapilamaz")
    return _random.choice(list(liste))


@gomulu("shuffle", "karistir")
def karistir(liste):
    yeni = list(liste)
    _random.shuffle(yeni)
    return yeni


@gomulu("show", "gosterimi")
def gosterimi(deger):
    return gosterim(deger)
