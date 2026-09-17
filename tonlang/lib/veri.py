"""Buyuk veri isleri: data()

Dosyalar satir satir okunur; milyonlarca satir bellege sigmadan islenir.

    veri = data("satislar.csv")
    print: %veri%.count()
    buyukler = %veri%.filter(func(s) -> %s.tutar% > 1000)
    print: %buyukler%.sum("tutar")
"""

import csv
import json as _json
import os

from ..errors import TonRuntimeError, TonTypeError
from ..values import Isim, dogru_mu, metin as _metin, sayi_mi, tonlastir
from . import gomulu, isim_alani


def _sayi(v):
    if sayi_mi(v):
        return v
    try:
        return float(_metin(v).replace(",", "."))
    except (ValueError, TypeError):
        return None


class Veri:
    """Tembel (lazy) veri akisi."""

    def __init__(self, y, kaynak, ad="veri"):
        self.y = y
        self.kaynak = kaynak          # cagrilinca yeni bir iterator veren is
        self.ad = ad

    def __iter__(self):
        return iter(self.kaynak())

    def zincir(self, fn, ad=None):
        return Veri(self.y, lambda: fn(self.kaynak()), ad or self.ad)


def _dosya_akisi(yol):
    uzanti = os.path.splitext(yol)[1].lower()

    def ac():
        if uzanti in (".csv", ".tsv"):
            ayirac = "\t" if uzanti == ".tsv" else ","
            with open(yol, encoding="utf-8", newline="") as f:
                for satir in csv.DictReader(f, delimiter=ayirac):
                    yield {k: _cevir(v) for k, v in satir.items() if k is not None}
        elif uzanti in (".jsonl", ".ndjson"):
            with open(yol, encoding="utf-8") as f:
                for satir in f:
                    satir = satir.strip()
                    if satir:
                        yield tonlastir(_json.loads(satir))
        elif uzanti == ".json":
            with open(yol, encoding="utf-8") as f:
                veri = tonlastir(_json.load(f))
            if isinstance(veri, list):
                yield from veri
            else:
                yield veri
        else:
            with open(yol, encoding="utf-8") as f:
                for satir in f:
                    yield satir.rstrip("\n")
    return ac


def _cevir(deger):
    if deger is None or deger == "":
        return deger
    ham = deger.strip()
    try:
        return int(ham)
    except ValueError:
        pass
    try:
        return float(ham)
    except ValueError:
        return deger


def _alan(satir, ad):
    if ad is None:
        return satir
    if isinstance(satir, dict):
        return satir.get(_metin(ad))
    return satir


def _sar(veri):
    """Veri nesnesini TON kutuphane nesnesine cevirir."""
    y = veri.y

    def satirlar(sinir=None):
        if sinir is None:
            return list(veri)
        cikti = []
        for i, satir in enumerate(veri):
            if i >= int(sinir):
                break
            cikti.append(satir)
        return cikti

    def sec(is_):
        return _sar(veri.zincir(lambda it: (s for s in it if dogru_mu(y.cagir(is_, [s])))))

    def donustur(is_):
        return _sar(veri.zincir(lambda it: (y.cagir(is_, [s]) for s in it)))

    def alanlar_sec(*adlar):
        secilen = [_metin(a) for a in (adlar[0] if len(adlar) == 1 and isinstance(adlar[0], list)
                                       else adlar)]
        return _sar(veri.zincir(
            lambda it: ({k: s.get(k) for k in secilen} if isinstance(s, dict) else s
                        for s in it)))

    def sayisi():
        n = 0
        for _ in veri:
            n += 1
        return n

    def toplam(alan=None):
        t = 0
        for s in veri:
            d = _sayi(_alan(s, alan))
            if d is not None:
                t += d
        return t

    def ortalama(alan=None):
        t, n = 0, 0
        for s in veri:
            d = _sayi(_alan(s, alan))
            if d is not None:
                t += d
                n += 1
        return t / n if n else 0

    def enaz(alan=None):
        return _uc(alan, min)

    def encok(alan=None):
        return _uc(alan, max)

    def _uc(alan, fn):
        sonuc = None
        for s in veri:
            d = _sayi(_alan(s, alan))
            if d is None:
                continue
            sonuc = d if sonuc is None else fn(sonuc, d)
        return sonuc

    def grupla(alan):
        cikti = {}
        for s in veri:
            anahtar = _metin(_alan(s, alan))
            cikti[anahtar] = cikti.get(anahtar, 0) + 1
        return cikti

    def toplamlar(alan, deger_alani):
        cikti = {}
        for s in veri:
            anahtar = _metin(_alan(s, alan))
            d = _sayi(_alan(s, deger_alani)) or 0
            cikti[anahtar] = cikti.get(anahtar, 0) + d
        return cikti

    def sirala(alan=None, tersten=False):
        ogeler = list(veri)
        ogeler.sort(key=_sirala_anahtari(alan), reverse=dogru_mu(tersten))
        return _sar(Veri(y, lambda: iter(ogeler), veri.ad))

    def _sirala_anahtari(alan):
        def anahtar(s):
            d = _sayi(_alan(s, alan))
            return (0, d, "") if d is not None else (1, 0, _metin(_alan(s, alan)))
        return anahtar

    def ustten(adet=10, alan=None):
        ogeler = list(veri)
        ogeler.sort(key=_sirala_anahtari(alan), reverse=True)
        return ogeler[:int(adet)]

    def altdan(adet=10, alan=None):
        ogeler = list(veri)
        ogeler.sort(key=_sirala_anahtari(alan))
        return ogeler[:int(adet)]

    def sutun(alan):
        return [_alan(s, alan) for s in veri]

    def hepsi_calistir(is_):
        for s in veri:
            y.cagir(is_, [s])
        return True

    def kaydet(dosya):
        yol = _metin(dosya)
        if not os.path.isabs(yol):
            yol = os.path.join(y.kok, yol)
        uzanti = os.path.splitext(yol)[1].lower()
        ogeler = list(veri)
        if uzanti == ".json":
            with open(yol, "w", encoding="utf-8") as f:
                from ..values import pythonlastir
                _json.dump(pythonlastir(ogeler), f, ensure_ascii=False, indent=2)
        elif uzanti in (".csv", ".tsv"):
            if not ogeler or not isinstance(ogeler[0], dict):
                raise TonTypeError("CSV olarak kaydetmek icin satirlar harita olmali")
            ayirac = "\t" if uzanti == ".tsv" else ","
            with open(yol, "w", encoding="utf-8", newline="") as f:
                yazici = csv.DictWriter(f, fieldnames=list(ogeler[0].keys()), delimiter=ayirac)
                yazici.writeheader()
                for s in ogeler:
                    yazici.writerow({k: _metin(v) for k, v in s.items()})
        else:
            with open(yol, "w", encoding="utf-8") as f:
                for s in ogeler:
                    f.write(_metin(s) + "\n")
        return yol

    alan_nesnesi = isim_alani("veri", {
        "rows": satirlar, "satirlar": satirlar,
        "head": lambda adet=10: satirlar(adet), "ilk": lambda adet=10: satirlar(adet),
        "filter": sec, "sec": sec,
        "map": donustur, "donustur": donustur,
        "select": alanlar_sec, "alanlar": alanlar_sec,
        "count": sayisi, "sayisi": sayisi,
        "sum": toplam, "topla": toplam,
        "avg": ortalama, "ortalama": ortalama,
        "min": enaz, "enaz": enaz,
        "max": encok, "encok": encok,
        "group": grupla, "grupla": grupla,
        "totals": toplamlar, "toplamlar": toplamlar,
        "sort": sirala, "sirala": sirala,
        "column": sutun, "sutun": sutun,
        "each": hepsi_calistir, "hepsi": hepsi_calistir,
        "save": kaydet, "kaydet": kaydet,
        "top": ustten, "ust": ustten,
        "bottom": altdan, "alt": altdan,
        "kaynak": veri.ad,
    })
    return alan_nesnesi


@gomulu("data", "veri", yorumlayici=True)
def veri_ac(y, kaynak, tur=None):
    if isinstance(kaynak, list):
        ogeler = list(kaynak)
        return _sar(Veri(y, lambda: iter(ogeler), "liste"))
    if isinstance(kaynak, Isim) and kaynak.ad == "veri":
        return kaynak
    yol = _metin(kaynak)
    if not os.path.isabs(yol):
        yol = os.path.join(y.kok, yol)
    if not os.path.isfile(yol):
        raise TonRuntimeError("Veri dosyasi bulunamadi: %s" % _metin(kaynak))
    return _sar(Veri(y, _dosya_akisi(yol), os.path.basename(yol)))
