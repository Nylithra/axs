"""Es zamanli (asenkron) isler.

    gorev = asyn(https://api.lanux.online)   # arka planda getir
    gorev = asyn(uzun_is, 5)                 # arka planda calistir
    sonuc = wait(%gorev%)                    # bitmesini bekle
    wait(2)                                  # 2 saniye bekle
"""

import threading
import time

from ..errors import AxsRuntimeError, AxsTypeError
from ..values import Gorev, cagrilabilir_mi, metin as _metin, sayi_mi, tur as _tur
from . import gomulu, hem


def _baslat(ad, calis):
    gorev = Gorev(ad)

    def sarmal():
        try:
            gorev.sonuc = calis()
        except BaseException as e:  # noqa: BLE001 - gorevde ne olursa saklanir
            gorev.hata = e
        finally:
            gorev.bitti = True

    gorev.thread = threading.Thread(target=sarmal, daemon=True)
    gorev.thread.start()
    return gorev


@gomulu("asyn", "async", "arkaplan", "esza", yorumlayici=True)
def asyn(y, hedef, *args):
    if cagrilabilir_mi(hedef):
        gorev = _baslat(getattr(hedef, "ad", "is"), lambda: y.cagir(hedef, list(args)))
    elif isinstance(hedef, str):
        from .ag import getir
        adres = hedef
        gorev = _baslat(adres, lambda: getir(adres, *args))
    else:
        raise AxsTypeError("asyn() bir is ya da adres ister, %s verildi" % _tur(hedef))
    y.gorevler.append(gorev)
    return gorev


@gomulu("wait", "bekle")
def bekle(hedef=None, sure=None):
    if hedef is None:
        return None
    if sayi_mi(hedef):
        time.sleep(float(hedef))
        return None
    if isinstance(hedef, Gorev):
        return hedef.bekle(sure)
    if isinstance(hedef, list):
        return [bekle(g, sure) for g in hedef]
    raise AxsTypeError("bekle() sayi ya da gorev ister, %s verildi" % _tur(hedef))


@gomulu("waitall", "hepsini_bekle")
def hepsini_bekle(gorevler):
    if isinstance(gorevler, Gorev):
        gorevler = [gorevler]
    return [g.bekle() if isinstance(g, Gorev) else g for g in gorevler]


@hem("gorev", "done", "bitti_mi")
def bitti_mi(gorev):
    if not isinstance(gorev, Gorev):
        raise AxsTypeError("bitti_mi() bir gorev ister")
    return gorev.bitti


@hem("gorev", "result", "sonucu")
def sonucu(gorev, sure=None):
    return gorev.bekle(sure)


@gomulu("parallel", "paralel", yorumlayici=True)
def paralel(y, isler, *args):
    """Birden cok isi ayni anda calistirir, sonuclarini sirayla dondurur."""
    if not isinstance(isler, list):
        raise AxsTypeError("paralel() bir is listesi ister")
    gorevler = []
    for oge in isler:
        if cagrilabilir_mi(oge):
            gorevler.append(_baslat(getattr(oge, "ad", "is"),
                                    lambda o=oge: y.cagir(o, list(args))))
        elif isinstance(oge, str):
            from .ag import getir
            gorevler.append(_baslat(oge, lambda a=oge: getir(a)))
        else:
            raise AxsTypeError("paralel() listesinde is ya da adres olmali")
    y.gorevler.extend(gorevler)
    return [g.bekle() for g in gorevler]


@gomulu("after", "sonra", yorumlayici=True)
def sonra(y, saniye, hedef, *args):
    if not cagrilabilir_mi(hedef):
        raise AxsTypeError("sonra() bir is ister")

    def calis():
        time.sleep(float(saniye))
        return y.cagir(hedef, list(args))

    gorev = _baslat("sonra:%s" % _metin(saniye), calis)
    y.gorevler.append(gorev)
    return gorev


@gomulu("every", "her_saniye", yorumlayici=True)
def her_saniye(y, saniye, hedef, adet=None):
    """Belirli araliklarla tekrarlar. adet verilmezse durdurulana kadar surer."""
    if not cagrilabilir_mi(hedef):
        raise AxsTypeError("her_saniye() bir is ister")
    sinir = int(adet) if adet is not None else None

    def calis():
        sayac = 0
        while sinir is None or sayac < sinir:
            time.sleep(float(saniye))
            y.cagir(hedef, [])
            sayac += 1
        return sayac

    gorev = _baslat("her:%s" % _metin(saniye), calis)
    y.gorevler.append(gorev)
    return gorev


@gomulu("timeout", "sure_sinir", yorumlayici=True)
def sure_sinir(y, saniye, hedef, *args):
    gorev = asyn(y, hedef, *args)
    gorev.thread.join(float(saniye))
    if not gorev.bitti:
        raise AxsRuntimeError("Islem %s saniyede bitmedi" % _metin(saniye))
    return gorev.bekle()
