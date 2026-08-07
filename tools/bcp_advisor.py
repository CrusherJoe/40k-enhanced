#!/usr/bin/env python3
"""bcp_advisor.py — SIM-VALIDATED list recommender. Bridges the aggregate stats (bcp_meta: what winners run)
with the mechanistic sim (wh.sim: what a change actually DOES to your army).

The stats say "winners run X, you run Y". That's a divergence, not advice — a lone Captain buffs no one and
dies; cutting a unit removes whatever JOB it did. So here we TEST changes: load your real list (tapestry /
attach / buffs all live), run it against a GAUNTLET of current top-meta lists, then for each candidate change
rebuild the army and re-sim — reporting the holistic ledger: what the army LOSES vs GAINS.

Metric is the sim's VP MARGIN (your avg VP minus opponent's) across the gauntlet — a MECHANISTIC board-state
read, NOT a real win% (per-game 40k is a coin-flip; trust the relative Δ, not the absolute). See sim STATUS.

  PYTHONPATH=src python3 tools/bcp_advisor.py <event_db_slug> <player> [--gauntlet 6] [--screen 120] [--final 400]
"""
import sys, os, copy, argparse, sqlite3, glob, json, collections
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "src"))
import bcp_meta as BM
from wh.sim import bcp, run, listloader as L, rosters as R
import db as DB


def synth_unit(slug, name):
    """Build a candidate Unit from BSData by NAME (default wargear / typical size) the same way listloader
    builds a parsed unit: resolve profile -> auto role/threat -> rosters.mk. Returns None if unresolvable."""
    sl, prof = L._resolve(slug, name)
    if not prof:
        return None
    kw = [k.upper() for k in prof.get("keywords", [])]
    single = ("CHARACTER" in kw or "TITANIC" in kw or ("VEHICLE" in kw and "MOUNTED" not in kw)
              or ("MONSTER" in kw and "MOUNTED" not in kw))
    models = 1 if single else 5                      # typical size; an approximation for a candidate
    try:
        pts = DB.points(sl, name)["first"]
    except Exception:
        pts = 100
    role, threat = L._role_threat(prof, models, pts)
    try:
        return R.mk(sl, name, models, role=role, threat=threat)
    except Exception:
        return None


def cached(template):
    """A build thunk that deep-copies a pre-built Army each call (so run.simulate gets fresh state without
    re-parsing the list text thousands of times)."""
    return lambda: copy.deepcopy(template)


def with_change(template, cut=None, add_unit=None):
    """A copy of the army with `cut` (unit name) removed and/or `add_unit` (a Unit) appended."""
    a = copy.deepcopy(template)
    if cut:
        a.units = [u for u in a.units if u.name != cut]
    if add_unit is not None:
        a.units.append(copy.deepcopy(add_unit))
    return a


def gauntlet(gsize, exclude_db=None, exclude_player=None):
    """Pick a diverse gauntlet of current top-meta opponent lists: the best-placing LOADABLE list from each
    faction, most-successful factions first. Returns [(label, army_template)]."""
    loadable = bcp.loadable_factions()
    best = {}                          # faction -> (placing, list_id, db, player, detach)
    for dbp in glob.glob("data/bcp/*.sqlite"):
        ev = dbp[:-7]
        pf = ev + "-placings.json"
        if not os.path.exists(pf):
            continue
        if BM.is_league(os.path.basename(ev)):
            continue
        placing = {p["player"]: p["placing"] for p in json.load(open(pf))["placings"] if p.get("placing")}
        con = sqlite3.connect(dbp)
        for lid, player, fac, det in con.execute("SELECT list_id,player,faction,detachment FROM lists"):
            if fac not in loadable or player not in placing:
                continue
            pl = placing[player]
            if fac not in best or pl < best[fac][0]:
                best[fac] = (pl, lid, dbp, player, det)
    picks = sorted(best.values(), key=lambda x: x[0])       # best finishers first, one per faction
    out = []
    for pl, lid, dbp, player, det in picks:
        if len(out) >= gsize:
            break
        try:
            army = bcp.load(lid, db=dbp, side="B")
        except Exception:
            continue
        fac = next(f for f, v in best.items() if v[1] == lid)
        out.append((f"{fac} ({det}) — {player} #{pl}", army))
    return out


def margin(build_me, opp_template, games, seed):
    """Sim VP margin (my_vp - opp_vp) for me vs one opponent."""
    r = run.simulate(build_me, cached(opp_template), games=games, seed=seed)
    return r["my_vp"] - r["opp_vp"]


def gauntlet_margin(build_me, gaunt, games, seed=11):
    return sum(margin(build_me, opp, games, seed) for _, opp in gaunt) / max(1, len(gaunt))


def candidates(event_db, player):
    """Stats-driven cut/add candidates (chapter-legal), reusing bcp_meta. Returns (row, chapter, cuts, adds)."""
    con = sqlite3.connect(event_db); con.row_factory = sqlite3.Row
    row = con.execute("SELECT * FROM lists WHERE player LIKE ?", (f"%{player}%",)).fetchone()
    if not row:
        sys.exit(f"no list for {player} in {event_db}")
    mine = set(u[0] for u in con.execute("SELECT name FROM units WHERE list_id=?", (row["list_id"],)))
    fac = row["faction"]
    is_sm = "Space Marines" in (fac or "")
    tch = BM.sm_chapter(row["army_text"], mine) if is_sm else None
    corpus = BM.load_corpus()
    stats, nf, nt = BM.unit_stats(corpus, fac)
    legal = lambda u: not (is_sm and BM._chapter_locked_elsewhere(u, tch))
    cuts = sorted([(u, s) for u, s in stats.items() if u in mine and s["lift"] < -0.05],
                  key=lambda kv: kv[1]["lift"])
    adds = sorted([(u, s) for u, s in stats.items()
                   if u not in mine and s["top_rate"] >= 0.30 and s["lift"] > 0.05 and legal(u)],
                  key=lambda kv: -kv[1]["lift"])
    return row, tch, fac, cuts, adds, nf, nt


def simrec(event_db, player, gsize=6, screen=120, final=400, seed=11):
    row, tch, fac, cuts, adds, nf, nt = candidates(event_db, player)
    slug = L._FACTION_SLUG.get(fac)
    me0 = bcp.load(row["list_id"], db=event_db, side="A")
    gaunt = gauntlet(gsize, exclude_player=row["player"])
    if not gaunt:
        sys.exit("could not build a gauntlet (no loadable top-cut opponents on disk)")
    base = gauntlet_margin(cached(me0), gaunt, screen, seed)

    # role coverage of the current list (for the "leaves a hole?" read)
    roles = collections.defaultdict(list)
    for u in me0.units:
        roles[u.role].append(u.name)

    # --- CUT ledger: what does removing each flagged unit DO? ---
    cut_rows = []
    for cu, cs in cuts[:5]:
        if cu not in {u.name for u in me0.units}:
            continue
        role = next((u.role for u in me0.units if u.name == cu), "?")
        m = gauntlet_margin(cached(with_change(me0, cut=cu)), gaunt, screen, seed)
        only = len(roles.get(role, [])) <= 1
        cut_rows.append(dict(name=cu, role=role, lift=cs["lift"], delta=m - base, only=only))

    # --- SWAP ledger: role-matched, synthesizable adds; rebuild + re-sim ---
    swap_rows = []
    used = set()
    for cu, cs in cuts[:5]:
        crole = next((u.role for u in me0.units if u.name == cu), None)
        if crole is None:
            continue
        for au, as_ in adds:
            if au in used:
                continue
            unit = synth_unit(slug, au)
            if unit is None or unit.role != crole:          # must model + be the same role as what we cut
                continue
            m = gauntlet_margin(cached(with_change(me0, cut=cu, add_unit=unit)), gaunt, screen, seed)
            used.add(au)
            swap_rows.append(dict(cut=cu, add=au, role=crole, delta=m - base,
                                  add_threat=unit.threat, top=as_["top_rate"]))
            break
    # re-verify the single best swap at the higher game count
    best = max(swap_rows, key=lambda r: r["delta"], default=None)
    if best and best["delta"] > 0:
        unit = synth_unit(slug, best["add"])
        best["delta"] = gauntlet_margin(cached(with_change(me0, cut=best["cut"], add_unit=unit)),
                                        gaunt, final, seed) - gauntlet_margin(cached(me0), gaunt, final, seed)
        best["verified"] = final

    return dict(me=me0.name, chapter=tch, fac=fac, base=base, gaunt=[g[0] for g in gaunt],
                roles=dict(roles), cuts=cut_rows, swaps=swap_rows, best=best, screen=screen)


def report(r):
    L_ = []
    ch = f" [{r['chapter']}]" if r["chapter"] else ""
    L_.append(f"SIM-VALIDATED ADVISOR — {r['me']}{ch}")
    L_.append(f"  metric = sim VP margin vs a {len(r['gaunt'])}-list current-meta gauntlet (mechanistic board")
    L_.append(f"  read, NOT a win% — trust the Δ). baseline margin: {r['base']:+.1f} VP  ({r['screen']} games/opp)")
    L_.append("  gauntlet: " + "; ".join(g[:38] for g in r["gaunt"]))
    L_.append("")
    L_.append("WHAT CUTTING EACH FLAGGED UNIT DOES (list minus the unit, re-simmed):")
    for c in r["cuts"]:
        hole = "  ⚠ ONLY source of this role — leaves a HOLE" if c["only"] else ""
        sign = "improves" if c["delta"] > 0.3 else ("hurts" if c["delta"] < -0.3 else "~neutral")
        L_.append(f"  - {c['name'][:26]:26} (role {c['role']:9}) board {c['delta']:+.1f} VP → {sign}{hole}")
    if not r["cuts"]:
        L_.append("  (nothing in your list under-indexes with winners)")
    L_.append("")
    L_.append("ROLE-MATCHED SWAPS, RE-SIMMED (cut A → add a meta staple of the SAME role, rebuilt & tested):")
    for s in sorted(r["swaps"], key=lambda s: -s["delta"]):
        v = f"  [verified {r['best']['verified']}g]" if r.get("best") and s is r["best"] and r["best"].get("verified") else ""
        sign = "GAIN" if s["delta"] > 0.3 else ("LOSS" if s["delta"] < -0.3 else "wash")
        L_.append(f"  −{s['cut'][:22]:22} +{s['add'][:22]:22} (role {s['role']:9}) board {s['delta']:+.1f} VP → {sign}{v}")
    if not r["swaps"]:
        L_.append("  (no role-matched, Chapter-legal, modellable meta staple to swap in)")
    L_.append("")
    b = r.get("best")
    if b and b["delta"] > 0.3:
        L_.append(f"VERDICT: the strongest TESTED change is −{b['cut']} +{b['add']} "
                  f"({b['delta']:+.1f} VP board swing vs the meta). It keeps your {b['role']} role and the sim")
        L_.append("  shows the army holding more board — but eyeball the actual wargear/synergy before finalising.")
    else:
        L_.append("VERDICT: no single tested swap clearly improves the board vs the meta — the gap is structural")
        L_.append("  (disposition / detachment / whole-army tempo), not one unit. Cutting the flagged units without")
        L_.append("  a same-role replacement would LOSE board (see holes above).")
    L_.append("")
    L_.append("  CAVEAT: candidate adds use default wargear/size and the sim's auto role/threat; VP margin is a")
    L_.append("  mechanistic board read, not a win%. This TESTS the holistic 'what do I lose/gain', but confirm")
    L_.append("  the exact loadout + synergy yourself. Small 11E sample; gauntlet grows as more GTs are pulled.")
    return "\n".join(L_)


def main():
    ap = argparse.ArgumentParser(description="Sim-validated list recommender (stats candidates -> tested swaps).")
    ap.add_argument("event"); ap.add_argument("player")
    ap.add_argument("--gauntlet", type=int, default=6); ap.add_argument("--screen", type=int, default=120)
    ap.add_argument("--final", type=int, default=400)
    a = ap.parse_args()
    event_db = a.event if a.event.endswith(".sqlite") else f"data/bcp/{a.event}.sqlite"
    print(report(simrec(event_db, a.player, gsize=a.gauntlet, screen=a.screen, final=a.final)))


if __name__ == "__main__":
    main()
