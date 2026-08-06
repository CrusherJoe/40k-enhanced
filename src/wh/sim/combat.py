"""Dice-resolved combat for the 40k simulator — the real thing, not EV.

resolve_attacks() rolls actual d6 (numpy-vectorized) for a weapon fired/swung by N models into a
target unit, honoring the 11e keyword set (BLAST, RAPID FIRE, TORRENT, SUSTAINED/LETHAL HITS,
DEVASTATING WOUNDS, ANTI-x, MELTA, LANCE, HEAVY, TWIN-LINKED) + hit/wound/AP mods and re-rolls, and
returns the damage instances to allocate. apply_damage() allocates with correct 11e rules: regular
damage does NOT spill between models (overkill wasted); mortal wounds DO spill; Feel No Pain is rolled
per lost wound. The mean of resolve_attacks matches wh.mathhammer.expected_damage (see test_combat).
"""
from __future__ import annotations

import re
import numpy as np

from ..dice import target_number, wound_needed
from ..mathhammer import _kw


def roll_expr(expr, rng, n):
    """Roll a dice expression ('D6+8', 'D3', '2D6', '3') n times -> int array of length n."""
    s = str(expr).upper().replace(" ", "")
    m = re.fullmatch(r"(\d*)D(\d+)([+-]\d+)?", s)
    if m:
        k = int(m.group(1) or 1)
        faces = int(m.group(2))
        flat = int(m.group(3) or 0)
        return rng.integers(1, faces + 1, size=(n, k)).sum(1) + flat
    return np.full(n, int(float(s)), dtype=int)


def _reroll(mask_success, rolls, rng, mode):
    """Re-roll dice where not successful (mode 'fails') or ==1 (mode 'ones'); return new rolls."""
    if mode == "none":
        return rolls
    redo = (rolls == 1) if mode == "ones" else ~mask_success
    if redo.any():
        rolls = rolls.copy()
        rolls[redo] = rng.integers(1, 7, size=int(redo.sum()))
    return rolls


def resolve_attacks(weapon, n_models, target, mods, rng, half_range=False, charged=False):
    """Return (damage_instances int-array, mortal_wounds int) from N models using `weapon` vs target.
    target is a light struct with .toughness .save .invuln .keywords .fnp .damage_reduction."""
    kw = _kw(weapon)
    melee = "WS" in weapon
    # --- attacks ---
    a = roll_expr(weapon["A"], rng, n_models)
    if getattr(mods, "reroll_attacks", False):
        a = np.maximum(a, roll_expr(weapon["A"], rng, n_models))
    N = int(a.sum())
    if "BLAST" in kw and target.models > 1:
        N += (target.models // 5) * n_models
    if "RAPID FIRE" in kw and half_range and not melee:
        rf = kw["RAPID FIRE"]; N += int(rf if isinstance(rf, int) else 0) * n_models
    if N <= 0:
        return np.zeros(0, dtype=int), 0

    # --- hits ---
    torrent = "TORRENT" in kw
    skill = target_number(weapon.get("WS") or weapon.get("BS"))
    in_cov = target.in_cover or target.abilities.get("stealth")     # Stealth (24.33) = benefit of cover
    cover = -1 if (in_cov and not melee and not torrent and "IGNORES COVER" not in kw) else 0
    hmod = mods.hit + cover + (1 if ("HEAVY" in kw and getattr(mods, "stationary", False) and not melee) else 0)
    if torrent:
        hit = np.ones(N, dtype=bool); crit_h = np.zeros(N, dtype=bool)
    else:
        r = rng.integers(1, 7, N)
        succ = (r != 1) & ((r + hmod >= skill) | (r >= mods.crit_hit))
        r = _reroll(succ, r, rng, mods.reroll_hits)
        crit_h = r >= mods.crit_hit
        hit = (r != 1) & ((r + hmod >= skill) | crit_h)
    n_hit = int(hit.sum()); n_crit_h = int(crit_h[hit].sum()) if not torrent else 0

    # sustained hits add extra (non-crit) hits
    extra = 0
    if "SUSTAINED HITS" in kw and not torrent:
        sh = kw["SUSTAINED HITS"]
        per = int(sh) if isinstance(sh, int) else int(round(roll_expr(sh, rng, max(1, n_crit_h)).mean())) if n_crit_h else 0
        extra = n_crit_h * per
    total_hits = n_hit + extra

    # --- wounds ---
    lethal = "LETHAL HITS" in kw
    auto_w = n_crit_h if lethal else 0
    rolling = total_hits - (n_crit_h if lethal else 0)
    need = wound_needed(int(weapon["S"]) + getattr(mods, "str_bonus", 0), target.toughness)
    wmod = mods.wound + (1 if ("LANCE" in kw and charged) else 0)
    crit_w_need = mods.crit_wound
    for k, v in kw.items():
        if k.startswith("ANTI-") and isinstance(v, int):
            tk = k[5:].replace(" ", "").upper()
            if any(tk == t.replace(" ", "").upper() for t in target.keywords):
                crit_w_need = min(crit_w_need, v)
    if rolling > 0:
        wr = rng.integers(1, 7, rolling)
        wsucc = (wr != 1) & ((wr + wmod >= need) | (wr >= crit_w_need))
        twin = "TWIN-LINKED" in kw
        wr = _reroll(wsucc, wr, rng, "fails" if twin else mods.reroll_wounds)
        crit_w = wr >= crit_w_need
        wounded = (wr != 1) & ((wr + wmod >= need) | crit_w)
        n_crit_w = int(crit_w[wounded].sum()); n_wound = int(wounded.sum())
    else:
        n_crit_w = n_wound = 0
    n_wound += auto_w                                  # lethal auto-wounds (never crit)

    # --- damage char per wound ---
    melta = int(kw["MELTA"]) if ("MELTA" in kw and half_range and isinstance(kw.get("MELTA"), int)) else 0

    def dmg_for(count):
        if count <= 0:
            return np.zeros(0, dtype=int)
        d = roll_expr(weapon["D"], rng, count) + melta
        if target.damage_reduction:
            d = np.maximum(1, d - target.damage_reduction)
        return d

    # --- saves (dev-wounds crit-wounds become mortals, bypass saves) ---
    dev = "DEVASTATING WOUNDS" in kw
    mortals = 0
    if dev and n_crit_w > 0:
        mortals = int(dmg_for(n_crit_w).sum())
        savable = n_wound - n_crit_w
    else:
        savable = n_wound
    ap = int(weapon["AP"]) - mods.ap_bonus
    save_need = min(target_number(target.save) - ap, target_number(target.invuln) if target.invuln else 99)
    if savable > 0 and save_need <= 6:
        sr = rng.integers(1, 7, savable)
        failed = int(((sr == 1) | (sr < save_need)).sum())          # nat 1 always fails; else need save_need+
    else:
        failed = savable if savable > 0 else 0
    inst = dmg_for(failed)
    # SHOOT-WARD: durable-elite bodies shrug a fraction of PREMIUM (high-AP) anti-elite SHOOTING that the
    # point model over-lands — the aggregate of positioning / character-protection / spread / cover on the
    # key models that keeps real Custodes competitive vs quality guns. Deliberately NOT applied to low-AP
    # dakka (they tank that with their 2+ anyway), so the grindy anchors (Orks/Necrons) are untouched.
    ward = None if melee else target.abilities.get("shoot_ward")
    if ward and ap <= -3 and len(inst) > 0:            # AP-3/-4 only (fusion/rail/wraithcannon/plasma/ion),
        #                                                not AP-2 dakka/rokkits -> spares the Orks/Necrons anchors
        need = target_number(ward)
        inst = inst[rng.integers(1, 7, len(inst)) < need]      # roll >= need -> wound ignored
    return inst, mortals


def apply_damage(unit, instances, mortals, rng):
    """Allocate damage to a unit (correct 11e): regular damage does NOT spill (overkill wasted);
    mortals DO spill; FNP rolled per lost wound. Mutates unit.models / unit.cur_w. Returns wounds lost."""
    lost = 0
    fnp = target_number(unit.fnp) if unit.fnp else 99
    # SHADOWFIELD: a 2++ that cannot be re-rolled and is DESTROYED the instant a save is failed. Any
    # failed-save damage instance here means the 2++ was failed -> drop it (revert to armour) permanently.
    if unit.abilities.get("shadowfield") and len(instances) > 0:
        unit.invuln = None
        unit.abilities = dict(unit.abilities, shadowfield=False)
    for d in instances:
        if unit.models <= 0:
            break
        if fnp <= 6 and d > 0:
            d = int((rng.integers(1, 7, int(d)) < fnp).sum())      # FNP saves some
        if d <= 0:
            continue
        taken = min(d, unit.cur_w)                                  # no spill: cap at current model
        unit.cur_w -= taken; lost += taken
        if unit.cur_w <= 0:
            unit.models -= 1
            unit.cur_w = unit.wounds if unit.models > 0 else 0
    # mortals spill across models
    m = mortals
    while m > 0 and unit.models > 0:
        if fnp <= 6:
            m = int((rng.integers(1, 7, m) < fnp).sum())
            if m <= 0:
                break
        take = min(m, unit.cur_w); unit.cur_w -= take; lost += take; m -= take
        if unit.cur_w <= 0:
            unit.models -= 1; unit.cur_w = unit.wounds if unit.models > 0 else 0
    return lost
