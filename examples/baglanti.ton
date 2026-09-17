# Baglanti ornekleri: internet ve veritabani ayni kelimeyle -> connect()

# --- internet ---
api = connect(https://api.github.com)
print: GitHub'a baglandim: %(%api%.adres)%

# sonuc = %api%.get("/repos/nylithra/ton-language")
# print: Yildiz: %(%sonuc%.stargazers_count)%

# tek seferlik istek:
# print(get(https://api.lanux.online))

# --- veritabani ---
db = connect("kayitlar.db")
%db%.run("create table if not exists kisiler (ad text, yas int)")
%db%.run("delete from kisiler")
%db%.run("insert into kisiler values (?, ?)", ["Nyl", 20])
%db%.run("insert into kisiler values (?, ?)", ["Ton", 1])

print: Tablolar: %(%db%.tables())%
print: Kayitlar: %(%db%.all("select * from kisiler"))%
print: Tek kayit: %(%db%.one("select * from kisiler where ad = ?", ["Nyl"]))%
%db%.close()
delete("kayitlar.db")
