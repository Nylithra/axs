/*!
 * ton.js - TON dilinin tarayici calisma zamani
 * Derlenmis TON kodu bu dosyadaki `TON` nesnesini kullanir.
 * Ek hicbir kutuphane gerekmez.
 */
(function (global) {
  "use strict";

  var T = {};
  var HAZIR = Object.create(null);
  var YONTEMLER = { metin: {}, liste: {}, harita: {}, gorev: {}, sayi: {}, ondalik: {} };

  T.surum = "1.0.0";
  T.ai_adres = "/api/ai";

  // ------------------------------------------------------------------ hata
  function TonHata(mesaj) {
    var e = new Error(mesaj);
    e.ton = true;
    e.mesaj = mesaj;
    return e;
  }
  T.hata_at = function (mesaj) { throw TonHata(mesaj); };
  T.hata_metni = function (e) {
    if (!e) return "bilinmeyen hata";
    return e.mesaj || e.message || String(e);
  };
  T.eksik = function (is_adi, parametre) {
    throw TonHata("'" + is_adi + "' icin '" + parametre + "' degeri verilmedi");
  };

  // ------------------------------------------------------------------ turler
  function sayi_mi(v) { return typeof v === "number" && !isNaN(v); }
  function harita_mi(v) {
    return v !== null && typeof v === "object" && !Array.isArray(v) && !v.__is && !v.__gorev;
  }

  T.tur = function (v) {
    if (v === null || v === undefined) return "null";
    if (typeof v === "boolean") return "bool";
    if (typeof v === "number") return Number.isInteger(v) ? "sayi" : "ondalik";
    if (typeof v === "string") return "metin";
    if (Array.isArray(v)) return "liste";
    if (typeof v === "function") return "is";
    if (v.__gorev) return "gorev";
    return "harita";
  };

  T.dogru_mu = function (v) {
    if (v === null || v === undefined || v === false) return false;
    if (v === true) return true;
    if (typeof v === "number") return v !== 0 && !isNaN(v);
    if (typeof v === "string") return v.length > 0;
    if (Array.isArray(v)) return v.length > 0;
    if (typeof v === "function") return true;
    return Object.keys(v).length > 0;
  };

  T.metin = function (v) {
    if (v === null || v === undefined) return "null";
    if (v === true) return "true";
    if (v === false) return "false";
    if (typeof v === "number") {
      if (!isFinite(v)) return isNaN(v) ? "NaN" : (v > 0 ? "sonsuz" : "-sonsuz");
      if (Number.isInteger(v)) return String(v);
      return String(parseFloat(v.toFixed(12)));
    }
    if (typeof v === "string") return v;
    if (Array.isArray(v)) return "[" + v.map(T.gosterim).join(", ") + "]";
    if (typeof v === "function") return "<is " + (v.__ad || "isimsiz") + ">";
    if (v.__gorev) return "<gorev" + (v.bitti ? " bitti" : " calisiyor") + ">";
    return "{" + Object.keys(v).map(function (k) {
      return k + ": " + T.gosterim(v[k]);
    }).join(", ") + "}";
  };

  T.gosterim = function (v) {
    if (typeof v === "string") return '"' + v.replace(/"/g, '\\"') + '"';
    return T.metin(v);
  };

  T.harita = function (ciftler) {
    var h = {};
    for (var i = 0; i < ciftler.length; i++) {
      var a = ciftler[i][0];
      h[typeof a === "string" ? a : T.metin(a)] = ciftler[i][1];
    }
    return h;
  };

  T.is = function (fn, ad, adlar) {
    fn.__is = true;
    fn.__ad = ad;
    fn.__adlar = adlar || [];
    return fn;
  };

  // ------------------------------------------------------------------ islemler
  function sayi_iste(islec, a, b) {
    if (!sayi_mi(a) || !sayi_mi(b)) {
      throw TonHata("'" + islec + "' islemi " + T.tur(a) + " ile " + T.tur(b) +
                    " arasinda yapilamaz");
    }
  }

  T.topla = function (a, b) {
    if (typeof a === "string" || typeof b === "string") return T.metin(a) + T.metin(b);
    if (Array.isArray(a) && Array.isArray(b)) return a.concat(b);
    if (harita_mi(a) && harita_mi(b)) return Object.assign({}, a, b);
    sayi_iste("+", a, b);
    return a + b;
  };
  T.cikar = function (a, b) { sayi_iste("-", a, b); return a - b; };
  T.carp = function (a, b) {
    if (typeof a === "string" && sayi_mi(b)) return a.repeat(Math.max(0, Math.floor(b)));
    if (Array.isArray(a) && sayi_mi(b)) {
      var c = []; for (var i = 0; i < Math.floor(b); i++) c = c.concat(a); return c;
    }
    sayi_iste("*", a, b);
    return a * b;
  };
  T.bol = function (a, b) {
    sayi_iste("/", a, b);
    if (b === 0) throw TonHata("Sifira bolunemez");
    return a / b;
  };
  T.kalan = function (a, b) {
    sayi_iste("mod", a, b);
    if (b === 0) throw TonHata("Sifira bolunemez");
    return a % b;
  };
  T.us = function (a, b) { sayi_iste("^", a, b); return Math.pow(a, b); };
  T.eksi = function (a) {
    if (!sayi_mi(a)) throw TonHata("'-' sadece sayilarda kullanilir");
    return -a;
  };

  function esit(a, b) {
    if (a === null || a === undefined) return b === null || b === undefined;
    if (sayi_mi(a) && sayi_mi(b)) return a === b;
    if (T.tur(a) !== T.tur(b)) return false;
    if (Array.isArray(a)) {
      if (a.length !== b.length) return false;
      for (var i = 0; i < a.length; i++) if (!esit(a[i], b[i])) return false;
      return true;
    }
    if (harita_mi(a)) {
      var ka = Object.keys(a), kb = Object.keys(b);
      if (ka.length !== kb.length) return false;
      for (var j = 0; j < ka.length; j++) if (!esit(a[ka[j]], b[ka[j]])) return false;
      return true;
    }
    return a === b;
  }
  T.esit = esit;
  T.esit_degil = function (a, b) { return !esit(a, b); };

  function sirala_cifti(a, b) {
    if (typeof a === "string" && typeof b === "string") return [a, b];
    if (sayi_mi(a) && sayi_mi(b)) return [a, b];
    if ((Array.isArray(a) || harita_mi(a)) && (Array.isArray(b) || harita_mi(b))) {
      return [uzunluk(a), uzunluk(b)];
    }
    throw TonHata(T.tur(a) + " ile " + T.tur(b) + " karsilastirilamaz");
  }
  T.kucuk = function (a, b) { var p = sirala_cifti(a, b); return p[0] < p[1]; };
  T.buyuk = function (a, b) { var p = sirala_cifti(a, b); return p[0] > p[1]; };
  T.kucuk_esit = function (a, b) { var p = sirala_cifti(a, b); return p[0] <= p[1]; };
  T.buyuk_esit = function (a, b) { var p = sirala_cifti(a, b); return p[0] >= p[1]; };

  // ------------------------------------------------------------------ erisim
  T.dizin = function (nesne, anahtar) {
    if (nesne === null || nesne === undefined) {
      throw TonHata("null icinde sira ile erisim yok");
    }
    if (typeof nesne === "string" || Array.isArray(nesne)) {
      if (!sayi_mi(anahtar)) {
        throw TonHata("Sira numarasi sayi olmali, " + T.tur(anahtar) + " verildi");
      }
      var i = Math.floor(anahtar);
      if (i < 0) i += nesne.length;
      if (i < 0 || i >= nesne.length) {
        throw TonHata(T.tur(nesne) + " icinde " + T.metin(anahtar) + ". sira yok (uzunluk " +
                      nesne.length + ")");
      }
      return nesne[i];
    }
    if (harita_mi(nesne)) {
      var k = typeof anahtar === "string" ? anahtar : T.metin(anahtar);
      return Object.prototype.hasOwnProperty.call(nesne, k) ? nesne[k] : null;
    }
    throw TonHata(T.tur(nesne) + " icinde sira ile erisim yok");
  };

  T.ata_dizin = function (nesne, anahtar, deger) {
    if (Array.isArray(nesne)) {
      var i = Math.floor(anahtar);
      if (i < 0) i += nesne.length;
      if (i < 0 || i >= nesne.length) {
        throw TonHata("Liste disinda sira: " + T.metin(anahtar));
      }
      nesne[i] = deger;
      return deger;
    }
    if (harita_mi(nesne)) {
      nesne[typeof anahtar === "string" ? anahtar : T.metin(anahtar)] = deger;
      return deger;
    }
    throw TonHata(T.tur(nesne) + " icine deger konulamaz");
  };

  T.uye = function (nesne, ad) {
    var t = T.tur(nesne);
    var tablo = YONTEMLER[t];
    if (tablo && tablo[ad]) return bagla(tablo[ad], nesne, ad);
    if (harita_mi(nesne)) {
      return Object.prototype.hasOwnProperty.call(nesne, ad) ? nesne[ad] : null;
    }
    if (nesne && nesne.__gorev) {
      if (ad === "bitti") return nesne.bitti;
      if (ad === "sonuc") return nesne.sozu;
    }
    throw TonHata(t + " uzerinde '" + ad + "' yok");
  };

  T.ata_uye = function (nesne, ad, deger) {
    if (harita_mi(nesne)) { nesne[ad] = deger; return deger; }
    throw TonHata(T.tur(nesne) + " uzerine '" + ad + "' yazilamaz");
  };

  function bagla(fn, nesne, ad) {
    var b = function () {
      var args = Array.prototype.slice.call(arguments);
      return fn.apply(null, [nesne].concat(args));
    };
    b.__ad = ad;
    b.__adlar = (fn.__adlar || []).slice(1);
    return b;
  }

  // ------------------------------------------------------------------ cagri
  T.h = function (ad) {
    var f = HAZIR[ad];
    if (!f) throw TonHata("'" + ad + "' adinda bir is yok (tarayici surumu)");
    return f;
  };

  T.cagir = async function (hedef, args, isimli) {
    if (typeof hedef !== "function") {
      throw TonHata(T.tur(hedef) + " cagrilamaz");
    }
    args = args || [];
    if (isimli) {
      var adlar = hedef.__adlar || [];
      var yeni = args.slice();
      for (var ad in isimli) {
        var yer = adlar.indexOf(ad);
        if (yer < 0) {
          throw TonHata("'" + (hedef.__ad || "is") + "' boyle bir deger almiyor: " + ad);
        }
        while (yeni.length < yer) yeni.push(undefined);
        yeni[yer] = isimli[ad];
      }
      args = yeni;
    }
    if (hedef.__is && args.length > (hedef.__adlar || []).length) {
      throw TonHata("'" + hedef.__ad + "' en fazla " + hedef.__adlar.length +
                    " deger alir, " + args.length + " verildi");
    }
    return await hedef.apply(null, args);
  };

  T.gezinti = function (kaynak) {
    if (Array.isArray(kaynak)) return kaynak;
    if (typeof kaynak === "string") return kaynak.split("");
    if (harita_mi(kaynak)) {
      return Object.keys(kaynak).map(function (k) { return [k, kaynak[k]]; });
    }
    throw TonHata("'for' listede, haritada ya da metinde gezer; " + T.tur(kaynak) +
                  " verildi");
  };

  T.tekrar = function (n) {
    if (!sayi_mi(n)) throw TonHata("'repeat' bir sayi ister, " + T.tur(n) + " verildi");
    return Math.floor(n);
  };

  // ------------------------------------------------------------------ kayit
  function kaydet(adlar, parametreler, fn) {
    fn.__adlar = parametreler;
    fn.__ad = adlar[0];
    for (var i = 0; i < adlar.length; i++) HAZIR[adlar[i]] = fn;
    return fn;
  }

  function yontem(turler, adlar, parametreler, fn) {
    fn.__adlar = parametreler;
    for (var i = 0; i < turler.length; i++) {
      for (var j = 0; j < adlar.length; j++) YONTEMLER[turler[i]][adlar[j]] = fn;
    }
    return fn;
  }

  function hem(turler, adlar, parametreler, fn) {
    kaydet(adlar, parametreler, fn);
    yontem(turler, adlar, parametreler, fn);
    return fn;
  }

  function m(v) { return typeof v === "string" ? v : T.metin(v); }
  function uzunluk(v) {
    if (v === null || v === undefined) return 0;
    if (typeof v === "string" || Array.isArray(v)) return v.length;
    if (harita_mi(v)) return Object.keys(v).length;
    throw TonHata(T.tur(v) + " icin uzunluk yok");
  }
  function liste_iste(v, ad) {
    if (Array.isArray(v)) return v;
    if (typeof v === "string") return v.split("");
    if (harita_mi(v)) return Object.keys(v);
    throw TonHata(ad + " bir liste ister, " + T.tur(v) + " verildi");
  }

  // ------------------------------------------------------------------ yazdirma
  T.cikti_ogesi = null;

  function ciktiya_yaz(metin) {
    if (typeof document !== "undefined") {
      var hedef = T.cikti_ogesi ||
        document.getElementById("ton-cikti") ||
        document.querySelector("[data-ton-cikti]");
      if (hedef) {
        hedef.textContent += metin;
        hedef.scrollTop = hedef.scrollHeight;
      }
    }
  }

  kaydet(["print", "yaz", "say", "goster"], ["deger"], function () {
    var parcalar = Array.prototype.map.call(arguments, T.metin).join(" ");
    if (typeof console !== "undefined") console.log(parcalar);
    ciktiya_yaz(parcalar + "\n");
    return null;
  });

  kaydet(["write", "yazdir"], ["deger"], function () {
    var parcalar = Array.prototype.map.call(arguments, T.metin).join("");
    ciktiya_yaz(parcalar);
    return null;
  });

  kaydet(["konsol", "console"], ["deger"], function () {
    if (typeof console !== "undefined") console.log.apply(console, arguments);
    return null;
  });

  // ------------------------------------------------------------------ cekirdek
  hem(["metin", "liste", "harita"], ["len", "uzunluk", "say_adet"], ["deger"], uzunluk);
  hem(["metin", "liste", "harita", "sayi", "ondalik", "gorev"], ["type", "tur"], ["deger"],
      function (v) { return T.tur(v); });

  kaydet(["text", "metin", "str"], ["deger", "basamak"], function (v, basamak) {
    if (basamak !== undefined && basamak !== null && sayi_mi(v)) {
      return v.toFixed(Math.floor(basamak));
    }
    return T.metin(v);
  });

  kaydet(["number", "sayi", "num"], ["deger", "varsayilan"], function (v, varsayilan) {
    if (sayi_mi(v)) return v;
    if (typeof v === "boolean") return v ? 1 : 0;
    if (typeof v === "string") {
      var ham = v.trim().replace(",", ".");
      if (ham !== "" && !isNaN(Number(ham))) return Number(ham);
    }
    if (varsayilan !== undefined && varsayilan !== null) return varsayilan;
    throw TonHata("'" + T.metin(v) + "' sayiya cevrilemedi");
  });

  kaydet(["int", "tam"], ["deger"], function (v) {
    return Math.trunc(HAZIR["number"](v));
  });
  kaydet(["bool", "mantik"], ["deger"], function (v) { return T.dogru_mu(v); });
  kaydet(["liste", "tolist"], ["deger"], function (v) {
    if (v === undefined || v === null) return [];
    if (Array.isArray(v)) return v.slice();
    if (typeof v === "string") return v.split("");
    if (harita_mi(v)) return Object.keys(v);
    return [v];
  });
  kaydet(["harita", "tomap"], ["deger"], function (v) {
    if (harita_mi(v)) return Object.assign({}, v);
    if (Array.isArray(v)) {
      var h = {};
      v.forEach(function (o) { if (Array.isArray(o) && o.length === 2) h[m(o[0])] = o[1]; });
      return h;
    }
    return {};
  });
  hem(["liste", "harita"], ["copy", "kopya"], ["deger"], function (v) {
    if (Array.isArray(v)) return v.slice();
    if (harita_mi(v)) return Object.assign({}, v);
    return v;
  });
  kaydet(["is_empty", "bos_mu"], ["deger"], function (v) { return !T.dogru_mu(v); });
  kaydet(["error", "hata"], ["mesaj"], function (mesaj) {
    throw TonHata(T.metin(mesaj === undefined ? "Hata" : mesaj));
  });
  kaydet(["exit", "cik"], ["kod"], function () { throw TonHata("__ton_cik__"); });
  kaydet(["show", "gosterimi"], ["deger"], function (v) { return T.gosterim(v); });

  kaydet(["json", "jsonoku"], ["metin"], function (ham) {
    if (typeof ham !== "string") return ham;
    try { return JSON.parse(ham); } catch (e) {
      throw TonHata("JSON okunamadi: " + e.message);
    }
  });
  hem(["liste", "harita", "metin"], ["tojson", "jsonyaz"], ["deger", "guzel"],
      function (v, guzel) {
        return JSON.stringify(v, null, T.dogru_mu(guzel) ? 2 : 0);
      });

  kaydet(["now", "simdi"], ["bicim"], function () {
    var a = new Date();
    var iki = function (n) { return String(n).padStart(2, "0"); };
    return {
      yil: a.getFullYear(), ay: a.getMonth() + 1, gun: a.getDate(),
      saat: a.getHours(), dakika: a.getMinutes(), saniye: a.getSeconds(),
      metin: a.getFullYear() + "-" + iki(a.getMonth() + 1) + "-" + iki(a.getDate()) + " " +
             iki(a.getHours()) + ":" + iki(a.getMinutes()) + ":" + iki(a.getSeconds()),
      zaman: Date.now() / 1000
    };
  });
  kaydet(["timestamp", "zaman"], [], function () { return Date.now() / 1000; });
  kaydet(["random", "rastgele"], ["alt", "ust"], function (alt, ust) {
    if (alt === undefined) return Math.random();
    if (ust === undefined) { ust = alt; alt = 1; }
    if (Number.isInteger(alt) && Number.isInteger(ust)) {
      return Math.floor(Math.random() * (ust - alt + 1)) + alt;
    }
    return Math.random() * (ust - alt) + alt;
  });
  kaydet(["pick", "sec_rastgele"], ["liste"], function (l) {
    var ogeler = liste_iste(l, "sec_rastgele()");
    if (!ogeler.length) throw TonHata("Bos listeden secim yapilamaz");
    return ogeler[Math.floor(Math.random() * ogeler.length)];
  });
  kaydet(["shuffle", "karistir"], ["liste"], function (l) {
    var y = liste_iste(l, "karistir()").slice();
    for (var i = y.length - 1; i > 0; i--) {
      var j = Math.floor(Math.random() * (i + 1));
      var g = y[i]; y[i] = y[j]; y[j] = g;
    }
    return y;
  });

  // ------------------------------------------------------------------ metin
  hem(["metin"], ["upper", "buyuk"], ["metin"], function (s) { return m(s).toUpperCase(); });
  hem(["metin"], ["lower", "kucuk"], ["metin"], function (s) { return m(s).toLowerCase(); });
  hem(["metin"], ["trim", "kirp"], ["metin", "karakterler"], function (s) {
    return m(s).trim();
  });
  hem(["metin"], ["title", "basharf"], ["metin"], function (s) {
    return m(s).split(" ").map(function (p) {
      return p ? p[0].toUpperCase() + p.slice(1) : p;
    }).join(" ");
  });
  hem(["metin"], ["split", "ayir"], ["metin", "ayirac", "adet"], function (s, ayirac) {
    if (ayirac === undefined || ayirac === null) return m(s).split(/\s+/).filter(Boolean);
    return m(s).split(m(ayirac));
  });
  hem(["liste", "metin"], ["join", "birlestir"], ["ogeler", "ayirac"],
      function (ogeler, ayirac) {
        if (typeof ogeler === "string") { var g = ogeler; ogeler = ayirac; ayirac = g; }
        return liste_iste(ogeler, "birlestir()").map(T.metin).join(m(ayirac || ""));
      });
  hem(["metin"], ["replace", "degistir"], ["metin", "eski", "yeni"],
      function (s, eski, yeni) {
        return m(s).split(m(eski)).join(m(yeni === undefined ? "" : yeni));
      });
  hem(["metin", "liste", "harita"], ["contains", "icerir"], ["kap", "parca"],
      function (kap, parca) {
        if (typeof kap === "string") return kap.indexOf(m(parca)) >= 0;
        if (harita_mi(kap)) return Object.prototype.hasOwnProperty.call(kap, m(parca));
        return liste_iste(kap, "icerir()").some(function (o) { return esit(o, parca); });
      });
  hem(["metin"], ["starts", "ile_baslar"], ["metin", "parca"], function (s, p) {
    return m(s).startsWith(m(p));
  });
  hem(["metin"], ["ends", "ile_biter"], ["metin", "parca"], function (s, p) {
    return m(s).endsWith(m(p));
  });
  hem(["metin", "liste"], ["find", "bul"], ["kap", "parca"], function (kap, parca) {
    if (typeof kap === "string") return kap.indexOf(m(parca));
    var l = liste_iste(kap, "bul()");
    for (var i = 0; i < l.length; i++) if (esit(l[i], parca)) return i;
    return -1;
  });
  hem(["metin", "liste"], ["slice", "kes"], ["kap", "bas", "son"], function (kap, bas, son) {
    bas = bas === undefined ? 0 : Math.floor(bas);
    return son === undefined || son === null ? kap.slice(bas) : kap.slice(bas, Math.floor(son));
  });
  hem(["metin", "liste"], ["reverse", "ters"], ["kap"], function (kap) {
    if (typeof kap === "string") return kap.split("").reverse().join("");
    return liste_iste(kap, "ters()").slice().reverse();
  });
  hem(["metin"], ["repeat_text", "tekrarla_metin"], ["metin", "adet"], function (s, n) {
    return m(s).repeat(Math.max(0, Math.floor(n)));
  });
  hem(["metin"], ["lines", "satirlar"], ["metin"], function (s) {
    return m(s).split(/\r?\n/);
  });
  hem(["metin", "liste"], ["count", "adet"], ["kap", "parca"], function (kap, parca) {
    if (typeof kap === "string") return kap.split(m(parca)).length - 1;
    return liste_iste(kap, "adet()").filter(function (o) { return esit(o, parca); }).length;
  });
  hem(["metin"], ["pad", "doldur"], ["metin", "uzunluk", "karakter", "sag"],
      function (s, u, karakter, sag) {
        var k = m(karakter === undefined ? " " : karakter).slice(0, 1) || " ";
        u = Math.floor(u);
        return (sag === false) ? m(s).padStart(u, k) : m(s).padEnd(u, k);
      });
  hem(["metin"], ["match", "esles"], ["metin", "desen"], function (s, desen) {
    var r = new RegExp(m(desen));
    var e = r.exec(m(s));
    if (!e) return null;
    return e.length > 1 ? e.slice(1) : e[0];
  });
  hem(["metin"], ["matches", "eslesenler"], ["metin", "desen"], function (s, desen) {
    var r = new RegExp(m(desen), "g");
    return m(s).match(r) || [];
  });
  hem(["metin"], ["clean", "temizle"], ["metin"], function (s) {
    return m(s).split(/\s+/).filter(Boolean).join(" ");
  });
  kaydet(["chars", "karakterler"], ["metin"], function (s) { return m(s).split(""); });
  kaydet(["code", "kod"], ["karakter"], function (s) { return m(s).charCodeAt(0); });
  kaydet(["char", "karakter"], ["sayi"], function (n) {
    return String.fromCharCode(Math.floor(n));
  });

  // ------------------------------------------------------------------ liste
  hem(["liste"], ["push", "ekle"], ["liste", "deger"], function (l) {
    if (!Array.isArray(l)) throw TonHata("ekle() bir liste ister, " + T.tur(l) + " verildi");
    for (var i = 1; i < arguments.length; i++) l.push(arguments[i]);
    return l;
  });
  hem(["liste"], ["pop", "cikar_son"], ["liste", "sira"], function (l, sira) {
    if (!l.length) return null;
    return sira === undefined || sira === null ? l.pop() : l.splice(Math.floor(sira), 1)[0];
  });
  hem(["liste"], ["insert", "araya_ekle"], ["liste", "sira", "deger"],
      function (l, sira, deger) { l.splice(Math.floor(sira), 0, deger); return l; });
  hem(["liste", "harita"], ["remove", "sil"], ["kap", "anahtar"], function (kap, anahtar) {
    if (harita_mi(kap)) { delete kap[m(anahtar)]; return kap; }
    for (var i = 0; i < kap.length; i++) {
      if (esit(kap[i], anahtar)) { kap.splice(i, 1); break; }
    }
    return kap;
  });
  hem(["liste", "harita", "metin"], ["first", "ilk"], ["kap", "adet"], function (kap, adet) {
    var l = liste_iste(kap, "ilk()");
    if (adet === undefined || adet === null) return l.length ? l[0] : null;
    return l.slice(0, Math.floor(adet));
  });
  hem(["liste", "harita", "metin"], ["last", "son_oge"], ["kap", "adet"],
      function (kap, adet) {
        var l = liste_iste(kap, "son_oge()");
        if (adet === undefined || adet === null) return l.length ? l[l.length - 1] : null;
        return l.slice(-Math.floor(adet));
      });
  hem(["liste"], ["unique", "benzersiz"], ["liste"], function (l) {
    var c = [];
    liste_iste(l, "benzersiz()").forEach(function (o) {
      if (!c.some(function (x) { return esit(x, o); })) c.push(o);
    });
    return c;
  });
  hem(["liste"], ["sum", "topla"], ["liste", "alan"], function (l, alan) {
    var t = 0;
    liste_iste(l, "topla()").forEach(function (o) {
      var d = (alan !== undefined && alan !== null && harita_mi(o)) ? o[m(alan)] : o;
      if (sayi_mi(d)) t += d;
    });
    return t;
  });
  hem(["liste"], ["avg", "ortalama"], ["liste", "alan"], function (l, alan) {
    var s = [];
    liste_iste(l, "ortalama()").forEach(function (o) {
      var d = (alan !== undefined && alan !== null && harita_mi(o)) ? o[m(alan)] : o;
      if (sayi_mi(d)) s.push(d);
    });
    if (!s.length) return 0;
    return s.reduce(function (a, b) { return a + b; }, 0) / s.length;
  });
  kaydet(["min", "enkucuk"], ["degerler"], function () {
    var l = yaygin(arguments);
    return l.length ? l.reduce(function (a, b) { return T.kucuk(b, a) ? b : a; }) : null;
  });
  kaydet(["max", "enbuyuk"], ["degerler"], function () {
    var l = yaygin(arguments);
    return l.length ? l.reduce(function (a, b) { return T.buyuk(b, a) ? b : a; }) : null;
  });
  function yaygin(args) {
    if (args.length === 1 && Array.isArray(args[0])) return args[0].slice();
    return Array.prototype.slice.call(args);
  }

  hem(["harita"], ["keys", "anahtarlar"], ["harita"], function (h) {
    if (!harita_mi(h)) throw TonHata("anahtarlar() bir harita ister");
    return Object.keys(h);
  });
  hem(["harita"], ["values", "degerler"], ["harita"], function (h) {
    if (!harita_mi(h)) throw TonHata("degerler() bir harita ister");
    return Object.keys(h).map(function (k) { return h[k]; });
  });
  hem(["harita"], ["items", "ciftler"], ["harita"], function (h) {
    return Object.keys(h).map(function (k) { return [k, h[k]]; });
  });
  hem(["harita"], ["has", "var_mi"], ["harita", "anahtar"], function (h, a) {
    return harita_mi(h) ? Object.prototype.hasOwnProperty.call(h, m(a))
                        : liste_iste(h, "var_mi()").some(function (o) { return esit(o, a); });
  });
  kaydet(["al"], ["harita", "anahtar", "varsayilan"], function (h, a, varsayilan) {
    var v = varsayilan === undefined ? null : varsayilan;
    if (harita_mi(h)) {
      return Object.prototype.hasOwnProperty.call(h, m(a)) ? h[m(a)] : v;
    }
    if (Array.isArray(h) || typeof h === "string") {
      var i = Math.floor(a);
      return (i >= -h.length && i < h.length) ? h[i < 0 ? i + h.length : i] : v;
    }
    return v;
  });
  yontem(["harita"], ["get", "al"], ["harita", "anahtar", "varsayilan"], HAZIR["al"]);
  hem(["harita"], ["set", "koy"], ["harita", "anahtar", "deger"], function (h, a, d) {
    h[m(a)] = d;
    return h;
  });
  hem(["harita", "liste"], ["merge", "kaynastir"], ["a", "b"], function (a, b) {
    if (harita_mi(a)) return Object.assign({}, a, b);
    return liste_iste(a, "kaynastir()").concat(liste_iste(b, "kaynastir()"));
  });
  kaydet(["range", "aralik"], ["bas", "son", "adim"], function (bas, son, adim) {
    if (son === undefined || son === null) { son = bas; bas = 1; }
    adim = adim === undefined || adim === null ? 1 : Math.floor(adim);
    if (adim === 0) throw TonHata("aralik adimi 0 olamaz");
    var c = [];
    if (adim > 0) { for (var i = bas; i <= son; i += adim) c.push(i); }
    else { for (var j = bas; j >= son; j += adim) c.push(j); }
    return c;
  });
  kaydet(["zip", "esle"], ["listeler"], function () {
    var listeler = Array.prototype.map.call(arguments, function (l) {
      return liste_iste(l, "esle()");
    });
    if (!listeler.length) return [];
    var n = Math.min.apply(null, listeler.map(function (l) { return l.length; }));
    var c = [];
    for (var i = 0; i < n; i++) {
      c.push(listeler.map(function (l) { return l[i]; }));
    }
    return c;
  });
  kaydet(["flat", "duzlestir"], ["liste"], function duz(l) {
    var c = [];
    liste_iste(l, "duzlestir()").forEach(function (o) {
      if (Array.isArray(o)) c = c.concat(duz(o)); else c.push(o);
    });
    return c;
  });

  hem(["liste"], ["map", "donustur"], ["liste", "is"], async function (l, is_) {
    var c = [], ogeler = liste_iste(l, "donustur()");
    for (var i = 0; i < ogeler.length; i++) c.push(await T.cagir(is_, [ogeler[i]]));
    return c;
  });
  hem(["liste"], ["filter", "sec"], ["liste", "is"], async function (l, is_) {
    var c = [], ogeler = liste_iste(l, "sec()");
    for (var i = 0; i < ogeler.length; i++) {
      if (T.dogru_mu(await T.cagir(is_, [ogeler[i]]))) c.push(ogeler[i]);
    }
    return c;
  });
  hem(["liste"], ["reduce", "indirge"], ["liste", "is", "baslangic"],
      async function (l, is_, baslangic) {
        var ogeler = liste_iste(l, "indirge()").slice(), toplam;
        if (baslangic === undefined || baslangic === null) {
          if (!ogeler.length) return null;
          toplam = ogeler.shift();
        } else { toplam = baslangic; }
        for (var i = 0; i < ogeler.length; i++) {
          toplam = await T.cagir(is_, [toplam, ogeler[i]]);
        }
        return toplam;
      });
  hem(["liste", "harita"], ["each", "hepsi"], ["kap", "is"], async function (kap, is_) {
    if (harita_mi(kap)) {
      var anahtarlar = Object.keys(kap);
      for (var i = 0; i < anahtarlar.length; i++) {
        await T.cagir(is_, [anahtarlar[i], kap[anahtarlar[i]]]);
      }
      return kap;
    }
    var ogeler = liste_iste(kap, "hepsi()");
    for (var j = 0; j < ogeler.length; j++) await T.cagir(is_, [ogeler[j]]);
    return kap;
  });
  hem(["liste"], ["sort", "sirala"], ["liste", "anahtar", "tersten"],
      async function (l, anahtar, tersten) {
        var ogeler = liste_iste(l, "sirala()").slice();
        var anahtarlar = [];
        for (var i = 0; i < ogeler.length; i++) {
          if (anahtar === undefined || anahtar === null) anahtarlar.push(ogeler[i]);
          else if (typeof anahtar === "string") {
            anahtarlar.push(harita_mi(ogeler[i]) ? ogeler[i][anahtar] : ogeler[i]);
          } else { anahtarlar.push(await T.cagir(anahtar, [ogeler[i]])); }
        }
        var cift = ogeler.map(function (o, i) { return [anahtarlar[i], o]; });
        cift.sort(function (a, b) {
          var x = a[0], y = b[0];
          if (sayi_mi(x) && sayi_mi(y)) return x - y;
          return T.metin(x) < T.metin(y) ? -1 : (T.metin(x) > T.metin(y) ? 1 : 0);
        });
        if (T.dogru_mu(tersten)) cift.reverse();
        return cift.map(function (c) { return c[1]; });
      });
  hem(["liste"], ["group", "grupla"], ["liste", "anahtar"], async function (l, anahtar) {
    var c = {}, ogeler = liste_iste(l, "grupla()");
    for (var i = 0; i < ogeler.length; i++) {
      var k;
      if (typeof anahtar === "string") {
        k = harita_mi(ogeler[i]) ? ogeler[i][anahtar] : ogeler[i];
      } else { k = await T.cagir(anahtar, [ogeler[i]]); }
      k = m(k);
      if (!c[k]) c[k] = [];
      c[k].push(ogeler[i]);
    }
    return c;
  });
  hem(["liste"], ["any", "herhangi"], ["liste", "is"], async function (l, is_) {
    var ogeler = liste_iste(l, "herhangi()");
    for (var i = 0; i < ogeler.length; i++) {
      var d = is_ ? await T.cagir(is_, [ogeler[i]]) : ogeler[i];
      if (T.dogru_mu(d)) return true;
    }
    return false;
  });
  hem(["liste"], ["all", "hepsi_dogru"], ["liste", "is"], async function (l, is_) {
    var ogeler = liste_iste(l, "hepsi_dogru()");
    for (var i = 0; i < ogeler.length; i++) {
      var d = is_ ? await T.cagir(is_, [ogeler[i]]) : ogeler[i];
      if (!T.dogru_mu(d)) return false;
    }
    return true;
  });

  // ------------------------------------------------------------------ matematik
  kaydet(["abs", "mutlak"], ["sayi"], function (x) { return Math.abs(x); });
  kaydet(["round", "yuvarla"], ["sayi", "basamak"], function (x, b) {
    b = b === undefined || b === null ? 0 : Math.floor(b);
    var k = Math.pow(10, b);
    var s = Math.round(x * k) / k;
    return b <= 0 ? Math.round(s) : s;
  });
  kaydet(["floor", "asagi"], ["sayi"], function (x) { return Math.floor(x); });
  kaydet(["ceil", "yukari"], ["sayi"], function (x) { return Math.ceil(x); });
  kaydet(["sqrt", "karekok"], ["sayi"], function (x) {
    if (x < 0) throw TonHata("Negatif sayinin karekoku alinamaz");
    return Math.sqrt(x);
  });
  kaydet(["pow", "us"], ["sayi", "us"], function (x, y) { return Math.pow(x, y); });
  kaydet(["sin"], ["sayi"], function (x) { return Math.sin(x); });
  kaydet(["cos"], ["sayi"], function (x) { return Math.cos(x); });
  kaydet(["tan"], ["sayi"], function (x) { return Math.tan(x); });
  kaydet(["log"], ["sayi", "taban"], function (x, taban) {
    return taban ? Math.log(x) / Math.log(taban) : Math.log(x);
  });
  kaydet(["pi"], [], function () { return Math.PI; });
  kaydet(["percent", "yuzde"], ["parca", "butun"], function (p, b) {
    return b === 0 ? 0 : p * 100 / b;
  });
  kaydet(["clamp", "sinirla"], ["sayi", "alt", "ust"], function (x, alt, ust) {
    return Math.max(alt, Math.min(x, ust));
  });

  global.TON = T;
  T._HAZIR = HAZIR;
  T._YONTEMLER = YONTEMLER;
  T._kaydet = kaydet;
  T._hem = hem;
  T._liste_iste = liste_iste;
  T._m = m;
  T._harita_mi = harita_mi;
  T._sayi_mi = sayi_mi;
  T._TonHata = TonHata;
})(typeof globalThis !== "undefined" ? globalThis : this);

/* ---------------------------------------------------------------------------
 * Tarayiciya ozgu bolum: ag, es zamanli isler, veri, DOM ve baslatici
 * ------------------------------------------------------------------------- */
(function (global) {
  "use strict";

  var T = global.TON;
  var kaydet = T._kaydet, hem = T._hem, m = T._m;
  var harita_mi = T._harita_mi, TonHata = T._TonHata;
  var liste_iste = T._liste_iste;

  function belge() {
    if (typeof document === "undefined") {
      throw TonHata("Bu is sadece tarayicida calisir (sayfa yok)");
    }
    return document;
  }

  // ------------------------------------------------------------------ ag
  function adres_kur(adres, parametreler) {
    adres = m(adres);
    if (parametreler && harita_mi(parametreler)) {
      var p = Object.keys(parametreler).map(function (k) {
        return encodeURIComponent(k) + "=" + encodeURIComponent(T.metin(parametreler[k]));
      }).join("&");
      if (p) adres += (adres.indexOf("?") >= 0 ? "&" : "?") + p;
    }
    return adres;
  }

  async function istek(yontem, adres, veri, basliklar) {
    var ayar = { method: yontem, headers: {} };
    if (basliklar && harita_mi(basliklar)) {
      Object.keys(basliklar).forEach(function (k) {
        ayar.headers[k] = T.metin(basliklar[k]);
      });
    }
    if (veri !== undefined && veri !== null) {
      if (harita_mi(veri) || Array.isArray(veri)) {
        ayar.body = JSON.stringify(veri);
        if (!ayar.headers["Content-Type"]) {
          ayar.headers["Content-Type"] = "application/json; charset=utf-8";
        }
      } else {
        ayar.body = T.metin(veri);
      }
    }
    var cevap;
    try {
      cevap = await fetch(adres, ayar);
    } catch (e) {
      throw TonHata("Baglanti kurulamadi (" + adres + "): " + (e.message || e));
    }
    var ham = await cevap.text();
    var govde = ham;
    var tur = cevap.headers.get("content-type") || "";
    if (tur.indexOf("json") >= 0 || /^\s*[{[]/.test(ham)) {
      try { govde = JSON.parse(ham); } catch (e) { govde = ham; }
    }
    var basliklar_cikti = {};
    cevap.headers.forEach(function (v, k) { basliklar_cikti[k.toLowerCase()] = v; });
    return { durum: cevap.status, basarili: cevap.ok, veri: govde,
             basliklar: basliklar_cikti };
  }

  function basariyi_dogrula(cevap, adres) {
    if (cevap.basarili) return cevap.veri;
    var ozet = T.metin(cevap.veri);
    if (ozet.length > 200) ozet = ozet.slice(0, 200) + "...";
    throw TonHata("Istek basarisiz (" + cevap.durum + ") " + adres + ": " + ozet);
  }

  kaydet(["get", "getir"], ["adres", "parametreler", "basliklar"],
         async function (adres, parametreler, basliklar) {
           var tam = adres_kur(adres, parametreler);
           return basariyi_dogrula(await istek("GET", tam, null, basliklar), tam);
         });
  kaydet(["post", "gonder"], ["adres", "veri", "basliklar"],
         async function (adres, veri, basliklar) {
           var tam = m(adres);
           return basariyi_dogrula(await istek("POST", tam, veri, basliklar), tam);
         });
  kaydet(["request", "istek"], ["adres", "yontem", "veri", "basliklar"],
         async function (adres, yontem, veri, basliklar) {
           return await istek(m(yontem || "GET").toUpperCase(), m(adres), veri, basliklar);
         });
  kaydet(["encode", "adresle"], ["metin"], function (v) {
    return encodeURIComponent(m(v));
  });

  // ------------------------------------------------------------------ es zamanli
  function gorev_yap(sozu, ad) {
    var g = { __gorev: true, ad: ad || "gorev", bitti: false, sonuc: null, hata: null };
    g.sozu = sozu.then(function (d) { g.bitti = true; g.sonuc = d; return d; },
                       function (e) { g.bitti = true; g.hata = e; throw e; });
    return g;
  }

  kaydet(["asyn", "async", "arkaplan", "esza"], ["hedef", "degerler"],
         function (hedef) {
           var args = Array.prototype.slice.call(arguments, 1);
           if (typeof hedef === "function") {
             return gorev_yap(T.cagir(hedef, args), hedef.__ad || "is");
           }
           if (typeof hedef === "string") {
             return gorev_yap(T.cagir(T.h("get"), [hedef].concat(args)), hedef);
           }
           throw TonHata("asyn() bir is ya da adres ister, " + T.tur(hedef) + " verildi");
         });

  kaydet(["wait", "bekle"], ["hedef"], async function (hedef) {
    if (hedef === undefined || hedef === null) return null;
    if (T._sayi_mi(hedef)) {
      await new Promise(function (c) { setTimeout(c, hedef * 1000); });
      return null;
    }
    if (hedef && hedef.__gorev) return await hedef.sozu;
    if (Array.isArray(hedef)) {
      var c = [];
      for (var i = 0; i < hedef.length; i++) c.push(await T.h("wait")(hedef[i]));
      return c;
    }
    if (typeof hedef.then === "function") return await hedef;
    throw TonHata("bekle() sayi ya da gorev ister, " + T.tur(hedef) + " verildi");
  });

  kaydet(["waitall", "hepsini_bekle"], ["gorevler"], async function (gorevler) {
    if (gorevler && gorevler.__gorev) gorevler = [gorevler];
    return await Promise.all(liste_iste(gorevler, "hepsini_bekle()").map(function (g) {
      return g && g.__gorev ? g.sozu : g;
    }));
  });

  kaydet(["parallel", "paralel"], ["isler", "degerler"], async function (isler) {
    var args = Array.prototype.slice.call(arguments, 1);
    return await Promise.all(liste_iste(isler, "paralel()").map(function (o) {
      if (typeof o === "function") return T.cagir(o, args);
      if (typeof o === "string") return T.cagir(T.h("get"), [o]);
      throw TonHata("paralel() listesinde is ya da adres olmali");
    }));
  });

  kaydet(["after", "sonra", "zamanla", "timer"], ["saniye", "is"],
         function (saniye, is_) {
           if (typeof is_ !== "function") throw TonHata("sonra() bir is ister");
           return gorev_yap(new Promise(function (c, r) {
             setTimeout(function () { T.cagir(is_, []).then(c, r); }, saniye * 1000);
           }), "sonra");
         });

  kaydet(["every", "her_saniye"], ["saniye", "is", "adet"], function (saniye, is_, adet) {
    var sayac = 0;
    var kimlik = setInterval(function () {
      sayac++;
      T.cagir(is_, []);
      if (adet !== undefined && adet !== null && sayac >= adet) clearInterval(kimlik);
    }, saniye * 1000);
    var g = gorev_yap(Promise.resolve(kimlik), "her");
    g.durdur = function () { clearInterval(kimlik); };
    return g;
  });

  kaydet(["timeout", "sure_sinir"], ["saniye", "is", "degerler"],
         async function (saniye, is_) {
           var args = Array.prototype.slice.call(arguments, 2);
           var zamanlayici;
           var sure = new Promise(function (_, r) {
             zamanlayici = setTimeout(function () {
               r(TonHata("Islem " + T.metin(saniye) + " saniyede bitmedi"));
             }, saniye * 1000);
           });
           try {
             return await Promise.race([T.cagir(is_, args), sure]);
           } finally { clearTimeout(zamanlayici); }
         });

  // ------------------------------------------------------------------ yapay zeka
  kaydet(["ai_setup", "zeka_ayarla"], ["url", "kisilik", "model"],
         function (url, kisilik, model) {
           if (url) T.ai_adres = m(url);
           if (kisilik) T.ai_kisilik = m(kisilik);
           if (model) T.ai_model = m(model);
           return true;
         });
  kaydet(["ai_ready", "zeka_hazir"], [], function () { return !!T.ai_adres; });
  kaydet(["ai", "zeka", "sorbana"], ["soru", "model", "kisilik"],
         async function (soru, model, kisilik) {
           var govde = { soru: T.metin(soru) };
           if (model || T.ai_model) govde.model = m(model || T.ai_model);
           if (kisilik || T.ai_kisilik) govde.kisilik = m(kisilik || T.ai_kisilik);
           var c = await istek("POST", T.ai_adres, govde);
           if (!c.basarili) {
             throw TonHata("Yapay zeka hatasi (" + c.durum + "): " + T.metin(c.veri));
           }
           if (harita_mi(c.veri)) return T.metin(c.veri.cevap || c.veri.metin || c.veri);
           return T.metin(c.veri);
         });

  // ------------------------------------------------------------------ veri
  function csv_coz(ham) {
    var satirlar = ham.split(/\r?\n/).filter(function (s) { return s.trim() !== ""; });
    if (!satirlar.length) return [];
    var basliklar = satirlar[0].split(",").map(function (s) { return s.trim(); });
    return satirlar.slice(1).map(function (satir) {
      var parcalar = satir.split(",");
      var h = {};
      basliklar.forEach(function (b, i) {
        var d = (parcalar[i] === undefined ? "" : parcalar[i]).trim();
        h[b] = (d !== "" && !isNaN(Number(d))) ? Number(d) : d;
      });
      return h;
    });
  }

  function veri_sar(satirlar) {
    function alan(s, a) {
      return (a === undefined || a === null) ? s : (harita_mi(s) ? s[m(a)] : s);
    }
    function sayilar(a) {
      return satirlar.map(function (s) { return Number(alan(s, a)); })
                     .filter(function (d) { return !isNaN(d); });
    }
    var nesne = {
      satirlar: satirlar,
      rows: function () { return satirlar.slice(); },
      count: function () { return satirlar.length; },
      sayisi: function () { return satirlar.length; },
      head: function (n) { return satirlar.slice(0, n === undefined ? 10 : n); },
      ilk: function (n) { return satirlar.slice(0, n === undefined ? 10 : n); },
      sum: function (a) { return sayilar(a).reduce(function (x, y) { return x + y; }, 0); },
      avg: function (a) {
        var s = sayilar(a);
        return s.length ? s.reduce(function (x, y) { return x + y; }, 0) / s.length : 0;
      },
      min: function (a) { var s = sayilar(a); return s.length ? Math.min.apply(null, s) : null; },
      max: function (a) { var s = sayilar(a); return s.length ? Math.max.apply(null, s) : null; },
      column: function (a) { return satirlar.map(function (s) { return alan(s, a); }); },
      group: function (a) {
        var c = {};
        satirlar.forEach(function (s) {
          var k = m(alan(s, a));
          c[k] = (c[k] || 0) + 1;
        });
        return c;
      },
      totals: function (a, d) {
        var c = {};
        satirlar.forEach(function (s) {
          var k = m(alan(s, a));
          var v = Number(alan(s, d));
          c[k] = (c[k] || 0) + (isNaN(v) ? 0 : v);
        });
        return c;
      },
      top: function (n, a) {
        return satirlar.slice().sort(function (x, y) {
          return Number(alan(y, a)) - Number(alan(x, a));
        }).slice(0, n === undefined ? 10 : n);
      },
      sort: function (a, tersten) {
        var y = satirlar.slice().sort(function (p, q) {
          var x = alan(p, a), z = alan(q, a);
          if (T._sayi_mi(x) && T._sayi_mi(z)) return x - z;
          return T.metin(x) < T.metin(z) ? -1 : 1;
        });
        if (T.dogru_mu(tersten)) y.reverse();
        return veri_sar(y);
      },
      filter: async function (is_) {
        var c = [];
        for (var i = 0; i < satirlar.length; i++) {
          if (T.dogru_mu(await T.cagir(is_, [satirlar[i]]))) c.push(satirlar[i]);
        }
        return veri_sar(c);
      },
      map: async function (is_) {
        var c = [];
        for (var i = 0; i < satirlar.length; i++) c.push(await T.cagir(is_, [satirlar[i]]));
        return veri_sar(c);
      },
      select: function () {
        var adlar = (arguments.length === 1 && Array.isArray(arguments[0]))
          ? arguments[0] : Array.prototype.slice.call(arguments);
        return veri_sar(satirlar.map(function (s) {
          var h = {};
          adlar.forEach(function (a) { h[m(a)] = harita_mi(s) ? s[m(a)] : s; });
          return h;
        }));
      }
    };
    // turkce adlar
    nesne.sec = nesne.filter; nesne.donustur = nesne.map; nesne.sutun = nesne.column;
    nesne.topla = nesne.sum; nesne.ortalama = nesne.avg; nesne.enaz = nesne.min;
    nesne.encok = nesne.max; nesne.grupla = nesne.group; nesne.toplamlar = nesne.totals;
    nesne.ust = nesne.top; nesne.sirala = nesne.sort; nesne.alanlar = nesne.select;
    Object.keys(nesne).forEach(function (k) {
      if (typeof nesne[k] === "function") nesne[k].__adlar = [];
    });
    return nesne;
  }

  kaydet(["data", "veri"], ["kaynak"], async function (kaynak) {
    if (Array.isArray(kaynak)) return veri_sar(kaynak.slice());
    if (harita_mi(kaynak) && kaynak.satirlar) return kaynak;
    var adres = m(kaynak);
    var ham = await istek("GET", adres);
    if (Array.isArray(ham.veri)) return veri_sar(ham.veri);
    if (typeof ham.veri === "string") return veri_sar(csv_coz(ham.veri));
    return veri_sar([ham.veri]);
  });

  // ------------------------------------------------------------------ DOM
  function oge(secici) {
    if (secici === null || secici === undefined) return null;
    if (typeof secici === "object" && secici.nodeType) return secici;
    var e = belge().querySelector(m(secici));
    if (!e) throw TonHata("Sayfada '" + m(secici) + "' bulunamadi");
    return e;
  }

  kaydet(["oge", "el"], ["secici"], function (secici) {
    var e = belge().querySelector(m(secici));
    return e || null;
  });
  kaydet(["ogeler", "els"], ["secici"], function (secici) {
    return Array.prototype.slice.call(belge().querySelectorAll(m(secici)));
  });
  kaydet(["olustur", "create"], ["etiket", "icerik", "ozellikler"],
         function (etiket, icerik, ozellikler) {
           var e = belge().createElement(m(etiket));
           if (icerik !== undefined && icerik !== null) e.innerHTML = T.metin(icerik);
           if (ozellikler && harita_mi(ozellikler)) {
             Object.keys(ozellikler).forEach(function (k) {
               e.setAttribute(k, T.metin(ozellikler[k]));
             });
           }
           return e;
         });

  kaydet(["yaz_ic", "set_html"], ["secici", "html"], function (secici, html) {
    oge(secici).innerHTML = T.metin(html);
    return true;
  });
  kaydet(["oku_ic", "get_html"], ["secici"], function (secici) {
    return oge(secici).innerHTML;
  });
  kaydet(["yaz_metin", "set_text"], ["secici", "metin"], function (secici, metin) {
    oge(secici).textContent = T.metin(metin);
    return true;
  });
  kaydet(["oku_metin", "get_text"], ["secici"], function (secici) {
    return oge(secici).textContent;
  });
  kaydet(["temizle_ic", "clear_html"], ["secici"], function (secici) {
    oge(secici).innerHTML = "";
    return true;
  });
  kaydet(["ekle_oge", "append_el"], ["secici", "icerik"], function (secici, icerik) {
    var hedef = oge(secici);
    if (icerik && icerik.nodeType) hedef.appendChild(icerik);
    else hedef.insertAdjacentHTML("beforeend", T.metin(icerik));
    return true;
  });
  kaydet(["sil_oge", "remove_el"], ["secici"], function (secici) {
    var e = oge(secici);
    if (e.parentNode) e.parentNode.removeChild(e);
    return true;
  });

  kaydet(["deger", "value"], ["secici", "yeni"], function (secici, yeni) {
    var e = oge(secici);
    if (yeni === undefined) {
      if (e.type === "checkbox") return e.checked;
      var d = e.value === undefined ? "" : e.value;
      return (d !== "" && !isNaN(Number(d)) && e.type === "number") ? Number(d) : d;
    }
    if (e.type === "checkbox") e.checked = T.dogru_mu(yeni);
    else e.value = T.metin(yeni);
    return yeni;
  });
  kaydet(["ozellik", "attr"], ["secici", "ad", "yeni"], function (secici, ad, yeni) {
    var e = oge(secici);
    if (yeni === undefined) return e.getAttribute(m(ad));
    e.setAttribute(m(ad), T.metin(yeni));
    return yeni;
  });
  kaydet(["stil", "style"], ["secici", "ozellik", "deger"], function (secici, ozellik, deger) {
    var e = oge(secici);
    if (deger === undefined) return getComputedStyle(e)[m(ozellik)];
    e.style[m(ozellik)] = T.metin(deger);
    return true;
  });
  kaydet(["ekle_sinif", "add_class"], ["secici", "sinif"], function (secici, sinif) {
    oge(secici).classList.add(m(sinif));
    return true;
  });
  kaydet(["sil_sinif", "remove_class"], ["secici", "sinif"], function (secici, sinif) {
    oge(secici).classList.remove(m(sinif));
    return true;
  });
  kaydet(["degistir_sinif", "toggle_class"], ["secici", "sinif"], function (secici, sinif) {
    return oge(secici).classList.toggle(m(sinif));
  });
  kaydet(["gorunur", "visible"], ["secici", "goster"], function (secici, goster) {
    var e = oge(secici);
    if (goster === undefined) return e.style.display !== "none";
    e.style.display = T.dogru_mu(goster) ? "" : "none";
    return true;
  });
  kaydet(["odak", "focus"], ["secici"], function (secici) {
    oge(secici).focus();
    return true;
  });

  function olay_bagla(hedef, ad, is_, engelle) {
    hedef.addEventListener(ad, function (e) {
      if (engelle) e.preventDefault();
      T.cagir(is_, [olay_haritasi(e)]).catch(hata_goster);
    });
    return true;
  }

  function olay_haritasi(e) {
    var h = { tur: e.type, tus: e.key || "", hedef: e.target ? (e.target.id || "") : "" };
    if (e.target && e.target.value !== undefined) h.deger = e.target.value;
    if (e.target && e.target.dataset) {
      Object.keys(e.target.dataset).forEach(function (k) { h[k] = e.target.dataset[k]; });
    }
    return h;
  }

  kaydet(["tikla", "on_click"], ["secici", "is"], function (secici, is_) {
    return olay_bagla(oge(secici), "click", is_, false);
  });
  kaydet(["olay", "on"], ["secici", "olay_adi", "is"], function (secici, ad, is_) {
    return olay_bagla(oge(secici), m(ad), is_, false);
  });
  kaydet(["gonderim", "on_submit"], ["secici", "is"], function (secici, is_) {
    return olay_bagla(oge(secici), "submit", is_, true);
  });
  kaydet(["tus", "on_key"], ["secici", "is"], function (secici, is_) {
    return olay_bagla(oge(secici), "keyup", is_, false);
  });
  kaydet(["sayfa_hazir", "on_ready"], ["is"], function (is_) {
    if (belge().readyState !== "loading") { T.cagir(is_, []).catch(hata_goster); }
    else {
      belge().addEventListener("DOMContentLoaded", function () {
        T.cagir(is_, []).catch(hata_goster);
      });
    }
    return true;
  });

  kaydet(["form_verisi", "form_data"], ["secici"], function (secici) {
    var f = oge(secici);
    var h = {};
    Array.prototype.forEach.call(f.elements || [], function (e) {
      if (!e.name) return;
      h[e.name] = e.type === "checkbox" ? e.checked : e.value;
    });
    return h;
  });

  kaydet(["uyari", "alert"], ["mesaj"], function (mesaj) {
    global.alert(T.metin(mesaj));
    return true;
  });
  kaydet(["onay", "confirm"], ["soru"], function (soru) {
    return global.confirm(T.metin(soru));
  });
  kaydet(["ask", "sor", "sor_kutu", "prompt"], ["soru", "varsayilan"], function (soru, varsayilan) {
    var c = global.prompt(T.metin(soru), varsayilan === undefined ? "" : T.metin(varsayilan));
    return c === null ? "" : c;
  });

  kaydet(["git", "go"], ["adres"], function (adres) {
    global.location.href = m(adres);
    return true;
  });
  kaydet(["adres", "location"], [], function () { return global.location.href; });
  kaydet(["yenile", "reload"], [], function () { global.location.reload(); return true; });
  kaydet(["sayfa_basligi", "page_title"], ["yeni"], function (yeni) {
    if (yeni === undefined) return belge().title;
    belge().title = T.metin(yeni);
    return true;
  });

  kaydet(["sakla", "store"], ["ad", "deger"], function (ad, deger) {
    try { global.localStorage.setItem("ton:" + m(ad), JSON.stringify(deger)); }
    catch (e) { return false; }
    return true;
  });
  kaydet(["saklanan", "stored"], ["ad", "varsayilan"], function (ad, varsayilan) {
    try {
      var ham = global.localStorage.getItem("ton:" + m(ad));
      if (ham === null) return varsayilan === undefined ? null : varsayilan;
      return JSON.parse(ham);
    } catch (e) { return varsayilan === undefined ? null : varsayilan; }
  });
  kaydet(["sakli_sil", "store_remove"], ["ad"], function (ad) {
    try { global.localStorage.removeItem("ton:" + m(ad)); } catch (e) { return false; }
    return true;
  });


  // ------------------------------------------------------------------ eksik cekirdek isleri
  hem(["gorev"], ["done", "bitti_mi"], ["gorev"], function (g) {
    if (!g || !g.__gorev) throw TonHata("bitti_mi() bir gorev ister");
    return g.bitti;
  });
  hem(["gorev"], ["result", "sonucu"], ["gorev"], async function (g) {
    if (!g || !g.__gorev) throw TonHata("sonucu() bir gorev ister");
    return await g.sozu;
  });

  kaydet(["call", "cagir"], ["hedef", "argumanlar"], async function (hedef, argumanlar) {
    if (typeof hedef === "string") {
      var bulunan = T._HAZIR[hedef];
      if (!bulunan) throw TonHata("'" + hedef + "' adinda bir is yok");
      hedef = bulunan;
    }
    return await T.cagir(hedef, liste_iste(argumanlar || [], "cagir()"));
  });

  kaydet(["params", "parametreleri"], ["is"], function (is_) {
    return (is_ && is_.__adlar) ? is_.__adlar.slice() : [];
  });

  kaydet(["builtins", "hazir_isler"], [], function () {
    return Object.keys(T._HAZIR).sort();
  });

  kaydet(["template", "sablon"], ["metin", "degerler"], function (sablon_metni, degerler) {
    var h = degerler || {};
    return m(sablon_metni).replace(/%%([A-Za-z_][\w.]*)%%/g, function (tam, yol) {
      var parcalar = yol.split(".");
      var d = h;
      for (var i = 0; i < parcalar.length; i++) {
        if (d === null || d === undefined) return tam;
        d = harita_mi(d) ? d[parcalar[i]] : undefined;
      }
      return d === undefined ? tam : T.metin(d);
    });
  });

  kaydet(["ai_json", "zeka_veri"], ["soru", "model"], async function (soru, model) {
    var ham = await T.h("ai")(T.metin(soru) +
      "\n\nSadece gecerli JSON dondur, baska hicbir sey yazma.", model);
    ham = m(ham).trim();
    if (ham.indexOf("```") === 0) {
      ham = ham.replace(/^```[a-z]*\s*/i, "").replace(/```\s*$/, "").trim();
    }
    return T.h("json")(ham);
  });

  kaydet(["ai_chat", "zeka_sohbet"], ["gecmis", "soru", "model"],
         async function (gecmis, soru, model) {
           var mesajlar = Array.isArray(gecmis) ? gecmis.slice() : [];
           if (soru !== undefined && soru !== null) {
             mesajlar.push({ rol: "user", metin: T.metin(soru) });
           }
           var cevap = await T.h("ai")(T.metin(soru), model);
           mesajlar.push({ rol: "assistant", metin: cevap });
           return { cevap: cevap, gecmis: mesajlar };
         });

  // ------------------------------------------------------------------ baslatici
  function hata_goster(e) {
    if (e && e.mesaj === "__ton_cik__") return;
    var mesaj = T.hata_metni(e);
    if (typeof console !== "undefined") console.error("TON hatasi: " + mesaj);
    if (typeof document !== "undefined") {
      var kutu = document.getElementById("ton-hata");
      if (!kutu) {
        kutu = document.createElement("pre");
        kutu.id = "ton-hata";
        kutu.style.cssText = "margin:1rem;padding:1rem;border-radius:8px;" +
          "background:#fee;color:#900;font:14px/1.5 ui-monospace,monospace;" +
          "white-space:pre-wrap;border:1px solid #f99";
        if (document.body) document.body.appendChild(kutu);
      }
      kutu.textContent = "TON hatasi: " + mesaj;
    }
  }
  T.hata_goster = hata_goster;

  T.calistir = function (program) {
    var soz = Promise.resolve().then(function () { return program(T); });
    return soz.catch(hata_goster);
  };

  // <script type="text/ton"> bloklari: sunucudan derlenmis hali istenir
  T.betikleri_calistir = function () {
    if (typeof document === "undefined") return;
    var betikler = document.querySelectorAll('script[type="text/ton"][src]');
    Array.prototype.forEach.call(betikler, function (b) {
      var s = document.createElement("script");
      s.src = b.src.replace(/\.(ton|tn|nyl|tnl)$/, ".ton.js");
      document.head.appendChild(s);
    });
  };
})(typeof globalThis !== "undefined" ? globalThis : this);
