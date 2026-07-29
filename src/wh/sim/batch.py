"""Run YOUR list against the whole FIELD — every real full-text list in the listhammer archive (or a
faction's), each with its own disposition -> mission -> deployment map. Produces a compact scouting table:
the read, the biggest threat, and the un-removable piece, per real opponent list. This is how you prep for
an actual event: not vs 10 archetypes, but vs the specific lists people are bringing.

  python -m wh.sim.batch custodes [--faction Necrons] [--games 60]
"""
from __future__ import annotations

from . import runbook, rosters, listloader


def scout(me_name, faction=None, games=60, seed=11, limit=None):
    me_builder = getattr(rosters, me_name)
    lists = listloader.all_lists()
    if faction:
        lists = [L for L in lists if faction.lower() in L["faction"].lower()]
    if limit:
        lists = lists[:limit]
    rows = []
    for L in lists:
        try:
            r = runbook.build(me_builder, listloader.builder(index=L["i"]), games=games, seed=seed)
        except Exception as ex:
            rows.append(dict(L=L, err=str(ex)[:40]))
            continue
        head, _ = runbook._assess(r)
        pk = runbook._priority_kills(r)
        pa = runbook._play_around(r)
        rows.append(dict(L=L, read=head.split("—")[0].strip(),
                         threat=(pk[0]["name"] if pk else "-"),
                         wall=(pa[0]["name"] if pa else "-"),
                         missing=len(getattr(r["opp"], "_missing", []) or [])))
    return rows


_ORDER = {"FAVOURED": 0, "EVEN / GRINDY": 1, "ATTRITION-NEGATIVE": 2, "HARD": 3}


def report(me_name, rows):
    ok = [r for r in rows if "err" not in r]
    L = [f"FIELD SCOUT — {me_name} vs {len(ok)} real archive lists (each with its own mission/deployment)",
         f"  {'FACTION':22} {'DETACHMENT':22} {'REC':>5} {'READ':16} BIGGEST THREAT  / CAN'T REMOVE"]
    for r in sorted(ok, key=lambda r: (_ORDER.get(r["read"], 9), r["L"]["faction"])):
        Lm = r["L"]
        miss = f"  [~{r['missing']} unmodelled]" if r["missing"] else ""
        L.append(f"  {Lm['faction'][:22]:22} {Lm['detachment'][:22]:22} {str(Lm['wins'])+'-'+str(Lm['losses']):>5} "
                 f"{r['read']:16} {r['threat'][:18]:18} / {r['wall'][:18]}{miss}")
    bad = [r for r in rows if "err" in r]
    if bad:
        L += ["", f"({len(bad)} lists skipped — load/parse issues)"]
    # tally
    from collections import Counter
    tally = Counter(r["read"] for r in ok)
    L += ["", "Field summary: " + "  ".join(f"{k}: {tally.get(k,0)}" for k in _ORDER)]
    return "\n".join(L)


def main():
    import argparse
    ap = argparse.ArgumentParser(description="Scout your list against the whole archive field.")
    ap.add_argument("me")
    ap.add_argument("--faction", default=None, help="filter to one faction (substring)")
    ap.add_argument("--games", type=int, default=60)
    ap.add_argument("--limit", type=int, default=None)
    a = ap.parse_args()
    print(report(a.me, scout(a.me, a.faction, a.games, limit=a.limit)))


if __name__ == "__main__":
    main()
