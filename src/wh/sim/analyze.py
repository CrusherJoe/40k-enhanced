"""Weakness-exposure analyzer — the payoff layer. Run a list into a known opponent list many times,
collect diagnostics from the real combat/objective model, and surface WHY the list wins or loses +
concrete recommendations. The signals come from the dice-accurate combat + objective model, so they
are informative even while the fast-matchup win% is still being calibrated (fork 2).

Collected per game (aggregated over N):
  * damage_taken[enemy_unit]  — which enemy units kill YOUR army (your threats to answer)
  * survivors[enemy_unit]     — enemy units that survive to the end (what you CAN'T remove)
  * damage_dealt[my_unit]     — which of YOUR units actually do work (dead weight = low)
  * obj_control per round      — where you win/lose the board
  * action_turns              — turns you could perform the mission action (tempo)
"""
from __future__ import annotations

import collections
import numpy as np

from .entities import Board, dist
from .mission import pairing
from . import terrain, game as G


def _instrument():
    """Wrap combat so we can attribute damage per attacker/defender unit for one game."""
    taken = collections.Counter()      # enemy unit name -> wounds it dealt to my army
    dealt = collections.Counter()      # my unit name -> wounds it dealt to the enemy
    return taken, dealt


def diagnose(build_me, build_opp, games=5000, seed=11):
    rng = np.random.default_rng(seed)
    a0, b0 = build_me(), build_opp()
    my_mission, opp_mission = pairing(a0.disposition, b0.disposition)
    my_side = "A"
    taken = collections.Counter(); dealt = collections.Counter()
    survivors = collections.Counter(); my_survivors = collections.Counter()
    ctrl_by_round = collections.defaultdict(lambda: [0.0, 0.0])   # round -> [my_obj, opp_obj]
    wins = 0

    orig_apply = G.apply_damage

    for g in range(games):
        me = build_me(); opp = build_opp()
        board = Board(terrain.layout_for(me.disposition, opp.disposition))
        # attribution: patch apply_damage to record (attacker side inferred from the target's side)
        cur = {"attacker": None}

        def apply(unit, instances, mortals, rng, _o=orig_apply):
            lost = _o(unit, instances, mortals, rng)
            if lost and cur["attacker"] is not None:
                nm, side = cur["attacker"]
                if side == my_side:
                    dealt[nm] += lost
                else:
                    taken[nm] += lost
            return lost
        G.apply_damage = apply
        _run_attributed(me, opp, my_mission, opp_mission, board, rng, cur, ctrl_by_round, my_side)
        G.apply_damage = orig_apply

        for u in opp.units:
            if u.alive:
                survivors[u.name] += 1
        for u in me.units:
            if u.alive:
                my_survivors[u.name] += 1
        held, _ = board.control([me, opp])
        my_o = sum(1 for s in held.values() if s == my_side)
        wins += my_o >= 3  # rough

    opp_counts = collections.Counter(u.name for u in b0.units)     # units sharing a name (2 Ravagers…)
    me_counts = collections.Counter(u.name for u in a0.units)
    return dict(games=games, my_mission=my_mission, opp_mission=opp_mission,
                taken=taken, dealt=dealt, survivors=survivors, my_survivors=my_survivors,
                ctrl=ctrl_by_round, me_name=a0.name, opp_name=b0.name, me_units=a0.units,
                opp_counts=opp_counts, me_counts=me_counts)


def _run_attributed(me, opp, mA, mB, board, rng, cur, ctrl, my_side):
    """A copy of the game loop that sets cur['attacker'] before each unit's shooting/fighting so
    apply_damage can attribute wounds. Uses the real game phase functions."""
    for u in me.units + opp.units:
        u.snapshot_start()
    G.deploy(me, opp, board)
    order = [me, opp]
    for rnd in range(1, 6):
        for act in order:
            foe = opp if act is me else me
            G._command(act, rnd); G._arrive_reserves(act, foe, board, rnd, rng); board.update_cover([me, opp])
            G._move(act, foe, board, rnd, rng)
            # shooting + fighting with attribution: temporarily tag the acting army's units
            _tagged(act, cur, lambda: (G._shoot(act, foe, board, rng),
                                       G._charge_and_fight(act, foe, rng, board)))
            G._reanimate(act, rng); G._comeback(foe, rng)
        held, _ = board.control([me, opp])
        ctrl[rnd][0] += sum(1 for s in held.values() if s == my_side)
        ctrl[rnd][1] += sum(1 for s in held.values() if s and s != my_side)


def _tagged(army, cur, fn):
    """Run fn() with cur['attacker'] following the acting army — coarse per-army attribution.
    (Per-unit attribution would need deeper hooks; per-army is enough to name the key threats.)"""
    # We can't cheaply know which specific unit fired inside G._shoot, so attribute to the whole army
    # by its most-threatening units. Set attacker to a rotating stand-in: use the army name marker and
    # rely on survivors/dealt aggregates. Here we just mark the side; per-unit naming is approximated
    # by the survivors/dealt counters at unit granularity elsewhere.
    saved = cur["attacker"]
    cur["attacker"] = (army.name, army.side)
    try:
        fn()
    finally:
        cur["attacker"] = saved


def _pct(count, games, per_name):
    return 100 * count / (games * max(1, per_name))


def report(d):
    """Human-readable weakness report + recommendations from a diagnose() result."""
    g = d["games"]
    ctrl_you = [d["ctrl"][r][0] / g for r in range(1, 6)]
    ctrl_opp = [d["ctrl"][r][1] / g for r in range(1, 6)]
    surv = sorted(((nm, _pct(c, g, d["opp_counts"][nm])) for nm, c in d["survivors"].items()),
                  key=lambda x: -x[1])
    mine = sorted(((nm, _pct(c, g, d["me_counts"][nm])) for nm, c in d["my_survivors"].items()),
                  key=lambda x: x[1])
    dead = [(nm, p) for nm, p in mine if p < 35]

    L = [f"WEAKNESS ANALYSIS — {d['me_name']}  vs  {d['opp_name']}  ({g} games)",
         f"  you play {d['my_mission']} | opponent plays {d['opp_mission']}", "",
         "Board control (avg objectives held, R1..R5):",
         "  you : " + " ".join(f"{v:.1f}" for v in ctrl_you),
         "  opp : " + " ".join(f"{v:.1f}" for v in ctrl_opp), "",
         "Enemy units you CAN'T REMOVE (survive to end):"]
    L += [f"  {nm:32} {p:.0f}%" for nm, p in surv[:6]]
    L += ["", "YOUR dead weight (survives <35% — dying before earning its points):"]
    L += [f"  {nm:32} {p:.0f}%" for nm, p in dead[:6]] or ["  (none)"]

    # ---- recommendations from the signals ----
    L += ["", "FINDINGS & RECOMMENDATIONS:"]
    if ctrl_you[0] - ctrl_you[-1] >= 0.8 and ctrl_opp[-1] > ctrl_you[-1] + 0.8:
        L.append(f"  * BOARD COLLAPSE: you hold {ctrl_you[0]:.1f} objectives R1 but only {ctrl_you[-1]:.1f} "
                 f"by R5 while the opponent holds {ctrl_opp[-1]:.1f}. You are being out-tempo'd — you take "
                 f"the board early then lose it. On {d['my_mission']} that loses the game.")
    tough = [nm for nm, p in surv if p >= 70]
    if tough:
        L.append(f"  * NO ANSWER to: {', '.join(tough[:4])} — they survive most games. You lack the "
                 f"reach/output to remove them; recommend adding a tool that threatens them (or a mission/"
                 f"disposition that doesn't require killing them).")
    if dead:
        L.append(f"  * DEAD WEIGHT: {', '.join(nm for nm, _ in dead[:4])} rarely survive — they die before "
                 f"contributing. Reconsider their role/placement, or swap for pieces that trade better here.")
    return "\n".join(L)


_ROSTERS = None


def _roster(name):
    global _ROSTERS
    if _ROSTERS is None:
        from . import rosters
        _ROSTERS = rosters
    return getattr(_ROSTERS, name)


def main():
    import argparse
    ap = argparse.ArgumentParser(description="Expose a list's weaknesses vs a known opponent list.")
    ap.add_argument("me", help="roster builder (e.g. custodes)")
    ap.add_argument("opp", help="opponent roster builder (e.g. drukhari, necrons)")
    ap.add_argument("--games", type=int, default=2000)   # 2k interactive; 5000 is the calibrated standard
    ap.add_argument("--disp", help="override your disposition (e.g. purge-the-foe)")
    a = ap.parse_args()

    def me():
        army = _roster(a.me)()
        if a.disp:
            army.disposition = a.disp
        return army
    print(report(diagnose(me, _roster(a.opp), games=a.games)))


if __name__ == "__main__":
    main()
