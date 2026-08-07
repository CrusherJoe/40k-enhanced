// Discover BCP's login UI + auth network calls. Usage: node discover.mjs [url]
import { chromium } from 'playwright';

const START = process.argv[2] || 'https://www.bestcoastpairings.com/login';
const b = await chromium.launch({ headless: true });
const ctx = await b.newContext({ userAgent: 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0 Safari/537.36' });
const p = await ctx.newPage();

const auth = [];
p.on('request', r => {
  const u = r.url();
  if (/cognito|amazonaws|auth|login|token|signin/i.test(u)) auth.push(`${r.method()} ${u.slice(0,110)}`);
});

try {
  await p.goto(START, { waitUntil: 'domcontentloaded', timeout: 45000 });
  await p.waitForTimeout(4000);
  console.log('URL after load:', p.url());
  console.log('TITLE:', await p.title());

  const inputs = await p.$$eval('input', els => els.map(e => ({ type: e.type, name: e.name, id: e.id, ph: e.placeholder, aria: e.getAttribute('aria-label') })));
  console.log('INPUTS:', JSON.stringify(inputs, null, 1));

  const buttons = await p.$$eval('button, a[role=button], [class*=button]', els =>
    els.map(e => (e.innerText || e.getAttribute('aria-label') || '').trim()).filter(t => t && t.length < 40).slice(0, 25));
  console.log('BUTTONS/LINKS:', JSON.stringify([...new Set(buttons)]));

  const bodytext = (await p.innerText('body')).slice(0, 400).replace(/\n+/g, ' | ');
  console.log('BODY SNIPPET:', bodytext);
} catch (e) {
  console.log('ERROR:', String(e).slice(0, 200));
}
console.log('AUTH-RELATED REQUESTS:', JSON.stringify([...new Set(auth)], null, 1));
await b.close();
