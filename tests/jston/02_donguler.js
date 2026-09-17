let toplam = 0;
for (let i = 1; i <= 5; i++) {
  toplam += i;
}
console.log(toplam);

const liste = [10, 20, 30];
for (const x of liste) {
  console.log("oge", x);
}

const kisi = { ad: "Nyl", yas: 20 };
for (const k in kisi) {
  console.log(k, kisi[k]);
}

let i = 0;
while (i < 3) {
  i++;
}
console.log("while", i);

let j = 0;
do {
  j += 2;
} while (j < 5);
console.log("do", j);

for (let n = 0; n < 6; n++) {
  if (n % 2 === 0) continue;
  if (n > 4) break;
  console.log("tek", n);
}

for (let x = 1; x <= 2; x++) {
  for (let y = 1; y <= 2; y++) {
    console.log(x, y, x * y);
  }
}
