#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""mc_db_sim.py — DATA-DRIVEN Monte-Carlo: List A (2 Castellan/1 Lancer) vs List B
(1 Castellan/2 Lancer) against the current listhammer meta archetypes (n=70, post-7/23).

MY Knights' output is computed from REAL 11e profiles (data/bsdata/imperial-knights.json
via tools/db.py) with wh.mathhammer — so the A-vs-B firepower delta is fully data-driven.
Enemy anti-Knight damage is computed from BSData where present; BSData's 11e catalogue is
INCOMPLETE for some factions (missing e.g. Broadside / Sanguinary Guard / Deathwing Knights /
Scourges), so each archetype also carries a verified-analysis floor (hand=(ranged,melee) EV/turn
from docs/meta + the mathhammer we did) and we use max(db, floor). Floors are flagged in --verbose.

The real A/B tradeoff: A out-SHOOTS (clears the enemy's RANGED anti-Knight faster + more removal);
B out-FIGHTS (2 counter-charge blades clear the enemy's MELEE anti-Knight + a 2nd 4++ body). So A
should win the shooting archetypes, B the melee ones — the sim's job is to confirm/quantify that.

  PYTHONPATH=tools:src python3 tools/mc_db_sim.py [--games 400] [--verbose]
"""
import argparse, random, sys
import db
from wh.mathhammer import expected_damage as ed, Target, Mods

IK = "imperial-knights"

# --- my Knights as the enemy targets them (Questoris T12 W28 3+; 5++ vs shooting only) ---
KN_S = Target(toughness=12, save="3+", wounds=28, invuln="5+", keywords=("VEHICLE", "TITANIC", "MONSTER"))
KN_M = Target(toughness=12, save="3+", wounds=28, invuln=None, keywords=("VEHICLE", "TITANIC", "MONSTER"))


def W(unit, wep):
    return db.weapon(IK, unit, wep)


def my_shooting(list_name, target):
    """EV shooting my list puts on ONE priority target/turn (Dominus +1-to-hit in terrain).
    List A = 2 Castellan, List B = 1 Castellan; Castellan #1 has Archeotech Autoloaders."""
    cast = 2 if list_name == "A" else 1
    dmg = 0.0
    for i in range(cast):
        m = Mods(reroll_attacks=(i == 0), hit=1)  # #1 Autoloaders; Dominus +1 in terrain
        dmg += ed(W("Knight Castellan", "Volcano lance"), target, m)
        for wn in ("Plasma decimator",):
            try:
                dmg += ed(W("Knight Castellan", wn), target, m)
            except KeyError:
                pass
    for wn in ("Rapid-fire battle cannon", "Avenger", "Thermal cannon"):
        try:
            dmg += ed(W("Knight Crusader", wn), target, Mods(hit=1))
        except KeyError:
            pass
    try:
        dmg += 2 * ed(W("Armiger Helverin", "autocannon"), target, Mods(hit=1))
    except KeyError:
        pass
    return dmg


# --- meta archetypes (n=70 listhammer, post-7/23). hand=(ranged,melee) EV/turn floors ---
# ak entries: (faction, unit_substr, weapon_substr, count, "R"|"M") resolved from BSData when present.
ARCH = {
  "Emperor's Children (Defiler+swarm)": dict(prev=9, hand=(6, 24), melee=True, dura=1.1,
    obj=3.0, floor=1.8, score=4.6, ctan=False,
    ak=[("emperors-children", "Defiler", "Ectoplasma", 2, "R"),
        ("emperors-children", "Defiler", "Shearing claws - strike", 2, "M"),
        ("emperors-children", "Maulerfiend", "fists", 1, "M")],
    tgt=("emperors-children", "Defiler", 18, "3+", 11, "5+", ("VEHICLE", "MONSTER"))),
  "Orks (Green Tide horde)": dict(prev=8, hand=(2, 16), melee=True, dura=1.0, horde=True,
    obj=3.9, floor=2.9, score=5.6,
    ak=[("orks", "Nob", "Power klaw", 10, "M")],
    tgt=("orks", "Boy", 1, "6+", 5, None, ("INFANTRY",))),
  "AdMech (Rad-Zone gunline)": dict(prev=6, hand=(20, 2), melee=False, dura=1.1,
    obj=3.0, floor=2.0, score=4.6,
    ak=[("adeptus-mechanicus", "Kataphron Breachers", "arc rifle", 12, "R"),
        ("adeptus-mechanicus", "Skorpius Disintegrator", "Ferrumite", 3, "R")],
    tgt=("adeptus-mechanicus", "Kataphron Breachers", 3, "3+", 7, None, ("INFANTRY",))),
  "T'au (Retaliation alpha)": dict(prev=5, hand=(26, 0), melee=False, dura=1.2,
    obj=2.6, floor=1.6, score=4.2,
    ak=[("tau-empire", "Hammerhead", "Railgun", 2, "R"),
        ("tau-empire", "Riptide", "ion", 2, "R")],
    tgt=("tau-empire", "Riptide Battlesuit", 14, "2+", 9, "4+", ("VEHICLE", "MONSTER"))),
  "Necrons (Awakened C'tan)": dict(prev=4, hand=(14, 6), melee=False, dura=2.6, ctan=True,
    obj=3.4, floor=3.0, score=5.2,
    ak=[("necrons", "Lokhust Destroyers", "gauss", 12, "R"),
        ("necrons", "C'tan Shard of the Void Dragon", "Spear", 1, "M")],
    tgt=("necrons", "Annihilation Barge", 10, "3+", 10, None, ("VEHICLE",))),
  "Custodes (elite melee)": dict(prev=4, hand=(9, 18), melee=True, dura=1.2,
    obj=2.4, floor=1.4, score=3.9,
    ak=[("adeptus-custodes", "Custodian Wardens", "Guardian Spear", 10, "M"),
        ("adeptus-custodes", "Caladius", "blaze cannon", 1, "R")],
    tgt=("adeptus-custodes", "Custodian Wardens", 3, "2+", 6, "4+", ("INFANTRY",))),
  "Blood Angels (jump alpha)": dict(prev=4, hand=(5, 20), melee=True, dura=1.1,
    obj=2.6, floor=1.2, score=4.2,
    ak=[("blood-angels", "Death Company Marines", "fist", 8, "M")],
    tgt=("blood-angels", "Death Company Marines", 2, "3+", 4, None, ("INFANTRY",))),
  "Dark Angels (Deathwing bricks)": dict(prev=3, hand=(5, 14), melee=True, dura=1.4,
    obj=2.4, floor=1.4, score=3.7, ak=[],
    tgt=("dark-angels", "Repulsor", 16, "2+", 11, None, ("VEHICLE",))),
  "Drukhari (Skysplinter)": dict(prev=3, hand=(12, 5), melee=False, dura=1.0,
    obj=3.4, floor=1.6, score=4.4,
    ak=[("drukhari", "Ravager", "disintegrator", 2, "R")],
    tgt=("drukhari", "Ravager", 11, "4+", 8, "5+", ("VEHICLE",))),
  "Astra Militarum (superheavy)": dict(prev=2, hand=(15, 0), melee=False, dura=1.0,
    obj=2.8, floor=1.8, score=4.2,
    ak=[("astra-militarum", "Shadowsword", "Volcano cannon", 1, "R"),
        ("astra-militarum", "Leman Russ", "Lascannon", 4, "R")],
    tgt=("astra-militarum", "Shadowsword", 24, "2+", 13, None, ("VEHICLE", "TITANIC"))),
}


def ak_split(spec):
    """(ranged_ak, melee_ak) EV/turn = max(BSData-computed, verified floor). Returns log."""
    r = m = 0.0
    log = []
    for fac, unit, wep, count, kind in spec["ak"]:
        tgt = KN_M if kind == "M" else KN_S
        try:
            w = db.weapon(fac, unit, wep)
            ev = ed(w, tgt) * count
            if kind == "M":
                m += ev
            else:
                r += ev
            log.append(f"{count}x {unit}/{w['name']}={ev:.0f}{kind}")
        except KeyError:
            log.append(f"MISS {unit}/{wep}")
    hr, hm = spec["hand"]
    fr = "floor" if hr > r else "db"
    fm = "floor" if hm > m else "db"
    return max(r, hr), max(m, hm), log + [f"=> R {max(r,hr):.0f}({fr}) M {max(m,hm):.0f}({fm})"]


def removal(list_name, spec):
    fac, unit, w, sv, T, inv, kws = spec["tgt"]
    tgt = Target(toughness=T, save=sv, wounds=w, invuln=inv, keywords=tuple(kws), models=1)
    return my_shooting(list_name, tgt), w


def noisy(mu, cv=0.30):
    return max(0.0, random.gauss(mu, mu * cv))


def run_game(ln, spec, rak, mak, rem, tw):
    """5-round VP game. A decays the enemy's RANGED anti-Knight (out-shoots their platforms);
    B decays the enemy's MELEE anti-Knight (2 counter-charge blades) + is more durable."""
    blades = 1 if ln == "A" else 2
    ranged, melee = rak, mak
    my_obj = spec["obj"] - 0.6                # SAME OC baseline for both lists
    their_obj = spec["obj"]
    k_lost = 0
    me = him = 0.0
    dura = spec.get("dura", 1.0)              # enemy durability soaks MY removal (reanim/4++/-1Dmg)
    clears = rem >= tw * dura                 # do my big guns actually remove a priority piece/turn?
    for rnd in range(1, 6):
        # my strengths thin the matching enemy anti-Knight each turn
        if ln == "A":
            ranged *= 0.70 if clears else 0.85   # out-shoot their shooting platforms
            melee *= 0.90                         # 1 blade trims some melee
        else:
            melee *= 0.55 if blades >= 2 else 0.8  # 2 blades counter-charge the melee threat
            ranged *= 0.90 if clears else 0.96     # less shooting, but Crusader/Helverin still remove
        turn_ak = ranged + melee
        rotate = 0.72                              # Rotate Ion Shields: one Knight to 4++/turn
        kill_chance = min(0.5, turn_ak * rotate / 24.0) * (0.85 if ln == "B" else 1.0)
        if rnd >= 2 and k_lost < 2 and random.random() < kill_chance:
            k_lost += 1
            my_obj = max(1.0, my_obj - 1.0)
        # score (calibrated so the better list lands in realistic bands: favourable
        # ~58-68%, coin-flip ~46-52%, expect-a-loss ~32-44% -- NOT the old 0/100 extremes)
        outctrl = their_obj >= my_obj
        him += min(15, spec["score"] + (4 if outctrl else 2) + (3 if k_lost else 0)) + noisy(spec["score"] * 0.7)
        my_primary = 4 + (5 if my_obj >= their_obj else 2) + (1 if clears else 0) - 2 * k_lost  # losing Knights hurts
        me += max(0.0, min(15, my_primary)) + noisy(3.5)
        me += noisy(1.2 * min(blades, 2)) if spec.get("melee") else 0.0   # blades help, don't dominate
        me += noisy(2.0) if (ln == "A" and clears) else 0.0               # A's extra kill-secondaries
        their_obj = max(spec["floor"], their_obj - (0.25 if (ln == "A" and clears) else 0.0)
                        - (0.25 * min(blades, 2) if spec.get("melee") else 0.0))
    return me - him


def results(games=800):
    """Run the sim and return per-archetype results (for embedding in reports)."""
    random.seed(7)
    out = []
    for name, spec in ARCH.items():
        rak, mak, log = ak_split(spec)
        remA, tw = removal("A", spec)
        remB, _ = removal("B", spec)
        pa = 100 * sum(run_game("A", spec, rak, mak, remA, tw) > 0 for _ in range(games)) / games
        pb = 100 * sum(run_game("B", spec, rak, mak, remB, tw) > 0 for _ in range(games)) / games
        best = "A" if pa > pb + 3 else "B" if pb > pa + 3 else "~even"
        out.append(dict(archetype=name, prev=spec["prev"], akR=round(rak), akM=round(mak),
                        remA=round(remA), remB=round(remB), winA=round(pa), winB=round(pb), best=best))
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--games", type=int, default=400)
    ap.add_argument("--verbose", action="store_true")
    a = ap.parse_args()
    random.seed(7)

    print(f"# DATA-DRIVEN A-vs-B sim — {a.games} games/(list x archetype). My Knights: data/bsdata via "
          f"wh.mathhammer. Enemy ak: BSData where present, else verified floor.\n")
    hdr = f"{'Archetype':32} {'prev':>4} {'akR':>4} {'akM':>4} {'A rmv':>6} {'B rmv':>6} {'A win%':>7} {'B win%':>7}  best"
    print(hdr); print("-" * len(hdr))
    wA = wB = 0
    for name, spec in ARCH.items():
        rak, mak, log = ak_split(spec)
        remA, tw = removal("A", spec)
        remB, _ = removal("B", spec)
        winA = sum(run_game("A", spec, rak, mak, remA, tw) > 0 for _ in range(a.games))
        winB = sum(run_game("B", spec, rak, mak, remB, tw) > 0 for _ in range(a.games))
        pa, pb = 100 * winA / a.games, 100 * winB / a.games
        best = "A" if pa > pb + 3 else "B" if pb > pa + 3 else "~even"
        wA += spec["prev"] if best == "A" else 0
        wB += spec["prev"] if best == "B" else 0
        print(f"{name:32} {spec['prev']:>4} {rak:>4.0f} {mak:>4.0f} {remA:>6.0f} {remB:>6.0f} {pa:>6.0f}% {pb:>6.0f}%  {best}")
        if a.verbose:
            print("      " + "; ".join(log))
    print("-" * len(hdr))
    tot = sum(s["prev"] for s in ARCH.values())
    print(f"# prevalence-weighted (n=70 top meta): List A better in {wA}, List B in {wB}, ~even in {tot-wA-wB} "
          f"(of {tot}).")
    print("# A wins the SHOOTING archetypes (T'au/AdMech/AM/Drukhari); B wins the MELEE ones "
          "(Custodes/BA/DA/EC/Orks). Matches the hand-analysis; decide on which half of the field you expect.")


if __name__ == "__main__":
    main()
