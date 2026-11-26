// Interaction checks: menu drop-down, sliders, hover states. Writes screenshots to _tools/out/states.
import { createRequire } from 'node:module';
import fs from 'node:fs';
import path from 'node:path';
import { fileURLToPath, pathToFileURL } from 'node:url';
const require = createRequire(import.meta.url);
const { chromium } = require(process.env.PLAYWRIGHT_CORE || 'playwright-core');
const HERE = path.dirname(fileURLToPath(import.meta.url));
const ROOT = path.dirname(HERE);
const OUT = path.join(HERE, 'out', 'states'); fs.mkdirSync(OUT, { recursive: true });
const MOBILE_UA = 'Mozilla/5.0 (iPhone; CPU iPhone OS 17_0 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.0 Mobile/15E148 Safari/604.1';
const url = pathToFileURL(path.join(ROOT, 'index.html')).href;
const browser = await chromium.launch({ headless: true });
const errors = [];
async function open(w, h, mobile) {
  const ctx = await browser.newContext({ viewport: { width: w, height: h }, isMobile: mobile, hasTouch: mobile, ...(mobile ? { userAgent: MOBILE_UA } : {}) });
  await ctx.route(/calendly\.com/, (r) => r.abort());
  const page = await ctx.newPage();
  page.on('pageerror', (e) => errors.push(String(e)));
  page.on('console', (m) => { if (m.type() === 'error' && !/calendly|ERR_FAILED/.test(m.text())) errors.push(m.text()); });
  await page.goto(url, { waitUntil: 'load' }); await page.evaluate(() => document.fonts.ready);
  return page;
}
// menu
for (const [name, w, h] of [['mobile-390', 390, 844], ['tablet-768', 768, 1024]]) {
  const page = await open(w, h, true);
  await page.click('.menu-toggle'); await page.waitForTimeout(900);
  await page.screenshot({ path: path.join(OUT, `${name}-nav-open.png`) });
  console.log(name, 'menu open:', await page.getAttribute('.menu-toggle', 'aria-expanded'));
  await page.click('.site-nav__link >> nth=1'); await page.waitForTimeout(900);
  console.log(name, 'after link click:', await page.getAttribute('.menu-toggle', 'aria-expanded'), 'scrollY', await page.evaluate(() => Math.round(scrollY)), 'projects top', await page.evaluate(() => Math.round(document.getElementById('Projects').getBoundingClientRect().top)));
  await page.evaluate(() => scrollTo(0, 0)); await page.waitForTimeout(600);
  await page.click('.menu-toggle'); await page.waitForTimeout(500); await page.keyboard.press('Escape');
  const afterEscape = await page.getAttribute('.menu-toggle', 'aria-expanded');
  await page.click('.menu-toggle'); await page.waitForTimeout(500); await page.mouse.click(40, h - 200);
  console.log(name, 'after Escape:', afterEscape, '| after outside click:', await page.getAttribute('.menu-toggle', 'aria-expanded'));
  await page.context().close();
}
// sliders at desktop
{
  const page = await open(1440, 900, false);
  const tx = (sel) => page.evaluate((s) => new DOMMatrix(getComputedStyle(document.querySelector(s)).transform).m41, sel);
  await page.evaluate(() => document.getElementById('Projects').scrollIntoView()); await page.waitForTimeout(500);
  const p = '#Projects [data-slider-track]';
  console.log('projects start', await tx(p), 'prev disabled', await page.getAttribute('#Projects [data-slider-prev]', 'aria-disabled'));
  await page.click('#Projects [data-slider-next]'); await page.waitForTimeout(450); console.log('projects next x1', await tx(p));
  await page.click('#Projects [data-slider-next]'); await page.waitForTimeout(450); console.log('projects next x2', await tx(p));
  for (let i = 0; i < 25; i++) await page.click('#Projects [data-slider-next]', { force: true });
  await page.waitForTimeout(450); console.log('projects end', await tx(p), 'next disabled', await page.getAttribute('#Projects [data-slider-next]', 'aria-disabled'));
  await page.screenshot({ path: path.join(OUT, 'desktop-projects-end.png') });
  for (let i = 0; i < 25; i++) await page.click('#Projects [data-slider-prev]', { force: true });
  await page.waitForTimeout(450);
  // drag two cards to the left with the mouse
  const box = await page.locator('#Projects .slider__slide >> nth=1').boundingBox();
  await page.mouse.move(box.x + 100, box.y + 100); await page.mouse.down(); await page.mouse.move(box.x - 300, box.y + 110, { steps: 12 }); await page.waitForTimeout(350); await page.mouse.up(); await page.waitForTimeout(450);
  console.log('projects after drag', await tx(p), 'url unchanged', page.url() === url);
  await page.evaluate(() => document.getElementById('Reviews').scrollIntoView()); await page.waitForTimeout(400);
  const r = '#Reviews [data-slider-track]';
  const hgt = () => page.evaluate((s) => document.querySelector(s).getBoundingClientRect().height, r);
  console.log('reviews start', await tx(r), 'height', await hgt());
  await page.click('#Reviews [data-slider-next]'); await page.waitForTimeout(500); console.log('reviews next', await tx(r), 'height', await hgt());
  await page.screenshot({ path: path.join(OUT, 'desktop-reviews-next.png') });
  // hover states
  await page.evaluate(() => scrollTo(0, 0)); await page.waitForTimeout(300);
  await page.hover('.hero .button'); await page.waitForTimeout(700); await page.screenshot({ path: path.join(OUT, 'hover-hero-button.png'), clip: { x: 80, y: 500, width: 360, height: 140 } });
  await page.hover('.button--outline'); await page.waitForTimeout(700); await page.screenshot({ path: path.join(OUT, 'hover-contact.png'), clip: { x: 1180, y: 0, width: 180, height: 71 } });
  await page.evaluate(() => document.getElementById('Projects').scrollIntoView()); await page.waitForTimeout(400);
  for (let i = 0; i < 25; i++) await page.click('#Projects [data-slider-prev]', { force: true });
  await page.waitForTimeout(500);
  await page.hover('#Projects .card__more >> nth=0'); await page.waitForTimeout(900);
  const cb = await page.locator('#Projects .card >> nth=0').boundingBox();
  await page.screenshot({ path: path.join(OUT, 'hover-card.png'), clip: { x: cb.x - 20, y: cb.y - 20, width: cb.width + 40, height: cb.height + 40 } });
  // subscribe form
  await page.evaluate(() => document.querySelector('.site-footer').scrollIntoView()); await page.fill('.subscribe__field', 'test@example.com'); await page.click('.subscribe__submit'); await page.waitForTimeout(300);
  console.log('subscribe message visible:', await page.isVisible('.subscribe__message'), '| row hidden:', await page.isHidden('.subscribe__row'));
  await page.context().close();
}
// reviews on phone: one per view
{
  const page = await open(390, 844, true);
  await page.evaluate(() => document.getElementById('Reviews').scrollIntoView()); await page.waitForTimeout(400);
  const r = '#Reviews [data-slider-track]';
  const st = () => page.evaluate((s) => { const e = document.querySelector(s); return [new DOMMatrix(getComputedStyle(e).transform).m41, e.getBoundingClientRect().height]; }, r);
  console.log('phone reviews start', await st()); await page.click('#Reviews [data-slider-next]'); await page.waitForTimeout(500); console.log('phone reviews next', await st());
  await page.context().close();
}
console.log('page errors:', errors.length ? errors : 'none');
await browser.close();
