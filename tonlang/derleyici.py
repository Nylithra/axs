"""TON -> JavaScript derleyicisi (tarayici tarafi).

Cekirdek ile ayni lexer ve parser kullanilir; burada sadece AST JavaScript'e
cevrilir. Uretilen kodun tamami `async`tir: TON'da

    sonuc = get("/api/veri")

diye duz yazarsin, tarayicida bu `await`li bir fetch olur. Boylece dilin
"her sey basit" kurali tarayicida da bozulmaz.
"""

import json
import os

from . import nodes as N
from .errors import TonError, TonRuntimeError, TonSyntaxError
from .okuma import dosya_oku
from .parser import cozumle, cozumle_ifade
from .surum import UZANTILAR

ONEK = "$"

# `ai = "groq"` gibi: hem degisken hem ayar olan adlar. Cekirdekte yorumlayici
# degiskeni dogrudan okur; tarayicida derlenmis koddan calisma zamanina bildirilir.
AYAR_ADLARI = {"ai"}

IKILI_ISLER = {
    "+": "topla", "-": "cikar", "*": "carp", "/": "bol", "mod": "kalan", "^": "us",
    "==": "esit", "!=": "esit_degil", "<": "kucuk", ">": "buyuk",
    "<=": "kucuk_esit", ">=": "buyuk_esit",
}

# Tarayicida calismayan hazir isler -> daha anlasilir hata mesaji icin
TARAYICIDA_YOK = {
    "meta": "kod uretimi cekirdekte calisir",
    "kodu_calistir": "kod uretimi cekirdekte calisir",
    "define": "kod uretimi cekirdekte calisir",
    "tanimla": "kod uretimi cekirdekte calisir",
    "eval_ton": "kod uretimi cekirdekte calisir",
    "degerini_bul": "kod uretimi cekirdekte calisir",
    "get_var": "degiskenlere ad ile erisim cekirdekte calisir",
    "degeri": "degiskenlere ad ile erisim cekirdekte calisir",
    "set_var": "degiskenlere ad ile erisim cekirdekte calisir",
    "degeri_ayarla": "degiskenlere ad ile erisim cekirdekte calisir",
    "names": "degiskenlere ad ile erisim cekirdekte calisir",
    "adlar": "degiskenlere ad ile erisim cekirdekte calisir",
    "defined": "degiskenlere ad ile erisim cekirdekte calisir",
    "tanimli_mi": "degiskenlere ad ile erisim cekirdekte calisir",
    "read": "dosya isleri cekirdekte calisir",
    "oku": "dosya isleri cekirdekte calisir",
    "save": "dosya isleri cekirdekte calisir",
    "kaydet": "dosya isleri cekirdekte calisir",
    "append": "dosya isleri cekirdekte calisir",
    "dosya_ekle": "dosya isleri cekirdekte calisir",
    "delete": "dosya isleri cekirdekte calisir",
    "dosya_sil": "dosya isleri cekirdekte calisir",
    "files": "dosya isleri cekirdekte calisir",
    "dosyalar": "dosya isleri cekirdekte calisir",
    "folder": "dosya isleri cekirdekte calisir",
    "klasor": "dosya isleri cekirdekte calisir",
    "size": "dosya isleri cekirdekte calisir",
    "boyut": "dosya isleri cekirdekte calisir",
    "file_exists": "dosya isleri cekirdekte calisir",
    "dosya_var": "dosya isleri cekirdekte calisir",
    "env": "ortam degiskenleri cekirdekte okunur",
    "ortam": "ortam degiskenleri cekirdekte okunur",
    "download": "dosya indirmek cekirdekte calisir",
    "indir": "dosya indirmek cekirdekte calisir",
}


class Kapsam:
    def __init__(self, ust=None, tur="program"):
        self.adlar = set()
        self.ust = ust
        self.tur = tur

    def bildir(self, ad):
        self.adlar.add(ad)

    def bildir_yeni(self, ad):
        """Ad bir ust kapsamda varsa oraya yazilir; yoksa burada acilir.

        Cekirdekteki Kapsam.ata kurali ile ayni davranis. Ayri bir dosya
        ("use ... as") kendi adlarini her zaman kendi icinde acar."""
        if self.tur == "modul" or not self.var_mi(ad):
            self.adlar.add(ad)

    def var_mi(self, ad):
        k = self
        while k is not None:
            if ad in k.adlar:
                return True
            k = k.ust
        return False


class Derleyici:
    def __init__(self, dosya=None, hazir_isler=None):
        self.dosya = dosya
        self.kok = os.path.dirname(os.path.abspath(dosya)) if dosya else os.getcwd()
        self.hazir = hazir_isler if hazir_isler is not None else _hazir_isler()
        self.onbellek = {}      # yol -> cozumlenmis program
        self.eklenenler = set()  # koda gomulmus dosyalar
        self.sayac = 0

    # ------------------------------------------------------------ giris
    def derle(self, kaynak, ad=None):
        program = cozumle(kaynak, self.dosya)
        kapsam = Kapsam(None, "program")
        self.adlari_topla(program, kapsam)
        govde = self.blok(program, kapsam, 1)
        bildirim = self.bildirimler(kapsam, 1)
        basluk = "// %s - TON derleyicisi urunudur\n" % (ad or self.dosya or "ton")
        return (basluk
                + "TON.calistir(async function (T) {\n"
                + bildirim + govde
                + "});\n")

    # ------------------------------------------------------------ ad toplama
    def adlari_topla(self, deyimler, kapsam):
        """Bir kapsamda atanan butun adlari bulur (ic islere inmez)."""
        for d in deyimler:
            t = d.tur
            if t == "Ata":
                hedef = d.hedef
                if isinstance(hedef, (N.Ad, N.Degisken)):
                    kapsam.bildir_yeni(hedef.ad)
            elif t == "IsTanimi":
                if d.ad:
                    kapsam.bildir_yeni(d.ad)
            elif t == "Her":
                kapsam.bildir_yeni(d.ad)
                if d.ikinci:
                    kapsam.bildir_yeni(d.ikinci)
                self.adlari_topla(d.govde, kapsam)
            elif t == "Tekrarla":
                if d.sayac:
                    kapsam.bildir_yeni(d.sayac)
                self.adlari_topla(d.govde, kapsam)
            elif t == "Eger":
                for _, govde in d.dallar:
                    self.adlari_topla(govde, kapsam)
                if d.digeri:
                    self.adlari_topla(d.digeri, kapsam)
            elif t == "Surece":
                self.adlari_topla(d.govde, kapsam)
            elif t == "Dene":
                kapsam.bildir_yeni("hata")
                if d.hata_adi:
                    kapsam.bildir_yeni(d.hata_adi)
                self.adlari_topla(d.govde, kapsam)
                self.adlari_topla(d.yakala_govde, kapsam)
            elif t == "Kullan":
                self.kullan_adlari(d, kapsam)

    def kullan_adlari(self, d, kapsam):
        if d.takma:
            kapsam.bildir_yeni(d.takma)
            return
        _, program = self.kullanilan_program(d)
        self.adlari_topla(program, kapsam)

    def kullanilan_program(self, d):
        kaynak_adi = d.kaynak.deger if isinstance(d.kaynak, N.Sabit) else None
        if kaynak_adi is None and isinstance(d.kaynak, N.Metin):
            parcalar = [p for p in d.kaynak.parcalar if p[0] == "text"]
            kaynak_adi = "".join(p[1] for p in parcalar)
        if kaynak_adi in ("web", "tonweb"):
            raise TonSyntaxError(
                "Tarayici tarafinda 'use web' yoktur; web kutuphanesi sunucu icindir. "
                "Tarayicida DOM isleri (bul, tikla, yaz_ic ...) zaten hazirdir.",
                d.line, self.dosya)
        yol = self.dosya_bul(kaynak_adi or "")
        if yol is None:
            raise TonRuntimeError("'%s' bulunamadi" % kaynak_adi, d.line, self.dosya)
        if yol not in self.onbellek:
            self.onbellek[yol] = cozumle(dosya_oku(yol), yol)
        return yol, self.onbellek[yol]

    def dosya_bul(self, ad):
        temel = ad if os.path.isabs(ad) else os.path.join(self.kok, ad)
        adaylar = [temel] + ([temel + u for u in UZANTILAR]
                             if not os.path.splitext(ad)[1] else [])
        for a in adaylar:
            if os.path.isfile(a):
                return a
        return None

    def bildirimler(self, kapsam, girinti, haric=()):
        adlar = sorted(a for a in kapsam.adlar if a not in haric)
        if not adlar:
            return ""
        return "%slet %s;\n" % ("  " * girinti, ", ".join(ONEK + a for a in adlar))

    # ------------------------------------------------------------ deyimler
    def blok(self, deyimler, kapsam, girinti):
        return "".join(self.deyim(d, kapsam, girinti) for d in deyimler)

    def deyim(self, d, kapsam, girinti):
        bosluk = "  " * girinti
        t = d.tur
        if t == "IfadeDeyimi":
            return "%s%s;\n" % (bosluk, self.ifade(d.ifade, kapsam))
        if t == "Ata":
            return self.atama(d, kapsam, girinti)
        if t == "Eger":
            parcalar = []
            for i, (kosul, govde) in enumerate(d.dallar):
                anahtar = "if" if i == 0 else "} else if"
                parcalar.append("%s%s (T.dogru_mu(%s)) {\n%s"
                                % (bosluk if i == 0 else "", anahtar,
                                   self.ifade(kosul, kapsam),
                                   self.blok(govde, kapsam, girinti + 1)))
            metin = "".join(parcalar)
            if d.digeri is not None:
                metin += "%s} else {\n%s" % (bosluk, self.blok(d.digeri, kapsam, girinti + 1))
            return metin + bosluk + "}\n"
        if t == "Surece":
            return ("%swhile (T.dogru_mu(%s)) {\n%s%s}\n"
                    % (bosluk, self.ifade(d.kosul, kapsam),
                       self.blok(d.govde, kapsam, girinti + 1), bosluk))
        if t == "Tekrarla":
            sayac = self.yeni_ad("s")
            atama = ("%s%s = %s + 1;\n" % ("  " * (girinti + 1), ONEK + d.sayac, sayac)
                     if d.sayac else "")
            return ("%sfor (let %s = 0, _n = T.tekrar(%s); %s < _n; %s++) {\n%s%s%s}\n"
                    % (bosluk, sayac, self.ifade(d.sayi, kapsam), sayac, sayac,
                       atama, self.blok(d.govde, kapsam, girinti + 1), bosluk))
        if t == "Her":
            oge = self.yeni_ad("o")
            if d.ikinci:
                ic = ("%s%s = %s[0]; %s = %s[1];\n"
                      % ("  " * (girinti + 1), ONEK + d.ad, oge, ONEK + d.ikinci, oge))
            else:
                ic = "%s%s = %s;\n" % ("  " * (girinti + 1), ONEK + d.ad, oge)
            return ("%sfor (const %s of T.gezinti(%s)) {\n%s%s%s}\n"
                    % (bosluk, oge, self.ifade(d.kaynak, kapsam), ic,
                       self.blok(d.govde, kapsam, girinti + 1), bosluk))
        if t == "IsTanimi":
            return bosluk + self.is_tanimi(d, kapsam, girinti) + ";\n"
        if t == "Dondur":
            deger = self.ifade(d.deger, kapsam) if d.deger is not None else "null"
            return "%sreturn %s;\n" % (bosluk, deger)
        if t == "Durdur":
            return bosluk + "break;\n"
        if t == "Atla":
            return bosluk + "continue;\n"
        if t == "Dene":
            e = self.yeni_ad("e")
            yakala = "%s%s = T.hata_metni(%s);\n" % ("  " * (girinti + 1), ONEK + "hata", e)
            if d.hata_adi and d.hata_adi != "hata":
                yakala += "%s%s = %s;\n" % ("  " * (girinti + 1), ONEK + d.hata_adi,
                                            ONEK + "hata")
            return ("%stry {\n%s%s} catch (%s) {\n%s%s%s}\n"
                    % (bosluk, self.blok(d.govde, kapsam, girinti + 1), bosluk, e,
                       yakala, self.blok(d.yakala_govde, kapsam, girinti + 1), bosluk))
        if t == "Kullan":
            return self.kullan(d, kapsam, girinti)
        raise TonRuntimeError("Tarayici derleyicisi '%s' deyimini bilmiyor" % t,
                              d.line, self.dosya)

    def atama(self, d, kapsam, girinti):
        bosluk = "  " * girinti
        deger = self.ifade(d.deger, kapsam)
        hedef = d.hedef
        if isinstance(hedef, (N.Ad, N.Degisken)):
            ad = ONEK + hedef.ad
            if not kapsam.var_mi(hedef.ad):
                kapsam.bildir(hedef.ad)
            if d.islec != "=":
                deger = "T.%s(%s, %s)" % (IKILI_ISLER[d.islec[0]], ad, deger)
            satir = "%s%s = %s;\n" % (bosluk, ad, deger)
            if hedef.ad in AYAR_ADLARI:
                satir += "%sT.ayar(%s, %s);\n" % (bosluk, json.dumps(hedef.ad), ad)
            return satir
        if isinstance(hedef, N.Dizin):
            nesne = self.ifade(hedef.nesne, kapsam)
            anahtar = self.ifade(hedef.anahtar, kapsam)
            if d.islec != "=":
                deger = "T.%s(T.dizin(%s, %s), %s)" % (IKILI_ISLER[d.islec[0]],
                                                       nesne, anahtar, deger)
            return "%sT.ata_dizin(%s, %s, %s);\n" % (bosluk, nesne, anahtar, deger)
        if isinstance(hedef, N.Uye):
            nesne = self.ifade(hedef.nesne, kapsam)
            ad = json.dumps(hedef.ad)
            if d.islec != "=":
                deger = "T.%s(T.uye(%s, %s), %s)" % (IKILI_ISLER[d.islec[0]],
                                                     nesne, ad, deger)
            return "%sT.ata_uye(%s, %s, %s);\n" % (bosluk, nesne, ad, deger)
        raise TonSyntaxError("Buraya deger atanamaz", d.line, self.dosya)

    def is_tanimi(self, d, kapsam, girinti, isim_ver=True):
        ic = Kapsam(kapsam, "is")
        for ad, _ in d.parametreler:
            ic.bildir(ad)
        self.adlari_topla(d.govde, ic)
        parametreler = []
        denetim = []
        bosluk = "  " * (girinti + 1)
        for ad, varsayilan in d.parametreler:
            parametreler.append(ONEK + ad)
            if varsayilan is not None:
                denetim.append("%sif (%s === undefined) %s = %s;\n"
                               % (bosluk, ONEK + ad, ONEK + ad, self.ifade(varsayilan, ic)))
            else:
                denetim.append("%sif (%s === undefined) T.eksik(%s, %s);\n"
                               % (bosluk, ONEK + ad, json.dumps(d.ad or "is"),
                                  json.dumps(ad)))
        govde = (self.bildirimler(ic, girinti + 1, haric=[p[0] for p in d.parametreler])
                 + "".join(denetim)
                 + self.blok(d.govde, ic, girinti + 1))
        ad_metni = (ONEK + d.ad) if (d.ad and isim_ver) else ""
        metin = ("%s = T.is(async function (%s) {\n%s%s}, %s, %s)"
                 % (ad_metni, ", ".join(parametreler), govde, "  " * girinti,
                    json.dumps(d.ad or "isimsiz"),
                    json.dumps([p[0] for p in d.parametreler])))
        if not ad_metni:
            return metin[3:]  # " = " onekini at
        return metin

    def kullan(self, d, kapsam, girinti):
        bosluk = "  " * girinti
        yol, program = self.kullanilan_program(d)
        if not program or (yol in self.eklenenler and not d.takma):
            return ""
        self.eklenenler.add(yol)
        if d.takma:
            ic = Kapsam(kapsam, "modul")
            self.adlari_topla(program, ic)
            adlar = sorted(ic.adlar)
            govde = (self.bildirimler(ic, girinti + 1)
                     + self.blok(program, ic, girinti + 1)
                     + "%sreturn {%s};\n" % ("  " * (girinti + 1),
                                             ", ".join('%s: %s%s' % (a, ONEK, a)
                                                       for a in adlar)))
            if not kapsam.var_mi(d.takma):
                kapsam.bildir(d.takma)
            return ("%s%s = await (async function () {\n%s%s})();\n"
                    % (bosluk, ONEK + d.takma, govde, bosluk))
        self.adlari_topla(program, kapsam)
        return self.blok(program, kapsam, girinti)

    # ------------------------------------------------------------ ifadeler
    def ifade(self, e, kapsam):
        t = e.tur
        if t == "Sabit":
            return json.dumps(e.deger)
        if t == "Metin":
            return self.metin(e.parcalar, kapsam, e.line)
        if t == "Degisken":
            return self.ad_coz(e.ad, kapsam, e.line, degisken=True)
        if t == "Ad":
            return self.ad_coz(e.ad, kapsam, e.line, degisken=False)
        if t == "Liste":
            return "[%s]" % ", ".join(self.ifade(x, kapsam) for x in e.ogeler)
        if t == "Harita":
            ciftler = []
            for a, d in e.ciftler:
                ciftler.append("[%s, %s]" % (self.ifade(a, kapsam), self.ifade(d, kapsam)))
            return "T.harita([%s])" % ", ".join(ciftler)
        if t == "Dizin":
            return "T.dizin(%s, %s)" % (self.ifade(e.nesne, kapsam),
                                        self.ifade(e.anahtar, kapsam))
        if t == "Uye":
            return "T.uye(%s, %s)" % (self.ifade(e.nesne, kapsam), json.dumps(e.ad))
        if t == "Cagri":
            args = ", ".join(self.ifade(a, kapsam) for a in e.argumanlar)
            isimli = ", ".join("%s: %s" % (json.dumps(k), self.ifade(v, kapsam))
                               for k, v in e.isimli.items())
            return "(await T.cagir(%s, [%s]%s))" % (
                self.ifade(e.hedef, kapsam), args,
                (", {%s}" % isimli) if isimli else "")
        if t == "Ikili":
            if e.islec == "and":
                return "(T.dogru_mu(T._g = %s) ? %s : T._g)" % (
                    self.ifade(e.sol, kapsam), self.ifade(e.sag, kapsam))
            if e.islec == "or":
                return "(T.dogru_mu(T._g = %s) ? T._g : %s)" % (
                    self.ifade(e.sol, kapsam), self.ifade(e.sag, kapsam))
            return "T.%s(%s, %s)" % (IKILI_ISLER[e.islec],
                                     self.ifade(e.sol, kapsam), self.ifade(e.sag, kapsam))
        if t == "Tekli":
            if e.islec == "not":
                return "(!T.dogru_mu(%s))" % self.ifade(e.deger, kapsam)
            return "T.eksi(%s)" % self.ifade(e.deger, kapsam)
        if t == "IsTanimi":
            if e.ad and not kapsam.var_mi(e.ad):
                kapsam.bildir(e.ad)
            return "(%s)" % self.is_tanimi(e, kapsam, 1, isim_ver=bool(e.ad))
        raise TonRuntimeError("Tarayici derleyicisi '%s' ifadesini bilmiyor" % t,
                              e.line, self.dosya)

    def ad_coz(self, ad, kapsam, satir, degisken):
        if kapsam.var_mi(ad):
            # Ayni ad hem degisken hem hazir is olabilir (`ai = "groq"` sonra
            # `ai("...")`). Cekirdekteki kural: deger cagrilabilir degilse
            # hazir ise dusulur.
            if ad in self.hazir and not degisken:
                return "T.golge(%s, %s)" % (ONEK + ad, json.dumps(ad))
            return ONEK + ad
        if ad in self.hazir:
            return "T.h(%s)" % json.dumps(ad)
        if ad in TARAYICIDA_YOK:
            raise TonSyntaxError(
                "'%s' tarayicida yoktur (%s). Sunucudan veri almak icin "
                "get()/post() kullan." % (ad, TARAYICIDA_YOK[ad]), satir, self.dosya)
        if degisken:
            raise TonSyntaxError("'%s' adinda bir degisken yok" % ad, satir, self.dosya)
        raise TonSyntaxError("'%s' adinda bir is yok" % ad, satir, self.dosya)

    def metin(self, parcalar, kapsam, satir):
        parcalar_js = []
        for p in parcalar:
            if p[0] == "text":
                parcalar_js.append(json.dumps(p[1]))
            elif p[0] == "expr":
                dugum = cozumle_ifade(p[1], self.dosya)
                parcalar_js.append("T.metin(%s)" % self.ifade(dugum, kapsam))
            else:
                dugum = N.Degisken(p[1], [], line=satir)
                for tip, anahtar in p[2]:
                    if tip == "attr":
                        dugum = N.Uye(dugum, anahtar, line=satir)
                    elif tip == "index":
                        dugum = N.Dizin(dugum, N.Sabit(anahtar, line=satir), line=satir)
                    else:
                        dugum = N.Dizin(dugum, N.Degisken(anahtar, [], line=satir),
                                        line=satir)
                parcalar_js.append("T.metin(%s)" % self.ifade(dugum, kapsam))
        if not parcalar_js:
            return '""'
        if len(parcalar_js) == 1 and parcalar[0][0] == "text":
            return parcalar_js[0]
        return "(%s)" % " + ".join(parcalar_js)

    def yeni_ad(self, onek):
        self.sayac += 1
        return "_%s%d" % (onek, self.sayac)


ISLER_DOSYASI = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
                             "tonweb", "tarayici", "isler.json")


def _hazir_isler():
    """Tarayici calisma zamanindaki hazir islerin adlari.

    Liste ton.js'ten uretilir (tonweb/tarayici/isler.json), boylece derleyici ile
    calisma zamani birbirinden kopamaz.
    """
    try:
        with open(ISLER_DOSYASI, encoding="utf-8") as f:
            return set(json.load(f))
    except (OSError, ValueError):
        from .lib import gomululeri_yukle
        adlar = set(gomululeri_yukle().keys()) - set(TARAYICIDA_YOK)
        adlar.update(TARAYICI_ISLERI)
        return adlar


# Sadece tarayicida bulunan isler (DOM, depolama, sayfa)
TARAYICI_ISLERI = {
    "oge", "el", "ogeler", "els", "olustur", "create",
    "yaz_ic", "set_html", "oku_ic", "get_html", "yaz_metin", "set_text",
    "oku_metin", "get_text", "temizle_ic", "clear_html",
    "deger", "value", "ozellik", "attr", "stil", "style",
    "ekle_sinif", "add_class", "sil_sinif", "remove_class",
    "degistir_sinif", "toggle_class", "ekle_oge", "append_el", "sil_oge", "remove_el",
    "tikla", "on_click", "olay", "on", "gonderim", "on_submit", "tus", "on_key",
    "gorunur", "visible", "odak", "focus",
    "uyari", "alert", "onay", "confirm", "sor_kutu", "prompt",
    "git", "go", "adres", "location", "yenile", "reload",
    "sakla", "store", "saklanan", "stored", "sakli_sil", "store_remove",
    "sayfa_hazir", "on_ready", "konsol", "console",
    "form_verisi", "form_data", "sayfa_basligi", "page_title",
}


def derle(kaynak, dosya=None, ad=None):
    """TON kaynagini JavaScript'e cevirir."""
    return Derleyici(dosya).derle(kaynak, ad)


def dosya_derle(yol):
    return Derleyici(yol).derle(dosya_oku(yol), os.path.basename(yol))
