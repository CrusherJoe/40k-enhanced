#!/usr/bin/env python3
"""bcp_validate.py — validate the sim against REAL tournament results.

Ground truth we actually have: every DECIDED, fully-simmable pairing from a pulled BCP event (both
decklists load) is a real game with a known winner + score, across the whole meta — not just Custodes.
For each, sim me(p1) vs opp(p2) and compare the sim's predicted winner/win% to what really happened.

  PYTHONPATH=src python3 tools/bcp_validate.py <event> [--sample N] [--games G] [--seed S]

Reports: directional accuracy (did the sim pick the real winner — noisy per game, meaningful in aggregate)
and a reliability curve (does a sim X% favourite really win ~X%? — exposes the amplification skew)."""
import sys, os, json, sqlite3, argparse, random
sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "src"))
from wh.sim import bcp, run
from wh.sim import listloader as L


def simmable(row):
    return bool(row) and row["parse_ok"] and L._FACTION_SLUG.get(row["faction"]) and row["n_units"] > 0


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("event"); ap.add_argument("--sample", type=int, default=60)
    ap.add_argument("--games", type=int, default=40); ap.add_argument("--seed", type=int, default=7)
    a = ap.parse_args()
    db = f"data/bcp/{a.event}.sqlite"
    con = sqlite3.connect(db); con.row_factory = sqlite3.Row
    lists = {r["player"]: r for r in con.execute("SELECT * FROM lists")}
    pair = json.load(open(f"data/bcp/{a.event}-pairings.json"))
    dec = [p for p in pair if p.get("p1_pts") is not None and p.get("p2_pts") is not None
           and p["p1_pts"] != p["p2_pts"] and simmable(lists.get(p["p1"])) and simmable(lists.get(p["p2"]))]
    random.seed(a.seed); random.shuffle(dec)
    dec = dec[:a.sample]
    print(f"# {a.event}: validating {len(dec)} real pairings @ {a.games} games each")
    correct = 0; rows = []; bins = {}
    for i, p in enumerate(dec):
        try:
            me = bcp.builder(lists[p["p1"]]["list_id"], db=db, side="A")
            opp = bcp.builder(lists[p["p2"]]["list_id"], db=db, side="B")
            simw = run.simulate(me, opp, games=a.games, seed=a.seed)["win"]   # sim win% for p1
        except Exception:
            continue
        real_p1_won = p["p1_pts"] > p["p2_pts"]
        pred_p1_won = simw > 50
        correct += (pred_p1_won == real_p1_won)
        rows.append((simw, real_p1_won))
        b = min(9, simw // 10)                                   # decile bin
        bins.setdefault(b, [0, 0]); bins[b][0] += real_p1_won; bins[b][1] += 1
    n = len(rows)
    if not n:
        print("no simmable pairings"); return
    print(f"\nDIRECTIONAL ACCURACY: sim picked the real winner in {correct}/{n} = {round(100*correct/n)}% "
          f"(coin-flip = 50%)")
    print("\nRELIABILITY (does a sim X% favourite really win ~X%? — big gaps = the amplification skew):")
    print(f"  {'sim win% bin':14} {'real win%':>9} {'n':>4}")
    for b in sorted(bins):
        wins, tot = bins[b]
        print(f"  {b*10:>3}-{b*10+9:<9} {round(100*wins/tot):>8}% {tot:>4}")


if __name__ == "__main__":
    main()
