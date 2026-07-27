#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""db.py — the read accessor for the local data/ database.

THE golden-rule enforcer: analysis, list-building, and sims call THIS instead of
hand-copying points/profiles. POINTS come from data/mfm/ (authoritative); PROFILES
from data/bsdata/. Everything is cached per-process.

  from db import points, enhancement, detachment_dp, profile, weapon, list_cost, mfm, bsdata

  points("imperial-knights", "Knight Castellan")        -> {'first':425,'additional':450}
  enhancement("imperial-knights", "Blessed Plate")      -> 30
  detachment_dp("imperial-knights", "Valourstrike Lance")-> 2
  profile("tau-empire", "Hammerhead Gunship")           -> {stats, ranged[], melee[], ...}
  weapon("tau-empire", "Hammerhead Gunship", "Railgun") -> {S:20, AP:-5, D:'D6+6', ...}
  list_cost("imperial-knights", [("Knight Castellan",2),("Knight Crusader",1,"Rapid-fire battle cannon"),
                                  ("Cerastus Knight Lancer",1),("Armiger Helverin",1)],
            enhancements=["Archeotech Autoloaders","Blessed Plate"], allies=75)  -> 1970

Run directly for a quick lookup:  python3 tools/db.py imperial-knights "Knight Castellan"
"""
import functools, json, os, re, sys

DATA = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "data")


@functools.lru_cache(maxsize=None)
def mfm(slug):
    p = os.path.join(DATA, "mfm", slug + ".json")
    if not os.path.exists(p):
        raise KeyError(f"no MFM data for {slug!r} (run: python3 tools/mfm_db.py {slug})")
    return json.load(open(p, encoding="utf-8"))


@functools.lru_cache(maxsize=None)
def bsdata(slug):
    p = os.path.join(DATA, "bsdata", slug + ".json")
    if not os.path.exists(p):
        raise KeyError(f"no BSData profiles for {slug!r} (run: python3 tools/bsdata_db.py {slug})")
    return json.load(open(p, encoding="utf-8"))


@functools.lru_cache(maxsize=None)
def bsrules(slug):
    """Every named rule / army rule / detachment rule / ability for a faction
    (data/bsdata/rules/<slug>.json, built by tools/bsdata_rules.py). {name: text}."""
    p = os.path.join(DATA, "bsdata", "rules", slug + ".json")
    if not os.path.exists(p):
        raise KeyError(f"no rules DB for {slug!r} (run: python3 tools/bsdata_rules.py {slug})")
    return json.load(open(p, encoding="utf-8"))


def rule(slug, name):
    """Exact (case/apostrophe-insensitive) rule/ability text, e.g.
    rule('adeptus-custodes', \"Martial Ka'tah\")  ->  the army-rule text."""
    r = _ci(bsrules(slug), name)
    if r is None:
        raise KeyError(f"rule {name!r} not in {slug} rules DB")
    return r


def find_rules(slug, substr):
    """All rules/abilities whose NAME or TEXT contains substr (case-insensitive)."""
    t = substr.lower()
    return {k: v for k, v in bsrules(slug).items() if t in k.lower() or t in v.lower()}


@functools.lru_cache(maxsize=None)
def strats(slug):
    """Stratagem cards by detachment (data/strats/<slug>.json). BSData does not carry these;
    they come from the faction pack + 39k.pro (see tools/strats_ingest.py). Returns
    {detachment: {name: {type, cp, when, target, effect, ...}}} (keys starting with '_' are notes)."""
    p = os.path.join(DATA, "strats", slug + ".json")
    if not os.path.exists(p):
        raise KeyError(f"no strats DB for {slug!r}")
    return {k: v for k, v in json.load(open(p, encoding="utf-8")).items() if not k.startswith("_")}


def strat(slug, name):
    """One stratagem card by name (searches every detachment, apostrophe/case-insensitive)."""
    for det in strats(slug).values():
        v = _ci(det, name)
        if v is not None:
            return v
    raise KeyError(f"stratagem {name!r} not in {slug} strats DB")


def _ci(d, name):
    """case-insensitive dict lookup that tolerates straight/curly apostrophes."""
    if name in d:
        return d[name]
    norm = lambda s: re.sub(r"[’']", "'", s).lower().strip()
    t = norm(name)
    for k, v in d.items():
        if norm(k) == t:
            return v
    return None


def points(slug, unit):
    u = _ci(mfm(slug)["units"], unit)
    if u is None:
        raise KeyError(f"{unit!r} not in MFM {slug}")
    return {"first": u["points_first"], "additional": u.get("points_additional")}


def wargear_cost(slug, unit, wargear):
    u = _ci(mfm(slug)["units"], unit) or {}
    for w in u.get("wargear", []):
        if re.sub(r"[’']", "'", w["name"]).lower() == re.sub(r"[’']", "'", wargear).lower():
            return w["points"]
    return 0


def enhancement(slug, name):
    v = _ci(mfm(slug)["enhancements"], name)
    if v is None:
        raise KeyError(f"enhancement {name!r} not in MFM {slug}")
    return v


def detachment_dp(slug, name):
    dets = mfm(slug)["detachments"]
    v = _ci(dets, name) or _ci(dets, name.upper())
    if v is None:  # detachments are stored UPPERCASE in the SSR
        for k, val in dets.items():
            if re.sub(r"[’']", "'", k).lower() == re.sub(r"[’']", "'", name).lower():
                return val
        raise KeyError(f"detachment {name!r} not in MFM {slug}")
    return v


def profile(slug, unit):
    norm = lambda s: re.sub(r"[’']", "'", s).lower().strip()
    t = norm(unit)
    sheets = bsdata(slug)["datasheets"]
    for d in sheets:                       # exact (apostrophe-insensitive)
        if norm(d["name"]) == t:
            return d
    subs = [d for d in sheets if t in norm(d["name"]) or norm(d["name"]) in t]
    if len(subs) == 1:
        return subs[0]
    if subs:                                # prefer the shortest name (most generic)
        return min(subs, key=lambda d: len(d["name"]))
    raise KeyError(f"{unit!r} not in BSData {slug} (near: "
                   f"{[d['name'] for d in sheets if t.split()[0] in norm(d['name'])][:5]})")


def find(slug, substr):
    """List datasheet names matching a substring (for discovering exact names)."""
    t = re.sub(r"[’']", "'", substr).lower()
    return [d["name"] for d in bsdata(slug)["datasheets"]
            if t in re.sub(r"[’']", "'", d["name"]).lower()]


def weapon(slug, unit, wname):
    d = profile(slug, unit)
    t = re.sub(r"[’']", "'", wname).lower()
    for w in d.get("ranged", []) + d.get("melee", []):
        if t in re.sub(r"[’']", "'", w["name"]).lower():
            return w
    raise KeyError(f"weapon {wname!r} not on {unit} ({slug})")


def unit_cost(slug, unit, copies=1, wargear=()):
    p = points(slug, unit)
    total = p["first"]
    if copies > 1:
        total += (p["additional"] or p["first"]) * (copies - 1)  # escalating per 2nd+ model
    for wg in (wargear if isinstance(wargear, (list, tuple)) else [wargear]):
        if wg:
            total += wargear_cost(slug, unit, wg)
    return total


def list_cost(slug, units, enhancements=(), allies=0):
    """units = [(name, copies[, wargear...]), ...]. Returns the total points."""
    total = allies
    for entry in units:
        name, copies = entry[0], entry[1]
        wg = entry[2:] if len(entry) > 2 else ()
        total += unit_cost(slug, name, copies, wg)
    for e in enhancements:
        total += enhancement(slug, e)
    return total


if __name__ == "__main__":
    if len(sys.argv) >= 3:
        slug, name = sys.argv[1], sys.argv[2]
        try:
            print(name, "points:", points(slug, name))
        except KeyError:
            try:
                print(name, "enhancement:", enhancement(slug, name), "pts")
            except KeyError:
                print(json.dumps(profile(slug, name), indent=1, ensure_ascii=False))
    else:
        print(__doc__)
