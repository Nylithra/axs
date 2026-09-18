# Gateway akisi: Hello -> Identify -> READY -> olaylar -> heartbeat
use jubbio

jubbio.giris("SAHTE_TOKEN", "UYG1")
jubbio.ag_ayarla(adres: env("SAHTE_GATEWAY"), kayit: false)

sayac = 0

func hazir(veri)
  print: HAZIR: %veri.user.username% (oturum %veri.session_id%)
end

func mesaj(m)
  sayac += 1
  print: MESAJ %sayac%: %m.content% <- %m.author.username% (kanal %m.channel_id%)
end

func katildi(veri)
  print: KATILDI: %veri.user.username%
  print: toplam %sayac% mesaj alindi, bot duruyor
  jubbio.dur()
end

jubbio.dinle("hazir", hazir)
jubbio.dinle("mesaj", mesaj)
jubbio.dinle("uye_katildi", katildi)

jubbio.calistir(["sunucular", "mesajlar", "icerik"], yeniden_baglan: false)

print: ben: %(jubbio.ben().username)%
print: bitti
