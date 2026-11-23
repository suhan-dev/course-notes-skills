"""Wrap an HTML body with $...$ / $$...$$ math into a self-rendering widget.

    python3 mkwidget.py body.html out.json TITLE

Writes {"title": TITLE, "widget_code": "<html>"}: the body plus KaTeX 0.16.9
(CSS and auto-render from jsdelivr) and a few styles that use the host's
colour variables (--text-primary, --text-secondary).  For chat surfaces that
render HTML widgets but not math in plain messages.  TITLE: letters, digits,
_ or - only.  Check the body first with check.js.
"""
import json
import sys

HEAD = """<link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/katex@0.16.9/dist/katex.min.css">
<style>
.tx{color:var(--text-primary);font-size:15px;line-height:1.75;max-width:720px}
.tx p{margin:0 0 10px}
.tx .katex-display{margin:10px 0;overflow-x:auto;overflow-y:hidden}
.tx .katex{color:var(--text-primary)}
.tx .note{color:var(--text-secondary);font-size:13px}
.tx table{border-collapse:collapse;margin:8px 0}
.tx td,.tx th{border:1px solid var(--border-primary,#8884);padding:4px 8px}
</style>
<div class="tx" id="tx">
"""
TAIL = """
</div>
<script>
(function(){
  var root=document.getElementById('tx');
  var opts={delimiters:[{left:'$$',right:'$$',display:true},{left:'$',right:'$',display:false}],
            macros:{"\\\\dbar":"\\\\text{đ}","\\\\pdc":"\\\\left(\\\\frac{\\\\partial #1}{\\\\partial #2}\\\\right)_{#3}"},throwOnError:false};
  function load(src,cb){var s=document.createElement('script');s.src=src;s.onload=cb;document.head.appendChild(s);}
  function go(){renderMathInElement(root,opts);}
  var base='https://cdn.jsdelivr.net/npm/katex@0.16.9/dist/';
  if(window.renderMathInElement){go();return;}
  load(base+'katex.min.js',function(){load(base+'contrib/auto-render.min.js',go);});
})();
</script>
"""

if __name__ == '__main__':
    if len(sys.argv) != 4:
        sys.exit(__doc__)
    body = open(sys.argv[1], encoding='utf-8').read()
    code = HEAD + body + TAIL
    with open(sys.argv[2], 'w', encoding='utf-8') as f:
        json.dump({"title": sys.argv[3], "widget_code": code}, f, ensure_ascii=False)
    print(len(code))
