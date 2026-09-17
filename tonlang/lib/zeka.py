"""Yapay zeka isleri: ai()

Saglayiciyi tek satirda secersin:

    ai = "groq"
    print: %(ai("Merhaba de"))%

Anahtar ya ortam degiskeninden gelir (GROQ_API_KEY gibi) ya da elle verilir:

    ai_setup(key: "...")                      # secili saglayici icin
    ai_setup(saglayici: "gemini", key: "...")  # baska saglayici icin
"""

import os

from ..errors import TonRuntimeError
from ..values import metin as _metin
from . import gomulu
from .ag import _istek

# ---------------------------------------------------------------- saglayicilar
# Model adlari zamanla degisir; `ai_modeller()` canli listeyi verir,
# `ai_setup(model: "...")` ile istedigini secersin.
SAGLAYICILAR = {
    "claude": {
        "baslik": "Claude (Anthropic)",
        "adres": "https://api.anthropic.com/v1/messages",
        "modeller_adresi": "https://api.anthropic.com/v1/models",
        "model": "claude-opus-5",
        "bicim": "anthropic",
        "anahtar_adlari": ("ANTHROPIC_API_KEY", "CLAUDE_API_KEY"),
    },
    "chatgpt": {
        "baslik": "ChatGPT (OpenAI)",
        "adres": "https://api.openai.com/v1/chat/completions",
        "modeller_adresi": "https://api.openai.com/v1/models",
        "model": "gpt-5.5",
        "bicim": "openai",
        "sinir_alani": "max_completion_tokens",
        "anahtar_adlari": ("OPENAI_API_KEY", "CHATGPT_API_KEY"),
    },
    "gemini": {
        "baslik": "Gemini (Google)",
        "adres": "https://generativelanguage.googleapis.com/v1beta/models",
        "modeller_adresi": "https://generativelanguage.googleapis.com/v1beta/models",
        "model": "gemini-3.8-flash",
        "bicim": "gemini",
        "anahtar_adlari": ("GEMINI_API_KEY", "GOOGLE_API_KEY"),
    },
    "grok": {
        "baslik": "Grok (xAI)",
        "adres": "https://api.x.ai/v1/chat/completions",
        "modeller_adresi": "https://api.x.ai/v1/models",
        "model": "grok-4.6",
        "bicim": "openai",
        "anahtar_adlari": ("XAI_API_KEY", "GROK_API_KEY"),
    },
    "groq": {
        "baslik": "Groq",
        "adres": "https://api.groq.com/openai/v1/chat/completions",
        "modeller_adresi": "https://api.groq.com/openai/v1/models",
        "model": "openai/gpt-oss-120b",
        "bicim": "openai",
        "anahtar_adlari": ("GROQ_API_KEY",),
    },
}

TAKMA_ADLAR = {
    "anthropic": "claude", "antropik": "claude", "opus": "claude", "sonnet": "claude",
    "openai": "chatgpt", "gpt": "chatgpt", "chat_gpt": "chatgpt",
    "google": "gemini", "bard": "gemini",
    "xai": "grok", "x": "grok",
}

SIRA = ("claude", "chatgpt", "gemini", "grok", "groq")

# Her saglayicinin anahtari ayri tutulur; saglayici degistirince kaybolmaz.
ANAHTARLAR = {}
# Kullanicinin degistirdigi ayarlar (model, adres, sinir...)
OZEL = {}

AYAR = {
    "saglayici": None,     # None = kendi bulsun
    "kisilik": "",
    "sinir": int(os.environ.get("TON_AI_MAX", "1024")),
}


def _ad_coz(ad):
    ad = _metin(ad).strip().lower().replace(" ", "").replace("-", "")
    return TAKMA_ADLAR.get(ad, ad)


def _anahtar_bul(ad):
    """Once elle verilen, sonra ortam degiskenleri."""
    if ANAHTARLAR.get(ad):
        return ANAHTARLAR[ad]
    for cevre_adi in SAGLAYICILAR[ad]["anahtar_adlari"]:
        deger = os.environ.get(cevre_adi)
        if deger:
            return deger
    return ""


def _genel_anahtar():
    return os.environ.get("TON_AI_KEY", "")


def _ayar(ad, alan):
    """Saglayicinin ayari: once kullanicinin degistirdigi, sonra varsayilan."""
    ozel = OZEL.get(ad, {})
    if alan in ozel:
        return ozel[alan]
    return SAGLAYICILAR[ad].get(alan)


def _secili(y=None, saglayici=None):
    """Hangi saglayici kullanilacak?

    1. cagriya yazilan     ai("...", saglayici: "grok")
    2. `ai = "groq"` degiskeni
    3. ai_setup(saglayici: "...")
    4. anahtari olan ilk saglayici
    """
    if saglayici:
        ad = _ad_coz(saglayici)
    else:
        ad = None
        if y is not None:
            try:
                deger = y.evren.bul("ai")
                if isinstance(deger, str) and deger.strip():
                    ad = _ad_coz(deger)
            except KeyError:
                pass
        if ad is None and AYAR["saglayici"]:
            ad = AYAR["saglayici"]
        if ad is None:
            for aday in SIRA:
                if _anahtar_bul(aday):
                    ad = aday
                    break
        if ad is None:
            ad = "claude"
    if ad not in SAGLAYICILAR:
        raise TonRuntimeError(
            "'%s' diye bir yapay zeka saglayicisi yok. Secenekler: %s"
            % (_metin(saglayici or ad), ", ".join(SIRA)))
    return ad


# ---------------------------------------------------------------- ayarlar
@gomulu("ai_setup", "zeka_ayarla", yorumlayici=True)
def zeka_ayarla(y, key=None, model=None, url=None, kisilik=None, sinir=None,
                saglayici=None):
    ad = _ad_coz(saglayici) if saglayici else _secili(y)
    if saglayici:
        if ad not in SAGLAYICILAR:
            raise TonRuntimeError("'%s' diye bir saglayici yok. Secenekler: %s"
                                  % (_metin(saglayici), ", ".join(SIRA)))
        AYAR["saglayici"] = ad
        # `ai` degiskeni ile ayni seyi anlatsinlar: ikisi de secili saglayici.
        y.evren.ata("ai", ad)
    if key is not None:
        ANAHTARLAR[ad] = _metin(key)
    if model is not None:
        OZEL.setdefault(ad, {})["model"] = _metin(model)
    if url is not None:
        OZEL.setdefault(ad, {})["adres"] = _metin(url)
    if kisilik is not None:
        AYAR["kisilik"] = _metin(kisilik)
    if sinir is not None:
        AYAR["sinir"] = int(sinir)
    return True


@gomulu("ai_ready", "zeka_hazir", yorumlayici=True)
def zeka_hazir(y, saglayici=None):
    ad = _secili(y, saglayici)
    return bool(_anahtar_bul(ad) or _genel_anahtar())


@gomulu("ai_info", "ai_ayar", "zeka_ayar", yorumlayici=True)
def zeka_ayar(y, saglayici=None):
    """Su an hangi saglayici, hangi model, anahtar var mi?"""
    ad = _secili(y, saglayici)
    return {
        "saglayici": ad,
        "baslik": SAGLAYICILAR[ad]["baslik"],
        "model": _ayar(ad, "model"),
        "adres": _ayar(ad, "adres"),
        "bicim": SAGLAYICILAR[ad]["bicim"],
        "anahtar_var": bool(_anahtar_bul(ad) or _genel_anahtar()),
        "sinir": AYAR["sinir"],
    }


@gomulu("ai_providers", "ai_saglayicilar", "zeka_saglayicilar")
def zeka_saglayicilar():
    """Butun saglayicilar ve anahtarlarinin hazir olup olmadigi."""
    return [{
        "ad": ad,
        "baslik": SAGLAYICILAR[ad]["baslik"],
        "model": _ayar(ad, "model"),
        "anahtar_var": bool(_anahtar_bul(ad)),
        "anahtar_adi": SAGLAYICILAR[ad]["anahtar_adlari"][0],
    } for ad in SIRA]


# ---------------------------------------------------------------- istek kurma
def _mesajlar(soru):
    if isinstance(soru, list):
        cikti = []
        for m in soru:
            if isinstance(m, dict):
                rol = m.get("rol") or m.get("role") or "user"
                cikti.append({"role": "assistant" if rol in ("assistant", "zeka", "ai")
                              else "user",
                              "content": _metin(m.get("metin") or m.get("content") or "")})
            else:
                cikti.append({"role": "user", "content": _metin(m)})
        return cikti
    return [{"role": "user", "content": _metin(soru)}]


def _istek_kur(ad, mesajlar, model, kisilik, sinir, anahtar):
    """Saglayiciya gore adres, baslik ve govde uretir."""
    bicim = SAGLAYICILAR[ad]["bicim"]
    adres = _ayar(ad, "adres")

    if bicim == "anthropic":
        govde = {"model": model, "max_tokens": sinir, "messages": mesajlar}
        if kisilik:
            govde["system"] = kisilik
        basliklar = {"x-api-key": anahtar, "anthropic-version": "2023-06-01",
                     "content-type": "application/json"}
        return adres, basliklar, govde

    if bicim == "gemini":
        icerik = [{"role": "model" if m["role"] == "assistant" else "user",
                   "parts": [{"text": m["content"]}]} for m in mesajlar]
        govde = {"contents": icerik, "generationConfig": {"maxOutputTokens": sinir}}
        if kisilik:
            govde["systemInstruction"] = {"parts": [{"text": kisilik}]}
        tam_adres = "%s/%s:generateContent" % (adres.rstrip("/"), model)
        return tam_adres, {"content-type": "application/json",
                           "x-goog-api-key": anahtar}, govde

    # openai uyumlu: chatgpt, grok, groq
    if kisilik:
        mesajlar = [{"role": "system", "content": kisilik}] + mesajlar
    govde = {"model": model, "messages": mesajlar}
    govde[_ayar(ad, "sinir_alani") or "max_tokens"] = sinir
    basliklar = {"Authorization": "Bearer " + anahtar, "content-type": "application/json"}
    return adres, basliklar, govde


def _cevabi_ayikla(veri):
    if isinstance(veri, str):
        return veri
    if isinstance(veri, dict):
        # anthropic
        icerik = veri.get("content")
        if isinstance(icerik, list):
            return "".join(p.get("text", "") for p in icerik if isinstance(p, dict))
        # openai uyumlu
        secenekler = veri.get("choices")
        if isinstance(secenekler, list) and secenekler:
            ilk = secenekler[0]
            if isinstance(ilk, dict):
                mesaj = ilk.get("message") or {}
                return _metin(mesaj.get("content", ilk.get("text", "")))
        # gemini
        adaylar = veri.get("candidates")
        if isinstance(adaylar, list) and adaylar:
            parcalar = (adaylar[0].get("content") or {}).get("parts") or []
            return "".join(p.get("text", "") for p in parcalar if isinstance(p, dict))
        if "text" in veri:
            return _metin(veri["text"])
    return _metin(veri)


def _hata_mesaji(ad, model, cevap):
    veri = cevap["veri"]
    ayrinti = veri
    if isinstance(veri, dict):
        hata = veri.get("error")
        if isinstance(hata, dict):
            ayrinti = hata.get("message") or hata
        elif hata:
            ayrinti = hata
    ayrinti = _metin(ayrinti)
    if len(ayrinti) > 300:
        ayrinti = ayrinti[:300] + "..."
    if cevap["durum"] in (401, 403):
        return ("%s anahtarin kabul edilmedi (%s). %s ortam degiskenini ya da "
                "ai_setup(key: \"...\") degerini kontrol et. Ayrinti: %s"
                % (SAGLAYICILAR[ad]["baslik"], cevap["durum"],
                   SAGLAYICILAR[ad]["anahtar_adlari"][0], ayrinti))
    if cevap["durum"] in (400, 404) and "model" in ayrinti.lower():
        return ("'%s' modeli %s icin gecerli degil. Gecerli modelleri gormek icin "
                "ai_modeller() yaz, sonra ai_setup(model: \"...\") ile sec. Ayrinti: %s"
                % (model, SAGLAYICILAR[ad]["baslik"], ayrinti))
    return "%s hatasi (%s): %s" % (SAGLAYICILAR[ad]["baslik"], cevap["durum"], ayrinti)


# ---------------------------------------------------------------- ai()
@gomulu("ai", "zeka", "sorbana", yorumlayici=True)
def zeka(y, soru, model=None, kisilik=None, sinir=None, saglayici=None):
    ad = _secili(y, saglayici)
    anahtar = _anahtar_bul(ad) or _genel_anahtar()
    if not anahtar:
        raise TonRuntimeError(
            "%s icin anahtar yok. %s ortam degiskenini ayarla ya da "
            "ai_setup(key: \"...\") yaz. Saglayicilari gormek icin: ai_saglayicilar()"
            % (SAGLAYICILAR[ad]["baslik"], SAGLAYICILAR[ad]["anahtar_adlari"][0]))

    model = _metin(model) if model else _ayar(ad, "model")
    kisilik = _metin(kisilik) if kisilik else AYAR["kisilik"]
    sinir = int(sinir) if sinir else AYAR["sinir"]

    adres, basliklar, govde = _istek_kur(ad, _mesajlar(soru), model, kisilik,
                                         sinir, anahtar)
    cevap = _istek("POST", adres, govde, basliklar, zaman_asimi=120)
    if not cevap["basarili"]:
        raise TonRuntimeError(_hata_mesaji(ad, model, cevap))
    return _cevabi_ayikla(cevap["veri"])


@gomulu("ai_models", "ai_modeller", "zeka_modeller", yorumlayici=True)
def zeka_modeller(y, saglayici=None):
    """Saglayicinin su an verdigi model adlarini listeler."""
    ad = _secili(y, saglayici)
    anahtar = _anahtar_bul(ad) or _genel_anahtar()
    if not anahtar:
        raise TonRuntimeError("%s icin anahtar yok." % SAGLAYICILAR[ad]["baslik"])
    adres = _ayar(ad, "modeller_adresi") or SAGLAYICILAR[ad]["modeller_adresi"]
    bicim = SAGLAYICILAR[ad]["bicim"]
    if bicim == "anthropic":
        basliklar = {"x-api-key": anahtar, "anthropic-version": "2023-06-01"}
    elif bicim == "gemini":
        basliklar = {"x-goog-api-key": anahtar}
    else:
        basliklar = {"Authorization": "Bearer " + anahtar}
    cevap = _istek("GET", adres, None, basliklar)
    if not cevap["basarili"]:
        raise TonRuntimeError(_hata_mesaji(ad, "", cevap))
    veri = cevap["veri"]
    adlar = []
    if isinstance(veri, dict):
        for oge in veri.get("data") or veri.get("models") or []:
            if isinstance(oge, dict):
                model_adi = oge.get("id") or oge.get("name") or ""
                if model_adi.startswith("models/"):
                    model_adi = model_adi[len("models/"):]
                if model_adi:
                    adlar.append(model_adi)
    return sorted(adlar)


@gomulu("ai_json", "zeka_veri", yorumlayici=True)
def zeka_veri(y, soru, model=None, saglayici=None):
    from .cekirdek import json_oku
    ham = zeka(y, _metin(soru) + "\n\nSadece gecerli JSON dondur, baska hicbir sey yazma.",
               model=model, saglayici=saglayici)
    ham = ham.strip()
    if ham.startswith("```"):
        ham = ham.split("\n", 1)[-1]
        if ham.endswith("```"):
            ham = ham[:-3]
        if ham.startswith("json"):
            ham = ham[4:]
    return json_oku(ham.strip())


@gomulu("ai_chat", "zeka_sohbet", yorumlayici=True)
def zeka_sohbet(y, gecmis, soru=None, model=None, saglayici=None):
    mesajlar = list(gecmis) if isinstance(gecmis, list) else []
    if soru is not None:
        mesajlar.append({"rol": "user", "metin": _metin(soru)})
    cevap = zeka(y, mesajlar, model=model, saglayici=saglayici)
    mesajlar.append({"rol": "assistant", "metin": cevap})
    return {"cevap": cevap, "gecmis": mesajlar}
