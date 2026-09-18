# -*- coding: utf-8 -*-
"""Eski `%ad%` yazimini yeni Axs yazimina cevirir.

  sablon / metin icinde :  %ad% -> ad;      %(ifade)% -> (ifade);
  ifade icinde          :  %ad% -> ad

Lexer'in kendi kurallarini kullanir:
  * `ad: ...` sablon cagrisi yalnizca parantez derinligi 0 iken satir basinda
    gecerlidir (cok satirli sozluk/dizi icindeki `Authorization:` gibi
    satirlar sablon degildir).
  * `ad;` yazimi yalnizca onceki karakter alfanumerik ya da BITISIK degilken
    okunur; guvenli olmayan yerlerde `%ad%` oldugu gibi birakilir.
Tek tirnakli ham metinlere hic dokunulmaz.
"""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from axslang.lexer import BITISIK, TEMPLATE_RE, VAR_RE, anahtar  # noqa: E402

ACIK = "([{"
KAPALI = ")]}"


def _son(cikti):
    for parca in reversed(cikti):
        if parca:
            return parca[-1]
    return ""


def metin_cevir(ham):
    """Sablon govdesi / cift tirnakli metin icindeki degiskenleri cevirir."""
    cikti = []
    i = 0
    n = len(ham)
    while i < n:
        if ham[i] == "\\" and i + 1 < n:
            cikti.append(ham[i:i + 2])
            i += 2
            continue
        if ham.startswith("%%", i):
            cikti.append("%%")
            i += 2
            continue
        if ham.startswith("%(", i):
            derinlik = 0
            j = i + 1
            son = -1
            while j < n:
                if ham[j] == "(":
                    derinlik += 1
                elif ham[j] == ")":
                    derinlik -= 1
                    if derinlik == 0:
                        son = j
                        break
                j += 1
            if son != -1 and ham.startswith(")%", son):
                ic = ham[i + 2:son]
                onceki = _son(cikti)
                if not (onceki.isalnum() or onceki in BITISIK):
                    cikti.append("(" + ifade_cevir(ic) + ");")
                else:
                    cikti.append("%(" + ifade_cevir(ic) + ")%")
                i = son + 2
                continue
        if ham[i] == "(" and not (_son(cikti).isalnum() or _son(cikti) in BITISIK):
            # zaten yeni yazim: `(ifade);` -- icini de cevir
            derinlik = 0
            j = i
            son = -1
            while j < n:
                if ham[j] == "(":
                    derinlik += 1
                elif ham[j] == ")":
                    derinlik -= 1
                    if derinlik == 0:
                        son = j
                        break
                j += 1
            if son != -1 and ham.startswith(");", son):
                cikti.append("(" + ifade_cevir(ham[i + 1:son]) + ");")
                i = son + 2
                continue
        m = VAR_RE.match(ham, i)
        if m:
            onceki = _son(cikti)
            erisim = m.group(2)
            guvenli = (not (onceki.isalnum() or onceki in BITISIK)
                       and ";" not in erisim
                       and anahtar(m.group(1)) is None)
            if guvenli:
                cikti.append(m.group(1) + erisim + ";")
            else:
                cikti.append(m.group(0))
            i = m.end()
            continue
        cikti.append(ham[i])
        i += 1
    return "".join(cikti)


def ifade_cevir(ham):
    """Kod (ifade) parcasinda `%ad%` -> `ad`.

    Adi bir anahtar kelimeyle ayni olan degiskenler (`son`, `dur`, ...) ciplak
    yazilamaz; onlar `%ad%` olarak kalir.
    """
    def _degis(m):
        if anahtar(m.group(1)) is not None:
            return m.group(0)
        return m.group(1) + m.group(2)
    return VAR_RE.sub(_degis, ham)


def _sablon_govdesi(govde):
    """Sablon govdesini, sondaki yorumu ayirarak cevirir (lexer ile ayni kural)."""
    yorum = govde.find("#")
    if yorum == 0:
        return ifade_cevir(govde)
    if yorum > 0 and govde[yorum - 1] in " \t":
        return metin_cevir(govde[:yorum]) + ifade_cevir(govde[yorum:])
    return metin_cevir(govde)


def kod_cevir(satir, derinlik, ucluk):
    """Kod satirini cevirir; yeni (metin, derinlik, ucluk) dondurur."""
    cikti = []
    i = 0
    n = len(satir)
    while i < n:
        c = satir[i]
        if ucluk:
            kapanis = satir.find(ucluk * 3, i)
            if kapanis == -1:
                govde = satir[i:]
                cikti.append(metin_cevir(govde) if ucluk == '"' else govde)
                return "".join(cikti), derinlik, ucluk
            govde = satir[i:kapanis]
            cikti.append((metin_cevir(govde) if ucluk == '"' else govde)
                         + ucluk * 3)
            i = kapanis + 3
            ucluk = None
            continue
        if c == "#":
            # yorumlar cogunlukla ifade ornegi icerir: %ad% -> ad
            cikti.append(ifade_cevir(satir[i:]))
            break
        if c in "\"'":
            if satir.startswith(c * 3, i):
                cikti.append(c * 3)
                i += 3
                ucluk = c
                continue
            j = i + 1
            ham = []
            while j < n and satir[j] != c:
                if satir[j] == "\\" and j + 1 < n:
                    ham.append(satir[j:j + 2])
                    j += 2
                    continue
                ham.append(satir[j])
                j += 1
            govde = "".join(ham)
            kapali = j < n
            cikti.append(c + (metin_cevir(govde) if c == '"' else govde)
                         + (c if kapali else ""))
            i = j + 1
            continue
        j = i
        while j < n and satir[j] not in "\"'#":
            j += 1
        parca = satir[i:j]
        for k in parca:
            if k in ACIK:
                derinlik += 1
            elif k in KAPALI:
                derinlik = max(0, derinlik - 1)
        cikti.append(ifade_cevir(parca))
        i = j
    return "".join(cikti), derinlik, ucluk


def satir_cevir(satir, derinlik, ucluk, devam=False):
    if ucluk is None and derinlik == 0 and not devam:
        m = TEMPLATE_RE.match(satir)
        if m and anahtar(m.group(1)) is None:
            onek = satir[:m.start(2)]
            return onek + _sablon_govdesi(m.group(2)), derinlik, ucluk
    return kod_cevir(satir, derinlik, ucluk)


def dosya_cevir(yol):
    with open(yol, encoding="utf-8") as f:
        metin = f.read()
    derinlik = 0
    ucluk = None
    devam = False
    cikti = []
    for satir in metin.split("\n"):
        yeni, derinlik, ucluk = satir_cevir(satir, derinlik, ucluk, devam)
        cikti.append(yeni)
        devam = ucluk is None and yeni.rstrip(" \t\r").endswith("\\")
    yeni_metin = "\n".join(cikti)
    if yeni_metin != metin:
        with open(yol, "w", encoding="utf-8") as f:
            f.write(yeni_metin)
        return True
    return False


if __name__ == "__main__":
    for yol in sys.argv[1:]:
        if dosya_cevir(yol):
            print("cevrildi:", yol)
