"""The DOSSIER — the full tournament-prep deliverable for a list. Assembles, into one document:
  1. YOUR TAPESTRY   — army rule + every chosen detachment's stratagems + the rule->engine mapping.
  2. MATCHUP MAP     — one row per meta archetype: the read, your posture, the single biggest threat,
                       and the one-line game plan. The "how does my list do into X" overview.
  3. RUNBOOKS        — the full per-archetype play guide (priority kills / play-around / workhorses /
                       liabilities / stratagems / the trap).
  4. LIST FIXES      — the optimizer's TESTED swap + detachment recommendations on a chosen matchup.

Mechanistic, not a win% oracle (see the sim STATUS). Writes reports/dossier-<me>.md.

  python -m wh.sim.dossier custodes [--games 250] [--opt necrons]
"""
from __future__ import annotations

import os

from . import runbook, optimize, rosters, strategy as St
from .gauntlet import tapestry, OPPONENTS, ME_META
import db


def _read_short(head):
    return head.split("—")[0].strip()


def _matchup_row(me_name, opp, r):
    arch = St.archetype(getattr(rosters, opp)())
    head, wincon = runbook._assess(r)
    pk = runbook._priority_kills(r)
    pa = runbook._play_around(r)
    threat = pk[0]["name"] if pk else (pa[0]["name"] if pa else "-")
    posture = r["my_strategy"].name if r["my_strategy"] else "balanced"
    return dict(opp=opp, arch=arch, read=_read_short(head), threat=threat, posture=posture, wincon=wincon)


def build(me_name="custodes", games=250, opt_opp="necrons", seed=11):
    me_builder = getattr(rosters, me_name)
    slug, dets = ME_META.get(me_name, (getattr(me_builder(), "slug", me_name), ("",)))
    out = [f"# TOURNAMENT DOSSIER — {me_builder().name}", ""]

    # 1. tapestry (army rule + BOTH detachments' strats)
    out.append(tapestry(me_builder(), slug, dets[0]))
    if len(dets) > 1:
        try:
            extra = db.strats(slug).get(dets[1], {})
            out += ["", f"## {dets[1]} stratagems ({len(extra)}) — DB"]
            out += [f"- **{nm}** ({s.get('cp','?')}CP) — {' '.join(str(s.get('effect','')).split())[:150]}"
                    for nm, s in extra.items()]
        except Exception:
            pass

    # 2+3. run every matchup once (reuse the sim for both the map row and the full runbook)
    rows, books = [], []
    for opp in OPPONENTS:
        r = runbook.build(me_builder, getattr(rosters, opp), games=games, seed=seed)
        rows.append(_matchup_row(me_name, opp, r))
        books.append(runbook.report(r))

    out += ["", "# MATCHUP MAP", "",
            f"  {'ARCHETYPE (list)':28} {'READ':16} {'POSTURE':9} BIGGEST THREAT"]
    for row in rows:
        out.append(f"  {row['opp']+' ('+row['arch']+')':28} {row['read']:16} {row['posture']:9} {row['threat']}")
    out += ["", "Read the runbooks below for the full plan per archetype."]

    out += ["", "# RUNBOOKS (per archetype)", ""]
    for b in books:
        out += ["```", b, "```", ""]

    # 4. list fixes
    out += ["# LIST FIXES — tested swap + detachment recommendations", "",
            f"(optimizer vs {opt_opp})", "```"]
    r = optimize.optimize(me_builder, getattr(rosters, opt_opp),
                          screen=max(400, games // 2), final=games, seed=seed)
    out += [optimize.report(r), "```"]

    doc = "\n".join(out)
    d = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(
        os.path.abspath(__file__))))), "reports")
    os.makedirs(d, exist_ok=True)
    path = os.path.join(d, f"dossier-{me_name}.md")
    open(path, "w").write(doc)
    return doc, path


def main():
    import argparse
    ap = argparse.ArgumentParser(description="Generate the full tournament dossier for a list.")
    ap.add_argument("me", nargs="?", default="custodes")
    ap.add_argument("--games", type=int, default=250)
    ap.add_argument("--opt", default="necrons")
    a = ap.parse_args()
    doc, path = build(a.me, a.games, a.opt)
    print(doc)
    print(f"\n[written to {path}]")


if __name__ == "__main__":
    main()
