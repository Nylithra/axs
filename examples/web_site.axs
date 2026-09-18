# Basit bir web sitesi.  Calistir:  axs examples/web_site.axs
# Sonra tarayicida ac: http://localhost:8080

use web

func anasayfa(istek)
  govde = """
    <h1>Axs Web</h1>
    <p>Bu sayfa <b>axsweb</b> ile yazildi.</p>
    <p><a href='/selam/dunya'>Selam sayfasi</a> - <a href='/api/saat'>API</a></p>
    <form action='/mesaj' method='post'>
      <input name='mesaj' placeholder='Bir sey yaz'>
      <button>Gonder</button>
    </form>
  """
  return web.html(baslik: "Axs Web", govde: govde)
end

func selam(istek)
  ad = istek.parametreler.ad
  return web.html(baslik: "Selam", govde: "<h1>Selam " + web.escape(ad) + "</h1>")
end

func saat(istek)
  return {saat: now().metin, surum: "1.0.0"}
end

func mesaj(istek)
  gelen = istek.veri.mesaj
  return web.html(baslik: "Alindi", govde: "<h1>Aldim</h1><p>" + web.escape(gelen) + "</p>")
end

web.page("/", anasayfa)
web.page("/selam/:ad", selam)
web.api("/api/saat", saat)
web.post("/mesaj", mesaj)

web.serve(8080)
