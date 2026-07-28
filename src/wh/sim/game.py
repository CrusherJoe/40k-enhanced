"""The turn-by-turn game loop: deployment -> 5 battle rounds (command / move / shoot / charge / fight)
-> real objective OC scoring + real primary-mission VP + a state-driven secondary. Tactics are greedy
heuristics (move to contest objectives / into range, focus-fire the best target, charge when reachable).
Combat is dice-resolved (wh.sim.combat). Missions come from data/missions.yaml via wh.sim.mission."""
from __future__ import annotations

import numpy as np

from .entities import Board, dist, HOME_Y, DEPLOY_LINE, BOARD_H
from .combat import resolve_attacks, apply_damage
from .mission import score_turn, end_of_battle
from ..mathhammer import Mods
from .. import sim


def _mods_for(unit, target, charged=False):
    """Assemble the Mods for this unit vs this target from its abilities/army rules (the tapestry)."""
    m = Mods(charged=charged)
    ab = unit.abilities
    if ab.get("crit_hit"):
        m.crit_hit = ab["crit_hit"]                       # e.g. Martial Mastery crit-on-5
    if ab.get("reroll_hits"):
        m.reroll_hits = ab["reroll_hits"]
    if ab.get("reroll_wounds"):
        m.reroll_wounds = ab["reroll_wounds"]
    if ab.get("lance_charge") and charged:
        pass
    return m


def _best_weapon_set(unit, target, melee):
    """Pick the weapon profile(s) to use vs a target. Handles multi-profile weapons (e.g. Blade
    Champion's 3 Vaultswords) by choosing the profile with the best expected removal on this target."""
    pool = unit.melee if melee else unit.ranged
    # group weapons by 'slot' (models carry one of a set of profiles). Simplest: for each distinct
    # 'slot', pick its best profile vs the target; return list of (weapon, n_models).
    from collections import defaultdict
    slots = defaultdict(list)
    for w in pool:
        slots[w.get("slot", w["name"])].append(w)
    chosen = []
    for slot, ws in slots.items():
        if len(ws) == 1:
            chosen.append(ws[0])
        else:
            chosen.append(max(ws, key=lambda w: _score_weapon(w, target)))
    return chosen


def _score_weapon(w, target):
    # crude removal proxy for profile choice: strength vs toughness, AP, damage, attacks
    s = int(w["S"]); ap = -int(w["AP"]); d = 3 if "D" in str(w["D"]) else int(w["D"]) if str(w["D"]).isdigit() else 3
    a = 4 if "D" in str(w["A"]) else int(w["A"]) if str(w["A"]).isdigit() else 3
    return a * (1.4 if s >= target.toughness else 0.7) * (1 + 0.3 * ap) * d



def _wdmg(w):
    d = str(w.get("D", 1))
    return 4 if "D6" in d else 3 if "D3" in d else (int(d) if d.isdigit() else 2)


def _in_range(unit, target, w):
    if w.get("rng", 0) <= 0:
        return False
    return dist(unit.pos, target.pos) <= w["rng"]


def _shoot(me, opp, rng):
    focus = {}                                               # units already shooting each target
    shooters = list(me.on_board())
    for t in me.on_board():                                  # open-topped transports let cargo shoot
        if t.open_topped:
            for p in t.embarked:
                p.pos = t.pos
                shooters.append(p)
    for u in shooters:
        if u.fell_back or not u.ranged:
            continue
        targets = [t for t in opp.on_board()]
        if not targets:
            continue
        # focus: most useful damage (threat-weighted, prefer finishing) BUT spread fire — heavily
        # penalise a target already engaged by 2+ of my units (you can't dogpile one model in real 40k).
        best = None; best_val = 0
        for t in targets:
            best_val, best = _pick(u, t, u.ranged, focus, best_val, best)
        if best is None:
            continue
        focus[id(best)] = focus.get(id(best), 0) + 1
        los = _los(u, best, rng)                             # terrain/LoS: far shots on a real board
        if los <= 0:                                         # (esp. the T1 alpha) often have no line of sight
            continue
        for w in _best_weapon_set(u, best, melee=False):
            if not _in_range(u, best, w):
                continue
            half = dist(u.pos, best.pos) <= w["rng"] / 2
            shooters = max(1, int(round(u.models * los)))    # only models with LoS fire
            inst, mort = resolve_attacks(w, shooters, best, _mods_for(u, best), rng, half_range=half)
            apply_damage(best, inst, mort, rng)
            if not best.alive:
                break


def _los(u, t, rng):
    """Fraction of the shooting unit that has line of sight to the target. Real boards are ~30% blocking
    terrain: across the table (turn-1 alpha range) most guns are screened; LoS improves as armies close
    and as the target sits in the open. A little per-unit noise. Returns 0..1."""
    d = dist(u.pos, t.pos)
    base = 0.30 + 0.65 * max(0.0, 1 - d / 40.0)              # ~0.3 at 40"+, ~0.95 at contact
    if t.in_cover:
        base -= 0.1
    return max(0.0, min(1.0, base + rng.normal(0, 0.12)))


def _pick(u, t, pool, focus, best_val, best, melee=False):
    """Efficiency-weighted target value: REMOVING a unit (fraction of its wounds you clear) matters far
    more than chipping a tough one — so spears wipe the fragile scorers instead of pinging a Ravager,
    and anti-tank isn't wasted on chaff. Threat scales it; fire-spread penalises pile-on."""
    dmg = _expected_vs(u, t, melee=melee)
    wpn_d = max((_wdmg(w) for w in pool), default=1)
    if wpn_d >= 3 and t.wounds < wpn_d:
        dmg *= 0.4                                        # anti-tank into chaff = mostly wasted overkill
    frac = min(1.0, dmg / max(1.0, t.total_w))            # fraction of the unit removed
    val = t.threat * (0.25 + 0.75 * frac) * (0.5 + 0.5 * frac)   # heavily reward WIPING a unit
    val /= (1 + 1.5 * focus.get(id(t), 0))
    return (val, t) if val > best_val else (best_val, best)


def _expected_vs(u, t, melee):
    """Cheap EV proxy (for AI target choice only) using the first weapon slot."""
    pool = u.melee if melee else u.ranged
    if not pool:
        return 0.0
    w = max(pool, key=lambda w: _score_weapon(w, t))
    return u.models * _score_weapon(w, t) * 0.12


def _charge_and_fight(me, opp, rng, board):
    # charges: melee units within 8" declare + roll 2d6
    for u in me.on_board():
        if not u.melee or u.fell_back:
            continue
        near = [t for t in opp.on_board() if 0 < dist(u.pos, t.pos) <= 12]
        if not near:
            continue
        t = min(near, key=lambda t: dist(u.pos, t.pos))
        need = dist(u.pos, t.pos) - 1.0
        roll = int(rng.integers(1, 7) + rng.integers(1, 7))
        rr = u.abilities.get("reroll_charge")
        if rr and roll < need:
            roll = max(roll, int(rng.integers(1, 7) + rng.integers(1, 7)))
        if roll >= need:
            u.pos = (t.pos[0], t.pos[1] + (0.5 if u.side == "A" else -0.5))
            u.charged = True
    # fight: chargers first (active player), then alternate — simplified: active chargers, then all others
    fighters = [u for u in me.on_board() if u.melee] + [u for u in opp.on_board() if u.melee]
    fighters.sort(key=lambda u: (not u.charged))
    piled = {}                                                # base-contact limit: you can only physically
    def cap(t):                                               # surround a BIG single model with ~2-3 units;
        return t.wounds >= 8 and t.models == 1                # multi-model squads can be focused freely.
    for u in fighters:
        if not u.alive or not u.melee:
            continue
        foe = me if u.side == "B" else opp
        engaged = [t for t in foe.on_board() if dist(u.pos, t.pos) <= 3.0]
        if not engaged:
            continue
        def mval(t):
            dmg = _expected_vs(u, t, melee=True)
            frac = min(1.0, dmg / max(1.0, t.total_w))
            v = t.threat * (0.25 + 0.75 * frac) * (0.5 + 0.5 * frac)   # reward wiping the unit
            return v / (1 + 2.0 * piled.get(id(t), 0)) if cap(t) else v
        t = max(engaged, key=mval)
        if cap(t) and piled.get(id(t), 0) >= 3:
            alt = [x for x in engaged if not (cap(x) and piled.get(id(x), 0) >= 3)]
            if alt:
                t = max(alt, key=mval)
        piled[id(t)] = piled.get(id(t), 0) + 1
        for w in _best_weapon_set(u, t, melee=True):
            inst, mort = resolve_attacks(w, u.models, t, _mods_for(u, t, charged=u.charged), rng, charged=u.charged)
            apply_damage(t, inst, mort, rng)
        u.fought = True


def _melee_primary(u, opp):
    """A unit whose melee is its real threat should hunt, even if it also has a gun (e.g. a C'tan)."""
    if not u.melee or not opp.on_board():
        return False
    t = min(opp.on_board(), key=lambda x: dist(u.pos, x.pos))
    mbest = max((_score_weapon(w, t) for w in u.melee), default=0)
    rbest = max((_score_weapon(w, t) for w in u.ranged), default=0)
    return mbest >= rbest and u.role in ("line", "anti_tank", "fast", "character")


def _move(me, opp, board, rnd, rng):
    """Objective-centric AI: every unit is assigned the objective it should contest/hold (spread across
    the board, weighted by need + reachability). Melee-primary units that find an enemy sitting ON their
    objective charge in to clear it; everyone else moves to stand on the point. This makes both armies
    fight OVER objectives instead of scrumming in midfield."""
    held, _ = board.control([me, opp])
    crowd = {}
    order = sorted(me.on_board(), key=lambda u: -u.eff_oc() - (2 if _melee_primary(u, opp) else 0))
    for u in order:
        u.advanced = u.fell_back = u.charged = False
        oi = _best_objective(u, board, held, me, opp, crowd)
        crowd[oi] = crowd.get(oi, 0) + 1
        dest = board.objectives[oi]
        boost = 3 if u.role in ("fast", "action") else 0
        moved = False
        if _melee_primary(u, opp):
            on_point = [t for t in opp.on_board() if dist(t.pos, dest) <= 4]
            if on_point:
                _step_toward(u, min(on_point, key=lambda t: dist(u.pos, t.pos)).pos, u.move + boost)
                moved = True
        if not moved:
            _step_toward(u, dest, u.move + boost)
        if u.embarked and dist(u.pos, dest) <= 8:      # transport delivers its cargo onto the point
            _disembark(u, dest)


def _disembark(transport, dest):
    for i, p in enumerate(transport.embarked):
        p.transport = None
        p.pos = (dest[0] + (i - len(transport.embarked) / 2) * 1.2, dest[1] + (0.5 if p.side == "A" else -0.5))
    transport.embarked = []


def _best_objective(u, board, held, me, opp, crowd):
    opp_side = "B" if u.side == "A" else "A"
    best_i, best_v = 0, -1e9
    for i, o in enumerate(board.objectives):
        who = held.get(i)
        enemy_near = any(dist(t.pos, o) <= 4 for t in opp.on_board())
        if who == opp_side:
            need = 3.0                                     # flip an enemy point
        elif who is None:
            need = 2.0                                     # claim an open point
        else:
            need = 2.2 if enemy_near else 0.7              # defend if contested, else lightly hold
        if i == 0:
            need += 0.6                                    # centre matters most
        if board.in_territory(o, opp_side) and u.role in ("fast", "action", "character"):
            need += 0.5                                    # fast pieces push the enemy home
        v = need - dist(u.pos, o) / 30.0 - 0.5 * crowd.get(i, 0)   # spread out; prefer reachable
        if v > best_v:
            best_v, best_i = v, i
    return best_i


def _step_toward(u, dest, move):
    d = dist(u.pos, dest)
    if d <= move or d == 0:
        u.pos = dest
    else:
        f = move / d
        u.pos = (u.pos[0] + (dest[0] - u.pos[0]) * f, u.pos[1] + (dest[1] - u.pos[1]) * f)


def _arrive_reserves(me, board, rnd, rng):
    if rnd < 2:
        return
    for u in me.units:
        if u.in_reserve and u.alive:
            # deep strike near a contested/enemy objective, 9"+ from enemies (assumed placeable)
            oi = board.home_objective("B" if me.side == "A" else "A")
            ox, oy = board.objectives[oi]
            u.pos = (ox, oy + (9 if me.side == "A" else -9))
            u.in_reserve = False


def _command(me, rnd):
    me.cp += 1
    for u in me.on_board():
        u.fought = False
        # battle-shock: below half strength -> Ld test (simplified: 8+ on 2d6 with Ld)
        if u.models * 2 < u.start_strength:
            u.battle_shocked = False   # Custodes/most pass reliably; opponents handled in roster ld


def _reanimate(army, rng):
    for u in army.units:
        if u.reanimate and u.alive and u.models < u.start_strength:
            # reanimation protocols: return ~reanimate * start models this turn
            back = int(round(u.reanimate * u.start_strength * 0.9))
            if back:
                u.models = min(u.start_strength, u.models + back)
                if u.cur_w <= 0:
                    u.cur_w = u.wounds


def _comeback(army, rng):
    """Once-per-game 'necrodermis' return for C'tan-type units (ability 'comeback' = prob)."""
    for u in army.units:
        if u.abilities.get("comeback") and not u.alive and not getattr(u, "_came_back", False):
            if rng.random() < u.abilities["comeback"]:
                u.models = 1
                u.cur_w = u.wounds
            u._came_back = True


def play_game(armyA, armyB, missionA, missionB, board, rng, first=None):
    for u in armyA.units + armyB.units:
        u.snapshot_start()
    armies = [armyA, armyB]
    order = ([armyA, armyB] if (first or "A") == "A" else [armyB, armyA])
    vp = {"A": 0.0, "B": 0.0}
    missions = {"A": missionA, "B": missionB}
    firstsides = {armyA.side: order[0] is armyA, armyB.side: order[0] is armyB}
    for rnd in range(1, 6):
        for me in order:
            opp = armyB if me is armyA else armyA
            _command(me, rnd)
            _arrive_reserves(me, board, rnd, rng)
            board.update_cover(armies)
            _move(me, opp, board, rnd, rng)
            alive_before = sum(1 for u in opp.units if u.alive)
            _shoot(me, opp, rng)
            _charge_and_fight(me, opp, rng, board)
            _reanimate(me, rng)
            _comeback(opp, rng)                              # C'tan necrodermis return after being attacked
            kills = alive_before - sum(1 for u in opp.units if u.alive)
            held, _ = board.control(armies)
            vp[me.side] += score_turn(missions[me.side], held, board, me, opp, rnd,
                                      kills, firstsides[me.side])
    for me in armies:
        opp = armyB if me is armyA else armyA
        held, _ = board.control(armies)
        vp[me.side] += end_of_battle(missions[me.side], held, board, me, opp)
    # cap primary at 50, add nothing else; whoever has more VP wins
    return vp
