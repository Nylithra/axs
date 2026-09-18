puan = 75
if puan >= 90
  print: AA
elif puan >= 70
  print: BB
else
  print: FF
end

if not puan == 0 and puan < 100
  print: gecerli puan
end

repeat 3
  print: selam
end

repeat 3 as n
  print: sira n;
end

toplam = 0
for s in [1, 2, 3, 4, 5]
  if s mod 2 == 0
    skip
  end
  if s > 4
    stop
  end
  toplam += s
end
print: tek toplam toplam;

for harf in "axs"
  print: harf harf;
end

for k, v in {a: 1, b: 2}
  print: k;=v;
end

i = 0
while i < 3
  i += 1
end
print: i i;

# ic ice
for x in [1, 2]
  for y in [10, 20]
    print: x;x%y% = (x * y);
  end
end
