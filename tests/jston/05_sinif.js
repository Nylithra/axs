class Sayac {
  constructor(baslangic) {
    this.deger = baslangic;
    this.adim = 1;
  }
  arttir() {
    this.deger += this.adim;
    return this.deger;
  }
  goster() {
    return "sayac=" + this.deger;
  }
}

const s = new Sayac(10);
s.arttir();
s.arttir();
console.log(s.goster());
console.log(s.deger);

const t = new Sayac(0);
t.arttir();
console.log(t.deger, s.deger);
