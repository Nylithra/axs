"""Dosya isleri: oku, kaydet, listele."""

import os
import shutil

from ..errors import AxsRuntimeError
from ..values import metin as _metin
from . import gomulu


def _yol(y, ad):
    ad = _metin(ad)
    if os.path.isabs(ad):
        return ad
    return os.path.join(y.kok, ad)


@gomulu("read", "oku", yorumlayici=True)
def oku(y, dosya, varsayilan=None):
    yol = _yol(y, dosya)
    if not os.path.isfile(yol):
        if varsayilan is not None:
            return varsayilan
        raise AxsRuntimeError("Dosya bulunamadi: %s" % _metin(dosya))
    from ..okuma import dosya_oku
    return dosya_oku(yol)


@gomulu("save", "kaydet", yorumlayici=True)
def kaydet(y, dosya, icerik=""):
    yol = _yol(y, dosya)
    klasor = os.path.dirname(yol)
    if klasor and not os.path.isdir(klasor):
        os.makedirs(klasor, exist_ok=True)
    with open(yol, "w", encoding="utf-8") as f:
        f.write(_metin(icerik))
    return True


@gomulu("append", "dosya_ekle", yorumlayici=True)
def dosya_ekle(y, dosya, icerik=""):
    with open(_yol(y, dosya), "a", encoding="utf-8") as f:
        f.write(_metin(icerik))
    return True


@gomulu("file_exists", "dosya_var", yorumlayici=True)
def dosya_var(y, dosya):
    return os.path.exists(_yol(y, dosya))


@gomulu("delete", "dosya_sil", yorumlayici=True)
def dosya_sil(y, dosya):
    yol = _yol(y, dosya)
    if os.path.isdir(yol):
        shutil.rmtree(yol)
        return True
    if os.path.isfile(yol):
        os.remove(yol)
        return True
    return False


@gomulu("files", "dosyalar", yorumlayici=True)
def dosyalar(y, klasor=".", desen=None):
    yol = _yol(y, klasor)
    if not os.path.isdir(yol):
        return []
    adlar = sorted(os.listdir(yol))
    if desen:
        import fnmatch
        adlar = [a for a in adlar if fnmatch.fnmatch(a, _metin(desen))]
    return adlar


@gomulu("folder", "klasor", yorumlayici=True)
def klasor(y, yol):
    os.makedirs(_yol(y, yol), exist_ok=True)
    return True


@gomulu("size", "boyut", yorumlayici=True)
def boyut(y, dosya):
    yol = _yol(y, dosya)
    return os.path.getsize(yol) if os.path.exists(yol) else 0
