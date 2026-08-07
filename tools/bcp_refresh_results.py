#!/usr/bin/env python3
"""bcp_refresh_results.py — (re)build placings.json + pairings.json for every on-disk BCP event, robustly.

Fixes two ways the old placings() silently produced empty standings (which drop a whole event from the
placing-based corpus in bcp_meta):
  1) It required a league where placing == points-desc-rank for EVERY row — one tie broke it. Now we pick the
     league that actually looks like INDIVIDUAL standings (distinct placings ≈ #players) and trust `placing`.
  2) Some GTs post NO eventplacings rows at all (the TO entered results only as pairings). Now, when
     eventplacings has no clean individual league, we DERIVE standings from the pairings (rank by total game
     points) — recovering events like ringkriege / calgary that have real games but no posted standings.
Team events (each placing shared by many players — e.g. WATC) have no clean individual league and no reliable
per-player total, so they stay empty here and are excluded from the placing corpus (correct).

  PYTHONPATH=src python3 tools/bcp_refresh_results.py            # refresh ALL on-disk events
  PYTHONPATH=src python3 tools/bcp_refresh_results.py <slug>...  # only these
Idempotent; safe to re-run (e.g. after an upcoming event finishes and posts results).
"""
import sys, os, json, glob, collections
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import bcp_corpus as BC

RATIO = 0.80          # a league is INDIVIDUAL standings if this fraction of placings are distinct


def _eventplacings(eid):
    rows = BC._paged("eventplacings", [("eventId", eid), ("limit", 99), ("expand[]", "user")], lambda r: r["id"])
    byl = collections.defaultdict(list)
    for r in rows:
        byl[r.get("leagueId")].append(r)
    best = None                                            # (top_points, rows) of the best individual league
    for rs in byl.values():
        pl = [r.get("placing") for r in rs if r.get("placing") is not None]
        if not pl or len(set(pl)) / len(rs) < RATIO:
            continue                                       # team / bucketed league — skip
        top = max((r.get("points") or 0) for r in rs)
        if best is None or top > best[0]:
            best = (top, rs)
    if not best:
        return []
    out = [{"placing": r["placing"], "points": r.get("points"), "player": BC._nm(r.get("user"))} for r in best[1]]
    return [x for x in out if x["player"]]


def _pairings(eid):
    out = []
    for rnd in range(1, 9):
        got = BC._paged("pairings", [("eventId", eid), ("round", rnd), ("pairingType", "Pairing"),
                                     ("limit", 99), ("expand[]", "player1"), ("expand[]", "player2"),
                                     ("expand[]", "player1Game"), ("expand[]", "player2Game")], lambda r: r["id"])
        for x in got:
            out.append({"round": rnd, "p1": BC._nm(x.get("player1")), "p2": BC._nm(x.get("player2")),
                        "p1_pts": (x.get("player1Game") or {}).get("gamePoints"),
                        "p2_pts": (x.get("player2Game") or {}).get("gamePoints")})
    return out


def _derive_from_pairings(pairings):
    """Rank players by total game points across rounds — a standings proxy when no eventplacings are posted."""
    pts, played = collections.Counter(), collections.Counter()
    for x in pairings:
        for who, p in (("p1", "p1_pts"), ("p2", "p2_pts")):
            nm = x.get(who)
            if nm and x.get(p) is not None:
                pts[nm] += x[p]; played[nm] += 1
    if not pts:
        return []
    ranked = sorted(pts, key=lambda p: -pts[p])
    return [{"placing": i, "points": pts[p], "player": p, "derived": True} for i, p in enumerate(ranked, 1)]


def refresh(slug):
    roster = f"data/bcp/{slug}.json"
    if not os.path.exists(roster):
        return None
    eid = json.load(open(roster))["event"]["id"]
    pairings = _pairings(eid)
    json.dump(pairings, open(f"data/bcp/{slug}-pairings.json", "w"))
    placings = _eventplacings(eid)
    src = "eventplacings"
    if not placings:
        placings = _derive_from_pairings(pairings)
        src = "derived-from-pairings" if placings else "none"
    json.dump({"placings": placings}, open(f"data/bcp/{slug}-placings.json", "w"))
    dec = sum(1 for x in pairings if x.get("p1_pts") is not None and x.get("p2_pts") is not None
              and x["p1_pts"] != x["p2_pts"])
    return len(placings), dec, src


def main():
    slugs = sys.argv[1:] or sorted(os.path.basename(p)[:-5] for p in glob.glob("data/bcp/*.json")
                                   if not p.endswith(("-placings.json", "-pairings.json"))
                                   and os.path.exists(p[:-5] + ".sqlite"))
    tot_pl = tot_ev = 0
    for s in slugs:
        r = refresh(s)
        if r is None:
            continue
        npl, dec, src = r
        tot_pl += npl; tot_ev += 1 if npl else 0
        print(f"  {s[:44]:44} placings={npl:4} decided={dec:4}  [{src}]", flush=True)
    print(f"\n# {tot_ev} events now have standings; {tot_pl} placing rows total", flush=True)


if __name__ == "__main__":
    main()
