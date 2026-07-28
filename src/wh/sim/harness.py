"""Anchor-gated regression harness — the calibration backbone. Runs Custodes vs every opponent and scores
the sim against the REAL listhammer win rates (gauntlet.ANCHORS). Prints sim / real / gap per matchup and a
single weighted error number (by sample size — the large-sample anchors count more; the 22-24 game ones are
noisy and down-weighted). Use it before/after every calibration change so a fix that helps one matchup can't
silently thrash another.

  python -m wh.sim.harness [--games 200] [--fast]       (--fast = the large-sample anchors only)
"""
from __future__ import annotations

import math

from . import run, rosters
from .gauntlet import ANCHORS

# large-sample anchors (>=40 games) drive calibration; small ones are shown but lightly weighted.
FAST = ["necrons", "orks", "tau", "tyranids", "dark_angels", "blood_angels", "thousand_sons"]


def scorecard(games=200, seed=11, subset=None):
    opps = subset or list(ANCHORS)
    rows = []
    for o in opps:
        real, n = ANCHORS[o]
        w = run.simulate(rosters.custodes, getattr(rosters, o), games=games, seed=seed)["win"]
        wt = math.sqrt(n)                                 # weight by sample size (sqrt keeps it gentle)
        rows.append(dict(opp=o, sim=w, real=real, gap=w - real, n=n, wt=wt))
    werr = sum(abs(r["gap"]) * r["wt"] for r in rows) / sum(r["wt"] for r in rows)
    maxgap = max(rows, key=lambda r: abs(r["gap"]))
    return dict(rows=rows, werr=werr, maxgap=maxgap, games=games)


def report(sc):
    L = [f"ANCHOR SCORECARD ({sc['games']} games/matchup)  —  sim vs real listhammer",
         f"  {'opponent':14} {'sim':>4} {'real':>5} {'gap':>5} {'n':>4}"]
    for r in sorted(sc["rows"], key=lambda r: r["gap"]):
        flag = "  <-- worst" if r is sc["maxgap"] else ("  (small n)" if r["n"] < 40 else "")
        L.append(f"  {r['opp']:14} {r['sim']:>3}% {r['real']:>4.0f}% {r['gap']:>+4.0f} {r['n']:>4}{flag}")
    L += ["", f"  WEIGHTED ERROR (sqrt-sample-weighted mean |gap|): {sc['werr']:.1f}  "
          f"(lower is better; worst matchup {sc['maxgap']['opp']} {sc['maxgap']['gap']:+.0f})"]
    return "\n".join(L)


def main():
    import argparse
    ap = argparse.ArgumentParser(description="Score the sim against the real listhammer anchors.")
    ap.add_argument("--games", type=int, default=200)
    ap.add_argument("--fast", action="store_true", help="large-sample anchors only")
    a = ap.parse_args()
    print(report(scorecard(a.games, subset=FAST if a.fast else None)))


if __name__ == "__main__":
    main()
