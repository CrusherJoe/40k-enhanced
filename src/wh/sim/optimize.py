"""List-improvement optimizer — the recommendations engine. Take a list + an opponent, find its
dead-weight units (from the weakness analyzer), try swapping each for a candidate that addresses the
list's gaps, RE-SIMULATE, and report the win-rate delta of each swap. This turns the analyzer's
directional findings into concrete, TESTED "swap X for Y -> +N% win" recommendations.

  python -m wh.sim.optimize <me> <opp> [--screen 1500] [--final 5000]

Screening uses a lower game count across many candidates; the top swaps are re-verified at --final.
Candidates are faction options that plug common holes (anti-monster/tank, durable bodies). Points are
reported so you can see the trade (the swap isn't forced points-neutral; you balance it)."""
from __future__ import annotations

import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(
    os.path.abspath(__file__))))), "tools"))
import db

from . import run, analyze, rosters


def _pts(name, slug="adeptus-custodes"):
    try:
        return db.points(slug, name)["first"]
    except Exception:
        return 0


def _custodes_candidates():
    """Custodes options that plug common gaps: anti-monster/tank output + durable bodies."""
    S, mk, C = "adeptus-custodes", rosters.mk, rosters.CRIT5
    out = []
    for name, role, threat, ab in [
        ("Caladius Grav-tank", "anti_tank", 3.2, None),            # twin arachnus S12 -> threatens C'tan/vehicles
        ("Telemon Heavy Dreadnought", "anti_tank", 3.2, C),        # arachnus storm + durable
        ("Contemptor-Galatus Dreadnought", "line", 2.8, C),        # melee dread, cracks monsters
        ("Trajann Valoris", "character", 3.6, C),                  # elite character
        ("Aquilon Custodians", "anti_tank", 2.6, dict(C, reroll_wounds="fails")),
    ]:
        try:
            kw = dict(role=role, threat=threat)
            if ab:
                kw["abilities"] = ab
            n = 3 if name == "Aquilon Custodians" else 1
            mk(S, name, n)                                         # probe it resolves
            out.append((name, (lambda nm=name, k=kw, nn=n: mk(S, nm, nn, **k)), _pts(name)))
        except Exception:
            pass
    return out


# Detachment fit: Shield Host's army rule (Martial Mastery — melee crit-on-5) does NOTHING for a
# vehicle/dreadnought. So if the winning swaps pile on VEHICLES, the deeper move is to change the
# DETACHMENT — a second-order lever the unit-swap search can't see. These are the real Custodes
# detachments in data/strats; DP cost is the human's call (Solar Spearhead is a 2-DP detachment).
_VEHICLE_HOMES = [
    ("Might of the Moritoi", "Contemptor/Telemon dreadnought focus", 1),
    ("Solar Spearhead", "buffs VEHICLES army-wide, but costs 2 Detachment Points", 2),
]


def _is_vehicle(cbuild):
    try:
        u = cbuild()
        return any(k in u.keywords for k in ("VEHICLE", "MONSTER", "TITANIC"))
    except Exception:
        return False


def _swap_builder(build_me, remove_name, cand_build):
    def b():
        a = build_me()
        for i, u in enumerate(a.units):
            if u.name == remove_name:
                del a.units[i]
                break
        a.units.append(cand_build())
        return a
    return b


def optimize(build_me, build_opp, candidates=None, screen=500, final=2000, seed=11):
    candidates = candidates or _custodes_candidates()
    base = run.simulate(build_me, build_opp, games=screen, seed=seed)["win"]
    d = analyze.diagnose(build_me, build_opp, games=500, seed=seed)
    surv = sorted(((nm, 100 * c / (d["games"] * d["me_counts"][nm])) for nm, c in d["my_survivors"].items()),
                  key=lambda x: x[1])
    dead = [nm for nm, p in surv if p < 45][:2] or [nm for nm, _ in surv[:2]]

    trials = []
    for rm in dead:
        rmpts = _pts(rm)
        for cname, cbuild, cpts in candidates:
            if cname == rm:
                continue
            w = run.simulate(_swap_builder(build_me, rm, cbuild), build_opp, games=screen, seed=seed)["win"]
            trials.append(dict(delta=w - base, rm=rm, add=cname, win=w, dpts=cpts - rmpts))
    trials.sort(key=lambda t: -t["delta"])
    veh = {cname for cname, cbuild, _ in candidates if _is_vehicle(cbuild)}

    # re-verify the top 3 improving swaps at the full game count
    for t in trials[:3]:
        if t["delta"] > 0:
            cbuild = next(cb for cn, cb, _ in candidates if cn == t["add"])
            t["win"] = run.simulate(_swap_builder(build_me, t["rm"], cbuild), build_opp, games=final, seed=seed)["win"]
            t["delta"] = t["win"] - base
    return dict(base=base, trials=trials, me=d["me_name"], opp=d["opp_name"], final=final, veh=veh)


def report(r):
    L = [f"LIST-IMPROVEMENT SEARCH — {r['me']}  vs  {r['opp']}",
         f"  baseline win rate: {r['base']}%", "",
         "Swaps tried (remove dead weight -> add a gap-filler), re-simulated:",
         f"  {'SWAP':52} {'ΔpTS':>6} {'win%':>6} {'Δwin':>6}"]
    for t in sorted(r["trials"], key=lambda t: -t["delta"])[:10]:
        arrow = "+" if t["delta"] >= 0 else ""
        L.append(f"  -{t['rm']:22} +{t['add']:24} {t['dpts']:+6} {t['win']:>5}% {arrow}{t['delta']:>4}%")
    best = max(r["trials"], key=lambda t: t["delta"], default=None)
    L += [""]
    if best and best["delta"] >= 3:
        L.append(f"RECOMMENDATION: swap OUT {best['rm']} -> IN {best['add']} "
                 f"({best['dpts']:+} pts) for +{best['delta']}% (to {best['win']}%). "
                 f"It plugs the gap the analyzer flagged. Re-verified at {r['final']} games.")
    else:
        L.append("RECOMMENDATION: no single tested swap materially improves this matchup — the problem "
                 "is structural (mission/disposition or a whole-army speed/tempo gap), not one unit.")

    # second-order lever: if the winning swaps are vehicles, Shield Host's melee rule wastes on them.
    veh = r.get("veh") or set()
    top_veh = [t for t in sorted(r["trials"], key=lambda t: -t["delta"])[:4]
               if t["delta"] >= 3 and t["add"] in veh]
    if len(top_veh) >= 2:
        homes = "; ".join(f"{nm} ({why})" for nm, why, _ in _VEHICLE_HOMES)
        L += ["",
              f"DETACHMENT NOTE: your best swaps here ({', '.join(dict.fromkeys(t['add'] for t in top_veh))}) "
              "are VEHICLES/DREADNOUGHTS. Shield Host's Martial Mastery (melee crit-on-5) does nothing for "
              "them. If you lean into 2+ of these, the deeper fix is to change the DETACHMENT to a "
              f"vehicle/dread home: {homes}. Full detachment-swap re-simulation isn't modelled yet — treat "
              "this as a direction, then re-test by hand."]
    return "\n".join(L)


def main():
    import argparse
    ap = argparse.ArgumentParser(description="Find TESTED list-improvement swaps for a matchup.")
    ap.add_argument("me"); ap.add_argument("opp")
    ap.add_argument("--screen", type=int, default=600); ap.add_argument("--final", type=int, default=3000)
    a = ap.parse_args()
    print(report(optimize(getattr(rosters, a.me), getattr(rosters, a.opp), screen=a.screen, final=a.final)))


if __name__ == "__main__":
    main()
