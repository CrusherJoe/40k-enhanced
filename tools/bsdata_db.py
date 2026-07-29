#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""bsdata_db.py — normalize BSData wh40k-11e catalogues into a local profile DB.

Source: a local clone of github.com/BSData/wh40k-11e at data/_src/wh40k-11e
(gitignored; refresh with `git -C data/_src/wh40k-11e pull`). Output: one
data/bsdata/<slug>.json per faction with clean datasheets:
  {name, stats{M,T,Sv,W,Ld,OC}, invuln, ranged[], melee[], abilities{}, damaged, keywords}

Profiles/weapons/abilities come from BSData. POINTS are NOT authoritative here —
the MFM (data/mfm/, tools/mfm_db.py) is the only source of truth for points.

BSData model: datasheets are `model`/`unit` sharedSelectionEntries in the cat that
holds them (a *Library* cat for IK/Astra/Aeldari/…, or the self-contained faction
cat for Necrons/Orks/T'au). Weapon/ability targetIds resolve against that cat plus
its catalogueLinks (one level). Generalized from tools/gen_profiles.py.

Usage:
  python3 tools/bsdata_db.py --all            # build every mapped faction
  python3 tools/bsdata_db.py imperial-knights  # one faction
  python3 tools/bsdata_db.py --list
"""
import argparse, glob, json, os, re, sys

SRC = "data/_src/wh40k-11e"
OUT_DIR = "data/bsdata"

# slug -> the BSData filename that CONTAINS this faction's datasheets (the cat with
# the model/unit sharedSelectionEntries). Linked libraries are merged automatically
# for targetId resolution. SM chapters hold only their chapter-specific units; load
# space-marines.json alongside for the common Marine datasheets.
FACTION_FILE = {
    "adepta-sororitas": "Imperium - Adepta Sororitas.json",
    "adeptus-custodes": "Imperium - Adeptus Custodes.json",
    "adeptus-mechanicus": "Imperium - Adeptus Mechanicus.json",
    "aeldari": "Aeldari - Aeldari Library.json",
    "agents-of-the-imperium": "Imperium - Agents of the Imperium.json",
    "astra-militarum": "Imperium - Astra Militarum - Library.json",
    "black-templars": "Imperium - Black Templars.json",
    "blood-angels": "Imperium - Blood Angels.json",
    "chaos-daemons": "Chaos - Chaos Daemons Library.json",
    "chaos-knights": "Chaos - Chaos Knights Library.json",
    "chaos-space-marines": "Chaos - Chaos Space Marines.json",
    "dark-angels": "Imperium - Dark Angels.json",
    "death-guard": "Chaos - Death Guard.json",
    "deathwatch": "Imperium - Deathwatch.json",
    "drukhari": "Aeldari - Aeldari Library.json",
    "emperors-children": "Chaos - Emperor's Children.json",
    "genestealer-cults": "Genestealer Cults.json",
    "grey-knights": "Imperium - Grey Knights.json",
    "imperial-fists": "Imperium - Imperial Fists.json",
    "imperial-knights": "Imperium - Imperial Knights - Library.json",
    "iron-hands": "Imperium - Iron Hands.json",
    "leagues-of-votann": "Leagues of Votann.json",
    "necrons": "Necrons.json",
    "orks": "Orks.json",
    "raven-guard": "Imperium - Raven Guard.json",
    "salamanders": "Imperium - Salamanders.json",
    "space-marines": "Imperium - Space Marines.json",
    "space-wolves": "Imperium - Space Wolves.json",
    "tau-empire": "T'au Empire.json",
    "thousand-sons": "Chaos - Thousand Sons.json",
    "tyranids": "Tyranids.json",
    "ultramarines": "Imperium - Ultramarines.json",
    "white-scars": "Imperium - White Scars.json",
    "world-eaters": "Chaos - World Eaters.json",
}

# Aeldari + Drukhari share one BSData library; split by the raw 'Faction:' category.
FACTION_FILTER = {"aeldari": ("exclude", "Faction: Drukhari"), "drukhari": ("include", "Faction: Drukhari")}

CORE_RULES = {"Deadly Demise", "Lone Operative", "Feel No Pain", "Fights First",
              "Stealth", "Scouts", "Infiltrators", "Deep Strike", "Leader", "Firing Deck"}
FACTION_RULES_SKIP = {"Sustained Hits", "Lethal Hits", "Devastating Wounds", "Blast",
                      "Twin-linked", "Rapid Fire", "Melta", "Torrent", "Hazardous",
                      "Ignores Cover", "Precision", "Heavy", "Assault", "Pistol",
                      "Anti", "Lance", "Extra Attacks", "Indirect Fire", "One Shot",
                      "Conversion", "Psychic", "Hover"}


# ---- indexes (populated per build over the faction cat + its linked libs) --------
def new_ctx():
    return {"SSE": {}, "SSEG": {}, "SP": {}, "SR": {}}


def merge_cat(ctx, cat):
    for e in cat.get("sharedSelectionEntries", []):
        ctx["SSE"].setdefault(e["id"], e)
    for g in cat.get("sharedSelectionEntryGroups", []):
        ctx["SSEG"].setdefault(g["id"], g)
    for p in cat.get("sharedProfiles", []):
        ctx["SP"].setdefault(p["id"], p)
    for r in cat.get("sharedRules", []):
        ctx["SR"].setdefault(r["id"], r)


def ch(p):
    return {c["name"]: c.get("$text") for c in p.get("characteristics", [])}


def clean_text(s):
    if not s:
        return s
    return re.sub(r"\s+", " ", s.replace("^^", "").replace("**", "")).strip()


def clean_name(s):
    return re.sub(r"^[^0-9A-Za-z]+", "", s or "").strip()


def num(v):
    if v is None:
        return None
    v = v.strip()
    return int(v) if re.fullmatch(r"-?\d+", v) else v


def kw_list(s):
    return [k.strip().upper() for k in s.split(",")] if s and s != "-" else []


def resolve_rule_name(il):
    name = il.get("name", "")
    for m in il.get("modifiers", []):
        if m.get("field") == "name":
            if m.get("type") == "append":
                name = f"{name} {m['value']}".strip()
            elif m.get("type") == "set":
                name = m["value"]
    return name


def collect_weapons(ctx, entry, seen, out):
    profs = list(entry.get("profiles", []))
    for il in entry.get("infoLinks", []):        # weapons can be infoLink -> sharedProfile too
        if il.get("type") == "profile":
            tgt = ctx["SP"].get(il.get("targetId"))
            if tgt and tgt.get("typeName") in ("Ranged Weapons", "Melee Weapons"):
                profs.append(tgt)
    for p in profs:
        if p.get("typeName") in ("Ranged Weapons", "Melee Weapons"):
            nm = clean_name(p["name"])
            if nm not in seen:
                seen.add(nm)
                out.append((p["typeName"], nm, ch(p)))
    for se in entry.get("selectionEntries", []):
        collect_weapons(ctx, se, seen, out)
    for g in entry.get("selectionEntryGroups", []):
        collect_weapons(ctx, g, seen, out)
    for el in entry.get("entryLinks", []):
        tgt = ctx["SSE"].get(el.get("targetId")) or ctx["SSEG"].get(el.get("targetId"))
        if tgt:
            collect_weapons(ctx, tgt, seen, out)


def weapon_dict(tn, name, c):
    d = {"name": name}
    if tn == "Ranged Weapons":
        rng = c.get("Range", "") or ""
        d["range"] = num(rng.replace('"', "")) if rng and rng != "-" else rng
        d["A"], d["BS"] = num(c.get("A")), c.get("BS")
    else:
        d["A"], d["WS"] = num(c.get("A")), c.get("WS")
    d["S"], d["AP"], d["D"] = num(c.get("S")), num(c.get("AP")), num(c.get("D"))
    kw = kw_list(c.get("Keywords"))
    if kw:
        d["abilities"] = kw  # weapon keywords, as consumed by wh.mathhammer + data/profiles
    return d


def unit_profiles(ctx, entry):
    """The 'Unit' statline profiles on an entry — inline OR referenced via an infoLink to a
    sharedProfile (ctx['SP']). Newer BSData cuts (e.g. AM Kasrkin, Aeldari Windriders) put the
    statline on a model sub-entry as an infoLink->sharedProfile, so inline-only lookup misses them."""
    out = [p for p in entry.get("profiles", []) if p.get("typeName") == "Unit"]
    for il in entry.get("infoLinks", []):
        if il.get("type") == "profile":
            tgt = ctx["SP"].get(il.get("targetId"))
            if tgt and tgt.get("typeName") == "Unit":
                out.append(tgt)
    return out


def _all_unit_holders(ctx, entry, depth=0, seen=None):
    """Every entry bearing a 'Unit' statline profile, recursing selectionEntries,
    selectionEntryGroups (+their entryLinks), and entryLinks (resolved via ctx)."""
    seen = set() if seen is None else seen
    if id(entry) in seen or depth > 6:
        return []
    seen.add(id(entry))
    out = [entry] if unit_profiles(ctx, entry) else []
    kids = list(entry.get("selectionEntries", []))
    for g in entry.get("selectionEntryGroups", []):
        if unit_profiles(ctx, g):        # a group can carry the Unit statline inline (Victrix Honour Guard)
            out.append(g)
        kids += g.get("selectionEntries", [])
        kids += g.get("selectionEntryGroups", [])   # groups nest (Deathwatch kill-team squad members)
        kids += [t for el in g.get("entryLinks", [])
                 if (t := ctx["SSE"].get(el.get("targetId")) or ctx["SSEG"].get(el.get("targetId")))]
    kids += [t for el in entry.get("entryLinks", [])
             if (t := ctx["SSE"].get(el.get("targetId")) or ctx["SSEG"].get(el.get("targetId")))]
    for k in kids:
        out += _all_unit_holders(ctx, k, depth + 1, seen)
    return out


def profile_source(ctx, entry):
    # direct: unit statline on the entry itself (inline or via infoLink -> sharedProfile)
    if unit_profiles(ctx, entry):
        return entry, []
    # direct model sub-entries (original path — handles Canis Rex's pilot etc.)
    models = [s for s in entry.get("selectionEntries", [])
              if s.get("type") == "model" and unit_profiles(ctx, s)]
    if models:
        primary = next((m for m in models if m["name"] == entry["name"]), models[0])
        return primary, [m for m in models if m is not primary]
    # fallback: statline lives in a group / entryLink (Sanguinary Guard, Deathwing
    # Knights, Broadside, ...). Take the first Unit-holder; skip noisy extras.
    holders = _all_unit_holders(ctx, entry)
    return (holders[0], []) if holders else (None, [])


def build_profile(ctx, entry):
    src, extra = profile_source(ctx, entry)
    if src is None:
        return None
    up = unit_profiles(ctx, src)
    if not up:
        return None
    st = ch(up[0])
    insv = (st.get("InSv") or "")
    prof = {"name": entry["name"], "source": "bsdata-wh40k-11e",
            "stats": {"M": num((st.get("M") or "").replace('"', "")), "T": num(st.get("T")),
                      "Sv": st.get("Sv"), "W": num(st.get("W")), "Ld": st.get("LD"), "OC": num(st.get("OC"))}}
    if insv and insv not in ("-", ""):
        prof["invuln"] = insv.replace("*", "")
        prof["invuln_ranged_only"] = insv.endswith("*")
    weps = []
    collect_weapons(ctx, entry, set(), weps)   # recurse the whole unit (src may be one model)
    ranged = [weapon_dict(t, n, c) for t, n, c in weps if t == "Ranged Weapons"]
    melee = [weapon_dict(t, n, c) for t, n, c in weps if t == "Melee Weapons"]
    if ranged:
        prof["ranged"] = ranged
    if melee:
        prof["melee"] = melee
    core, faction, datasheet = [], [], []
    for il in src.get("infoLinks", []):
        if il.get("type") == "rule":
            base = il.get("name", "")
            if base in CORE_RULES:
                core.append(resolve_rule_name(il))
            elif not any(base.startswith(s) for s in FACTION_RULES_SKIP):
                faction.append(resolve_rule_name(il))
    for p in src.get("profiles", []):
        if p.get("typeName") == "Abilities":
            datasheet.append({"name": p["name"], "text": clean_text(ch(p).get("Description"))})
    for ig in src.get("infoGroups", []):
        for p in ig.get("profiles", []):
            datasheet.append({"name": ig.get("name"), "text": clean_text(ch(p).get("Description"))})
    ab = {k: v for k, v in (("core", core), ("faction", faction), ("datasheet", datasheet)) if v}
    if ab:
        prof["abilities"] = ab
    for il in src.get("infoLinks", []):
        if il.get("type") == "profile" and (il.get("name") or "").startswith("Damaged"):
            tgt = ctx["SP"].get(il.get("targetId"))
            thr = re.search(r"(\d+-\d+)", il.get("name", ""))
            prof["damaged"] = {"threshold": thr.group(1) if thr else il.get("name"),
                               "text": clean_text((ch(tgt).get("Description") if tgt else "") or "")}
            break
    prof["keywords"] = [cl["name"] for cl in src.get("categoryLinks", [])
                        if not cl["name"].startswith("Faction:")]
    if extra:
        prof["extra_profiles"] = []
        for m in extra:
            s = ch(unit_profiles(ctx, m)[0])
            prof["extra_profiles"].append({"name": m["name"],
                "stats": {"M": num((s.get("M") or "").replace('"', "")), "T": num(s.get("T")),
                          "Sv": s.get("Sv"), "W": num(s.get("W")), "Ld": s.get("LD"), "OC": num(s.get("OC"))}})
    return prof


def load_cat(path):
    return json.load(open(path, encoding="utf-8"))["catalogue"]


def _fac_stem(fname):
    """The faction's distinctive name from its catalogue filename — used to tell its OWN
    datasheet library (e.g. 'Library - Tyranids') from shared ally libraries it also links
    (e.g. a Chaos army linking 'Chaos Daemons Library')."""
    s = fname.replace(".json", "")
    for pre in ("Imperium - ", "Chaos - ", "Aeldari - ", "Library - "):
        s = s.replace(pre, "")
    return s.replace(" - Library", "").replace(" Library", "").strip()


def build_faction(slug, id2file):
    fname = FACTION_FILE[slug]
    path = os.path.join(SRC, fname)
    if not os.path.exists(path):
        print(f"# {slug}: MISSING {fname}", file=sys.stderr)
        return None
    cat = load_cat(path)
    ctx = new_ctx()
    merge_cat(ctx, cat)
    # merge one level of linked catalogues (libraries / base SM / agents) for resolution.
    # A faction's own datasheets are sometimes DEFINED in a linked "Library" catalogue
    # (e.g. Tyranids.json references Raveners but they live in "Library - Tyranids.json"),
    # so those libraries must also be a DISCOVERY source, not just a resolution index.
    stem = _fac_stem(fname)                      # this faction's distinctive name
    discover = [cat]
    for link in cat.get("catalogueLinks", []):
        lf = id2file.get(link.get("targetId"))
        if lf and os.path.exists(os.path.join(SRC, lf)):
            try:
                lcat = load_cat(os.path.join(SRC, lf))
                merge_cat(ctx, lcat)
                # discover ONLY from the faction's OWN library (name matches), never shared
                # ally libraries (e.g. CSM links the Chaos Daemons library — those are allies,
                # resolved at load time, not this faction's datasheets)
                if "Library" in lf and stem and stem in lf:
                    discover.append(lcat)
            except Exception:
                pass
    # datasheets = model/unit entries defined in this faction's cat OR its linked Library
    entries, seen_ids = [], set()
    for lc in discover:
        for e in lc.get("sharedSelectionEntries", []) + lc.get("selectionEntries", []):
            if e.get("type") in ("model", "unit") and e.get("id") not in seen_ids:
                seen_ids.add(e.get("id"))
                entries.append(e)
    flt = FACTION_FILTER.get(slug)
    sheets, seen_names = [], set()
    for e in entries:
        if flt:  # split shared libraries by the raw 'Faction:' category
            mode, kw = flt
            cats = [cl["name"] for cl in e.get("categoryLinks", [])]
            if (kw in cats) != (mode == "include"):
                continue
        try:
            p = build_profile(ctx, e)
            if p and p["name"] not in seen_names:   # dedup (a unit can be in main + library)
                seen_names.add(p["name"])
                sheets.append(p)
        except Exception as ex:
            print(f"#   {slug}: skip {e.get('name')}: {ex}", file=sys.stderr)
    sheets.sort(key=lambda d: d["name"])
    db = {"slug": slug, "source": f"BSData/wh40k-11e :: {fname}", "datasheets": sheets}
    os.makedirs(OUT_DIR, exist_ok=True)
    outp = os.path.join(OUT_DIR, slug + ".json")
    json.dump(db, open(outp, "w", encoding="utf-8"), indent=1, ensure_ascii=False)
    print(f"# {slug}: {len(sheets)} datasheets -> {outp}", file=sys.stderr)
    return db


def index_ids():
    """targetId (catalogue id) -> filename, for resolving catalogueLinks."""
    id2file = {}
    for path in glob.glob(os.path.join(SRC, "*.json")):
        try:
            cat = json.load(open(path, encoding="utf-8")).get("catalogue", {})
            if cat.get("id"):
                id2file[cat["id"]] = os.path.basename(path)
        except Exception:
            pass
    return id2file


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("slug", nargs="?")
    ap.add_argument("--all", action="store_true")
    ap.add_argument("--list", action="store_true")
    a = ap.parse_args()
    if a.list:
        print("\n".join(sorted(FACTION_FILE)))
        return
    if not os.path.isdir(SRC):
        sys.exit(f"BSData clone not found at {SRC}. Run: git clone --depth 1 "
                 f"https://github.com/BSData/wh40k-11e.git {SRC}")
    id2file = index_ids()
    slugs = sorted(FACTION_FILE) if a.all else [a.slug] if a.slug else []
    if not slugs:
        ap.error("give a slug or --all")
    total = 0
    for slug in slugs:
        db = build_faction(slug, id2file)
        if db:
            total += len(db["datasheets"])
    print(f"# TOTAL: {total} datasheets across {len(slugs)} factions", file=sys.stderr)


if __name__ == "__main__":
    main()
