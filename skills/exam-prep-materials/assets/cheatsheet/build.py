#!/usr/bin/env python3
"""Build cheatsheet.html from content.py.

    python3 build.py && node pw.js          # -> cheatsheet.pdf, fill report

A4 pages with three columns.  The boxes of content.py are packed into the
columns in order, in the browser after the fonts have loaded: a box goes into
the current column, and if the column overflows it moves to the next one; new
pages are added as needed.  Each page header shows the range of section
numbers on that page.  KaTeX renders the mathematics ($...$, $$...$$); set
KATEX_DIST to its dist/ folder (npm pack katex@0.16.9 && tar xzf katex-0.16.9.tgz
gives package/dist), default node_modules/katex/dist.
"""
import html
import os
import re

from content import BOXES, FOOT, META, PARTS, SUBTITLE, TITLE

KDIR = os.environ.get('KATEX_DIST', 'node_modules/katex/dist')

CSS = r'''
@page{size:A4;margin:0}
*{box-sizing:border-box}
html,body{margin:0;padding:0;background:#fff}
body{font-family:'NanumBarunGothic','NanumGothic','Nanum Gothic','Apple SD Gothic Neo',sans-serif;
     font-size:7.25pt;line-height:1.32;color:#1c1c1e;-webkit-print-color-adjust:exact;print-color-adjust:exact}
.page{width:210mm;height:297mm;padding:6mm 6.5mm 5mm;position:relative;overflow:hidden;
      display:flex;flex-direction:column;break-after:page}
.page:last-child{break-after:auto}
header{display:flex;align-items:flex-end;justify-content:space-between;border-bottom:1.2pt solid #1c1c1e;
       padding-bottom:1.2mm;margin-bottom:2mm}
header h1{font-size:12pt;margin:0;letter-spacing:-.2pt}
header h1 small{font-size:8pt;font-weight:400;color:#555;margin-left:2mm}
header .meta{text-align:right;font-size:6.2pt;color:#444;line-height:1.35}
.legend span{display:inline-block;padding:0 1.6mm;border-radius:1mm;color:#fff;margin-left:.8mm;font-size:5.8pt}
.cols{flex:1;min-height:0;display:grid;grid-template-columns:repeat(3,1fr);column-gap:3.2mm;margin-bottom:4mm}
.col{overflow:hidden;min-height:0}
.box{border:.6pt solid var(--c);border-radius:1.6mm;margin:0 0 1.8mm;background:#fff;break-inside:avoid}
.box>h2{margin:0;padding:.55mm 1.6mm .45mm;background:var(--c);color:#fff;font-size:8pt;font-weight:700;
        border-radius:1.3mm 1.3mm 0 0}
.box>h2 b{display:inline-block;background:rgba(255,255,255,.25);border-radius:.8mm;padding:0 1mm;
          margin-right:1.2mm;font-size:6.8pt}
.bd{padding:1mm 1.5mm 1mm}
ul{margin:0;padding:0;list-style:none}
li{position:relative;padding-left:2.2mm;margin:0 0 .5mm;line-height:1.42}
li:before{content:'';position:absolute;left:.4mm;top:1.25mm;width:1mm;height:1mm;border-radius:50%;background:var(--c)}
.k{background:var(--t);border-radius:1mm;padding:.6mm 1.2mm;margin:.6mm 0 .8mm;border-left:1.6pt solid var(--c);line-height:1.62}
.st{font-size:6.5pt;background:#f3f3f6;border-radius:1mm;padding:.35mm 1.1mm;margin:.2mm 0 .6mm;line-height:1.55}
.st b{color:var(--c);margin-right:.7mm}.st b:not(:first-child){margin-left:1.6mm}
.tag{display:inline-block;font-size:5.4pt;color:#fff;background:#999;border-radius:.7mm;padding:0 .8mm}
table{border-collapse:collapse;width:100%;margin:.5mm 0 .8mm;font-size:6.5pt}
td,th{border:.4pt solid #cfcfd6;padding:.35mm .7mm}
th{background:var(--t);color:var(--c);text-align:left}
.katex{font-size:1.06em}.katex-display{margin:.5mm 0}
.foot{position:absolute;bottom:2.2mm;left:6.5mm;right:6.5mm;font-size:5.6pt;color:#888;
      display:flex;justify-content:space-between}
'''


def esc_math(t):
    # a raw < or > inside $...$ would open an HTML tag and swallow the text
    return re.sub(r'\$[^$]+\$', lambda m: m.group(0).replace('<', r'\lt ').replace('>', r'\gt '), t)


def main():
    part_css = ''.join(f'.{c}{{--c:{col};--t:{tint}}}' for c, col, tint, _ in PARTS)
    legend = '<div class="legend">' + ''.join(
        f'<span style="background:{col}">{html.escape(lab)}</span>' for _, col, _, lab in PARTS) + '</div>'
    boxes = ''.join(
        f'<section class="box {cls}"><h2><b>{html.escape(no)}</b>{html.escape(title)}</h2>'
        f'<div class="bd">{esc_math(body)}</div></section>' for cls, no, title, body in BOXES)
    page_tpl = (f'<div class="page"><header><h1>{html.escape(TITLE)}<small>{html.escape(SUBTITLE)}'
                f'<span class="rng"></span></small></h1><div class="meta">{html.escape(META)}<br>{legend}</div></header>'
                f'<div class="cols"><div class="col"></div><div class="col"></div><div class="col"></div></div>'
                f'<div class="foot"><span>{html.escape(FOOT)}</span><span class="pno"></span></div></div>')
    doc = f'''<!doctype html><html lang="ko"><head><meta charset="utf-8"><title>{html.escape(TITLE)}</title>
<link rel="stylesheet" href="{KDIR}/katex.min.css"><style>{CSS}{part_css}</style>
<script src="{KDIR}/katex.min.js"></script><script src="{KDIR}/contrib/auto-render.min.js"></script>
</head><body>
<template id="tpl">{page_tpl}</template>
<div id="pool" style="width:63.5mm">{boxes}</div>
<script>
renderMathInElement(document.getElementById('pool'), {{
  delimiters:[{{left:'$$',right:'$$',display:true}},{{left:'$',right:'$',display:false}}],
  macros:{{"\\\\d":"\\\\mathrm{{d}}","\\\\pdc":"\\\\left(\\\\frac{{\\\\partial #1}}{{\\\\partial #2}}\\\\right)_{{#3}}"}},
  throwOnError:false, strict:false }});
document.fonts.ready.then(function(){{
  var pool = document.getElementById('pool'), tpl = document.getElementById('tpl');
  var cols = [], ci = -1;
  function newPage(){{
    var pg = tpl.content.firstElementChild.cloneNode(true);
    document.body.insertBefore(pg, pool);
    cols = cols.concat([].slice.call(pg.querySelectorAll('.col')));
  }}
  function over(c){{ return c.scrollHeight > c.clientHeight + 1; }}
  [].slice.call(pool.children).forEach(function(bx){{
    if (ci < 0){{ newPage(); ci = 0; }}
    cols[ci].appendChild(bx);
    if (over(cols[ci]) && cols[ci].children.length > 1){{
      ci++; if (ci >= cols.length) newPage();
      cols[ci].appendChild(bx);
    }}
  }});
  pool.remove();
  var pages = document.querySelectorAll('.page');
  [].forEach.call(pages, function(pg, i){{
    pg.querySelector('.pno').textContent = (i + 1) + ' / ' + pages.length;
    var nos = [].map.call(pg.querySelectorAll('.box>h2>b'), function(b){{ return b.textContent; }})
                .filter(function(t){{ return /^§/.test(t); }});
    if (nos.length) pg.querySelector('.rng').textContent = ' · ' + nos[0] + (nos.length > 1 ? '–' + nos[nos.length-1] : '');
  }});
  document.body.dataset.ready = '1';
}});
</script></body></html>'''
    with open('cheatsheet.html', 'w', encoding='utf-8') as f:
        f.write(doc)
    print('cheatsheet.html: %d boxes' % len(BOXES))


if __name__ == '__main__':
    main()
