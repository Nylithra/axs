#!/usr/bin/env python3
"""Axs test kosucusu.

    python3 tests/run_tests.py            # tum testleri calistir
    python3 tests/run_tests.py --guncelle # beklenen ciktilari yeniden uret
    python3 tests/run_tests.py 05         # sadece adinda 05 gecenler
"""

import json
import os
import subprocess
import sys
import time

KOK = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
KUTU = os.path.join(KOK, "tests", "cases")
AXS = os.path.join(KOK, "axs")


def durumlar(suzgec=None):
    for ad in sorted(os.listdir(KUTU)):
        if not ad.endswith(".axs") or ad.endswith("_yardimci.axs"):
            continue
        if suzgec and suzgec not in ad:
            continue
        yield ad


def calistir(ad):
    p = subprocess.run([sys.executable, AXS, os.path.join(KUTU, ad)],
                       capture_output=True, text=True, timeout=120)
    return p.stdout + p.stderr


def birim_testleri():
    """Cekirdek davranislarini python tarafindan sinar."""
    sys.path.insert(0, KOK)
    from axslang import calistir as ton_calistir
    from axslang.errors import TonError, TonSyntaxError

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
        ('ai = "groq"\nprint: ai;', "groq"),
        ('a = 1\nprint(a)', "1"),
        ('a = 1\nprint: a;', "1"),
        ('kisi = {ad: "Nyl"}\nprint: merhaba kisi.ad;', "merhaba Nyl"),
        ('print: duz metin', "duz metin"),
        ('a = 2\nprint: hesap (a + 3);', "hesap 5"),
        ('print(1 / 0)', "HATA: Sifira bolunemez"),
        ('print("a" + 1)', "a1"),
        ('print(1 == 1.0)', "true"),
        ('print("1" == 1)', "false"),
        ('print(bilinmeyen_is())', "HATA: 'bilinmeyen_is' diye bir sey yok"),
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
    from axslang import calistir_dosya
    from axslang.okuma import metne_cevir

    dosya_durumlari = [
        ("bom_crlf", '\ufeff'.encode("utf-8") + 'print: selam\r\n'.encode("utf-8"), "selam"),
        ("ansi", 'print: Türkçe\r\n'.encode("cp1254"), "Türkçe"),
        ("duz", 'print: duz\n'.encode("utf-8"), "duz"),
    ]
    for ad, baytlar, beklenen in dosya_durumlari:
        with tempfile.NamedTemporaryFile("wb", suffix=".axs", delete=False) as f:
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


TARAYICI_DURUMLARI = [
    "01_degiskenler", "02_islemler", "03_kosul_dongu", "04_isler",
    "05_metin", "06_koleksiyon", "11_esyamanli", "12_kullan",
]


def tarayici_testleri():
    """Ayni test dosyalarini JavaScript'e derleyip node ile calistirir.

    Cekirdek ve tarayici ayni ciktiyi vermek zorundadir."""
    import shutil
    import tempfile

    node = shutil.which("node")
    if not node:
        return 0, [], True

    sys.path.insert(0, KOK)
    from axslang.derleyici import dosya_derle
    from axslang.errors import TonError

    gecen, kalan = 0, []
    calisma_zamani = os.path.join(KOK, "axsweb", "tarayici", "axs.js")

    # 1) isler.json, axs.js ile ayni mi?
    p = subprocess.run(
        [node, "-e", "require(%s); console.log(JSON.stringify(Object.keys(AXS._HAZIR).sort()))"
         % json.dumps(calisma_zamani)],
        capture_output=True, text=True, timeout=60)
    try:
        canli = json.loads(p.stdout)
    except ValueError:
        canli = None
    with open(os.path.join(KOK, "axsweb", "tarayici", "isler.json"), encoding="utf-8") as f:
        kayitli = json.load(f)
    if canli is not None and canli == kayitli:
        gecen += 1
    else:
        kalan.append(("isler.json", "axs.js ile ayni", "farkli - yeniden uret"))

    # 2) tarayiciya ozgu davranislar
    from axslang.derleyici import derle as tarayiciya_derle

    kucuk_testler = [
        # `ai = "groq"` hem degisken hem ayar
        ('ai = "groq"\nprint: %ai% %(ai_ayar().saglayici)%', "groq groq"),
        ('ai = "openai"\nprint: %(ai_ayar().saglayici)%', "chatgpt"),
        # hazir isi golgeleyen degisken: cagri yine hazir ise gider
        ('len = 5\nprint: %len% %(len("abc"))%', "5 3"),
        # cagrilabilir deger golgeleyebilir
        ('func len(x) -> 99\nprint: %(len("abc"))%', "99"),
    ]
    for kaynak, beklenen in kucuk_testler:
        try:
            kod = tarayiciya_derle(kaynak, "<tarayici-test>")
        except TonError as e:
            kalan.append((kaynak, beklenen, e.rapor()))
            continue
        p2 = subprocess.run(
            [node, "-e", "require(%s); %s" % (json.dumps(calisma_zamani), kod)],
            capture_output=True, text=True, timeout=60)
        bulunan = (p2.stdout + p2.stderr).strip()
        if bulunan == beklenen:
            gecen += 1
        else:
            kalan.append((kaynak, beklenen, bulunan))

    # 3) test dosyalari ayni ciktiyi veriyor mu?
    gecici = tempfile.mkdtemp(prefix="ton-js-")
    try:
        for ad in TARAYICI_DURUMLARI:
            kaynak = os.path.join(KUTU, ad + ".axs")
            try:
                kod = dosya_derle(kaynak)
            except TonError as e:
                kalan.append((ad, "derlenmeli", e.rapor()))
                continue
            js_yolu = os.path.join(gecici, ad + ".js")
            with open(js_yolu, "w", encoding="utf-8") as f:
                f.write(kod)
            p = subprocess.run(
                [node, "-e", "require(%s); require(%s);"
                 % (json.dumps(calisma_zamani), json.dumps(js_yolu))],
                capture_output=True, text=True, timeout=120)
            bulunan = p.stdout + p.stderr
            with open(os.path.join(KUTU, ad + ".out"), encoding="utf-8") as f:
                beklenen = f.read()
            if bulunan == beklenen:
                gecen += 1
            else:
                kalan.append((ad, beklenen.strip()[:120], bulunan.strip()[:120]))
    finally:
        shutil.rmtree(gecici, ignore_errors=True)
    return gecen, kalan, False


JSTON_KUTUSU = os.path.join(KOK, "tests", "jston")


def jston_testleri():
    """JavaScript programlarini Axs'e cevirir ve ayni ciktiyi verdiklerini dogrular.

    Olcut: `node x.js` ile `axs x.axs` bayt bayt ayni yazmali."""
    import shutil
    import tempfile

    node = shutil.which("node")
    if not node or not os.path.isdir(JSTON_KUTUSU):
        return 0, [], True

    sys.path.insert(0, KOK)
    from axslang.errors import TonError
    from axslang.jston import dosya_cevir

    gecen, kalan = 0, []
    gecici = tempfile.mkdtemp(prefix="ton-jston-")
    try:
        for ad in sorted(os.listdir(JSTON_KUTUSU)):
            if not ad.endswith(".js"):
                continue
            js_yolu = os.path.join(JSTON_KUTUSU, ad)
            p_js = subprocess.run([node, js_yolu], capture_output=True, text=True,
                                  timeout=120)
            js_cikti = p_js.stdout + p_js.stderr
            try:
                kod, _uyarilar = dosya_cevir(js_yolu)
            except TonError as e:
                kalan.append((ad, "cevrilmeli", e.rapor()))
                continue
            ton_yolu = os.path.join(gecici, os.path.splitext(ad)[0] + ".axs")
            with open(ton_yolu, "w", encoding="utf-8") as f:
                f.write(kod)
            p_ton = subprocess.run([sys.executable, AXS, ton_yolu],
                                   capture_output=True, text=True, timeout=120)
            ton_cikti = p_ton.stdout + p_ton.stderr
            if js_cikti == ton_cikti:
                gecen += 1
            else:
                kalan.append((ad, js_cikti.strip()[:200], ton_cikti.strip()[:200]))
    finally:
        shutil.rmtree(gecici, ignore_errors=True)
    return gecen, kalan, False


AG_KUTUSU = os.path.join(KOK, "tests", "ag")

# Sahte gateway'in yollayacagi mesajlar ve REST kaydinin eklenecegi testler
MESAJLAR = {
    "bot.axs": ["!selam", "!topla 10 20 12", "!kutu", "merhaba", "!dur"],
    "soket.tarayici.axs": ["!merhaba"],
    "slash.axs": [],
    "panel.axs": [],
}
# Sahte gateway'in yollayacagi slash etkilesimleri
KOMUTLAR = {
    "panel.axs": [
        {"_t": 2, "name": "ayarla"},
        {"_t": 3, "custom_id": "p_kategori", "values": ["200"]},
        {"_t": 3, "custom_id": "p_ac"},
        {"_t": 5, "custom_id": "p_form", "components": [
            {"components": [{"custom_id": "konu", "value": "Sorun"}]},
            {"components": [{"custom_id": "aciklama", "value": "Detay"}]}]},
    ],
    "slash.axs": [
        {"name": "selam"},
        {"name": "topla", "options": [{"name": "bir", "type": 4, "value": 15},
                                      {"name": "iki", "type": 4, "value": 27}]},
        {"name": "yanki", "options": [{"name": "metin", "type": 3,
                                       "value": "merhaba TON"}]},
        {"name": "olmayan"},
    ],
}
REST_KAYDI = {"bot.axs", "slash.axs", "panel.axs"}


def ag_testleri():
    """Gateway (WebSocket) akisini sahte bir sunucuya karsi dogrular."""
    if not os.path.isdir(AG_KUTUSU):
        return 0, [], True
    sunucu_yolu = os.path.join(AG_KUTUSU, "sahte_gateway.py")
    if not os.path.isfile(sunucu_yolu):
        return 0, [], True

    gecen, kalan = 0, []
    for ad in sorted(os.listdir(AG_KUTUSU)):
        if not ad.endswith(".axs"):
            continue
        beklenen_yol = os.path.join(AG_KUTUSU, os.path.splitext(ad)[0] + ".out")
        if not os.path.exists(beklenen_yol):
            continue
        sira = gecen + len(kalan)
        # Tarayici testleri sabit porta baglanir (env() tarayicida yok)
        port = 8300 if ad.endswith(".tarayici.axs") else 8210 + sira * 2
        rest_port = port + 1
        mesajlar = MESAJLAR.get(ad)
        sunucu_cevresi = dict(os.environ)
        if mesajlar is not None:
            sunucu_cevresi["SAHTE_MESAJLAR"] = json.dumps(mesajlar)
        if ad in KOMUTLAR:
            sunucu_cevresi["SAHTE_KOMUTLAR"] = json.dumps(KOMUTLAR[ad])
        sunucu = subprocess.Popen([sys.executable, sunucu_yolu, str(port)],
                                  stdout=subprocess.PIPE, text=True,
                                  env=sunucu_cevresi)
        rest = subprocess.Popen(
            [sys.executable, AXS, os.path.join(AG_KUTUSU, "sahte_rest.axs")],
            stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True,
            env=dict(os.environ, SAHTE_REST_PORT=str(rest_port)))
        try:
            sunucu.stdout.readline()          # "hazir"
            time.sleep(2.0)                   # REST sunucusu acilsin
            cevre = dict(os.environ,
                         SAHTE_GATEWAY="ws://127.0.0.1:%d/ws/bot" % port,
                         SAHTE_REST="http://127.0.0.1:%d/api" % rest_port)
            if ad.endswith(".tarayici.axs"):
                # Ayni dosyayi tarayici calisma zamaninda (node) calistir
                sys.path.insert(0, KOK)
                from axslang.jston import cevir as _bos  # noqa: F401
                from axslang.derleyici import dosya_derle
                import shutil as _shutil
                node_yolu = _shutil.which("node")
                if not node_yolu:
                    continue
                kod = dosya_derle(os.path.join(AG_KUTUSU, ad))
                js = os.path.join(AG_KUTUSU, "_gecici.js")
                with open(js, "w", encoding="utf-8") as f:
                    f.write(kod)
                calisma = os.path.join(KOK, "axsweb", "tarayici", "axs.js")
                try:
                    p = subprocess.run(
                        [node_yolu, "-e",
                         "setTimeout(()=>process.exit(0), 8000);"
                         "require(%s);require(%s);"
                         % (json.dumps(calisma), json.dumps(js))],
                        capture_output=True, text=True, env=cevre, timeout=120)
                finally:
                    if os.path.exists(js):
                        os.remove(js)
            else:
                p = subprocess.run([sys.executable, AXS, os.path.join(AG_KUTUSU, ad)],
                                   capture_output=True, text=True, env=cevre,
                                   timeout=120)
            bulunan = p.stdout + p.stderr
            if ad in REST_KAYDI:
                rest.terminate()
                bulunan += "".join(
                    satir for satir in (rest.stdout.read() or "").splitlines(True)
                    if satir.startswith("REST "))
        finally:
            sunucu.terminate()
            rest.terminate()
        with open(beklenen_yol, encoding="utf-8") as f:
            beklenen = f.read()
        if bulunan == beklenen:
            gecen += 1
        else:
            kalan.append((ad, beklenen.strip()[:200], bulunan.strip()[:200]))
    return gecen, kalan, False


def main():
    argv = sys.argv[1:]
    guncelle = "--guncelle" in argv
    argv = [a for a in argv if not a.startswith("--")]
    suzgec = argv[0] if argv else None

    gecen, kalan = 0, 0
    for ad in durumlar(suzgec):
        beklenen_yol = os.path.join(KUTU, os.path.splitext(ad)[0] + ".out")
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

    tgecen, tkalan, atlandi = tarayici_testleri()
    if atlandi:
        print("\nTarayici testleri: node bulunamadi, atlandi")
    else:
        print("\nTarayici testleri (Axs -> JavaScript): %d gecti, %d kaldi"
              % (tgecen, len(tkalan)))
    for ad, beklenen, bulunan in tkalan:
        print("  KALDI %s\n    beklenen: %s\n    bulunan : %s" % (ad, beklenen, bulunan))

    jgecen, jkalan, jatlandi = jston_testleri()
    if jatlandi:
        print("\njston testleri: node bulunamadi, atlandi")
    else:
        print("\njston testleri (JavaScript -> AXS, node ile ayni cikti): "
              "%d gecti, %d kaldi" % (jgecen, len(jkalan)))
    for ad, beklenen, bulunan in jkalan:
        print("  KALDI %s\n    node: %s\n    ton : %s" % (ad, beklenen, bulunan))

    agecen, akalan, aatlandi = ag_testleri()
    if not aatlandi:
        print("\nGateway testleri (WebSocket): %d gecti, %d kaldi"
              % (agecen, len(akalan)))
    for ad, beklenen, bulunan in akalan:
        print("  KALDI %s\n    beklenen: %s\n    bulunan : %s" % (ad, beklenen, bulunan))

    toplam_kalan = kalan + len(bkalan) + len(tkalan) + len(jkalan) + len(akalan)
    print("\n%d gecti, %d kaldi"
          % (gecen + bgecen + tgecen + jgecen + agecen, toplam_kalan))
    return 1 if toplam_kalan else 0


if __name__ == "__main__":
    sys.exit(main())
