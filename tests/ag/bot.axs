# Uctan uca: gateway'den komut gelir, bot REST ile cevap yollar.
use jubbio

jubbio.giris("SAHTE_TOKEN")
jubbio.ag_ayarla(adres: env("SAHTE_GATEWAY"))
jubbio.ayarla(temel: env("SAHTE_REST"))

func mesaj(m)
  if %m.kendim%
    return null
  end
  icerik = trim(al(%m%, "content", ""))
  if not starts(%icerik%, "!")
    print: atlandi: %icerik%
    return null
  end
  parcalar = split(%icerik%, " ")
  komut = replace(%parcalar[0]%, "!", "", 1)

  if %komut% == "selam"
    jubbio.yolla(%m.guild_id%, %m.channel_id%, "Selam " + jubbio.bahset(%m.author.id%) + "!")
  elif %komut% == "topla"
    toplam = 0
    for p in slice(%parcalar%, 1)
      toplam += number(%p%, 0)
    end
    jubbio.yolla(%m.guild_id%, %m.channel_id%, "toplam " + %toplam%)
  elif %komut% == "kutu"
    jubbio.yolla(%m.guild_id%, %m.channel_id%, {baslik: "Kutu", aciklama: "govde", renk: "#2f6fed"})
  elif %komut% == "dur"
    print: dur komutu geldi
    jubbio.dur()
  end
  return null
end

jubbio.dinle("mesaj", mesaj)
jubbio.calistir(["sunucular", "mesajlar", "icerik"], yeniden_baglan: false)
print: bot durdu
