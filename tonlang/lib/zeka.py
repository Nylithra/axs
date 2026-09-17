"""Yapay zeka isleri: ai()

    ai_setup(key: "...")            # bir kez ayarla (ya da TON_AI_KEY ortam degiskeni)
    cevap = ai("Merhaba de")
"""

import json as _json
import os

from ..errors import TonRuntimeError
from ..values import metin as _metin, pythonlastir
from . import gomulu
from .ag import _istek

AYAR = {
    "adres": os.environ.get("TON_AI_URL", "https://api.anthropic.com/v1/messages"),
    "anahtar": os.environ.get("TON_AI_KEY") or os.environ.get("ANTHROPIC_API_KEY") or "",
    "model": os.environ.get("TON_AI_MODEL", "claude-opus-5"),
    "sinir": int(os.environ.get("TON_AI_MAX", "1024")),
    "kisilik": "",
}


@gomulu("ai_setup", "zeka_ayarla")
def zeka_ayarla(key=None, model=None, url=None, kisilik=None, sinir=None):
    if key is not None:
        AYAR["anahtar"] = _metin(key)
    if model is not None:
        AYAR["model"] = _metin(model)
    if url is not None:
        AYAR["adres"] = _metin(url)
    if kisilik is not None:
        AYAR["kisilik"] = _metin(kisilik)
    if sinir is not None:
        AYAR["sinir"] = int(sinir)
    return True


def _anthropic_mi(adres):
    return "anthropic.com" in adres or adres.endswith("/v1/messages")


def _mesajlar(soru):
    if isinstance(soru, list):
        cikti = []
        for m in soru:
            if isinstance(m, dict):
                cikti.append({"role": m.get("rol") or m.get("role") or "user",
                              "content": _metin(m.get("metin") or m.get("content") or "")})
            else:
                cikti.append({"role": "user", "content": _metin(m)})
        return cikti
    return [{"role": "user", "content": _metin(soru)}]


@gomulu("ai", "zeka", "sorbana")
def zeka(soru, model=None, kisilik=None, sinir=None):
    if not AYAR["anahtar"]:
        raise TonRuntimeError(
            "Yapay zeka anahtari yok. `ai_setup(key: \"...\")` yaz ya da "
            "TON_AI_KEY ortam degiskenini ayarla.")
    model = _metin(model) if model else AYAR["model"]
    kisilik = _metin(kisilik) if kisilik else AYAR["kisilik"]
    sinir = int(sinir) if sinir else AYAR["sinir"]
    mesajlar = _mesajlar(soru)

    if _anthropic_mi(AYAR["adres"]):
        govde = {"model": model, "max_tokens": sinir, "messages": mesajlar}
        if kisilik:
            govde["system"] = kisilik
        basliklar = {"x-api-key": AYAR["anahtar"], "anthropic-version": "2023-06-01",
                     "content-type": "application/json"}
    else:
        if kisilik:
            mesajlar = [{"role": "system", "content": kisilik}] + mesajlar
        govde = {"model": model, "max_tokens": sinir, "messages": mesajlar}
        basliklar = {"Authorization": "Bearer " + AYAR["anahtar"],
                     "content-type": "application/json"}

    cevap = _istek("POST", AYAR["adres"], govde, basliklar, zaman_asimi=120)
    veri = cevap["veri"]
    if not cevap["basarili"]:
        raise TonRuntimeError("Yapay zeka hatasi (%s): %s" % (cevap["durum"], _metin(veri)))
    return _cevabi_ayikla(veri)


def _cevabi_ayikla(veri):
    if isinstance(veri, str):
        return veri
    if isinstance(veri, dict):
        icerik = veri.get("content")
        if isinstance(icerik, list):
            return "".join(p.get("text", "") for p in icerik if isinstance(p, dict))
        secenekler = veri.get("choices")
        if isinstance(secenekler, list) and secenekler:
            ilk = secenekler[0]
            if isinstance(ilk, dict):
                mesaj = ilk.get("message") or {}
                return _metin(mesaj.get("content", ilk.get("text", "")))
        if "text" in veri:
            return _metin(veri["text"])
    return _metin(veri)


@gomulu("ai_json", "zeka_veri")
def zeka_veri(soru, model=None):
    from .cekirdek import json_oku
    ham = zeka(_metin(soru) + "\n\nSadece gecerli JSON dondur, baska hicbir sey yazma.",
               model=model)
    ham = ham.strip()
    if ham.startswith("```"):
        ham = ham.split("\n", 1)[-1]
        if ham.endswith("```"):
            ham = ham[:-3]
        if ham.startswith("json"):
            ham = ham[4:]
    return json_oku(ham.strip())


@gomulu("ai_chat", "zeka_sohbet")
def zeka_sohbet(gecmis, soru=None, model=None):
    mesajlar = list(gecmis) if isinstance(gecmis, list) else []
    if soru is not None:
        mesajlar.append({"rol": "user", "metin": _metin(soru)})
    cevap = zeka(mesajlar, model=model)
    mesajlar.append({"rol": "assistant", "metin": cevap})
    return {"cevap": cevap, "gecmis": mesajlar}


@gomulu("ai_ready", "zeka_hazir")
def zeka_hazir():
    return bool(AYAR["anahtar"])
