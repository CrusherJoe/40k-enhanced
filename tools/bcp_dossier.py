#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""bcp_dossier.py — full field dossier: YOUR list vs the real event, by archetype.

For each archetype in the event (data/bcp/<event>-archetypes.json), pick a parseable
representative list, sim YOUR army (a rosters handle, default death_rnr) against it, and
weave the sim read together with the hand-written archetype verdict/how-to-play. Writes a
markdown dossier: a MATCHUP MAP (one row per archetype, sorted by field prevalence) plus
full RUNBOOKS for the most common archetypes.

  PYTHONPATH=src python3 tools/bcp_dossier.py [me] [--min 2] [--games 120] [--books 14]
"""
import argparse, json, os, sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "src"))
from wh.sim import rosters, bcp, runbook
from wh.sim.runbook import _assess

REC = "data/bcp/lso2026-archetypes.json"


def _rep_build(arch):
    """A build thunk for the first parseable list in an archetype (its representative)."""
    for p in arch["players"]:
        try:
            b = bcp.builder(p["list_id"])
            b()                      # probe: raises if unparseable / no units
            return b, p["player"]
        except Exception:
            continue
    return None, None


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("me", nargs="?", default="death_rnr")
    ap.add_argument("--min", type=int, default=2, help="min archetype size to include")
    ap.add_argument("--games", type=int, default=120)
    ap.add_argument("--books", type=int, default=14, help="how many top archetypes get a full runbook")
    ap.add_argument("--out", default=None)
    a = ap.parse_args()

    rec = json.load(open(REC, encoding="utf-8"))
    me_builder = getattr(rosters, a.me)
    me_name = me_builder().name
    arches = sorted([(k, v) for k, v in rec["archetypes"].items() if v["size"] >= a.min],
                    key=lambda kv: -kv[1]["size"])

    rows, books = [], []
    for key, arch in arches:
        build_opp, rep = _rep_build(arch)
        if not build_opp:
            rows.append({"key": key, "n": arch["size"], "verdict": arch["verdict"] or "(TBD)",
                         "read": "—", "margin": None, "rep": "(unparseable reps)", "arch": arch})
            continue
        r = runbook.build(me_builder, build_opp, games=a.games)
        head, wincon = _assess(r)
        margin = (r["ctrl"][3] + r["ctrl"][4]) / 2 - (r["octrl"][3] + r["octrl"][4]) / 2
        rows.append({"key": key, "n": arch["size"], "verdict": arch["verdict"] or "(TBD)",
                     "read": head.split(" —")[0].split()[0], "margin": margin, "rep": rep,
                     "arch": arch, "r": r})
        sys.stderr.write(f"# {key}: {rows[-1]['read']} (rep {rep})\n"); sys.stderr.flush()

    # ---- render markdown ----
    disp = me_builder().disposition
    L = [f"# Field Dossier — {me_name}",
         f"*vs the {rec['event']} field ({rec['n_lists']} lists / {rec['n_archetypes']} archetypes). "
         f"Your disposition: **{disp}**. {a.games} games per matchup.*",
         "",
         "> Sim reads are **directional** (see the sim STATUS) — trust the VERDICT + how-to-play "
         "(hand-verified from the Knights seat) as the plan; the sim read is a mechanistic cross-check.",
         "",
         "## Matchup map",
         "",
         "| N | Archetype | Verdict | Sim | Board |",
         "|--:|-----------|---------|-----|------:|"]
    for x in rows:
        mg = f"{x['margin']:+.2f}" if x["margin"] is not None else "—"
        L.append(f"| {x['n']} | {x['key']} | {x['verdict']} | {x['read']} | {mg} |")
    covered = sum(x["n"] for x in rows)
    L += ["", f"*Covers {covered}/{rec['n_lists']} lists ({100*covered//rec['n_lists']}%). "
          f"Board = your avg objective margin R4-5 (mechanistic).*", "", "---", "", "## Runbooks",
          "*The most common archetypes you'll face, most prevalent first.*", ""]
    for x in rows[:a.books]:
        if "r" not in x:
            continue
        L += [f"### {x['key']}  ·  {x['n']} in field  ·  {x['verdict']}", ""]
        if x["arch"]["play"]:
            L += [f"**How to play:** {x['arch']['play']}", ""]
        L += ["```", runbook.report(x["r"]).rstrip(), "```", ""]

    out = a.out or f"reports/{a.me}-field-dossier.md"
    os.makedirs(os.path.dirname(out) or ".", exist_ok=True)
    open(out, "w", encoding="utf-8").write("\n".join(L))
    print(f"\n# dossier -> {out}  ({len(rows)} archetypes, {sum(1 for x in rows if 'r' in x)} simmed)",
          file=sys.stderr)


if __name__ == "__main__":
    main()
