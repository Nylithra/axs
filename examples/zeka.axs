# Yapay zeka.  Saglayiciyi tek satirda secersin:

ai = "groq"        # claude · chatgpt · gemini · grok · groq

# Anahtar ortam degiskeninden gelir (GROQ_API_KEY gibi)
# ya da elle verilir:  ai_setup(key: "...")

print: Saglayicilar:
for s in ai_saglayicilar()
  hazir = "yok"
  if %s.anahtar_var%
    hazir = "hazir"
  end
  print:   %s.ad% - %s.model% (%s.anahtar_adi%: %hazir%)
end

print:
print: Secili: %(ai_ayar().saglayici)% / %(ai_ayar().model)%

if not ai_ready()
  print:
  print: Anahtar yok. Once %(ai_ayar().saglayici)% icin anahtar ver:
  print:   ai_setup(key: "...")
  exit(0)
end

# --- duz soru ---
print: %(ai("Bir cumleyle TON dilini tanit"))%

# --- JSON isteyerek ---
veri = ai_json("Turkiye'nin 3 buyuk sehrini {sehirler: [...]} bicimde ver")
print: %veri.sehirler%

# --- ayni soruyu iki saglayiciya sormak ---
print: %(ai("2+2 kac? sadece sayi yaz", saglayici: "groq"))%
print: %(ai("2+2 kac? sadece sayi yaz", saglayici: "gemini"))%

# --- sohbet ---
sohbet = ai_chat([], "Merhaba, adin ne?")
print: %sohbet.cevap%
sohbet = ai_chat(%sohbet.gecmis%, "Az once ne sordum?")
print: %sohbet.cevap%

# --- model degistirmek ---
# print(ai_modeller())            # saglayicinin canli model listesi
# ai_setup(model: "...")
