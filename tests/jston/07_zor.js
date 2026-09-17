// dagitici atama
const [ilk, ikinci] = [10, 20];
const { ad, yas } = { ad: "Nyl", yas: 20 };
console.log(ilk, ikinci, ad, yas);

// yerinde siralama
const sayilar = [5, 1, 4, 2];
sayilar.sort((a, b) => a - b);
console.log(JSON.stringify(sayilar));
sayilar.sort((a, b) => b - a);
console.log(JSON.stringify(sayilar));

const kisiler = [{ ad: "b", yas: 30 }, { ad: "a", yas: 20 }];
kisiler.sort((x, y) => x.yas - y.yas);
console.log(JSON.stringify(kisiler.map(k => k.ad)));

// ic ice kapanis
function sayacYap() {
  let n = 0;
  return function () {
    n += 1;
    return n;
  };
}
const say = sayacYap();
say();
console.log(say());

// metin kacislari ve ozel karakterler
console.log("tirnak: \"x\"  yuzde: %  ters: \\  satir:");
console.log('tek tirnak', `sablon %`);

// nesne anahtarlari
const harita = { "iki kelime": 1, normal: 2, 3: "uc" };
console.log(harita["iki kelime"], harita.normal, harita[3]);

// cok satirli ok isi
const islet = (liste) => {
  let t = 0;
  for (const x of liste) {
    t += x;
  }
  return t;
};
console.log(islet([1, 2, 3]));

// zincirleme
console.log([1, 2, 3, 4].filter(x => x > 1).map(x => x * 10).join("+"));

// mantiksal
const bos = "";
console.log(bos || "varsayilan", 5 && 6, !bos);
