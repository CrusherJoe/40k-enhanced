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
# Agents of the Imperium (Navigator, Assassins, Inquisitors, …) ally into most Imperium armies,
# so their datasheets live in the agents cut, not the host army's — add it as a trailing fallback.
_AGENTS = ["agents-of-the-imperium"]
# the common Marine pool + every chapter that holds named characters other chapters can't see
_SM = ["space-marines", "salamanders", "ultramarines", "imperial-fists", "raven-guard",
       "white-scars", "iron-hands"]
_FALLBACK = {"blood-angels": _SM + _AGENTS, "dark-angels": _SM + _AGENTS,
             "space-marines": _SM[1:] + _AGENTS,
             "black-templars": _SM + _AGENTS, "deathwatch": _SM + _AGENTS, "space-wolves": _SM + _AGENTS,
             # Imperium armies that commonly ally in an Agent (e.g. Knights' Navigator)
             "imperial-knights": _AGENTS, "astra-militarum": _AGENTS, "adepta-sororitas": _AGENTS,
             "adeptus-custodes": _AGENTS, "adeptus-mechanicus": _AGENTS, "grey-knights": _AGENTS,
             # Chaos cross-allies: Knights ally Daemons/CSM; Daemons appear in CSM/DG/TS/WE/Knight lists
             "chaos-knights": ["chaos-daemons", "chaos-space-marines"],
             "chaos-daemons": ["chaos-space-marines", "chaos-knights"],
             "chaos-space-marines": ["chaos-daemons", "chaos-knights"],
             "death-guard": ["chaos-daemons", "chaos-knights"], "thousand-sons": ["chaos-daemons"],
             "world-eaters": ["chaos-daemons"],
             # Xenos cross-allies: GSC ally Tyranids; Drukhari/Aeldari share the Aeldari range
             "genestealer-cults": ["tyranids"], "drukhari": ["aeldari"], "aeldari": ["drukhari"]}

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


def _group_map(lines):
    """Map each line index -> the 'Attached unit N' group it falls under (or None). BCP/GW exports group a
    Bodyguard unit with its attached Leader/Support CHARACTERs under 'Attached unit N' blocks; a plain
    section header (BATTLELINE / OTHER DATASHEETS / ...) ends the attached region."""
    gmap, g = {}, None
    for idx, ln in enumerate(lines):
        s = ln.strip()
        m = re.match(r'(?i)^attached unit\s+(\d+)', s)
        if m:
            g = int(m.group(1))
        elif re.match(r'(?i)^(battleline|other datasheets?|dedicated transports?|allied|characters?)\b', s):
            g = None
        gmap[idx] = g
    return gmap


def parse_units_ex(text):
    """Yield (name, points, block_lines, group, role) per unit. `group` is the 'Attached unit N' id (or
    None); `role` is 'leader'|'support'|'bodyguard'|None from the unit's '• Attached as:' line — the
    AUTHORITATIVE attachment structure from the export (so we don't have to guess who leads whom)."""
    lines = text.splitlines()
    gmap = _group_map(lines)
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
        role = None
        for bl in block[:8]:
            mm = re.search(r'(?i)attached as:\s*(leader|support|bodyguard)', bl)
            if mm:
                role = mm.group(1).lower()
                break
        yield name, pts, block, gmap.get(i), role


def parse_units(text):
    """Yield (name, points, block_lines) per unit entry (back-compat shim over parse_units_ex)."""
    for name, pts, block, _grp, _role in parse_units_ex(text):
        yield name, pts, block


# ---- ENHANCEMENTS: the foundation of the tapestry (sit just above detachment rules) -----------------
_ENH_TEXT = {}


def _enh_text(slug, name):
    """Enhancement rules text from the BSData rules DB (cached). Returns '' if not found."""
    key = (slug, name)
    if key not in _ENH_TEXT:
        txt = ""
        try:
            import sys, os as _os
            sys.path.insert(0, _os.path.join(_os.path.dirname(_os.path.dirname(_os.path.dirname(
                _os.path.dirname(_os.path.abspath(__file__))))), "tools"))
            import db as _db
            r = _db.find_rules(slug, name) or {}
            exact = next((v for k, v in r.items() if k.lower() == name.lower()), None)
            txt = str(exact if exact is not None else (next(iter(r.values())) if r else ""))
        except Exception:
            txt = ""
        _ENH_TEXT[key] = txt
    return _ENH_TEXT[key]


def _parse_enhancements(block):
    """Enhancement names on a unit, from its '• Enhancements: X' line(s)."""
    out = []
    for bl in block:
        m = re.search(r"(?i)enhancements?:\s*(.+)", bl)
        if m:
            out += [e.strip() for e in re.split(r"\s*,\s*|\s+and\s+", m.group(1)) if e.strip()]
    return out


def _apply_enhancements(slug, u):
    """Classify each enhancement's DB rules text into modelled effects. ABILITY effects (re-roll/crit/FNP)
    go on the CHARACTER now (the attach merge carries them to its squad); WEAPON/keyword effects
    (Lethal/Sustained/Dev/+AP/Precision/Battleline) are stashed in u._enh_wfx and applied to the BEARER'S
    UNIT at attach time (they buff 'the bearer and Battleline models in the bearer's unit')."""
    u._enh_wfx = None
    if not getattr(u, "_enh", None):
        return
    wfx = {"ranged_kw": [], "melee_kw": [], "melee_ap": 0, "unit_ability": {}, "unit_kw": []}
    for name in u._enh:
        raw = _enh_text(slug, name).upper()
        if not raw:
            continue
        # only classify the UNCONDITIONAL clause — drop 'if this unit has ... / if that ...' riders so a
        # conditional keyword (e.g. Fusillade's [SUSTAINED HITS 1] gated on the Pyromancy Discipline)
        # isn't granted unconditionally. Conservative: under-grant a situational rider, never over-grant.
        t = re.split(r"\bIF (?:THIS|THAT|YOU|YOUR|THE BEARER)\b", raw)[0]
        melee = "MELEE" in t
        ranged = ("RANGED" in t or "SHOOTING" in t) and not melee
        dst = wfx["ranged_kw"] if ranged else (wfx["melee_kw"] if melee else wfx["ranged_kw"])
        if "LETHAL HITS" in t:
            dst.append("LETHAL HITS")
        if "SUSTAINED HITS" in t:
            dst.append("SUSTAINED HITS 1")
        if "DEVASTATING WOUNDS" in t:
            dst.append("DEVASTATING WOUNDS")
        if "PRECISION" in t:
            wfx["unit_ability"]["precision"] = True           # lets the squad snipe attached leaders
        if "ARMOUR PENETRATION" in t or "ARMOR PENETRATION" in t:
            wfx["melee_ap"] += 1                               # 'improve AP by 1' (Blades of Valour: melee)
        if "BATTLELINE KEYWORD" in t or "HAS THE BATTLELINE" in t:
            wfx["unit_kw"].append("BATTLELINE")
        if "RE-ROLL" in t or "REROLL" in t:
            if "WOUND" in t:
                u.abilities["reroll_wounds"] = "fails" if "FAILED WOUND" in t else "ones"
            if "HIT ROLL" in t:
                u.abilities["reroll_hits"] = "fails" if "FAILED HIT" in t else "ones"
        m = re.search(r"FEEL NO PAIN (\d)\+?", t)
        if m:
            fnp = m.group(1) + "+"
            u.fnp = fnp if not u.fnp else min(u.fnp, fnp, key=lambda s: int(str(s)[0]))
    u._enh_wfx = wfx


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
         entry=None, side="B"):
    """Build an Army from an archive list — a specific one (`index` or `entry`) or the best-record match for
    `faction`[+`detachment`]. `disposition` overrides the archive's; `override(army)` applies faction tapestry.
    `side` "A" builds it as YOUR army (own deployment zone / turn), "B" (default) as the opponent."""
    if entry is None:
        entry = _archive()[index] if index is not None else pick(faction, detachment, min_text)
    faction = faction or entry["faction"]
    slug = _FACTION_SLUG.get(faction) or faction
    units, missing, submodels = [], [], set()
    for uname, pts, block, grp, arole in parse_units_ex(entry["listText"]):
        sl, prof = _resolve(slug, uname)
        if prof is None:
            missing.append(uname)
            continue
        # a datasheet's sub-model pilots (e.g. Sir Hekhtur under Canis Rex) may be listed on
        # their own line by the exporter — record them so they aren't flagged "missing" below.
        for ep in prof.get("extra_profiles", []):
            submodels.add(_NORM(ep.get("name", "")))
        models = _model_count(uname, block, prof)
        role, threat = _role_threat(prof, models, pts)
        u = _R.mk(sl, uname if sl == slug else _NORM(uname), models, role=role, threat=threat)
        # AUTHORITATIVE attachment from the export: which 'Attached unit N' group + Leader/Support/Bodyguard
        u._grp = grp
        u._arole = arole
        # ENHANCEMENTS — foundation of the tapestry (sit just above detachment rules): parse the names and
        # fold their combat effect into this unit's abilities so an attached leader carries it to its squad.
        u._enh = _parse_enhancements(block)
        _apply_enhancements(sl, u)
        units.append(u)
    missing = [m for m in missing if _NORM(m) not in submodels]
    disp = disposition or _DISP.get((entry.get("disposition") or "").strip().lower(), "take-and-hold")
    army = Army(name or f"{faction} — {entry.get('detachment', '?')} ({entry.get('wins')}-{entry.get('losses')})",
                disp, side, units, cp=3)
    _FACTION_DEFAULT.get(slug, lambda a: None)(army)
    (override or OVERRIDES.get(slug, lambda a: None))(army)
    # ARMY RULE — Oath of Moment: re-roll Hits vs the Oath target; +1 to Wound too for a Codex-SM
    # detachment (space-marines slug) with no BA/DA/DW/SW. Caanok Var (Calculated Annihilation) re-rolls
    # Wound-1s vs the target AND re-selects it when it dies (Oath never wastes). game.py applies it.
    if slug in ("space-marines", "blood-angels", "dark-angels"):
        army._oath = True
        army._oath_codex_bonus = (slug == "space-marines")
        army._caanok = any("caanok" in (u.name or "").lower() for u in army.units)
    army._missing = missing               # datasheets absent from the BSData cut (skipped) — surfaced for review
    _R._deploy(army)
    return army
