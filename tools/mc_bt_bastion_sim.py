# -*- coding: utf-8 -*-
"""mc_bt_bastion_sim.py — DATA-DRIVEN Monte-Carlo for the friend's BLACK TEMPLARS "Templar Bastion"
list (Bastion Task Force detachment) vs the LSO-meta archetypes, from BT's side.

This is a DIFFERENT army than the delivered-spike list (mc_bt_sim.py): it's a durable, objective-
holding, auspex-CONTROL grinder — so it's modelled on the durable-grind template (mc_gv_sim.py),
NOT the delivery-dependent one. Its removal is RELIABLE (guns shoot regardless; no bus to strand).

Verified mechanics baked in:
  * Templar Vow = ACCEPT ANY CHALLENGE: +1 to Wound in melee when S <= target's T (helps wound UP).
  * Interlocking Tactics: Battleline units auspex-scan -> army re-rolls Hit rolls of 1 vs the scan.
  * Repulsor Executioner INTERCEPTION STRIKE: full Hit re-roll vs a target within 12" of a friendly
    Astartes unit (~always on in a brick list) -> reliable ranged removal (2x Heavy Laser Destroyer
    + gatling + multi-melta).
  * Sword Brethren brick = crit-on-5 (Marshal Inspirational Exemplar) + [LETHAL HITS] + Castellan
    re-roll + Accept vow + 2 thunder hammers (Dev); Hero of the Chapter makes it Battleline so
    Light of Vengeance can add [SUSTAINED HITS 1]. The anti-tank/anti-elite melee (NO Slayers +2S
    here — that's Marshal's Household, not Bastion).
  * Durability: brick bodies + Angels Defiant (-1 to Wound vs S>T) + Grimaldus's +1 T / +1 AP relic.
    Grimaldus FNP is HIM + Cenobyte Servitors only (not the brick).
  * Debuff toolkit: Guided Disruption (pin: -2 M/-2 charge) + Shock Bombardment (suppress: -1 hit)
    blunt melee/alpha enemies.

  PYTHONPATH=tools:src python3 tools/mc_bt_bastion_sim.py [--games 800] [--verbose]
"""
import argparse, random
import db
from wh.mathhammer import expected_damage as ed, Target, Mods

SM = "space-marines"; BT = "black-templars"
RR = Mods(reroll_hits="fails")                                   # Interception Strike / auspex / Grimaldus re-roll
MELEE = Mods(reroll_hits="fails", crit_hit=5)                    # crit-on-5 (Inspirational Exemplar) + re-roll (Vehement/Litanies)
MELEE_VOW = Mods(reroll_hits="fails", crit_hit=5, wound=1)       # + Accept Any Challenge when S <= T


def _w(fac, unit, wep):
    for f in (fac, SM if fac == BT else BT):
        try:
            return db.weapon(f, unit, wep)
        except Exception:
            continue
    raise KeyError(wep)


def bastion_shoot(target):
    """The RELIABLE Interception-Strike gun package (2 Repulsor Executioners) onto one target."""
    dmg = 0.0
    mv = ("VEHICLE" in target.keywords) or ("MONSTER" in target.keywords) or ("TITANIC" in target.keywords)
    if mv:
        try: dmg += 4 * ed(_w(SM, "Repulsor Executioner", "laser destroyer"), target, RR)   # 2x2 HLD, full re-roll
        except KeyError: pass
        try: dmg += 2 * ed(_w(BT, "Repulsor Executioner", "melta"), target, RR)              # 2 multi-melta
        except KeyError: pass
    else:
        try: dmg += 2 * ed(_w(SM, "Repulsor Executioner", "gatling"), target, RR)            # 2 gatling (A12, Dev) vs infantry
        except KeyError: pass
    return dmg


def bastion_melee(target):
    """The Sword Brethren crit-5 brick (+ EC/AI support) onto the priority target. Accept vow adds +1
    to wound when S <= T; thunder hammers add Dev-wound spikes."""
    dmg = 0.0
    try:
        w = _w(BT, "Sword Brethren Squad", "power weapon")          # S5 AP-2 D2 A3 [LETHAL HITS]
        mods = MELEE_VOW if int(w["S"]) <= target.toughness else MELEE
        dmg += 6 * ed(w, target, mods)                             # ~6 power weapons
    except KeyError:
        pass
    try:
        th = _w(BT, "Sword Brethren Squad", "hammer")              # thunder hammer S8 AP-2 D2 [DEV]
        mods = MELEE_VOW if int(th["S"]) <= target.toughness else MELEE
        dmg += 2 * ed(th, target, mods)
    except KeyError:
        pass
    dmg *= 1.25                                                    # Marshal/Castellan attacks + Light of Vengeance Sustained
    return dmg


def T(t, sv, w_, inv=None, models=1, kws=("INFANTRY",)):
    return Target(toughness=t, save=sv, wounds=w_, invuln=inv, models=models, keywords=tuple(kws))


# enemy_kill = EV dmg/turn into BT's bricks (already blunted by Angels Defiant + relic +1 T + bodies);
# obj = enemy board control; fast = out-manoeuvres the slow bricks; horde = out-bodies; melee = the
# pin/suppress toolkit blunts them extra (-2 M/-2 charge, -1 hit); dura = enemy soaks BT's removal.
ARCH = {
  "Emperor's Children (Defiler+swarm)": dict(prev=9, verdict="FAV", enemy_kill=12, obj=3.0, floor=1.8, score=4.6,
     melee=True, tgt=T(11, "3+", 18, "5+", 1, ("VEHICLE", "MONSTER"))),
  "Orks (Green Tide horde)": dict(prev=8, verdict="UNFAV", enemy_kill=16, obj=3.6, floor=2.6, score=5.4, horde=True,
     tgt=T(5, "6+", 1, None, 20, ("INFANTRY",))),
  "AdMech (Rad-Zone gunline)": dict(prev=6, verdict="FAV", enemy_kill=12, obj=2.9, floor=1.8, score=4.4,
     tgt=T(7, "3+", 3, None, 6, ("VEHICLE",))),
  "T'au (Retaliation alpha)": dict(prev=5, verdict="COIN", enemy_kill=17, obj=2.9, floor=1.8, score=4.7,
     tgt=T(9, "2+", 14, "4+", 1, ("VEHICLE", "MONSTER"))),
  "Necrons (Awakened C'tan)": dict(prev=4, verdict="COIN", enemy_kill=14, obj=3.4, floor=2.4, score=5.0, dura=1.6,
     tgt=T(12, "4+", 10, "4+", 1, ("VEHICLE", "MONSTER"))),
  "Custodes (elite melee)": dict(prev=4, verdict="COIN", enemy_kill=20, obj=2.7, floor=1.7, score=4.4, dura=1.4,
     melee=True, tgt=T(6, "2+", 3, "4+", 5, ("INFANTRY",))),
  "Blood Angels (jump alpha)": dict(prev=4, verdict="FAV", enemy_kill=15, obj=2.6, floor=1.6, score=4.6,
     melee=True, tgt=T(4, "3+", 2, None, 10, ("INFANTRY",))),
  "Dark Angels (Deathwing)": dict(prev=3, verdict="COIN", enemy_kill=19, obj=2.7, floor=1.7, score=4.3, dura=1.5,
     melee=True, tgt=T(5, "2+", 3, "4+", 5, ("INFANTRY",))),
  "Drukhari (Skysplinter)": dict(prev=3, verdict="UNFAV", enemy_kill=13, obj=3.2, floor=1.9, score=4.7, fast=True,
     tgt=T(8, "4+", 11, "5+", 1, ("VEHICLE",))),
  "Astra Militarum (superheavy)": dict(prev=2, verdict="FAV", enemy_kill=13, obj=2.8, floor=1.8, score=4.3,
     tgt=T(13, "2+", 24, None, 1, ("VEHICLE", "TITANIC"))),
}


def noisy(mu, cv=0.28):
    return max(0.0, random.gauss(mu, mu * cv))


def run_game(spec, shoot, melee, tw):
    """A durable hold-and-grind: reliable guns + a crit-5 melee brick remove the priority piece every
    turn (no delivery risk), the bricks hold objectives, and the pin/suppress toolkit blunts melee/alpha.
    Weaknesses: SLOW (fast enemies out-manoeuvre) and out-BODIED (hordes)."""
    dura = spec.get("dura", 1.0)
    # reliable removal: best of the guns (vs armour) or the melee brick (vs elites), both dependable
    removal = max(shoot, melee)
    clears = removal >= 0.75 * tw * dura
    # durable holder but SLOW (M6 foot bricks) -> it holds its share yet starts BEHIND the enemy's
    # contested board; fast enemies out-manoeuvre, hordes out-body. Removing legs only slowly claws back.
    their_obj = spec["obj"] + (0.6 if spec.get("fast") else 0.0) + (0.3 if spec.get("horde") else 0.0)
    # body_edge > 0 when BT OUT-bodies the opponent (e.g. vs a 5-model Knight army) -> BT starts ahead
    my_obj = spec["obj"] - 0.45 + spec.get("body_edge", 0.0)
    # the pin/suppress toolkit + Angels Defiant blunt melee/alpha pressure
    kill = spec["enemy_kill"] * (0.8 if spec.get("melee") else 1.0)
    bodies_lost = 0
    me = him = 0.0
    for rnd in range(1, 6):
        if rnd >= 2 and random.random() < min(0.5, kill / 28.0):
            bodies_lost += 1
            my_obj = max(1.0, my_obj - 0.4)
        outctrl = their_obj >= my_obj
        him += min(15, spec["score"] + (4 if outctrl else 2) + (2 if bodies_lost else 0)) + noisy(spec["score"] * 0.7)
        if clears:
            their_obj = max(spec["floor"], their_obj - 0.25)
        me += max(0.0, min(15, 5 + (5 if my_obj >= their_obj else 2) + (1 if clears else 0) - bodies_lost)) + noisy(3.5)
        me += noisy(2.2) if clears else 0.0
    return me - him


def results(games=800):
    random.seed(11)
    out = []
    for name, spec in ARCH.items():
        tgt = spec["tgt"]
        shoot = bastion_shoot(tgt); melee = bastion_melee(tgt)
        win = sum(run_game(spec, shoot, melee, tgt.wounds) > 0 for _ in range(games))
        out.append(dict(archetype=name, prev=spec["prev"], verdict=spec["verdict"],
                        shoot=round(shoot), melee=round(melee), tgtW=tgt.wounds, win=round(100 * win / games)))
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--games", type=int, default=800)
    ap.add_argument("--verbose", action="store_true")
    a = ap.parse_args()
    print(f"# TEMPLAR BASTION (Black Templars, Bastion Task Force) sim — {a.games} games/archetype. From data/bsdata via wh.mathhammer.\n")
    hdr = f"{'Archetype':34} {'prev':>4} {'verdict':>7} {'guns':>5} {'melee':>6} {'tgtW':>5} {'BT win%':>8}"
    print(hdr); print("-" * len(hdr))
    tot = wsum = 0
    for x in results(a.games):
        print(f"{x['archetype']:34} {x['prev']:>4} {x['verdict']:>7} {x['shoot']:>5} {x['melee']:>6} {x['tgtW']:>5} {x['win']:>7}%")
        tot += x["prev"]; wsum += x["prev"] * x["win"]
    print("-" * len(hdr))
    print(f"# prevalence-weighted BT-Bastion win rate: {wsum/tot:.0f}%  "
          f"(durable hold-and-grind — reliable guns + crit-5 melee, no delivery risk; slow, out-bodied by hordes).")


if __name__ == "__main__":
    main()
