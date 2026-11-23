// pw.js --- print cheatsheet.html to cheatsheet.pdf and report how full it is.
//   node pw.js
// Prints, per column, how far down the last box reaches (% of the column) and
// how many pixels overflow (must be 0), then the number of KaTeX errors.
// Tune by moving boxes or changing the body size in build.py; keep every column
// under 100% and every overflow at 0.
const path = require('path');
const { chromium } = require('playwright');
(async () => {
  const b = await chromium.launch();
  const p = await b.newPage();
  await p.goto('file://' + path.resolve('cheatsheet.html'));
  await p.waitForFunction(() => document.body.dataset.ready === '1', null, { timeout: 30000 });
  await p.evaluate(() => document.fonts.ready);
  const fill = await p.evaluate(() => [...document.querySelectorAll('.col')].map(c => {
    const r = c.getBoundingClientRect(), e = c.lastElementChild;
    return e ? Math.round(100 * (e.getBoundingClientRect().bottom - r.top) / r.height) : 0;
  }));
  const over = await p.evaluate(() => [...document.querySelectorAll('.col')].map(c => c.scrollHeight - c.clientHeight));
  const errs = await p.evaluate(() => [...document.querySelectorAll('.katex-error')].map(e => e.title || e.textContent).slice(0, 10));
  console.log('fill %   ', JSON.stringify(fill));
  console.log('overflow ', JSON.stringify(over));
  console.log('katex errors', errs.length, errs.length ? JSON.stringify(errs) : '');
  await p.pdf({ path: 'cheatsheet.pdf', preferCSSPageSize: true, printBackground: true });
  console.log('cheatsheet.pdf written');
  await b.close();
  process.exit(over.some(x => x > 1) || errs.length ? 1 : 0);
})();
