"""Axs dilinin hata turleri. Hata mesajlari Turkce ve sade tutulur."""


class AxsError(Exception):
    """Tum Axs hatalarinin atasi."""

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


class AxsSyntaxError(AxsError):
    baslik = "Yazim hatasi"


class AxsRuntimeError(AxsError):
    baslik = "Calisma hatasi"


class AxsNameError(AxsRuntimeError):
    baslik = "Bilinmeyen ad"


class AxsTypeError(AxsRuntimeError):
    baslik = "Tur hatasi"


class AxsUserError(AxsRuntimeError):
    """`hata("...")` ile kullanicinin kendi firlattigi hata."""

    baslik = "Hata"
