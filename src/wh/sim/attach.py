"""LEADER / attached-CHARACTER modelling (11E) — the tapestry transfer that keeps buff characters alive.

In 11E a CHARACTER with the Leader ability attaches to a Bodyguard unit. Two things matter and neither was
modelled (characters were standalone blobs that died the instant they were reachable, so army-wide
multipliers evaporated turn 1 — a proven cause of the sim's fragility swings, see __init__ STATUS):

  1. TWO-WAY TAPESTRY: the Leader confers its combat abilities to the whole unit (crit-on-5, re-rolls,
     +S/+A on the charge, Feel No Pain, a better invuln...). The unit is only as good as its attached
     character makes it — that IS the tapestry.
  2. PROTECTION: while attached, the Character CANNOT be targeted — attacks hit the Bodyguard unit; the
     Character is removed only once the unit is destroyed (it then detaches and fights on alone). There is
     NO "Look Out, Sir" in 11E; the protection is the Leader rule itself. The one exception is PRECISION,
     which lets an attacker allocate wounds to the attached Character directly.

This module attaches leaders to bodyguards heuristically (works for curated rosters AND listloader-built
lists), merges the tapestry into the bodyguard, and detaches a leader when its host dies. Targeting/PRECISION
are handled in game.py (embedded leaders are excluded from on_board(); PRECISION shooters may pick them)."""
from __future__ import annotations

import math

from ..dice import target_number

_RR = {None: 0, "": 0, "none": 0, "ones": 1, "fails": 2}
_RR_INV = {0: None, 1: "ones", 2: "fails"}
_BODY_ROLES = ("line", "anti_horde", "screen", "action")


def _better_reroll(a, b):
    return _RR_INV[max(_RR.get(a, 0), _RR.get(b, 0))]


def _better_save(a, b):
    """Return the better (lower target-number) of two save strings like '4+' / None."""
    if not a:
        return b
    if not b:
        return a
    return a if target_number(a) <= target_number(b) else b


def _merge_one(body, leader):
    """Fold ONE leader's combat tapestry into the bodyguard (best-of), the way an attached character buffs
    its squad. Non-combat/one-off keys are copied only if the unit lacks them."""
    out = dict(body.abilities)
    for k, v in leader.abilities.items():
        if k == "crit_hit":
            out[k] = min(v, out.get(k, 7))                 # crit-on-5 beats crit-on-6
        elif k in ("reroll_hits", "reroll_wounds"):
            out[k] = _better_reroll(out.get(k), v)
        elif k in ("str_charge", "wound_charge", "ap_bonus"):
            out[k] = max(v, out.get(k, 0))
        elif k == "reroll_charge":
            out[k] = out.get(k) or v
        else:
            out.setdefault(k, v)                           # e.g. shoot_ward, fnp buffs carried as abilities
    body.abilities = out
    body.fnp = _better_save(body.fnp, leader.fnp)          # a leader can confer/upgrade a FNP or invuln
    if leader.invuln:
        body.invuln = _better_save(body.invuln, leader.invuln)


def recompute(body):
    """Rebuild the bodyguard's tapestry from its BASE (un-led) stats + whichever leaders are still alive
    and attached. Called when a leader is sniped off (PRECISION) or detaches, so a dead character's buff
    correctly disappears — merge-at-attach can't be un-done without this base snapshot."""
    body.abilities = dict(body._base_ab)
    body.fnp = body._base_fnp
    body.invuln = body._base_invuln
    for ldr in body.leading:
        if ldr.alive and getattr(ldr, "embedded", False):
            _merge_one(body, ldr)


def _can_lead(u):
    return u.role == "character" and not u.tall and u.models == 1


def _is_body(u):
    return (u.role in _BODY_ROLES and u.role != "character" and not u.tall
            and u.models >= 1 and u.transport is None and not getattr(u, "embedded", False))


def _add_ability(weapon, kw):
    ab = list(weapon.get("abilities", []))
    if kw not in ab:
        ab.append(kw)
    weapon["abilities"] = ab


def apply_enh_wfx(unit, wfx):
    """Apply an enhancement's WEAPON/keyword effects to a unit (the bearer's squad): inject weapon
    keywords (Lethal/Sustained/Dev/Precision), improve melee AP, add unit keywords/abilities. Enhancements
    read 'the bearer AND Battleline models in the bearer's unit', so they buff the whole squad's guns."""
    if not wfx:
        return
    for w in unit.ranged:
        for kw in wfx.get("ranged_kw", []):
            _add_ability(w, kw)
    for w in unit.melee:
        for kw in wfx.get("melee_kw", []):
            _add_ability(w, kw)
        if wfx.get("melee_ap"):
            w["AP"] = int(w.get("AP", 0)) - wfx["melee_ap"]     # 'improve AP by 1' => more negative
    for k, v in wfx.get("unit_ability", {}).items():
        unit.abilities[k] = v
    if wfx.get("unit_kw"):
        unit.keywords = tuple(unit.keywords) + tuple(k for k in wfx["unit_kw"] if k not in unit.keywords)


def _embed(leader, body):
    if not hasattr(body, "_base_ab"):                      # snapshot un-led stats so recompute() can undo
        body._base_ab = dict(body.abilities); body._base_fnp = body.fnp; body._base_invuln = body.invuln
    leader.embedded = True
    leader.host = body
    body.leading = list(getattr(body, "leading", [])) + [leader]
    _merge_one(body, leader)
    from . import tapestry as _tap
    _tap.apply_fx(body, getattr(leader, "_aura", None))     # LEADER AURA (Feirros FNP5+, Biologis Lethal...)
    apply_enh_wfx(body, getattr(leader, "_enh_wfx", None))  # the leader's enhancement buffs its new squad
    leader._wfx_done = True


def attach_all(army):
    """Embed each attached CHARACTER into its Bodyguard unit and merge the tapestry. If the list carries the
    AUTHORITATIVE structure (listloader tagged each unit with `_grp`/`_arole` from the export's 'Attached
    unit N' + 'Attached as: Leader/Support/Bodyguard'), use it exactly. Otherwise (curated rosters, old
    exports) fall back to a greedy heuristic (beefiest available bodyguard, matched reserve status)."""
    # 1) authoritative: group by the export's 'Attached unit N', Leaders/Supports -> the Bodyguard
    groups = {}
    for u in army.units:
        g = getattr(u, "_grp", None)
        r = getattr(u, "_arole", None)
        if g is None or not r:
            continue
        groups.setdefault(g, {"body": None, "chars": []})
        if r == "bodyguard":
            groups[g]["body"] = u
        else:                                              # leader | support
            groups[g]["chars"].append(u)
    if groups:
        for g in groups.values():
            body = g["body"]
            if body is None:
                continue
            for ldr in g["chars"]:
                _embed(ldr, body)
        _apply_standalone_enh(army)
        return

    # 2) heuristic fallback (no export annotations)
    leaders = [u for u in army.units if _can_lead(u)]
    bodies = [u for u in army.units if _is_body(u)]
    used = set()
    for ldr in leaders:
        cand = [b for b in bodies if id(b) not in used and b.in_reserve == ldr.in_reserve]
        if not cand:
            continue
        b = max(cand, key=lambda b: (b.oc * b.models, b.total_w))   # beefiest available bodyguard
        used.add(id(b))
        _embed(ldr, b)
    _apply_standalone_enh(army)


def _apply_standalone_enh(army):
    """An enhancement on a character that ended up UN-attached still buffs that character itself."""
    for u in army.units:
        if getattr(u, "_enh_wfx", None) and not getattr(u, "_wfx_done", False):
            apply_enh_wfx(u, u._enh_wfx)
            u._wfx_done = True


def detach_dead(armies):
    """When a bodyguard dies, its attached leader(s) detach and fight on alone (become targetable). Called
    after each combat resolution. The buff they gave the (now dead) unit is naturally gone; the leader
    keeps its own abilities as a standalone unit."""
    for army in armies:
        for u in army.units:
            leading = getattr(u, "leading", None)
            if leading and not u.alive:
                for ldr in leading:
                    ldr.embedded = False
                    ldr.host = None
                    ldr.pos = u.pos                         # it appears where its unit fell
                u.leading = []


def embedded_leaders(unit):
    """Attached, still-alive leaders of a unit (the PRECISION-only targets)."""
    return [l for l in getattr(unit, "leading", []) if l.alive and getattr(l, "embedded", False)]


def on_leader_killed(leader):
    """A PRECISION attacker sniped this embedded leader: detach it and rebuild its host's tapestry so the
    buff it was providing is lost."""
    host = leader.host
    leader.embedded = False
    leader.host = None
    if host is not None and leader in getattr(host, "leading", []):
        host.leading.remove(leader)
        if host.alive:
            recompute(host)
