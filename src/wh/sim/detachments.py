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
