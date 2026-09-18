# Ortak altyapi: veritabani, ayarlar, gomulu kutular, kayit, yetki
use jubbio

MARKA = "TON"
RENK = "#5865f2"
RENK_YESIL = "#43b581"
RENK_KIRMIZI = "#f04747"
RENK_SARI = "#faa61a"
RENK_GRI = "#747f8d"

_db = connect(env("TON_VERI", "ton.db"))

func veritabanini_kur()
  _db.run("""create table if not exists ayarlar (
     sunucu text, anahtar text, deger text, primary key (sunucu, anahtar))""")
  _db.run("""create table if not exists uyarilar (
     id integer primary key autoincrement, sunucu text, kullanici text,
     sebep text, yetkili text, zaman text)""")
  _db.run("""create table if not exists ticketlar (
     kanal text primary key, sunucu text, sahip text, konu text,
     durum text, zaman text)""")
  return true
end

# ---------------------------------------------------------------- ayarlar
func ayar_yaz(sunucu, anahtar, deger)
  _db.run("""insert into ayarlar (sunucu, anahtar, deger) values (?, ?, ?)
             on conflict(sunucu, anahtar) do update set deger = excluded.deger""",
            [metin(sunucu), anahtar, metin(deger)])
  return true
end

func ayar_oku(sunucu, anahtar, varsayilan = "")
  satir = _db.one("select deger from ayarlar where sunucu = ? and anahtar = ?",
                    [metin(sunucu), anahtar])
  if satir == null
    return varsayilan
  end
  return satir.deger
end

func ayar_acik_mi(sunucu, anahtar, varsayilan = false)
  deger = ayar_oku(sunucu, anahtar, "")
  if deger == ""
    return varsayilan
  end
  return deger == "1"
end

# ---------------------------------------------------------------- gomulu kutular
func kutu(baslik, aciklama, renk = RENK)
  return {baslik: baslik, aciklama: aciklama, renk: renk,
          alt_yazi: MARKA}
end

func basarili(aciklama)
  return kutu("✅ Tamam", aciklama, RENK_YESIL)
end

func uyari_kutusu(aciklama)
  return kutu("⚠️ Dikkat", aciklama, RENK_SARI)
end

func hata_kutusu(aciklama)
  return kutu("❌ Olmadi", aciklama, RENK_KIRMIZI)
end

# ---------------------------------------------------------------- yetki
# Komutu yazan kisi yetkili mi?
func yetkili_mi(e, izinler = null)
  uye = al(e, "member", null)
  if uye == null
    return false
  end
  if izinler != null
    if jubbio.izni_var(uye, izinler)
      return true
    end
  end
  if jubbio.izni_var(uye, ["yonetici"])
    return true
  end
  rol = ayar_oku(al(e, "guild_id", ""), "yetkili_rol", "")
  if rol != ""
    if contains(al(uye, "roles", []), rol)
      return true
    end
  end
  return false
end

func yetkisiz_cevap(e)
  jubbio.cevapla(e, hata_kutusu("Bu komutu kullanma yetkin yok."), gizli: true)
  return null
end

# ---------------------------------------------------------------- kayit
func kayit(sunucu, baslik, aciklama, renk = RENK_GRI)
  kanal = ayar_oku(sunucu, "kayit_kanali", "")
  if kanal == ""
    return null
  end
  try
    jubbio.yolla(sunucu, kanal, {baslik: baslik, aciklama: aciklama,
                                   renk: renk, alt_yazi: MARKA + " kayit"})
  catch mesaj
    print: [kayit] gonderilemedi: mesaj;
  end
  return null
end

# ---------------------------------------------------------------- uyarilar
func uyari_ekle(sunucu, kullanici, sebep, yetkili)
  _db.run("""insert into uyarilar (sunucu, kullanici, sebep, yetkili, zaman)
             values (?, ?, ?, ?, ?)""",
            [metin(sunucu), metin(kullanici), sebep, metin(yetkili), tarih()])
  return uyari_sayisi(sunucu, kullanici)
end

func uyari_sayisi(sunucu, kullanici)
  satir = _db.one("""select count(*) as adet from uyarilar
                     where sunucu = ? and kullanici = ?""",
                    [metin(sunucu), metin(kullanici)])
  return al(satir, "adet", 0)
end

func uyari_listesi(sunucu, kullanici, sinir = 10)
  return _db.all("""select id, sebep, yetkili, zaman from uyarilar
                    where sunucu = ? and kullanici = ? order by id desc limit ?""",
                   [metin(sunucu), metin(kullanici), sinir])
end

func uyari_sil(sunucu, kullanici)
  return _db.run("delete from uyarilar where sunucu = ? and kullanici = ?",
                   [metin(sunucu), metin(kullanici)])
end

# ---------------------------------------------------------------- ticket kaydi
func ticket_yaz(kanal, sunucu, sahip, konu)
  _db.run("""insert or replace into ticketlar
             (kanal, sunucu, sahip, konu, durum, zaman) values (?, ?, ?, ?, ?, ?)""",
            [metin(kanal), metin(sunucu), metin(sahip), konu, "acik", tarih()])
  return true
end

func ticket_oku(kanal)
  return _db.one("select * from ticketlar where kanal = ?", [metin(kanal)])
end

func ticket_kapat_kaydi(kanal)
  _db.run("update ticketlar set durum = 'kapali' where kanal = ?", [metin(kanal)])
  return true
end

func ticket_sayisi(sunucu)
  satir = _db.one("select count(*) as adet from ticketlar where sunucu = ?",
                    [metin(sunucu)])
  return al(satir, "adet", 0)
end

func acik_ticket(sunucu, sahip)
  return _db.one("""select kanal from ticketlar
                    where sunucu = ? and sahip = ? and durum = 'acik'""",
                   [metin(sunucu), metin(sahip)])
end
