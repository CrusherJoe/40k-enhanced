#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""bsdata_rules.py — pull the RULES half of BSData into the local DB.

tools/bsdata_db.py normalizes UNIT datasheets into data/bsdata/<slug>.json. But the
DETACHMENT RULES (BSData `rules` nodes: Assemblage of Might, Martial Mastery, The
Hammer Falls, …) and ARMY RULES / shared ABILITIES (sharedProfiles: Martial Ka'tah and
its stances, …) live elsewhere and were never captured — so they had to be hand-grepped
out of data/_src. This fixes that: it walks each faction catalogue AND the catalogues it
links (catalogueLinks, one level, same as the datasheet build) and writes every named
rule/ability to data/bsdata/rules/<slug>.json = {"<Name>": "<text>"}.

Query via tools/db.py: db.rule(slug, name) / db.find_rules(slug, substr).

Usage:
  python3 tools/bsdata_rules.py --all
  python3 tools/bsdata_rules.py adeptus-custodes
  python3 tools/bsdata_rules.py --list
"""
import argparse, glob, json, os, sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from bsdata_db import FACTION_FILE, SRC   # reuse the slug -> datasheet-file map

OUT_DIR = "data/bsdata/rules"


def _index_by_id():
    """id -> parsed catalogue, for every _src file (to resolve catalogueLinks)."""
    idx = {}
    for p in glob.glob(os.path.join(SRC, "*.json")):
        try:
            cat = json.load(open(p, encoding="utf-8")).get("catalogue")
        except Exception:
            continue
        if cat and cat.get("id"):
            idx[cat["id"]] = cat
    return idx


def _cats_for(slug, by_id):
    """The faction catalogue + everything it links (one level)."""
    fname = FACTION_FILE.get(slug)
    if not fname:
        return []
    path = os.path.join(SRC, fname)
    if not os.path.exists(path):
        return []
    root = json.load(open(path, encoding="utf-8")).get("catalogue")
    if not root:
        return []
    cats = [root]
    for link in (root.get("catalogueLinks") or []):
        tid = link.get("targetId")
        if tid and tid in by_id and by_id[tid] is not root:
            cats.append(by_id[tid])
    return cats


def _text(node):
    """Rule/ability text: a direct description, or the first non-empty characteristic."""
    d = node.get("description")
    if d:
        return d.strip()
    for c in (node.get("characteristics") or []):
        if isinstance(c, dict):
            t = c.get("$text") or c.get("text")
            if t:
                return t.strip()
    return None


def collect(cat):
    """Every named rule (rules/sharedRules) + Abilities profile in a catalogue."""
    out = {}
    def add(name, text):
        if name and text and (name not in out or len(text) > len(out[name])):
            out[name] = text
    def walk(o):
        if isinstance(o, dict):
            for key in ("rules", "sharedRules"):
                for r in (o.get(key) or []):
                    if isinstance(r, dict):
                        add(r.get("name"), _text(r))
            for key in ("profiles", "sharedProfiles"):
                for pr in (o.get(key) or []):
                    if isinstance(pr, dict) and pr.get("typeName") == "Abilities":
                        add(pr.get("name"), _text(pr))
            for v in o.values():
                walk(v)
        elif isinstance(o, list):
            for x in o:
                walk(x)
    walk(cat)
    return out


def build(slug, by_id):
    rules = {}
    for cat in _cats_for(slug, by_id):
        for name, text in collect(cat).items():
            if name not in rules or len(text) > len(rules[name]):
                rules[name] = text
    if not rules:
        return 0
    os.makedirs(OUT_DIR, exist_ok=True)
    out = os.path.join(OUT_DIR, f"{slug}.json")
    json.dump(dict(sorted(rules.items())), open(out, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    return len(rules)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("slug", nargs="?")
    ap.add_argument("--all", action="store_true")
    ap.add_argument("--list", action="store_true")
    a = ap.parse_args()
    if a.list:
        print("\n".join(sorted(FACTION_FILE)))
        return
    by_id = _index_by_id()
    slugs = sorted(FACTION_FILE) if a.all else ([a.slug] if a.slug else [])
    if not slugs:
        ap.error("give a slug, --all, or --list")
    tot = 0
    for s in slugs:
        n = build(s, by_id)
        print(f"# {s}: {n} rules/abilities", file=sys.stderr)
        tot += n
    print(f"# {tot} total across {len(slugs)} factions", file=sys.stderr)


if __name__ == "__main__":
    main()
