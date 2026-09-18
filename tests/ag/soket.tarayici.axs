# Ayni soket arayuzu tarayici calisma zamaninda da calisir
s = connect(ws://127.0.0.1:8300/ws/bot)

hello = %s%.al(5)
print: hello op=%(%hello%.op)% aralik=%(%hello%.d.heartbeat_interval)%

%s%.yolla({op: 2, d: {token: "Bot X", intents: 1}})

hazir = %s%.al(5)
print: %(%hazir%.t)% -> %(%hazir%.d.user.username)%

mesaj = %s%.al(5)
print: %(%mesaj%.t)% -> %(%mesaj%.d.content)%

%s%.kapat()
print: acik=%(%s%.acik)%
