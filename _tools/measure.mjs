// Screenshots the replica the same way the live site was captured and compares
// element positions with the captured ones.
//   node _tools/measure.mjs [viewport ...]        (run "python _tools/build.py --debug" first)
import { createRequire } from 'node:module';
import fs from 'node:fs';
import path from 'node:path';
import { fileURLToPath, pathToFileURL } from 'node:url';
const require = createRequire(import.meta.url);
const { chromium } = require(process.env.PLAYWRIGHT_CORE || 'playwright-core');

const HERE = path.dirname(fileURLToPath(import.meta.url));
const ROOT = path.dirname(HERE);
const RESEARCH = path.join(path.dirname(ROOT), 'site-research');
const OUT = path.join(HERE, 'out');
const MOBILE_UA = 'Mozilla/5.0 (iPhone; CPU iPhone OS 17_0 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.0 Mobile/15E148 Safari/604.1';
const VP = { 'wide-1920': { w: 1920, h: 1080 }, 'desktop-1440': { w: 1440, h: 900 }, 'laptop-1280': { w: 1280, h: 800 }, 'tablet-992': { w: 992, h: 1024 }, 'tablet-768': { w: 768, h: 1024, mobile: true }, 'mobile-390': { w: 390, h: 844, mobile: true } };
for (const a of process.argv.slice(2)) { const m = /^w(\d+)$/.exec(a); if (m) VP[a] = { w: +m[1], h: 900, mobile: +m[1] < 1000 }; }   // any width: w834
const want = process.argv.slice(2).filter((a) => VP[a]);
const names = want.length ? want : ['desktop-1440', 'mobile-390'];
fs.mkdirSync(OUT, { recursive: true });

const browser = await chromium.launch({ headless: true });
for (const name of names) {
  const vp = VP[name];
  const ctx = await browser.newContext({ viewport: { width: vp.w, height: vp.h }, isMobile: !!vp.mobile, hasTouch: !!vp.mobile, ...(vp.mobile ? { userAgent: MOBILE_UA } : {}) });
  await ctx.route(/calendly\.com/, (r) => r.abort());      // blank in the live captures too
  const page = await ctx.newPage();
  const errors = [];
  page.on('pageerror', (e) => errors.push(String(e).slice(0, 200)));
  page.on('requestfailed', (r) => { if (!/calendly/.test(r.url())) errors.push('request failed: ' + r.url().slice(-80)); });
  await page.goto(pathToFileURL(path.join(ROOT, process.env.PAGE || 'index.html')).href, { waitUntil: 'load' });
  await page.evaluate(() => document.fonts.ready);
  await page.evaluate(async () => {
    const sleep = (ms) => new Promise((r) => setTimeout(r, ms));
    let y = 0, i = 0;
    while (i++ < 500) { const max = document.documentElement.scrollHeight - innerHeight; if (y >= max) break; y = Math.min(y + Math.round(innerHeight * 0.45), max); window.scrollTo(0, y); await sleep(120); }
    await sleep(400); window.scrollTo(0, 0); await sleep(600);
  });
  await page.evaluate(() => Promise.all([...document.images].map((i) => { i.loading = 'eager'; return i.decode().catch(() => { }); })));
  await page.waitForTimeout(500);
  const info = await page.evaluate(() => ({
    h: document.documentElement.scrollHeight, w: document.documentElement.scrollWidth,
    broken: [...document.images].filter((i) => i.complete && !i.naturalWidth).map((i) => i.getAttribute('src')),
    rects: [...document.querySelectorAll('[data-o]')].map((e) => { const r = e.getBoundingClientRect(); return { key: e.dataset.o, x: r.x + scrollX, y: r.y + scrollY, w: r.width, h: r.height }; }),
    sections: [...document.querySelectorAll('.site-header, .intro, main > section, .site-footer')].map((e) => { const r = e.getBoundingClientRect(); return { cls: e.className, y: r.y + scrollY, h: r.height }; }),
  }));
  const cdp = await ctx.newCDPSession(page);
  const { data } = await cdp.send('Page.captureScreenshot', { format: 'png', captureBeyondViewport: true, clip: { x: 0, y: 0, width: vp.w, height: info.h, scale: 1 } });
  fs.writeFileSync(path.join(OUT, (process.env.TAG || '') + name + '.png'), Buffer.from(data, 'base64'));
  fs.writeFileSync(path.join(OUT, name + '.json'), JSON.stringify(info, null, 1));

  console.log(`\n== ${name}: height ${info.h}, scrollWidth ${info.w}${info.w > vp.w ? ' OVERFLOW' : ''}${info.broken.length ? ' BROKEN ' + info.broken.join(',') : ''}${errors.length ? ' ERRORS ' + [...new Set(errors)].join(' | ') : ''}`);
  const refFile = path.join(RESEARCH, 'data', 'elements', name, 'home.json');
  const secFile = path.join(RESEARCH, 'data', 'sections', name, 'home.json');
  if (fs.existsSync(secFile)) {
    const ref = JSON.parse(fs.readFileSync(secFile, 'utf8'));
    console.log('sections (original y,h -> replica y,h):');
    ref.forEach((s, i) => { const m = info.sections[i]; console.log(`  ${s.label.padEnd(44)} ${s.y.toFixed(1)}, ${s.h.toFixed(1)}  ->  ${m ? m.y.toFixed(1) + ', ' + m.h.toFixed(1) : '?'}${m && (Math.abs(m.h - s.h) > 0.6) ? '   <-- ' + (m.h - s.h).toFixed(1) : ''}`); });
  }
  if (fs.existsSync(refFile) && info.rects.length) {
    const ref = new Map(JSON.parse(fs.readFileSync(refFile, 'utf8')).map((r) => [r.key, r]));
    let bad = 0, n = 0;
    for (const r of info.rects) {
      const t = ref.get(r.key); if (!t) { console.log('  (no original for ' + r.key + ')'); continue; }
      n++;
      const d = [r.x - t.x, r.y - t.y, r.w - t.w, r.h - t.h];
      if (d.some((v) => Math.abs(v) > 0.6)) { bad++; console.log(`  ${r.key.slice(0, 58).padEnd(58)} dx ${d[0].toFixed(1)}  dy ${d[1].toFixed(1)}  dw ${d[2].toFixed(1)}  dh ${d[3].toFixed(1)}`); }
    }
    console.log(`elements checked: ${n}, off by more than 0.6px: ${bad}`);
  }
  await ctx.close();
}
await browser.close();
