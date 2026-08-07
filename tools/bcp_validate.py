#!/usr/bin/env python3
"""bcp_validate.py — validate the sim against REAL tournament results (the real ground truth).

Every DECIDED, fully-simmable BCP pairing is a real game with a known winner + score, across the whole
meta AND both players' real DISPOSITIONS (army x disposition vs army x disposition, asymmetric via
matrix.yaml). This sims each pairing and asks: does ANY sim signal RANK real winners above losers?

Metrics (rank-based AUC is the key one — immune to a calibration offset; 0.5 = no signal, >0.5 =
predictive, <0.5 = anti-predictive):
  - AUC(sim win%  -> real winner), AUC(sim VP-margin -> real winner)
  - Pearson(sim VP-margin, real VP-margin)   - directional accuracy   - reliability curve
  - bias: mean predicted p1-win% vs real p1-win-rate

  PYTHONPATH=src python3 tools/bcp_validate.py <event>[,<event>...] [--sample N] [--games G] [--seed S]
"""
import sys, os, json, sqlite3, argparse, random
sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "src"))
import numpy as np
from wh.sim import bcp, run
from wh.sim import listloader as L


def _ok(row):
    return bool(row) and row["parse_ok"] and L._FACTION_SLUG.get(row["faction"]) and row["n_units"] > 0


def _auc(scores, labels):
    """Mann-Whitney AUC: P(score(win) > score(loss)), ties=0.5."""
    pos = np.array([s for s, l in zip(scores, labels) if l], float)
    neg = np.array([s for s, l in zip(scores, labels) if not l], float)
    if not len(pos) or not len(neg):
        return float("nan")
    gt = (pos[:, None] > neg[None, :]).sum()
    eq = (pos[:, None] == neg[None, :]).sum()
    return float((gt + 0.5 * eq) / (len(pos) * len(neg)))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("events")
    ap.add_argument("--sample", type=int, default=0, help="0 = all simmable pairings")
    ap.add_argument("--games", type=int, default=30); ap.add_argument("--seed", type=int, default=7)
    a = ap.parse_args()
    pairs = []
    for ev in a.events.split(","):
        db = f"data/bcp/{ev}.sqlite"
        con = sqlite3.connect(db); con.row_factory = sqlite3.Row
        lists = {r["player"]: r for r in con.execute("SELECT * FROM lists")}
        for p in json.load(open(f"data/bcp/{ev}-pairings.json")):
            if (p.get("p1_pts") is not None and p.get("p2_pts") is not None and p["p1_pts"] != p["p2_pts"]
                    and _ok(lists.get(p["p1"])) and _ok(lists.get(p["p2"]))):
                pairs.append((db, lists[p["p1"]]["list_id"], lists[p["p2"]]["list_id"],
                              p["p1_pts"] > p["p2_pts"], p["p1_pts"] - p["p2_pts"]))
    random.seed(a.seed); random.shuffle(pairs)
    if a.sample:
        pairs = pairs[:a.sample]
    print(f"# validating {len(pairs)} real pairings @ {a.games} games each ({a.events})", flush=True)

    winp, vpm, won, rmarg = [], [], [], []
    for i, (db, l1, l2, p1_won, rm) in enumerate(pairs):
        try:
            s = run.simulate(bcp.builder(l1, db=db, side="A"), bcp.builder(l2, db=db, side="B"),
                             games=a.games, seed=a.seed)
        except Exception:
            continue
        winp.append(s["win"]); vpm.append(s["my_vp"] - s["opp_vp"]); won.append(p1_won); rmarg.append(rm)
        if (i + 1) % 50 == 0:
            print(f"  ... {i+1}/{len(pairs)}", flush=True)
    n = len(won)
    if not n:
        print("no pairings simmed"); return
    acc = np.mean([(w > 50) == wn for w, wn in zip(winp, won)])
    print(f"\n# RESULTS ({n} pairings)")
    print(f"  directional accuracy (win%>50 == real winner): {round(100*acc)}%   (coin-flip 50)")
    print(f"  AUC  sim win%     -> real winner : {_auc(winp, won):.3f}   (0.5 none, >0.5 predictive)")
    print(f"  AUC  sim VP-margin-> real winner : {_auc(vpm, won):.3f}")
    print(f"  Pearson(sim VP-margin, real VP-margin): {np.corrcoef(vpm, rmarg)[0,1]:.3f}")
    print(f"  bias: mean predicted p1-win% {np.mean(winp):.0f}  vs  real p1-win-rate {100*np.mean(won):.0f}%")
    print("\n  RELIABILITY (sim win% bin -> real win%):")
    w = np.array(winp); wn = np.array(won, float)
    for b in range(0, 100, 10):
        m = (w >= b) & (w < b + 10)
        if m.sum():
            print(f"    {b:>3}-{b+9:<3} real {round(100*wn[m].mean()):>3}%  n={int(m.sum())}")


if __name__ == "__main__":
    main()
