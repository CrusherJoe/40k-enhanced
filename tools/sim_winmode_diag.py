#!/usr/bin/env python3
"""sim_winmode_diag.py — WHY each Custodes matchup is won/lost: tabled vs OUTSCORED,
avg VP, per-side casualties. Diagnostic behind the combat-model finding (2026-08-06): every
anchor is decided on VP/scoring, not tabling — combat dice are correct; the residual is
mobility/board-control + un-crackable durable centrepieces, NOT a damage bug. Run:
  PYTHONPATH=src python3 tools/sim_winmode_diag.py
"""
import numpy as np, collections
from wh.sim import run, rosters, game
from wh.sim.entities import Board
from wh.sim.mission import pairing, score_turn, end_of_battle
from wh.sim import deployments, secondaries as _sec, attach as _att, strategy as _strat

def diag(opp_name, games=120, seed=7):
    build_me, build_opp = rosters.custodes, getattr(rosters, opp_name)
    rng = np.random.default_rng(seed)
    a0,b0 = build_me(), build_opp()
    mA,mB = pairing(a0.disposition,b0.disposition)
    dep = deployments.for_mission(mA)
    tabled_win=tabled_loss=score_win=score_loss=0
    myvp=oppvp=0.0
    me_dead_by5=opp_dead_by5=0
    for g in range(games):
        me=build_me(); opp=build_opp()
        board=Board(deployment=dep)
        first="A" if rng.random()<0.5 else "B"
        vp=game.play_game(me,opp,mA,mB,board,rng,first=first)
        myvp+=vp["A"]; oppvp+=vp["B"]
        me_alive=sum(1 for u in me.units if u.alive)
        opp_alive=sum(1 for u in opp.units if u.alive)
        me_dead_by5 += (me_alive==0); opp_dead_by5 += (opp_alive==0)
        win = vp["A"]>vp["B"]
        if win and opp_alive==0: tabled_win+=1
        elif win: score_win+=1
        elif me_alive==0: tabled_loss+=1
        else: score_loss+=1
    n=games
    print(f"=== Custodes vs {opp_name} ({n} games) ===")
    print(f"  win% {round(100*(tabled_win+score_win)/n)}  | avg VP {myvp/n:.1f} vs {oppvp/n:.1f}")
    print(f"  WINS: by tabling {tabled_win}  by score {score_win}")
    print(f"  LOSS: opp tabled me {tabled_loss}  outscored {score_loss}")
    print(f"  games I got TABLED: {me_dead_by5}/{n} ({round(100*me_dead_by5/n)}%) | I TABLED opp: {opp_dead_by5}/{n} ({round(100*opp_dead_by5/n)}%)")

for o in ("blood_angels","orks","aeldari","tau","tyranids"):
    diag(o)
