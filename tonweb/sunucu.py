"""tonweb sunucusu: yollar, istekler, cevaplar."""

import json as _json
import mimetypes
import os
import threading
import urllib.parse
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer

from tonlang.errors import TonError, TonRuntimeError, TonTypeError
from tonlang.lib import isim_alani, kutuphane
from tonlang.values import (Gomulu, Isim, cagrilabilir_mi, metin as _metin, pythonlastir,
                            tonlastir, tur as _tur)

from . import html as H
from .surum import SURUM


VARSAYILAN_SIMGE = (
    '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 64 64">'
    '<rect width="64" height="64" rx="14" fill="#2f6fed"/>'
    '<text x="32" y="45" font-family="system-ui,sans-serif" font-size="38" '
    'font-weight="700" fill="#fff" text-anchor="middle">T</text></svg>'
).encode("utf-8")


class Cevap:
    """Acik cevap: web.json(), web.redirect(), web.file() bunu uretir."""

    def __init__(self, govde=b"", durum=200, tur="text/html; charset=utf-8", basliklar=None):
        self.govde = govde
        self.durum = durum
        self.tur = tur
        self.basliklar = dict(basliklar or {})

    def __repr__(self):
        return "<cevap %s>" % self.durum


class Uygulama:
    def __init__(self, y):
        self.y = y
        self.yollar = []
        self.duragan = []        # (url_onu, klasor)
        self.sunucu = None
        self.thread = None
        self.sessiz = False
        self.hata_isi = None
        self.bulunamadi_isi = None

    # ---------------------------------------------------------- yol ekleme
    def yol_ekle(self, yontem, desen, isle):
        if not cagrilabilir_mi(isle):
            raise TonTypeError("Yol icin bir is gerekir, %s verildi" % _tur(isle))
        desen = _metin(desen)
        if not desen.startswith("/"):
            desen = "/" + desen
        self.yollar.append({
            "yontem": _metin(yontem).upper(),
            "parcalar": [p for p in desen.strip("/").split("/") if p != ""],
            "desen": desen,
            "is": isle,
        })
        return True

    def eslesme(self, yontem, yol):
        parcalar = [p for p in yol.strip("/").split("/") if p != ""]
        for kayit in self.yollar:
            if kayit["yontem"] not in (yontem, "ANY"):
                continue
            parametreler = self._esles(kayit["parcalar"], parcalar)
            if parametreler is not None:
                return kayit, parametreler
        return None, None

    @staticmethod
    def _esles(desen, parcalar):
        parametreler = {}
        if desen and desen[-1] == "*":
            if len(parcalar) < len(desen) - 1:
                return None
            desen = desen[:-1]
            parametreler["kalan"] = "/".join(parcalar[len(desen):])
            parcalar = parcalar[:len(desen)]
        if len(desen) != len(parcalar):
            return None
        for d, p in zip(desen, parcalar):
            if d.startswith(":"):
                parametreler[d[1:]] = urllib.parse.unquote(p)
            elif d != p:
                return None
        return parametreler


def _sorgu_coz(ham):
    cikti = {}
    for k, v in urllib.parse.parse_qs(ham or "", keep_blank_values=True).items():
        cikti[k] = v[0] if len(v) == 1 else v
    return cikti


def _cerez_coz(ham):
    cikti = {}
    for parca in (ham or "").split(";"):
        if "=" in parca:
            k, v = parca.split("=", 1)
            cikti[k.strip()] = urllib.parse.unquote(v.strip())
    return cikti


def _cevaba_cevir(sonuc):
    if isinstance(sonuc, Cevap):
        return sonuc
    if sonuc is None:
        return Cevap(b"", 204, "text/plain; charset=utf-8")
    if isinstance(sonuc, (dict, list)):
        govde = _json.dumps(pythonlastir(sonuc), ensure_ascii=False).encode("utf-8")
        return Cevap(govde, 200, "application/json; charset=utf-8")
    if isinstance(sonuc, bytes):
        return Cevap(sonuc, 200, "application/octet-stream")
    return Cevap(_metin(sonuc).encode("utf-8"), 200, "text/html; charset=utf-8")


def _isleyici_kur(uygulama):
    y = uygulama.y

    class Isleyici(BaseHTTPRequestHandler):
        server_version = "TONWeb/" + SURUM
        protocol_version = "HTTP/1.1"

        def log_message(self, bicim, *args):
            if not uygulama.sessiz:
                y.cikti("  %s %s\n" % (self.command, self.path))

        def _islem(self, yontem):
            ayrisik = urllib.parse.urlparse(self.path)
            yol = urllib.parse.unquote(ayrisik.path)
            try:
                kayit, parametreler = uygulama.eslesme(yontem, yol)
                if kayit is None:
                    duragan = self._duragan_bul(yol)
                    if duragan is not None:
                        return self._gonder(duragan)
                    return self._gonder(self._bulunamadi(yol))
                istek = self._istek_kur(yontem, yol, ayrisik.query, parametreler)
                sonuc = y.cagir(kayit["is"], [istek])
                return self._gonder(_cevaba_cevir(sonuc))
            except BrokenPipeError:
                return None
            except Exception as e:  # noqa: BLE001 - sunucu ayakta kalmali
                return self._gonder(self._hata(e))

        def _istek_kur(self, yontem, yol, sorgu, parametreler):
            uzunluk = int(self.headers.get("Content-Length") or 0)
            ham = self.rfile.read(uzunluk) if uzunluk else b""
            govde = ham.decode("utf-8", "replace")
            icerik_turu = (self.headers.get("Content-Type") or "").lower()
            if "json" in icerik_turu and govde.strip():
                try:
                    veri = tonlastir(_json.loads(govde))
                except ValueError:
                    veri = {}
            elif "form-urlencoded" in icerik_turu:
                veri = _sorgu_coz(govde)
            else:
                veri = {}
            return {
                "yol": yol, "path": yol,
                "yontem": yontem, "method": yontem,
                "sorgu": _sorgu_coz(sorgu), "query": _sorgu_coz(sorgu),
                "parametreler": parametreler, "params": parametreler,
                "govde": govde, "body": govde,
                "veri": veri, "data": veri,
                "basliklar": {k.lower(): v for k, v in self.headers.items()},
                "cerezler": _cerez_coz(self.headers.get("Cookie")),
                "ip": self.client_address[0] if self.client_address else "",
            }

        def _duragan_bul(self, yol):
            for onek, klasor in uygulama.duragan:
                if not yol.startswith(onek):
                    continue
                goreli = yol[len(onek):].lstrip("/")
                if goreli in ("", "/"):
                    goreli = "index.html"
                hedef = os.path.normpath(os.path.join(klasor, goreli))
                if not hedef.startswith(os.path.normpath(klasor)):
                    continue
                if os.path.isfile(hedef):
                    return _dosya_cevabi(hedef)
            return None

        def _bulunamadi(self, yol):
            if uygulama.bulunamadi_isi is not None:
                return _cevaba_cevir(y.cagir(uygulama.bulunamadi_isi, [yol]))
            if yol == "/favicon.ico":
                return Cevap(VARSAYILAN_SIMGE, 200, "image/svg+xml")
            govde = H.sayfa(baslik="Bulunamadi",
                            govde="<h1>404</h1><p><code>%s</code> bulunamadi.</p>"
                                  % H.kacir(yol))
            return Cevap(govde.encode("utf-8"), 404)

        def _hata(self, e):
            mesaj = e.rapor() if hasattr(e, "rapor") else "%s: %s" % (type(e).__name__, e)
            if not uygulama.sessiz:
                y.cikti("  ! %s\n" % mesaj)
            if uygulama.hata_isi is not None:
                try:
                    return _cevaba_cevir(y.cagir(uygulama.hata_isi, [mesaj]))
                except Exception:  # noqa: BLE001
                    pass
            govde = H.sayfa(baslik="Hata",
                            govde="<h1>500</h1><pre>%s</pre>" % H.kacir(mesaj))
            return Cevap(govde.encode("utf-8"), 500)

        def _gonder(self, cevap):
            govde = cevap.govde
            if isinstance(govde, str):
                govde = govde.encode("utf-8")
            self.send_response(cevap.durum)
            self.send_header("Content-Type", cevap.tur)
            self.send_header("Content-Length", str(len(govde)))
            for k, v in cevap.basliklar.items():
                self.send_header(k, v)
            self.end_headers()
            if govde:
                self.wfile.write(govde)
            return None

        def do_GET(self):
            self._islem("GET")

        def do_POST(self):
            self._islem("POST")

        def do_PUT(self):
            self._islem("PUT")

        def do_DELETE(self):
            self._islem("DELETE")

        def do_PATCH(self):
            self._islem("PATCH")

        def do_HEAD(self):
            self._islem("GET")

    return Isleyici


def _dosya_cevabi(yol):
    tur = mimetypes.guess_type(yol)[0] or "application/octet-stream"
    if tur.startswith("text/") or tur in ("application/javascript", "application/json"):
        tur += "; charset=utf-8"
    with open(yol, "rb") as f:
        return Cevap(f.read(), 200, tur)


# ---------------------------------------------------------------- TON arayuzu
@kutuphane("web", "tonweb")
def yukle(y):
    uygulama = Uygulama(y)

    def _yol(dosya):
        dosya = _metin(dosya)
        return dosya if os.path.isabs(dosya) else os.path.join(y.kok, dosya)

    def sayfa_ekle(yol, isle):
        return uygulama.yol_ekle("GET", yol, isle)

    def gonderi_ekle(yol, isle):
        return uygulama.yol_ekle("POST", yol, isle)

    def api_ekle(yol, isle, yontem="ANY"):
        return uygulama.yol_ekle(yontem, yol, isle)

    def yol_ekle(yol, isle, yontem="GET"):
        return uygulama.yol_ekle(yontem, yol, isle)

    def duragan(klasor, onek="/"):
        onek = _metin(onek)
        if not onek.startswith("/"):
            onek = "/" + onek
        uygulama.duragan.append((onek.rstrip("/") or "/", _yol(klasor)))
        return True

    def json_cevap(deger, durum=200):
        govde = _json.dumps(pythonlastir(deger), ensure_ascii=False).encode("utf-8")
        return Cevap(govde, int(durum), "application/json; charset=utf-8")

    def yonlendir(adres, durum=302):
        return Cevap(b"", int(durum), "text/plain", {"Location": _metin(adres)})

    def dosya_cevap(dosya):
        hedef = _yol(dosya)
        if not os.path.isfile(hedef):
            raise TonRuntimeError("Dosya bulunamadi: %s" % _metin(dosya))
        return _dosya_cevabi(hedef)

    def durum_cevap(kod, govde=""):
        return Cevap(_metin(govde).encode("utf-8"), int(kod))

    def metin_cevap(govde, durum=200):
        return Cevap(_metin(govde).encode("utf-8"), int(durum), "text/plain; charset=utf-8")

    def cerez_ekle(cevap, ad, deger, gun=7):
        if not isinstance(cevap, Cevap):
            cevap = _cevaba_cevir(cevap)
        cevap.basliklar["Set-Cookie"] = "%s=%s; Path=/; Max-Age=%d" % (
            _metin(ad), urllib.parse.quote(_metin(deger)), int(gun) * 86400)
        return cevap

    def bicimle(dosya, degerler=None):
        """HTML dosyasini okur, icindeki %ad% yerlerini doldurur."""
        from tonlang.lib.meta import sablon
        hedef = _yol(dosya)
        if not os.path.isfile(hedef):
            raise TonRuntimeError("Sablon bulunamadi: %s" % _metin(dosya))
        with open(hedef, encoding="utf-8") as f:
            return sablon(y, f.read(), degerler or {})

    def baslat(port=8080, adres="0.0.0.0", sessiz=False, arkaplan=False):
        if uygulama.sunucu is not None:
            raise TonRuntimeError("Sunucu zaten calisiyor")
        uygulama.sessiz = bool(sessiz)
        try:
            uygulama.sunucu = ThreadingHTTPServer((_metin(adres), int(port)),
                                                  _isleyici_kur(uygulama))
        except OSError as e:
            raise TonRuntimeError("Sunucu baslatilamadi (port %s): %s" % (_metin(port), e))
        uygulama.sunucu.daemon_threads = True
        y.cikti("TON web sunucusu hazir -> http://localhost:%s  (durdurmak icin Ctrl-C)\n"
                % _metin(port))
        if arkaplan:
            uygulama.thread = threading.Thread(target=uygulama.sunucu.serve_forever, daemon=True)
            uygulama.thread.start()
            return True
        try:
            uygulama.sunucu.serve_forever()
        except KeyboardInterrupt:
            y.cikti("\nSunucu durduruldu.\n")
        finally:
            durdur()
        return True

    def arkaplanda_baslat(port=8080, adres="127.0.0.1", sessiz=True):
        return baslat(port, adres, sessiz, True)

    def durdur():
        if uygulama.sunucu is not None:
            uygulama.sunucu.shutdown()
            uygulama.sunucu.server_close()
            uygulama.sunucu = None
        return True

    def yollari_yaz():
        return [{"yontem": k["yontem"], "yol": k["desen"]} for k in uygulama.yollar]

    # ---------------------------------------------------------- tarayici tarafi
    def _ic_yol(yontem, desen, fn, ad="ic"):
        """Python tarafindan yazilmis bir isleyiciyi yola baglar."""
        uygulama.yol_ekle(yontem, desen, Gomulu("web." + ad, fn))
        return True

    def tarayici_js(yol="/ton.js"):
        """ton.js calisma zamanini yayinlar."""
        from .paket import calisma_zamani
        icerik = calisma_zamani().encode("utf-8")

        def isle(istek):
            return Cevap(icerik, 200, "application/javascript; charset=utf-8")
        return _ic_yol("GET", yol, isle, "ton_js")

    def betik(yol, ton_dosyasi):
        """Bir .ton dosyasini derleyip JavaScript olarak yayinlar.

        Her istekte yeniden derlenir; dosyayi degistirip sayfayi yenilemen yeter."""
        from .paket import derle as tarayiciya_derle
        kaynak = _yol(ton_dosyasi)

        def isle(istek):
            try:
                kod = tarayiciya_derle(kaynak)
            except TonError as e:
                kod = ("TON.hata_goster({mesaj: %s});"
                       % _json.dumps(e.rapor()))
            return Cevap(kod.encode("utf-8"), 200, "application/javascript; charset=utf-8")
        return _ic_yol("GET", yol, isle, "betik")

    def uygulama_ekle(yol, ton_dosyasi, baslik=None, govde=None, js_yolu=None):
        """Tarayicida calisan bir TON uygulamasini yayinlar.

        web.uygulama("/", "sayac.ton")  ->  sayfa + ton.js + derlenmis kod"""
        from .paket import sayfa as paket_sayfasi
        kaynak = _yol(ton_dosyasi)
        ad = os.path.splitext(os.path.basename(kaynak))[0]
        betik_yolu = js_yolu or ("/%s.ton.js" % ad)
        if not any(k["desen"] == "/ton.js" for k in uygulama.yollar):
            tarayici_js("/ton.js")
        betik(betik_yolu, kaynak)

        def isle(istek):
            try:
                html = paket_sayfasi(kaynak, baslik=baslik, govde=govde, gomulu=False,
                                     betik_adresi=betik_yolu)
            except TonError as e:
                html = H.sayfa(baslik="Hata",
                               govde="<h1>Derleme hatasi</h1><pre>%s</pre>"
                                     % H.kacir(e.rapor()))
                return Cevap(html.encode("utf-8"), 500)
            return Cevap(html.encode("utf-8"), 200)
        return _ic_yol("GET", yol, isle, "uygulama")

    def ai_ucu(yol="/api/ai"):
        """Tarayicidaki ai() bu uca gelir; anahtar sunucuda kalir."""
        from tonlang.lib.zeka import zeka

        def isle(istek):
            veri = istek.get("veri") or {}
            soru = veri.get("soru") or veri.get("prompt") or ""
            if not soru:
                return Cevap(b'{"hata":"soru bos"}', 400,
                             "application/json; charset=utf-8")
            try:
                cevap = zeka(soru, model=veri.get("model"), kisilik=veri.get("kisilik"))
            except TonError as e:
                return json_cevap({"hata": e.mesaj}, 500)
            return json_cevap({"cevap": cevap})
        return _ic_yol("POST", yol, isle, "ai_ucu")

    def hata_isi(isle):
        uygulama.hata_isi = isle
        return True

    def bulunamadi_isi(isle):
        uygulama.bulunamadi_isi = isle
        return True

    return isim_alani("web", {
        # yollar
        "page": sayfa_ekle, "sayfa": sayfa_ekle,
        "post": gonderi_ekle, "gonderi": gonderi_ekle,
        "api": api_ekle,
        "route": yol_ekle, "yol": yol_ekle,
        "static": duragan, "duragan": duragan,
        "routes": yollari_yaz, "yollar": yollari_yaz,
        # tarayici tarafi
        "app": uygulama_ekle, "uygulama": uygulama_ekle,
        "script": betik, "betik": betik,
        "runtime": tarayici_js, "tarayici_js": tarayici_js,
        "ai_endpoint": ai_ucu, "ai_ucu": ai_ucu,
        "on_error": hata_isi, "hata_olunca": hata_isi,
        "on_missing": bulunamadi_isi, "bulunamazsa": bulunamadi_isi,
        # cevaplar
        "json": json_cevap,
        "redirect": yonlendir, "yonlendir": yonlendir,
        "file": dosya_cevap, "dosya": dosya_cevap,
        "status": durum_cevap, "durum": durum_cevap,
        "text": metin_cevap, "metin": metin_cevap,
        "cookie": cerez_ekle, "cerez": cerez_ekle,
        # html
        "html": H.sayfa, "sayfa_yap": H.sayfa,
        "tag": H.etiket, "etiket": H.etiket,
        "table": H.tablo, "tablo": H.tablo,
        "list": H.liste, "liste": H.liste,
        "link": H.baglanti, "baglanti": H.baglanti,
        "escape": H.kacir, "kacir": H.kacir,
        "render": bicimle, "bicimle": bicimle,
        # sunucu
        "serve": baslat, "calistir": baslat,
        "start": arkaplanda_baslat, "baslat": arkaplanda_baslat,
        "stop": durdur, "durdur": durdur,
        "surum": SURUM,
    })
