"""WebSocket istemcisi (RFC 6455) - ek pakete ihtiyac duymaz.

    s = connect(wss://ornek.com/ws)
    %s%.yolla({selam: "dunya"})
    print: %(%s%.al())%
    %s%.kapat()

Surekli dinlemek icin:

    func gelince(mesaj)
      print: %mesaj%
    end
    %s%.dinle(gelince)
    %s%.bekle()
"""

import base64
import hashlib
import json as _json
import os
import socket
import ssl
import struct
import threading
import time
import urllib.parse

from ..errors import AxsRuntimeError, AxsTypeError
from ..values import Gorev, cagrilabilir_mi, metin as _metin, pythonlastir, axslastir
from . import isim_alani

SIHIRLI = "258EAFA5-E914-47DA-95CA-C5AB0DC85B11"

# cerceve turleri
SURUYOR = 0x0
METIN = 0x1
IKILI = 0x2
KAPAT = 0x8
PING = 0x9
PONG = 0xA


class SoketKapali(Exception):
    """Baglanti kapandi."""

    def __init__(self, kod=1000, sebep=""):
        super().__init__("%s %s" % (kod, sebep))
        self.kod = kod
        self.sebep = sebep


class Soket:
    """Tek bir WebSocket baglantisi."""

    def __init__(self, adres, basliklar=None, zaman_asimi=30):
        self.adres = adres
        self.acik = False
        self.kapanma_kodu = None
        self.kapanma_sebebi = ""
        self._gonderme_kilidi = threading.Lock()
        self._tampon = b""
        self._dinleyici = None
        self._dur = threading.Event()
        self._baglan(adres, basliklar or {}, zaman_asimi)

    # ------------------------------------------------------------ baglanti
    def _baglan(self, adres, basliklar, zaman_asimi):
        parca = urllib.parse.urlparse(adres)
        guvenli = parca.scheme == "wss"
        port = parca.port or (443 if guvenli else 80)
        yol = parca.path or "/"
        if parca.query:
            yol += "?" + parca.query
        try:
            ham = socket.create_connection((parca.hostname, port), timeout=zaman_asimi)
        except OSError as e:
            raise AxsRuntimeError("Baglanti kurulamadi (%s): %s" % (adres, e))
        if guvenli:
            baglam = ssl.create_default_context()
            ca = os.environ.get("REQUESTS_CA_BUNDLE") or os.environ.get("SSL_CERT_FILE")
            if ca and os.path.exists(ca):
                baglam.load_verify_locations(ca)
            try:
                ham = baglam.wrap_socket(ham, server_hostname=parca.hostname)
            except ssl.SSLError as e:
                raise AxsRuntimeError("Guvenli baglanti kurulamadi (%s): %s" % (adres, e))
        self.sok = ham
        self._el_sikis(parca, yol, port, basliklar, zaman_asimi)
        self.acik = True

    def _el_sikis(self, parca, yol, port, basliklar, zaman_asimi):
        anahtar = base64.b64encode(os.urandom(16)).decode()
        konak = parca.hostname
        if port not in (80, 443):
            konak += ":%d" % port
        satirlar = [
            "GET %s HTTP/1.1" % yol,
            "Host: %s" % konak,
            "Upgrade: websocket",
            "Connection: Upgrade",
            "Sec-WebSocket-Key: %s" % anahtar,
            "Sec-WebSocket-Version: 13",
            "User-Agent: Axs/1.0",
        ]
        for k, v in basliklar.items():
            satirlar.append("%s: %s" % (k, _metin(v)))
        self.sok.settimeout(zaman_asimi)
        self.sok.sendall(("\r\n".join(satirlar) + "\r\n\r\n").encode("utf-8"))

        cevap = b""
        while b"\r\n\r\n" not in cevap:
            parca_veri = self.sok.recv(4096)
            if not parca_veri:
                raise AxsRuntimeError("El sikismasi yarida kesildi: %s" % self.adres)
            cevap += parca_veri
            if len(cevap) > 65536:
                raise AxsRuntimeError("El sikismasi cevabi cok buyuk")
        basluk, _, kalan = cevap.partition(b"\r\n\r\n")
        self._tampon = kalan
        metin_basluk = basluk.decode("latin-1")
        ilk_satir = metin_basluk.split("\r\n", 1)[0]
        if "101" not in ilk_satir:
            raise AxsRuntimeError(
                "WebSocket el sikismasi reddedildi (%s): %s" % (self.adres, ilk_satir))
        beklenen = base64.b64encode(
            hashlib.sha1((anahtar + SIHIRLI).encode()).digest()).decode()
        for satir in metin_basluk.split("\r\n")[1:]:
            if satir.lower().startswith("sec-websocket-accept:"):
                if satir.split(":", 1)[1].strip() != beklenen:
                    raise AxsRuntimeError("Sunucunun el sikisma yaniti gecersiz")
                break

    # ------------------------------------------------------------ cerceveler
    def _oku(self, adet, zaman_asimi=None):
        self.sok.settimeout(zaman_asimi)
        while len(self._tampon) < adet:
            try:
                parca = self.sok.recv(max(4096, adet - len(self._tampon)))
            except socket.timeout:
                raise
            except OSError as e:
                raise SoketKapali(1006, str(e))
            if not parca:
                raise SoketKapali(1006, "baglanti dustu")
            self._tampon += parca
        cikti, self._tampon = self._tampon[:adet], self._tampon[adet:]
        return cikti

    def _cerceve_gonder(self, tur, veri=b""):
        if not self.acik:
            raise AxsRuntimeError("Baglanti kapali")
        ilk = bytes([0x80 | tur])
        uzunluk = len(veri)
        maske = os.urandom(4)
        if uzunluk < 126:
            basluk = ilk + bytes([0x80 | uzunluk])
        elif uzunluk < 65536:
            basluk = ilk + bytes([0x80 | 126]) + struct.pack(">H", uzunluk)
        else:
            basluk = ilk + bytes([0x80 | 127]) + struct.pack(">Q", uzunluk)
        maskeli = bytes(b ^ maske[i % 4] for i, b in enumerate(veri))
        with self._gonderme_kilidi:
            try:
                self.sok.sendall(basluk + maske + maskeli)
            except OSError as e:
                self.acik = False
                raise AxsRuntimeError("Gonderilemedi: %s" % e)

    def _cerceve_al(self, zaman_asimi=None):
        """Tam bir mesaj okur (parcali cerceveleri birlestirir)."""
        parcalar = []
        mesaj_turu = None
        while True:
            basluk = self._oku(2, zaman_asimi)
            son = bool(basluk[0] & 0x80)
            tur = basluk[0] & 0x0F
            maskeli = bool(basluk[1] & 0x80)
            uzunluk = basluk[1] & 0x7F
            if uzunluk == 126:
                uzunluk = struct.unpack(">H", self._oku(2, zaman_asimi))[0]
            elif uzunluk == 127:
                uzunluk = struct.unpack(">Q", self._oku(8, zaman_asimi))[0]
            maske = self._oku(4, zaman_asimi) if maskeli else None
            veri = self._oku(uzunluk, zaman_asimi) if uzunluk else b""
            if maske:
                veri = bytes(b ^ maske[i % 4] for i, b in enumerate(veri))

            if tur == PING:
                self._cerceve_gonder(PONG, veri)
                continue
            if tur == PONG:
                continue
            if tur == KAPAT:
                kod = struct.unpack(">H", veri[:2])[0] if len(veri) >= 2 else 1005
                sebep = veri[2:].decode("utf-8", "replace")
                self.kapanma_kodu = kod
                self.kapanma_sebebi = sebep
                try:
                    self._cerceve_gonder(KAPAT, veri[:2])
                except AxsRuntimeError:
                    pass
                self.acik = False
                raise SoketKapali(kod, sebep)

            if tur in (METIN, IKILI):
                mesaj_turu = tur
            parcalar.append(veri)
            if son:
                break
        govde = b"".join(parcalar)
        if mesaj_turu == IKILI:
            return govde
        return govde.decode("utf-8", "replace")

    # ------------------------------------------------------------ Axs arayuzu
    def yolla(self, mesaj):
        if isinstance(mesaj, (dict, list)):
            ham = _json.dumps(pythonlastir(mesaj), ensure_ascii=False,
                              separators=(",", ":"))
        elif isinstance(mesaj, bytes):
            self._cerceve_gonder(IKILI, mesaj)
            return True
        else:
            ham = _metin(mesaj)
        self._cerceve_gonder(METIN, ham.encode("utf-8"))
        return True

    def al(self, zaman_asimi=None):
        try:
            veri = self._cerceve_al(zaman_asimi)
        except socket.timeout:
            return None
        except SoketKapali as e:
            self.acik = False
            raise AxsRuntimeError("Baglanti kapandi (%s) %s" % (e.kod, e.sebep))
        return _coz(veri)

    def kapat(self, kod=1000, sebep=""):
        self._dur.set()
        if self.acik:
            try:
                self._cerceve_gonder(KAPAT,
                                     struct.pack(">H", int(kod)) + sebep.encode("utf-8"))
            except (AxsRuntimeError, OSError):
                pass
        self.acik = False
        try:
            self.sok.close()
        except OSError:
            pass
        return True


def _coz(veri):
    """Metin JSON ise haritaya cevrilir."""
    if isinstance(veri, bytes):
        return veri
    kirp = veri.strip()
    if kirp[:1] in ("{", "["):
        try:
            return axslastir(_json.loads(kirp))
        except ValueError:
            return veri
    return veri


def soket_alani(y, soket):
    """Soketi Axs'ten kullanilabilir hale getirir."""

    def dinle(is_, hata_isi=None):
        """Gelen her mesaj icin verilen isi calistirir (arka planda)."""
        if not cagrilabilir_mi(is_):
            raise AxsTypeError("dinle() bir is ister")
        gorev = Gorev("soket:" + soket.adres)

        def dongu():
            try:
                while soket.acik and not soket._dur.is_set():
                    try:
                        veri = soket._cerceve_al(1.0)
                    except socket.timeout:
                        continue
                    except SoketKapali as e:
                        soket.acik = False
                        if getattr(soket, "_durum_yaz", None):
                            soket._durum_yaz()
                        if hata_isi is not None:
                            y.cagir(hata_isi, [e.kod, e.sebep])
                        break
                    y.cagir(is_, [_coz(veri)])
            except BaseException as e:      # noqa: BLE001 - gorevde saklanir
                gorev.hata = e
            finally:
                gorev.bitti = True

        gorev.thread = threading.Thread(target=dongu, daemon=True)
        gorev.thread.start()
        soket._dinleyici = gorev
        y.gorevler.append(gorev)
        return gorev

    def bekle(sure=None):
        """Dinleme bitene kadar (ya da baglanti kapanana kadar) bekler."""
        gorev = soket._dinleyici
        if gorev is None:
            while soket.acik and not soket._dur.is_set():
                time.sleep(0.2)
            return True
        gorev.thread.join(sure)
        if gorev.hata is not None:
            raise gorev.hata
        return True

    def durdur():
        soket._dur.set()
        return True

    def yolla(mesaj):
        try:
            return soket.yolla(mesaj)
        finally:
            durum_yaz()

    def al(zaman_asimi=None):
        try:
            return soket.al(zaman_asimi)
        finally:
            durum_yaz()

    def kapat(kod=1000, sebep=""):
        try:
            return soket.kapat(kod, sebep)
        finally:
            durum_yaz()

    alan = isim_alani("baglanti", {
        "adres": soket.adres,
        "tur": "soket",
        "send": yolla, "yolla": yolla,
        "receive": al, "al": al,
        "listen": dinle, "dinle": dinle,
        "wait": bekle, "bekle": bekle,
        "stop": durdur, "durdur": durdur,
        "close": kapat, "kapat": kapat,
        "acik": True, "open": True,
        "kapanma_kodu": None,
    })

    def durum_yaz():
        alan.uyeler["acik"] = soket.acik
        alan.uyeler["open"] = soket.acik
        alan.uyeler["kapanma_kodu"] = soket.kapanma_kodu

    soket._durum_yaz = durum_yaz
    return alan


def soket_ac(y, adres, basliklar=None, zaman_asimi=30):
    soket = Soket(_metin(adres), basliklar, float(zaman_asimi))
    return soket_alani(y, soket)
