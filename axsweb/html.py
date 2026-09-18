"""HTML uretimi: etiketler, sayfa iskeleti, kacis."""

from axslang.values import metin as _metin

TEK_ETIKETLER = {"br", "hr", "img", "input", "meta", "link"}

VARSAYILAN_STIL = """
  :root { color-scheme: light dark; --ana: #2f6fed; --yazi: #16181d; --zemin: #ffffff;
          --yumusak: #f3f5f9; --cizgi: #e2e6ef; }
  @media (prefers-color-scheme: dark) {
    :root { --yazi: #e8eaf0; --zemin: #14161b; --yumusak: #1d2027; --cizgi: #2a2f3a; }
  }
  * { box-sizing: border-box; }
  body { margin: 0; padding: 2rem 1rem; background: var(--zemin); color: var(--yazi);
         font: 16px/1.6 system-ui, -apple-system, "Segoe UI", Roboto, sans-serif; }
  main, .kutu { max-width: 46rem; margin: 0 auto; }
  h1, h2, h3 { line-height: 1.25; }
  a { color: var(--ana); }
  code, pre { background: var(--yumusak); border-radius: 6px; }
  code { padding: .1rem .35rem; }
  pre { padding: 1rem; overflow-x: auto; }
  table { border-collapse: collapse; width: 100%; }
  th, td { border-bottom: 1px solid var(--cizgi); padding: .5rem; text-align: left; }
  input, textarea, select, button { font: inherit; padding: .5rem .7rem;
    border: 1px solid var(--cizgi); border-radius: 8px; background: var(--zemin);
    color: var(--yazi); }
  button { background: var(--ana); color: #fff; border-color: transparent; cursor: pointer; }
"""


def kacir(deger):
    """HTML icinde guvenli hale getirir."""
    s = _metin(deger)
    return (s.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")
             .replace('"', "&quot;"))


def etiket(ad, icerik="", **ozellikler):
    ad = _metin(ad)
    parcalar = []
    for k, v in ozellikler.items():
        k = k.rstrip("_").replace("_", "-")
        if v is True:
            parcalar.append(" " + k)
        elif v is not False and v is not None:
            parcalar.append(' %s="%s"' % (k, kacir(v)))
    ozellik_metni = "".join(parcalar)
    if ad in TEK_ETIKETLER:
        return "<%s%s>" % (ad, ozellik_metni)
    if isinstance(icerik, (list, tuple)):
        icerik = "".join(_metin(p) for p in icerik)
    return "<%s%s>%s</%s>" % (ad, ozellik_metni, _metin(icerik), ad)


def sayfa(baslik="Axs", govde="", stil=None, bas=None, dil="tr", betik=None):
    if isinstance(govde, (list, tuple)):
        govde = "\n".join(_metin(p) for p in govde)
    stil_metni = VARSAYILAN_STIL if stil is None else _metin(stil)
    return (
        "<!doctype html>\n"
        '<html lang="%s">\n<head>\n<meta charset="utf-8">\n'
        '<meta name="viewport" content="width=device-width, initial-scale=1">\n'
        "<title>%s</title>\n<style>%s</style>\n%s</head>\n"
        "<body>\n<main>\n%s\n</main>\n%s</body>\n</html>\n"
        % (dil, kacir(baslik), stil_metni, (_metin(bas) + "\n") if bas else "",
           _metin(govde), ("<script>%s</script>\n" % _metin(betik)) if betik else "")
    )


def tablo(satirlar, basliklar=None):
    """Harita listesinden HTML tablo uretir."""
    satirlar = list(satirlar or [])
    if basliklar is None:
        basliklar = list(satirlar[0].keys()) if satirlar and isinstance(satirlar[0], dict) else []
    bas = "".join(etiket("th", kacir(b)) for b in basliklar)
    govde = []
    for s in satirlar:
        if isinstance(s, dict):
            govde.append(etiket("tr", "".join(etiket("td", kacir(s.get(b, ""))) for b in basliklar)))
        else:
            govde.append(etiket("tr", etiket("td", kacir(s))))
    return etiket("table", etiket("thead", etiket("tr", bas)) + etiket("tbody", "".join(govde)))


def liste(ogeler, sirali=False):
    ic = "".join(etiket("li", kacir(o)) for o in (ogeler or []))
    return etiket("ol" if sirali else "ul", ic)


def baglanti(adres, yazi=None):
    return etiket("a", kacir(yazi if yazi is not None else adres), href=adres)
