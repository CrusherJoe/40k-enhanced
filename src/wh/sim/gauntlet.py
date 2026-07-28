"""THE GAUNTLET — run a list through the full evaluation, the repeatable "analyze this list" flow for the
positional sim. Three sections:
  1. TAPESTRY REPORT   — army rule + detachment rule + stratagems (from the DB) and the sim-modelled unit
                         abilities, so you can eyeball that the rules are represented before trusting output.
  2. PER-MATCHUP        — win% + weakness findings vs every known opponent (grindy matchups trustworthy,
                         fast/alpha directional — flagged per row).
  3. IMPROVEMENTS       — optimize()'s tested swap recommendations + detachment test on a chosen matchup.

  python -m wh.sim.gauntlet custodes [--games 1500] [--opt necrons]

Games default 1500 (stable win% ~±2-3%, ~1 min/matchup). Bump to 5000 for the calibrated standard on a
specific matchup. The report is printed and written to reports/gauntlet-<me>.md.
"""
from __future__ import annotations

import os, sys, collections

sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(
    os.path.abspath(__file__))))), "tools"))
import db

from . import run, analyze, optimize, rosters

# the meta field (opponent roster builders) + which matchups the sim reads to-the-point vs directional
OPPONENTS = ["necrons", "orks", "space_marines", "thousand_sons", "tyranids",
             "drukhari", "aeldari", "tau", "dark_angels", "blood_angels"]
GRINDY = {"necrons", "orks", "space_marines", "thousand_sons", "tyranids"}   # win% trustworthy
# me-roster -> (bsdata slug, detachment name) for the tapestry pull
ME_META = {"custodes": ("adeptus-custodes", "Shield Host")}


def tapestry(me_army, slug, detachment):
    L = [f"# 1. TAPESTRY — {me_army.name}",
         f"Faction: {slug}  |  Detachment: {detachment}  |  Disposition: {me_army.disposition}", ""]
    # army rule + detachment rule text (from the DB)
    L.append("## Army & detachment rules (DB)")
    for rn in ("Martial Ka'tah", "Martial Mastery"):
        try:
            txt = db.rule(slug, rn)
            L.append(f"- **{rn}** — {_one(txt, 400)}")
        except Exception:
            pass
    # detachment stratagems
    try:
        strats = db.strats(slug)[detachment]
        L += ["", f"## {detachment} stratagems ({len(strats)}) — DB"]
        for nm, s in strats.items():
            L.append(f"- **{nm}** ({s.get('cp','?')}CP, {s.get('type','')}) — {_one(s.get('effect',''), 160)}")
    except Exception as e:
        L.append(f"(stratagems unavailable: {e})")
    # how the sim MODELS it (so you can see rule -> engine mapping)
    L += ["", "## Sim-modelled tapestry (per unit)"]
    for u in me_army.units:
        tags = _ability_tags(u)
        if tags:
            L.append(f"- {u.name:26} {', '.join(tags)}")
    return "\n".join(L)


def _one(txt, n):
    return " ".join(str(txt).split())[:n].strip()


def _ability_tags(u):
    t = []
    ab = u.abilities
    if ab.get("crit_hit"):
        t.append(f"Martial Mastery (crit {ab['crit_hit']}+)")
    if ab.get("reroll_hits"):
        t.append(f"reroll hits({ab['reroll_hits']})")
    if ab.get("reroll_wounds"):
        t.append(f"reroll wounds({ab['reroll_wounds']})")
    if ab.get("reroll_charge"):
        t.append("reroll charge")
    if ab.get("shadowfield"):
        t.append("shadowfield 2++")
    if ab.get("comeback"):
        t.append(f"return {int(ab['comeback']*100)}%")
    if u.fnp:
        t.append(f"FNP {u.fnp}")
    if u.damage_reduction:
        t.append(f"-{u.damage_reduction} dmg")
    if u.reanimate:
        t.append(f"reanimate {int(u.reanimate*100)}%")
    if u.deep_strike:
        t.append("deep strike")
    return t


def matchups(me_builder, games, seed=11):
    rows = []
    for opp in OPPONENTS:
        ob = getattr(rosters, opp)
        win = run.simulate(me_builder, ob, games=games, seed=seed)["win"]
        d = analyze.diagnose(me_builder, ob, games=games, seed=seed)
        rows.append(dict(opp=opp, win=win, find=_findings(d), grindy=opp in GRINDY))
    rows.sort(key=lambda r: -r["win"])
    return rows


def _findings(d):
    g = d["games"]
    surv = sorted(((nm, 100 * c / (g * d["opp_counts"][nm])) for nm, c in d["survivors"].items()),
                  key=lambda x: -x[1])
    mine = sorted(((nm, 100 * c / (g * d["me_counts"][nm])) for nm, c in d["my_survivors"].items()),
                  key=lambda x: x[1])
    ctrl = [d["ctrl"][r][0] / g for r in range(1, 6)]
    cant = ", ".join(f"{nm} {p:.0f}%" for nm, p in surv[:2] if p >= 60)
    dead = ", ".join(f"{nm} {p:.0f}%" for nm, p in mine[:2] if p < 35)
    return dict(ctrl=ctrl, cant=cant or "-", dead=dead or "-")


def matchup_report(rows):
    L = ["# 2. PER-MATCHUP ANALYSIS", "",
         f"  {'OPPONENT':16} {'WIN%':>5}  {'READ':11} {'BOARD R1→R5':14} CANT-REMOVE / YOUR DEAD WEIGHT"]
    for r in rows:
        read = "to-the-pt" if r["grindy"] else "DIRECTIONAL"
        board = " ".join(f"{v:.1f}" for v in r["find"]["ctrl"])
        L.append(f"  {r['opp']:16} {r['win']:>4}%  {read:11} {board:14} "
                 f"can't:{r['find']['cant']}  | dead:{r['find']['dead']}")
    grindy = [r for r in rows if r["grindy"]]
    avg = round(sum(r["win"] for r in grindy) / max(1, len(grindy)))
    L += ["", f"Grindy-matchup average (trustworthy band): {avg}% across {len(grindy)} opponents. "
          "Fast/alpha rows are DIRECTIONAL — read the ranking + findings, not the exact %."]
    return "\n".join(L)


def run_gauntlet(me_name="custodes", games=1500, opt_opp="necrons", seed=11):
    me_builder = getattr(rosters, me_name)
    slug, det = ME_META.get(me_name, (me_name, "?"))
    out = [tapestry(me_builder(), slug, det), ""]
    rows = matchups(me_builder, games, seed)
    out.append(matchup_report(rows))
    # improvements on the chosen (calibrated) matchup
    out += ["", "# 3. IMPROVEMENT SUGGESTIONS (tested swaps + detachment test)",
            f"(optimize vs {opt_opp} — the calibrated matchup where recommendations are trustworthy)", ""]
    r = optimize.optimize(me_builder, getattr(rosters, opt_opp),
                          screen=max(400, games // 3), final=games, seed=seed)
    out.append(optimize.report(r))
    report = "\n".join(out)
    d = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(
        os.path.abspath(__file__))))), "reports")
    os.makedirs(d, exist_ok=True)
    path = os.path.join(d, f"gauntlet-{me_name}.md")
    open(path, "w").write(report)
    return report, path


def main():
    import argparse
    ap = argparse.ArgumentParser(description="Run a list through the full gauntlet (tapestry + matchups + fixes).")
    ap.add_argument("me", nargs="?", default="custodes")
    ap.add_argument("--games", type=int, default=1500)
    ap.add_argument("--opt", default="necrons", help="matchup to run the optimizer on")
    a = ap.parse_args()
    report, path = run_gauntlet(a.me, a.games, a.opt)
    print(report)
    print(f"\n[written to {path}]")


if __name__ == "__main__":
    main()
