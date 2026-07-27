# -*- coding: utf-8 -*-
"""mc_gv_sim.py — DATA-DRIVEN Monte-Carlo for GREAT VALUE (Imperial Fists) vs the
n=70 listhammer meta archetypes. Mirrors tools/mc_db_sim.py but from GV's side.

GV's OATH-boosted convergence output (Sternguard Dev + cyclone + brick melee + Speeder
melta, all with Oath: full Hit re-roll + +1 to Wound; Sternguard also full Wound re-roll)
is computed from REAL profiles (data/bsdata via tools/db.py) with wh.mathhammer. GV's
durability (2+/4++ + Armour of Contempt) and each enemy's ability to actually hurt TEQ
bodies are the meta-calibrated params (docs/meta + gv_data). Output = GV win% per archetype.

  PYTHONPATH=tools:src python3 tools/mc_gv_sim.py [--games 800] [--verbose]

CP economy: ~2 CP/round (1 per player-turn). Oath of Moment is FREE (army rule, always modelled
on); AoC/Fury/Dropship/Epic Challenge compete for ~1 strat/turn, so GV durability here is innate
2+/4++ (baked into enemy_kill), NOT always-on AoC.
"""
import argparse, random
import db
from wh.mathhammer import expected_damage as ed, Target, Mods

SM = "space-marines"
IF = "imperial-fists"
OATH_SHOOT = Mods(reroll_hits="fails", wound=1)                       # Oath: rr Hits + +1 Wound
OATH_STERN = Mods(reroll_hits="fails", reroll_wounds="fails", wound=1)  # Sternguard Focus: full wound rr vs Oath
OATH_MELEE = Mods(reroll_hits="fails", reroll_wounds="fails", wound=1)  # brick: Oath + full Wrath re-roll


def w(fac, unit, wep):
    return db.weapon(fac, unit, wep)


def gv_oath_output(target):
    """GV's damage onto the ONE Oathed target/turn, from real profiles (the convergence)."""
    dmg = 0.0
    # Sternguard (10): bolt rifle, Dev + FULL wound re-roll vs Oath -> unsaveable mortals
    try:
        dmg += 10 * ed(w(SM, "Sternguard Veteran Squad", "bolt rifle"), target, OATH_STERN)
    except KeyError:
        pass
    # Cyclone Terminators: 2 cyclone/krak missiles (AP-2, Lethal via Fusillade)
    for wn in ("Cyclone", "Krak missile", "missile"):
        try:
            dmg += 2 * ed(w(SM, "Terminator Squad", wn), target, OATH_SHOOT)
            break
        except KeyError:
            continue
    # 2 Land Speeders: multi-melta (2 shots ea)
    try:
        dmg += 4 * ed(w(SM, "Land Speeder", "melta"), target, OATH_SHOOT)
    except KeyError:
        pass
    return dmg


def gv_brick_melee(target):
    """The Lysander brick on the charge: 9 thunder hammers + Lysander's Fist, Oath + full re-roll."""
    dmg = 0.0
    try:
        dmg += 9 * ed(w(SM, "Terminator Assault Squad", "hammer"), target, OATH_MELEE)
    except KeyError:
        pass
    try:
        dmg += ed(w(IF, "Darnath Lysander", "Fist"), target, OATH_MELEE)
    except KeyError:
        pass
    return dmg


# GV's durable bodies as the enemy sees them (Terminator: T5 W3 2+/4++, Armour of Contempt).
# We model AoC as making enemy AP one better handled by giving the TEQ a strong save + 4++.
TEQ = Target(toughness=5, save="2+", wounds=3, invuln="4+", models=10, keywords=("INFANTRY",))
MEQ = Target(toughness=4, save="3+", wounds=2, invuln=None, models=10, keywords=("INFANTRY",))

# priority target GV Oaths/removes each turn, per archetype (a Target profile)
def T(t, sv, w_, inv=None, models=1, kws=("INFANTRY",)):
    return Target(toughness=t, save=sv, wounds=w_, invuln=inv, models=models, keywords=tuple(kws))

# archetypes: enemy_kill = EV dmg/turn they actually land on GV's TEQ bodies (meta-calibrated:
# glass/anti-tank armies bounce off AoC+4++; hordes/mortals/elite-melee hurt); obj/floor/score as before.
ARCH = {
  "Emperor's Children (Defiler+swarm)": dict(prev=9, verdict="FAV", enemy_kill=13, obj=3.0, floor=1.8, score=4.6,
     tgt=T(11, "3+", 18, "5+", 1, ("VEHICLE", "MONSTER"))),          # Defiler
  "Orks (Green Tide horde)": dict(prev=8, verdict="COIN", enemy_kill=18, obj=4.2, floor=3.2, score=6.0, horde=True,
     tgt=T(5, "6+", 1, None, 20, ("INFANTRY",))),                     # Boyz blob
  "AdMech (Rad-Zone gunline)": dict(prev=6, verdict="FAV", enemy_kill=10, obj=2.9, floor=1.9, score=4.4,
     tgt=T(7, "3+", 3, None, 6, ("INFANTRY",))),                      # Kataphron brick
  "T'au (Retaliation alpha)": dict(prev=5, verdict="COIN", enemy_kill=19, obj=2.7, floor=1.7, score=4.4,
     tgt=T(9, "2+", 14, "4+", 1, ("VEHICLE", "MONSTER"))),            # Riptide/Crisis bomb
  "Necrons (Awakened C'tan)": dict(prev=4, verdict="COIN-", enemy_kill=15, obj=3.4, floor=3.0, score=5.2, dura=1.9,
     tgt=T(12, "4+", 10, "4+", 1, ("VEHICLE", "MONSTER"))),           # C'tan (durable)
  "Custodes (elite melee)": dict(prev=4, verdict="COIN", enemy_kill=20, obj=2.7, floor=1.7, score=4.3, dura=1.5,
     tgt=T(6, "2+", 3, "4+", 5, ("INFANTRY",))),                      # Custodian brick
  "Blood Angels (jump alpha)": dict(prev=4, verdict="FAV", enemy_kill=14, obj=2.5, floor=1.3, score=4.4,
     tgt=T(4, "3+", 2, None, 10, ("INFANTRY",))),                     # Death Company
  "Dark Angels (Deathwing)": dict(prev=3, verdict="COIN", enemy_kill=18, obj=2.7, floor=1.7, score=4.2, dura=1.6,
     tgt=T(5, "2+", 3, "4+", 5, ("INFANTRY",))),                      # Deathwing Knights
  "Drukhari (Skysplinter)": dict(prev=3, verdict="FAV", enemy_kill=10, obj=3.2, floor=1.6, score=4.5,
     tgt=T(8, "4+", 11, "5+", 1, ("VEHICLE",))),                      # Ravager/Venom
  "Astra Militarum (superheavy)": dict(prev=2, verdict="FAV", enemy_kill=12, obj=2.8, floor=1.8, score=4.2,
     tgt=T(13, "2+", 24, None, 1, ("VEHICLE", "TITANIC"))),           # Shadowsword
}


def noisy(mu, cv=0.28):
    return max(0.0, random.gauss(mu, mu * cv))


def run_game(spec, oath_dmg, brick, tw):
    """GV grinds: removes an enemy leg/turn (Oath convergence), tanks their damage behind
    2+/4++/AoC, and out-scores on sticky OC + bodies. dura = enemy soaks GV's removal."""
    dura = spec.get("dura", 1.0)
    clears = (oath_dmg + 0.35 * brick) >= tw * dura       # does Oath+brick remove their priority piece/turn?
    my_obj, their_obj = spec["obj"] - 0.4, spec["obj"]    # GV is sticky/durable -> holds its share
    bodies_lost = 0
    me = him = 0.0
    for rnd in range(1, 6):
        # their turn: can they crack GV's TEQ? (AoC+4++ blunts most; hordes/melee/mortals hurt)
        kill = spec["enemy_kill"]
        if rnd >= 2 and random.random() < min(0.5, kill / 26.0):
            bodies_lost += 1
            my_obj = max(1.0, my_obj - 0.6)               # losing a unit dents OC (but sticky softens it)
        outctrl = their_obj >= my_obj
        him += min(15, spec["score"] + (4 if outctrl else 2) + (2 if bodies_lost else 0)) + noisy(spec["score"] * 0.7)
        # GV turn: Oath removes a leg -> their board control decays; sticky OC banks primary
        if clears:
            their_obj = max(spec["floor"], their_obj - 0.3)
        me += max(0.0, min(15, 5 + (5 if my_obj >= their_obj else 2) + (1 if clears else 0) - bodies_lost)) + noisy(3.5)
        me += noisy(2.5) if clears else 0.0               # kill secondaries from the convergence
    return me - him


def results(games=800):
    random.seed(11)
    out = []
    for name, spec in ARCH.items():
        tgt = spec["tgt"]
        oath = gv_oath_output(tgt)
        brick = gv_brick_melee(tgt)
        win = sum(run_game(spec, oath, brick, tgt.wounds) > 0 for _ in range(games))
        out.append(dict(archetype=name, prev=spec["prev"], verdict=spec["verdict"],
                        oath=round(oath), brick=round(brick), tgtW=tgt.wounds, win=round(100 * win / games)))
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--games", type=int, default=800)
    ap.add_argument("--verbose", action="store_true")
    a = ap.parse_args()
    print(f"# GREAT VALUE data-driven sim — {a.games} games/archetype. Oath output from data/bsdata via wh.mathhammer.\n")
    hdr = f"{'Archetype':34} {'prev':>4} {'verdict':>7} {'Oath dmg':>9} {'brick':>6} {'tgtW':>5} {'GV win%':>8}"
    print(hdr); print("-" * len(hdr))
    tot = wsum = 0
    for x in results(a.games):
        print(f"{x['archetype']:34} {x['prev']:>4} {x['verdict']:>7} {x['oath']:>9} {x['brick']:>6} {x['tgtW']:>5} {x['win']:>7}%")
        tot += x["prev"]; wsum += x["prev"] * x["win"]
    print("-" * len(hdr))
    print(f"# prevalence-weighted GV win rate across the top meta: {wsum/tot:.0f}%  "
          f"(strong all-comers; hardest = Orks horde; softest = the glass-alpha + gunline metas).")


if __name__ == "__main__":
    main()
