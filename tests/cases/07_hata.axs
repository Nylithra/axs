try
  hata("bilerek")
catch e
  print: yakalandi: e;
end

try
  x = 1 / 0
catch
  print: bolme hatasi: hata;
end

try
  print(yokdegisken)
catch mesaj
  print: mesaj;
end

# eski %ad% yazimi da calismaya devam eder
try
  print(%yokdegisken%)
catch mesaj
  print: mesaj;
end

try
  liste = [1]
  print(liste[5])
catch mesaj
  print: mesaj;
end

func guvenli_bol(a, b)
  try
    return a / b
  catch
    return 0
  end
end
print(guvenli_bol(10, 2), guvenli_bol(10, 0))

try
  print("ton" - 1)
catch mesaj
  print: mesaj;
end
print: devam ediyor
