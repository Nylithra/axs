use web

func anasayfa(istek)
  return "<h1>Merhaba</h1>"
end

func kullanici(istek)
  return {ad: istek.parametreler.ad, yol: istek.yol}
end

func yanki(istek)
  return web.json({alinan: istek.veri, yontem: istek.yontem})
end

web.page("/", anasayfa)
web.page("/kullanici/:ad", kullanici)
web.api("/yanki", yanki)
web.start(8123)
wait(0.3)

print(get("http://127.0.0.1:8123/"))
print(get("http://127.0.0.1:8123/kullanici/nyl"))
print(post("http://127.0.0.1:8123/yanki", {x: 1}))
print(request("http://127.0.0.1:8123/olmayan").durum)
print(web.routes().len())
print(web.tag("p", "selam", class: "kutu"))
print(web.list(["a", "b"]))
print(web.table([{a: 1, b: 2}]))
print(web.escape("<script>"))
web.stop()
