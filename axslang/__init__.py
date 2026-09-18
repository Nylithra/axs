"""Axs dili - cekirdek .

Ek hicbir pakete ihtiyac duymaz; sadece Python 3.8+ standart kutuphanesi yeter.
"""

from .surum import SURUM, SURUM_ADI

__all__ = ["SURUM", "SURUM_ADI", "calistir", "calistir_dosya"]


def calistir(kaynak, dosya=None, cikti=None, argv=None):
    """Bir Axs kaynagini calistirir."""
    from .interpreter import Yorumlayici
    y = Yorumlayici(dosya, cikti, argv)
    return y.calistir_kaynak(kaynak, dosya)


def calistir_dosya(yol, cikti=None, argv=None):
    """Bir .axs/.nyl dosyasini calistirir."""
    from .interpreter import Yorumlayici
    y = Yorumlayici(yol, cikti, argv)
    return y.calistir_dosya(yol)
