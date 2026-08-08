"""Detachment army rules as ENGINE EFFECTS, so optimize() can TEST a detachment swap (not just flag it).

Each Custodes detachment rule is transcribed from the faction pack (data/faction-packs/adeptus-custodes.txt,
the DETACHMENT RULES blocks) and mapped to the abilities the sim actually reads (crit_hit / reroll_hits /
reroll_charge / move / oc). A detachment REPLACES the army's detachment rule, so applying a non-Shield-Host
detachment first strips Shield Host's Martial Mastery (the only crit_hit source in a Custodes build) and then
grants its own effect to the qualifying units (by keyword). Base Custodes carry no VEHICLE/WALKER units, so a
vehicle/dread detachment only pays off once dreads/tanks are swapped in — which is precisely the interaction
optimize() surfaces. Effects are deliberately conservative (a re-roll of 1s stands in for a diffuse +1).

  from wh.sim.detachments import under, apply_detachment, CUSTODES
  build = under(rosters.custodes, "Might of the Moritoi")   # a build_fn under a different detachment
"""
from __future__ import annotations


def _strip_martial_mastery(army):
    """Remove Shield Host's Martial Mastery (crit-on-5) — the detachment being replaced. Intrinsic unit
    abilities (a Blade Champion's charge re-roll, Allarus wound re-roll) are NOT detachment-granted and stay."""
    for u in army.units:
        u.abilities.pop("crit_hit", None)


def _shield_host(army):
    # Martial Mastery: friendly ADEPTUS CUSTODES melee crit on 5+ (already baked into the base build's
    # Ka'tah units). No-op: the base custodes() IS Shield Host; new non-Custodes vehicles don't get it.
    return army


def _might_of_the_moritoi(army):
    # "March of the Honoured Dead": ADEPTUS CUSTODES WALKER units have +2" M and +1 to advance & charge rolls.
    _strip_martial_mastery(army)
    for u in army.units:
        if "WALKER" in u.keywords:
            u.move += 2
            u.abilities["reroll_charge"] = True        # +1 charge ~ a charge re-roll in this model
    return army


def _solar_spearhead(army):
    # "Auric Armour": ADEPTUS CUSTODES VEHICLE units at Starting Strength +2 OC; when damaged, re-roll hit
    # rolls of 1. Modelled as +2 OC and a steady re-roll of 1s on those vehicles. (Costs 2 Detachment Points.)
    _strip_martial_mastery(army)
    for u in army.units:
        if "VEHICLE" in u.keywords:
            u.oc += 2
            u.abilities["reroll_hits"] = "ones"
    return army


def _lions_of_the_emperor(army):
    # "Against All Odds": a non-VEHICLE unit with no other friendly unit within 6" adds 1 to Hit & Wound.
    # Isolation is rare in a castle and not tracked per-attack here -> approximated conservatively as a
    # re-roll of 1s to hit on non-vehicle units (well below the full +1/+1 the rule can reach when isolated).
    _strip_martial_mastery(army)
    for u in army.units:
        if "VEHICLE" not in u.keywords:
            u.abilities.setdefault("reroll_hits", "ones")
    return army


def _tharanatoi(army):
    # "The Hammer Falls": an ADEPTUS CUSTODES TERMINATOR unit that made an ingress move can re-roll charge.
    _strip_martial_mastery(army)
    for u in army.units:
        if "TERMINATOR" in u.keywords and u.deep_strike:
            u.abilities["reroll_charge"] = True
    return army


CUSTODES = {
    "Shield Host": _shield_host,
    "Might of the Moritoi": _might_of_the_moritoi,
    "Solar Spearhead": _solar_spearhead,
    "Lions of the Emperor": _lions_of_the_emperor,
    "Tharanatoi Hammerblow": _tharanatoi,
}

# Detachment Points cost (from the pack: Solar Spearhead is the 2-DP ARMOURY detachment; the rest are 1 DP
# in this modelling). Surfaced so a swap's DP trade is explicit — you balance it against your enhancements.
DP = {"Shield Host": 1, "Might of the Moritoi": 1, "Solar Spearhead": 2,
      "Lions of the Emperor": 1, "Tharanatoi Hammerblow": 1}


def apply_detachment(army, name, table=None):
    """Mutate `army` so it plays under detachment `name`. Always call on a freshly-built army (each
    Monte-Carlo build), never twice on the same object — the WALKER/VEHICLE stat bumps are additive."""
    (table or CUSTODES)[name](army)
    army.detachment_rules = (name,)
    return army


def under(build_fn, name, table=None):
    """Wrap a roster build function so it builds under detachment `name` — a drop-in build_fn for run/optimize."""
    def b():
        return apply_detachment(build_fn(), name, table)
    return b


# ---------------------------------------------------------------------------------------------------------
# More faction detachment models (2026-08-08). ONLY detachments whose army rule is a FLAT combat/defensive
# buff that maps faithfully to the engine's vocabulary are modelled here — transcribed from the faction packs
# (data/faction-packs/*). Detachments driven by Miracle Dice / rotating Combat Doctrines / scoring / movement
# tricks / narrow conditionals are deliberately NOT modelled (a fabricated flat buff would mislead the sim);
# they fall back to bcp_advisor's DATA-DRIVEN detachment read (real finish %ile). Effects stay conservative
# (a re-roll of 1s stands in for a +1). No base-rule strip: these factions' own detachment rule isn't applied
# by listloader, so a tested model shows its MARGINAL value over running no detachment rule.
def _grant(army, pred, abil=None, move=0, oc=0, fnp=None):
    for u in army.units:
        if not pred(u):
            continue
        if abil:
            for k, v in abil.items():
                u.abilities[k] = v
        if move:
            u.move += move
        if oc:
            u.oc += oc
        if fnp:
            u.fnp = fnp if not getattr(u, "fnp", None) else min(u.fnp, fnp)
    return army


def _kw(*ks):
    return lambda u: any(k in u.keywords for k in ks)


_ALL = lambda u: True

# --- Space Marines (Astartes) ---
SPACE_MARINES = {
    # Psychic Disciplines → Divination (the competitive pick): ADEPTUS ASTARTES PSYKER units re-roll 1s to hit & wound
    "Librarius Conclave": lambda a: _grant(a, _kw("PSYKER"), abil={"reroll_hits": "ones", "reroll_wounds": "ones"}),
    # Calculated Annihilation: re-roll a Wound roll of 1 vs the Oath of Moment target — approx army-wide wound-1 re-roll
    "Hammer of Avernii": lambda a: _grant(a, _ALL, abil={"reroll_wounds": "ones"}),
    # Masters of Shadow: ranged attacks from >12" hit you at Benefit of Cover — model as army-wide Stealth (−1 to be hit)
    "Shadowmark Talon": lambda a: _grant(a, _ALL, abil={"stealth": True}),
    # Mastered Doctrines (rotating Combat Doctrines) — conservative army-wide re-roll of 1s to hit
    "Blade of Ultramar": lambda a: _grant(a, _ALL, abil={"reroll_hits": "ones"}),
}
# --- Imperial Knights ---
IMPERIAL_KNIGHTS = {
    # Knights of Legend: every IMPERIAL KNIGHTS model has Feel No Pain 6+ (+ regains 1 wound/turn, not modelled)
    "Freeblade Company": lambda a: _grant(a, _ALL, fnp=6),
    # Rain of Devastation: DOMINUS-class +1 to hit vs units in terrain — re-roll-1 stand-in on the big Knights
    "Dominus Foebreakers": lambda a: _grant(a, _kw("TITANIC", "DOMINUS"), abil={"reroll_hits": "ones"}),
}
# --- Adepta Sororitas --- (NB: Hallowed Martyrs / Bringers of Flame run on MIRACLE DICE / Acts of Faith, which
# the sim does not model → intentionally NOT here; they stay on the data-driven read. Only the flat one maps.)
ADEPTA_SORORITAS = {
    # Holy Quest: CELESTIAN SACRESANTS get +1 BS & WS — re-roll-1 stand-in on that (narrow) unit
    "Champions of Faith": lambda a: _grant(a, _kw("SACRESANT"), abil={"reroll_hits": "ones"}),
}

TABLES = {"adeptus-custodes": CUSTODES, "space-marines": SPACE_MARINES,
          "imperial-knights": IMPERIAL_KNIGHTS, "adepta-sororitas": ADEPTA_SORORITAS}
DP.update({k: 1 for tbl in (SPACE_MARINES, IMPERIAL_KNIGHTS, ADEPTA_SORORITAS) for k in tbl})
