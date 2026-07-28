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


def _in_range(unit, target, w):
    if w.get("rng", 0) <= 0:
        return False
    return dist(unit.pos, target.pos) <= w["rng"]


def _shoot(me, opp, rng):
    focus = {}                                               # units already shooting each target
    for u in me.on_board():
        if u.fell_back or not u.ranged:
            continue
        targets = [t for t in opp.on_board()]
        if not targets:
            continue
        # focus: most useful damage (threat-weighted, prefer finishing) BUT spread fire — heavily
        # penalise a target already engaged by 2+ of my units (you can't dogpile one model in real 40k).
        best = None; best_val = 0
        for t in targets:
            val = _expected_vs(u, t, melee=False) * t.threat
            if t.total_w <= _expected_vs(u, t, melee=False) * 1.4:
                val *= 1.5
            val /= (1 + 1.5 * focus.get(id(t), 0))
            if val > best_val:
                best_val, best = val, t
        if best is None:
            continue
        focus[id(best)] = focus.get(id(best), 0) + 1
        for w in _best_weapon_set(u, best, melee=False):
            if not _in_range(u, best, w):
                continue
            half = dist(u.pos, best.pos) <= w["rng"] / 2
            inst, mort = resolve_attacks(w, u.models, best, _mods_for(u, best), rng, half_range=half)
            apply_damage(best, inst, mort, rng)
            if not best.alive:
                break


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
    for u in fighters:
        if not u.alive or not u.melee:
            continue
        foe = me if u.side == "B" else opp
        engaged = [t for t in foe.on_board() if dist(u.pos, t.pos) <= 3.0]
        if not engaged:
            continue
        t = max(engaged, key=lambda t: _expected_vs(u, t, melee=True) * t.threat)
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
    held, _ = board.control([me, opp])
    for u in me.on_board():
        u.advanced = u.fell_back = u.charged = False
        if _melee_primary(u, opp):
            # hunt the enemy this unit most wants to fight (best removal × threat), biased to the nearest
            tgt = max(opp.on_board(), key=lambda t: _expected_vs(u, t, melee=True) * t.threat / (1 + dist(u.pos, t.pos) / 12))
            _step_toward(u, tgt.pos, u.move + (3 if u.role == "fast" else 0))
        else:
            obj = _pick_objective(u, board, held, opp)
            _step_toward(u, board.objectives[obj], u.move)


def _pick_objective(u, board, held, opp):
    # prefer an uncontrolled/enemy objective we can reach and matter on; else nearest
    scored = []
    for i, o in enumerate(board.objectives):
        d = dist(u.pos, o)
        want = 2.0 if held.get(i) != u.side else 0.6      # contest what we don't hold
        if board.in_territory(o, "B" if u.side == "A" else "A"):
            want += 0.4                                    # pushing enemy territory (home-grab)
        scored.append((want - d / 60.0, i))
    return max(scored)[1]


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
            back = int(round(u.reanimate * u.start_strength * 0.5))
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
                u.cur_w = max(1, u.wounds // 2)
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
