#!/usr/bin/env python3
"""bcp_auth.py — supply a FRESH, BCP-accepted access token automatically. No more copy-pasting tokens.

THE KEY FINDING (learned by diffing a working browser request):
  BCP's API has two gates. (1) A WAF blocks the `Python-urllib` User-Agent — every pull tool sends a Chrome
  UA, so that's handled. (2) The API only honors access tokens minted through BCP's OWN login server
  (auth.bestcoastpairings.com — a custom OAuth2 authorize->code->token flow, NOT direct Cognito). A token we
  mint headlessly via Cognito InitiateAuth is valid at Cognito yet REJECTED by BCP ("invalid authorization
  token"), because it never went through that login flow / server-side session registration.

  SO: we log in the way the browser does — a headless Chromium drives the real login form (tools/bcp_login/
  login.mjs) and hands back the blessed tokens. get_token() runs it on demand and caches the result, so
  callers always get a working token and a human never pastes one again.

Setup (.env.bcp, gitignored — NEVER commit):
    BCP_EMAIL=you@example.com
    BCP_PASSWORD=your-bcp-password
    # BCP_TOKEN=eyJ...        # optional manual fallback (a browser access token, ~1h) if node/browser absent
One-time deps (also see tools/refresh.py / portability note): node + `npm --prefix tools/bcp_login install`
  + `npx --prefix tools/bcp_login playwright install --with-deps chromium`.

  from bcp_auth import get_token ;  tok = get_token()   # a working access token (add 'Bearer ' yourself)
  python3 tools/bcp_auth.py                             # login + health-check against BCP's real API
"""
import os, json, time, base64, subprocess, urllib.request, urllib.error

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
ENV = os.path.join(ROOT, ".env.bcp")
CACHE = os.path.join(ROOT, "data", ".bcp_token_cache.json")
LOGIN_JS = os.path.join(ROOT, "tools", "bcp_login", "login.mjs")
UA = "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0 Safari/537.36"


def _env():
    d = {}
    if os.path.exists(ENV):
        for ln in open(ENV):
            ln = ln.strip()
            if ln and not ln.startswith("#") and "=" in ln:
                k, v = ln.split("=", 1)
                d[k.strip()] = v.strip()
    return d


def _exp(tok):
    try:
        p = tok.split(".")[1]; p += "=" * (-len(p) % 4)
        return json.loads(base64.urlsafe_b64decode(p)).get("exp", 0)
    except Exception:
        return 0


def _valid(tok, skew=120):
    return bool(tok) and _exp(tok) - skew > time.time()


def _cache_read():
    if os.path.exists(CACHE):
        try:
            return json.load(open(CACHE))
        except Exception:
            pass
    return {}


def _cache_write(**kw):
    d = _cache_read(); d.update({k: v for k, v in kw.items() if v})
    os.makedirs(os.path.dirname(CACHE), exist_ok=True)
    json.dump(d, open(CACHE, "w"))


def browser_login(timeout=150):
    """Drive the real BCP login in headless Chromium and return {access_token, id_token, refresh_token}.
    Requires node + the tools/bcp_login deps. Raises RuntimeError on failure."""
    if not os.path.exists(LOGIN_JS):
        raise RuntimeError(f"missing {LOGIN_JS}")
    try:
        r = subprocess.run(["node", LOGIN_JS], capture_output=True, text=True, timeout=timeout, cwd=ROOT)
    except FileNotFoundError:
        raise RuntimeError("node not found — install Node.js and the bcp_login deps (see module docstring)")
    except subprocess.TimeoutExpired:
        raise RuntimeError("browser login timed out")
    line = next((l for l in r.stdout.splitlines() if l.strip().startswith("{")), None)
    if not line:
        raise RuntimeError("browser login failed: " + (r.stderr.strip()[-200:] or "no token in output"))
    toks = json.loads(line)
    if not toks.get("access_token"):
        raise RuntimeError("browser login returned no access_token")
    _cache_write(access_token=toks["access_token"], refresh_token=toks.get("refresh_token"))
    return toks


def get_token(force=False):
    """Return a BCP-accepted access token. Uses a cached token while valid, else logs in via the headless
    browser (the only tokens BCP honors). Falls back to a manual BCP_TOKEN if the browser path is unavailable."""
    if not force:
        cached = _cache_read().get("access_token")
        if _valid(cached):
            return cached
    env = _env()
    if env.get("BCP_EMAIL") and env.get("BCP_PASSWORD"):
        try:
            return browser_login()["access_token"]
        except Exception as e:
            if _valid(env.get("BCP_TOKEN")):
                print(f"# bcp_auth: browser login failed ({str(e)[:80]}); using manual BCP_TOKEN", flush=True)
                return env["BCP_TOKEN"].strip()
            raise
    if _valid(env.get("BCP_TOKEN")):
        return env["BCP_TOKEN"].strip()
    raise RuntimeError("no BCP auth: set BCP_EMAIL+BCP_PASSWORD in .env.bcp (auto browser login) "
                       "or paste a browser access token as BCP_TOKEN")


def api_ok(tok):
    """Health check: does this token WORK against BCP's authed API (not just Cognito)? -> (ok, detail)."""
    try:
        h = {"User-Agent": UA, "client-id": "web-app", "Accept": "*/*", "env": "bcp",
             "origin": "https://www.bestcoastpairings.com", "referer": "https://www.bestcoastpairings.com/"}
        pl = json.load(urllib.request.urlopen(urllib.request.Request(
            "https://newprod-api.bestcoastpairings.com/v1/players?limit=5&eventId=6C7fsq4RocJ4", headers=h), timeout=20))
        players = pl.get("data", pl) if isinstance(pl, dict) else pl
        lid = next((p.get("armyListId") or p.get("listId") for p in players if p.get("armyListId") or p.get("listId")), None)
        if not lid:
            return False, "could not resolve a test list id"
        h2 = dict(h, authorization="Bearer " + tok)
        d = json.load(urllib.request.urlopen(urllib.request.Request(
            f"https://newprod-api.bestcoastpairings.com/v1/armylists/{lid}", headers=h2), timeout=20))
        return True, f"fetched armyListText ({len(d.get('armyListText') or '')} chars)"
    except urllib.error.HTTPError as e:
        return False, f"HTTP {e.code} {e.read()[:80].decode(errors='replace')}"


if __name__ == "__main__":
    try:
        t = get_token(force=True)
    except Exception as e:
        print("login failed:", e); raise SystemExit(1)
    left = int(_exp(t) - time.time())
    ok, detail = api_ok(t)
    print(f"logged in — token valid ~{left//60} min; BCP API: " + ("WORKS ✓ — " if ok else "REJECTED ✗ — ") + detail)
