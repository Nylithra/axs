# Testler icin sahte Jubbio REST sunucusu
use web

func yanki(istek)
  print: REST %istek.yontem% %istek.yol% %istek.govde%
  if ends(%istek.yol%, "/channels")
    if %istek.yontem% == "GET"
      return [{id: 100, name: "genel", type: 0}, {id: 200, name: "DESTEK", type: 4}]
    end
    return {id: 555, name: "destek-1", type: 0}
  end
  if ends(%istek.yol%, "/roles")
    return [{id: 300, name: "@everyone"}, {id: 301, name: "Yetkili"}]
  end
  return {ok: true, id: 999}
end

web.api("/api/*", yanki)
web.serve(number(env("SAHTE_REST_PORT", "8195")), sessiz: true)
