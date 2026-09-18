# Yapay zeka saglayicilari: istek bicimleri ve cevap cozumu.
# Gercek API'ye cikmadan, yerel sahte bir sunucuyla sinanir.

use web

# --- sahte saglayicilar ---
func anthropic_ucu(istek)
  g = istek.veri
  metin = "anthropic model=" + g.model + " sinir=" + g.max_tokens
  metin = metin + " sistem=" + g.system + " soru=" + g.messages[0].content
  return {content: [{type: "text", text: metin}]}
end

func openai_ucu(istek)
  g = istek.veri
  roller = join(map(g.messages, func(m) -> m.role), ",")
  son = last(g.messages)
  metin = "openai model=" + g.model + " alanlar=" + join(keys(g), "|")
  metin = metin + " roller=" + roller + " son=" + %son.content%
  return {choices: [{message: {content: metin}}]}
end

func gemini_ucu(istek)
  g = istek.veri
  ayar = g.generationConfig
  ilk = g.contents[0]
  metin = "gemini yol=" + istek.parametreler.kalan + " sinir=" + ayar.maxOutputTokens
  metin = metin + " rol=" + ilk.role + " soru=" + ilk.parts[0].text
  metin = metin + " sistem=" + g.systemInstruction.parts[0].text
  return {candidates: [{content: {parts: [{text: metin}]}}]}
end

func yetkisiz(istek)
  return web.json({error: {message: "invalid api key"}}, 401)
end

func model_yok(istek)
  return web.json({error: {message: "The model `abc` does not exist"}}, 404)
end

web.post("/anthropic", anthropic_ucu)
web.post("/openai", openai_ucu)
web.post("/gemini/*", gemini_ucu)
web.post("/yetkisiz", yetkisiz)
web.post("/modelyok", model_yok)
web.start(8134)
wait(0.3)

temel = "http://127.0.0.1:8134"

# --- her saglayiciyi yerel uca yonlendir ---
ai_setup(saglayici: "claude", key: "deneme", url: temel + "/anthropic")
ai_setup(saglayici: "chatgpt", key: "deneme", url: temel + "/openai")
ai_setup(saglayici: "grok", key: "deneme", url: temel + "/openai")
ai_setup(saglayici: "groq", key: "deneme", url: temel + "/openai")
ai_setup(saglayici: "gemini", key: "deneme", url: temel + "/gemini")
ai_setup(kisilik: "kisa konus", sinir: 256)

# --- ai = "..." ile secim ---
ai = "claude"
print: (ai("selam"));

ai = "chatgpt"
print: (ai("selam"));

ai = "grok"
print: (ai("selam", model: "grok-ozel"));

ai = "groq"
print: (ai("selam"));

ai = "gemini"
print: (ai("selam"));

# --- cagri icinde saglayici secmek degiskeni bozmasin ---
print: (ai("selam", saglayici: "claude"));
print: hala (ai_ayar().saglayici);

# --- sohbet gecmisi ---
ai = "chatgpt"
sohbet = ai_chat([], "ilk soru")
print: (len(sohbet.gecmis)); mesaj

# --- hatalar ---
ai_setup(saglayici: "groq", url: temel + "/yetkisiz")
ai = "groq"
try
  ai("selam")
catch m
  print: m;
end

ai_setup(saglayici: "groq", url: temel + "/modelyok")
try
  ai("selam")
catch m
  print: m;
end

# --- anahtar yoksa ---
ai = "bilinmeyen"
try
  ai("selam")
catch m
  print: m;
end

web.stop()
