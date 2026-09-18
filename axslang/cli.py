"""`axs` komut satiri araci."""

import os
import sys

from .errors import AxsError
from .interpreter import Yorumlayici
from .surum import SURUM, SURUM_ADI, UZANTILAR

YARDIM = """Axs - cok basit bir programlama dili

Kullanim:
  axs <dosya.axs> [degerler...]   Bir Axs dosyasini calistirir
  axs                             Etkilesimli kabuk (REPL)
  axs -e "print: merhaba"         Tek satir kod calistirir
  axs kontrol <dosya>             Sadece yazim denetimi yapar
  axs install <paket>             Kutuphane indirir (ornek: axs install jubbio)
  axs paketler                    Kurulu kutuphaneleri listeler
  axs kaldir <paket>              Kutuphaneyi siler
  axs derle <dosya> [-o a.js]     Tarayici icin JavaScript'e cevirir
  axs paket <dosya> [-o a.html]   Tek dosyalik calisir HTML uretir
  axs cevir <dosya.js> [-o a.axs] JavaScript kodunu Axs'e cevirir
  axs yeni <ad>                   Yeni bir Axs projesi olusturur
  axs isler                       Hazir islerin listesini yazar
  axs -s | --surum                Surumu yazar
  axs -y | --yardim               Bu yaziyi yazar

Dosya uzantilari: %s
""" % ", ".join(UZANTILAR)

ORNEK = """# %s - Axs ile yazildi

ad = "dunya"

print: Merhaba %%ad%%!

func selamla(kisi)
  return "Selam " + %%kisi%%
end

mesaj = selamla("Axs")

print: %%mesaj%%
"""


def _boru_kapandi():
    """Cikti borusu kapandiginda sessizce cik (head, less ... ile kullanimda)."""
    try:
        devnull = os.open(os.devnull, os.O_WRONLY)
        os.dup2(devnull, sys.stdout.fileno())
    except (OSError, ValueError):
        pass


def _hata_yaz(e):
    sys.stderr.write(e.rapor() + "\n" if isinstance(e, AxsError) else str(e) + "\n")


def dosya_coz(ad):
    """Uzantisi yazilmamis dosyalari da bulur: `axs main` -> main.axs"""
    if os.path.isfile(ad):
        return ad
    for u in UZANTILAR:
        if os.path.isfile(ad + u):
            return ad + u
    return None


def calistir_dosya(yol, argv):
    y = Yorumlayici(yol, argv=argv)
    try:
        y.calistir_dosya(yol)
        return 0
    except AxsError as e:
        _hata_yaz(e)
        return 1
    except SystemExit as e:
        return int(e.code or 0)
    except RecursionError:
        sys.stderr.write("Calisma hatasi: is kendini cok fazla cagirdi (sonsuz dongu?)\n")
        return 1
    except BrokenPipeError:
        # `axs dosya.axs | head` gibi: karsi taraf okumayi birakti
        _boru_kapandi()
        return 0
    except KeyboardInterrupt:
        sys.stderr.write("\nDurduruldu.\n")
        return 130


def kontrol(yol):
    from .okuma import dosya_oku
    from .parser import cozumle
    try:
        cozumle(dosya_oku(yol), yol)
    except AxsError as e:
        _hata_yaz(e)
        return 1
    except OSError as e:
        sys.stderr.write("Dosya okunamadi: %s\n" % e)
        return 1
    print("Tamam: %s" % yol)
    return 0


def yeni_proje(ad):
    klasor = os.path.abspath(ad)
    os.makedirs(klasor, exist_ok=True)
    ana = os.path.join(klasor, "main.axs")
    if os.path.exists(ana):
        sys.stderr.write("Zaten var: %s\n" % ana)
        return 1
    with open(ana, "w", encoding="utf-8") as f:
        f.write(ORNEK % os.path.basename(klasor))
    print("Olusturuldu: %s\nCalistirmak icin: axs %s" % (ana, os.path.join(ad, "main.axs")))
    return 0


def derle_komutu(argv, paket):
    """axs derle / axs paket"""
    if not argv:
        sys.stderr.write("Kaynak dosya gerekli\n")
        return 1
    cikti_yolu = None
    dosyalar = []
    i = 0
    while i < len(argv):
        if argv[i] in ("-o", "--cikti", "--out"):
            if i + 1 >= len(argv):
                sys.stderr.write("-o icin dosya adi gerekli\n")
                return 1
            cikti_yolu = argv[i + 1]
            i += 2
            continue
        dosyalar.append(argv[i])
        i += 1
    if len(dosyalar) != 1:
        sys.stderr.write("Tek bir kaynak dosya ver\n")
        return 1
    yol = dosya_coz(dosyalar[0])
    if yol is None:
        sys.stderr.write("Dosya bulunamadi: %s\n" % dosyalar[0])
        return 1
    try:
        sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
        from axsweb.paket import derle as tarayiciya_derle, sayfa
        icerik = sayfa(yol) if paket else tarayiciya_derle(yol)
    except AxsError as e:
        _hata_yaz(e)
        return 1
    except ImportError:
        sys.stderr.write("axsweb bulunamadi; tarayici derleyicisi icin gerekli.\n")
        return 1
    if cikti_yolu is None:
        temel = os.path.splitext(yol)[0]
        cikti_yolu = temel + (".html" if paket else ".axs.js")
    with open(cikti_yolu, "w", encoding="utf-8") as f:
        f.write(icerik)
    print("Olusturuldu: %s" % cikti_yolu)
    if paket:
        print("Tarayicida acmak icin dosyaya cift tikla.")
    return 0


# ---------------------------------------------------------------- paketler
VARSAYILAN_DEPO = "Nylithra/ton-language"
DALLAR = ("claude/ton-language-core-qyppl7", "main", "master")


def paket_klasoru(yerel=False):
    """Kutuphanelerin kurulacagi klasor."""
    if yerel:
        return os.path.join(os.getcwd(), "kutuphaneler")
    return os.path.join(os.path.expanduser("~"), ".axs", "kutuphaneler")


def _indir(adres, zaman_asimi=30):
    import urllib.error
    import urllib.request
    istek = urllib.request.Request(adres, headers={"User-Agent": "Axs/1.0"})
    try:
        with urllib.request.urlopen(istek, timeout=zaman_asimi) as c:
            return c.read()
    except urllib.error.HTTPError as e:
        if e.code == 404:
            return None
        raise
    except urllib.error.URLError as e:
        raise OSError(str(e.reason))


def _ham_adres(depo, dal, yol):
    return "https://raw.githubusercontent.com/%s/%s/%s" % (depo, dal, yol)


def _depodan_al(yol):
    """Dosyayi depodan indirir; dallari sirayla dener."""
    depo = os.environ.get("AXS_DEPO", VARSAYILAN_DEPO)
    dallar = [os.environ.get("AXS_DAL")] if os.environ.get("AXS_DAL") else list(DALLAR)
    son_hata = None
    for dal in dallar:
        adres = _ham_adres(depo, dal, yol)
        try:
            veri = _indir(adres)
        except OSError as e:
            son_hata = e
            continue
        if veri is not None:
            return veri, adres
    if son_hata is not None:
        raise OSError(son_hata)
    return None, None


def _paket_listesi():
    veri, _ = _depodan_al("kutuphaneler/liste.json")
    if veri is None:
        return {}
    import json as _json
    try:
        return _json.loads(veri.decode("utf-8")).get("paketler", {})
    except ValueError:
        return {}


def kur_komutu(argv):
    """axs install <paket>"""
    yerel = "--yerel" in argv or "--buraya" in argv
    adlar = [a for a in argv if not a.startswith("--")]

    if not adlar:
        print("Kullanim: axs install <paket>\n")
        try:
            paketler = _paket_listesi()
        except OSError as e:
            sys.stderr.write("Paket listesi alinamadi: %s\n" % e)
            return 1
        if not paketler:
            sys.stderr.write("Paket listesi alinamadi.\n")
            return 1
        print("Kurulabilecek paketler:")
        for ad, bilgi in sorted(paketler.items()):
            print("  %-12s %s" % (ad, bilgi.get("aciklama", "")))
        return 0

    hedef_klasor = paket_klasoru(yerel)
    os.makedirs(hedef_klasor, exist_ok=True)
    sonuc = 0
    for ham_ad in adlar:
        if not _tek_paket_kur(ham_ad, hedef_klasor):
            sonuc = 1
    return sonuc


def _tek_paket_kur(ham_ad, hedef_klasor):
    from .surum import UZANTILAR

    # `axs install https://.../foo.axs`
    if ham_ad.startswith(("http://", "https://")):
        ad = os.path.splitext(os.path.basename(ham_ad))[0]
        try:
            veri = _indir(ham_ad)
        except OSError as e:
            sys.stderr.write("Indirilemedi: %s\n" % e)
            return False
        if veri is None:
            sys.stderr.write("Bulunamadi: %s\n" % ham_ad)
            return False
        return _yaz(hedef_klasor, ad, veri, ham_ad)

    ad = os.path.splitext(ham_ad)[0] if ham_ad.endswith(UZANTILAR) else ham_ad
    try:
        veri, adres = _depodan_al("kutuphaneler/%s.axs" % ad)
    except OSError as e:
        sys.stderr.write("Baglanti kurulamadi: %s\n" % e)
        return False
    if veri is None:
        sys.stderr.write("'%s' diye bir paket yok. Listeyi gormek icin: axs install\n"
                         % ad)
        return False
    return _yaz(hedef_klasor, ad, veri, adres)


def _yaz(klasor, ad, veri, kaynak):
    yol = os.path.join(klasor, ad + ".axs")
    with open(yol, "wb") as f:
        f.write(veri)
    satir = veri.decode("utf-8", "replace").count("\n") + 1
    print("Kuruldu: %s  (%d satir)" % (ad, satir))
    print("  kaynak : %s" % kaynak)
    print("  konum  : %s" % yol)
    print("  kullanim: use %s" % ad)
    return True


def paketleri_yaz():
    from .surum import UZANTILAR
    bulundu = False
    for klasor in (paket_klasoru(), paket_klasoru(True),
                   os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
                                "kutuphaneler")):
        if not os.path.isdir(klasor):
            continue
        adlar = sorted(a for a in os.listdir(klasor) if a.endswith(UZANTILAR))
        if not adlar:
            continue
        bulundu = True
        print("%s:" % klasor)
        for a in adlar:
            print("  %s" % os.path.splitext(a)[0])
    if not bulundu:
        print("Kurulu paket yok. Kurmak icin: axs install jubbio")
    return 0


def paket_kaldir(ad):
    from .surum import UZANTILAR
    ad = os.path.splitext(ad)[0] if ad.endswith(UZANTILAR) else ad
    silindi = False
    for klasor in (paket_klasoru(), paket_klasoru(True)):
        yol = os.path.join(klasor, ad + ".axs")
        if os.path.isfile(yol):
            os.remove(yol)
            print("Silindi: %s" % yol)
            silindi = True
    if not silindi:
        sys.stderr.write("'%s' kurulu degil.\n" % ad)
        return 1
    return 0


def jston_komutu(argv):
    """ton jston <dosya.js> [-o cikti.axs]"""
    cikti_yolu = None
    dosyalar = []
    i = 0
    while i < len(argv):
        if argv[i] in ("-o", "--cikti", "--out"):
            if i + 1 >= len(argv):
                sys.stderr.write("-o icin dosya adi gerekli\n")
                return 1
            cikti_yolu = argv[i + 1]
            i += 2
            continue
        dosyalar.append(argv[i])
        i += 1
    if len(dosyalar) != 1:
        sys.stderr.write("Tek bir .js dosyasi ver\n")
        return 1
    kaynak_yolu = dosyalar[0]
    if not os.path.isfile(kaynak_yolu):
        sys.stderr.write("Dosya bulunamadi: %s\n" % kaynak_yolu)
        return 1
    from .jston import dosya_cevir
    try:
        kod, uyarilar = dosya_cevir(kaynak_yolu)
    except AxsError as e:
        _hata_yaz(e)
        return 1
    if cikti_yolu == "-":
        sys.stdout.write(kod)
        return 0
    if cikti_yolu is None:
        cikti_yolu = os.path.splitext(kaynak_yolu)[0] + ".axs"
    with open(cikti_yolu, "w", encoding="utf-8") as f:
        f.write(kod)
    print("Olusturuldu: %s" % cikti_yolu)
    if uyarilar:
        print("\n%d yer elle gozden gecirilmeli (dosyanin basinda da yazili):"
              % len(uyarilar))
        for u in uyarilar:
            print("  - %s" % u)
    else:
        print("Ceviri tam: elle duzeltilecek yer yok.")
    print("\nCalistirmak icin: axs %s" % cikti_yolu)
    return 0


def isleri_yaz():
    y = Yorumlayici()
    adlar = sorted(y.gomulu.keys())
    satir = []
    for ad in adlar:
        satir.append(ad)
        if len(satir) == 6:
            print("  ".join(s.ljust(16) for s in satir))
            satir = []
    if satir:
        print("  ".join(s.ljust(16) for s in satir))
    print("\nToplam %d hazir is." % len(adlar))
    return 0


ACICILAR = ("if", "eger", "eğer", "while", "surece", "sürece", "for", "her",
            "repeat", "tekrar", "func", "is", "iş", "fonksiyon", "try", "dene")


def kabuk():
    y = Yorumlayici()
    print("%s %s - cikmak icin `cik()` ya da Ctrl-D" % (SURUM_ADI, SURUM))
    tampon = []
    while True:
        try:
            istem = "... " if tampon else "axs> "
            satir = input(istem)
        except (EOFError, KeyboardInterrupt):
            print()
            return 0
        ilk = satir.strip().split("(")[0].split(" ")[0]
        if tampon or ilk in ACICILAR:
            tampon.append(satir)
            duz = " ".join(s.strip() for s in tampon)
            acik = sum(1 for p in tampon for w in [p.strip().split(" ")[0]] if w in ACICILAR)
            kapali = sum(1 for p in tampon if p.strip() in ("end", "son", "bitir"))
            if acik > kapali:
                continue
            kaynak = "\n".join(tampon)
            tampon = []
        else:
            kaynak = satir
        if not kaynak.strip():
            continue
        try:
            from .parser import cozumle
            program = cozumle(kaynak, "<kabuk>")
            sonuc = y.blok(program, y.evren)
            # sadece ifadelerin sonucunu goster (atama ve tanimlari degil)
            if sonuc is not None and program and program[-1].tur == "IfadeDeyimi":
                from .values import metin
                print(metin(sonuc))
        except SystemExit:
            return 0
        except AxsError as e:
            _hata_yaz(e)
        except KeyboardInterrupt:
            print()


def main(argv=None):
    argv = list(sys.argv[1:] if argv is None else argv)
    if not argv:
        return kabuk()

    ilk = argv[0]
    if ilk in ("-y", "--yardim", "-h", "--help"):
        print(YARDIM)
        return 0
    if ilk in ("-s", "--surum", "-v", "--version"):
        paket_koku = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        print("%s %s" % (SURUM_ADI, SURUM))
        print("  calisan kopya : %s" % paket_koku)
        kutuphane = os.path.join(paket_koku, "kutuphaneler")
        if os.path.isdir(kutuphane):
            adlar = sorted(os.path.splitext(a)[0] for a in os.listdir(kutuphane)
                    if a.endswith(UZANTILAR))
            print("  kutuphaneler  : %s" % (", ".join(adlar) or "-"))
        print("  python        : %d.%d.%d" % sys.version_info[:3])
        return 0
    if ilk in ("-e", "--calistir", "--eval"):
        if len(argv) < 2:
            sys.stderr.write("-e icin kod gerekli\n")
            return 1
        y = Yorumlayici(argv=argv[2:])
        try:
            y.calistir_kaynak(argv[1], "<komut>")
            return 0
        except BrokenPipeError:
            _boru_kapandi()
            return 0
        except AxsError as e:
            _hata_yaz(e)
            return 1
        except SystemExit as e:
            return int(e.code or 0)
    if ilk in ("kontrol", "check"):
        if len(argv) < 2:
            sys.stderr.write("kontrol icin dosya gerekli\n")
            return 1
        yol = dosya_coz(argv[1])
        if yol is None:
            sys.stderr.write("Dosya bulunamadi: %s\n" % argv[1])
            return 1
        return kontrol(yol)
    if ilk in ("derle", "build"):
        return derle_komutu(argv[1:], paket=False)
    if ilk in ("paket", "bundle"):
        return derle_komutu(argv[1:], paket=True)
    if ilk in ("install", "kur", "indir"):
        return kur_komutu(argv[1:])
    if ilk in ("paketler", "packages"):
        return paketleri_yaz()
    if ilk in ("kaldir", "uninstall", "sil"):
        if len(argv) < 2:
            sys.stderr.write("Silinecek paket adi gerekli\n")
            return 1
        return paket_kaldir(argv[1])
    if ilk in ("cevir", "jston", "js2axs"):
        return jston_komutu(argv[1:])
    if ilk in ("yeni", "new"):
        if len(argv) < 2:
            sys.stderr.write("yeni icin proje adi gerekli\n")
            return 1
        return yeni_proje(argv[1])
    if ilk in ("isler", "builtins"):
        return isleri_yaz()
    if ilk.startswith("-"):
        sys.stderr.write("Bilinmeyen secenek: %s\n%s" % (ilk, YARDIM))
        return 1

    yol = dosya_coz(ilk)
    if yol is None:
        sys.stderr.write("Dosya bulunamadi: %s\n" % ilk)
        return 1
    return calistir_dosya(yol, argv[1:])


if __name__ == "__main__":
    sys.exit(main())
