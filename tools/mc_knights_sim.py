# -*- coding: utf-8 -*-
"""mc_knights_sim.py — real-mission Monte-Carlo for the LSO Knights LIST A (2 Castellan / 1 Lancer /
1 Crusader + Helverin + Navigator), disposition = PURGE THE FOE. Follows the standard workflow:
scores the REAL 11E missions via sim_game/missions, 10,000 games/archetype, verdicts DERIVED from win%.

Knights capability profile: HIGH kill (Volcano lances one-shot anchors) but LOW action + LOW control
(a ~6-model army has no cheap action-doers and gets out-OC'd by bodies) — the big-model weakness the
mission layer stress-tests. Purge the Foe is the recommended disposition because the matrix hands
Knights kill-missions (Unstoppable Force / Meatgrinder / Destroyer's Wrath) that reward their killing.

Caps are seeded from the ESTABLISHED per-matchup verdicts (lso_data) + Knights' profile, then the real
missions + variance produce the win% (which can diverge from the seed verdict — that divergence is the
finding). Opponent dispositions are parsed from each matchup's stated `disp`.

  PYTHONPATH=tools:src python3 tools/mc_knights_sim.py [--games 10000]
"""
import argparse, re
import lso_data as L
import sim_game

MY_DISP = "purge-the-foe"
CUST_SEC = 0.85                      # Knights have few cheap units -> weak secondary/action game

# caps by verdict class (cust = Knights, opp = the archetype). Knights: low action/control, high kill,
# very durable (opp kill moderate unless anti-tank). Board control anti-correlated + body/horde bumps.
CAPS = {
    "fav":   (dict(action=.56, kill=.80, ctrl=2.2, home=.30), dict(action=.72, kill=.46, ctrl=1.7, home=.24)),
    "coin":  (dict(action=.54, kill=.71, ctrl=2.0, home=.26), dict(action=.72, kill=.55, ctrl=2.0, home=.25)),
    "unfav": (dict(action=.52, kill=.63, ctrl=1.8, home=.22), dict(action=.72, kill=.63, ctrl=2.4, home=.28)),
    "loss":  (dict(action=.48, kill=.58, ctrl=1.5, home=.18), dict(action=.74, kill=.68, ctrl=2.9, home=.28)),
}


def vclass(v):
    v = (v or "").upper()
    if "AUTO-LOSS" in v or "EXPECT-A-LOSS" in v:
        return "loss"
    if "UNFAV" in v:
        return "unfav"
    if "FAV" in v:
        return "fav"
    return "coin"                    # COIN-FLIP / PRELIM / Target / mirror


def parse_disp(s):
    if "mirror" in (s or "").lower():
        return "purge-the-foe"       # the gun-Knight mirror runs Purge
    first = (s or "").split("/")[0].split("(")[0].strip().lower()
    for frag, key in [("take", "take-and-hold"), ("priority", "priority-assets"),
                      ("recon", "reconnaissance"), ("disrupt", "disruption"), ("purge", "purge-the-foe")]:
        if frag in first:
            return key
    return "take-and-hold"           # 'Various' / unknown default


def parse_prev(p):
    p = str(p).lower()
    if "high" in p:
        return 9
    if "target" in p:
        return 4
    if "med" in p:
        m = re.search(r"\((\d)", p)
        return int(m.group(1)) if m else 5
    if "low" in p:
        return 2
    return 3


def build_arch():
    arch = {}
    for m in L.MATCHUPS:
        cls = vclass(m.get("verdict"))
        cust, opp = (dict(CAPS[cls][0]), dict(CAPS[cls][1]))
        horde = "green tide" in m["archetype"].lower() or "kult of speed" in m["archetype"].lower()
        if horde:
            opp["ctrl"] = max(opp["ctrl"], 3.0)
        name = f'{m["faction"]} — {m["archetype"]}'
        arch[name] = dict(prev=parse_prev(m.get("prev")), disp=parse_disp(m.get("disp")),
                          cust=cust, opp=opp, horde=horde, _mkey=m["key"])
    return arch


def results(games=10000, seed=11):
    arch = build_arch()
    base = sim_game.results(arch, MY_DISP, games, seed, cust_sec=CUST_SEC)
    for x, (name, spec) in zip(base, arch.items()):
        x["mkey"] = spec["_mkey"]
    return base


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--games", type=int, default=10000)
    ap.add_argument("--seed", type=int, default=11)
    a = ap.parse_args()
    rows = results(a.games, a.seed)
    sim_game.print_table(f"LSO KNIGHTS LIST A — {a.games} games/archetype", rows, MY_DISP)


if __name__ == "__main__":
    main()
