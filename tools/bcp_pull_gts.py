#!/usr/bin/env python3
"""bcp_pull_gts.py — batch-pull the current-balance 40k GTs into per-event DBs (to thicken the meta corpus).

For each matching GT (bcp_corpus filters: >=5 rounds, >=28 players, in the balance window) that we don't
already have, pull the roster + army lists (token) + placings (deduped to the overall league) + pairings,
and build data/bcp/<slug>.sqlite. Skips events already present. Reuses bcp_pull (roster/lists) + bcp_db.

  PYTHONPATH=src python3 tools/bcp_pull_gts.py [--start 2026-07-27] [--end 2026-08-07]
"""
import sys, os, re, json, subprocess, argparse, collections
sys.path.insert(0, "tools")
import bcp_corpus as BC

HAVE = {"VAiZ9vjF61Rk": "lso2026", "r9vSaIhXEfwq": "nm2026", "Kp5qxem4qZk3": "denver-aug2026"}


def slug(name, eid):
    s = re.sub(r"[^a-z0-9]+", "-", (name or "").lower()).strip("-")[:32]
    return f"{s or 'ev'}-{eid[:6]}"


def placings(eid, roster_names):
    """Deduped overall-league placings: the one league where placing == points-desc rank."""
    rows = BC._paged("eventplacings", [("eventId", eid), ("limit", 99), ("expand[]", "user")], lambda r: r["id"])
    byl = collections.defaultdict(list)
    for r in rows:
        byl[r.get("leagueId")].append(r)
    best = None
    for lg, rs in byl.items():
        s = sorted(rs, key=lambda r: -(r.get("points") or 0))
        if sum(1 for i, r in enumerate(s, 1) if r.get("placing") == i) == len(rs):
            if best is None or (s[0].get("points") or 0) > best[1]:
                best = (lg, s[0].get("points") or 0)
    if not best:
        return []
    out = [{"placing": r["placing"], "points": r["points"], "player": BC._nm(r.get("user"))}
           for r in byl[best[0]]]
    return [x for x in out if x["player"]]


def pairings(eid):
    out = []
    for rnd in range(1, 7):
        for x in BC._paged("pairings", [("eventId", eid), ("round", rnd), ("pairingType", "Pairing"),
                                        ("limit", 99), ("expand[]", "player1"), ("expand[]", "player2"),
                                        ("expand[]", "player1Game"), ("expand[]", "player2Game")], lambda r: r["id"]):
            out.append({"round": rnd, "p1": BC._nm(x.get("player1")), "p2": BC._nm(x.get("player2")),
                        "p1_pts": (x.get("player1Game") or {}).get("gamePoints"),
                        "p2_pts": (x.get("player2Game") or {}).get("gamePoints")})
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--start", default="2026-07-27"); ap.add_argument("--end", default="2026-08-07")
    a = ap.parse_args()
    import glob as _glob
    evs = BC.enumerate_events(a.start, a.end, 5, 28)

    def have(e):
        if e["id"] in HAVE:
            return True
        return bool(_glob.glob(f"data/bcp/*-{e['id'][:6]}.sqlite"))   # already pulled (slug ends with eid[:6])

    new = [e for e in evs if not have(e)]
    print(f"# {len(evs)} GTs in window; {len(new)} new to pull ({len(evs)-len(new)} already on disk)", flush=True)
    done = []
    for i, e in enumerate(new):
        sg = slug(e.get("name"), e["id"]); eid = e["id"]
        try:
            subprocess.run([sys.executable, "tools/bcp_pull.py", eid, "--store", f"data/bcp/{sg}.json",
                            "--fetch-lists", f"data/bcp/{sg}-lists"], check=True, capture_output=True, timeout=600)
            rn = {p["name"] for p in json.load(open(f"data/bcp/{sg}.json"))["players"]}
            json.dump({"placings": placings(eid, rn)}, open(f"data/bcp/{sg}-placings.json", "w"))
            json.dump(pairings(eid), open(f"data/bcp/{sg}-pairings.json", "w"))
            subprocess.run([sys.executable, "tools/bcp_db.py", "build", f"data/bcp/{sg}-lists/_raw",
                            "--db", f"data/bcp/{sg}.sqlite", "--roster", f"data/bcp/{sg}.json"],
                           check=True, capture_output=True, timeout=300)
            import sqlite3
            nl = sqlite3.connect(f"data/bcp/{sg}.sqlite").execute("SELECT count(*) FROM lists").fetchone()[0]
            done.append(sg)
            print(f"  [{i+1}/{len(new)}] {sg:40} {e.get('totalPlayers'):>3}p  {nl} lists", flush=True)
        except Exception as ex:
            print(f"  [{i+1}/{len(new)}] {sg:40} ERR {str(ex)[:50]}", flush=True)
    print(f"\n# pulled {len(done)} events. Add to bcp_meta.EVENTS:\n  {done}")


if __name__ == "__main__":
    main()
