"""Axs tarayici paketi: derlenmis kodu tek bir HTML dosyasina koyar.

    axs paket sayac.axs      ->  sayac.html  (cift tiklayip acabilirsin)
"""

import os

from axslang.derleyici import Derleyici
from axslang.okuma import dosya_oku

from . import html as H

TARAYICI_KLASORU = os.path.join(os.path.dirname(os.path.abspath(__file__)), "tarayici")
CALISMA_ZAMANI = os.path.join(TARAYICI_KLASORU, "axs.js")

EK_STIL = """
  #axs-cikti { white-space: pre-wrap; font: 14px/1.6 ui-monospace, SFMono-Regular,
    Menlo, monospace; background: var(--yumusak); padding: 1rem; border-radius: 8px;
    margin-top: 1rem; }
  #axs-cikti:empty { display: none; }
  #axs-uygulama:empty { display: none; }
"""


def calisma_zamani():
    """axs.js icerigi."""
    return dosya_oku(CALISMA_ZAMANI, satirlari_duzelt=False)


def derle(axs_dosyasi):
    """Bir Axs dosyasini tarayici JavaScript'ine cevirir."""
    d = Derleyici(axs_dosyasi)
    return d.derle(dosya_oku(axs_dosyasi), os.path.basename(axs_dosyasi))


GOVDE_UZANTILARI = (".govde.html", ".body.html")


def govde_bul(axs_dosyasi, govde=None):
    """Yaninda `<ad>.govde.html` varsa onu sayfa govdesi yapar.

    Paket ciktisi `<ad>.html` oldugu icin govde dosyasinin adi ayridir."""
    if govde is not None:
        return govde
    temel = os.path.splitext(axs_dosyasi)[0]
    for uzanti in GOVDE_UZANTILARI:
        if os.path.isfile(temel + uzanti):
            return dosya_oku(temel + uzanti)
    return ""


def sayfa(axs_dosyasi, baslik=None, govde=None, gomulu=True, betik_adresi=None,
          js_adresi=None):
    """Tarayicida calisacak tam HTML sayfasini uretir."""
    ad = os.path.splitext(os.path.basename(axs_dosyasi))[0]
    icerik = ('<div id="axs-uygulama">%s</div>\n<pre id="axs-cikti"></pre>'
              % govde_bul(axs_dosyasi, govde))
    if gomulu:
        betikler = ("<script>\n%s\n</script>\n<script>\n%s\n</script>"
                    % (calisma_zamani(), derle(axs_dosyasi)))
    else:
        betikler = ('<script src="%s"></script>\n<script src="%s"></script>'
                    % (js_adresi or "/axs.js", betik_adresi or ("/%s.axs.js" % ad)))
    return H.sayfa(baslik=baslik or ad,
                   govde=icerik + "\n" + betikler,
                   stil=H.VARSAYILAN_STIL + EK_STIL)
