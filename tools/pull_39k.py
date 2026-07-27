#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""pull_39k.py — pull STRATAGEMS (detachment-specific) from 39k.pro into data/strats/<slug>.json.

39k.pro is a client-side SPA: its ENTIRE ruleset is embedded in the single JS bundle
(/assets/index-*.js) as minified object literals — no /api/ calls, no auth. This tool downloads
the current bundle, extracts every stratagem + the detachment/publication/faction objects needed to
place it, and writes one file per faction:

  data/strats/<slug>.json = { "<Detachment Name>": { "<Strat Name>": {category,cp,when,target,effect,lore} } }

Strats are DETACHMENT-SPECIFIC, so they are grouped by detachment (resolved via
stratagem.detachmentId -> detachment.name; faction via detachment.publicationId ->
publication.factionKeywordId -> faction.name). Points stay MFM, profiles stay BSData; this is the
strat layer neither carries. Query via db.strats(slug) / db.strat(slug, name).

Usage:
  python3 tools/pull_39k.py --fetch                 # download the current bundle to the cache
  python3 tools/pull_39k.py                          # parse cache -> write every faction's strats
  python3 tools/pull_39k.py --slug adeptus-custodes  # just one faction (still writes the file)
  python3 tools/pull_39k.py --bundle /path/to.js     # parse a specific bundle file
"""
import argparse, glob, json, os, re, sys, urllib.request

DATA = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "data")
CACHE = os.path.join(DATA, "_src", "39k_bundle.js")   # gitignored (data/_src/*)
HOME = "https://39k.pro/"
UA = {"User-Agent": "Mozilla/5.0 (wh-tools research)"}

# a JS double-quoted string literal (handles \" and \\ escapes) -> decode with json.loads
S = r'"(?:[^"\\]|\\.)*"'
STRAT_CATS = ("strategicPloy", "battleTactic", "wargear", "epicDeed")


def _get(url):
    req = urllib.request.Request(url, headers=UA)
    return urllib.request.urlopen(req, timeout=60).read().decode("utf-8", "replace")


def fetch_bundle():
    shell = _get(HOME)
    m = re.search(r'src="(/assets/index-[0-9a-f]+\.js)"', shell)
    if not m:
        sys.exit("could not find the JS bundle URL in the homepage shell")
    url = HOME.rstrip("/") + m.group(1)
    print(f"# downloading {url}", file=sys.stderr)
    js = _get(url)
    os.makedirs(os.path.dirname(CACHE), exist_ok=True)
    open(CACHE, "w", encoding="utf-8").write(js)
    print(f"# cached {len(js):,} bytes -> {CACHE}", file=sys.stderr)
    return js


def _s(tok):
    """decode a captured JS string literal to str."""
    try:
        return json.loads(tok)
    except Exception:
        return tok.strip('"')


# Anchor on the localisation block (tolerant: targetRules is optional — some strats have no target),
# then read the header (category/cpCost/detachmentId) BACKWARD within a bounded window so a match can
# never bleed across objects. This is what makes the extraction complete + non-corrupting.
_LOC = re.compile(
    r'localisations:\{en:\{name:(' + S + r'),lore:(' + S + r'),whenRules:(' + S + r')'
    r'(?:,targetRules:(null|' + S + r'))?,effectRules:(' + S + r')')
_CAT = re.compile(r'category:"(' + "|".join(STRAT_CATS) + r')"')
_CP = re.compile(r'cpCost:"([^"]*)"')
_DET = re.compile(r'detachmentId:(null|"[^"]+")')


def _last(pat, s):
    m = None
    for m in pat.finditer(s):
        pass
    return m


def parse_strats(js):
    """Every stratagem: id-less card = {category, cp, detachmentId, name, when, target, effect, lore}.
    A localisation counts as a stratagem only if a strat-enum `category` sits in the 400 chars before
    it (that same-object window also carries cpCost + detachmentId)."""
    out = []
    for m in _LOC.finditer(js):
        head = js[max(0, m.start() - 400):m.start()]
        cat = _last(_CAT, head)
        if not cat:                       # not a stratagem (e.g. an ability that also has whenRules)
            continue
        cp = _last(_CP, head)
        det = _last(_DET, head)
        detv = det.group(1) if det else "null"
        tgt = m.group(4)
        out.append(dict(category=cat.group(1), cp=(cp.group(1) if cp else None),
                        detachmentId=(None if detv == "null" else detv.strip('"')),
                        name=_s(m.group(1)), lore=_s(m.group(2)), when=_s(m.group(3)),
                        target=(None if not tgt or tgt == "null" else _s(tgt)),
                        effect=_s(m.group(5))))
    return out


def parse_detachments(js):
    """detachmentId -> {name, publicationId, dp}. Identified by the detachmentPointsCost field."""
    pat = re.compile(
        r'id:"(?P<id>[^"]+)",publicationId:"(?P<pub>[^"]*)"'
        r'.*?detachmentPointsCost:(?P<dp>\d+|null),pointsCost:[^,]*,'
        r'localisations:\{en:\{name:(?P<name>' + S + r')\}\}', re.DOTALL)
    out = {}
    for m in pat.finditer(js):
        out[m.group("id")] = dict(name=_s(m.group("name")), publicationId=m.group("pub"),
                                  dp=(None if m.group("dp") == "null" else int(m.group("dp"))))
    return out


def parse_publications(js):
    """publicationId -> factionKeywordId."""
    pat = re.compile(r'id:"(?P<id>[^"]+)",factionKeywordId:"(?P<fk>[^"]+)"')
    return {m.group("id"): m.group("fk") for m in pat.finditer(js)}


def parse_factions(js):
    """factionKeywordId -> faction display name (faction objects carry commonName in localisations)."""
    pat = re.compile(r'id:"(?P<id>[^"]+)"[^{}]*?localisations:\{en:\{name:(?P<name>' + S + r'),commonName:')
    return {m.group("id"): _s(m.group("name")) for m in pat.finditer(js)}


# 39k names some factions by their umbrella keyword; map those to the faction-pack slug so a
# faction's strats land in ONE file (not split across two).
SLUG_ALIAS = {
    "adeptus-astartes": "space-marines",
    "asuryani": "aeldari",
    "heretic-astartes": "chaos-space-marines",
    "legiones-daemonica": "chaos-daemons",
}


def slugify(name):
    s = re.sub(r"[^a-z0-9]+", "-", name.lower().replace("’", "").replace("'", "")).strip("-")
    return SLUG_ALIAS.get(s, s)


def known_slugs():
    return {os.path.splitext(os.path.basename(p))[0]
            for p in glob.glob(os.path.join(DATA, "faction-packs", "*.txt"))}


def build(js, only_slug=None):
    strats = parse_strats(js)
    dets = parse_detachments(js)
    pubs = parse_publications(js)
    facs = parse_factions(js)
    slugs = known_slugs()

    # faction slug -> { detachment name -> { strat name -> card } }
    by_faction = {}
    unplaced = 0
    for s in strats:
        det = dets.get(s["detachmentId"])
        if not det:
            unplaced += 1
            continue
        fk = pubs.get(det["publicationId"])
        fac_name = facs.get(fk) if fk else None
        if not fac_name:
            unplaced += 1
            continue
        slug = slugify(fac_name)
        if slug not in slugs:                      # keep the raw slug but flag it
            slug = slug
        by_faction.setdefault(slug, {}).setdefault(det["name"], {})[s["name"]] = dict(
            type=s["category"], cp=_cpval(s["cp"]), when=s["when"],
            target=s["target"], effect=s["effect"], lore=s["lore"])

    written = []
    os.makedirs(os.path.join(DATA, "strats"), exist_ok=True)
    for slug, dets in sorted(by_faction.items()):
        if only_slug and slug != only_slug:
            continue
        path = os.path.join(DATA, "strats", slug + ".json")
        # PRECEDENCE: FACTION PACK is primary truth; 39k is FALLBACK. Merge at the STRAT level and
        # never clobber a strat tagged _src="faction-pack". (Order-independent, so re-running the
        # 39k pull can't overwrite the pack's authoritative cards.)
        merged = {}
        if os.path.exists(path):
            merged = {k: v for k, v in json.load(open(path, encoding="utf-8")).items()
                      if not k.startswith("_")}
        for dname, cards in dets.items():
            dst = dict(merged.get(dname, {}))
            for sname, card in cards.items():
                cur = dst.get(sname)
                if cur and cur.get("_src") == "faction-pack":
                    continue                              # faction pack wins
                dst[sname] = dict(card, _src="39k.pro")
            merged[dname] = dst
        payload = {"_source": "stratagems grouped by DETACHMENT. PRIMARY = faction pack "
                              "(_src=faction-pack); FALLBACK = 39k.pro JS bundle via pull_39k.py "
                              "(_src=39k.pro) for strats/detachments the pack omits."}
        for dname in sorted(merged):
            payload[dname] = {k: merged[dname][k] for k in sorted(merged[dname])}
        json.dump(payload, open(path, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
        n = sum(len(v) for k, v in payload.items() if not k.startswith("_"))
        written.append((slug, len(payload) - 1, n, slug in slugs))
    return written, len(strats), unplaced


def _cpval(cp):
    try:
        return int(cp)
    except Exception:
        return cp


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--fetch", action="store_true", help="download the current bundle first")
    ap.add_argument("--bundle", help="parse this bundle file instead of the cache")
    ap.add_argument("--slug", help="only write this faction slug")
    a = ap.parse_args()
    if a.fetch:
        js = fetch_bundle()
    else:
        path = a.bundle or CACHE
        if not os.path.exists(path):
            sys.exit(f"no bundle at {path} — run with --fetch first")
        js = open(path, encoding="utf-8").read()
    written, total, unplaced = build(js, a.slug)
    for slug, ndet, nstr, known in written:
        flag = "" if known else "  <-- slug not in faction-packs (check mapping)"
        print(f"{slug:26} {ndet:2} detachments  {nstr:3} strats{flag}")
    print(f"# {total} stratagems parsed; {unplaced} unplaced; {len(written)} faction files written",
          file=sys.stderr)


if __name__ == "__main__":
    main()
