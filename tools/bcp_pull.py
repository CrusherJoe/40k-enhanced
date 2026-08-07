#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""bcp_pull.py — pull an event roster from BestCoastPairings.

BCP's site (bestcoastpairings.com) is a React SPA; the roster loads from its public
JSON API at newprod-api.bestcoastpairings.com/v1. This fetches the full player list for
an event and emits, for each player: name, faction, sub-faction (disposition), team,
and a LINK to that player's list page (bestcoastpairings.com/list/<listId>).

API notes (verified 2026-07-29 against Lone Star Open 2026, event VAiZ9vjF61Rk):
  - Header `client-id: web-app` is required (no user login needed for the roster).
  - GET /v1/players?eventId=<id>&limit=<N<100>&expand[]=user&expand[]=faction
      &expand[]=subFaction&expand[]=team  ->  {"data": [...], "nextKey": "<cursor>"}
    Cursor pagination: pass the returned nextKey back as ?nextKey=... until it stops.
    Page size MUST be < 100 (limit>=100 -> 409 "limit must be less than 100").
  - GET /v1/events/<id>  ->  event metadata (name, totalPlayers, ...).
  - Each player row carries listId + listUrl ("/list/<id>"). The decklist TEXT itself
    (/armylists/<id>) requires an authenticated BCP user token (401 otherwise); this
    tool only needs the public roster + the link. See --save note for the text route.

Usage:
  python3 tools/bcp_pull.py VAiZ9vjF61Rk                 # print roster table
  python3 tools/bcp_pull.py VAiZ9vjF61Rk --json          # JSON rows
  python3 tools/bcp_pull.py VAiZ9vjF61Rk --store data/bcp/lso2026.json
  python3 tools/bcp_pull.py VAiZ9vjF61Rk --html out.html # linked HTML roster
"""
import argparse, json, os, sys, time, urllib.parse, urllib.request

API = "https://newprod-api.bestcoastpairings.com/v1"
SITE = "https://www.bestcoastpairings.com"
UA = ("Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) "
      "Chrome/124.0 Safari/537.36")
HEADERS = {"User-Agent": UA, "client-id": "web-app", "Accept": "application/json"}
DELAY_S = 0.4          # gentle between pages
PAGE = 99              # must be < 100


def _get(path, params):
    url = f"{API}{path}?" + urllib.parse.urlencode(params, doseq=True)
    req = urllib.request.Request(url, headers=HEADERS)
    with urllib.request.urlopen(req, timeout=30) as r:
        return json.load(r)


def event_meta(event_id):
    return _get(f"/events/{event_id}", {})


def fetch_players(event_id):
    """Paginate the full player roster via the nextKey cursor."""
    # faction + team are returned by default; expanding them actually blanks them out
    # (expand[]=faction -> "faction":{}). Only user + subFaction need expanding.
    params = [("eventId", event_id), ("limit", PAGE),
              ("expand[]", "user"), ("expand[]", "subFaction")]
    out, seen_keys, cursor = [], set(), None
    while True:
        p = list(params) + ([("nextKey", cursor)] if cursor else [])
        d = _get("/players", p)
        rows = d.get("data", [])
        out.extend(rows)
        nk = d.get("nextKey")
        # stop when the feed is exhausted or the cursor stalls/repeats
        if not rows or not nk or nk in seen_keys:
            break
        seen_keys.add(nk)
        cursor = nk
        time.sleep(DELAY_S)
    return out


def fetch_lists(rows, outdir, token, delay=0.15):
    """Pull each player's decklist TEXT (armyListText) into outdir/<slug>.txt and the raw
    JSON into outdir/_raw/<slug>.json. Requires a logged-in BCP bearer token (the roster
    itself is public, but /armylists/<id> is not). Resumable: skips slugs already saved.

    Getting the token: log into bestcoastpairings.com, DevTools Console ->
      Object.entries(localStorage).filter(([k])=>/accessToken/.test(k)).forEach(([k,v])=>console.log(v))
    Tokens are short-lived (~1h). Pass raw (with or without a leading 'Bearer ')."""
    import re as _re
    token = token.strip()
    if token.lower().startswith("bearer "):
        token = token[7:]
    h = dict(HEADERS, authorization="Bearer " + token)
    rawdir = os.path.join(outdir, "_raw")
    os.makedirs(rawdir, exist_ok=True)

    def slug(r):
        n = _re.sub(r"[^a-z0-9]+", "-", r["name"].lower()).strip("-")
        f = _re.sub(r"[^a-z0-9]+", "-", str(r["faction"] or "").lower()).strip("-")
        return f"{n}_{f}_{r['listId']}"

    todo = [r for r in rows if r["listId"]]
    ok = err = skip = 0
    for r in todo:
        base = slug(r)
        if os.path.exists(os.path.join(outdir, base + ".txt")):
            skip += 1
            continue
        try:
            req = urllib.request.Request(f"{API}/armylists/{r['listId']}", headers=h)
            with urllib.request.urlopen(req, timeout=30) as resp:
                d = json.load(resp)
            with open(os.path.join(outdir, base + ".txt"), "w", encoding="utf-8") as fh:
                fh.write(f"# {r['name']} | {r['faction']} | {r['detachment']} | team={r['team']}\n")
                fh.write(f"# list: {r['listUrl']}  status={d.get('listStatus')}\n\n")
                fh.write(d.get("armyListText") or "")
            json.dump(d, open(os.path.join(rawdir, base + ".json"), "w"))
            ok += 1
        except Exception as ex:
            err += 1
            print(f"# ERR {r['name']} {r['listId']}: {str(ex)[:70]}", file=sys.stderr)
        time.sleep(delay)
    print(f"# fetch-lists: {ok} saved, {skip} already present, {err} errors -> {outdir}/",
          file=sys.stderr)


def row(p):
    u = p.get("user") or {}
    name = " ".join(x for x in (u.get("firstName"), u.get("lastName")) if x).strip() \
        or p.get("name") or "(unknown)"
    lid = p.get("listId") or p.get("armyListId") or p.get("armyListObjectId")
    return {
        "name": name,
        "faction": (p.get("faction") or {}).get("name"),
        "detachment": (p.get("subFaction") or {}).get("name"),
        "team": (p.get("team") or {}).get("name"),
        "dropped": p.get("dropped", False),
        "listId": lid,
        "listUrl": (SITE + "/list/" + lid) if lid else None,
    }


def to_html(rows, meta, event_id):
    ev = meta.get("name", event_id)
    total = len(rows)
    withlist = sum(1 for r in rows if r["listId"])
    facs = {}
    for r in rows:
        facs[r["faction"]] = facs.get(r["faction"], 0) + 1
    opts = "".join(f'<option value="{f}">{f} ({n})</option>'
                   for f, n in sorted(facs.items(), key=lambda kv: (-kv[1], str(kv[0]))))
    trs = []
    for i, r in enumerate(sorted(rows, key=lambda r: r["name"].lower()), 1):
        nm = r["name"]
        cell = (f'<a href="{r["listUrl"]}" target="_blank" rel="noopener">{nm}</a>'
                if r["listUrl"] else f'{nm} <span class="nolist">(no list)</span>')
        drop = ' <span class="drop">dropped</span>' if r["dropped"] else ""
        trs.append(
            f'<tr data-fac="{r["faction"] or ""}"><td class="n">{i}</td>'
            f'<td>{cell}{drop}</td><td>{r["faction"] or ""}</td>'
            f'<td>{r["detachment"] or ""}</td><td>{r["team"] or ""}</td></tr>')
    return f"""<!doctype html><meta charset="utf-8">
<title>{ev} — roster</title>
<style>
 body{{font:15px/1.5 system-ui,sans-serif;margin:0;background:#f6f7f9;color:#1a1a1a}}
 header{{background:#1a1f2b;color:#fff;padding:18px 24px}}
 header h1{{margin:0 0 4px;font-size:20px}} header p{{margin:0;opacity:.8;font-size:13px}}
 .bar{{padding:12px 24px;background:#fff;border-bottom:1px solid #e2e4e8;position:sticky;top:0}}
 input,select{{font:14px system-ui;padding:6px 8px;border:1px solid #ccc;border-radius:6px}}
 table{{border-collapse:collapse;width:100%;background:#fff}}
 th,td{{text-align:left;padding:8px 24px;border-bottom:1px solid #eee}}
 th{{font-size:12px;text-transform:uppercase;letter-spacing:.04em;color:#666;cursor:pointer}}
 td.n{{color:#999;width:40px}} a{{color:#2456c4;text-decoration:none}} a:hover{{text-decoration:underline}}
 .nolist{{color:#b00;font-size:12px}} .drop{{color:#a60;font-size:11px;border:1px solid #d9b;border-radius:4px;padding:0 4px}}
</style>
<header><h1>{ev}</h1>
<p>{total} players &middot; {withlist} with a submitted list &middot; each name links to that player's BCP list</p></header>
<div class="bar">
 <input id="q" placeholder="search name / team…" oninput="flt()">
 <select id="fac" onchange="flt()"><option value="">All factions ({total})</option>{opts}</select>
</div>
<table><thead><tr><th>#</th><th>Player</th><th>Faction</th><th>Detachment</th><th>Team</th></tr></thead>
<tbody id="tb">{"".join(trs)}</tbody></table>
<script>
 function flt(){{var q=document.getElementById('q').value.toLowerCase(),
   f=document.getElementById('fac').value;
   document.querySelectorAll('#tb tr').forEach(function(tr){{
     var okf=!f||tr.dataset.fac===f, okq=!q||tr.textContent.toLowerCase().indexOf(q)>-1;
     tr.style.display=(okf&&okq)?'':'none';}});}}
</script>"""


def main():
    ap = argparse.ArgumentParser(description="Pull a BestCoastPairings event roster (names + list links).")
    ap.add_argument("event_id", help="BCP event id, e.g. VAiZ9vjF61Rk (from /event/<id> in the URL)")
    ap.add_argument("--json", action="store_true", help="emit JSON rows to stdout")
    ap.add_argument("--store", default=None, help="write the full JSON archive to this path")
    ap.add_argument("--html", default=None, help="write a linked, filterable HTML roster to this path")
    ap.add_argument("--fetch-lists", dest="fetch_lists", default=None, metavar="DIR",
                    help="pull each player's decklist TEXT into DIR (needs a bearer token; see --token-file)")
    ap.add_argument("--token-file", dest="token_file", default=".env.bcp",
                    help="file holding the BCP bearer token (BCP_TOKEN=... or the raw token); default .env.bcp")
    a = ap.parse_args()

    meta = event_meta(a.event_id)
    players = fetch_players(a.event_id)
    rows = [row(p) for p in players]
    withlist = sum(1 for r in rows if r["listId"])
    print(f"# {meta.get('name', a.event_id)} — {len(rows)} players "
          f"({withlist} with a list, {len(rows)-withlist} without)", file=sys.stderr)

    if a.store:
        os.makedirs(os.path.dirname(a.store) or ".", exist_ok=True)
        json.dump({"event": {"id": a.event_id, "name": meta.get("name"),
                             "totalPlayers": meta.get("totalPlayers"),
                             "eventDate": meta.get("eventDate")},
                   "players": rows}, open(a.store, "w"), indent=1)
        print(f"# archive -> {a.store}", file=sys.stderr)

    if a.html:
        os.makedirs(os.path.dirname(a.html) or ".", exist_ok=True)
        open(a.html, "w", encoding="utf-8").write(to_html(rows, meta, a.event_id))
        print(f"# html roster -> {a.html}", file=sys.stderr)

    if a.fetch_lists:
        token = None
        try:                                              # preferred: auto-refresh from creds in .env.bcp
            sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
            import bcp_auth
            token = bcp_auth.get_token()
        except Exception as e:                            # fallback: a raw/BCP_TOKEN= token file
            if os.path.exists(a.token_file):
                raw = open(a.token_file).read().strip()
                token = raw.split("=", 1)[1].strip() if raw.startswith("BCP_TOKEN=") else raw
            if not token:
                sys.exit(f"--fetch-lists needs BCP creds in .env.bcp (see .env.bcp.example): {e}")
        fetch_lists(rows, a.fetch_lists, token)

    if a.json:
        print(json.dumps(rows, indent=1)); return

    print(f"{'#':>3}  {'PLAYER':22} {'FACTION':22} {'DETACHMENT':22} LIST")
    print("-" * 100)
    for i, r in enumerate(sorted(rows, key=lambda r: r["name"].lower()), 1):
        print(f"{i:>3}  {r['name'][:21]:22} {str(r['faction'])[:21]:22} "
              f"{str(r['detachment'])[:21]:22} {r['listUrl'] or '(none)'}")


if __name__ == "__main__":
    main()
