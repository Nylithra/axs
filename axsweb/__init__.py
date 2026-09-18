"""axsweb - Axs'in web kutuphanesi.

    use web

    func anasayfa(istek)
      return web.html(baslik: "Merhaba", govde: "<h1>Merhaba Axs</h1>")
    end

    web.page("/", anasayfa)
    web.serve(8080)
"""

from .sunucu import yukle  # noqa: F401
from .surum import SURUM  # noqa: F401
