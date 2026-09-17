function selamla(ad, selam = "Merhaba") {
  return selam + ", " + ad + "!";
}
console.log(selamla("Nyl"));
console.log(selamla("TON", "Selam"));

function fakt(n) {
  if (n <= 1) return 1;
  return n * fakt(n - 1);
}
console.log(fakt(10));

const kare = (x) => x * x;
const carp = (a, b) => a * b;
console.log(kare(7), carp(6, 7));

const sayilar = [1, 2, 3, 4, 5];
console.log(JSON.stringify(sayilar.map(x => x * 2)));
console.log(JSON.stringify(sayilar.filter(x => x % 2 === 1)));
console.log(sayilar.reduce((t, x) => t + x, 0));
sayilar.forEach(function (x) { console.log("oge:", x); });

let sayac = 0;
function arttir() {
  sayac += 1;
  return sayac;
}
arttir();
arttir();
console.log("sayac", sayac);

function uygula(f, deger) {
  return f(deger);
}
console.log(uygula(kare, 9));
