#!/usr/bin/env python3
"""bcp_auth.py — get a valid BCP access token WITHOUT manual copy-paste.

BCP auth is AWS Cognito (user pool us-east-1_ypv5m82ww, app client 5083iih0nitpn5enl02fkpr9bc — read from
any BCP access token's `iss`/`client_id`). Given your credentials (or a refresh token) in .env.bcp, this
logs in / refreshes and caches the access token, so bcp_pull / bcp_corpus / bcp_pull_gts never need a
hand-pasted token again.

.env.bcp (gitignored — NEVER commit; credentials, not just a token):
    BCP_EMAIL=you@example.com
    BCP_PASSWORD=...                 # your BCP login
    # optional alternatives / fallbacks:
    # BCP_REFRESH_TOKEN=eyJ...       # a Cognito refresh token (no password needed; long-lived)
    # BCP_TOKEN=eyJ...               # a manually-pasted access token (last-resort fallback)

Precedence each call: cached access token (if still valid) -> refresh token -> email+password login ->
manual BCP_TOKEN. New tokens are cached to data/.bcp_token_cache.json (gitignored).

  from bcp_auth import get_token ;  tok = get_token()          # raw access token (add 'Bearer ' yourself)
  python3 tools/bcp_auth.py                                    # print status / force a refresh
"""
import os, json, time, base64, urllib.request, urllib.error

COGNITO = "https://cognito-idp.us-east-1.amazonaws.com/"
CLIENT_ID = "5083iih0nitpn5enl02fkpr9bc"
ENV = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), ".env.bcp")
CACHE = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "data", ".bcp_token_cache.json")


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


def _cognito(payload):
    req = urllib.request.Request(COGNITO, data=json.dumps(payload).encode(),
                                 headers={"Content-Type": "application/x-amz-json-1.1",
                                          "X-Amz-Target": "AWSCognitoIdentityProviderService.InitiateAuth"})
    with urllib.request.urlopen(req, timeout=30) as r:
        return json.load(r)["AuthenticationResult"]


def _cache_read():
    if os.path.exists(CACHE):
        try:
            return json.load(open(CACHE))
        except Exception:
            pass
    return {}


def _cache_write(access, refresh=None):
    d = _cache_read()
    d["access_token"] = access
    if refresh:
        d["refresh_token"] = refresh
    os.makedirs(os.path.dirname(CACHE), exist_ok=True)
    json.dump(d, open(CACHE, "w"))


def get_token(force=False):
    """Return a valid BCP access token, refreshing/logging in as needed. Raises if nothing works."""
    env = _env()
    cache = _cache_read()
    if not force and _valid(cache.get("access_token")):
        return cache["access_token"]
    # 1) refresh token (cached or env) — no password needed
    rt = cache.get("refresh_token") or env.get("BCP_REFRESH_TOKEN")
    if rt:
        try:
            res = _cognito({"AuthFlow": "REFRESH_TOKEN_AUTH", "ClientId": CLIENT_ID,
                            "AuthParameters": {"REFRESH_TOKEN": rt}})
            _cache_write(res["AccessToken"])              # refresh flow returns no new refresh token
            return res["AccessToken"]
        except Exception as e:
            print(f"# bcp_auth: refresh failed ({str(e)[:60]}); trying password", flush=True)
    # 2) email + password
    if env.get("BCP_EMAIL") and env.get("BCP_PASSWORD"):
        res = _cognito({"AuthFlow": "USER_PASSWORD_AUTH", "ClientId": CLIENT_ID,
                        "AuthParameters": {"USERNAME": env["BCP_EMAIL"], "PASSWORD": env["BCP_PASSWORD"]}})
        _cache_write(res["AccessToken"], res.get("RefreshToken"))
        return res["AccessToken"]
    # 3) last resort: a manually-pasted access token
    if _valid(env.get("BCP_TOKEN")):
        return env["BCP_TOKEN"]
    raise RuntimeError("no BCP credentials in .env.bcp (need BCP_EMAIL+BCP_PASSWORD, or BCP_REFRESH_TOKEN, "
                       "or a fresh BCP_TOKEN)")


if __name__ == "__main__":
    try:
        t = get_token(force=True)
        left = int(_exp(t) - time.time())
        print(f"OK — access token valid for ~{left//60} min (cached to {CACHE})")
    except Exception as e:
        print("FAILED:", e)
