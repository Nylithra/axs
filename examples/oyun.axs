# Sayi tahmin oyunu.  Calistir: axs examples/oyun.axs

gizli = random(1, 20)
hak = 5

print: 1 ile 20 arasinda bir sayi tuttum. hak; hakkin var!

while hak > 0
  cevap = ask("Tahminin: ")
  tahmin = number(cevap, 0)
  hak -= 1

  if tahmin == gizli
    print: Bildin! Sayi gizli; idi.
    exit(0)
  elif tahmin < gizli
    print: Daha buyuk bir sayi dene. (hak; hak kaldi)
  else
    print: Daha kucuk bir sayi dene. (hak; hak kaldi)
  end
end

print: Haklarin bitti. Sayi gizli; idi.
