"""JavaScript sozcuk cozumleyicisi."""

import re

from ..errors import TonSyntaxError

ANAHTAR_KELIMELER = {
    "var", "let", "const", "function", "return", "if", "else", "for", "while",
    "do", "switch", "case", "default", "break", "continue", "new", "delete",
    "typeof", "instanceof", "in", "of", "this", "null", "true", "false",
    "undefined", "class", "extends", "super", "try", "catch", "finally",
    "throw", "async", "await", "yield", "import", "export", "from", "static",
    "void", "get", "set",
}

ISARETLER = [
    ">>>=", "...", "===", "!==", "**=", "<<=", ">>=", ">>>", "&&=", "||=", "??=",
    "=>", "==", "!=", "<=", ">=", "&&", "||", "??", "?.", "++", "--",
    "+=", "-=", "*=", "/=", "%=", "&=", "|=", "^=", "**", "<<", ">>",
    "{", "}", "(", ")", "[", "]", ";", ",", "<", ">", "+", "-", "*", "/", "%",
    "&", "|", "^", "!", "~", "?", ":", "=", ".",
]

AD_RE = re.compile(r"[A-Za-z_$][A-Za-z0-9_$]*")
SAYI_RE = re.compile(
    r"0[xX][0-9a-fA-F_]+|0[bB][01_]+|0[oO][0-7_]+"
    r"|(?:\d[\d_]*)?\.\d[\d_]*(?:[eE][+-]?\d+)?"
    r"|\d[\d_]*\.?(?:[eE][+-]?\d+)?"
)

# Bu tokenlardan SONRA gelen `/` bolme isaretidir; digerlerinde regex baslar.
BOLME_ONCESI = {"NAME", "NUM", "STR", "TEMPLATE", "REGEX"}
BOLME_ISARETLERI = {")", "]", "}", "++", "--"}
IFADE_BITIREN_KELIMELER = {"this", "super", "null", "true", "false", "undefined"}

KACISLAR = {"n": "\n", "t": "\t", "r": "\r", "b": "\b", "f": "\f", "v": "\v",
            "0": "\0", "\\": "\\", "'": "'", '"': '"', "`": "`", "\n": ""}


class Token:
    __slots__ = ("kind", "value", "line", "satir_basi")

    def __init__(self, kind, value, line, satir_basi=False):
        self.kind = kind
        self.value = value
        self.line = line
        self.satir_basi = satir_basi   # oncesinde satir sonu var mi (ASI icin)

    def __repr__(self):
        return "Token(%s, %r, %d)" % (self.kind, self.value, self.line)


def _kacis_coz(ham, satir):
    cikti = []
    i = 0
    n = len(ham)
    while i < n:
        c = ham[i]
        if c == "\\" and i + 1 < n:
            k = ham[i + 1]
            if k == "u":
                if i + 2 < n and ham[i + 2] == "{":
                    kapanis = ham.find("}", i + 3)
                    cikti.append(chr(int(ham[i + 3:kapanis], 16)))
                    i = kapanis + 1
                    continue
                cikti.append(chr(int(ham[i + 2:i + 6], 16)))
                i += 6
                continue
            if k == "x":
                cikti.append(chr(int(ham[i + 2:i + 4], 16)))
                i += 4
                continue
            cikti.append(KACISLAR.get(k, k))
            i += 2
            continue
        cikti.append(c)
        i += 1
    return "".join(cikti)


def coz(kaynak, dosya=None):
    """JavaScript kaynagini token listesine cevirir."""
    tokenlar = []
    i = 0
    n = len(kaynak)
    satir = 1
    yeni_satir = True

    def son_anlamli():
        return tokenlar[-1] if tokenlar else None

    def regex_olabilir():
        t = son_anlamli()
        if t is None:
            return True
        if t.kind in BOLME_ONCESI:
            if t.kind == "NAME" and t.value in ANAHTAR_KELIMELER \
                    and t.value not in IFADE_BITIREN_KELIMELER:
                return True
            return False
        if t.kind == "PUNCT" and t.value in BOLME_ISARETLERI:
            return False
        return True

    def ekle(kind, value):
        tokenlar.append(Token(kind, value, satir, yeni_satir))

    while i < n:
        c = kaynak[i]

        if c == "\n":
            satir += 1
            yeni_satir = True
            i += 1
            continue
        if c in " \t\r\f\v ﻿":
            i += 1
            continue

        # yorumlar
        if kaynak.startswith("//", i):
            while i < n and kaynak[i] != "\n":
                i += 1
            continue
        if kaynak.startswith("/*", i):
            kapanis = kaynak.find("*/", i + 2)
            if kapanis == -1:
                raise TonSyntaxError("Yorum kapatilmamis (*/ yok)", satir, dosya)
            satir += kaynak.count("\n", i, kapanis)
            if kaynak.count("\n", i, kapanis):
                yeni_satir = True
            i = kapanis + 2
            continue

        # metinler
        if c in "\"'":
            j = i + 1
            ham = []
            while j < n and kaynak[j] != c:
                if kaynak[j] == "\\":
                    ham.append(kaynak[j:j + 2])
                    j += 2
                    continue
                if kaynak[j] == "\n":
                    raise TonSyntaxError("Metin tirnagi kapatilmamis", satir, dosya)
                ham.append(kaynak[j])
                j += 1
            if j >= n:
                raise TonSyntaxError("Metin tirnagi kapatilmamis", satir, dosya)
            ekle("STR", _kacis_coz("".join(ham), satir))
            yeni_satir = False
            i = j + 1
            continue

        # sablon metin: `a ${b} c`
        if c == "`":
            parcalar = []
            tampon = []
            j = i + 1
            while j < n and kaynak[j] != "`":
                if kaynak[j] == "\\":
                    tampon.append(kaynak[j:j + 2])
                    j += 2
                    continue
                if kaynak.startswith("${", j):
                    parcalar.append(("text", _kacis_coz("".join(tampon), satir)))
                    tampon = []
                    derinlik = 1
                    k = j + 2
                    bas = k
                    while k < n and derinlik:
                        if kaynak[k] == "{":
                            derinlik += 1
                        elif kaynak[k] == "}":
                            derinlik -= 1
                            if derinlik == 0:
                                break
                        elif kaynak[k] in "\"'`":
                            tirnak = kaynak[k]
                            k += 1
                            while k < n and kaynak[k] != tirnak:
                                k += 2 if kaynak[k] == "\\" else 1
                        k += 1
                    parcalar.append(("expr", kaynak[bas:k]))
                    j = k + 1
                    continue
                if kaynak[j] == "\n":
                    satir += 1
                tampon.append(kaynak[j])
                j += 1
            if j >= n:
                raise TonSyntaxError("Sablon metin kapatilmamis (`)", satir, dosya)
            parcalar.append(("text", _kacis_coz("".join(tampon), satir)))
            ekle("TEMPLATE", parcalar)
            yeni_satir = False
            i = j + 1
            continue

        # duzenli ifade
        if c == "/" and regex_olabilir():
            j = i + 1
            kose = False
            tamam = False
            while j < n:
                if kaynak[j] == "\\":
                    j += 2
                    continue
                if kaynak[j] == "[":
                    kose = True
                elif kaynak[j] == "]":
                    kose = False
                elif kaynak[j] == "/" and not kose:
                    tamam = True
                    break
                elif kaynak[j] == "\n":
                    break
                j += 1
            if tamam:
                desen = kaynak[i + 1:j]
                j += 1
                bayrak_bas = j
                while j < n and kaynak[j].isalpha():
                    j += 1
                ekle("REGEX", (desen, kaynak[bayrak_bas:j]))
                yeni_satir = False
                i = j
                continue

        # sayilar
        m = SAYI_RE.match(kaynak, i)
        if m and (c.isdigit() or (c == "." and i + 1 < n and kaynak[i + 1].isdigit())):
            ham = m.group(0).replace("_", "")
            if ham[:2].lower() in ("0x", "0b", "0o"):
                deger = int(ham, 0)
            elif "." in ham or "e" in ham.lower():
                deger = float(ham)
            else:
                deger = int(ham)
            ekle("NUM", deger)
            yeni_satir = False
            i = m.end()
            continue

        # adlar
        m = AD_RE.match(kaynak, i)
        if m:
            ekle("NAME", m.group(0))
            yeni_satir = False
            i = m.end()
            continue

        # isaretler
        for isaret in ISARETLER:
            if kaynak.startswith(isaret, i):
                ekle("PUNCT", isaret)
                yeni_satir = False
                i += len(isaret)
                break
        else:
            raise TonSyntaxError("Anlasilmayan karakter: %r" % c, satir, dosya)

    tokenlar.append(Token("EOF", None, satir, True))
    return tokenlar
