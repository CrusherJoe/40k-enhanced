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


def attach_all(army):
    """Pair each attachable CHARACTER with a suitable Bodyguard unit (greedy, one leader per unit) and
    merge the tapestry. Leaders with no available bodyguard stay standalone. Matches reserve status so a
    deep-striking character doesn't get glued to an on-board squad."""
    leaders = [u for u in army.units if _can_lead(u)]
    bodies = [u for u in army.units if _is_body(u)]
    used = set()
    for ldr in leaders:
        cand = [b for b in bodies if id(b) not in used and b.in_reserve == ldr.in_reserve]
        if not cand:
            continue
        # prefer the beefiest real bodyguard (most board-presence: OC x models, then raw wounds)
        b = max(cand, key=lambda b: (b.oc * b.models, b.total_w))
        used.add(id(b))
        if not hasattr(b, "_base_ab"):                     # snapshot un-led stats so recompute() can undo
            b._base_ab = dict(b.abilities); b._base_fnp = b.fnp; b._base_invuln = b.invuln
        ldr.embedded = True
        ldr.host = b
        b.leading = list(getattr(b, "leading", [])) + [ldr]
        _merge_one(b, ldr)


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
