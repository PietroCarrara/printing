function main() {
  var doc = Document.openDocument(scriptArgs[0]);

  for (var i = 0; i < doc.countPages(); i++) {
    var page = doc.loadPage(i);
    var processor = new Processor(doc, {
      pageIndex: i,
      page: page,
    });
    page.process(processor);
  }
  // TODO: Update page contents. For now, all the pages that
  // we process are just a "/Form Do", so no need to worry

  doc.save(scriptArgs[1]);
}

function Processor(document, opts) {
  opts = opts || {};

  return {
    document: document,
    resources: [],
    level: opts.level || 0,
    page: opts.page || null,
    pageIndex: opts.pageIndex || null,
    output: new Buffer(),
    ctm: mupdf.Matrix.identity,
    graphicsState: [],
    op_Do_form: function (name, xobj) {
      this.output.writeLine("/" + name + " Do");

      // "Remove boundaries" from XObject
      // var bbox = xobj.get("BBox");
      // if (true) {
      //   xobj.put("BBox", [-800, -800, 800, 800]);
      //   // xobj.put("BBox", this.page.getObject().get("MediaBox"));
      // }

      // var matrix = xobj.get("Matrix");
      // if (matrix) {
      //   xobj.put("Matrix", mupdf.Matrix.identity);
      //   var prepend = new Buffer();
      //   var contents = xobj.readStream();
      //   prepend.writeLine(asArray(matrix).join(" ") + " cm"); // Apply matrix "by hand"
      //   prepend.writeBuffer(contents);
      //   xobj.writeStream(prepend);
      // }

      var subprocess = new Processor(this.document, {
        level: this.level + 1,
        page: this.page,
        pageIndex: this.pageIndex,
      });
      xobj.process(subprocess, this.document);
      xobj.writeStream(subprocess.output);
    },
    push_resources: function (xobject) {
      this.resources.push(xobject);
    },
    pop_resources: function () {
      this.resources.pop();
    },

    // Operators with no override
    op_w: function (linewidth) {
      this.output.writeLine(linewidth + " w");
    },
    op_j: function (linejoin) {
      this.output.writeLine(linejoin + " j");
    },
    op_J: function (linecap) {
      this.output.writeLine(linecap + " J");
    },
    op_M: function (miterlimit) {
      this.output.writeLine(miterlimit + " M");
    },
    op_d: function (array, phase) {
      this.output.writeLine("[" + array.join(" ") + "] " + phase + " d");
    },
    op_ri: function (intent) {
      print("warn: unimplemented 'op_ri' called!");
    },
    op_i: function (flatness) {
      print("warn: unimplemented 'op_i' called!");
    },
    op_gs: function (name, extgstate) {
      this.output.writeLine("/" + name + " gs");
    },
    op_q: function () {
      this.output.writeLine("q");
      this.graphicsState.push(this.ctm);
    },
    op_Q: function () {
      this.output.writeLine("Q");
      this.ctm = this.graphicsState.pop();
    },
    op_cm: function (a, b, c, d, e, f) {
      this.output.writeLine([a, b, c, d, e, f].join(" ") + " " + "cm");
      this.ctm = Matrix.concat([a, b, c, d, e, f], this.ctm);
    },
    op_m: function (x, y) {
      this.output.writeLine(x + " " + y + " " + " m");
    },
    op_l: function (x, y) {
      this.output.writeLine(x + " " + y + " " + " l");
    },
    op_c: function (x1, y1, x2, y2, x3, y3) {
      this.output.writeLine([x1, y1, x2, y2, x3, y3].join(" ") + " c");
    },
    op_v: function (x2, y2, x3, y3) {
      this.output.writeLine([x2, y2, x3, y3].join(" ") + " v");
    },
    op_y: function (x1, y1, x3, y3) {
      this.output.writeLine([x1, y1, x3, y3].join(" ") + " y");
    },
    op_h: function () {
      this.output.writeLine("h");
    },
    op_re: function (x, y, w, h) {
      this.output.writeLine([x, y, w, h].join(" ") + " re");
    },
    op_S: function () {
      this.output.writeLine("S");
    },
    op_s: function () {
      this.output.writeLine("s");
    },
    op_F: function () {
      this.output.writeLine("F");
    },
    op_f: function () {
      this.output.writeLine("f");
    },
    op_fstar: function () {
      this.output.writeLine("f*");
    },
    op_B: function () {
      this.output.writeLine("B");
    },
    op_Bstar: function () {
      this.output.writeLine("B*");
    },
    op_b: function () {
      this.output.writeLine("b");
    },
    op_bstar: function () {
      this.output.writeLine("b*");
    },
    op_n: function () {
      this.output.writeLine("n");
    },
    op_W: function () {
      this.output.writeLine("W");
    },
    op_Wstar: function () {
      this.output.writeLine("W*");
    },
    op_BT: function () {
      this.output.writeLine("BT");
    },
    op_ET: function () {
      this.output.writeLine("ET");
    },
    op_Tc: function (charspace) {
      this.output.writeLine(charspace + " Tc");
    },
    op_Tw: function (wordspace) {
      this.output.writeLine(wordspace + " Tw");
    },
    op_Tz: function (scale) {
      this.output.writeLine(scale + " Tz");
    },
    op_TL: function (leading) {
      this.output.writeLine(leading + " TL");
    },
    op_Tf: function (name, size) {
      this.output.writeLine("/" + name + " " + size + " Tf");
    },
    op_Tr: function (render) {
      this.output.writeLine(render + " Tr");
    },
    op_Ts: function (rise) {
      this.output.writeLine(rise + "Ts");
    },
    op_Td: function (tx, ty) {
      this.output.writeLine(tx + " " + ty + " Td");
    },
    op_TD: function (tx, ty) {
      this.output.writeLine(tx + " " + ty + " TD");
    },
    op_Tm: function (a, b, c, d, e, f) {
      this.output.writeLine([a, b, c, d, e, f].join(" ") + " Tm");
    },
    op_Tstar: function () {
      this.output.writeLine("T*");
    },
    op_TJ: function (array) {
      this.output.write("[");
      for (var i in array) {
        var value = array[i];
        if (typeof value === "number") {
          this.output.write(" " + value.toString());
        } else {
          this.output.write(" (");
          this.output.writeBuffer(byteString(value));
          this.output.write(")");
        }
      }
      this.output.writeLine("] TJ");
    },
    op_Tj: function (str) {
      this.output.write(" (");
      this.output.writeBuffer(byteString(str));
      this.output.write(")");

      this.output.writeLine(" Tj");
    },
    op_squote: function (str) {
      print("warn: unimplemented 'op_squote' called!");
    },
    op_dquote: function (aw, ac, str) {
      print("warn: unimplemented 'op_dquote' called!");
    },
    op_d0: function (wx, wy) {
      print("warn: unimplemented 'op_d0' called!");
    },
    op_d1: function (wx, wy, llx, lly, urx, ury) {
      print("warn: unimplemented 'op_d1' called!");
    },
    op_CS: function (name, colorspace) {
      this.output.writeLine("/" + name + " " + "CS");
    },
    op_cs: function (name, colorspace) {
      this.output.writeLine("/" + name + " " + "cs");
    },
    op_SC_pattern: function (name, patId, colors) {
      // TODO: pdf_obj instead of patId!
      this.output.writeLine(colors.join(" ") + "/" + name + " SCN");
    },
    op_sc_pattern: function (name, patId, colors) {
      // TODO: pdf_obj instead of patId!
      this.output.writeLine(colors.join(" ") + "/" + name + " scn");
    },
    op_SC_shade: function (name, shade) {
      print("warn: unimplemented 'op_SC_shade' called!");
    },
    op_sc_shade: function (name, shade) {
      print("warn: unimplemented 'op_sc_shade' called!");
    },
    op_SC_color: function (colors) {
      // TODO: should this really be SCN?
      var output = this.output;
      colors.forEach(function (color) {
        output.write(" " + color);
      });
      this.output.writeLine(" SCN");
    },
    op_sc_color: function (colors) {
      var output = this.output;
      colors.forEach(function (color) {
        output.write(" " + color);
      });
      this.output.writeLine(" scn");
    },
    op_G: function (g) {
      this.output.writeLine(g + " G");
    },
    op_g: function (g) {
      this.output.writeLine(g + " g");
    },
    op_RG: function (r, g, b) {
      this.output.writeLine([r, g, b].join(" ") + " RG");
    },
    op_rg: function (r, g, b) {
      this.output.writeLine([r, g, b].join(" ") + " rg");
    },
    op_K: function (c, m, y, k) {
      print("warn: unimplemented 'op_K' called!");
    },
    op_k: function (c, m, y, k) {
      print("warn: unimplemented 'op_k' called!");
    },
    op_BI: function (img, colorspace) {
      print("warn: unimplemented 'op_BI' called!");
    },
    op_sh: function (name, image) {
      this.output.writeLine("/" + name + " " + sh);
      print("warn: unimplemented 'op_sh' called!");
    },
    op_Do_image: function (name, image) {
      // Draw a red square below images
      // this.output.writeLine("q");
      // this.output.writeLine("1 0 0 RG");
      // this.output.writeLine("0 0 m");
      // this.output.writeLine("-0.1 -0.1 1.1 1.1 re");
      // this.output.writeLine("h");
      // this.output.writeLine("S");
      // this.output.writeLine("Q");

      // print(image.getXResolution()); // Segfault?

      this.output.writeLine("/" + name + " Do");
    },
    op_MP: function (tag) {
      print("warn: unimplemented 'op_MP' called!");
    },
    op_DP: function (tag, raw) {
      print("warn: unimplemented 'op_DP' called!");
    },
    op_BMC: function (tag) {
      this.output.writeLine("/" + tag + " BMC");
    },
    op_BDC: function (tag, raw) {
      this.output.writeLine("/" + tag + " " + raw + " " + " BDC");
    },
    op_EMC: function () {
      this.output.writeLine("EMC");
    },
    op_BX: function () {
      this.output.writeLine("BX");
    },
    op_EX: function () {
      this.output.writeLine("EX");
    },
  };
}

function byteString(strOrArray) {
  var buffer = new Buffer();

  if (typeof strOrArray === "string" || typeof strOrArray === "number") {
    buffer.write(escapePdfString(strOrArray.toString()));
  }
  if (typeof strOrArray === "object") {
    strOrArray.forEach(function (byte) {
      // ASCII codepoints that should be escaped: (, ), \
      if (byte === 40 || byte === 41 || byte === 92) {
        buffer.write("\\");
      }
      buffer.writeByte(byte);
    });
  }

  return buffer;
}

function asArray(pdfArray) {
  var array = [];
  pdfArray.forEach(function (value) {
    array.push(value);
  });
  return array;
}

function escapePdfString(str) {
  var result = "";
  for (var i in str) {
    if (str[i] === "(" || str[i] === ")" || str[i] === "\\") {
      result += "\\";
    }
    result += str[i];
  }

  return result;
}

function pdfObjPrint(pdfObj) {
  if (pdfObj.isStream()) {
    print(". =", pdfObj.readStream().asString());
  }
  pdfObj.forEach(function (v, k) {
    if (v.isIndirect()) {
      print(k, "=", v, "->", v.resolve());
    } else if (v.isArray()) {
      v.forEach(function (v, i) {
        print(k, "[", i, "]", "=", v, "->", v.resolve());
      });
    } else {
      print(k, "=", v);
    }
  });
}

if (scriptArgs.length !== 2) {
  print("usage: mutool run input.pdf output.pdf");
} else {
  main();
}
