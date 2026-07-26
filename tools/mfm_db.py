#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""mfm_db.py — build a LOCAL database of Munitorum Field Manual (MFM) data.

Source: the official live MFM SSR at mfm.warhammer-community.com/en/<slug>.
Every faction follows the SAME URL pattern. This tool fetches (browser UA) or
reads a saved page, parses it, and writes data/mfm/<slug>.json with:
  - units        : name -> {points_first, points_additional?, wargear:[{name,points}]}
                   (points_additional = the ESCALATING cost for the 2nd+ identical model)
  - enhancements : name -> points
  - detachments  : name -> detachment_points (DP cost)
Attachment (which SUPPORT/LEADER can join which BODYGUARD) is captured as raw
notes when present (parsing TBD — flagged, not silently dropped).

★ The MFM is the ONLY source of truth for POINTS (unit, wargear, enhancement) and
  DP costs. BSData is stale for points — never cost a list from BSData.

The live page 403s / 307-redirects automated clients intermittently; when a fetch
comes back incomplete (no unit-name slots), pass a saved page instead:
  python3 tools/mfm_db.py imperial-knights --src /path/to/saved.html

Usage:
  python3 tools/mfm_db.py imperial-knights            # fetch + build
  python3 tools/mfm_db.py imperial-knights --src X.html
  python3 tools/mfm_db.py --list                      # known slugs
"""
import argparse, html as htmllib, json, os, re, sys, urllib.request

BASE = "https://mfm.warhammer-community.com/en/{}"
UA = ("Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) "
      "Chrome/124.0 Safari/537.36")
OUT_DIR = "data/mfm"
RAW_DIR = "data/mfm/raw"

# faction slug list (extend as needed; all follow /en/<slug>)
SLUGS = [
    "adepta-sororitas", "adeptus-custodes", "adeptus-mechanicus", "aeldari",
    "astra-militarum", "black-templars", "blood-angels", "chaos-daemons",
    "chaos-knights", "chaos-space-marines", "dark-angels", "death-guard",
    "deathwatch", "drukhari", "emperors-children", "genestealer-cults",
    "grey-knights", "imperial-knights", "leagues-of-votann", "necrons",
    "orks", "space-marines", "space-wolves", "tau-empire", "thousand-sons",
    "tyranids", "world-eaters", "agents-of-the-imperium",
]


def clean(s):
    return htmllib.unescape(re.sub(r"\s+", " ", re.sub(r"<[^>]+>", " ", s))).strip()


def fetch(slug):
    req = urllib.request.Request(BASE.format(slug), headers={"User-Agent": UA})
    with urllib.request.urlopen(req, timeout=30) as r:
        return r.read().decode("utf-8", "ignore")


PTS = re.compile(r"^(?:▲\s*)?(?:\(\+\d+\)\s*)?(\d+)\s*pts$")
NAME = re.compile(r"^[A-Z0-9 '’.\-/()]+$")


def parse_units(h):
    """S:-slot walk (from gen_points.py): NAME slot starts a unit, following
    'N pts' slots are its costs (first, then escalating additional); wargear-
    option slots are identified by the 'per <name>' template mapping."""
    divs = re.findall(r'<div hidden id="S:([0-9a-f]+)">(.*?)</div>', h, re.S)
    slot = {int(sid, 16): clean(c) for sid, c in divs}
    wargear = {int(m.group(2), 16): m.group(1).strip()
               for m in re.finditer(r'<span>per ([^<]+)</span><template id="P:([0-9a-f]+)"', h)}
    units = []
    for idx in sorted(slot):
        txt = slot[idx]
        m = PTS.match(txt)
        if m:
            if not units:
                continue
            if idx in wargear:
                units[-1]["wargear"].append({"name": wargear[idx], "points": int(m.group(1))})
            else:
                units[-1]["costs"].append(int(m.group(1)))
        elif txt and NAME.match(txt) and len(txt) < 40 and any(c.isalpha() for c in txt) \
                and not any(k in txt for k in ("COST", "UNIT", "WARGEAR", "OPTION", "PTS")):
            units.append({"name": txt.replace("▲", "").strip().title(), "costs": [], "wargear": []})
    out = {}
    for u in units:
        if not u["costs"]:
            continue
        rec = {"points_first": u["costs"][0]}
        if len(u["costs"]) > 1:
            rec["points_additional"] = u["costs"][1]
        if u["wargear"]:
            rec["wargear"] = u["wargear"]
        out[u["name"]] = rec
    return out


def parse_enhancements(h):
    """Rendered 'justify-between' span pairs: <span>NAME</span><span>N pts</span>."""
    out = {}
    for m in re.finditer(r'justify-between[^"]*"><span>([^<]+)</span><span>(\d+)\s*pts</span>', h):
        out[htmllib.unescape(m.group(1)).strip()] = int(m.group(2))
    return out


def parse_detachments(h):
    """Detachment -> DP cost. Markup varies ('2DP', '0dp'); capture NAME + DP."""
    out = {}
    for m in re.finditer(r'>([A-Z][A-Za-z’\' ]{4,34})</[a-z]+><[^>]*>\s*(\d)\s*DP\b', h, re.I):
        out[htmllib.unescape(m.group(1)).strip()] = int(m.group(2))
    return out


def build(slug, src=None):
    h = open(src, encoding="utf-8").read() if src else fetch(slug)
    os.makedirs(RAW_DIR, exist_ok=True)
    with open(os.path.join(RAW_DIR, slug + ".html"), "w", encoding="utf-8") as fh:
        fh.write(h)
    units, enh, dets = parse_units(h), parse_enhancements(h), parse_detachments(h)
    db = {"slug": slug, "source": BASE.format(slug),
          "units": units, "enhancements": enh, "detachments": dets}
    os.makedirs(OUT_DIR, exist_ok=True)
    path = os.path.join(OUT_DIR, slug + ".json")
    with open(path, "w", encoding="utf-8") as fh:
        json.dump(db, fh, indent=1, ensure_ascii=False, sort_keys=True)
    print(f"# {slug}: {len(units)} units, {len(enh)} enhancements, {len(dets)} detachments -> {path}",
          file=sys.stderr)
    if not units:
        print("# WARNING: 0 units parsed — the page was likely incomplete (bot redirect). "
              "Re-run with a complete saved page: --src <file>.", file=sys.stderr)
    return db


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("slug", nargs="?", help="faction slug, e.g. imperial-knights")
    ap.add_argument("--src", help="parse a saved MFM SSR html file instead of fetching")
    ap.add_argument("--list", action="store_true", help="list known slugs")
    a = ap.parse_args()
    if a.list or not a.slug:
        print("\n".join(SLUGS)); return
    db = build(a.slug, a.src)
    for name in ("Knight Castellan", "Knight Crusader", "Cerastus Knight Lancer", "Armiger Helverin"):
        if name in db["units"]:
            print(f"  {name}: {db['units'][name]}")


if __name__ == "__main__":
    main()
