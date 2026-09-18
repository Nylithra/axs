# Web + veritabani: kucuk bir not defteri.
# Calistir: axs examples/notlar_web.axs   ->  http://localhost:8080

use web

db = connect("notlar.db")
db.run("create table if not exists notlar (metin text)")

func anasayfa(istek)
  satirlar = db.all("select rowid as no, metin from notlar order by rowid desc")
  govde = """
    <h1>Notlarım</h1>
    <form action="/ekle" method="post">
      <input name="metin" placeholder="Yeni not" style="width:70%%">
      <button>Ekle</button>
    </form>
  """
  return web.html(baslik: "Notlar", govde: govde + web.table(satirlar))
end

func ekle(istek)
  metin = istek.veri.metin
  if metin
    db.run("insert into notlar values (?)", [metin])
  end
  return web.redirect("/")
end

func api(istek)
  return db.all("select rowid as no, metin from notlar")
end

web.page("/", anasayfa)
web.post("/ekle", ekle)
web.api("/api/notlar", api)

web.serve(8080)
