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

import os, subprocess, html as _html

from . import runbook, optimize, rosters, strategy as St
from .gauntlet import tapestry, OPPONENTS, ME_META
import db

_READ_CLASS = {"FAVOURED": "fav", "EVEN": "even", "ATTRITION": "attr", "HARD": "hard"}


def _read_key(read):
    for k in _READ_CLASS:
        if read.startswith(k):
            return _READ_CLASS[k]
    return "even"


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


def gather(me_name="custodes", games=250, opt_opp="necrons", seed=11):
    """Run the sim ONCE and collect the structured pieces (tapestry, map rows, runbooks, fixes)."""
    me_builder = getattr(rosters, me_name)
    slug, dets = ME_META.get(me_name, (getattr(me_builder(), "slug", me_name), ("",)))
    tap = tapestry(me_builder(), slug, dets[0])
    if len(dets) > 1:
        try:
            extra = db.strats(slug).get(dets[1], {})
            tap += f"\n\n## {dets[1]} stratagems ({len(extra)}) — DB\n" + "\n".join(
                f"- **{nm}** ({s.get('cp','?')}CP) — {' '.join(str(s.get('effect','')).split())[:150]}"
                for nm, s in extra.items())
        except Exception:
            pass
    rows, books = [], []
    for opp in OPPONENTS:
        r = runbook.build(me_builder, getattr(rosters, opp), games=games, seed=seed)
        rows.append(_matchup_row(me_name, opp, r))
        books.append(runbook.report(r))
    opt = optimize.optimize(me_builder, getattr(rosters, opt_opp),
                            screen=max(400, games // 2), final=games, seed=seed)
    fixes = optimize.report(opt)
    return dict(name=me_builder().name, me=me_name, tap=tap, rows=rows, books=books,
                fixes=fixes, opt_opp=opt_opp, games=games)


def render_markdown(P):
    out = [f"# TOURNAMENT DOSSIER — {P['name']}", "", P["tap"], "",
           "# MATCHUP MAP", "", f"  {'ARCHETYPE (list)':28} {'READ':18} {'POSTURE':9} BIGGEST THREAT"]
    for row in P["rows"]:
        out.append(f"  {row['opp']+' ('+row['arch']+')':28} {row['read']:18} {row['posture']:9} {row['threat']}")
    out += ["", "# RUNBOOKS (per archetype)", ""]
    for b in P["books"]:
        out += ["```", b, "```", ""]
    out += ["# LIST FIXES — tested swap + detachment recommendations", "",
            f"(optimizer vs {P['opt_opp']})", "```", P["fixes"], "```"]
    return "\n".join(out)


_CSS = """
body{font-family:'DejaVu Sans',Arial,sans-serif;color:#1a1a1a;max-width:920px;margin:0 auto;padding:24px;line-height:1.4}
h1{font-size:22px;border-bottom:3px solid #8a6d1a;padding-bottom:6px}
h2{font-size:15px;color:#5a4a12;margin-top:22px}
.sub{color:#666;font-size:12px;margin:2px 0 16px}
table.map{border-collapse:collapse;width:100%;font-size:13px;margin:8px 0 18px}
table.map th{background:#2a2a2a;color:#fff;text-align:left;padding:6px 9px}
table.map td{padding:5px 9px;border-bottom:1px solid #ddd}
.pill{padding:2px 8px;border-radius:10px;font-weight:bold;font-size:11px;color:#fff;white-space:nowrap}
.fav{background:#1f8a3b}.even{background:#2a6db0}.attr{background:#b8860b}.hard{background:#b23030}
.book{border:1px solid #ccc;border-left:4px solid #8a6d1a;border-radius:4px;padding:10px 14px;margin:12px 0;
 white-space:pre-wrap;font-family:'DejaVu Sans Mono',monospace;font-size:11px;page-break-inside:avoid}
.book .rb-title{font-weight:bold;font-size:13px;color:#5a4a12}
pre{white-space:pre-wrap;font-family:'DejaVu Sans Mono',monospace;font-size:11px;background:#f6f4ee;padding:10px;border-radius:4px}
.note{background:#fff6e0;border:1px solid #e0c060;padding:8px 12px;border-radius:4px;font-size:12px;margin:10px 0}
"""


def render_html(P):
    e = _html.escape
    h = [f"<html><head><meta charset='utf-8'><title>Dossier — {e(P['name'])}</title><style>{_CSS}</style></head><body>",
         f"<h1>Tournament Dossier — {e(P['name'])}</h1>",
         f"<div class='sub'>{len(P['rows'])} archetypes · {P['games']} games each · mechanistic matchup analysis "
         "(not a win% prediction — the values are the sim's internal scale)</div>",
         "<div class='note'>How to use: the MAP is your at-a-glance cheat sheet; the RUNBOOKS are your per-archetype "
         "prep (who to kill, what to ignore, what to protect, the trap). The sim maps the DYNAMICS of each matchup.</div>",
         "<h2>Matchup Map</h2>",
         "<table class='map'><tr><th>Archetype (list)</th><th>Read</th><th>Posture</th><th>Biggest threat</th></tr>"]
    for row in P["rows"]:
        h.append(f"<tr><td>{e(row['opp'])} <span style='color:#888'>({e(row['arch'])})</span></td>"
                 f"<td><span class='pill {_read_key(row['read'])}'>{e(row['read'])}</span></td>"
                 f"<td>{e(row['posture'])}</td><td>{e(row['threat'])}</td></tr>")
    h.append("</table>")
    # tapestry
    h.append("<h2>Your Tapestry</h2><pre>" + e(P["tap"]) + "</pre>")
    # runbooks
    h.append("<h2>Runbooks (per archetype)</h2>")
    for b in P["books"]:
        lines = b.split("\n")
        title = e(lines[0]); rest = e("\n".join(lines[1:]))
        h.append(f"<div class='book'><span class='rb-title'>{title}</span>\n{rest}</div>")
    h.append("<h2>List Fixes — tested swaps + detachment test</h2><pre>" + e(P["fixes"]) + "</pre>")
    h.append("</body></html>")
    return "\n".join(h)


def build(me_name="custodes", games=250, opt_opp="necrons", seed=11, pdf=True):
    P = gather(me_name, games, opt_opp, seed)
    d = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(
        os.path.abspath(__file__))))), "reports")
    os.makedirs(d, exist_ok=True)
    md_path = os.path.join(d, f"dossier-{me_name}.md")
    open(md_path, "w").write(render_markdown(P))
    pdf_path = None
    if pdf:
        html_path = os.path.join(d, f"dossier-{me_name}.html")
        open(html_path, "w", encoding="utf-8").write(render_html(P))
        try:
            subprocess.run(["soffice", "--headless", "--convert-to", "pdf", "--outdir", d, html_path],
                           check=True, capture_output=True, timeout=120)
            pdf_path = os.path.join(d, f"dossier-{me_name}.pdf")
        except Exception as ex:
            print(f"(pdf render skipped: {ex})")
    return render_markdown(P), md_path, pdf_path


def main():
    import argparse
    ap = argparse.ArgumentParser(description="Generate the full tournament dossier for a list.")
    ap.add_argument("me", nargs="?", default="custodes")
    ap.add_argument("--games", type=int, default=250)
    ap.add_argument("--opt", default="necrons")
    a = ap.parse_args()
    doc, md_path, pdf_path = build(a.me, a.games, a.opt)
    print(doc)
    print(f"\n[markdown: {md_path}]" + (f"\n[PDF: {pdf_path}]" if pdf_path else ""))


if __name__ == "__main__":
    main()
