"""`ton` komut satiri araci."""

import os
import sys

from .errors import TonError
from .interpreter import Yorumlayici
from .surum import SURUM, SURUM_ADI, UZANTILAR

YARDIM = """TON - cok basit bir programlama dili

Kullanim:
  ton <dosya.ton> [degerler...]   Bir TON dosyasini calistirir
  ton                             Etkilesimli kabuk (REPL)
  ton -e "print: merhaba"         Tek satir kod calistirir
  ton kontrol <dosya>             Sadece yazim denetimi yapar
  ton derle <dosya> [-o a.js]     Tarayici icin JavaScript'e cevirir
  ton paket <dosya> [-o a.html]   Tek dosyalik calisir HTML uretir
  ton yeni <ad>                   Yeni bir TON projesi olusturur
  ton isler                       Hazir islerin listesini yazar
  ton -s | --surum                Surumu yazar
  ton -y | --yardim               Bu yaziyi yazar

Dosya uzantilari: %s
""" % ", ".join(UZANTILAR)

ORNEK = """# %s - TON ile yazildi

ad = "dunya"

print: Merhaba %%ad%%!

func selamla(kisi)
  return "Selam " + %%kisi%%
end

mesaj = selamla("TON")

print: %%mesaj%%
"""


def _hata_yaz(e):
    sys.stderr.write(e.rapor() + "\n" if isinstance(e, TonError) else str(e) + "\n")


def dosya_coz(ad):
    """Uzantisi yazilmamis dosyalari da bulur: `ton main` -> main.ton"""
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
    except TonError as e:
        _hata_yaz(e)
        return 1
    except SystemExit as e:
        return int(e.code or 0)
    except RecursionError:
        sys.stderr.write("Calisma hatasi: is kendini cok fazla cagirdi (sonsuz dongu?)\n")
        return 1
    except KeyboardInterrupt:
        sys.stderr.write("\nDurduruldu.\n")
        return 130


def kontrol(yol):
    from .okuma import dosya_oku
    from .parser import cozumle
    try:
        cozumle(dosya_oku(yol), yol)
    except TonError as e:
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
    ana = os.path.join(klasor, "main.ton")
    if os.path.exists(ana):
        sys.stderr.write("Zaten var: %s\n" % ana)
        return 1
    with open(ana, "w", encoding="utf-8") as f:
        f.write(ORNEK % os.path.basename(klasor))
    print("Olusturuldu: %s\nCalistirmak icin: ton %s" % (ana, os.path.join(ad, "main.ton")))
    return 0


def derle_komutu(argv, paket):
    """ton derle / ton paket"""
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
        from tonweb.paket import derle as tarayiciya_derle, sayfa
        icerik = sayfa(yol) if paket else tarayiciya_derle(yol)
    except TonError as e:
        _hata_yaz(e)
        return 1
    except ImportError:
        sys.stderr.write("tonweb bulunamadi; tarayici derleyicisi icin gerekli.\n")
        return 1
    if cikti_yolu is None:
        temel = os.path.splitext(yol)[0]
        cikti_yolu = temel + (".html" if paket else ".ton.js")
    with open(cikti_yolu, "w", encoding="utf-8") as f:
        f.write(icerik)
    print("Olusturuldu: %s" % cikti_yolu)
    if paket:
        print("Tarayicida acmak icin dosyaya cift tikla.")
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
            istem = "... " if tampon else "ton> "
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
        except TonError as e:
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
        print("%s %s" % (SURUM_ADI, SURUM))
        return 0
    if ilk in ("-e", "--calistir", "--eval"):
        if len(argv) < 2:
            sys.stderr.write("-e icin kod gerekli\n")
            return 1
        y = Yorumlayici(argv=argv[2:])
        try:
            y.calistir_kaynak(argv[1], "<komut>")
            return 0
        except TonError as e:
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
