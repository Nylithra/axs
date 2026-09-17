const l = [10, 20, 30];
l.forEach((x, i) => console.log(i, x));
console.log(JSON.stringify(l.map((x, i) => x + i)));

const nesne = {
  ad: "TON",
  selam() { return "merhaba " + this.ad; }
};
console.log(nesne.selam());

let a, b;
a = b = 5;
console.log(a, b);

const kutu = { sayi: 1 };
kutu.sayi += 4;
console.log(kutu.sayi);

function ilkArti(liste) {
  for (const x of liste) {
    if (x > 0) return x;
  }
  return -1;
}
console.log(ilkArti([-1, -2, 7, 9]));

const puan = 85;
console.log(puan >= 90 ? "AA" : puan >= 80 ? "BA" : "CC");
