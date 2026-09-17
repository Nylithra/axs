function bol(a, b) {
  if (b === 0) {
    throw new Error("sifira bolme");
  }
  return a / b;
}

try {
  console.log(bol(10, 2));
  console.log(bol(1, 0));
} catch (e) {
  console.log("yakalandi");
}

function tur(n) {
  switch (n) {
    case 1:
      return "bir";
    case 2:
      return "iki";
    default:
      return "baska";
  }
}
console.log(tur(1), tur(2), tur(9));

const yas = 20;
console.log(yas >= 18 ? "yetiskin" : "cocuk");
console.log(0 || "varsayilan", "dolu" && "ikinci");

let x = null;
if (!x) {
  x = "atandi";
}
console.log(x);
