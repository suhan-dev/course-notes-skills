// check.js --- parse every $...$ and $$...$$ of an HTML body with KaTeX and
// report the ones that fail, before the body is posted as a widget.
//   NODE_PATH=<dir containing katex/> node check.js body.html
// It also flags a raw < or > inside math: in HTML, "$T<T_c$" opens a tag and
// swallows the text after it.  Write \lt and \gt inside math.
const katex = require("katex"), fs = require("fs");
const h = fs.readFileSync(process.argv[2], "utf8").replace(/&lt;/g, "<").replace(/&gt;/g, ">").replace(/&amp;/g, "&");
const macros = { "\\dbar": "\\text{đ}", "\\pdc": "\\left(\\frac{\\partial #1}{\\partial #2}\\right)_{#3}" };
const re = /\$\$([\s\S]+?)\$\$|\$([^$]+?)\$/g;
let m, n = 0, bad = 0;
while ((m = re.exec(h))) {
  n++;
  const t = m[1] ?? m[2];
  try { katex.renderToString(t, { macros, throwOnError: true, displayMode: !!m[1] }); }
  catch (e) { bad++; console.log("ERR", t, e.message); }
}
// a bare < or > inside math in the SOURCE opens or closes an HTML tag
const src = fs.readFileSync(process.argv[2], "utf8"), raw = [];
const re2 = /\$\$([\s\S]+?)\$\$|\$([^$]+?)\$/g;
while ((m = re2.exec(src))) { const t = m[1] ?? m[2]; if (/[<>]/.test(t)) raw.push(t); }
for (const s of raw) console.log("RAW < or > inside math (use \\lt / \\gt):", s.slice(0, 60));
console.log("total", n, "bad", bad, "raw<>", raw.length);
process.exit(bad || raw.length ? 1 : 0);
