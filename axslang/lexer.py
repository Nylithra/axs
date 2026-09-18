"""Axs sozcuk cozumleyicisi (lexer).

Axs'in tek altin kurali: degiskenler her zaman %ad% seklinde okunur.
Bu yuzden cikplak bir ad her zaman bir fonksiyon/anahtar kelimedir,
%ad% ise her zaman bir degiskendir. Belirsizlik yoktur.
"""

import re

from .errors import AxsSyntaxError

IDENT = r"[^\W\d]\w*"

# Anahtar kelimeler ve Turkce esanlamlilari -> ingilizce cekirdek ad
ALIASES = {
    "if": "if", "eger": "if", "eğer": "if",
    "elif": "elif", "yoksa": "elif", "veyaeger": "elif",
    "else": "else", "degilse": "else", "değilse": "else",
    "end": "end", "son": "end", "bitir": "end",
    "while": "while", "surece": "while", "sürece": "while",
    "repeat": "repeat", "tekrar": "repeat",
    "for": "for", "her": "for",
    "in": "in", "icinde": "in", "içinde": "in",
    "func": "func", "is": "func", "iş": "func", "fonksiyon": "func",
    "return": "return", "dondur": "return", "döndür": "return",
    "stop": "stop", "dur": "stop",
    "skip": "skip", "atla": "skip",
    "try": "try", "dene": "try",
    "catch": "catch", "yakala": "catch",
    "use": "use", "kullan": "use",
    "and": "and", "ve": "and",
    "or": "or", "veya": "or",
    "not": "not", "degil": "not", "değil": "not",
    "mod": "mod", "kalan": "mod",
    "true": "true", "dogru": "true", "doğru": "true", "evet": "true",
    "false": "false", "yanlis": "false", "yanlış": "false", "hayir": "false", "hayır": "false",
    "null": "null", "bos": "null", "boş": "null", "yok": "null",
}

# `ad: metin` sablon cagrisina donusemeyecek kelimeler
BLOK_KELIMELERI = set(ALIASES)

TEMPLATE_RE = re.compile(r"[ \t]*(" + IDENT + r")[ \t]*:(?!=)(.*)")
VAR_RE = re.compile(
    r"%(" + IDENT + r")((?:\." + IDENT + r"|\[[^\]\n%]*\])*)%"
)
# Sablon icinde `ad;`  ·  `kisi.ad;`  ·  `liste[0];`
SABLON_VAR_RE = re.compile(
    r"(" + IDENT + r")((?:\." + IDENT + r"|\[[^\]\n;]*\])*);"
)
# `ad;` yazimini baslatmayacak onceki karakterler (adres vb. yanlis eslesmesin)
BITISIK = set("._/:%\\")
ACC_RE = re.compile(r"\.(" + IDENT + r")|\[([^\]]*)\]")
NUM_RE = re.compile(r"\d[\d_]*(?:\.\d[\d_]*)?")
IDENT_RE = re.compile(IDENT)
URL_RE = re.compile(r"[A-Za-z][A-Za-z0-9+.\-]*://[^\s,()\[\]{}\"']+")

OPERATORS = [
    "==", "!=", "<=", ">=", "+=", "-=", "*=", "/=", "->",
    "=", "<", ">", "+", "-", "*", "/", "^",
    "(", ")", "[", "]", "{", "}", ",", ".", ":",
]

ESCAPES = {"n": "\n", "t": "\t", "r": "\r", "\\": "\\",
           '"': '"', "'": "'", "%": "%", ";": ";", "0": "\0"}


class Token:
    __slots__ = ("kind", "value", "line")

    def __init__(self, kind, value, line):
        self.kind = kind
        self.value = value
        self.line = line

    def __repr__(self):
        return "Token(%s, %r, %d)" % (self.kind, self.value, self.line)


def anahtar(ad):
    """Verilen adin cekirdek anahtar kelime karsiligi (yoksa None)."""
    return ALIASES.get(ad)


def _erisimler(ham, satir):
    """`.ad` ve `[...]` eklerini cozer."""
    cikti = []
    yer = 0
    while yer < len(ham):
        m = ACC_RE.match(ham, yer)
        if not m:
            raise AxsSyntaxError("Degisken yolu anlasilamadi: %r" % ham, satir)
        if m.group(1) is not None:
            cikti.append(("attr", m.group(1)))
        else:
            ic = m.group(2).strip()
            if re.fullmatch(r"-?\d+", ic):
                cikti.append(("index", int(ic)))
            elif len(ic) >= 2 and ic[0] == ic[-1] and ic[0] in "\"'":
                cikti.append(("index", ic[1:-1]))
            elif re.fullmatch(IDENT, ic or ""):
                cikti.append(("indexvar", ic))
            else:
                raise AxsSyntaxError(
                    "Kose parantez icinde sadece sayi, \"metin\" veya degisken adi olur: [%s]" % ic,
                    satir,
                )
        yer = m.end()
    return cikti


def metin_parcala(ham, satir, yorumla=True):
    """Ham metni duz parca / %degisken% parcalarina ayirir."""
    parcalar = []
    tampon = []
    i = 0
    n = len(ham)
    while i < n:
        c = ham[i]
        if c == "\\" and i + 1 < n:
            tampon.append(ESCAPES.get(ham[i + 1], "\\" + ham[i + 1]))
            i += 2
            continue
        # `ad;` ve `(ifade);` yazimi (sablonlarda)
        if yorumla and (c.isalpha() or c == "_" or c == "("):
            onceki = ham[i - 1] if i else ""
            if not (onceki.isalnum() or onceki in BITISIK):
                if c == "(":
                    derinlik = 0
                    j = i
                    while j < n:
                        if ham[j] == "(":
                            derinlik += 1
                        elif ham[j] == ")":
                            derinlik -= 1
                            if derinlik == 0:
                                break
                        j += 1
                    if j < n and ham.startswith(");", j):
                        if tampon:
                            parcalar.append(("text", "".join(tampon)))
                            tampon = []
                        parcalar.append(("expr", ham[i + 1:j]))
                        i = j + 2
                        continue
                else:
                    m = SABLON_VAR_RE.match(ham, i)
                    if m:
                        if tampon:
                            parcalar.append(("text", "".join(tampon)))
                            tampon = []
                        parcalar.append(("var", m.group(1),
                                         _erisimler(m.group(2), satir)))
                        i = m.end()
                        continue

        if c == "%" and yorumla:
            if ham.startswith("%%", i):
                tampon.append("%")
                i += 2
                continue
            if ham.startswith("%(", i):
                derinlik = 0
                j = i + 1
                while j < n:
                    if ham[j] == "(":
                        derinlik += 1
                    elif ham[j] == ")":
                        derinlik -= 1
                        if derinlik == 0 and ham.startswith(")%", j):
                            break
                    j += 1
                if j < n:
                    if tampon:
                        parcalar.append(("text", "".join(tampon)))
                        tampon = []
                    parcalar.append(("expr", ham[i + 2:j]))
                    i = j + 2
                    continue
            m = VAR_RE.match(ham, i)
            if m:
                if tampon:
                    parcalar.append(("text", "".join(tampon)))
                    tampon = []
                parcalar.append(("var", m.group(1), _erisimler(m.group(2), satir)))
                i = m.end()
                continue
        tampon.append(c)
        i += 1
    if tampon or not parcalar:
        parcalar.append(("text", "".join(tampon)))
    return parcalar


def coz(kaynak, dosya=None):
    """Kaynak metni Token listesine cevirir."""
    tokenlar = []
    i = 0
    n = len(kaynak)
    satir = 1
    derinlik = 0
    satir_basi = True

    def ekle(kind, value):
        tokenlar.append(Token(kind, value, satir))

    while i < n:
        c = kaynak[i]

        # --- satir basi: `ad: metin` sablon cagrisi mi? ---
        if satir_basi and derinlik == 0:
            m = TEMPLATE_RE.match(kaynak, i)
            if m and anahtar(m.group(1)) is None:
                ekle("NAME", m.group(1))
                ekle("OP", ":")
                govde = m.group(2)
                yorum = govde.find("#")
                # `#` bir metnin parcasi olabilir; sadece bosluktan sonra gelirse yorumdur
                if yorum > 0 and govde[yorum - 1] in " \t":
                    govde = govde[:yorum]
                elif yorum == 0:
                    govde = ""
                ekle("TEMPLATE", metin_parcala(govde.strip(), satir))
                i = m.end()
                continue
            satir_basi = False

        if c in " \t\r":
            i += 1
            continue

        if c == "#":
            while i < n and kaynak[i] != "\n":
                i += 1
            continue

        if c == "\\" and i + 1 < n and kaynak[i + 1] == "\n":
            i += 2
            satir += 1
            continue

        if c == "\n":
            i += 1
            satir += 1
            if derinlik == 0:
                if tokenlar and tokenlar[-1].kind != "NL":
                    tokenlar.append(Token("NL", None, satir - 1))
                satir_basi = True
            continue

        if c == ";":
            i += 1
            if tokenlar and tokenlar[-1].kind != "NL":
                ekle("NL", None)
            satir_basi = True
            continue

        # --- metin ---
        if c == '"' or c == "'":
            # uc tirnak: cok satirli metin
            if kaynak.startswith(c * 3, i):
                kapanis = kaynak.find(c * 3, i + 3)
                if kapanis == -1:
                    raise AxsSyntaxError("Uc tirnak kapatilmamis", satir)
                ham = kaynak[i + 3:kapanis]
                ekle("STR", metin_parcala(ham, satir, c == '"'))
                satir += ham.count("\n")
                i = kapanis + 3
                continue
            yorumla = c == '"'
            j = i + 1
            ham = []
            while j < n and kaynak[j] != c:
                if kaynak[j] == "\\" and j + 1 < n:
                    ham.append(kaynak[j:j + 2])
                    j += 2
                    continue
                if kaynak[j] == "\n":
                    raise AxsSyntaxError("Metin tirnagi kapatilmamis", satir)
                ham.append(kaynak[j])
                j += 1
            if j >= n:
                raise AxsSyntaxError("Metin tirnagi kapatilmamis", satir)
            ekle("STR", metin_parcala("".join(ham), satir, yorumla))
            i = j + 1
            continue

        # --- adres (tirnaksiz url) ---
        m = URL_RE.match(kaynak, i)
        if m:
            ekle("STR", [("text", m.group(0))])
            i = m.end()
            continue

        # --- degisken ---
        if c == "%":
            m = VAR_RE.match(kaynak, i)
            if not m:
                raise AxsSyntaxError(
                    "Degiskenler %ad% seklinde yazilir. '%' tek basina kullanilamaz "
                    "(kalan icin 'mod' yaz).",
                    satir,
                )
            ekle("VAR", (m.group(1), _erisimler(m.group(2), satir)))
            i = m.end()
            continue

        # --- sayi ---
        m = NUM_RE.match(kaynak, i)
        if m:
            ham = m.group(0).replace("_", "")
            ekle("NUM", float(ham) if "." in ham else int(ham))
            i = m.end()
            continue

        # --- ad / anahtar kelime ---
        m = IDENT_RE.match(kaynak, i)
        if m:
            ekle("NAME", m.group(0))
            i = m.end()
            continue

        # --- islec ---
        for op in OPERATORS:
            if kaynak.startswith(op, i):
                if op in "([{":
                    derinlik += 1
                elif op in ")]}":
                    derinlik = max(0, derinlik - 1)
                ekle("OP", op)
                i += len(op)
                break
        else:
            raise AxsSyntaxError("Anlasilmayan karakter: %r" % c, satir)

    if tokenlar and tokenlar[-1].kind != "NL":
        tokenlar.append(Token("NL", None, satir))
    tokenlar.append(Token("EOF", None, satir))
    return tokenlar
