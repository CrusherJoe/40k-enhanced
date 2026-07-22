"""Expected-damage mathhammer for 40k 11e weapon profiles.

Given a weapon profile (from data/profiles) and a target, compute expected
damage using an EV model that handles the common weapon abilities:
BLAST, RAPID FIRE X, TORRENT, SUSTAINED HITS X, LETHAL HITS, TWIN-LINKED,
DEVASTATING WOUNDS, ANTI-<kw> N+, MELTA X, LANCE, HEAVY, plus hit/wound
modifiers and re-rolls passed via `Mods`. Rules verified against the 11e core
rules PDF (see docs/core-rules-reference.md); notably cover is a -1 to HIT
(11e 13.08), not a save bonus, and Devastating Wounds crit-wounds become mortal
wounds equal to Damage (24.10).

This is an EV approximation (not a full distribution) and deliberately ignores
per-model wound spillover and some rare interactions; it is meant for comparing
weapons and units, which is what "best list" analysis needs.
"""

from __future__ import annotations

import re
from dataclasses import dataclass, field

from . import dice


@dataclass
class Target:
    toughness: int
    save: str            # e.g. "3+"
    wounds: int = 10
    invuln: str | None = None    # e.g. "4+"
    models: int = 1
    keywords: tuple = ()         # e.g. ("VEHICLE", "TITANIC")
    in_cover: bool = False
    fnp: str | None = None       # e.g. "5+"
    half_range: bool = False     # target within half range (melta / rapid fire)


@dataclass
class Mods:
    hit: int = 0                 # +1/-1 to hit
    wound: int = 0               # +1/-1 to wound
    reroll_hits: str = "none"    # none | ones | fails
    reroll_wounds: str = "none"
    ap_bonus: int = 0            # improve AP by N (more negative)
    charged: bool = False        # for LANCE
    stationary: bool = False     # for HEAVY
    reroll_attacks: bool = False # re-roll the Attacks dice (e.g. Archeotech Autoloaders)
    crit_hit: int = 6            # unmodified hit crits on this+
    crit_wound: int = 6


def _kw(weapon) -> dict:
    """Parse a weapon's ability list into {KEYWORD: arg}.

    A trailing token is treated as the argument only if it contains a digit
    (e.g. 'RAPID FIRE 3', 'ANTI-TITANIC 4+', 'SUSTAINED HITS D3'); otherwise the
    whole phrase is the keyword ('DEVASTATING WOUNDS', 'LETHAL HITS').
    """
    out = {}
    for a in weapon.get("abilities", []):
        s = re.sub(r"\s+", " ", str(a).strip().upper())
        head, _, tail = s.rpartition(" ")
        if head and re.search(r"\d", tail):
            out[head] = int(tail.rstrip("+")) if re.fullmatch(r"\d+\+?", tail) else tail
        else:
            out[s] = True
    return out


def _arg(v) -> float:
    """A keyword argument as a number (handles ints and dice like 'D3')."""
    return dice.expected(v) if not isinstance(v, bool) else 0.0


def expected_damage(weapon: dict, target: Target, mods: Mods | None = None) -> float:
    mods = mods or Mods()
    kw = _kw(weapon)
    melee = "WS" in weapon

    # --- attacks ---
    attacks = dice.expected_reroll(weapon["A"]) if mods.reroll_attacks else dice.expected(weapon["A"])
    if "BLAST" in kw and target.models > 1:
        attacks += target.models // 5
    if "RAPID FIRE" in kw and target.half_range and not melee:
        attacks += _arg(kw["RAPID FIRE"])

    # --- hit ---
    torrent = "TORRENT" in kw
    skill = dice.target_number(weapon.get("WS") or weapon.get("BS"))
    # 11e cover (13.08): benefit of cover worsens the attack's BS CHARACTERISTIC
    # by 1 -- numerically a -1 to hit, which is what we model here. Ranged only,
    # cancelled by [IGNORES COVER], irrelevant to melee/auto-hitting TORRENT.
    # NOTE: cover is a CHARACTERISTIC modifier, distinct from a Hit-ROLL modifier
    # -- so "ignore Hit-roll modifiers" effects (e.g. Gate Warden) do NOT remove
    # it, and it sits outside the +/-1 Hit-roll cap. This EV model lumps cover
    # into the hit modifier, which is exact for the common cases (cover alone, or
    # cover + a +1 Hit-roll bonus like Dominus); it can mis-handle the rare stack
    # of cover PLUS multiple Hit-roll debuffs (the roll cap wouldn't apply to cover).
    cover_hit = -1 if (target.in_cover and not melee and not torrent
                       and "IGNORES COVER" not in kw) else 0
    hit_mod = mods.hit + cover_hit + (1 if ("HEAVY" in kw and mods.stationary and not melee) else 0)
    crit_hit_rate = (7 - mods.crit_hit) / 6.0
    if torrent:
        p_hit, crit_hits = 1.0, 0.0
    else:
        p_hit = dice.with_reroll(dice.p_roll(skill, hit_mod), mods.reroll_hits)
        crit_hits = attacks * crit_hit_rate
    hits = attacks * p_hit

    if "SUSTAINED HITS" in kw and not torrent:
        hits += crit_hits * _arg(kw["SUSTAINED HITS"])

    # --- wound ---
    S = int(weapon["S"])
    D_expr = weapon["D"]
    if "MELTA" in kw and target.half_range:
        pass  # handled in damage step
    # anti-<kw> lowers the crit-wound threshold vs a matching target
    crit_wound_need = mods.crit_wound
    for k, v in kw.items():
        if k.startswith("ANTI-"):
            tkw = k[5:].replace(" ", "").upper()
            if any(tkw == t.replace(" ", "").upper() for t in target.keywords) and isinstance(v, int):
                crit_wound_need = min(crit_wound_need, v)
    crit_wound_rate = (7 - crit_wound_need) / 6.0

    need_w = dice.wound_needed(S, target.toughness)
    wmod = mods.wound + (1 if ("LANCE" in kw and mods.charged) else 0)
    p_wound = dice.p_roll(need_w, wmod)
    p_wound = max(p_wound, crit_wound_rate)  # a crit always wounds
    p_wound = dice.with_reroll(p_wound, "fails" if "TWIN-LINKED" in kw else mods.reroll_wounds)

    lethal = "LETHAL HITS" in kw
    auto_wounds = crit_hits if lethal else 0.0
    rolling_hits = hits - (crit_hits if lethal else 0.0)
    wounds_from_roll = rolling_hits * p_wound
    total_wounds = wounds_from_roll + auto_wounds
    crit_wounds = rolling_hits * crit_wound_rate

    # --- damage per wound ---
    dmg = dice.expected(D_expr)
    if "MELTA" in kw and target.half_range:
        dmg += _arg(kw["MELTA"])

    # --- saves ---  (cover does NOT affect saves in 11e; see cover_hit above)
    ap = int(weapon["AP"]) - mods.ap_bonus         # ap is <=0; ap_bonus makes it more negative
    armour_need = dice.target_number(target.save) - ap  # -ap because ap is negative
    inv_need = dice.target_number(target.invuln) if target.invuln else 99
    save_need = min(armour_need, inv_need)
    p_fail = 1.0 if save_need > 6 else 1 - (7 - max(2, save_need)) / 6.0

    dev = "DEVASTATING WOUNDS" in kw
    if dev:
        mortal_wounds = crit_wounds * dmg           # crit wounds bypass saves
        savable = total_wounds - crit_wounds
    else:
        mortal_wounds = 0.0
        savable = total_wounds
    unsaved = savable * p_fail

    fnp_ignore = dice.p_roll(dice.target_number(target.fnp)) if target.fnp else 0.0
    damage = (unsaved * dmg + mortal_wounds) * (1 - fnp_ignore)
    return damage


def profile_damage(profile: dict, weapon_name: str, target: Target,
                   mods: Mods | None = None) -> float:
    """Look up a weapon by (partial) name on a datasheet profile and resolve it."""
    q = weapon_name.strip().lower()
    for grp in ("ranged", "melee"):
        for w in profile.get(grp, []):
            if q in w["name"].lower():
                return expected_damage(w, target, mods)
    raise KeyError(f"{weapon_name!r} not found on {profile['name']}")
