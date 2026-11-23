// viewer-test.js --- end-to-end test of the PDF notes viewer (docs/index.html)
//
//   node viewer-test.js <site dir> [--shots <dir>]
//
// <site dir> is the folder the site serves: index.html, manifest.json and the
// PDFs it names (a course's docs/).  The test serves it on 127.0.0.1, opens it
// in Chromium through Playwright and checks what a reader does: the first
// load, the table of contents, switching language at a section, the document
// tabs and ?doc= routing, solution veils, #page= deep links, keeping the
// reading place across a window resize, and the phone layout.  It reads
// everything it needs from manifest.json and the rendered page, so it runs
// unchanged on any course.
//
// pdf.js comes from cdnjs/jsdelivr.  Sandboxes often block those hosts; then
// point PDFJS_DIR at an unpacked pdfjs-dist of the same version and every CDN
// request is answered from it:
//     npm pack pdfjs-dist@3.11.174 && tar xzf pdfjs-dist-3.11.174.tgz
//     PDFJS_DIR=$PWD/package node viewer-test.js ../docs
// Needs: node, playwright (with a Chromium it can launch).
// Exit code 0 when every check passed.

const http = require('http');
const fs = require('fs');
const path = require('path');
const { chromium } = require('playwright');

const args = process.argv.slice(2);
const SITE = path.resolve(args[0] || '.');
const SHOTS = args.indexOf('--shots') >= 0 ? path.resolve(args[args.indexOf('--shots') + 1]) : null;
const PDFJS = process.env.PDFJS_DIR ? path.resolve(process.env.PDFJS_DIR) : null;
const VERSION = '3.11.174';
const TYPES = { '.html': 'text/html; charset=utf-8', '.json': 'application/json',
                '.pdf': 'application/pdf', '.js': 'text/javascript' };

let fails = 0;
function check(cond, msg, extra) {
  if (cond) console.log('  ok   ' + msg);
  else { fails++; console.log('  FAIL ' + msg + (extra !== undefined ? '  ' + JSON.stringify(extra) : '')); }
}

function serve(root) {
  return new Promise(res => {
    const srv = http.createServer((req, resp) => {
      let p = decodeURIComponent(new URL(req.url, 'http://x').pathname);
      if (p.endsWith('/')) p += 'index.html';
      const f = path.join(root, p);
      if (!f.startsWith(root)) { resp.writeHead(403); return resp.end(); }
      fs.readFile(f, (err, data) => {
        if (err) { resp.writeHead(404); return resp.end('not found'); }
        resp.writeHead(200, { 'Content-Type': TYPES[path.extname(f)] || 'application/octet-stream' });
        resp.end(data);
      });
    });
    srv.listen(0, '127.0.0.1', () => res(srv));
  });
}

async function routeCdn(ctx) {
  if (!PDFJS) return;
  await ctx.route(new RegExp('cdnjs\\.cloudflare\\.com/ajax/libs/pdf\\.js/' + VERSION.replace(/\./g, '\\.') + '/(.*)$'), route => {
    const name = /pdf\.js\/[^/]+\/(.*)$/.exec(route.request().url())[1];
    route.fulfill({ path: path.join(PDFJS, 'build', name), contentType: 'text/javascript',
                    headers: { 'Access-Control-Allow-Origin': '*' } });
  });
  await ctx.route(new RegExp('cdn\\.jsdelivr\\.net/npm/pdfjs-dist@' + VERSION.replace(/\./g, '\\.') + '/(.*)$'), route => {
    const name = /pdfjs-dist@[^/]+\/(.*)$/.exec(route.request().url())[1];
    route.fulfill({ path: path.join(PDFJS, name), headers: { 'Access-Control-Allow-Origin': '*' } });
  });
}

const frame = page => page.evaluate(() => new Promise(r => requestAnimationFrame(() => requestAnimationFrame(r))));

// where the reader is: page number and the fraction of that page above the bar
// (3 px of slack: scroll positions are whole pixels, page tops are not)
const READ = `(() => {
  const pages = [...document.querySelectorAll('.page')];
  const y = scrollY + document.getElementById('bar').offsetHeight + 3;
  let i = 0;
  for (let k = 0; k < pages.length; k++) { if (pages[k].getBoundingClientRect().top + scrollY <= y) i = k; else break; }
  const el = pages[i], t = el.getBoundingClientRect().top + scrollY;
  return { p: i + 1, o: (y - t) / el.offsetHeight, n: pages.length,
           ind: document.getElementById('pageind').textContent };
})()`;
const read = page => page.evaluate(READ);

async function scrollToPos(page, pos) {      // pos = 0-based page + fraction
  await page.evaluate(pos => {
    const pages = [...document.querySelectorAll('.page')];
    const bar = document.getElementById('bar').offsetHeight;
    const i = Math.min(pages.length - 1, Math.floor(pos)), el = pages[i];
    window.scrollTo(0, Math.round(el.getBoundingClientRect().top + scrollY - bar + (pos - i) * el.offsetHeight));
  }, pos);
  await frame(page); await page.waitForTimeout(400);
}

async function ready(page, n) {
  await page.waitForFunction(n => document.querySelectorAll('.page').length === n &&
    /^\d+ \/ \d+$/.test(document.getElementById('pageind').textContent), n, { timeout: 30000 });
  await page.waitForFunction(() => document.querySelector('.page.has-img'), null, { timeout: 30000 });
  await page.waitForTimeout(300);
}

// the section the table of contents marks as current, by its leading number
async function currentSection(page) {
  await page.click('#tocbtn');
  await page.waitForFunction(() => document.getElementById('toc').classList.contains('in'));
  const t = await page.evaluate(() => {
    const c = document.querySelector('.tocitem.cur');
    return c ? c.textContent : null;
  });
  await page.keyboard.press('Escape');
  await page.waitForFunction(() => document.getElementById('toc').hidden, null, { timeout: 3000 });
  const m = t && /^\s*([0-9]+(?:\.[0-9]+)*|[A-Z](?:\.[0-9]+)*)/.exec(t);
  return m ? m[1] : t;
}

async function newCtx(browser, opts = {}) {
  const ctx = await browser.newContext({ viewport: { width: opts.w || 1280, height: opts.h || 800 },
    deviceScaleFactor: 1, isMobile: !!opts.mobile, hasTouch: !!opts.mobile });
  await routeCdn(ctx);
  return ctx;
}
async function newPage(ctx, errors) {
  const page = await ctx.newPage();
  page.on('pageerror', e => errors.push(String(e)));
  page.on('console', m => { if (m.type() === 'error') errors.push(m.text()); });
  return page;
}
async function shot(page, name) { if (SHOTS) await page.screenshot({ path: path.join(SHOTS, name + '.png') }); }

(async () => {
  const manifest = JSON.parse(fs.readFileSync(path.join(SITE, 'manifest.json'), 'utf8'));
  const enPages = manifest.pages && manifest.pages.en, koPages = manifest.pages && manifest.pages.ko;
  const extra = Object.keys(manifest.docs || {}).filter(id => manifest.docs[id].pages);
  if (SHOTS) fs.mkdirSync(SHOTS, { recursive: true });
  const srv = await serve(SITE);
  const base = 'http://127.0.0.1:' + srv.address().port + '/';
  const browser = await chromium.launch();

  // ------------------------------------------------------------ first load
  console.log('desktop 1280x800: ' + base);
  {
    const ctx = await newCtx(browser), errors = [];
    const page = await newPage(ctx, errors);
    await page.goto(base);
    await ready(page, enPages);
    let r = await read(page);
    check(r.n === enPages, 'English edition opens first with ' + enPages + ' pages', r);
    check(r.ind === '1 / ' + enPages, 'page indicator', r.ind);
    check(await page.evaluate(() => document.getElementById('updated').textContent) === manifest.updated,
          'updated date shown');
    const href = await page.evaluate(() => document.getElementById('dl').getAttribute('href'));
    check(/\?v=/.test(href) && href.indexOf(String(manifest.version)) > 0, 'PDF URL carries the manifest version', href);
    await shot(page, 'desktop-first');

    // ---------------------------------------------------- table of contents
    check(await page.evaluate(() => !document.getElementById('tocbtn').disabled), 'contents button usable');
    await page.click('#tocbtn');
    await page.waitForFunction(() => document.getElementById('toc').classList.contains('in'));
    const toc = await page.evaluate(() => ({
      items: document.querySelectorAll('.tocitem').length,
      parts: document.querySelectorAll('.tocitem.part').length,
      focusInside: document.getElementById('toc').contains(document.activeElement)
    }));
    check(toc.items > 0, 'contents lists the bookmarks', toc);
    check(toc.focusInside, 'focus moves into the contents panel');
    await shot(page, 'desktop-toc');
    // Tab stays inside the open panel
    for (let i = 0; i < 6; i++) await page.keyboard.press('Tab');
    check(await page.evaluate(() => document.getElementById('toc').contains(document.activeElement)), 'Tab is trapped in the panel');
    await page.keyboard.press('Escape');
    await page.waitForFunction(() => document.getElementById('toc').hidden, null, { timeout: 3000 });
    check(true, 'Escape closes the panel');

    // go to the last numbered section through the contents
    await page.click('#tocbtn');
    await page.waitForFunction(() => document.getElementById('toc').classList.contains('in'));
    const target = await page.evaluate(() => {
      const bs = [...document.querySelectorAll('button.tocitem')].filter(b => /^\s*[0-9A-Z]/.test(b.textContent));
      const b = bs[bs.length - 1]; b.click(); return b.textContent;
    });
    await page.waitForFunction(() => document.getElementById('toc').hidden, null, { timeout: 3000 });
    await page.waitForTimeout(300);
    const sec = await currentSection(page);
    check(sec && target.trim().startsWith(sec), 'contents jumps to "' + target.trim().slice(0, 40) + '"', sec);

    // ------------------------------------------------- language at a section
    if (koPages) {
      await scrollToPos(page, Math.max(0, enPages * 0.6));
      const before = await currentSection(page);
      await page.click('#btn-ko');
      await ready(page, koPages);
      const after = await currentSection(page);
      check(before && before === after, 'switching to Korean keeps the section (' + before + ')', { before, after });
      check(await page.evaluate(() => document.documentElement.lang) === 'ko', 'html lang follows the edition');
      await page.click('#btn-en');
      await ready(page, enPages);
      const back = await currentSection(page);
      check(back === before, 'and back to English (' + back + ')', { before, back });
    } else {
      check(await page.evaluate(() => document.getElementById('btn-ko').disabled), 'Korean button locked when no Korean edition');
    }

    // ----------------------------------------------------- deep link #page=
    const p = Math.min(3, enPages);
    await page.goto(base + '#page=' + p);
    await ready(page, enPages);
    r = await read(page);
    check(r.p === p, '#page=' + p + ' opens that page', r);

    // ----------------------------------------- reading place across resizes
    await scrollToPos(page, Math.min(enPages - 1, 1) + 0.4);
    const r0 = await read(page);
    await page.setViewportSize({ width: 700, height: 800 }); await frame(page); await page.waitForTimeout(500);
    const r1 = await read(page);
    await page.setViewportSize({ width: 1280, height: 800 }); await frame(page); await page.waitForTimeout(500);
    const r2 = await read(page);
    check(r1.p === r0.p && Math.abs(r1.o - r0.o) < 0.03, 'narrowing the window keeps the place', { r0, r1 });
    check(r2.p === r0.p && Math.abs(r2.o - r0.o) < 0.03, 'widening it again returns to the same place', { r0, r2 });

    // ----------------------------------------------------- document tabs
    if (extra.length) {
      const id = extra[0], n = manifest.docs[id].pages.en || manifest.docs[id].pages.ko;
      await page.goto(base);
      await ready(page, enPages);
      check(await page.evaluate(() => !document.getElementById('tabs').hidden), 'tabs shown for ' + (1 + extra.length) + ' documents');
      await page.click('#tabs a[data-doc="' + id + '"]');
      await ready(page, n);
      check(page.url() === base + '?doc=' + id, 'tab click routes to ?doc=' + id, page.url());
      const veils = await page.evaluate(() => [...document.querySelectorAll('.veil')].map(v => v.dataset.sol));
      if (veils.length) {
        check(true, 'solution pages are covered (' + new Set(veils).size + ' solutions, ' + veils.length + ' pages)');
        if (SHOTS) {   // a covered solution page in view
          await page.evaluate(id => {
            document.querySelector('.veil[data-sol="' + id + '"]').scrollIntoView({ block: 'start' });
            (document.scrollingElement || document.documentElement).scrollTop -= 260;   // the end of the problem page too
          }, veils[0]);
          await page.waitForTimeout(400);
          await shot(page, 'desktop-problems');
        }
        const first = veils[0];
        await page.evaluate(id => {
          const v = document.querySelector('.veil[data-sol="' + id + '"]');
          v.scrollIntoView(); v.click();
        }, first);
        await page.waitForTimeout(200);
        check(await page.evaluate(id => !document.querySelector('.veil[data-sol="' + id + '"]'), first),
              'tapping a veil reveals solution ' + first);
        await page.reload(); await ready(page, n);
        check(await page.evaluate(id => !document.querySelector('.veil[data-sol="' + id + '"]'), first),
              'a revealed solution stays revealed after reload (sessionStorage)');
        await page.click('#tocbtn');
        await page.waitForFunction(() => !document.getElementById('solall').hidden);
        await page.click('#solall');
        await page.waitForTimeout(200);
        check(await page.evaluate(() => document.querySelectorAll('.veil').length) === 0, 'reveal-all button');
        await page.click('#solall');
        await page.waitForTimeout(200);
        check(await page.evaluate(() => document.querySelectorAll('.veil').length) === veils.length, 'cover-all button');
        await page.keyboard.press('Escape');
      }
      await page.goBack();
      await ready(page, enPages);
      check(page.url() === base, 'Back returns to the first document', page.url());
    }
    check(errors.length === 0, 'no console errors', errors.slice(0, 3));
    await ctx.close();
  }

  // ------------------------------------------------------------ phone
  console.log('phone 375x667');
  {
    const ctx = await newCtx(browser, { w: 375, h: 667, mobile: true }), errors = [];
    const page = await newPage(ctx, errors);
    await page.goto(base);
    await ready(page, enPages);
    const lay = await page.evaluate(() => ({
      overflow: document.documentElement.scrollWidth - innerWidth,
      bar: document.getElementById('bar').getBoundingClientRect().height
    }));
    check(lay.overflow <= 0, 'no horizontal scroll', lay);
    await page.click('#tocbtn');
    await page.waitForFunction(() => document.getElementById('toc').classList.contains('in'));
    await page.waitForTimeout(350);
    const sheet = await page.evaluate(() => {
      const r = document.getElementById('toc').getBoundingClientRect();
      return { top: r.top, bottom: r.bottom, h: innerHeight, w: r.width };
    });
    check(sheet.top > 0.2 * sheet.h && Math.abs(sheet.bottom - sheet.h) < 2, 'contents opens as a bottom sheet', sheet);
    await shot(page, 'phone-toc');
    await page.keyboard.press('Escape');
    check(errors.length === 0, 'no console errors', errors.slice(0, 3));
    await ctx.close();
  }

  await browser.close(); srv.close();
  console.log(fails ? fails + ' check(s) failed' : 'all checks passed');
  process.exit(fails ? 1 : 0);
})().catch(e => { console.error(e); process.exit(2); });
