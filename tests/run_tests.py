#!/usr/bin/env python3
"""TON test kosucusu.

    python3 tests/run_tests.py            # tum testleri calistir
    python3 tests/run_tests.py --guncelle # beklenen ciktilari yeniden uret
    python3 tests/run_tests.py 05         # sadece adinda 05 gecenler
"""

import os
import subprocess
import sys

KOK = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
KUTU = os.path.join(KOK, "tests", "cases")
TON = os.path.join(KOK, "ton")


def durumlar(suzgec=None):
    for ad in sorted(os.listdir(KUTU)):
        if not ad.endswith(".ton") or ad.endswith("_yardimci.ton"):
            continue
        if suzgec and suzgec not in ad:
            continue
        yield ad


def calistir(ad):
    p = subprocess.run([sys.executable, TON, os.path.join(KUTU, ad)],
                       capture_output=True, text=True, timeout=120)
    return p.stdout + p.stderr


def birim_testleri():
    """Cekirdek davranislarini python tarafindan sinar."""
    sys.path.insert(0, KOK)
    from tonlang import calistir as ton_calistir
    from tonlang.errors import TonError, TonSyntaxError

    gecen, kalan = 0, []

    def bekle(kaynak, beklenen):
        cikti = []
        try:
            ton_calistir(kaynak, "<test>", cikti.append)
        except TonError as e:
            cikti.append("HATA: " + e.mesaj)
        bulunan = "".join(cikti)
        return bulunan.strip() == beklenen.strip(), bulunan.strip()

    durumlar_listesi = [
        ("print: merhaba", "merhaba"),
        ('a = 1\nprint: %a%', "1"),
        ('print(1 + 1)', "2"),
        ('print(%yok%)', "HATA: 'yok' adinda bir degisken yok"),
        ('a = 1\nprint(a)', "HATA: 'a' bir degisken; %a% seklinde yazmalisin"),
        ('print(1 / 0)', "HATA: Sifira bolunemez"),
        ('print("a" + 1)', "a1"),
        ('print(1 == 1.0)', "true"),
        ('print("1" == 1)', "false"),
        ('print(bilinmeyen_is())', "HATA: 'bilinmeyen_is' adinda bir is yok"),
        ('print: %a', "%a"),
        ('print: 50%% indirim', "50% indirim"),
    ]
    for kaynak, beklenen in durumlar_listesi:
        tamam, bulunan = bekle(kaynak, beklenen)
        if tamam:
            gecen += 1
        else:
            kalan.append((kaynak, beklenen, bulunan))

    # Windows'tan gelen dosyalar: BOM, CRLF ve ANSI kodlama
    import tempfile
    from tonlang import calistir_dosya
    from tonlang.okuma import metne_cevir

    dosya_durumlari = [
        ("bom_crlf", '\ufeff'.encode("utf-8") + 'print: selam\r\n'.encode("utf-8"), "selam"),
        ("ansi", 'print: Türkçe\r\n'.encode("cp1254"), "Türkçe"),
        ("duz", 'print: duz\n'.encode("utf-8"), "duz"),
    ]
    for ad, baytlar, beklenen in dosya_durumlari:
        with tempfile.NamedTemporaryFile("wb", suffix=".ton", delete=False) as f:
            f.write(baytlar)
            yol = f.name
        cikti = []
        try:
            calistir_dosya(yol, cikti.append)
            bulunan = "".join(cikti).strip()
        except TonError as e:
            bulunan = "HATA: " + e.mesaj
        finally:
            os.unlink(yol)
        if bulunan == beklenen:
            gecen += 1
        else:
            kalan.append((ad, beklenen, bulunan))

    if metne_cevir(b"\xef\xbb\xbfa\r\nb") == "a\nb":
        gecen += 1
    else:
        kalan.append(("metne_cevir", "a\nb", metne_cevir(b"\xef\xbb\xbfa\r\nb")))

    # yazim hatalari
    for kaynak in ['if 1\nprint: x', 'func f(\n', 'a = %', 'x = [1,']:
        try:
            ton_calistir(kaynak, "<test>", lambda s: None)
            kalan.append((kaynak, "yazim hatasi", "hata verilmedi"))
        except TonSyntaxError:
            gecen += 1
        except TonError:
            gecen += 1
    return gecen, kalan


def main():
    argv = sys.argv[1:]
    guncelle = "--guncelle" in argv
    argv = [a for a in argv if not a.startswith("--")]
    suzgec = argv[0] if argv else None

    gecen, kalan = 0, 0
    for ad in durumlar(suzgec):
        beklenen_yol = os.path.join(KUTU, ad[:-4] + ".out")
        bulunan = calistir(ad)
        if guncelle:
            with open(beklenen_yol, "w", encoding="utf-8") as f:
                f.write(bulunan)
            print("guncellendi: %s" % ad)
            continue
        if not os.path.exists(beklenen_yol):
            print("ATLANDI  %s (beklenen cikti yok)" % ad)
            continue
        with open(beklenen_yol, encoding="utf-8") as f:
            beklenen = f.read()
        if bulunan == beklenen:
            gecen += 1
            print("GECTI    %s" % ad)
        else:
            kalan += 1
            print("KALDI    %s" % ad)
            import difflib
            for satir in difflib.unified_diff(beklenen.splitlines(), bulunan.splitlines(),
                                              "beklenen", "bulunan", lineterm="", n=1):
                print("    " + satir)
    if guncelle:
        return 0

    bgecen, bkalan = birim_testleri()
    print("\nBirim testleri: %d gecti, %d kaldi" % (bgecen, len(bkalan)))
    for kaynak, beklenen, bulunan in bkalan:
        print("  KALDI %r\n    beklenen: %s\n    bulunan : %s" % (kaynak, beklenen, bulunan))

    toplam_kalan = kalan + len(bkalan)
    print("\n%d gecti, %d kaldi" % (gecen + bgecen, toplam_kalan))
    return 1 if toplam_kalan else 0


if __name__ == "__main__":
    sys.exit(main())
