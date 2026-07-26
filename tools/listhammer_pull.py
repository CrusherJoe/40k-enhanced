#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""listhammer_pull.py — bounded, reference-only fetcher for listhammer.info.

Decodes the server-rendered `__NUXT_DATA__` payload into structured tournament-list
rows (faction / detachment / disposition / record / full decklist). Handy one-command
refresher for the current top-table feed.

★ IMPORTANT LIMITATION (verified 2026-07-26): listhammer only SERVER-RENDERS the ~25
  MOST-RECENT lists. `?page=N` returns the SAME 25 entries for every N (no pagination in
  the SSR payload) — the deeper archive is fetched CLIENT-SIDE from `/api/`, which the
  site's robots.txt Disallows for everyone. So this tool CANNOT retrieve "pages 2-4"; it
  refreshes the recent-25 only. Because that feed ROLLS OVER as new events post, running
  this periodically still catches genuinely new lists as they cycle into the recent set.
  For deeper history: browse the site yourself (a human browser hitting /api/ is fine) and
  paste lists, or ask the operator for an export.

★ POLITE-USE GUARDRAILS (listhammer.info robots.txt, checked 2026-07-26):
  - The generic policy is `Allow: /` with `Content-Signal: search=yes, ai-train=no,
    use=reference`. We ONLY hit `/?page=N` (under Allow: /), NEVER `/api/`
    (Disallow: /api/ for everyone). This is reference use, not training/scraping.
  - Bounded by default (pages 1..4), one request at a time with a delay. Do NOT
    crank the page count to crawl the whole archive — that stops being reference use.
  - It's for a human reading the meta; treat outputs as personal reference.

Usage:
  python3 tools/listhammer_pull.py                 # pages 1-4, print table
  python3 tools/listhammer_pull.py --pages 1-6     # explicit range
  python3 tools/listhammer_pull.py --faction "Adepta Sororitas"   # filter
  python3 tools/listhammer_pull.py --save DIR      # also write decklists to DIR/<slug>.txt
  python3 tools/listhammer_pull.py --json          # emit JSON rows to stdout
"""
import argparse, json, os, re, sys, time, urllib.request

BASE = "https://listhammer.info/?page={}"
UA = ("Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) "
      "Chrome/124.0 Safari/537.36")
DELAY_S = 1.5          # be gentle: one page every ~1.5s
MAX_PAGES = 12         # hard cap so this can't become a crawler


def fetch(page):
    req = urllib.request.Request(BASE.format(page), headers={"User-Agent": UA})
    with urllib.request.urlopen(req, timeout=30) as r:
        return r.read().decode("utf-8", "ignore")


def decode_nuxt(html):
    """Resolve Nuxt's devalue flat-array payload -> list-entry dicts."""
    m = re.search(r'id="__NUXT_DATA__"[^>]*>(.*?)</script>', html, re.S)
    if not m:
        return []
    arr = json.loads(m.group(1))

    def R(i, depth=0, seen=None):
        seen = seen or set()
        if not isinstance(i, int) or i in seen or depth > 8:
            return i
        v = arr[i]
        seen = seen | {i}
        if isinstance(v, dict):
            return {k: R(x, depth + 1, seen) for k, x in v.items()}
        if isinstance(v, list):
            return [R(x, depth + 1, seen) for x in v]
        return v

    out = []
    for idx, v in enumerate(arr):
        if isinstance(v, dict) and "listText" in v and "faction" in v:
            out.append(R(idx))
    return out


def parse_range(s):
    if not s:
        return range(1, 5)
    if "-" in s:
        a, b = s.split("-", 1)
        return range(int(a), int(b) + 1)
    return range(int(s), int(s) + 1)


def slug(e, i):
    f = re.sub(r"[^a-z0-9]+", "-", str(e.get("faction", "")).lower()).strip("-")
    d = re.sub(r"[^a-z0-9]+", "-", str(e.get("detachment", "")).lower()).strip("-")[:24]
    return f"{f}_{d or i}"


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--pages", default="1-4", help="page range, e.g. 1-4 (default) or 3")
    ap.add_argument("--faction", default=None, help="filter to one faction (substring)")
    ap.add_argument("--save", default=None, help="dir to write decklists to")
    ap.add_argument("--store", default=None,
                    help="JSON archive to ACCUMULATE into (dedup by listUid). Run periodically "
                         "to build the meta dataset from the rolling recent-25 with no copy-paste.")
    ap.add_argument("--json", action="store_true", help="emit JSON rows")
    a = ap.parse_args()

    pages = list(parse_range(a.pages))
    if any(p > MAX_PAGES for p in pages):
        sys.exit(f"refusing pages beyond {MAX_PAGES} — this is a reference tool, not a crawler.")

    rows, seen = [], set()
    for p in pages:
        try:
            entries = decode_nuxt(fetch(p))
        except Exception as ex:
            print(f"# page {p}: fetch/parse failed: {ex}", file=sys.stderr)
            continue
        new = 0
        for e in entries:
            k = e.get("listUid") or (str(e.get("faction")), str(e.get("detachment")),
                                     e.get("wins"), str(e.get("eventName")))
            if k in seen:
                continue
            seen.add(k)
            rows.append(e)
            new += 1
        print(f"# page {p}: {len(entries)} entries, {new} new (running total {len(rows)})",
              file=sys.stderr)
        if p != pages[-1]:
            time.sleep(DELAY_S)

    # ACCUMULATE: merge this pull into a growing archive keyed by listUid so periodic
    # runs build up the meta dataset from the rolling recent-25 (no copy-paste, no /api/).
    if a.store:
        arch = {}
        if os.path.exists(a.store):
            try:
                for e in json.load(open(a.store)):
                    arch[str(e.get("listUid") or e.get("_k"))] = e
            except Exception:
                pass
        before = len(arch)
        for e in rows:
            arch[str(e.get("listUid") or id(e))] = e
        os.makedirs(os.path.dirname(a.store) or ".", exist_ok=True)
        json.dump(list(arch.values()), open(a.store, "w"), indent=1)
        print(f"# archive {a.store}: {before} -> {len(arch)} lists (+{len(arch) - before} new this run)",
              file=sys.stderr)

    if a.faction:
        rows = [e for e in rows if a.faction.lower() in str(e.get("faction", "")).lower()]

    if a.save:
        os.makedirs(a.save, exist_ok=True)
        for i, e in enumerate(rows):
            with open(os.path.join(a.save, slug(e, i) + ".txt"), "w") as fh:
                fh.write(f"{e.get('faction')} | {e.get('detachment')} | {e.get('disposition')} | "
                         f"{e.get('wins')}-{e.get('draws')}-{e.get('losses')} | {e.get('eventName')}\n\n")
                fh.write(e.get("listText", ""))
        print(f"# wrote {len(rows)} decklists to {a.save}/", file=sys.stderr)

    if a.json:
        print(json.dumps([{k: e.get(k) for k in
                           ("faction", "detachment", "disposition", "wins", "draws",
                            "losses", "eventName")} for e in rows], indent=1))
        return

    print(f"{'FACTION':20} {'DETACHMENT':34} {'DISPOSITION':15} {'W-D-L':7} EVENT")
    print("-" * 110)
    for e in rows:
        print(f"{str(e.get('faction'))[:19]:20} {str(e.get('detachment'))[:33]:34} "
              f"{str(e.get('disposition'))[:14]:15} "
              f"{e.get('wins')}-{e.get('draws')}-{e.get('losses'):<3} "
              f"{str(e.get('eventName'))[:26]}")
    print(f"\n# {len(rows)} lists across pages {pages[0]}-{pages[-1]} "
          f"(reference-only; robots: Allow /, never /api/).")


if __name__ == "__main__":
    main()
