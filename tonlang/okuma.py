"""Dosya okuma: Windows'tan gelen dosyalar da sorunsuz acilsin.

Not Defteri dosyanin basina gorunmez bir BOM isareti koyar ve satir sonlarini
CRLF yapar; Excel'in verdigi CSV'lerde de BOM vardir. Burasi hepsini temizler.
"""

KODLAMALAR = ("utf-8-sig", "cp1254", "latin-1")


def metne_cevir(ham, satirlari_duzelt=True):
    """Ham baytlari metne cevirir; kodlamayi kendi bulur."""
    for kodlama in KODLAMALAR:
        try:
            metin = ham.decode(kodlama)
            break
        except UnicodeDecodeError:
            continue
    else:
        metin = ham.decode("utf-8", "replace")
    if metin.startswith("﻿"):
        metin = metin[1:]
    if satirlari_duzelt:
        metin = metin.replace("\r\n", "\n").replace("\r", "\n")
    return metin


def dosya_oku(yol, satirlari_duzelt=True):
    """Bir dosyayi guvenle okur (BOM ve CRLF temizlenir)."""
    with open(yol, "rb") as f:
        return metne_cevir(f.read(), satirlari_duzelt)
