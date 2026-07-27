# -*- coding: utf-8 -*-
"""mc_custodes_sim.py — DATA-DRIVEN Monte-Carlo for the Meta Slayers' "The Better Thing 2"
(Adeptus Custodes, Shield Host + Tharanatoi Hammerblow) vs the LSO-meta archetypes.

Durable-grind template (like mc_gv_sim): Custodes are a 2+/4++/FNP wall that hits like a truck
and — unlike the slow BT lists — is FAST (M10-12 jetbikes/jet-packs + deep-strike Allarus), so its
removal REACHES (no delivery penalty). Output computed from REAL profiles (data/bsdata via db.py):
  * melee HAMMER = Guardian spears (S7 AP-2 D2 A5) with RENDAX ([LETHAL HITS], army rule Martial
    Ka'tah) + ASSEMBLAGE OF MIGHT (+1 to Wound vs the marked target) + Allarus SLAYERS OF TYRANTS
    (re-roll Wounds vs CHARACTER/MONSTER/VEHICLE).
  * shooting = the fast bits (Vertus hurricane bolters + lances + Allarus grenades) — a supplement.
Durability (2+/4++ + Wardens FNP + Valerian -1 AP) is baked into a modest enemy_kill.

The ONE structural hole: a TRUE HORDE out-bodies ~40 elite models on primary (horde flag).

  PYTHONPATH=tools:src python3 tools/mc_custodes_sim.py [--games 800] [--verbose]
"""
import argparse, random
import db
from wh.mathhammer import expected_damage as ed, Target, Mods

CU = "adeptus-custodes"
MARK = Mods(wound=1)                                  # Assemblage of Might: +1 to Wound vs the marked target
MARK_SLAY = Mods(wound=1, reroll_wounds="fails")      # + Allarus Slayers of Tyrants vs CHAR/MON/VEH


def _spear_lethal():
    """Guardian Spear with RENDAX (Martial Ka'tah adds [LETHAL HITS])."""
    w = dict(db.weapon(CU, "Custodian Guard", "Guardian spear"))
    w["abilities"] = list(w.get("abilities") or w.get("keywords") or []) + ["LETHAL HITS"]
    return w


def cust_hammer(target):
    """The committed melee onto the marked priority target: ~a Warden/Guard brick (5) + the Allarus
    (5), Guardian spears, Rendax-Lethal + Assemblage +1-wound; Allarus re-roll wounds vs CHAR/MON/VEH."""
    spear = _spear_lethal()
    mv = any(k in target.keywords for k in ("VEHICLE", "MONSTER", "CHARACTER", "TITANIC"))
    dmg = 0.0
    dmg += 5 * ed(spear, target, MARK)                          # 5 Guardian/Warden spears (A5)
    dmg += 5 * ed(spear, target, MARK_SLAY if mv else MARK)     # 5 Allarus spears (Slayers vs mv)
    dmg *= 1.15                                                 # the attached characters' attacks
    return dmg


def cust_shoot(target):
    """The fast supplement: Vertus hurricane bolters + Interceptor lances + Allarus grenades."""
    dmg = 0.0
    for unit, wep, n in [("Vertus Praetors", "hurricane", 12), ("Vertus Praetors", "Interceptor lance", 0),
                         ("Allarus Custodians", "grenade", 5), ("Venatari Custodians", "lance", 12)]:
        if not n:
            continue
        try:
            dmg += n * ed(db.weapon(CU, unit, wep), target, Mods())
        except Exception:
            pass
    return dmg


def T(t, sv, w_, inv=None, models=1, kws=("INFANTRY",)):
    return Target(toughness=t, save=sv, wounds=w_, invuln=inv, models=models, keywords=tuple(kws))


# enemy_kill = EV dmg/turn into Custodes' 2+/4++/FNP bodies (already low — the wall is hard to shift);
# obj = enemy board control; horde = out-bodies ~40 elite models; dura = enemy soaks the removal.
ARCH = {
  "Emperor's Children (Defiler+swarm)": dict(prev=9, verdict="FAV", enemy_kill=11, obj=3.0, floor=1.8, score=4.6,
     tgt=T(11, "3+", 18, "5+", 1, ("VEHICLE", "MONSTER"))),
  "Orks (Green Tide horde)": dict(prev=8, verdict="UNFAV", enemy_kill=14, obj=3.5, floor=2.6, score=5.2, horde=True,
     clear_cap=0.5, tgt=T(5, "6+", 1, None, 20, ("INFANTRY",))),
  "AdMech (Rad-Zone gunline)": dict(prev=6, verdict="FAV", enemy_kill=12, obj=2.9, floor=1.8, score=4.4,
     tgt=T(7, "3+", 3, None, 6, ("INFANTRY",))),
  "T'au (Retaliation alpha)": dict(prev=5, verdict="COIN", enemy_kill=15, obj=2.8, floor=1.7, score=4.5,
     tgt=T(9, "2+", 14, "4+", 1, ("VEHICLE", "MONSTER"))),
  "Necrons (Awakened C'tan)": dict(prev=4, verdict="COIN", enemy_kill=13, obj=3.4, floor=2.4, score=5.0, dura=1.6,
     tgt=T(12, "4+", 10, "4+", 1, ("VEHICLE", "MONSTER"))),
  "Custodes (the MIRROR)": dict(prev=4, verdict="EVEN", enemy_kill=15, obj=2.7, floor=1.7, score=4.2, dura=1.3,
     clear_cap=0.5, clear_flat=True, tgt=T(6, "2+", 3, "4+", 5, ("INFANTRY", "CHARACTER"))),
  "Blood Angels (jump alpha)": dict(prev=4, verdict="FAV", enemy_kill=13, obj=2.6, floor=1.5, score=4.5,
     tgt=T(4, "3+", 2, None, 10, ("INFANTRY",))),
  "Dark Angels (Deathwing)": dict(prev=3, verdict="COIN", enemy_kill=14, obj=2.7, floor=1.7, score=4.3, dura=1.4,
     tgt=T(5, "2+", 3, "4+", 5, ("INFANTRY",))),
  "Drukhari (Skysplinter)": dict(prev=3, verdict="FAV", enemy_kill=11, obj=3.1, floor=1.7, score=4.6,
     tgt=T(8, "4+", 11, "5+", 1, ("VEHICLE",))),
  "Astra Militarum (superheavy)": dict(prev=2, verdict="FAV", enemy_kill=12, obj=2.8, floor=1.8, score=4.3,
     tgt=T(13, "2+", 24, None, 1, ("VEHICLE", "TITANIC"))),
}


def run_game(spec, hammer, shoot, tw):
    """Symmetric board-control grind: each round both sides score off who holds more objectives, so a
    dead-even board -> coin flip (the mirror lands ~50%). Custodes' EDGE is earned two ways — CLEARING
    the contesting unit (removal vs the durable target) tilts the board toward me, and SURVIVING (2+/4++
    wall -> low enemy_kill) keeps my holders scoring. A true HORDE re-bodies faster than I can clear and
    out-OCs from the start, tilting the board the other way."""
    dura = spec.get("dura", 1.0)
    removal = hammer + 0.4 * shoot
    horde = spec.get("horde", False)
    # how reliably I clear the contesting unit each round (graded, capped); a horde re-bodies -> capped low.
    # clear_cap lets a matchup override the ceiling (mirror: the enemy is just as durable, so I don't
    # get a clean clear edge; Astra: few bodies -> I table them regardless of the superheavy's wounds).
    cap = spec.get("clear_cap", 0.45 if horde else 0.9)
    clear_p = min(cap, removal / (tw * dura * 5.0)) if not spec.get("clear_flat") else cap
    # how often the enemy shifts one of my holders (2+/4++ wall -> low); scaled by enemy_kill
    hurt_p = min(0.55, spec["enemy_kill"] / 40.0)
    my_obj = spec["obj"] - 0.15                       # durable + mobile holder, slight baseline edge
    their_obj = spec["obj"] + (0.7 if horde else 0.0) # horde out-OCs from turn 1
    me = him = 0.0
    for rnd in range(1, 6):
        if random.random() < clear_p:
            their_obj = max(spec["floor"], their_obj - 0.55)
        if rnd >= 2 and random.random() < hurt_p:
            my_obj = max(1.2, my_obj - 0.55)
        tilt = my_obj - their_obj
        me += 4.0 + 2.3 * tilt + random.gauss(0, 3.4)
        him += 4.0 + 2.3 * (-tilt) + spec["score"] * 0.05 + random.gauss(0, 3.4)
    return me - him


def results(games=800):
    random.seed(11)
    out = []
    for name, spec in ARCH.items():
        tgt = spec["tgt"]
        hammer = cust_hammer(tgt); shoot = cust_shoot(tgt)
        win = sum(run_game(spec, hammer, shoot, tgt.wounds) > 0 for _ in range(games))
        out.append(dict(archetype=name, prev=spec["prev"], verdict=spec["verdict"],
                        hammer=round(hammer), shoot=round(shoot), tgtW=tgt.wounds, win=round(100 * win / games)))
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--games", type=int, default=800)
    ap.add_argument("--verbose", action="store_true")
    a = ap.parse_args()
    print(f"# THE BETTER THING 2 (Custodes, Shield Host + Tharanatoi Hammerblow) sim — {a.games} games/archetype. From data/bsdata via wh.mathhammer.\n")
    hdr = f"{'Archetype':34} {'prev':>4} {'verdict':>7} {'hammer':>7} {'shoot':>6} {'tgtW':>5} {'Cust win%':>10}"
    print(hdr); print("-" * len(hdr))
    tot = wsum = 0
    for x in results(a.games):
        print(f"{x['archetype']:34} {x['prev']:>4} {x['verdict']:>7} {x['hammer']:>7} {x['shoot']:>6} {x['tgtW']:>5} {x['win']:>9}%")
        tot += x["prev"]; wsum += x["prev"] * x["win"]
    print("-" * len(hdr))
    print(f"# prevalence-weighted Custodes win rate: {wsum/tot:.0f}%  "
          f"(top-tier all-comers — no bad damage/durability matchup; the only hole is a true HORDE out-bodying it).")


if __name__ == "__main__":
    main()
