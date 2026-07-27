# -*- coding: utf-8 -*-
"""mc_bt_sim.py — DATA-DRIVEN Monte-Carlo for the corrected FIXED BLACK TEMPLARS list vs the
LSO-meta archetypes, from BT's side. Mirrors tools/mc_gv_sim.py.

BT's killing is a DELIVERED MELEE SPIKE, not shooting. Computed from REAL profiles (data/bsdata
via tools/db.py) with wh.mathhammer: the spike = 5 Sword Brethren master-crafted power weapons
([LETHAL HITS]) under a Marshal (INSPIRATIONAL EXEMPLAR -> crit on 5+, modelled as Mods.crit_hit=5)
+ Castellan re-rolls (Mods.reroll_hits) + Slayers of Abominations (+2 S vs MONSTER/VEHICLE -> S7).
BT shooting is deliberately THIN (2 Heavy Laser Destroyers + a Gladiator Lancer + 3 Eradicators,
Oath-boosted) — Marines shoot badly without Oath.

The two structural truths that cap BT and drive the model:
  * DELIVERY DEPENDENCE — only 2 Repulsor Executioners carry the two spikes. Shooty enemies pop a
    bus and strand a spike (the spike is melee -> if it can't reach, it does nothing, and BT's own
    shooting can't finish the job). So shooting metas are a delivery race BT is behind in.
  * CAN'T REACH / CAN'T OUT-BODY — vs castled gunlines it can't get there; vs hordes the spike is
    wasted (Slayers only fires vs MONSTER/VEHICLE) and the 10-bricks get out-bodied.

  PYTHONPATH=tools:src python3 tools/mc_bt_sim.py [--games 800] [--verbose]
"""
import argparse, random
import db
from wh.mathhammer import expected_damage as ed, Target, Mods

SM = "space-marines"; BT = "black-templars"
OATH = Mods(reroll_hits="fails")                              # SM Oath: re-roll Hits (no +1 wound for BT)
SPIKE = Mods(reroll_hits="fails", crit_hit=5)                 # Vehement Aggression re-roll + Inspirational Exemplar crit-on-5


def _w(fac, unit, wep):
    for f in (fac, SM if fac == BT else BT):
        try:
            return db.weapon(f, unit, wep)
        except Exception:
            continue
    raise KeyError(wep)


def bt_spike(target):
    """ONE delivered Sword Brethren spike (Marshal+Castellan+5 SB) onto the priority target.
    Slayers of Abominations: +2 S vs MONSTER/VEHICLE (-> S7). crit-on-5 + Lethal Hits auto-wounds."""
    dmg = 0.0
    mv = ("VEHICLE" in target.keywords) or ("MONSTER" in target.keywords)
    try:
        w = dict(_w(BT, "Sword Brethren Squad", "power weapon"))
        if mv:
            w["S"] = int(w["S"]) + 2                          # Slayers of Abominations
        dmg += 5 * ed(w, target, SPIKE)                      # 5 Sword Brethren (A3 each)
    except KeyError:
        pass
    dmg *= 1.35                                              # + Marshal & Castellan attacks under the same buffs
    return dmg


def bt_shoot(target):
    """BT's THIN Oath-boosted shooting (the reach it has for the un-chargeable)."""
    dmg = 0.0
    try: dmg += 2 * ed(_w(SM, "Repulsor Executioner", "laser destroyer"), target, OATH)   # 2 buses x1 HLD
    except KeyError: pass
    try: dmg += 3 * ed(_w(SM, "Eradicator Squad", "melta"), target, OATH)                  # 3 Eradicators
    except KeyError: pass
    try: dmg += 2 * ed(_w(SM, "Ballistus Dreadnought", "lascannon"), target, OATH)         # Gladiator Lancer proxy (las-class)
    except KeyError: pass
    return dmg


def T(t, sv, w_, inv=None, models=1, kws=("INFANTRY",)):
    return Target(toughness=t, save=sv, wounds=w_, invuln=inv, models=models, keywords=tuple(kws))


# enemy_kill = EV dmg/turn into BT's MEQ/TEQ bodies; obj = enemy board control; shooty = can pop a
# Repulsor early (delivery risk -> strands a melee spike); fast = out-manoeuvres M6; horde = the spike
# is wasted on 1-wound bodies (Slayers only fires vs Mon/Veh).
ARCH = {
  "Emperor's Children (Defiler+swarm)": dict(prev=9, verdict="EVEN", enemy_kill=14, obj=3.0, floor=1.9, score=4.6,
     tgt=T(11, "3+", 18, "5+", 1, ("VEHICLE", "MONSTER"))),                  # Defiler (spike food)
  "Orks (Green Tide horde)": dict(prev=8, verdict="UNFAV", enemy_kill=15, obj=3.6, floor=2.6, score=5.2, horde=True,
     tgt=T(5, "6+", 1, None, 20, ("INFANTRY",))),                            # Boyz (spike wasted, no S7)
  "AdMech (Rad-Zone gunline)": dict(prev=6, verdict="EVEN", enemy_kill=15, obj=2.9, floor=1.9, score=4.4, shooty=True,
     tgt=T(7, "3+", 3, None, 6, ("VEHICLE",))),                             # Kataphron (Veh -> spike S7)
  "T'au (Retaliation alpha)": dict(prev=5, verdict="HARD", enemy_kill=20, obj=3.0, floor=1.9, score=4.9, shooty=True,
     bus_pop=0.42, fast=True, tgt=T(9, "2+", 14, "4+", 1, ("VEHICLE", "MONSTER"))),                   # Riptide (must be reached)
  "Necrons (Awakened C'tan)": dict(prev=4, verdict="COIN-", enemy_kill=14, obj=3.4, floor=2.3, score=5.0, dura=1.5,
     shooty=True, tgt=T(12, "4+", 10, "4+", 1, ("VEHICLE", "MONSTER"))),     # C'tan (durable)
  "Custodes (elite melee)": dict(prev=4, verdict="COIN", enemy_kill=18, obj=2.7, floor=1.7, score=4.4, dura=1.4,
     tgt=T(6, "2+", 3, "4+", 5, ("INFANTRY",))),                            # Custodian brick (spike at S5)
  "Blood Angels (jump alpha)": dict(prev=4, verdict="COIN-", enemy_kill=18, obj=2.7, floor=1.6, score=4.6, fast=True,
     tgt=T(4, "3+", 2, None, 10, ("INFANTRY",))),                           # Death Company
  "Dark Angels (Deathwing)": dict(prev=3, verdict="EVEN", enemy_kill=16, obj=2.7, floor=1.7, score=4.3, dura=1.4,
     tgt=T(5, "2+", 3, "4+", 5, ("INFANTRY",))),                            # Deathwing (Lethal-on-5 grinds the 4++)
  "Drukhari (Skysplinter)": dict(prev=3, verdict="UNFAV", enemy_kill=13, obj=3.3, floor=1.8, score=4.7, fast=True,
     shooty=True, tgt=T(8, "4+", 11, "5+", 1, ("VEHICLE",))),               # Ravager
  "Astra Militarum (superheavy)": dict(prev=2, verdict="EVEN", enemy_kill=16, obj=2.8, floor=1.8, score=4.3, shooty=True,
     tgt=T(13, "2+", 24, None, 1, ("VEHICLE", "TITANIC"))),                 # Shadowsword (prime spike food)
}


def noisy(mu, cv=0.28):
    return max(0.0, random.gauss(mu, mu * cv))


# head-to-head list configs. The key delivery rule (core 18.04 + Assault Ramp): a spike can only
# move-and-charge out of a LAND RAIDER CRUSADER (Assault Ramp); a Repulsor with no ramp forces a
# Rapid Disembark (no charge) or a slow stationary Tactical Disembark -> POOR charge delivery. So:
#   delivery_base = how well the spikes actually reach the fight (0 ramp buses -> low; 2 -> high)
#   shoot_mult    = ranged AT (2 Heavy Laser Destroyers on 2 Repulsors -> high; 0 on 2 LRCs -> low)
#   bus_pop_mult  = bus survivability (LRC 2+ slightly tankier); reserve_floor/fast_relief = jump reserve.
CONFIGS = {
    "v1 (2 Repulsor)":   dict(delivery_base=0.72, shoot_mult=1.20, bus_pop_mult=1.00, reserve_floor=0.00, fast_relief=0.00),
    "v2a (Repulsor+LRC)":dict(delivery_base=0.85, shoot_mult=1.00, bus_pop_mult=0.85, reserve_floor=0.70, fast_relief=0.35),
    "v2b (2x LRC)":      dict(delivery_base=0.95, shoot_mult=0.78, bus_pop_mult=0.80, reserve_floor=0.70, fast_relief=0.35),
}
DOCUMENTED = "v2b (2x LRC)"   # the promoted list (results() defaults to this); the others are kept for tracking


def run_game(spec, spike, shoot, tw, cfg=None):
    """BT buses a spike into the priority piece and deletes it in melee, holds with cover-bricks, and
    grinds primary. Delivery-dependent: shooty enemies strand the spike; hordes waste it; fast enemies
    out-manoeuvre. Shooting is a thin supplement, not a removal tool on its own. cfg = list version."""
    if cfg is None:
        cfg = CONFIGS[DOCUMENTED]
    dura = spec.get("dura", 1.0)
    their_obj = spec["obj"] + (max(0.0, 0.6 - cfg["fast_relief"]) if spec.get("fast") else 0.0) + (0.6 if spec.get("horde") else 0.0)
    my_obj = spec["obj"] - 0.7
    buses = 2
    bodies_lost = 0
    me = him = 0.0
    for rnd in range(1, 6):
        kill = spec["enemy_kill"]
        if rnd >= 2 and random.random() < min(0.5, kill / 28.0):
            bodies_lost += 1
            my_obj = max(1.0, my_obj - 0.4)
        # shooty enemies pop a bus -> strand a melee spike (v2's Land Raider Crusader is far harder to pop)
        if spec.get("shooty") and buses > 0 and rnd <= 3 and random.random() < spec.get("bus_pop", 0.28) * cfg["bus_pop_mult"]:
            buses -= 1
        # fraction of the spike(s) that reach the fight; v2's jump reserve sets a delivery FLOOR
        # delivery quality = the config's base (Assault-Ramp buses reach; Repulsors deliver poorly),
        # scaled by surviving buses, with the jump reserve as a floor
        delivered = max(cfg["reserve_floor"], cfg["delivery_base"] * (0.6 + 0.4 * (buses / 2.0)))
        # removal = the delivered spikes (both can focus a big target) + a thin shooting supplement
        # (scaled by the config's ranged AT); a horde wastes the spike (Slayers only fires vs Mon/Veh).
        removal = spike * delivered * 1.5 * (0.4 if spec.get("horde") else 1.0) + 0.4 * shoot * cfg["shoot_mult"]
        clears = removal >= 0.75 * tw * dura
        outctrl = their_obj >= my_obj
        him += min(15, spec["score"] + (4 if outctrl else 2) + (2 if bodies_lost else 0)) + noisy(spec["score"] * 0.7)
        if clears:
            their_obj = max(spec["floor"], their_obj - 0.3)
        me += max(0.0, min(15, 5 + (5 if my_obj >= their_obj else 2) + (1 if clears else 0) - bodies_lost)) + noisy(3.5)
        me += noisy(2.5) if clears else 0.0
    return me - him


def results(games=800, cfg=None):   # default = the DOCUMENTED list (set below); others kept for tracking
    if cfg is None:
        cfg = CONFIGS[DOCUMENTED]
    random.seed(11)
    out = []
    for name, spec in ARCH.items():
        tgt = spec["tgt"]
        spike = bt_spike(tgt); shoot = bt_shoot(tgt)
        win = sum(run_game(spec, spike, shoot, tgt.wounds, cfg) > 0 for _ in range(games))
        out.append(dict(archetype=name, prev=spec["prev"], verdict=spec["verdict"],
                        spike=round(spike), shoot=round(shoot), tgtW=tgt.wounds, win=round(100 * win / games)))
    return out


def history(games=2000):
    """Per-archetype win% for EVERY list version (v1, v2, ...) + prevalence-weighted per version.
    This is the incremental-improvement tracker rendered into the deliverables."""
    names = list(CONFIGS.keys())
    per = {n: results(games, CONFIGS[n]) for n in names}
    rows, tot = [], sum(ARCH[a]["prev"] for a in ARCH)
    for i, arch in enumerate(ARCH):
        row = dict(archetype=arch, prev=ARCH[arch]["prev"])
        for n in names:
            row[n] = per[n][i]["win"]
        rows.append(row)
    weighted = {n: round(sum(ARCH[a]["prev"] * per[n][i]["win"] for i, a in enumerate(ARCH)) / tot) for n in names}
    return names, rows, weighted


def compare(games=4000):
    """Head-to-head across ALL delivery configs (v1 / v2a / v2b) — the version tracker."""
    names, rows, weighted = history(games)
    wcol = "".join(f"{n.split()[0]:>7}" for n in names)
    hdr = f"{'Archetype':34} {'prev':>4}{wcol}"
    print(hdr); print("-" * len(hdr))
    for r in rows:
        cells = "".join(f"{r[n]:>6}%" for n in names)
        print(f"{r['archetype']:34} {r['prev']:>4}{cells}")
    print("-" * len(hdr))
    wcells = "".join(f"{weighted[n]:>6}%" for n in names)
    print(f"{'PREVALENCE-WEIGHTED':34} {'':>4}{wcells}")
    for n in names:
        print(f"  {n:22} weighted = {weighted[n]}%")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--games", type=int, default=800)
    ap.add_argument("--verbose", action="store_true")
    ap.add_argument("--compare", action="store_true", help="v1 (current) vs v2 (improved) head-to-head")
    a = ap.parse_args()
    if a.compare:
        print(f"# BLACK TEMPLARS v1 (current fixed) vs v2 (improved: Land Raider Crusader + jump reserve) — {max(a.games,4000)} games/archetype\n")
        compare(max(a.games, 4000)); return
    print(f"# CORRECTED FIXED BLACK TEMPLARS sim — {a.games} games/archetype. Spike + shooting from data/bsdata via wh.mathhammer.\n")
    hdr = f"{'Archetype':34} {'prev':>4} {'verdict':>7} {'spike':>6} {'shoot':>6} {'tgtW':>5} {'BT win%':>8}"
    print(hdr); print("-" * len(hdr))
    tot = wsum = 0
    for x in results(a.games):
        print(f"{x['archetype']:34} {x['prev']:>4} {x['verdict']:>7} {x['spike']:>6} {x['shoot']:>6} {x['tgtW']:>5} {x['win']:>7}%")
        tot += x["prev"]; wsum += x["prev"] * x["win"]
    print("-" * len(hdr))
    print(f"# prevalence-weighted BT win rate across the top meta: {wsum/tot:.0f}%  "
          f"(swingy mid/low-tier; deletes what a spike reaches, loses to castled shooting / hordes / speed).")


if __name__ == "__main__":
    main()
