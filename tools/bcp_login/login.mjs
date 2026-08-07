// bcp_login/login.mjs — headless-browser login to BCP's OAuth server, emitting the blessed tokens as JSON.
// BCP's API only honors tokens minted through auth.bestcoastpairings.com (its custom OAuth2 authorize->code->
// token flow), NOT direct Cognito InitiateAuth. So we drive the real login form and read the tokens the SPA
// stores. Creds come from ../../.env.bcp (BCP_EMAIL / BCP_PASSWORD). Prints one JSON line to stdout on success.
import { chromium } from 'playwright';
import { readFileSync } from 'fs';
import { fileURLToPath } from 'url';
import { dirname, join } from 'path';

const HERE = dirname(fileURLToPath(import.meta.url));
const ENV = join(HERE, '..', '..', '.env.bcp');
const env = {};
for (const ln of readFileSync(ENV, 'utf8').split('\n')) {
  const s = ln.trim();
  if (s && !s.startsWith('#') && s.includes('=')) { const i = s.indexOf('='); env[s.slice(0, i).trim()] = s.slice(i + 1).trim(); }
}
if (!env.BCP_EMAIL || !env.BCP_PASSWORD) { console.error('need BCP_EMAIL and BCP_PASSWORD in .env.bcp'); process.exit(2); }

const UA = 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0 Safari/537.36';
const b = await chromium.launch({ headless: true, args: ['--no-sandbox'] });
const ctx = await b.newContext({ userAgent: UA });
const p = await ctx.newPage();
const fail = async (msg) => { console.error(msg); await b.close(); process.exit(1); };

try {
  await p.goto('https://www.bestcoastpairings.com/login', { waitUntil: 'domcontentloaded', timeout: 45000 });
  await p.waitForSelector('input[name=username]', { timeout: 30000 });
  await p.fill('input[name=username]', env.BCP_EMAIL);
  await p.fill('input[name=password]', env.BCP_PASSWORD);
  // click the SIGN IN button (not "Sign Up"/"My Warhammer")
  await p.click('button:has-text("SIGN IN"), button:has-text("Sign In")');
  // wait until we're back on the app origin (login completed) and tokens are stored
  await p.waitForURL(/www\.bestcoastpairings\.com/, { timeout: 45000 }).catch(() => {});
  let tokens = null;
  for (let i = 0; i < 30; i++) {                       // poll localStorage for the Cognito tokens
    tokens = await p.evaluate(() => {
      const out = {};
      for (const k of Object.keys(localStorage)) {
        if (k.endsWith('.accessToken')) out.access_token = localStorage.getItem(k);
        else if (k.endsWith('.idToken')) out.id_token = localStorage.getItem(k);
        else if (k.endsWith('.refreshToken')) out.refresh_token = localStorage.getItem(k);
      }
      return out.access_token ? out : null;
    });
    if (tokens) break;
    await p.waitForTimeout(1000);
  }
  if (!tokens) {
    const body = (await p.innerText('body').catch(() => '')).slice(0, 200).replace(/\n+/g, ' | ');
    await fail('login did not yield tokens (bad creds, MFA, or captcha?). page: ' + p.url() + ' :: ' + body);
  }
  console.log(JSON.stringify(tokens));
  await b.close();
} catch (e) {
  await fail('login error: ' + String(e).slice(0, 200));
}
