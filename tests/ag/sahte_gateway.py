#!/usr/bin/env python3
"""Sinama icin sahte Jubbio gateway'i (WebSocket).

Gercek protokolun ayni: Hello -> Identify -> READY -> olaylar -> heartbeat.
Sadece testlerde kullanilir; sifir bagimlilik.
"""

import base64
import hashlib
import json
import os
import socket
import struct
import sys
import threading

SIHIRLI = "258EAFA5-E914-47DA-95CA-C5AB0DC85B11"


def cerceve_yaz(sok, veri, tur=1):
    ham = veri.encode("utf-8") if isinstance(veri, str) else veri
    basluk = bytes([0x80 | tur])
    n = len(ham)
    if n < 126:
        basluk += bytes([n])
    elif n < 65536:
        basluk += bytes([126]) + struct.pack(">H", n)
    else:
        basluk += bytes([127]) + struct.pack(">Q", n)
    sok.sendall(basluk + ham)


def cerceve_oku(sok):
    basluk = b""
    while len(basluk) < 2:
        parca = sok.recv(2 - len(basluk))
        if not parca:
            return None, None
        basluk += parca
    tur = basluk[0] & 0x0F
    maskeli = basluk[1] & 0x80
    n = basluk[1] & 0x7F
    if n == 126:
        n = struct.unpack(">H", sok.recv(2))[0]
    elif n == 127:
        n = struct.unpack(">Q", sok.recv(8))[0]
    maske = sok.recv(4) if maskeli else None
    veri = b""
    while len(veri) < n:
        parca = sok.recv(n - len(veri))
        if not parca:
            return None, None
        veri += parca
    if maske:
        veri = bytes(c ^ maske[i % 4] for i, c in enumerate(veri))
    return tur, veri


def oturum(baglanti, kayit):
    istek = b""
    while b"\r\n\r\n" not in istek:
        parca = baglanti.recv(4096)
        if not parca:
            return
        istek += parca
    anahtar = ""
    for satir in istek.decode("latin-1").split("\r\n"):
        if satir.lower().startswith("sec-websocket-key:"):
            anahtar = satir.split(":", 1)[1].strip()
    kabul = base64.b64encode(
        hashlib.sha1((anahtar + SIHIRLI).encode()).digest()).decode()
    baglanti.sendall((
        "HTTP/1.1 101 Switching Protocols\r\n"
        "Upgrade: websocket\r\nConnection: Upgrade\r\n"
        "Sec-WebSocket-Accept: %s\r\n\r\n" % kabul).encode())

    cerceve_yaz(baglanti, json.dumps({"op": 10, "d": {"heartbeat_interval": 800}}))

    while True:
        tur, veri = cerceve_oku(baglanti)
        if tur is None or tur == 8:
            break
        try:
            gelen = json.loads(veri.decode("utf-8"))
        except ValueError:
            continue
        if gelen.get("op") == 2:
            kayit.append(("identify", gelen["d"]))
            cerceve_yaz(baglanti, json.dumps({
                "op": 0, "s": 1, "t": "READY",
                "d": {"session_id": "OTURUM1",
                      "user": {"id": 1, "username": "axs_bot"},
                      "application": {"id": os.environ.get("SAHTE_UYGULAMA", "UYG1")}}}))
            # tek cercevede birden cok olay: sunucunun yaptigi gibi
            icerikler = json.loads(os.environ.get("SAHTE_MESAJLAR", '["!selam", "!zar"]'))
            paketler = []
            for i, icerik in enumerate(icerikler):
                paketler.append(json.dumps({
                    "op": 0, "s": 2 + i, "t": "MESSAGE_CREATE",
                    "d": {"id": 100 + i, "content": icerik, "guild_id": 7,
                          "channel_id": 9,
                          "author": {"id": 42, "username": "nyl", "bot": False}}}))
            if paketler:
                cerceve_yaz(baglanti, "\n".join(paketler))
            # etkilesimler: komut (2), dugme/menu (3), form (5)
            uye = json.loads(os.environ.get(
                "SAHTE_UYE",
                '{"user": {"id": 42, "username": "nyl"}, "permissions": "8", '
                '"roles": []}'))
            for i, ham in enumerate(json.loads(os.environ.get("SAHTE_KOMUTLAR", "[]"))):
                ham = dict(ham)
                etkilesim_turu = ham.pop("_t", 2)
                cerceve_yaz(baglanti, json.dumps({
                    "op": 0, "s": 50 + i, "t": "INTERACTION_CREATE",
                    "d": {"id": 500 + i, "token": "TKN%d" % i,
                          "type": etkilesim_turu,
                          "guild_id": 7, "channel_id": 9,
                          "member": uye, "data": ham}}))
            cerceve_yaz(baglanti, json.dumps({
                "op": 0, "s": 4, "t": "GUILD_MEMBER_ADD",
                "d": {"guild_id": 7, "user": {"id": 43, "username": "yeni"}}}))
        elif gelen.get("op") == 1:
            kayit.append(("heartbeat", gelen.get("d")))
            cerceve_yaz(baglanti, json.dumps({"op": 11}))
    baglanti.close()


def calistir(port):
    kayit = []
    s = socket.socket()
    s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    s.bind(("127.0.0.1", port))
    s.listen(2)
    print("hazir", flush=True)
    while True:
        baglanti, _ = s.accept()
        threading.Thread(target=oturum, args=(baglanti, kayit), daemon=True).start()


if __name__ == "__main__":
    calistir(int(sys.argv[1]) if len(sys.argv) > 1 else 8188)
