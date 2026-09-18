# Yapay Zekâ

Axs beş sağlayıcıyla çalışır. Seçmek tek satır:

```axs
ai = "groq"

print: (ai("Bana bir fıkra anlat"));
```

| `ai = "..."` | Sağlayıcı | Anahtar (ortam değişkeni) | Varsayılan model |
|---|---|---|---|
| `claude` · `anthropic` | Claude (Anthropic) | `ANTHROPIC_API_KEY` | `claude-opus-5` |
| `chatgpt` · `openai` · `gpt` | ChatGPT (OpenAI) | `OPENAI_API_KEY` | `gpt-5.5` |
| `gemini` · `google` | Gemini (Google) | `GEMINI_API_KEY` | `gemini-3.8-flash` |
| `grok` · `xai` | Grok (xAI) | `XAI_API_KEY` | `grok-4.6` |
| `groq` | Groq | `GROQ_API_KEY` | `openai/gpt-oss-120b` |

`AXS_AI_KEY` hepsinde çalışan ortak anahtardır.

---

## Anahtar verme

Üç yol var, hepsi aynı kapıya çıkar:

```bash
export GROQ_API_KEY="gsk_..."        # 1. ortam değişkeni
```

```axs
ai_setup(key: "gsk_...")                       # 2. seçili sağlayıcı için
ai_setup(saglayici: "gemini", key: "AIza...")  # 3. belirli bir sağlayıcı için
```

Her sağlayıcının anahtarı ayrı tutulur: `ai = "groq"` deyip sonra
`ai = "gemini"` dediğinde anahtarlar kaybolmaz.

## Sağlayıcı seçmenin dört yolu

Öncelik sırasıyla:

```axs
ai("soru", saglayici: "grok")    # 1. sadece bu çağrı için
ai = "groq"                      # 2. o andan sonrası için
ai_setup(saglayici: "gemini")    # 3. (yukarıdakiyle aynı şey — ai de değişir)
                                 # 4. hiçbiri yoksa: anahtarı olan ilk sağlayıcı
```

## Ne var?

| İş | Ne yapar |
|---|---|
| `ai(soru)` | Sorar, cevabı metin olarak verir |
| `ai(soru, model:, kisilik:, sinir:, saglayici:)` | Ayarlı sorma |
| `ai_json(soru)` | Cevabı harita/liste olarak ister |
| `ai_chat(gecmis, soru)` | `{cevap, gecmis}` verir; geçmişi geri besleyebilirsin |
| `ai_ready()` | Anahtar var mı |
| `ai_ayar()` | Şu an hangi sağlayıcı, hangi model, anahtar var mı |
| `ai_saglayicilar()` | Beşinin durumu |
| `ai_modeller()` | Sağlayıcının **canlı** model listesi |

```axs
ai = "groq"
print: (ai_ayar());
# {saglayici: "groq", baslik: "Groq", model: "openai/gpt-oss-120b", ...}
```

## Model seçme

Varsayılan modeller zamanla eskir — sağlayıcılar model kapatır. Canlı listeyi
sor, sonra seç:

```axs
ai = "groq"
print: (ai_modeller());
ai_setup(model: "openai/gpt-oss-20b")
```

Model adı geçersizse Axs bunu açıkça söyler:

```
'abc' modeli Groq için geçerli değil. Geçerli modelleri görmek için
ai_modeller() yaz, sonra ai_setup(model: "...") ile seç.
```

## Kişilik ve uzunluk

```axs
ai_setup(kisilik: "Kısa ve Türkçe konuş", sinir: 2048)
```

## Tarayıcıda

Tarayıcıda API anahtarı tutulmaz — istek **kendi sunucuna** gider, anahtar
orada kalır:

```axs
# sunucu tarafı
use web
ai_setup(saglayici: "groq", key: "gsk_...")
web.ai_ucu("/api/ai")
web.uygulama("/", "sohbet.axs")
web.serve(8080)
```

```axs
# tarayıcı tarafı (sohbet.axs)
ai = "groq"
cevap = ai("merhaba")      # /api/ai'ye gider, sunucu sağlayıcıya sorar
yaz_metin("#cevap", cevap)
```

## Kendi uç noktan

OpenAI uyumlu bir sunucun varsa (yerel model, vekil sunucu, kurum içi API):

```axs
ai_setup(saglayici: "chatgpt", url: "http://localhost:11434/v1/chat/completions",
         key: "gerekmez", model: "llama3")
```

## Neden `ai = "groq"` çalışıyor?

`ai` hem bir hazır iş hem de bir değişken olabilir. Çıplak ad önce
değişkenlere baktığı için karışıklık olmaz: `ai("soru")` çağrı, `ai` ise seçtiğin
sağlayıcının adı.

```axs
ai = "groq"
print: ai;              # groq
print: (ai("selam"));   # Groq'un cevabı
```
