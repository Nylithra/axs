"""JavaScript AST'sini Axs kaynagina cevirir."""

import os
import re

from ..errors import AxsSyntaxError
from ..okuma import dosya_oku
from .parser import cozumle

GECERLI_AD = re.compile(r"[^\W\d]\w*$")

# --- islec karsiliklari ---
IKILI = {
    "+": "+", "-": "-", "*": "*", "/": "/", "%": "mod", "**": "^",
    "==": "==", "===": "==", "!=": "!=", "!==": "!=",
    "<": "<", ">": ">", "<=": "<=", ">=": ">=",
}
MANTIK = {"&&": "and", "||": "or", "??": "or"}
BIT_ISLECLERI = {"&", "|", "^", "<<", ">>", ">>>", "~"}

# --- hazir is karsiliklari:  JS  ->  Axs ---
GLOBAL_ISLER = {
    "parseInt": "tam", "parseFloat": "sayi", "Number": "sayi", "String": "metin",
    "Boolean": "mantik", "fetch": "get", "alert": "uyari", "confirm": "onay",
    "prompt": "sor", "structuredClone": "kopya",
}
NESNE_ISLERI = {
    ("console", "log"): "print", ("console", "info"): "print",
    ("console", "warn"): "print", ("console", "error"): "print",
    ("console", "debug"): "print",
    ("Math", "floor"): "asagi", ("Math", "ceil"): "yukari", ("Math", "round"): "yuvarla",
    ("Math", "abs"): "mutlak", ("Math", "sqrt"): "karekok", ("Math", "pow"): "us",
    ("Math", "min"): "enkucuk", ("Math", "max"): "enbuyuk", ("Math", "random"): "rastgele",
    ("Math", "trunc"): "tam", ("Math", "log"): "log", ("Math", "sin"): "sin",
    ("Math", "cos"): "cos", ("Math", "tan"): "tan",
    ("JSON", "stringify"): "tojson", ("JSON", "parse"): "json",
    ("Object", "keys"): "keys", ("Object", "values"): "values",
    ("Object", "entries"): "items", ("Object", "assign"): "merge",
    ("Object", "freeze"): "kopya",
    ("document", "getElementById"): "_oge_id", ("document", "querySelector"): "oge",
    ("document", "querySelectorAll"): "ogeler",
    ("localStorage", "setItem"): "sakla", ("localStorage", "getItem"): "saklanan",
    ("localStorage", "removeItem"): "sakli_sil",
}
NESNE_DEGERLERI = {("Math", "PI"): "pi()"}

# --- yontem karsiliklari (dogrudan ayni imza) ---
YONTEMLER = {
    "push": "push", "pop": "pop", "join": "join", "slice": "slice",
    "concat": "merge", "reverse": "reverse", "includes": "contains",
    "indexOf": "find", "map": "map", "filter": "filter", "reduce": "reduce",
    "forEach": "each", "toUpperCase": "upper", "toLowerCase": "lower",
    "trim": "trim", "split": "split", "replace": "replace", "replaceAll": "replace",
    "startsWith": "starts", "endsWith": "ends", "substring": "slice", "substr": "slice",
    "toFixed": None,           # ozel: metin(x, n)
    "toString": None,          # ozel: metin(x)
    "sort": "sort", "find": None, "shift": None, "unshift": None,
}


UCLUK_YARDIMCISI = """# JavaScript'teki `kosul ? evet : hayir` icin yardimci
func _ucluk(kosul, evet, hayir)
  if kosul
    return evet()
  end
  return hayir()
end
"""


YERINDE_YARDIMCISI = """# JS'te reverse()/sort() listeyi yerinde degistirir; bu onu taklit eder
func _yerinde_koy(_l, _yeni)
  _i = 0
  for _o in _yeni
    _l[_i] = _o
    _i += 1
  end
  return _l
end
"""


class Cevirici:
    def __init__(self, dosya=None):
        self.dosya = dosya
        self.satirlar = []
        self.uyarilar = []
        self.isler = set()          # is/sinif olarak bilinen adlar
        self.sayac = 0
        self.sinif_alanlari = {}    # sinif adi -> alan listesi
        self.deyim_basi = 0         # su anki deyimin ciktidaki baslangici
        self.deyim_girinti = 0
        self.bu_adi = "_bu"        # `this` neyi gosteriyor
        self.ucluk_gerekli = False  # a ? b : c kullanildi mi
        self.yerinde_gerekli = False  # reverse()/sort() yerinde degistirme

    # ------------------------------------------------------------ yardimcilar
    def uyar(self, mesaj, satir=None):
        kayit = "satir %s: %s" % (satir, mesaj) if satir else mesaj
        if kayit not in self.uyarilar:
            self.uyarilar.append(kayit)
        return mesaj

    def yaz(self, girinti, metin):
        self.satirlar.append("  " * girinti + metin if metin else "")

    def todo(self, girinti, mesaj, satir=None):
        self.uyar(mesaj, satir)
        self.yaz(girinti, "# TODO: " + mesaj)

    def yeni_ad(self, onek="_g"):
        self.sayac += 1
        return "%s%d" % (onek, self.sayac)

    # ------------------------------------------------------------ giris
    def cevir(self, program):
        self.isler_topla(program)
        self.blok(program, 0)
        if self.yerinde_gerekli:
            self.satirlar = YERINDE_YARDIMCISI.splitlines() + self.satirlar
        if self.ucluk_gerekli:
            self.satirlar = UCLUK_YARDIMCISI.splitlines() + self.satirlar
        govde = "\n".join(self.satirlar).rstrip() + "\n"
        if self.uyarilar:
            basluk = ["# " + "-" * 60,
                      "# jston: %d yer elle gozden gecirilmeli:" % len(self.uyarilar)]
            for u in self.uyarilar:
                basluk.append("#   - " + u)
            basluk.append("# " + "-" * 60)
            govde = "\n".join(basluk) + "\n\n" + govde
        return govde

    def isler_topla(self, deyimler):
        """is/sinif adlarini toplar: bunlar Axs'te ciplak ad olarak yazilir."""
        for d in deyimler:
            t = d.get("t")
            if t == "Is" and d.get("ad"):
                self.isler.add(d["ad"])
            elif t == "Sinif" and d.get("ad"):
                self.isler.add(d["ad"])
                self.sinif_alanlari[d["ad"]] = d
            elif t == "Degiskenler":
                for hedef, baslangic in d["bildirimler"]:
                    if hedef.get("t") == "Ad" and baslangic and \
                            baslangic.get("t") in ("Is", "Sinif"):
                        self.isler.add(hedef["ad"])
            elif t == "Disari":
                self.isler_topla([d["govde"]])
            elif t in ("Blok", "Etiket"):
                self.isler_topla(d.get("govde") or [])

    # ------------------------------------------------------------ deyimler
    def blok(self, deyimler, girinti):
        for d in deyimler:
            self.deyim(d, girinti)

    def deyim(self, d, girinti):
        # Satir ici cok satirli isler bu deyimin HEMEN ONUNE yazilir;
        # boylece kapsam (closure) bozulmaz.
        onceki = (self.deyim_basi, self.deyim_girinti)
        self.deyim_basi = len(self.satirlar)
        self.deyim_girinti = girinti
        try:
            self._deyim(d, girinti)
        finally:
            self.deyim_basi, self.deyim_girinti = onceki

    def _deyim(self, d, girinti):
        t = d["t"]
        satir = d.get("satir")

        if t == "Bos":
            return
        if t == "Blok":
            self.blok(d["govde"], girinti)
            return
        if t == "IfadeDeyimi":
            self.ifade_deyimi(d["ifade"], girinti)
            return
        if t == "Degiskenler":
            for hedef, baslangic in d["bildirimler"]:
                self.bildirim(hedef, baslangic, girinti, satir)
            return
        if t == "Is":
            self.is_yaz(d, girinti)
            return
        if t == "Sinif":
            self.sinif_yaz(d, girinti)
            return
        if t == "Disari":
            self.deyim(d["govde"], girinti)
            return
        if t == "Modul":
            self.yaz(girinti, "# %s %s   (Axs'te: use \"dosya.axs\")" % (d["tur"], d["metin"]))
            self.uyar("'%s' satiri yorum yapildi; Axs'te `use` kullanilir" % d["tur"], satir)
            return
        if t == "Dondur":
            if d["deger"] is None:
                self.yaz(girinti, "return null")
            else:
                self.yaz(girinti, "return " + self.ifade(d["deger"]))
            return
        if t == "Kir":
            self.yaz(girinti, "stop")
            return
        if t == "Devam":
            self.yaz(girinti, "skip")
            return
        if t == "Firlat":
            self.yaz(girinti, "hata(%s)" % self.hata_metni(d["deger"]))
            return
        if t == "Eger":
            self.eger_yaz(d, girinti)
            return
        if t == "Surece":
            self.yaz(girinti, "while " + self.ifade(d["kosul"]))
            self.blok(d["govde"], girinti + 1)
            self.yaz(girinti, "end")
            return
        if t == "YapSurece":
            self.yaz(girinti, "while true")
            self.blok(d["govde"], girinti + 1)
            self.yaz(girinti + 1, "if not (%s)" % self.ifade(d["kosul"]))
            self.yaz(girinti + 2, "stop")
            self.yaz(girinti + 1, "end")
            self.yaz(girinti, "end")
            return
        if t == "For":
            self.for_yaz(d, girinti)
            return
        if t == "ForIcinde":
            self.for_icinde_yaz(d, girinti, anahtar=False)
            return
        if t == "ForAnahtar":
            self.for_icinde_yaz(d, girinti, anahtar=True)
            return
        if t == "Secim":
            self.secim_yaz(d, girinti)
            return
        if t == "Dene":
            self.dene_yaz(d, girinti)
            return
        if t == "Etiket":
            self.todo(girinti, "'%s:' etiketi Axs'te yok" % d["ad"], satir)
            self.deyim(d["govde"], girinti)
            return
        self.todo(girinti, "'%s' deyimi cevrilemedi" % t, satir)

    def ifade_deyimi(self, e, girinti):
        t = e["t"]
        satir = e.get("satir")
        if t == "Guncelle":                      # x++  ->  x += 1
            hedef = self.atama_hedefi(e["deger"])
            self.yaz(girinti, "%s %s 1" % (hedef, "+=" if e["islec"] == "++" else "-="))
            return
        if t == "Atama":
            # a = b = 5  ->  b = 5 ;  a = b
            if e["deger"].get("t") == "Atama" and e["islec"] == "=":
                self.ifade_deyimi(e["deger"], girinti)
                self.yaz(girinti, "%s = %s" % (self.atama_hedefi(e["hedef"]),
                                               self.ifade(e["deger"]["hedef"])))
                return
            self.atama_yaz(e, girinti)
            return
        if t == "Sira":
            for oge in e["ogeler"]:
                self.ifade_deyimi(oge, girinti)
            return
        if t == "Metin":                         # "use strict" gibi
            self.yaz(girinti, "# " + e["deger"])
            return
        self.yaz(girinti, self.ifade(e))

    def bildirim(self, hedef, baslangic, girinti, satir):
        if hedef["t"] == "Ad":
            if baslangic is None:
                self.yaz(girinti, "%s = null" % hedef["ad"])
            elif baslangic["t"] == "Is":
                self.is_yaz(baslangic, girinti, ad=hedef["ad"])
            elif baslangic["t"] == "Sinif":
                self.sinif_yaz(baslangic, girinti, ad=hedef["ad"])
            else:
                # `const n = { selam() { return this.ad } }` icin `this` -> n
                eski_bu = self.bu_adi
                if baslangic["t"] == "Nesne":
                    self.bu_adi = hedef["ad"]
                try:
                    self.yaz(girinti, "%s = %s" % (hedef["ad"], self.ifade(baslangic)))
                finally:
                    self.bu_adi = eski_bu
            return
        # dagitici atama:  const [a, b] = x   /   const {a, b} = x
        gecici = self.yeni_ad("_dagit")
        self.yaz(girinti, "%s = %s" % (gecici, self.ifade(baslangic) if baslangic else "null"))
        if hedef["t"] == "Dizi":
            for sira, oge in enumerate(hedef["ogeler"]):
                if oge["t"] == "Bos":
                    continue
                if oge["t"] != "Ad":
                    self.todo(girinti, "ic ice dagitici atama cevrilemedi", satir)
                    continue
                self.yaz(girinti, "%s = %s[%d]" % (oge["ad"], gecici, sira))
        elif hedef["t"] == "Nesne":
            for tur, anahtar, deger in hedef["ciftler"]:
                if tur != "duz" or deger["t"] != "Ad":
                    self.todo(girinti, "ic ice dagitici atama cevrilemedi", satir)
                    continue
                self.yaz(girinti, "%s = %s.%s" % (deger["ad"], gecici, anahtar["deger"]))
        else:
            self.todo(girinti, "dagitici atama cevrilemedi", satir)

    def atama_yaz(self, e, girinti):
        hedef = self.atama_hedefi(e["hedef"])
        islec = e["islec"]
        if islec == "=":
            self.yaz(girinti, "%s = %s" % (hedef, self.ifade(e["deger"])))
            return
        if islec in ("+=", "-=", "*=", "/="):
            self.yaz(girinti, "%s %s %s" % (hedef, islec, self.ifade(e["deger"])))
            return
        if islec == "%=":
            self.yaz(girinti, "%s = %s mod %s"
                     % (hedef, self.oku(e["hedef"]), self.ifade(e["deger"])))
            return
        if islec == "**=":
            self.yaz(girinti, "%s = %s ^ %s"
                     % (hedef, self.oku(e["hedef"]), self.ifade(e["deger"])))
            return
        if islec in ("||=", "??="):
            self.yaz(girinti, "if not %s" % self.oku(e["hedef"]))
            self.yaz(girinti + 1, "%s = %s" % (hedef, self.ifade(e["deger"])))
            self.yaz(girinti, "end")
            return
        if islec == "&&=":
            self.yaz(girinti, "if %s" % self.oku(e["hedef"]))
            self.yaz(girinti + 1, "%s = %s" % (hedef, self.ifade(e["deger"])))
            self.yaz(girinti, "end")
            return
        self.todo(girinti, "'%s' atamasi cevrilemedi (bit islemleri Axs'te yok)" % islec,
                  e.get("satir"))

    def atama_hedefi(self, e):
        """Atamanin SOL tarafi: Axs'te ciplak ad ya da x.alan yazilir."""
        if e["t"] == "Ad":
            return e["ad"]
        if e["t"] == "Bu":
            return self.bu_adi
        if e["t"] == "Uye":
            nesne = self.ifade(e["nesne"])
            if e["hesapli"]:
                return "%s[%s]" % (nesne, self.ifade(e["ad"]))
            return "%s.%s" % (nesne, e["ad"])
        self.uyar("atama hedefi cevrilemedi: %s" % e["t"], e.get("satir"))
        return "_cevrilemedi"

    def oku(self, e):
        return self.ifade(e)

    def eger_yaz(self, d, girinti, anahtar="if"):
        self.yaz(girinti, "%s %s" % (anahtar, self.ifade(d["kosul"])))
        self.blok(d["govde"], girinti + 1)
        digeri = d["digeri"]
        if digeri:
            if len(digeri) == 1 and digeri[0]["t"] == "Eger":
                self.eger_yaz(digeri[0], girinti, "elif")
                return
            self.yaz(girinti, "else")
            self.blok(digeri, girinti + 1)
        self.yaz(girinti, "end")

    def sayac_dongusu(self, d):
        """for (let i = 0; i < n; i++) bicimini yakalar."""
        bas, kosul, adim = d["baslangic"], d["kosul"], d["adim"]
        if not (bas and kosul and adim):
            return None
        if bas["t"] != "Degiskenler" or len(bas["bildirimler"]) != 1:
            return None
        hedef, baslangic = bas["bildirimler"][0]
        if hedef["t"] != "Ad" or baslangic is None:
            return None
        ad = hedef["ad"]
        if kosul["t"] != "Ikili" or kosul["islec"] not in ("<", "<=") \
                or kosul["sol"].get("t") != "Ad" or kosul["sol"]["ad"] != ad:
            return None
        if adim["t"] != "Guncelle" or adim["islec"] != "++" \
                or adim["deger"].get("t") != "Ad" or adim["deger"]["ad"] != ad:
            return None
        return ad, baslangic, kosul

    def for_yaz(self, d, girinti):
        sayac = self.sayac_dongusu(d)
        if sayac:
            ad, baslangic, kosul = sayac
            son = self.ifade(kosul["sag"])
            if kosul["islec"] == "<":
                son = "%s - 1" % son if not son.lstrip("-").isdigit() \
                    else str(int(son) - 1)
            self.yaz(girinti, "for %s in range(%s, %s)"
                     % (ad, self.ifade(baslangic), son))
            self.blok(d["govde"], girinti + 1)
            self.yaz(girinti, "end")
            return
        if d["baslangic"]:
            self.deyim(d["baslangic"], girinti)
        if self.icerir(d["govde"], "Devam") and d["adim"]:
            self.todo(girinti, "dongude 'continue' var: 'skip' adim satirini atlar, "
                                "elle kontrol et", d.get("satir"))
        self.yaz(girinti, "while " + (self.ifade(d["kosul"]) if d["kosul"] else "true"))
        self.blok(d["govde"], girinti + 1)
        if d["adim"]:
            self.ifade_deyimi(d["adim"], girinti + 1)
        self.yaz(girinti, "end")

    def icerir(self, deyimler, tur):
        for d in deyimler:
            if not isinstance(d, dict):
                continue
            if d.get("t") == tur:
                return True
            for deger in d.values():
                if isinstance(deger, list) and deger and isinstance(deger[0], dict):
                    if self.icerir(deger, tur):
                        return True
                elif isinstance(deger, dict) and deger.get("t") and self.icerir([deger], tur):
                    return True
        return False

    def for_icinde_yaz(self, d, girinti, anahtar):
        hedef = d["hedef"]
        if hedef["t"] == "Degiskenler":
            ad_dugumu = hedef["bildirimler"][0][0]
        else:
            ad_dugumu = hedef.get("ifade", {})
        ad = ad_dugumu.get("ad") if ad_dugumu.get("t") == "Ad" else None
        if ad is None:
            ad = self.yeni_ad("_oge")
            self.todo(girinti, "dongu degiskeni cozulemedi", d.get("satir"))
        kaynak = self.ifade(d["kaynak"])
        self.yaz(girinti, "for %s in %s" % (ad, "keys(%s)" % kaynak if anahtar else kaynak))
        self.blok(d["govde"], girinti + 1)
        self.yaz(girinti, "end")

    def secim_yaz(self, d, girinti):
        deger = self.ifade(d["deger"])
        anahtar = "if"
        varsayilan = None
        for durum, govde in d["dallar"]:
            if durum is None:
                varsayilan = govde
                continue
            if govde and not self.icerir(govde, "Kir"):
                self.uyar("switch dalinda 'break' yok: Axs'te alt dala dusme yoktur",
                          d.get("satir"))
            self.yaz(girinti, "%s %s == %s" % (anahtar, deger, self.ifade(durum)))
            self.blok([s for s in govde if s["t"] != "Kir"], girinti + 1)
            anahtar = "elif"
        if varsayilan is not None:
            if anahtar == "if":
                self.blok([s for s in varsayilan if s["t"] != "Kir"], girinti)
                return
            self.yaz(girinti, "else")
            self.blok([s for s in varsayilan if s["t"] != "Kir"], girinti + 1)
        if anahtar != "if":
            self.yaz(girinti, "end")

    def dene_yaz(self, d, girinti):
        self.yaz(girinti, "try")
        self.blok(d["govde"], girinti + 1)
        ad = d["hata_adi"]["ad"] if d["hata_adi"] and d["hata_adi"]["t"] == "Ad" else "hata"
        self.yaz(girinti, "catch " + ad)
        self.blok(d["yakala"] or [], girinti + 1)
        self.yaz(girinti, "end")
        if d["sonunda"]:
            self.yaz(girinti, "# finally: Axs'te yok, asagidaki satirlar her durumda calisir")
            self.uyar("'finally' blogu try'dan sonraya tasindi", d.get("satir"))
            self.blok(d["sonunda"], girinti)

    def is_yaz(self, d, girinti, ad=None):
        ad = ad or d.get("ad") or self.yeni_ad("_is")
        self.isler.add(ad)
        params, hazirlik = self.params_yaz(d["params"], d.get("satir"))
        self.yaz(girinti, "func %s(%s)" % (ad, ", ".join(params)))
        for satir_metni in hazirlik:
            self.yaz(girinti + 1, satir_metni)
        self.blok(d["govde"], girinti + 1)
        self.yaz(girinti, "end")

    def params_yaz(self, params, satir):
        adlar = []
        hazirlik = []
        for tur, hedef, varsayilan in params:
            if tur == "kalan":
                self.uyar("'...%s' (kalan parametreler) Axs'te yok" % hedef, satir)
                adlar.append(hedef)
                continue
            if hedef["t"] != "Ad":
                gecici = self.yeni_ad("_p")
                adlar.append(gecici)
                self.uyar("parametrede dagitici atama elle cozulmeli", satir)
                continue
            if varsayilan is not None:
                adlar.append("%s = %s" % (hedef["ad"], self.ifade(varsayilan)))
            else:
                adlar.append(hedef["ad"])
        return adlar, hazirlik

    def sinif_yaz(self, d, girinti, ad=None):
        ad = ad or d.get("ad") or self.yeni_ad("_sinif")
        self.isler.add(ad)
        if d.get("ata"):
            self.uyar("'extends' (kalitim) Axs'te yok; '%s' icin elle cozulmeli" % ad,
                      d.get("satir"))
        kurucu = None
        yontemler = []
        alanlar = []
        for tur, uye_adi, deger, durağan in d["uyeler"]:
            if tur == "yontem" and uye_adi == "constructor":
                kurucu = deger
            elif tur == "yontem":
                yontemler.append((uye_adi, deger))
            else:
                alanlar.append((uye_adi, deger))
        params = []
        if kurucu:
            params, _ = self.params_yaz(kurucu["params"], d.get("satir"))
        self.yaz(girinti, "# sinif %s  ->  nesne ureten is" % ad)
        self.yaz(girinti, "func %s(%s)" % (ad, ", ".join(params)))
        self.yaz(girinti + 1, "_bu = {}")
        for uye_adi, deger in alanlar:
            self.yaz(girinti + 1, "_bu.%s = %s"
                     % (uye_adi, self.ifade(deger) if deger else "null"))
        for uye_adi, yontem in yontemler:
            y_params, _ = self.params_yaz(yontem["params"], d.get("satir"))
            self.yaz(girinti + 1, "func %s(%s)" % (uye_adi, ", ".join(y_params)))
            self.blok(yontem["govde"], girinti + 2)
            self.yaz(girinti + 1, "end")
            self.yaz(girinti + 1, "_bu.%s = %s" % (uye_adi, uye_adi))
        if kurucu:
            self.blok(kurucu["govde"], girinti + 1)
        self.yaz(girinti + 1, "return _bu")
        self.yaz(girinti, "end")

    def hata_metni(self, e):
        if e is None:
            return '"hata"'
        if e["t"] == "Yeni" and e["hedef"].get("ad", "").endswith("Error"):
            return self.ifade(e["args"][0]) if e["args"] else '"hata"'
        return self.ifade(e)

    # ------------------------------------------------------------ ifadeler
    def ifade(self, e, cagri_hedefi=False):
        if e is None:
            return "null"
        t = e["t"]
        satir = e.get("satir")

        if t == "Sayi":
            return repr(e["deger"]) if isinstance(e["deger"], float) else str(e["deger"])
        if t == "Metin":
            return axs_metin(e["deger"])
        if t == "Dogruluk":
            return "true" if e["deger"] else "false"
        if t == "Bos":
            return "null"
        if t == "Bu":
            return self.bu_adi
        if t == "Ad":
            ad = e["ad"]
            if cagri_hedefi:
                return ad
            return ad
        if t == "Sablon":
            return self.sablon(e)
        if t == "Duzenli":
            self.uyar("duzenli ifade metne cevrildi: /%s/ (match/matches ile kullan)"
                      % e["desen"], satir)
            return axs_metin(e["desen"])
        if t == "Dizi":
            return "[%s]" % ", ".join(self.ifade(o) for o in e["ogeler"]
                                      if o["t"] != "Bos")
        if t == "Nesne":
            return self.nesne(e)
        if t == "Is":
            return self.ok_isi(e)
        if t == "Sinif":
            self.uyar("ifade icindeki sinif cevrilemedi", satir)
            return "null"
        if t == "Uye":
            return self.uye(e)
        if t == "Cagri":
            return self.cagri(e)
        if t == "Yeni":
            return self.yeni(e)
        if t == "Ikili":
            return self.ikili(e)
        if t == "Mantik":
            if e["islec"] == "??":
                self.uyar("'??' yerine 'or' yazildi: JS'te sadece null/undefined'da, "
                          "Axs'te bos degerlerin hepsinde saga gecer", satir)
            return "(%s %s %s)" % (self.ifade(e["sol"]), MANTIK[e["islec"]],
                                   self.ifade(e["sag"]))
        if t == "Tekli":
            return self.tekli(e)
        if t == "Kosul":
            # a ? b : c  ->  _ucluk(a, func() -> b, func() -> c)
            # Dallar is olarak sarilir; boylece sadece secilen dal calisir.
            self.ucluk_gerekli = True
            return "_ucluk(%s, func() -> %s, func() -> %s)" % (
                self.ifade(e["kosul"]), self.ifade(e["evet"]), self.ifade(e["hayir"]))
        if t == "Atama":
            self.uyar("ifade icinde atama cevrilemedi", satir)
            return self.ifade(e["deger"])
        if t == "Guncelle":
            self.uyar("ifade icinde ++/-- cevrilemedi", satir)
            return self.ifade(e["deger"])
        if t == "Yayilim":
            self.uyar("'...' (yayilim) Axs'te yok", satir)
            return self.ifade(e["deger"])
        if t == "Sira":
            return self.ifade(e["ogeler"][-1])
        if t == "Ust":
            self.uyar("'super' Axs'te yok", satir)
            return "null"
        self.uyar("'%s' ifadesi cevrilemedi" % t, satir)
        return "null"

    def sablon(self, e):
        parcalar = []
        for tur, deger in e["parcalar"]:
            if tur == "text":
                parcalar.append(deger.replace("%", "%%").replace("\\", "\\\\")
                                .replace('"', '\\"'))
            else:
                parcalar.append("(%s);" % self.ifade(deger))
        return '"%s"' % "".join(parcalar)

    def nesne(self, e):
        parcalar = []
        for tur, anahtar, deger in e["ciftler"]:
            if tur == "yayilim":
                self.uyar("nesne icinde '...' Axs'te yok", e.get("satir"))
                continue
            if tur == "hesapli":
                ad = self.ifade(anahtar)
            else:
                ham = anahtar["deger"]
                ad = ham if GECERLI_AD.match(ham) else axs_metin(ham)
            parcalar.append("%s: %s" % (ad, self.ifade(deger)))
        return "{%s}" % ", ".join(parcalar)

    def ok_isi(self, e):
        """Satir ici is: tek ifadelikse `func(x) -> ...`, degilse ayri yazilir."""
        params, _ = self.params_yaz(e["params"], e.get("satir"))
        govde = e["govde"]
        if len(govde) == 1 and govde[0]["t"] == "Dondur" and govde[0]["deger"] is not None:
            return "func(%s) -> %s" % (", ".join(params), self.ifade(govde[0]["deger"]))
        # cok satirli: ayri bir is olarak en uste yazilir, burada adi kullanilir
        ad = self.yeni_ad("_is")
        self.uyar("cok satirli satir ici is '%s' adiyla ayri yazildi" % ad, e.get("satir"))
        eski_satirlar = self.satirlar
        self.satirlar = []
        self.is_yaz(e, self.deyim_girinti, ad=ad)
        uretilen = self.satirlar
        self.satirlar = eski_satirlar
        self.satirlar[self.deyim_basi:self.deyim_basi] = uretilen
        self.deyim_basi += len(uretilen)
        return ad

    def uye(self, e):
        nesne = e["nesne"]
        if nesne["t"] == "Ad" and not e["hesapli"]:
            anahtar = (nesne["ad"], e["ad"])
            if anahtar in NESNE_DEGERLERI:
                return NESNE_DEGERLERI[anahtar]
        if not e["hesapli"] and e["ad"] == "length":
            return "len(%s)" % self.ifade(nesne)
        hedef = self.ifade(nesne)
        if e["hesapli"]:
            return "%s[%s]" % (hedef, self.ifade(e["ad"]))
        return "%s.%s" % (hedef, e["ad"])

    def cagri(self, e):
        hedef = e["hedef"]
        args = [self.ifade(a) for a in e["args"]]

        # console.log(...) gibi
        if hedef["t"] == "Uye" and not hedef["hesapli"] and hedef["nesne"]["t"] == "Ad":
            anahtar = (hedef["nesne"]["ad"], hedef["ad"])
            if anahtar in NESNE_ISLERI:
                axs_adi = NESNE_ISLERI[anahtar]
                if axs_adi == "_oge_id":
                    ic = args[0] if args else '""'
                    return 'oge("#" + %s)' % ic if not ic.startswith('"') \
                        else 'oge("#%s")' % ic[1:-1]
                return "%s(%s)" % (axs_adi, ", ".join(args))
            if hedef["nesne"]["ad"] == "Array" and hedef["ad"] == "isArray":
                return '(type(%s) == "liste")' % (args[0] if args else "null")

        # yontem cagrisi:  x.map(...)
        if hedef["t"] == "Uye" and not hedef["hesapli"]:
            return self.yontem_cagrisi(hedef, e, args)

        # duz is cagrisi
        if hedef["t"] == "Ad":
            ad = hedef["ad"]
            if ad in GLOBAL_ISLER:
                return "%s(%s)" % (GLOBAL_ISLER[ad], ", ".join(args))
            if ad == "setTimeout" and len(args) >= 2:
                return "after(%s / 1000, %s)" % (args[1], args[0])
            if ad == "setInterval" and len(args) >= 2:
                return "every(%s / 1000, %s)" % (args[1], args[0])
            if ad == "require":
                self.uyar("require(): Axs'te `use \"dosya.axs\"` kullanilir",
                          e.get("satir"))
                return "null"
            return "%s(%s)" % (ad, ", ".join(args))
        return "%s(%s)" % (self.ifade(hedef), ", ".join(args))

    def yontem_cagrisi(self, hedef, e, args):
        ad = hedef["ad"]
        nesne = self.ifade(hedef["nesne"])
        satir = e.get("satir")
        if ad == "toFixed":
            return "metin(%s%s)" % (nesne, (", " + args[0]) if args else "")
        if ad == "toString":
            return "metin(%s)" % nesne
        if ad == "find":
            return "first(filter(%s, %s))" % (nesne, args[0] if args else "null")
        if ad == "findIndex":
            self.uyar("findIndex() karsiligi yok; filter/find ile cozulmeli", satir)
        if ad == "shift":
            return "%s.pop(0)" % nesne
        if ad == "unshift":
            return "%s.insert(0, %s)" % (nesne, args[0] if args else "null")
        if ad in ("splice", "every", "some", "flatMap", "matchAll", "exec", "test"):
            karsilik = {"every": "all", "some": "any", "flatMap": "map",
                        "test": "contains"}.get(ad)
            if karsilik:
                return "%s(%s%s)" % (karsilik, nesne,
                                     (", " + ", ".join(args)) if args else "")
            self.uyar("'%s()' karsiligi yok, elle yaz" % ad, satir)
            return "%s.%s(%s)" % (nesne, ad, ", ".join(args))
        if ad in ("map", "filter", "forEach", "reduce") and len(args) == 1:
            pass
        if ad == "replace":
            # JS'te replace() sadece ilk eslesmeyi degistirir
            return "%s.replace(%s, 1)" % (nesne, ", ".join(args)) if len(args) >= 2 \
                else "%s.replace(%s)" % (nesne, ", ".join(args))
        if ad in ("reverse", "sort"):
            return self.yerinde_yontem(ad, nesne, e, args)
        if ad in YONTEMLER and YONTEMLER[ad]:
            return "%s.%s(%s)" % (nesne, YONTEMLER[ad], ", ".join(args))
        if ad == "addEventListener" and len(args) >= 2:
            olay = e["args"][0]
            if olay["t"] == "Metin" and olay["deger"] == "click":
                return "tikla(%s, %s)" % (nesne, args[1])
            return "olay(%s, %s, %s)" % (nesne, args[0], args[1])
        return "%s.%s(%s)" % (nesne, ad, ", ".join(args))

    def yerinde_yontem(self, ad, nesne, e, args):
        """JS'te reverse()/sort() listeyi YERINDE degistirir; Axs'te yeni liste doner.

        Ayni davranis icin _yerinde_koy() yardimcisi kullanilir."""
        if ad == "reverse":
            yeni_liste = "reverse(%s)" % nesne
        else:
            yeni_liste = "sort(%s%s)" % (nesne, self.sirala_argumani(e))
        if e["hedef"]["nesne"]["t"] in ("Ad", "Uye", "Bu"):
            self.yerinde_gerekli = True
            return "_yerinde_koy(%s, %s)" % (nesne, yeni_liste)
        return yeni_liste

    def sirala_argumani(self, e):
        """sort((a,b) => a-b) gibi yaygin karsilastiricilari Axs'e cevirir."""
        args = e["args"]
        if not args:
            return ""
        k = args[0]
        if k.get("t") != "Is" or len(k.get("params", [])) != 2:
            self.uyar("sort() karsilastiricisi cevrilemedi; Axs'te alan adi ya da "
                      "anahtar isi verilir", e.get("satir"))
            return ""
        adlar = [p[1].get("ad") for p in k["params"] if p[0] == "duz"]
        govde = k["govde"]
        if len(govde) != 1 or govde[0]["t"] != "Dondur":
            self.uyar("sort() karsilastiricisi cevrilemedi", e.get("satir"))
            return ""
        ifade = govde[0]["deger"]
        if ifade.get("t") != "Ikili" or ifade.get("islec") != "-":
            self.uyar("sort() karsilastiricisi cevrilemedi", e.get("satir"))
            return ""
        sol, sag = ifade["sol"], ifade["sag"]
        sol_ad, sol_alan = self._sirala_parcasi(sol)
        sag_ad, sag_alan = self._sirala_parcasi(sag)
        if sol_ad is None or sag_ad is None or sol_alan != sag_alan:
            self.uyar("sort() karsilastiricisi cevrilemedi", e.get("satir"))
            return ""
        alan = (", " + axs_metin(sol_alan)) if sol_alan else ""
        if sol_ad == adlar[0] and sag_ad == adlar[1]:
            return alan
        if sol_ad == adlar[1] and sag_ad == adlar[0]:
            return (alan or ", null") + ", tersten: true"
        self.uyar("sort() karsilastiricisi cevrilemedi", e.get("satir"))
        return ""

    @staticmethod
    def _sirala_parcasi(e):
        """`a` ya da `a.alan` bicimini (ad, alan) olarak verir."""
        if e.get("t") == "Ad":
            return e["ad"], None
        if e.get("t") == "Uye" and not e.get("hesapli") and e["nesne"].get("t") == "Ad":
            return e["nesne"]["ad"], e["ad"]
        return None, None

    def yeni(self, e):
        hedef = e["hedef"]
        args = [self.ifade(a) for a in e["args"]]
        if hedef["t"] == "Ad":
            ad = hedef["ad"]
            if ad.endswith("Error"):
                return "hata(%s)" % (args[0] if args else '"hata"')
            if ad == "Date":
                return "now()"
            if ad == "Array":
                return "[]" if not args else "[]"
            if ad in ("Map", "Set", "Object"):
                self.uyar("new %s() yerine Axs haritasi/listesi kullanildi" % ad,
                          e.get("satir"))
                return "{}" if ad in ("Map", "Object") else "[]"
            return "%s(%s)" % (ad, ", ".join(args))
        return "%s(%s)" % (self.ifade(hedef), ", ".join(args))

    def ikili(self, e):
        islec = e["islec"]
        if islec in BIT_ISLECLERI:
            self.uyar("bit islemi '%s' Axs'te yok" % islec, e.get("satir"))
            return "0  # TODO: %s islemi" % islec
        if islec == "instanceof":
            self.uyar("'instanceof' Axs'te yok; type() ile karsilastir", e.get("satir"))
            return "false"
        if islec == "in":
            return "has(%s, %s)" % (self.ifade(e["sag"]), self.ifade(e["sol"]))
        axs_islec = IKILI.get(islec)
        if axs_islec is None:
            self.uyar("'%s' isleci cevrilemedi" % islec, e.get("satir"))
            return "null"
        return "(%s %s %s)" % (self.ifade(e["sol"]), axs_islec, self.ifade(e["sag"]))

    def tekli(self, e):
        islec = e["islec"]
        deger = self.ifade(e["deger"])
        if islec == "!":
            return "(not %s)" % deger
        if islec == "-":
            return "-%s" % deger
        if islec == "+":
            return "sayi(%s)" % deger
        if islec == "typeof":
            self.uyar("typeof: Axs'te tur adlari farklidir "
                      "(metin/sayi/bool/liste/harita/null)", e.get("satir"))
            return "type(%s)" % deger
        if islec == "await":
            return deger              # Axs'te her sey zaten sirayla akar
        if islec == "void":
            return "null"
        if islec == "delete":
            if e["deger"]["t"] == "Uye" and not e["deger"]["hesapli"]:
                return "remove(%s, %s)" % (self.ifade(e["deger"]["nesne"]),
                                           axs_metin(e["deger"]["ad"]))
            return "remove(%s)" % deger
        if islec == "~":
            self.uyar("bit islemi '~' Axs'te yok", e.get("satir"))
            return "0"
        self.uyar("'%s' tekli isleci cevrilemedi" % islec, e.get("satir"))
        return deger


def axs_metin(s):
    """Python metnini Axs metin sabitine cevirir."""
    govde = (s.replace("\\", "\\\\").replace('"', '\\"')
             .replace("%", "%%").replace("\n", "\\n").replace("\t", "\\t"))
    return '"%s"' % govde


def cevir(kaynak, dosya=None):
    """JavaScript kaynagini Axs kaynagina cevirir."""
    program = cozumle(kaynak, dosya)
    c = Cevirici(dosya)
    return c.cevir(program), c.uyarilar


def dosya_cevir(yol):
    if not os.path.isfile(yol):
        raise AxsSyntaxError("Dosya bulunamadi: %s" % yol)
    return cevir(dosya_oku(yol), yol)
