"""Baglanti isleri: connect(), get(), post(), indir().

TON'da her tur baglanti ayni kelimeyle kurulur:

    api = connect(https://api.lanux.online)
    db  = connect(veriler.db)
"""

import json as _json
import os
import ssl
import urllib.error
import urllib.parse
import urllib.request

from ..errors import TonRuntimeError
from ..values import Isim, metin as _metin, pythonlastir, tonlastir
from . import gomulu, isim_alani

ZAMAN_ASIMI = 30
BASLIK = {"User-Agent": "TON/1.0", "Accept": "*/*"}


def _cevap_coz(ham, tur_basligi):
    metin = ham.decode("utf-8", "replace")
    if "json" in (tur_basligi or "").lower():
        try:
            return tonlastir(_json.loads(metin))
        except ValueError:
            return metin
    kirp = metin.lstrip()
    if kirp[:1] in "{[":
        try:
            return tonlastir(_json.loads(metin))
        except ValueError:
            return metin
    return metin


def _istek(yontem, adres, veri=None, basliklar=None, zaman_asimi=None, ham=False):
    govde = None
    basliklar = dict(BASLIK, **{k: _metin(v) for k, v in (basliklar or {}).items()})
    if veri is not None:
        if isinstance(veri, (dict, list)):
            govde = _json.dumps(pythonlastir(veri), ensure_ascii=False,
                                separators=(",", ":")).encode("utf-8")
            basliklar.setdefault("Content-Type", "application/json; charset=utf-8")
        else:
            govde = _metin(veri).encode("utf-8")
            basliklar.setdefault("Content-Type", "text/plain; charset=utf-8")
    istek = urllib.request.Request(adres, data=govde, headers=basliklar, method=yontem)
    baglam = ssl.create_default_context()
    ca = os.environ.get("REQUESTS_CA_BUNDLE") or os.environ.get("SSL_CERT_FILE")
    if ca and os.path.exists(ca):
        baglam.load_verify_locations(ca)
    try:
        with urllib.request.urlopen(istek, timeout=zaman_asimi or ZAMAN_ASIMI,
                                    context=baglam) as c:
            icerik = c.read()
            return {
                "durum": c.status,
                "basarili": 200 <= c.status < 300,
                "basliklar": {k.lower(): v for k, v in c.headers.items()},
                "veri": icerik if ham else _cevap_coz(icerik, c.headers.get("Content-Type")),
            }
    except urllib.error.HTTPError as e:
        icerik = e.read()
        return {
            "durum": e.code,
            "basarili": False,
            "basliklar": {k.lower(): v for k, v in (e.headers or {}).items()},
            "veri": icerik if ham else _cevap_coz(icerik, (e.headers or {}).get("Content-Type")),
        }
    except urllib.error.URLError as e:
        raise TonRuntimeError("Baglanti kurulamadi (%s): %s" % (adres, e.reason))
    except (OSError, ValueError) as e:
        raise TonRuntimeError("Baglanti hatasi (%s): %s" % (adres, e))


def _adres_kur(temel, yol, parametreler=None):
    if yol is None:
        yol = ""
    yol = _metin(yol)
    if "://" in yol:
        adres = yol
    elif not temel:
        adres = yol
    else:
        adres = temel.rstrip("/") + "/" + yol.lstrip("/") if yol else temel
    if parametreler:
        ek = urllib.parse.urlencode({k: _metin(v) for k, v in parametreler.items()})
        adres += ("&" if "?" in adres else "?") + ek
    return adres


# ---------------------------------------------------------------- tek seferlik
def _basariyi_dogrula(cevap, adres):
    """Sunucu hata dondurduyse sessizce gecmeyelim."""
    if cevap["basarili"]:
        return cevap["veri"]
    ozet = _metin(cevap["veri"])
    if len(ozet) > 200:
        ozet = ozet[:200] + "..."
    raise TonRuntimeError("Istek basarisiz (%s) %s: %s" % (cevap["durum"], adres, ozet))


@gomulu("get", "getir")
def getir(adres, parametreler=None, basliklar=None, zaman_asimi=None):
    tam = _adres_kur("", adres, parametreler)
    return _basariyi_dogrula(_istek("GET", tam, None, basliklar, zaman_asimi), tam)


@gomulu("post", "gonder")
def gonder(adres, veri=None, basliklar=None, zaman_asimi=None):
    tam = _adres_kur("", adres)
    return _basariyi_dogrula(_istek("POST", tam, veri, basliklar, zaman_asimi), tam)


@gomulu("request", "istek")
def istek(adres, yontem="GET", veri=None, basliklar=None, zaman_asimi=None):
    return _istek(_metin(yontem).upper(), _adres_kur("", adres), veri, basliklar, zaman_asimi)


@gomulu("download", "indir", yorumlayici=True)
def indir(y, adres, dosya=None):
    c = _istek("GET", _adres_kur("", adres), ham=True)
    if not c["basarili"]:
        raise TonRuntimeError("Indirilemedi (%s): %s" % (c["durum"], adres))
    ad = _metin(dosya) if dosya else os.path.basename(urllib.parse.urlparse(adres).path) or "indirilen"
    yol = ad if os.path.isabs(ad) else os.path.join(y.kok, ad)
    with open(yol, "wb") as f:
        f.write(c["veri"])
    return yol


@gomulu("encode", "adresle")
def adresle(deger):
    return urllib.parse.quote(_metin(deger), safe="")


# ---------------------------------------------------------------- connect()
def _http_baglanti(adres):
    durum = {"adres": adres.rstrip("/"), "durum": 0, "basarili": False, "son": None}

    def cagir(yontem):
        def fn(yol="", veri=None, parametreler=None, basliklar=None, zaman_asimi=None):
            c = _istek(yontem, _adres_kur(durum["adres"], yol, parametreler),
                       veri, basliklar, zaman_asimi)
            durum["durum"] = c["durum"]
            durum["basarili"] = c["basarili"]
            durum["son"] = c
            alan.uyeler["durum"] = c["durum"]
            alan.uyeler["basarili"] = c["basarili"]
            alan.uyeler["son"] = c
            return _basariyi_dogrula(c, durum["adres"] + "/" + _metin(yol).lstrip("/"))
        return fn

    def ping():
        try:
            c = _istek("GET", durum["adres"])
            return bool(c["durum"])
        except TonRuntimeError:
            return False

    alan = isim_alani("baglanti", {
        "adres": durum["adres"],
        "durum": 0,
        "basarili": False,
        "son": None,
        "tur": "http",
        "get": cagir("GET"),
        "getir": cagir("GET"),
        "post": cagir("POST"),
        "gonder": cagir("POST"),
        "put": cagir("PUT"),
        "patch": cagir("PATCH"),
        "delete": cagir("DELETE"),
        "sil": cagir("DELETE"),
        "ping": ping,
        "kapat": lambda: True,
        "close": lambda: True,
    })
    return alan


def _veritabani_baglanti(yol):
    import sqlite3

    baglanti = sqlite3.connect(yol, check_same_thread=False)
    baglanti.row_factory = sqlite3.Row

    def _calistir(sql, *degerler):
        try:
            imlec = baglanti.execute(_metin(sql), _duzle(degerler))
        except sqlite3.Error as e:
            raise TonRuntimeError("SQL hatasi: %s" % e)
        return imlec

    def _duzle(degerler):
        if len(degerler) == 1 and isinstance(degerler[0], (list, tuple)):
            return [pythonlastir(d) for d in degerler[0]]
        return [pythonlastir(d) for d in degerler]

    def run(sql, *degerler):
        imlec = _calistir(sql, *degerler)
        baglanti.commit()
        return imlec.rowcount if imlec.rowcount >= 0 else 0

    def hepsi(sql, *degerler):
        return [dict(satir) for satir in _calistir(sql, *degerler).fetchall()]

    def tek(sql, *degerler):
        satir = _calistir(sql, *degerler).fetchone()
        return dict(satir) if satir else None

    def tablolar():
        return [s["name"] for s in hepsi(
            "select name from sqlite_master where type='table' order by name")]

    return isim_alani("baglanti", {
        "adres": yol,
        "tur": "veritabani",
        "run": run, "calistir": run,
        "all": hepsi, "hepsi": hepsi,
        "one": tek, "tek": tek,
        "tables": tablolar, "tablolar": tablolar,
        "close": lambda: baglanti.close(),
        "kapat": lambda: baglanti.close(),
    })


@gomulu("connect", "baglan", yorumlayici=True)
def baglan(y, adres, tur=None):
    adres = _metin(adres)
    secim = _metin(tur).lower() if tur else None
    if secim == "http" or (secim is None and adres.startswith(("http://", "https://"))):
        return _http_baglanti(adres)
    if secim in ("db", "veritabani", "sqlite") or adres.endswith((".db", ".sqlite", ".sqlite3")) \
            or adres.startswith("sqlite://"):
        yol = adres[len("sqlite://"):] if adres.startswith("sqlite://") else adres
        if not os.path.isabs(yol):
            yol = os.path.join(y.kok, yol)
        return _veritabani_baglanti(yol)
    if "://" in adres:
        return _http_baglanti(adres)
    return _http_baglanti("https://" + adres)
