# -*- coding: utf-8 -*-
"""gen_custodes.py — Analysis + Runbook PDFs for the Custodes "Better Thing 2" showcase.

PDF-only (skips Word). Pulls the tapestry/units/plans from custodes_data.py and the LIVE win% +
forced-mission + opponent disposition from the rebuilt real-mission sim (mc_custodes_sim). Verdicts
are DERIVED from the simulated win% so the docs never drift from the sim.

  PYTHONPATH=tools:src python3 tools/gen_custodes.py
"""
import custodes_data as D
import mc_custodes_sim as S
import gen_pdf as G

GAMES, SEED = 6000, 11


def _rows():
    """Join sim results with the narrative matchups (same faction order)."""
    sim = S.results(GAMES, SEED)
    tot = wsum = 0
    rows = []
    for r, m in zip(sim, D.MATCHUPS):
        w = r["win"]
        tot += r["prev"]; wsum += r["prev"] * w
        verdict, cls = _verdict(w)
        rows.append(dict(m=m, win=w, disp=r["disp"], mission=r["cu_mission"],
                         opp_mission=r["op_mission"], verdict=verdict, cls=cls))
    return rows, round(wsum / tot)


def _verdict(w):
    if w >= 62:
        return "Favourable", "fav"
    if w >= 55:
        return "Lean favourable", "fav"
    if w >= 45:
        return "Coin-flip", "even"
    if w >= 40:
        return "Lean unfavourable", "unfav"
    return "Unfavourable", "unfav"


def _disp_name(key):
    return {"take-and-hold": "Take and Hold", "purge-the-foe": "Purge the Foe",
            "reconnaissance": "Reconnaissance", "priority-assets": "Priority Assets",
            "disruption": "Disruption"}.get(key, key)


def analysis(rows, weighted):
    S1 = G.section("Overview", G.p(f"<b>{G.esc(D.LIST_NAME)}</b>")
                   + G.p(G.esc(D.DETACHMENTS)) + G.p(G.esc(D.DISPOSITION))
                   + G.p(f'<span class="small">{G.esc(D.LIST_TOTAL)}</span>')
                   + G.p(G.esc(D.IDENTITY)))

    finding = G.finding(
        f"<b>Prevalence-weighted win rate: ~{weighted}%.</b> The rebuilt sim scores the REAL 11E "
        f"missions (your Force Disposition is <b>Priority Assets</b>; each opponent's is taken from real "
        f"list data, and the matrix hands each side a different mission). The key finding: the biggest "
        f"weighted drag is <b>not</b> the Orks body-hole but the <b>Purge-the-Foe matchups (Emperor's "
        f"Children, T'au)</b> — the matrix forces Priority-Assets Custodes onto <b>Vital Link</b> (needs "
        f"you to hold centre + steal the enemy home; hard for a non-castle-cracker) while those armies "
        f"get the strong <b>Destroyer's Wrath</b>. You out-<i>fight</i> them but lose the <i>mission</i>.")

    hdr = ["Faction / archetype", "Opp disposition", "You play", "Win%", "Read"]
    trows, cls = [], []
    for r in rows:
        m = r["m"]
        trows.append([f'{G.esc(m["faction"])} — <span class="small">{G.esc(m["archetype"])}</span>',
                      _disp_name(r["disp"]), G.esc(r["mission"]), f'{r["win"]}%', r["verdict"]])
        cls.append(["", "", "", r["cls"], r["cls"]])
    S2 = G.section("Matchups (Custodes = Priority Assets)", G.table(hdr, trows, cls))

    # bands derived from live win%
    fav = [r for r in rows if r["win"] >= 55]
    even = [r for r in rows if 45 <= r["win"] < 55]
    unf = [r for r in rows if r["win"] < 45]
    def names(g): return ", ".join(f'{x["m"]["faction"]} ({x["win"]}%)' for x in g) or "—"
    S3 = G.section("Bands", G.p(f'<span class="fav">Favourable:</span> {G.esc(names(fav))}')
                   + G.p(f'<span class="even">Coin-flip / even:</span> {G.esc(names(even))}')
                   + G.p(f'<span class="unfav">Unfavourable:</span> {G.esc(names(unf))}'))

    tap = "".join(G.sub(n, G.p(G.esc(t))) for n, t in D.RULES)
    S4 = G.section("The rules tapestry (DB/pack-verified)", tap)

    prof = G.table(["Piece", "Profile / rule", "Note"],
                   [[G.esc(a), G.esc(b), G.esc(c)] for a, b, c in D.VERIFIED_PROFILES])
    S5 = G.section("Verified profiles & buffs", prof)

    S6 = G.section("Bottom line", G.p(G.esc(D.RECORD_NOTE)))
    return [S1, finding, S2, S3, S4, S5, S6]


def runbook(rows, weighted):
    S1 = G.section("Mindset", G.p(G.esc(D.MINDSET)))
    tap = G.table(["Rule", "What it does"], [[G.esc(n), G.esc(t)] for n, t in D.RULES])
    S2 = G.section("Tapestry quick-reference", tap)

    plans = ""
    for r in rows:
        m = r["m"]
        head = (f'{m["faction"]} — <span class="{r["cls"]}">{r["win"]}% ({G.esc(r["verdict"])})</span> '
                f'· you play <b>{G.esc(r["mission"])}</b> vs their {_disp_name(r["disp"])} '
                f'(they play {G.esc(r["opp_mission"])})')
        body = G.p(f'<b>Deciding factor:</b> {G.esc(m["deciding"])}') + G.ul([G.esc(x) for x in m["plan"]])
        if m.get("watch"):
            body += G.p(f'<b>Watch:</b> {G.esc(m["watch"])}')
        plans += G.sub(head, body)
    S3 = G.section("Per-matchup battle plans", plans)

    units = G.table(["Unit (count)", "×", "Role / rules", "Pts"],
                    [[G.esc(n), G.esc(c), G.esc(role), G.esc(pts)] for n, c, role, pts in D.UNITS])
    S4 = G.section("The list", units)
    return [S1, S2, S3, S4]


def main():
    rows, weighted = _rows()
    a = G.render("custodes-analysis", analysis(rows, weighted))
    print("wrote", a)
    b = G.render("custodes-runbook", runbook(rows, weighted))
    print("wrote", b)


if __name__ == "__main__":
    main()
