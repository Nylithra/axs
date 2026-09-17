const liste = [3, 1, 2];
liste.push(4);
console.log(JSON.stringify(liste));
console.log(liste.length, liste.indexOf(2), liste.includes(9));
console.log(JSON.stringify(liste.slice(1, 3)));
console.log(JSON.stringify(liste.concat([9])));
console.log(JSON.stringify(liste.reverse()));
console.log(liste.pop(), JSON.stringify(liste));

const kisi = { ad: "Nyl", yas: 20, diller: ["ton", "tnl"] };
console.log(kisi.ad, kisi["yas"], kisi.diller[0]);
kisi.sehir = "Ankara";
console.log(JSON.stringify(Object.keys(kisi)));
console.log(JSON.stringify(Object.values(kisi)));
console.log(JSON.stringify(kisi));

const metin = JSON.stringify({ x: 1, y: [2, 3] });
const geri = JSON.parse(metin);
console.log(metin, geri.y[1]);

const kisiler = [
  { ad: "a", yas: 30 },
  { ad: "b", yas: 20 }
];
console.log(JSON.stringify(kisiler.map(k => k.ad)));
console.log(kisiler.map(k => k.yas).reduce((t, y) => t + y, 0));
