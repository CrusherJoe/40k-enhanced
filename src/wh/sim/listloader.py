"""Generic archive -> Army loader: the DEFAULT way to turn a real listhammer list into a sim roster.

Reads an entry from data/listhammer_archive.json, parses its exported listText into (unit, points, models),
resolves every unit against BSData (db.profile, with a chapter fallback), auto-assigns a sim role + threat
from the profile, applies a faction-default tapestry (e.g. Astartes Oath of Moment), then calls the
faction's OVERRIDE hook for the modelling the heuristics can't derive (C'tan resilience, transports,
monster regen, weapon-loadout fixes). List CONTENT is 100% the archive's real list; only the sim-modelling
layer is added here. Entries with truncated listText (54 of 98) can't be parsed — the human re-fetches those.

  from wh.sim import listloader as L
  army = L.load(faction="Orks", detachment="Kult of Speed", disposition_default="disruption")
"""
from __future__ import annotations

import json, os, re, sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(
    os.path.abspath(__file__))))), "tools"))
import db

from .entities import Unit, Army
from . import rosters as _R

_ARCHIVE = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(
    os.path.abspath(__file__))))), "data", "listhammer_archive.json")

_DISP = {"take and hold": "take-and-hold", "purge the foe": "purge-the-foe",
         "reconnaissance": "reconnaissance", "priority assets": "priority-assets", "disruption": "disruption"}

# chapter datasheets that live in the generic space-marines cut / a named-character cut
_FALLBACK = {"blood-angels": ["space-marines"], "dark-angels": ["space-marines"],
             "space-marines": ["salamanders", "ultramarines", "imperial-fists"],
             # chapters that share the common Marine datasheet pool
             "black-templars": ["space-marines"], "deathwatch": ["space-marines"],
             "space-wolves": ["space-marines"]}

_FACTION_SLUG = {"Orks": "orks", "Aeldari": "aeldari", "Tyranids": "tyranids",
                 "Emperor's Children": "emperors-children", "Astra Militarum": "astra-militarum",
                 "Space Marines (Astartes)": "space-marines", "Blood Angels": "blood-angels",
                 "T'au Empire": "tau-empire", "Dark Angels": "dark-angels", "Thousand Sons": "thousand-sons",
                 "Necrons": "necrons", "Drukhari": "drukhari", "Adeptus Custodes": "adeptus-custodes",
                 "Chaos Space Marines": "chaos-space-marines", "Chaos Daemons": "chaos-daemons",
                 "Space Wolves": "space-wolves", "World Eaters": "world-eaters",
                 "Adeptus Mechanicus": "adeptus-mechanicus", "Leagues of Votann": "leagues-of-votann",
                 # factions with a BSData cut that the archive sample never hit — added for BCP field loading
                 "Imperial Knights": "imperial-knights", "Death Guard": "death-guard",
                 "Grey Knights": "grey-knights", "Chaos Knights": "chaos-knights",
                 "Genestealer Cult": "genestealer-cults", "Genestealer Cults": "genestealer-cults",
                 "Adepta Sororitas": "adepta-sororitas", "Black Templars": "black-templars",
                 "Deathwatch": "deathwatch", "Imperial Agents": "agents-of-the-imperium"}

_HDR = re.compile(r'^(.*?)\(([\d,]+)\s*points?\)', re.I)
_NORM = lambda s: s.replace("’", "'").replace("‘", "'")


def _archive():
    return json.load(open(_ARCHIVE, encoding="utf-8"))


def pick(faction, detachment=None, min_text=800):
    """Best-record archive entry for a faction (optionally a detachment substring) that has full text."""
    ls = [L for L in _archive() if L.get("faction") == faction and len(L.get("listText", "")) >= min_text
          and (detachment is None or detachment.lower() in (L.get("detachment") or "").lower())]
    if not ls:
        raise LookupError(f"no full-text {faction} list" + (f" for detachment {detachment!r}" if detachment else "")
                          + " in the archive (it may be one of the 54 truncated entries — re-fetch it)")
    ls.sort(key=lambda L: (-(L.get("wins", 0)), L.get("losses", 0)))
    return ls[0]


def _resolve(slug, name):
    """Resolve a datasheet to a profile, trying the faction slug then its chapter fallbacks + apostrophe norm."""
    for sl in [slug] + _FALLBACK.get(slug, []):
        for nm in (name, _NORM(name)):
            try:
                return sl, db.profile(sl, nm)
            except Exception:
                pass
    return None, None


_LEADER = ("nob", "boss", "sergeant", "sarge", "champion", "aspiring", "prime", "warden", "exarch",
           "captain", "lord", "canoptek", "runtherd", "shas", "crisis")
# weapon/wargear nouns — a body-line noun containing one of these is WARGEAR (e.g. "Hormagaunt talons"),
# not a model, so it must NOT be counted even when it shares the unit's stem.
_WARGEAR = ("talon", "blade", "claw", "sword", "gun", "rifle", "cannon", "fist", "pistol", "bolt", "spear",
            "axe", "hammer", "whip", "lash", "scythe", "launcher", "flamer", "melta", "plasma", "knife",
            "glaive", "maul", "staff", "rokkit", "blasta", "shoota", "slugga", "weapon", "tools", "grenade")


def _model_count(name, block, prof):
    """Model count from the bullet block. Single-model datasheets (character / non-suit vehicle / titanic
    / non-suit monster) are 1. For squads, count BODY lines — 'Nx <noun>' whose noun shares a stem with the
    unit name (the rank-and-file) plus any distinct leader-model line — not the wargear '◦' bullets."""
    kw = [k.upper() for k in prof.get("keywords", [])]
    single = ("CHARACTER" in kw or "TITANIC" in kw or ("VEHICLE" in kw and "MOUNTED" not in kw)
              or ("MONSTER" in kw and "MOUNTED" not in kw))
    if single:
        return 1
    stems = [w.lower().rstrip("s") for w in re.findall(r"[A-Za-z']+", name) if len(w) > 3]
    bodies = 0
    for ln in block:
        m = re.match(r"^[•▪◦\-\s]*(\d+)x\s+([A-Za-z].*)$", ln.strip())
        if not m:
            continue
        n, noun = int(m.group(1)), m.group(2).lower()
        if any(wg in noun for wg in _WARGEAR):        # wargear named after the unit (Hormagaunt talons) — skip
            continue
        if any(st in noun for st in stems) or any(lw in noun for lw in _LEADER):
            bodies += n
    if not bodies:                                         # nothing matched -> largest single Nx in the block
        ns = [int(x) for x in re.findall(r"(\d+)x\s", " ".join(block))]
        bodies = max(ns) if ns else 1
    return bodies


def _role_threat(prof, models, pts):
    """Auto-assign a sim role + threat weight from the resolved profile (the modelling heuristic)."""
    kw = [k.upper() for k in prof.get("keywords", [])]
    st = prof["stats"]
    W = int(st.get("W", 1)); T = int(st.get("T", 4)); M = int(st.get("M", 6)); OC = int(st.get("OC", 1))
    big = ("MONSTER" in kw or "VEHICLE" in kw) and W >= 8
    if big:
        role = "anti_tank"
    elif "CHARACTER" in kw and models == 1:
        role = "character"
    elif M >= 12:
        role = "fast"
    elif models >= 10 and pts / max(1, models) <= 9:
        role = "screen"
    elif pts / max(1, models) <= 12 and models >= 5:
        role = "action"
    else:
        role = "line"
    # threat ~ points, softened; big durable things and characters get a floor
    threat = round(min(6.0, max(0.3, pts / 60.0)), 1)
    if big:
        threat = round(min(6.0, max(threat, 2.4 + (W - 8) * 0.15 + (T - 8) * 0.2)), 1)
    return role, threat


def parse_units(text):
    """Yield (name, points, block_lines) per unit entry in an exported listText."""
    lines = text.splitlines()
    hdrs = [i for i, ln in enumerate(lines) if _HDR.match(ln.strip())]
    for k, i in enumerate(hdrs):
        s = lines[i].strip()
        m = _HDR.match(s)
        name = m.group(1).strip(" •\t•")
        pts = int(m.group(2).replace(",", ""))
        if not name or not name[0].isalpha():
            continue
        if pts >= 1000:                 # the army-name / "Strike Force" line carries the ~2000pt total
            continue
        # skip list-title / section headers (they carry the army points total, not a datasheet)
        if re.match(r'(?i)(strike force|force disposition|attached|other datasheet|character|battleline|'
                    r'dedicated transport|allied)', name):
            continue
        block = lines[i + 1: (hdrs[k + 1] if k + 1 < len(hdrs) else len(lines))]
        yield name, pts, block


# ---- per-faction default tapestry (applied by keyword) + override registry -------------------------
def _astartes_default(army):
    OATH = _R.OATH
    for u in army.units:
        # Oath of Moment ~ reroll-1s to hit, diffused army-wide; give the damage dealers (not pure chaff)
        if u.role in ("line", "anti_tank", "character", "fast") and "reroll_hits" not in u.abilities:
            u.abilities.update(OATH)


_FACTION_DEFAULT = {
    "space-marines": _astartes_default, "blood-angels": _astartes_default,
    "dark-angels": _astartes_default,
}

# Faction OVERRIDE hooks — the modelling the heuristics can't derive. Registered by the rosters module
# (which owns the deep tapestry: C'tan resilience, transports, monster regen, weapon-loadout fixes).
OVERRIDES = {}


def register_override(slug, fn):
    OVERRIDES[slug] = fn


def all_lists(min_text=800):
    """Every runnable (full-text) archive list, as light dicts (index + faction/detachment/disposition/
    record). Use the index with load(entry=...) / builder(index=...) to run YOUR list against any of them."""
    return [dict(i=i, faction=L["faction"], detachment=(L.get("detachment") or "").split("|")[0].strip(),
                 disposition=L.get("disposition", ""), wins=L.get("wins", 0), losses=L.get("losses", 0),
                 player=L.get("playerName", ""), slug=_FACTION_SLUG.get(L["faction"]))
            for i, L in enumerate(_archive()) if len(L.get("listText", "")) >= min_text
            and _FACTION_SLUG.get(L["faction"])]


def builder(faction=None, detachment=None, index=None, disposition=None):
    """A build_opp function bound to a specific archive list — pass to runbook/optimize/run as the opponent.
    Either an explicit `index` (from all_lists) or faction[+detachment] (best-record match)."""
    def b():
        return load(faction=faction, detachment=detachment, index=index, disposition=disposition)
    return b


def load(faction=None, detachment=None, disposition=None, name=None, override=None, min_text=800, index=None,
         entry=None):
    """Build an Army from an archive list — a specific one (`index` or `entry`) or the best-record match for
    `faction`[+`detachment`]. `disposition` overrides the archive's; `override(army)` applies faction tapestry."""
    if entry is None:
        entry = _archive()[index] if index is not None else pick(faction, detachment, min_text)
    faction = faction or entry["faction"]
    slug = _FACTION_SLUG.get(faction) or faction
    units, missing = [], []
    for uname, pts, block in parse_units(entry["listText"]):
        sl, prof = _resolve(slug, uname)
        if prof is None:
            missing.append(uname)
            continue
        models = _model_count(uname, block, prof)
        role, threat = _role_threat(prof, models, pts)
        units.append(_R.mk(sl, uname if sl == slug else _NORM(uname), models, role=role, threat=threat))
    disp = disposition or _DISP.get((entry.get("disposition") or "").strip().lower(), "take-and-hold")
    army = Army(name or f"{faction} — {entry.get('detachment', '?')} ({entry.get('wins')}-{entry.get('losses')})",
                disp, "B", units, cp=3)
    _FACTION_DEFAULT.get(slug, lambda a: None)(army)
    (override or OVERRIDES.get(slug, lambda a: None))(army)
    army._missing = missing               # datasheets absent from the BSData cut (skipped) — surfaced for review
    _R._deploy(army)
    return army
