"""Monte-Carlo driver: play N full positional games between two rosters and report the win rate.
Each game rebuilds fresh rosters, rolls off for first turn, resolves 5 rounds of dice combat over the
real board + objectives, scores the real missions, and compares total VP."""
from __future__ import annotations

import time
import numpy as np

from .entities import Board
from .mission import pairing
from .game import play_game
from . import terrain, deployments


def simulate(build_me, build_opp, games=2000, seed=11, verbose=False):
    rng = np.random.default_rng(seed)
    wins = 0
    my_vp = opp_vp = 0.0
    t0 = time.time()
    a0, b0 = build_me(), build_opp()
    my_mission, opp_mission = pairing(a0.disposition, b0.disposition)
    dep = deployments.for_mission(my_mission)               # deployment map from the mission (from dispositions)
    for g in range(games):
        me = build_me(); opp = build_opp()
        board = Board(deployment=dep)
        first = "A" if rng.random() < 0.5 else "B"
        vp = play_game(me, opp, my_mission, opp_mission, board, rng, first=first)
        my_vp += vp["A"]; opp_vp += vp["B"]
        wins += vp["A"] > vp["B"]
    dt = time.time() - t0
    res = dict(win=round(100 * wins / games), my_vp=round(my_vp / games, 1), opp_vp=round(opp_vp / games, 1),
               my_mission=my_mission, opp_mission=opp_mission, games=games, secs=round(dt, 1))
    if verbose:
        print(f"{me.name} ({a0.disposition}) vs {opp.name} ({b0.disposition})")
        print(f"  you play {my_mission} | opp plays {opp_mission}")
        print(f"  WIN {res['win']}%  (VP {res['my_vp']} vs {res['opp_vp']})  "
              f"[{games} games, {dt:.1f}s = {1000*dt/games:.1f}ms/game]")
    return res
