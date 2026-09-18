klasor("_gecici")
save("_gecici/not.txt", "birinci satir\n")
append("_gecici/not.txt", "ikinci satir\n")
print(read("_gecici/not.txt").trim().split("\n"))
print(file_exists("_gecici/not.txt"), file_exists("_gecici/yok.txt"))
print(read("_gecici/yok.txt", "varsayilan icerik"))
print(files("_gecici"))
print(size("_gecici/not.txt") > 0)

veri = {ad: "Nyl", diller: ["axs", "nyl"]}
save("_gecici/veri.json", tojson(veri))
geri = json(read("_gecici/veri.json"))
print(geri.ad, geri.diller[1])
print(tojson([1, 2]))

delete("_gecici")
print(file_exists("_gecici"))
