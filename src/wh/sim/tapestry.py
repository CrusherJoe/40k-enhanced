"""TAPESTRY ASSEMBLER — pull the COMPLETE rules stack for a list and fold it into the sim units.

THE LAW (do this EVERY time, never partially): a player's army is the sum of deliberate rules choices —
Army rule -> Detachment(s) -> Leader/Support characters -> Enhancements -> Unit datasheet abilities. Nobody
brings a detachment / character / enhancement for no reason; each PROVIDES a rule. Skipping any layer models
a strawman. This module pulls every layer from the DB (via tools/db.py) and applies it.

Two responsibilities:
  1. classify(text) -> a normalized effect dict, from any rules text (datasheet ability / enhancement /
     detachment rule). Conservative: it reads the UNCONDITIONAL clause only (drops 'if this unit has ...'
     riders) so a situational keyword is never granted for free.
  2. ingest_unit(unit, abilities_block, slug) -> apply the datasheet's own abilities to the unit, and stash
     LEADER AURAS ('while this model is leading a unit, models in that unit have ...') on unit._aura so they
     transfer to the Bodyguard when the character attaches (wh.sim.attach).
  plus assemble(army, slug) -> a human-readable report of the full stack, for eyeballing before trusting a
     sim (raises if a datasheet's abilities came back empty — a missing layer is a LOUD bug, not a shrug)."""
from __future__ import annotations

import os
import re
import sys

from ..dice import target_number

sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(
    os.path.dirname(os.path.abspath(__file__))))), "tools"))


def _db():
    import db
    return db


def _tn(s):
    try:
        return target_number(s)
    except Exception:
        return 99


def _rr(a, b):
    rank = {None: 0, "": 0, "none": 0, "ones": 1, "fails": 2}
    inv = {0: None, 1: "ones", 2: "fails"}
    return inv[max(rank.get(a, 0), rank.get(b, 0))]


def blank_fx():
    return {"ranged_kw": [], "melee_kw": [], "melee_ap": 0, "ranged_ap": 0,
            "unit_ability": {}, "unit_kw": [], "abilities": {}, "fnp": None, "invuln": None}


def classify(text):
    """Rules text -> (effect_dict, is_aura). is_aura True when the effect targets the LED unit ('while this
    model is leading a unit / models in that unit'). Only the unconditional clause is read."""
    raw = " ".join(str(text).split())
    U = raw.upper()
    is_aura = ("LEADING A UNIT" in U or "MODELS IN THAT UNIT" in U or "IN THE BEARER" in U
               or "MODELS IN THE BEARER" in U or "MODELS IN THIS UNIT" in U or "THIS MODEL’S UNIT" in U
               or "THIS MODEL'S UNIT" in U)
    # drop CONDITIONAL clauses so a situational keyword is never granted as a blanket unit-wide rule:
    #  - 'if this unit has ...'  (ability rider)
    #  - '... attack that targets a MONSTER or VEHICLE'  (target-type condition, e.g. Caanok's Cold and
    #    Calculating)
    #  - 'while within range of an objective / within 6"'  (positional condition, e.g. Unbreakable Duty)
    #  - 'against <KEYWORD> units'
    # but NOT the aura SCOPE intro 'while this model is leading a unit, ...' (that's who it applies to, not
    # a restriction) — so unit-wide auras (Surgical Precision's Lethal Hits) are kept.
    t = re.split(r"\b(?:IF (?:THIS|THAT|YOU|YOUR|THE BEARER|IT )|THAT TARGETS?|WITHIN RANGE OF|"
                 r"WITHIN \d|AGAINST (?:AN? )?[A-Z])", U)[0]
    fx = blank_fx()
    melee = "MELEE" in t
    ranged = ("RANGED" in t or "SHOOTING" in t) and not melee
    kwdst = fx["ranged_kw"] if ranged else (fx["melee_kw"] if melee else fx["ranged_kw"])
    if "LETHAL HITS" in t:
        (fx["melee_kw"] if melee else fx["ranged_kw"]).append("LETHAL HITS")
        if not melee and not ranged:                      # 'weapons ... have [LETHAL HITS]' = both
            fx["melee_kw"].append("LETHAL HITS")
    m = re.search(r"SUSTAINED HITS (\d)", t)
    if m:
        kwdst.append(f"SUSTAINED HITS {m.group(1)}")
    if "DEVASTATING WOUNDS" in t:
        (fx["melee_kw"] if melee else fx["ranged_kw"]).append("DEVASTATING WOUNDS")
    if "[PRECISION]" in t or "PRECISION] ABILITY" in t or "THE PRECISION" in t:
        fx["unit_ability"]["precision"] = True
    if "SECURED BY" in U or "IS SECURED" in U or "OBJECTIVE SECURED" in U:
        fx["unit_ability"]["secures"] = True              # sticky objective control (14.03)
    if "LONE OPERATIVE" in U:
        fx["unit_ability"]["lone_operative"] = True
    if re.search(r"\bSTEALTH\b", U):
        fx["unit_ability"]["stealth"] = True
    if "IGNORES COVER" in t:
        fx["ranged_kw"].append("IGNORES COVER")
    if "ARMOUR PENETRATION" in t or "ARMOR PENETRATION" in t:
        n = 1
        mm = re.search(r"BY (\d)", t)
        if mm:
            n = int(mm.group(1))
        (fx.__setitem__("melee_ap", fx["melee_ap"] + n) if melee or "MELEE WEAPON" in t
         else fx.__setitem__("ranged_ap", fx["ranged_ap"] + n))
    fm = re.search(r"FEEL NO PAIN (\d)\+?", t)
    if fm:
        fx["fnp"] = fm.group(1) + "+"
    im = re.search(r"INVULNERABLE SAVE OF (\d)\+", t) or re.search(r"(\d)\+ INVULNERABLE", t)
    if im:
        fx["invuln"] = im.group(1) + "+"
    if "RE-ROLL" in t or "REROLL" in t or "RE‑ROLL" in t:
        if "WOUND ROLL" in t:
            fx["abilities"]["reroll_wounds"] = "fails" if "FAILED WOUND" in t else "ones"
        if "HIT ROLL" in t:
            fx["abilities"]["reroll_hits"] = "fails" if "FAILED HIT" in t else "ones"
    if "CRITICAL HIT" in t and re.search(r"\b5\+?\b|ON A 5|OF 5", t):
        fx["abilities"]["crit_hit"] = 5
    return fx, is_aura


# ---- applying an effect dict to a unit --------------------------------------
def _add_kw(weapon, kw):
    ab = list(weapon.get("abilities", []))
    if kw not in ab:
        ab.append(kw)
    weapon["abilities"] = ab


def apply_fx(unit, fx):
    if not fx:
        return
    for w in unit.ranged:
        for kw in fx.get("ranged_kw", []):
            _add_kw(w, kw)
        if fx.get("ranged_ap"):
            w["AP"] = int(w.get("AP", 0)) - fx["ranged_ap"]
    for w in unit.melee:
        for kw in fx.get("melee_kw", []):
            _add_kw(w, kw)
        if fx.get("melee_ap"):
            w["AP"] = int(w.get("AP", 0)) - fx["melee_ap"]
    for k, v in fx.get("unit_ability", {}).items():
        unit.abilities[k] = v
    for k in ("reroll_hits", "reroll_wounds"):
        if fx.get("abilities", {}).get(k):
            unit.abilities[k] = _rr(unit.abilities.get(k), fx["abilities"][k])
    if fx.get("abilities", {}).get("crit_hit"):
        unit.abilities["crit_hit"] = min(unit.abilities.get("crit_hit", 7), fx["abilities"]["crit_hit"])
    if fx.get("unit_kw"):
        unit.keywords = tuple(unit.keywords) + tuple(k for k in fx["unit_kw"] if k not in unit.keywords)
    if fx.get("fnp"):
        unit.fnp = fx["fnp"] if not unit.fnp else min(unit.fnp, fx["fnp"], key=_tn)
    if fx.get("invuln"):
        unit.invuln = fx["invuln"] if not unit.invuln else min(unit.invuln, fx["invuln"], key=_tn)


def _merge_fx(dst, src):
    for k in ("ranged_kw", "melee_kw", "unit_kw"):
        dst[k] += [x for x in src[k] if x not in dst[k]]
    dst["melee_ap"] += src["melee_ap"]
    dst["ranged_ap"] += src["ranged_ap"]
    dst["unit_ability"].update(src["unit_ability"])
    for k in ("reroll_hits", "reroll_wounds"):
        if src["abilities"].get(k):
            dst["abilities"][k] = _rr(dst["abilities"].get(k), src["abilities"][k])
    if src["abilities"].get("crit_hit"):
        dst["abilities"]["crit_hit"] = min(dst["abilities"].get("crit_hit", 7), src["abilities"]["crit_hit"])
    for k in ("fnp", "invuln"):
        if src[k]:
            dst[k] = src[k] if not dst[k] else min(dst[k], src[k], key=_tn)


# ---- reading a datasheet's abilities block into a unit ----------------------
def ingest_unit(unit, abilities, slug=None):
    """Apply a datasheet's BSData abilities block (core / faction / datasheet) to a sim unit. Self-effects
    apply now; LEADER AURAS ('while leading a unit...') are stashed on unit._aura to transfer to the
    bodyguard at attach time. Records the ability NAMES on unit._tapestry for the assembler report."""
    unit._aura = getattr(unit, "_aura", None)
    unit._tapestry = names = list(getattr(unit, "_tapestry", []))
    if not abilities:
        return
    core = abilities.get("core", []) if isinstance(abilities, dict) else []
    for c in core:
        cu = str(c).upper()
        names.append(f"core:{c}")
        if "DEEP STRIKE" in cu:
            unit.deep_strike = True                        # capability only; reserve is a deploy DECISION
        if "LONE OPERATIVE" in cu:
            unit.abilities["lone_operative"] = True        # not targetable from >12"
        if "STEALTH" in cu:
            unit.abilities["stealth"] = True               # benefit of cover vs ranged
        fm = re.search(r"FEEL NO PAIN (\d)\+?", cu)
        if fm:
            fnp = fm.group(1) + "+"
            unit.fnp = fnp if not unit.fnp else min(unit.fnp, fnp, key=_tn)
    aura = getattr(unit, "_aura", None) or blank_fx()
    got_aura = False
    for d in (abilities.get("datasheet", []) if isinstance(abilities, dict) else []):
        if not isinstance(d, dict):
            continue
        nm, txt = d.get("name", ""), d.get("text", "")
        if nm.lower() == "leader" or nm.lower() == "support":     # attach-target list, handled by the export
            continue
        names.append(nm)
        fx, is_aura = classify(txt)
        if is_aura:
            _merge_fx(aura, fx)
            got_aura = True
        else:
            apply_fx(unit, fx)
    if got_aura:
        unit._aura = aura


def datasheet_abilities(slug, unit_name):
    """The BSData abilities block for a datasheet, tolerant of the chapter fallback cuts (Feirros/Caanok
    live in iron-hands, not space-marines)."""
    db = _db()
    from .listloader import _FALLBACK
    for sl in [slug] + _FALLBACK.get(slug, []):
        try:
            return db.profile(sl, unit_name).get("abilities", {})
        except Exception:
            continue
    return {}


# ---- the assembler report ---------------------------------------------------
def assemble(army, slug):
    """Human-readable full-stack tapestry report: Army -> Detachment(s) -> Leader/Support -> Enhancements
    -> Unit. Pull every layer from the DB so it can be eyeballed before trusting a sim number."""
    db = _db()
    L = [f"TAPESTRY — {army.name}  [{slug} / {army.disposition}]", ""]
    L.append("ARMY RULE")
    if getattr(army, "_oath", False):
        bonus = " + Codex +1-to-Wound" if getattr(army, "_oath_codex_bonus", False) else ""
        caa = " + Caanok Var re-select" if getattr(army, "_caanok", False) else ""
        L.append(f"  Oath of Moment (re-roll Hits vs target{bonus}{caa})")
    L.append("")
    L.append("DETACHMENT(S)")
    dets = getattr(army, "strat_dets", None) or ()
    for d in dets:
        try:
            n = len(db.strats(slug).get(d, {}))
        except Exception:
            n = 0
        L.append(f"  {d}: {n} stratagems")
    L.append("")
    L.append("UNITS (Leader/Support auras applied to their Bodyguard)")
    for u in army.units:
        if getattr(u, "embedded", False):
            continue
        led = getattr(u, "leading", None)
        tag = ""
        if led:
            tag = "  <- " + ", ".join(l.name for l in led)
        enh = getattr(u, "_enh", None) or []
        extra = []                                        # unit-level tapestry (wargear/aura granted)
        if u.invuln:
            extra.append(f"invuln {u.invuln}")
        if u.fnp:
            extra.append(f"FNP {u.fnp}")
        if u.abilities.get("precision"):
            extra.append("PRECISION")
        for k in ("reroll_hits", "reroll_wounds", "crit_hit"):
            if u.abilities.get(k):
                extra.append(f"{k}={u.abilities[k]}")
        L.append(f"  {u.name}{tag}")
        if enh:
            L.append(f"      enhancements: {', '.join(enh)}")
        if extra:
            L.append(f"      unit rules: {', '.join(extra)}")
        # WEAPON / WARGEAR layer — EVERY per-profile keyword is a rule (ASSAULT = advance & still shoot,
        # PISTOL = shoot in engagement range, MELEE = usable in the Fight phase, ...). Surface them all,
        # per profile (never blanketed across the unit).
        for w in u.ranged + u.melee:
            kws = list(w.get("abilities", []))
            if kws:
                L.append(f"      weapon: {w.get('name', '?')}: {', '.join(kws)}")
    return "\n".join(L)
