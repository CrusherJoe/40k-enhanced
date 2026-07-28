# -*- coding: utf-8 -*-
"""sim_game.py — the shared REAL-MISSION game loop for every list's Monte-Carlo sim.

Extracted from the Custodes rebuild so GV / BT / BT-Bastion / Custodes all score the SAME way: the
11E missions from tools/missions.py (your Force Disposition is fixed per list; each opponent's is the
real stated disposition of the meta archetype; the matrix hands each side its — usually different —
mission). Each sim supplies only its data:

  MY_DISPOSITION = "take-and-hold" | "purge-the-foe" | "priority-assets" | "reconnaissance" | "disruption"
  ARCH = { "<archetype>": dict(prev=<meta weight>, disp="<opp disposition>",
                               cust=dict(action=, kill=, ctrl=, home=),   # YOUR capability caps
                               opp =dict(action=, kill=, ctrl=, home=),   # the opponent's
                               horde=<bool, optional>), ... }
  results(ARCH, MY_DISPOSITION)  ->  [dict(name, prev, disp, mission, opp_mission, win), ...]

Capabilities (all in [0,1] except ctrl = expected # objectives at the round's peak):
  action_p  P(perform this mission's Objective Action this turn)   kill_p  P(kill an enemy near an obj)
  ctrl      peak objectives held (ramped over rounds)              home    P(hold opp home at end)
"""
import random
import missions
from missions import Caps

# Opponent Force Dispositions for the standard 10 meta archetypes, from real list data
# (data/listhammer_archive.json). Opponent property -> shared across every list's sim. A sim may
# override per-entry via the ARCH `disp` field; this dict is the canonical default by faction key.
OPP_DISP = {
    "emperors-children": "purge-the-foe", "orks": "take-and-hold", "adeptus-mechanicus": "priority-assets",
    "tau": "purge-the-foe", "necrons": "take-and-hold", "custodes": "take-and-hold",
    "blood-angels": "take-and-hold", "dark-angels": "priority-assets", "drukhari": "reconnaissance",
    "astra-militarum": "priority-assets",
}

DISP_NAME = {"take-and-hold": "Take and Hold", "purge-the-foe": "Purge the Foe",
             "reconnaissance": "Reconnaissance", "priority-assets": "Priority Assets",
             "disruption": "Disruption"}


def control_curve(peak, going_first):
    shape = [0.60, 0.95, 1.0, 1.0, 0.90]
    nudge = 0.12 if going_first else -0.06
    out = [0.0]
    for i, s in enumerate(shape):
        out.append(max(0.0, peak * s + (nudge if i < 2 else 0.0) + random.gauss(0, 0.28)))
    return out


def _secondary(base, factor):
    return max(0.0, min(40.0, random.gauss(base * factor, 6.5)))


def _play_side(mission_name, caps_dict, going_first, sec_base, sec_factor):
    caps = Caps(action_p=min(1, max(0, caps_dict["action"] + random.gauss(0, .05))),
                kill_p=min(1, max(0, caps_dict["kill"] + random.gauss(0, .05))),
                control=control_curve(caps_dict["ctrl"], going_first),
                enemy_home_p=caps_dict.get("home", 0.0))
    return missions.score_primary(mission_name, caps, going_first) + _secondary(sec_base, sec_factor)


def run_game(my_disp, spec, cust_sec=1.0):
    """One game: first-turn D6 roll-off, asymmetric primary for both sides, secondaries, 40k swing.
    cust_sec = your list's secondary-capability factor (fast/action-rich > 1; slow/few-bodies < 1);
    always cut vs a horde that denies actions/board."""
    while True:
        a, b = random.randint(1, 6), random.randint(1, 6)
        if a != b:
            break
    my_first = a > b
    my_mission, opp_mission = missions.pairing(my_disp, spec["disp"])
    horde = spec.get("horde", False)
    me = _play_side(my_mission, spec["cust"], my_first, 30, 0.84 if horde else cust_sec)
    opp = _play_side(opp_mission, spec["opp"], not my_first, 30, 1.0)
    # 40k game swing (dice / terrain / deployment / secondary draws / skill) — keeps favourites ~65-70%
    return (me - opp) + random.gauss(0, 15.0), my_mission, opp_mission


def results(arch, my_disp, games=6000, seed=11, cust_sec=1.0):
    random.seed(seed)
    out = []
    for name, spec in arch.items():
        wins = 0
        mm = om = ""
        for _ in range(games):
            d, mm, om = run_game(my_disp, spec, cust_sec)
            wins += d > 0
        out.append(dict(name=name, prev=spec["prev"], disp=spec["disp"],
                        mission=mm, opp_mission=om, win=round(100 * wins / games)))
    return out


def print_table(title, rows, my_disp):
    print(f"# {title} — disposition {DISP_NAME.get(my_disp, my_disp)}. Real missions via tools/missions.py.\n")
    hdr = f"{'Archetype':34} {'prev':>4} {'oppDisp':>15} {'you play':>20} {'win%':>5}"
    print(hdr); print("-" * len(hdr))
    tot = wsum = 0
    for x in rows:
        print(f"{x['name']:34} {x['prev']:>4} {DISP_NAME.get(x['disp'], x['disp']):>15} "
              f"{x['mission']:>20} {x['win']:>4}%")
        tot += x["prev"]; wsum += x["prev"] * x["win"]
    print("-" * len(hdr))
    print(f"# prevalence-weighted win rate: {wsum/tot:.0f}%")
    return round(wsum / tot)
