"""tonweb - TON'un web kutuphanesi.

    use web

    func anasayfa(istek)
      return web.html(baslik: "Merhaba", govde: "<h1>Merhaba TON</h1>")
    end

    web.page("/", anasayfa)
    web.serve(8080)
"""

from .sunucu import yukle  # noqa: F401
from .surum import SURUM  # noqa: F401
