# -*- coding: utf-8 -*-
"""mc_custodes_sim.py — DATA-DRIVEN Monte-Carlo for the Meta Slayers' "The Better Thing 2"
(Adeptus Custodes, Shield Host + Tharanatoi Hammerblow, disposition = PRIORITY ASSETS).

This is the REBUILT sim: it scores the REAL 11E missions (tools/missions.py, from data/*.yaml), not a
stand-in. Each game:
  * FIRST-TURN ROLL-OFF: D6 each, higher chooses to go first (nudges the early control curve).
  * MISSIONS ARE ASYMMETRIC: Custodes' disposition (Priority Assets) is fixed; each opponent's
    disposition is taken from REAL list data (data/listhammer_archive.json). Custodes plays
    matrix[priority-assets][opp]; the opponent plays matrix[opp][priority-assets] — usually different.
  * PRIMARY: missions.score_primary(mission, Caps(action_p, kill_p, control[r], enemy_home_p)); the
    Custodes caps are the validated capability table below; opponent caps model their board game.
  * SECONDARY: a 40VP layer (Custodes has strong action/assassination/board potential; matchup-scaled).
  * The MELEE ENGINE is computed from REAL profiles (best-of-Sustained/Lethal with crit-on-5 from
    Martial Mastery, MELEE ONLY; Assemblage +1-wound on the LED BRICKS / solo characters only, NOT the
    standalone Allarus; Allarus add Slayers of Tyrants). It's shown per matchup and sanity-checks kill_p.

  PYTHONPATH=tools:src python3 tools/mc_custodes_sim.py [--games 2000] [--seed 11]
"""
import argparse
import db, sim_game
from wh.mathhammer import expected_damage as ed, Target, Mods

CU = "adeptus-custodes"
CRIT5 = dict(crit_hit=5)                         # Martial Mastery: unmodified melee 5+ = Critical Hit


def _variant(unit, wname, ability):
    w = dict(db.weapon(CU, unit, wname))
    w["abilities"] = list(w.get("abilities") or w.get("keywords") or []) + [ability]
    return w


def best_stance(unit, wname, target, extra):
    """max(Dacatarai[SUSTAINED], Rendax[LETHAL]) with crit-on-5, MELEE — the per-unit best stance."""
    sus = _variant(unit, wname, "SUSTAINED HITS 1")
    leth = _variant(unit, wname, "LETHAL HITS")
    m = Mods(crit_hit=5, **{k: v for k, v in extra.items()})
    return max(ed(sus, target, m), ed(leth, target, m))


def hammer(target):
    """The committed melee into the marked priority target: one LED BRICK (5 Guardian spears, +1-wound
    Assemblage since a led brick is a CHARACTER unit per 19.01) + the standalone ALLARUS (5 spears, NO
    Assemblage, but Slayers of Tyrants re-roll wounds vs CHAR/MON/VEH). crit-5 on all (Martial Mastery)."""
    mv = any(k in target.keywords for k in ("VEHICLE", "MONSTER", "CHARACTER", "TITANIC"))
    brick = 5 * best_stance("Custodian Guard", "Guardian spear", target, dict(wound=1))
    allarus_extra = dict(reroll_wounds="fails") if mv else {}
    allarus = 5 * best_stance("Allarus Custodians", "Guardian spear", target, allarus_extra)
    return (brick + allarus) * 1.12                # + the attached characters' own attacks


def T(t, sv, w_, inv=None, models=1, kws=("INFANTRY",)):
    return Target(toughness=t, save=sv, wounds=w_, invuln=inv, models=models, keywords=tuple(kws))


# Custodes disposition is PRIORITY ASSETS. Each opponent's disposition is from listhammer_archive.json
# (the real stated disposition of the representative meta list). cust/opp = validated capability caps.
# opp caps are matchup-reflective: control is ANTI-CORRELATED with Custodes' (contested board sums
# to ~5), and opp kill_p is kept LOW because Custodes' 2+/4++/FNP wall is hard to shift off a point
# (a genuine Custodes edge) — higher only for the real alpha-strike / rail matchups.
ARCH = {
  "Emperor's Children (Coterie/Frenzied)": dict(prev=9, disp="purge-the-foe", verdict="FAV",
     cust=dict(action=.85, kill=.82, ctrl=2.5, home=.55), opp=dict(action=.70, kill=.45, ctrl=1.9, home=.30),
     tgt=T(11, "3+", 18, "5+", 1, ("VEHICLE", "MONSTER"))),
  "Orks (Green Tide horde)": dict(prev=8, disp="take-and-hold", verdict="UNFAV", horde=True,
     cust=dict(action=.75, kill=.85, ctrl=1.8, home=.0), opp=dict(action=.74, kill=.50, ctrl=3.0, home=.25),
     tgt=T(5, "6+", 1, None, 20, ("INFANTRY",))),
  "AdMech (Rad-Zone gunline)": dict(prev=6, disp="priority-assets", verdict="FAV",
     cust=dict(action=.82, kill=.78, ctrl=2.5, home=.0), opp=dict(action=.72, kill=.50, ctrl=1.8, home=.20),
     tgt=T(7, "3+", 3, None, 6, ("INFANTRY",))),
  "T'au (Retaliation alpha)": dict(prev=5, disp="purge-the-foe", verdict="COIN",
     cust=dict(action=.80, kill=.72, ctrl=2.4, home=.45), opp=dict(action=.70, kill=.58, ctrl=2.1, home=.28),
     tgt=T(9, "2+", 14, "4+", 1, ("VEHICLE", "MONSTER"))),
  "Necrons (Awakened Dynasty)": dict(prev=4, disp="take-and-hold", verdict="COIN",
     cust=dict(action=.85, kill=.62, ctrl=2.0, home=.0), opp=dict(action=.74, kill=.52, ctrl=2.6, home=.25),
     tgt=T(12, "4+", 10, "4+", 1, ("VEHICLE", "MONSTER"))),
  "Custodes (the MIRROR)": dict(prev=4, disp="take-and-hold", verdict="EVEN",
     cust=dict(action=.85, kill=.60, ctrl=2.4, home=.0), opp=dict(action=.85, kill=.60, ctrl=2.4, home=.25),
     tgt=T(6, "2+", 3, "4+", 5, ("INFANTRY", "CHARACTER"))),
  "Blood Angels (jump alpha)": dict(prev=4, disp="take-and-hold", verdict="FAV",
     # BA kill weight of attacks (volume) actually shifts Custodes bodies -> higher opp kill + control
     cust=dict(action=.82, kill=.82, ctrl=2.4, home=.0), opp=dict(action=.70, kill=.66, ctrl=2.15, home=.28),
     tgt=T(4, "3+", 2, None, 10, ("INFANTRY",))),
  "Dark Angels (Deathwing)": dict(prev=3, disp="priority-assets", verdict="COIN",
     cust=dict(action=.85, kill=.65, ctrl=2.4, home=.0), opp=dict(action=.74, kill=.52, ctrl=2.3, home=.25),
     tgt=T(5, "2+", 3, "4+", 5, ("INFANTRY",))),
  "Drukhari (Skysplinter)": dict(prev=3, disp="reconnaissance", verdict="FAV",
     cust=dict(action=.85, kill=.82, ctrl=2.5, home=.42), opp=dict(action=.76, kill=.55, ctrl=2.0, home=.28),
     tgt=T(8, "4+", 11, "5+", 1, ("VEHICLE",))),
  "Astra Militarum (superheavy)": dict(prev=2, disp="priority-assets", verdict="FAV",
     cust=dict(action=.85, kill=.75, ctrl=2.6, home=.0), opp=dict(action=.70, kill=.55, ctrl=1.8, home=.22),
     tgt=T(13, "2+", 24, None, 1, ("VEHICLE", "TITANIC"))),
}


MY_DISP = "priority-assets"                     # Custodes list disposition (stated on the list)


def results(games=10000, seed=11):
    """Thin adapter over the shared sim_game engine: adds the melee-hammer display column + Custodes'
    slight secondary edge (fast pieces + Sisters). Field names preserved for gen_custodes."""
    base = sim_game.results(ARCH, MY_DISP, games, seed, cust_sec=1.02)
    out = []
    for x, (name, spec) in zip(base, ARCH.items()):
        tgt = spec["tgt"]
        out.append(dict(name=x["name"], prev=x["prev"], verdict=spec["verdict"], disp=x["disp"],
                        cu_mission=x["mission"], op_mission=x["opp_mission"],
                        hammer=round(hammer(tgt)), tgtW=tgt.wounds, win=x["win"]))
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--games", type=int, default=2000)
    ap.add_argument("--seed", type=int, default=11)
    a = ap.parse_args()
    print(f"# THE BETTER THING 2 (Custodes, PRIORITY ASSETS) — {a.games} games/archetype. "
          f"Real missions via tools/missions.py; melee from data/bsdata.\n")
    hdr = (f"{'Archetype':34} {'prev':>4} {'oppDisp':>14} {'Custodes mission':>18} {'hammer':>7} "
           f"{'tgtW':>4} {'win%':>5}")
    print(hdr); print("-" * len(hdr))
    tot = wsum = 0
    for x in results(a.games, a.seed):
        print(f"{x['name']:34} {x['prev']:>4} {x['disp']:>14} {x['cu_mission']:>18} "
              f"{x['hammer']:>7} {x['tgtW']:>4} {x['win']:>4}%")
        tot += x["prev"]; wsum += x["prev"] * x["win"]
    print("-" * len(hdr))
    print(f"# prevalence-weighted Custodes win rate: {wsum/tot:.0f}%  "
          f"(asymmetric real missions; the horde control-crater is the one structural hole).")


if __name__ == "__main__":
    main()
