"""The turn-by-turn game loop: deployment -> 5 battle rounds (command / move / shoot / charge / fight)
-> real objective OC scoring + real primary-mission VP + a state-driven secondary. Tactics are greedy
heuristics (move to contest objectives / into range, focus-fire the best target, charge when reachable).
Combat is dice-resolved (wh.sim.combat). Missions come from data/missions.yaml via wh.sim.mission."""
from __future__ import annotations

import numpy as np

from .entities import Board, dist, HOME_Y, DEPLOY_LINE, BOARD_H, BOARD_W
from .combat import resolve_attacks, apply_damage
from .mission import score_turn, end_of_battle
from ..mathhammer import Mods
from .. import sim
from . import stratagems
from . import strategy as _strat
from . import secondaries as _sec
from . import attach as _attach


def _S(army):
    return getattr(army, "strategy", None) or _strat.BALANCED


# Optional per-unit damage attribution: if analysis sets ON_DAMAGE, it's called (attacker_unit, target,
# wounds_lost) after each apply_damage. The shoot/fight phases tag CUR_ATTACKER so the hook knows the source.
ON_DAMAGE = None
CUR_ATTACKER = None


def _rr_rank(a):
    return {None: 0, "": 0, "ones": 1, "fails": 2}.get(a, 0)


def _mods_for(unit, target, charged=False, army=None):
    """Assemble the Mods for this unit vs this target from its abilities/army rules (the tapestry)."""
    m = Mods(charged=charged)
    ab = unit.abilities
    if ab.get("crit_hit"):
        m.crit_hit = ab["crit_hit"]                       # e.g. Martial Mastery crit-on-5
    if ab.get("reroll_hits"):
        m.reroll_hits = ab["reroll_hits"]
    if ab.get("reroll_wounds"):
        m.reroll_wounds = ab["reroll_wounds"]
    if ab.get("str_charge") and charged:
        m.str_bonus = ab["str_charge"]                    # e.g. Blood Angels' Red Thirst: +2 S on the charge
    if ab.get("wound_charge") and charged:
        m.wound += ab["wound_charge"]
    m.stationary = getattr(unit, "stationary", False)     # [HEAVY] +1 to hit if it Remained Stationary
    # ARMY RULE — OATH OF MOMENT (Adeptus Astartes). vs the Oath target: full re-roll Hits; +1 to Wound for
    # a Codex-SM detachment (no BA/DA/DW/SW); Caanok Var (Calculated Annihilation) adds re-roll Wound-1s AND
    # RE-SELECTS the target when it dies, so the benefit never wastes.
    if army is not None and getattr(army, "_oath", False):
        ot = getattr(army, "_oath_target", None)
        if (ot is None or not ot.alive) and getattr(army, "_caanok", False):
            army._oath_target = ot = target               # RECALCULATING: re-oath onto a live target
        if ot is target:
            m.reroll_hits = "fails" if _rr_rank("fails") >= _rr_rank(m.reroll_hits) else m.reroll_hits
            if getattr(army, "_oath_codex_bonus", False):
                m.wound += 1
            if getattr(army, "_caanok", False) and _rr_rank(m.reroll_wounds) < 1:
                m.reroll_wounds = "ones"
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


def _ni(v, d=0):                          # weapon stats can be '-', '2D6', 'N/A' — best-effort int
    try:
        return int(str(v).strip())
    except (ValueError, TypeError):
        return d


def _score_weapon(w, target):
    # crude removal proxy for profile choice: strength vs toughness, AP, damage, attacks
    s = _ni(w["S"], 4); ap = -_ni(w["AP"], 0); d = 3 if "D" in str(w["D"]) else _ni(w["D"], 3)
    a = 4 if "D" in str(w["A"]) else _ni(w["A"], 3)
    return a * (1.4 if s >= target.toughness else 0.7) * (1 + 0.3 * ap) * d



def _wdmg(w):
    d = str(w.get("D", 1))
    return 4 if "D6" in d else 3 if "D3" in d else (int(d) if d.isdigit() else 2)


def _in_range(unit, target, w):
    if w.get("rng", 0) <= 0:
        return False
    return dist(unit.pos, target.pos) <= w["rng"]


def _engaged(u, opp):
    """Is this unit within Engagement Range of any enemy (locked in melee)? Then it may only shoot PISTOLs,
    and only at what it's engaged with. Threshold matches the fight phase's engagement test (3\" + the
    other unit's footprint) — NOT both radii, which over-flagged distant units as locked."""
    return any(e.alive and dist(u.pos, e.pos) <= 3.0 + e.radius for e in opp.on_board())


def _can_fire(w, engaged, advanced):
    """11E firing eligibility for a weapon PROFILE given the unit's state:
      - ENGAGED (locked in melee): only [PISTOL] weapons may fire (at the unit you're engaged with).
      - ADVANCED this turn: only [ASSAULT] weapons may fire.
      - otherwise: any weapon.
    Note [ASSAULT] weapons fire whether or not you Advanced — the Advance branch permits them, and a
    non-advanced unit reaches the final `return True` (all weapons, Assault included). Nothing but being
    locked in melee ever stops an Assault weapon from firing."""
    kw = w.get("abilities", [])
    if engaged:
        return "PISTOL" in kw
    if advanced:
        return "ASSAULT" in kw
    return True


def _shoot(me, opp, board, rng):
    focus = {}                                               # units already shooting each target
    held, _ = board.control([me, opp])                       # for VP-aware target priority
    shooters = list(me.on_board())
    for t in me.on_board():                                  # open-topped transports let cargo shoot
        if t.open_topped:
            for p in t.embarked:
                p.pos = t.pos
                shooters.append(p)
    for u in shooters:
        if u.fell_back or not u.ranged:
            continue
        # ASSAULT / PISTOL / engagement: an ADVANCED unit fires only [ASSAULT] weapons; a unit locked in
        # melee fires only [PISTOL] weapons (at the enemy it's engaged with). Skip if nothing can fire.
        engaged = _engaged(u, opp)
        if not any(_can_fire(w, engaged, u.advanced) for w in u.ranged):
            continue
        # GEOMETRIC LoS: you can only shoot targets you can SEE — Event-Companion ruins block the line,
        # AND intervening unit blobs SCREEN (a unit behind a screen can't be shot). This is the spatial
        # fix for shooting: you must clear the screen before the valuable unit behind it.
        blobs = me.on_board() + opp.on_board()
        if engaged:                                          # PISTOLs: only the enemy you're locked with
            targets = [t for t in opp.on_board()             # engagement test consistent with _engaged / fight
                       if dist(u.pos, t.pos) <= 3.0 + t.radius and board.has_los(u.pos, t.pos)]
        else:
            targets = [t for t in opp.on_board() if board.has_los(u.pos, t.pos) and not _screened(u, t, blobs)]
        # PRECISION: this shooter can pick an attached CHARACTER out of its unit (the only way to target an
        # embedded leader in 11E — there is no Look Out Sir). It appears at its host's position.
        if "PRECISION" in u.keywords or u.abilities.get("precision"):
            for t in list(targets):
                for l in _attach.embedded_leaders(t):
                    l.pos = t.pos
                    targets.append(l)
        if not targets:
            continue
        best = None; best_val = 0
        for t in targets:
            best_val, best = _pick(u, t, u.ranged, focus, best_val, best, board=board, held=held)
        if best is None:
            continue
        focus[id(best)] = focus.get(id(best), 0) + 1
        mods = _mods_for(u, best, army=me)
        stratagems.on_attack(me, opp, u, best, mods, "shoot")   # CP economy: attacker/defender may spend
        for w in _best_weapon_set(u, best, melee=False):
            if not _can_fire(w, engaged, u.advanced):           # ASSAULT-only if advanced / PISTOL-only if engaged
                continue
            if not _in_range(u, best, w):
                continue
            half = dist(u.pos, best.pos) <= w["rng"] / 2
            inst, mort = resolve_attacks(w, u.models, best, mods, rng, half_range=half)
            lost = apply_damage(best, inst, mort, rng)
            if ON_DAMAGE and lost:
                ON_DAMAGE(u, best, lost)
            if not best.alive:
                break
        if not best.alive and getattr(best, "host", None) is not None:
            _attach.on_leader_killed(best)                   # PRECISION sniped an embedded leader


def _screened(shooter, t, blobs):
    """A non-tall target is SCREENED (can't be shot) if another unit's footprint sits on the line
    between shooter and target. Tall models (vehicles/monsters) are seen over infantry screens."""
    if t.tall:
        return False
    from .entities import seg_hits_circle
    d_st = dist(shooter.pos, t.pos)
    for u in blobs:
        if u is shooter or u is t or u.tall or not u.alive:
            continue
        if dist(shooter.pos, u.pos) < d_st and dist(t.pos, u.pos) < d_st \
                and seg_hits_circle(shooter.pos, t.pos, u.pos, u.radius):
            return True
    return False


def _obj_relevance(t, board, held):
    """VP-play weighting: a unit ON/contesting an objective is worth more to remove than an equally-scary
    unit irrelevant to the mission. Real players kill the SCORERS, not the biggest stat-line. Returns a
    multiplier ~[0.8, 1.6]: 1.6 if the target is currently HOLDING an objective (kill it to flip/deny),
    1.3 if merely contesting one, 0.8 if it's off doing nothing (the scary corner unit)."""
    if board is None or held is None:
        return 1.0
    best = 0.8
    for i, o in enumerate(board.objectives):
        if dist(t.pos, o) <= 3.0 + 0.5 * t.radius:
            best = max(best, 1.6 if held.get(i) == t.side else 1.3)
    return best


def _pick(u, t, pool, focus, best_val, best, melee=False, board=None, held=None):
    """Efficiency-weighted target value: REMOVING a unit (fraction of its wounds you clear) matters far
    more than chipping a tough one — so spears wipe the fragile scorers instead of pinging a Ravager,
    and anti-tank isn't wasted on chaff. Threat scales it; fire-spread penalises pile-on; objective
    relevance (VP-play) tilts fire toward units that are actually scoring."""
    dmg = _expected_vs(u, t, melee=melee)
    wpn_d = max((_wdmg(w) for w in pool), default=1)
    if wpn_d >= 3 and t.wounds < wpn_d:
        dmg *= 0.4                                        # anti-tank into chaff = mostly wasted overkill
    frac = min(1.0, dmg / max(1.0, t.total_w))            # fraction of the unit removed
    val = t.threat * (0.25 + 0.75 * frac) * (0.5 + 0.5 * frac)   # heavily reward WIPING a unit
    val *= _obj_relevance(t, board, held)                 # VP-play: prioritise the scorers
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
    # charges: melee units declare + roll 2d6. `commit` widens/narrows the charge leash (cagey armies
    # only charge what's already close; alpha armies reach further).
    crange = 12 * min(1.4, max(0.5, _S(me).commit))
    held, _ = board.control([me, opp])                       # for VP-aware charge/fight priority
    for u in me.on_board():
        if not u.melee or u.fell_back or u.advanced:         # Advancing forbids charging this turn
            continue
        near = [t for t in opp.on_board() if 0 < dist(u.pos, t.pos) <= crange]
        if not near:
            continue
        # charge the enemy that matters MOST for VP (a scorer sitting on a point) among the reachable,
        # not merely the nearest — but keep distance a strong tie-breaker (a far charge often whiffs).
        t = max(near, key=lambda t: _obj_relevance(t, board, held) - dist(u.pos, t.pos) / 24.0)
        need = dist(u.pos, t.pos) - 1.0
        roll = int(rng.integers(1, 7) + rng.integers(1, 7))
        rr = u.abilities.get("reroll_charge")
        if rr and roll < need:
            roll = max(roll, int(rng.integers(1, 7) + rng.integers(1, 7)))
        if roll >= need:
            u.pos = (t.pos[0], t.pos[1] + (0.5 if u.side == "A" else -0.5))
            u.charged = True
    # fight: 11e ALTERNATING activation. Fights-First units (chargers) go first, then the rest — and within
    # each group the two players ALTERNATE (active first). This is the key combat-fidelity fix: the old
    # sequential order let the active player's chargers wipe the defenders BEFORE they could swing back
    # (a big charger over-advantage — it inflated Custodes' elite-melee matchups). Now a defender trades
    # back between the attacker's activations, so elite mirrors (Blood Angels) grind instead of a one-sided
    # sweep. COUNTER-OFFENSIVE: the defender (opp) may spend 2CP to fight FIRST with one unit.
    co_unit = stratagems.wants_counter_offensive(opp, [c for c in me.on_board() if c.charged], board)
    mine = [u for u in me.on_board() if u.melee]
    theirs = [u for u in opp.on_board() if u.melee]
    ff_me = [u for u in mine if u.charged]
    ff_them = [u for u in theirs if u is co_unit]
    rest_me = [u for u in mine if not u.charged]
    rest_them = [u for u in theirs if u is not co_unit]
    fighters = ([co_unit] if co_unit else []) + _interleave(ff_me, [t for t in ff_them if t is not co_unit]) \
        + _interleave(rest_me, rest_them)
    # ENGAGEMENT PERIMETER: a unit can only be attacked by as many enemy units as physically fit around
    # its footprint — you CANNOT pile the whole army onto one brick. Cap ~ its perimeter / an attacker's
    # frontage. This is the core screening/spatial fix for the focus-fire flaw.
    piled = {}
    def maxatk(t):
        return max(2, min(6, int(round(t.radius * 1.8))))
    for u in fighters:
        if not u.alive or not u.melee:
            continue
        foe = me if u.side == "B" else opp
        engaged = [t for t in foe.on_board() if dist(u.pos, t.pos) <= 3.0 + t.radius]
        if not engaged:
            continue
        def mval(t):
            dmg = _expected_vs(u, t, melee=True)
            frac = min(1.0, dmg / max(1.0, t.total_w))
            return t.threat * (0.25 + 0.75 * frac) * (0.5 + 0.5 * frac) \
                * _obj_relevance(t, board, held)          # reward wiping the unit + VP-play (kill scorers)
        avail = [t for t in engaged if piled.get(id(t), 0) < maxatk(t)]
        pool = avail or engaged                              # if all full, extras still swing (edge case)
        t = max(pool, key=mval)
        piled[id(t)] = piled.get(id(t), 0) + 1
        atk_army, def_army = (me, opp) if u.side == me.side else (opp, me)
        mods = _mods_for(u, t, charged=u.charged, army=atk_army)
        stratagems.on_attack(atk_army, def_army, u, t, mods, "fight")   # CP economy in melee
        for w in _best_weapon_set(u, t, melee=True):
            inst, mort = resolve_attacks(w, u.models, t, mods, rng, charged=u.charged)
            lost = apply_damage(t, inst, mort, rng)
            if ON_DAMAGE and lost:
                ON_DAMAGE(u, t, lost)
        # DEATH VISIONS OF SANGUINIUS: a Death Company model destroyed in melee strikes back (mortals to
        # its killer) — BA stickiness that makes them trade even while dying.
        if not t.alive and t.abilities.get("fight_on_death") and not getattr(t, "_dv_used", False):
            t._dv_used = True
            apply_damage(u, np.zeros(0, dtype=int), int(rng.integers(1, 4)), rng)
        u.fought = True


def _interleave(a, b):
    """Alternate two ordered lists (active player first): a0, b0, a1, b1, ..."""
    out = []
    for i in range(max(len(a), len(b))):
        if i < len(a):
            out.append(a[i])
        if i < len(b):
            out.append(b[i])
    return out


_ZONE = {"A": (2, 17), "B": (43, 58)}       # deployment zones (24" no-man's-land), 11e-style


def _durable(u):
    """A unit tough enough that it does NOT fear the enemy alpha — it pushes forward and trades."""
    sv = 3 if str(u.save)[0] in "23" else (int(str(u.save)[0]) if str(u.save)[0].isdigit() else 6)
    return sv <= 3 and (u.invuln is not None or u.wounds >= 3 or u.tall)


def _threat_type(enemy):
    """Is the enemy a SHOOTING alpha (long guns) or an ASSAULT alpha (fast melee)? Drives how I deploy."""
    shoot = sum(u.models * max((w.get("rng", 0) for w in u.ranged), default=0) for u in enemy.units if u.ranged)
    melee = sum(u.models * (u.move + 12) for u in enemy.units if u.melee and not u.ranged) + \
        sum(u.move for u in enemy.units if u.role == "fast")
    return "shooting" if shoot >= melee * 8 else "assault"


def deploy(A, B, board):
    """Threat-TYPE-aware deployment (how good players actually deploy):
      * vs an ASSAULT alpha: fragile units sit just outside the enemy's turn-1 melee reach (a first-turn
        charge then only happens on a mistake / Infiltrators).
      * vs a SHOOTING alpha: hiding back is pointless (the guns reach anyway) and wastes your own range,
        so DURABLE units push forward INTO COVER to trade + close; only fragile units shelter.
    Durable/aggressive units push forward regardless (they want to engage); deep-strikers stay in
    reserve; embarked units ride their transport."""
    for army, enemy in ((A, B), (B, A)):
        s = army.side
        x0, y0, x1, y1 = board.zone[s]                       # this deployment's zone rect for my side
        cx, cy = (x0 + x1) / 2, (y0 + y1) / 2
        fx, fy = board.fwd[s]                                 # forward = toward the enemy
        wx, wy = -fy, fx                                      # wide axis = perpendicular (spread along it)
        depth = abs(fx) * (x1 - x0) + abs(fy) * (y1 - y0) or 12.0
        wide = abs(wx) * (x1 - x0) + abs(wy) * (y1 - y0) or 30.0
        ttype = _threat_type(enemy)
        ereach = max((u.move for u in enemy.units if u.melee and not u.in_reserve), default=6) + 15
        on = [u for u in army.units if not u.in_reserve and u.transport is None]
        n = len(on)
        for i, u in enumerate(on):
            t = ((i / (n - 1)) - 0.5) if n > 1 else 0.0       # -0.5..0.5 along the wide axis
            aggressive = _melee_primary(u, enemy) and u.role in ("fast", "line", "anti_tank")
            # push forward if aggressive/durable/vs a gunline you can't hide from; else shelter at the back
            push = aggressive or _durable(u) or (ttype == "shooting" and u.wounds >= 2)
            df = 0.42 if push else max(-0.45, 0.45 - (ereach + 3) / depth)   # depth frac (centre->enemy)
            df = max(-0.46, min(0.46, df + _S(army).deploy_depth * 0.3))     # strategy deploy depth
            px = cx + wx * t * wide * 0.92 + fx * df * depth
            py = cy + wy * t * wide * 0.92 + fy * df * depth
            if push and ttype == "shooting" and board.ruins:                 # seek cover vs a gunline
                r = min(board.ruins, key=lambda r: (px - (r[0] + r[2]) / 2) ** 2 + (py - (r[1] + r[3]) / 2) ** 2)
                px, py = 0.6 * px + 0.4 * (r[0] + r[2]) / 2, 0.6 * py + 0.4 * (r[1] + r[3]) / 2
            u.pos = (max(1.0, min(BOARD_W - 1, px)), max(1.0, min(BOARD_H - 1, py)))
            u.side = army.side
    for army in (A, B):
        for u in army.units:
            if u.transport is not None:
                u.pos = u.transport.pos


def _melee_primary(u, opp):
    """A unit whose melee is its real threat should hunt, even if it also has a gun (e.g. a C'tan)."""
    if not u.melee or not opp.on_board():
        return False
    t = min(opp.on_board(), key=lambda x: dist(u.pos, x.pos))
    mbest = max((_score_weapon(w, t) for w in u.melee), default=0)
    rbest = max((_score_weapon(w, t) for w in u.ranged), default=0)
    return mbest >= rbest and u.role in ("line", "anti_tank", "fast", "character")


def _should_advance(u, opp):
    """Advance (Move + D6") when the extra reach helps AND the shooting given up isn't worth keeping:
    no guns to forgo, or ALL guns are [ASSAULT] (so advancing costs nothing — the whole point of ASSAULT),
    or the unit is a board-grabber (action/screen/fast) whose job is position, not this turn's shots. A
    unit that wants to charge doesn't Advance (Advancing forbids charging)."""
    if _melee_primary(u, opp):
        return False
    if not u.ranged:
        return True
    if all("ASSAULT" in w.get("abilities", []) for w in u.ranged):
        return True
    return u.role in ("action", "screen", "fast")


def _move(me, opp, board, rnd, rng):
    """Objective-centric AI: every unit is assigned the objective it should contest/hold (spread across
    the board, weighted by need + reachability). Melee-primary units that find an enemy sitting ON their
    objective charge in to clear it; everyone else moves to stand on the point. This makes both armies
    fight OVER objectives instead of scrumming in midfield."""
    held, _ = board.control([me, opp])
    S = _S(me)
    crowd = {}
    order = sorted(me.on_board(), key=lambda u: -u.eff_oc() - (2 if _melee_primary(u, opp) else 0))
    for u in order:
        u.advanced = u.fell_back = u.charged = u.stationary = False
        _sp = u.pos                                        # start position, to detect Remain Stationary
        # FALL BACK: a non-durable unit locked in melee by an enemy that would likely wipe it disengages to
        # preserve itself (and its VP) instead of standing to be tabled. It forfeits shooting/charging this
        # turn (the real cost). Durable bricks stay and TRADE — this is a losing-side-survives compression
        # lever, not a blanket retreat. (Revives u.fell_back, which was dead code — only ever reset.)
        if _fall_back(u, opp, board, rng):
            continue
        oi = _best_objective(u, board, held, me, opp, crowd)
        crowd[oi] = crowd.get(oi, 0) + 1
        dest = board.objectives[oi]
        boost = 3 if u.role in ("fast", "action") else 0
        moved = False
        # FAST HUNTERS (strategy.hunt_shooters): bikes/fast melee run down the enemy's premium guns.
        if S.hunt_shooters and u.role == "fast" and u.melee:
            prey = [e for e in opp.on_board() if e.ranged and not e.fell_back
                    and dist(u.pos, e.pos) <= u.move + boost + 6]
            if prey:
                _step_toward(u, max(prey, key=lambda e: e.threat).pos, u.move + boost)
                moved = True
        if not moved and _melee_primary(u, opp):
            # cagey (commit<1) melee only lunges at a target sitting ON its objective; aggressive commit
            # widens the leash so it hunts further afield.
            reach = 4 + 8 * max(0.0, S.commit - 0.6)
            on_point = [t for t in opp.on_board() if dist(t.pos, dest) <= reach]
            if on_point:
                _step_toward(u, min(on_point, key=lambda t: dist(u.pos, t.pos)).pos, u.move + boost)
                moved = True
        if not moved:
            # LoS-AWARE HOLD: take the objective-adjacent spot hidden from the most enemy guns (ruin between
            # = ZERO fire). los_hold scales how hard the unit prioritises cover over standing on the point.
            dest_pt = _covered_hold(u, dest, board, opp, S.los_hold)
            step = u.move + boost
            if dist(u.pos, dest_pt) > step and _should_advance(u, opp):
                step += int(rng.integers(1, 7))       # ADVANCE +D6" (forfeits non-Assault shooting + charge)
                u.advanced = True
            _step_toward(u, dest_pt, step)
        # Remained Stationary if it effectively didn't move (and didn't Advance/Fall Back) -> HEAVY bonus
        u.stationary = (not u.advanced and not u.fell_back and dist(u.pos, _sp) < 0.5)
        if u.embarked and dist(u.pos, dest) <= 8:      # transport delivers its cargo onto the point
            _disembark(u, dest)


def _fall_back(u, opp, board, rng):
    """Decide + execute Fall Back. Returns True if the unit disengaged (and should skip its normal move).
    Trigger: the unit is a non-durable piece engaged by melee enemies whose expected damage would cripple
    it (>=60% of its wounds) if it stayed. It retreats directly away from the engagers toward its own
    home edge, and is barred from shooting/charging this turn (guards elsewhere read u.fell_back)."""
    # only genuinely FRAGILE pieces flee (durable bricks + elite multi-wound bodies stay and TRADE)
    sv = int(str(u.save)[0]) if str(u.save)[0].isdigit() else 6
    if _durable(u) or (sv <= 3 and u.wounds >= 3):
        return False
    engagers = [e for e in opp.on_board()
                if e.melee and dist(u.pos, e.pos) <= 3.0 + u.radius + e.radius]
    if not engagers:
        return False
    incoming = sum(_expected_vs(e, u, melee=True) for e in engagers)
    outgoing = sum(_expected_vs(u, e, melee=True) for e in engagers)
    # flee only when near-certain to be wiped AND losing the exchange — otherwise stay and trade back
    if incoming < 0.9 * max(1.0, u.total_w) or outgoing >= 0.8 * incoming:
        return False
    ex = sum(e.pos[0] for e in engagers) / len(engagers)
    ey = sum(e.pos[1] for e in engagers) / len(engagers)
    hx, hy = board.home[u.side]
    # blend "away from the engagers" with "toward home" so the retreat also heads somewhere safe
    ax, ay = u.pos[0] - ex, u.pos[1] - ey
    tx, ty = hx - u.pos[0], hy - u.pos[1]
    import math
    an = math.hypot(ax, ay) or 1.0
    tn = math.hypot(tx, ty) or 1.0
    vx, vy = ax / an * 0.6 + tx / tn * 0.4, ay / an * 0.6 + ty / tn * 0.4
    vn = math.hypot(vx, vy) or 1.0
    step = u.move + (2 if u.role in ("fast", "action") else 0)
    u.pos = (max(1.0, min(BOARD_W - 1, u.pos[0] + vx / vn * step)),
             max(1.0, min(BOARD_H - 1, u.pos[1] + vy / vn * step)))
    u.fell_back = True
    # DESPERATE ESCAPE (09.07): a BATTLE-SHOCKED unit that Falls Back tests per model — each 1-2 loses a
    # model. (A non-shocked unit only tests if it moves THROUGH enemies, which this away-move doesn't.)
    if u.battle_shocked and u.models > 0:
        lost = int((rng.integers(1, 7, u.models) <= 2).sum())
        if lost:
            u.models = max(0, u.models - lost)
            u.cur_w = u.wounds if u.models > 0 else 0
    return True


def _covered_hold(u, dest, board, opp, weight=1.0):
    """Pick the spot to hold `dest` from: within control range (<=3") of the objective but HIDDEN from as
    many enemy shooters as possible (LoS blocked by a ruin). `weight` (strategy.los_hold) scales how much
    hiding is worth vs standing on the point. Non-tall units only."""
    if weight <= 0.05 or u.tall:
        return dest
    shooters = [e for e in opp.on_board() if e.ranged and e.alive and not e.fell_back]
    if not shooters:
        return dest
    import math
    best, best_score = dest, -1e9
    cands = [dest] + [(dest[0] + r * math.cos(math.radians(ang)), dest[1] + r * math.sin(math.radians(ang)))
                      for ang in range(0, 360, 45) for r in (2.6,)]
    for c in cands:
        if not (1 <= c[0] <= BOARD_W - 1 and 1 <= c[1] <= BOARD_H - 1):
            continue
        hidden = sum(1 for s in shooters if not board.has_los(c, s.pos))
        score = weight * hidden - 0.15 * dist(u.pos, c)
        if score > best_score:
            best_score, best = score, c
    return best


def _disembark(transport, dest):
    for i, p in enumerate(transport.embarked):
        p.transport = None
        p.pos = (dest[0] + (i - len(transport.embarked) / 2) * 1.2, dest[1] + (0.5 if p.side == "A" else -0.5))
    transport.embarked = []


def _best_objective(u, board, held, me, opp, crowd):
    opp_side = "B" if u.side == "A" else "A"
    S = _S(me)
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
        if board.in_territory(o, opp_side):
            if u.role in ("fast", "action", "character"):
                need += 0.5 * S.push_home                  # fast pieces push the enemy home (scaled)
            need -= S.own_half_bias                        # TURTLE: down-weight enemy-half objectives
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


def _arrive_reserves(me, opp, board, rnd, rng):
    if rnd < 2:
        return
    # STAGGER the drop: real deep-strike/reserves aren't a single all-at-once alpha (you also can't start
    # with most of your army in reserve). Bring ~half at R2, the rest from R3.
    res = [u for u in me.units if u.in_reserve and u.alive and not u.embedded]  # leaders arrive with host
    aggr = _S(me).reserve_aggr
    # ALPHA (aggr>0) brings everything at once for the charge; a shooty reserve (aggr<0) trickles in.
    split = 1.0 if aggr > 0.3 else (0.5 if aggr >= -0.3 else 0.34)
    k = len(res) if rnd >= 3 else max(1, int(round(len(res) * split + 0.49)))
    edge = 9 if me.side == "A" else -9
    # aggr>0 deep-strikes to threaten the ENEMY objective (charge next turn); aggr<0 arrives safe at OWN
    # objective to shoot; ~0 lands on a contested midfield point.
    tgt_side = ("B" if me.side == "A" else "A") if aggr >= -0.1 else me.side
    oi = board.home_objective(tgt_side)
    ox, oy = board.objectives[oi]
    for u in res[:k]:
        u.pos = (ox, oy + edge)
        u.in_reserve = False
        if u.deep_strike:
            # DEEP STRIKE (24.09): set up >9" from every enemy. Push back if the drop landed closer, so a
            # same-turn charge needs to cover >8" -> ~2D6>=9 (~28%), matching the real DS-charge odds.
            foes = opp.on_board()
            if foes:
                ne = min(foes, key=lambda e: dist(u.pos, e.pos))
                if dist(u.pos, ne.pos) < 9.1:
                    import math
                    vx, vy = u.pos[0] - ne.pos[0], u.pos[1] - ne.pos[1]
                    n = math.hypot(vx, vy) or 1.0
                    u.pos = (max(1.0, min(BOARD_W - 1, ne.pos[0] + vx / n * 9.1)),
                             max(1.0, min(BOARD_H - 1, ne.pos[1] + vy / n * 9.1)))


def _select_oath(army, opp):
    """Command phase: pick the Oath of Moment target — the enemy unit the army most wants dead (highest
    threat). Stored on army._oath_target; _mods_for grants the re-rolls/+1-wound vs it."""
    if not getattr(army, "_oath", False):
        return
    foes = opp.on_board()
    army._oath_target = max(foes, key=lambda t: t.threat) if foes else None


def _ld_val(ld):
    """Numeric Ld target for a 2D6 leadership roll (stored as '6+' or an int); default 6."""
    try:
        return int(str(ld).rstrip("+"))
    except (ValueError, TypeError):
        return 6


def _command(me, rnd, rng):
    if stratagems.ENABLED and getattr(me, "_strat", None) is None:
        stratagems.equip(me, getattr(me, "slug", None), getattr(me, "strat_dets", None))
    stratagems.turn_start(me)                    # reset per-turn CP budget + clear last turn's temp buffs
    me.cp += 1
    for u in me.on_board():
        u.fought = False
        # BATTLE-SHOCK (08.03 / 01.07): a unit AT OR BELOW half-strength (or already battle-shocked) tests
        # leadership — 2D6 >= a Ld in the unit. Fail -> battle-shocked until a later test passes: OC becomes
        # 0 (can't hold objectives, via eff_oc) and it can't be targeted by stratagems. Real morale variance,
        # and below-half hordes stop scoring.
        if u.battle_shocked or u.models * 2 <= u.start_strength:
            u.battle_shocked = int(rng.integers(1, 7) + rng.integers(1, 7)) < _ld_val(u.ld)
        else:
            u.battle_shocked = False


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
    _strat.equip(armyA, armyB); _strat.equip(armyB, armyA)   # opponent-aware strategy for both sides
    deploy(armyA, armyB, board)                 # threat-range-aware deployment
    armyA._sec = _sec.Secondaries(rng); armyB._sec = _sec.Secondaries(rng)   # Tactical secondary decks
    _attach.attach_all(armyA); _attach.attach_all(armyB)   # embed CHARACTERs into bodyguard units (tapestry)
    armies = [armyA, armyB]
    order = ([armyA, armyB] if (first or "A") == "A" else [armyB, armyA])
    vp = {"A": 0.0, "B": 0.0}
    missions = {"A": missionA, "B": missionB}
    firstsides = {armyA.side: order[0] is armyA, armyB.side: order[0] is armyB}
    for rnd in range(1, 6):
        for me in order:
            opp = armyB if me is armyA else armyA
            _command(me, rnd, rng)
            _select_oath(me, opp)                            # Army rule: pick the Oath of Moment target
            _arrive_reserves(me, opp, board, rnd, rng)
            board.update_cover(armies)
            _move(me, opp, board, rnd, rng)
            # snapshot enemy units at the start of my combat, for kill-count + secondary kill-metadata
            # (which of THIS turn's kills were characters / big models / on an objective).
            alive_before = sum(1 for u in opp.units if u.alive)
            on_obj_at_start = {id(u): any(dist(u.pos, o) <= 3.0 for o in board.objectives)
                               for u in opp.units if u.alive}
            _shoot(me, opp, board, rng)
            _charge_and_fight(me, opp, rng, board)
            _reanimate(me, rng)
            _comeback(opp, rng)                              # C'tan necrodermis return after being attacked
            _attach.detach_dead(armies)                      # a slain bodyguard's leader fights on alone
            kills = alive_before - sum(1 for u in opp.units if u.alive)
            destroyed = [_sec.destroyed_meta(u, on_obj_at_start.get(id(u), False))
                         for u in opp.units if not u.alive and id(u) in on_obj_at_start]
            held, _ = board.control(armies)
            vp[me.side] += score_turn(missions[me.side], held, board, me, opp, rnd,
                                      kills, firstsides[me.side])
            ctx = dict(board=board, me=me, opp=opp, held=held, destroyed=destroyed,
                       my_units=me.on_board(), opp_units=opp.on_board(),
                       my_home=board.home_objective(me.side), opp_home=board.home_objective(opp.side))
            vp[me.side] += me._sec.score(ctx, rng)
    for me in armies:
        opp = armyB if me is armyA else armyA
        held, _ = board.control(armies)
        vp[me.side] += end_of_battle(missions[me.side], held, board, me, opp)
    # cap primary at 50, add nothing else; whoever has more VP wins
    return vp
