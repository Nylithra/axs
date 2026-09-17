"""TON dilinin hata turleri. Hata mesajlari Turkce ve sade tutulur."""


class TonError(Exception):
    """Tum TON hatalarinin atasi."""

    baslik = "Hata"

    def __init__(self, mesaj, satir=None, dosya=None):
        super().__init__(mesaj)
        self.mesaj = mesaj
        self.satir = satir
        self.dosya = dosya

    def rapor(self):
        yer = ""
        if self.dosya:
            yer += self.dosya
        if self.satir:
            yer += (":" if yer else "") + str(self.satir)
        if yer:
            return "%s [%s]: %s" % (self.baslik, yer, self.mesaj)
        return "%s: %s" % (self.baslik, self.mesaj)

    def __str__(self):
        return self.rapor()


class TonSyntaxError(TonError):
    baslik = "Yazim hatasi"


class TonRuntimeError(TonError):
    baslik = "Calisma hatasi"


class TonNameError(TonRuntimeError):
    baslik = "Bilinmeyen ad"


class TonTypeError(TonRuntimeError):
    baslik = "Tur hatasi"


class TonUserError(TonRuntimeError):
    """`hata("...")` ile kullanicinin kendi firlattigi hata."""

    baslik = "Hata"
