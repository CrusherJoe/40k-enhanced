"""CP economy + a stratagem layer driven by the REAL detachment stratagems (data/strats via db.strats)
plus the universal 11e core. Each army builds its available pool (core + its detachment's strats), every
strat is CLASSIFIED from its DB effect text into a modelled combat effect, and a CP-spend policy fires the
best affordable one at the right trigger. Both armies gain 1 CP/round (game._command).

Modelled effect types (the mechanically-representable majority): defensive -1-to-be-hit (Go to Ground /
Unwavering Sentinels), Feel-No-Pain vs mortals or all (Arcane Genetic Alchemy), offensive re-roll /
Lethal-Sustained (Archeotech Munitions / battle tactics), +1 Attacks (Avenge the Fallen ~ more output),
and Counter-Offensive (fight first). Plus once-per-game unit abilities (Custodian Wardens' 4+++). Strats
whose effect is positional/mission (Vigilance Eternal sticky objective, Multipotentiality fall-back-shoot,
Rapid Ingress) are in the pool but flagged UNMODELLED — logged, not applied. This models the CP BUDGET's
swing on key trades, not every rule of all 1028 strats. Toggle with ENABLED.

Coverage note: the ME army gets core + its full detachment (the list under analysis); opponents get the
core set (symmetric economy). Opponent detachment strats are a documented follow-up (needs each opponent
roster's slug+detachment wired for the db lookup)."""
from __future__ import annotations

import re, collections

ENABLED = True

# Universal 11e core stratagems (available to every army), with modelled effects.
CORE = [
    dict(name="Go to Ground", cp=1, role="def", phase="shoot", hit=-1, req="INFANTRY"),
    dict(name="Smokescreen", cp=1, role="def", phase="shoot", hit=-1),
    dict(name="Counter-Offensive", cp=2, role="def", phase="fight", fight_first=True),
    dict(name="Command Re-roll", cp=1, role="def", phase="shoot", fnp=None, save_help=True),
    dict(name="Grenade", cp=1, role="off", phase="shoot", unmodelled=True),
    dict(name="Rapid Ingress", cp=1, role="util", phase="move", unmodelled=True),
    dict(name="Heroic Intervention", cp=1, role="util", phase="charge", unmodelled=True),
    dict(name="Fire Overwatch", cp=1, role="def", phase="charge", unmodelled=True),
    dict(name="Insane Bravery", cp=1, role="util", phase="command", unmodelled=True),
    dict(name="Tank Shock", cp=1, role="off", phase="charge", unmodelled=True),
]


def _classify(name, s):
    """Map a DB stratagem (dict with cp/effect/when) to a modelled combat effect, or mark it unmodelled."""
    e = " ".join(str(s.get("effect", "")).split()).lower()
    when = str(s.get("when", "")).lower()
    cp = s.get("cp", 1)
    base = dict(name=name, cp=cp)
    if "feel no pain" in e:
        m = re.search(r"feel no pain (\d)\+", e)
        return dict(base, role="def", phase="any", fnp=f"{m.group(1)}+" if m else "5+",
                    vs="mortal" if "mortal" in e else "all")
    if "subtract 1 from the hit roll" in e or "worsen the hit roll" in e or "-1 to be hit" in e:
        phase = "fight" if ("melee" in e or "fight" in when) else "shoot" if "ranged" in e else "any"
        return dict(base, role="def", phase=phase, hit=-1)
    if "add 1 to the attacks" in e:
        return dict(base, role="off", phase="fight", attacks=1)
    if "[lethal hits]" in e or "lethal hits" in e or "[sustained hits" in e or "sustained hits" in e:
        return dict(base, role="off", phase="shoot", reroll_wounds="ones")
    if "re-roll" in e and "wound" in e:
        return dict(base, role="off", phase="any", reroll_wounds="ones")
    if "re-roll" in e and "hit" in e:
        return dict(base, role="off", phase="any", reroll_hits="ones")
    if "add 1 to the wound roll" in e:
        return dict(base, role="off", phase="any", wound=1)
    return dict(base, role="util", phase="any", unmodelled=True)   # positional/mission/action strats


def build_pool(slug=None, detachments=None):
    """core + EVERY chosen detachment's classified stratagems (from the DB). 11e armies can run multiple
    detachments (e.g. Better Thing 2 = Shield Host + Tharanatoi Hammerblow) and get ALL their strats."""
    pool = [dict(c) for c in CORE]
    seen = {c["name"] for c in CORE}
    for det in (detachments or []):
        try:
            import db
            for nm, s in db.strats(slug).get(det, {}).items():
                if nm not in seen:
                    pool.append(_classify(nm, s)); seen.add(nm)
        except Exception:
            pass
    return pool


def equip(army, slug=None, detachments=None):
    """Attach a stratagem pool + CP economy to an army. Snapshots each unit's base FNP so temporary
    defensive FNP grants can be cleanly reset each turn. Idempotent. `detachments` is a list of names."""
    if getattr(army, "_strat", None) is not None:
        return
    if isinstance(detachments, str):
        detachments = [detachments]
    army._strat = dict(pool=build_pool(slug, detachments), used=collections.Counter(), turn_spent=0, spent=0)
    army.cp = 0
    for u in army.units:
        u._fnp_base = u.fnp


def turn_start(army):
    """Start of this army's turn: reset its per-turn spend budget and clear temporary defensive buffs
    (FNP grants / Wardens 4+++) that were active during the opponent's turn."""
    st = getattr(army, "_strat", None)
    if st is None:
        return
    st["turn_spent"] = 0
    for u in army.units:
        u.fnp = getattr(u, "_fnp_base", u.fnp)


def _afford(army, e, cap=3):
    st = army._strat
    return (not e.get("unmodelled") and army.cp >= e["cp"] and st["turn_spent"] < cap)


def _spend(army, e):
    army.cp -= e["cp"]
    army._strat["turn_spent"] += 1
    army._strat["spent"] += e["cp"]
    army._strat["used"][e["name"]] += 1


def _significant(attacker, target):
    """Is this attack worth a stratagem? Roughly: a meaningful chunk of a valuable unit is at stake."""
    from .game import _expected_vs
    dmg = _expected_vs(attacker, target, melee=False) + _expected_vs(attacker, target, melee=True)
    frac = dmg / max(1.0, target.total_w)
    return target.threat >= 1.6 and frac >= 0.25


def _ensure(army):
    if getattr(army, "_strat", None) is None:
        equip(army, getattr(army, "slug", None), getattr(army, "strat_dets", None))


def on_attack(atk_army, def_army, attacker, target, mods, phase):
    """Both sides consider spending CP on this attack. Defender first (survival), then attacker (finish).
    Mutates `mods` (hit/reroll) and may grant the target a temporary FNP. Returns names fired (for logs)."""
    if not ENABLED:
        return
    _ensure(atk_army); _ensure(def_army)
    # derive owners from unit sides (robust to caller order): defender owns the target, attacker the attacker
    defender = atk_army if atk_army.side == target.side else def_army
    attacker_army = atk_army if atk_army.side == attacker.side else def_army
    # -- once-per-game unit abilities (free) --
    if target.abilities.get("once_fnp") and not getattr(target, "_once_fnp_used", False) \
            and _significant(attacker, target):
        target.fnp = target.abilities["once_fnp"]
        target._once_fnp_used = True
        defender._strat["used"]["Wardens 4+++ (once/game)"] += 1
    # -- DEFENSIVE: the target's army spends to blunt a big incoming hit --
    if _significant(attacker, target):
        for e in sorted(defender._strat["pool"], key=lambda x: -x.get("cp", 0)):
            if e["role"] != "def" or e["phase"] not in (phase, "any"):
                continue
            if e.get("req") == "INFANTRY" and "INFANTRY" not in target.keywords:
                continue
            if not _afford(defender, e):
                continue
            if e.get("hit"):
                mods.hit += e["hit"]                     # attacker -1 to hit
            elif e.get("fnp") and (e.get("vs") != "mortal" or "DEVASTATING WOUNDS" in _kw(attacker)):
                if not target.fnp:
                    target.fnp = e["fnp"]
            elif e.get("save_help"):
                mods.hit -= 1                            # Command Re-roll a failed save ~ a light incoming-hit reduction
            else:
                continue
            _spend(defender, e)
            break
    # -- OFFENSIVE: the attacker's army spends to secure a kill on a high-value target --
    if target.threat >= 2.4:
        for e in sorted(attacker_army._strat["pool"], key=lambda x: x.get("cp", 0)):
            if e["role"] != "off" or e["phase"] not in (phase, "any"):
                continue
            if not _afford(attacker_army, e):
                continue
            if e.get("reroll_wounds") and not mods.reroll_wounds:
                mods.reroll_wounds = e["reroll_wounds"]
            elif e.get("reroll_hits") and not mods.reroll_hits:
                mods.reroll_hits = e["reroll_hits"]
            elif e.get("wound"):
                mods.wound += e["wound"]
            elif e.get("attacks") and not mods.reroll_hits:
                mods.reroll_hits = "ones"                # +1 Attacks modelled softly as more output (re-roll 1s)
            else:
                continue
            _spend(attacker_army, e)
            break


def _kw(u):
    out = []
    for w in u.ranged + u.melee:
        out += [a.upper() for a in w.get("abilities", [])]
    return out


def wants_counter_offensive(def_army, chargers, board):
    """Fight phase: the defender may spend 2CP so one of its engaged units fights FIRST vs a scary charge.
    Returns the unit to prioritise (and spends the CP), or None."""
    if not ENABLED or getattr(def_army, "_strat", None) is None:
        return None
    co = next((e for e in def_army._strat["pool"] if e.get("fight_first")), None)
    if not co or not _afford(def_army, co, cap=2):
        return None
    from .entities import dist
    threat = any(c.charged and c.threat >= 2.0 for c in chargers)
    if not threat:
        return None
    engaged = [u for u in def_army.on_board() if u.melee and u.alive
               and any(dist(u.pos, c.pos) <= 3.0 + c.radius for c in chargers)]
    if not engaged:
        return None
    _spend(def_army, co)
    return max(engaged, key=lambda u: u.threat)
