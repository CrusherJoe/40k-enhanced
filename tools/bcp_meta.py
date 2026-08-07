#!/usr/bin/env python3
"""bcp_meta.py — aggregate META engine + list-change RECOMMENDER, grounded in real placings.

Per-GAME prediction is a coin-flip (see wh-predictive-model), so this works in the AGGREGATE, where the
signal is real: how a faction/archetype/list PLACES across the current-balance corpus, and which units the
TOP-placing lists actually run. It then compares YOUR list to that winning profile and recommends changes.

  PYTHONPATH=src python3 tools/bcp_meta.py meta                       # faction performance table
  PYTHONPATH=src python3 tools/bcp_meta.py units <FactionSubstr>      # unit inclusion: field vs top lists
  PYTHONPATH=src python3 tools/bcp_meta.py recommend <event> <player> # compare a list to its faction meta

Current-balance 11E corpus (>=28 players / 5 rounds): LSO 2026, NM2026, Denver Aug '26. A list is 'TOP' if
it finished in the best third of its event. Thin for small factions — sample sizes are always shown; a
fresh BCP token + tools/bcp_corpus can widen it.
"""
import sys, os, re, json, sqlite3, argparse, collections, glob
sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "src"))

TOP_FRAC = 1 / 3.0            # a list is "top" if in the best third of its event
# DATASLATE hygiene: a BCP army list's footer carries "Data Version: vNNN". Per hutber's metaVersion map,
# appVersion 909 = "11th Release" (gameVersion 18, PRE the 1st dataslate); 912/913+ = "1st 11th update"
# (gameVersion 19, CURRENT). So the current-balance corpus is data-version >= 912 — this drops pre-dataslate
# games that a plain DATE cutoff misses (the 1st dataslate dropped mid-window, ~Aug 1).
MIN_DATA_VERSION = 912


def _data_version(army_text):
    m = re.search(r"Data Version:\s*v?(\d+)", army_text or "")
    return int(m.group(1)) if m else None


# Multi-week LEAGUE / escalation / team-league formats: rolling & provisional standings, mixed-dataslate over
# weeks, and "top third" is meaningless mid-season -> EXCLUDE from the placing-based corpus (meta/units/recommend).
# They stay VALID for winrates() (a single decided current-dataslate game is a game regardless of event format).
_LEAGUE_RE = re.compile(r"league|escalation|liga-t-m|(^|-)teams?(-|$)", re.I)


def is_league(ev):
    return bool(_LEAGUE_RE.search(ev))


def all_events(placings_only=True):
    """Current-balance events we have a DB+placings+pairings for. placings_only=True (default) also drops
    multi-week LEAGUE formats (provisional standings) so the placing corpus stays single-GT/final-standings."""
    evs = []
    for pj in glob.glob("data/bcp/*-placings.json"):
        ev = os.path.basename(pj)[:-len("-placings.json")]
        if not (os.path.exists(f"data/bcp/{ev}.sqlite") and os.path.exists(f"data/bcp/{ev}-pairings.json")):
            continue
        if placings_only and is_league(ev):
            continue
        evs.append(ev)
    return sorted(evs)


def load_corpus(events=None):
    events = events or all_events()
    rows = []
    for ev in events:
        placings = {p["player"]: p["placing"] for p in json.load(open(f"data/bcp/{ev}-placings.json"))["placings"]}
        n = max([p for p in placings.values() if p] or [1])
        con = sqlite3.connect(f"data/bcp/{ev}.sqlite"); con.row_factory = sqlite3.Row
        for r in con.execute("SELECT list_id,player,faction,detachment,disposition,army_text FROM lists"):
            pl = placings.get(r["player"])
            if not pl or not r["faction"]:
                continue
            dv = _data_version(r["army_text"])
            if dv is None or dv < MIN_DATA_VERSION:      # drop pre-dataslate + unverifiable lists (hygiene)
                continue
            units = collections.Counter(u[0] for u in
                                        con.execute("SELECT name FROM units WHERE list_id=?", (r["list_id"],)))
            pct = (pl - 1) / max(1, n - 1)                       # 0.0 = 1st, 1.0 = last
            rows.append(dict(ev=ev, player=r["player"], faction=r["faction"], detach=r["detachment"],
                             disp=r["disposition"], placing=pl, field=n, pct=pct, top=pct <= TOP_FRAC,
                             units=units))
    return rows


def faction_perf(corpus):
    by = collections.defaultdict(list)
    for r in corpus:
        by[r["faction"]].append(r)
    out = []
    for f, rs in by.items():
        out.append(dict(faction=f, n=len(rs), mean_pct=sum(r["pct"] for r in rs) / len(rs),
                        top_rate=sum(r["top"] for r in rs) / len(rs)))
    return sorted(out, key=lambda x: x["mean_pct"])


def unit_stats(corpus, faction):
    rs = [r for r in corpus if faction.lower() in r["faction"].lower()]
    tops = [r for r in rs if r["top"]]
    if not rs:
        return None, 0, 0
    field, top = collections.Counter(), collections.Counter()
    for r in rs:
        for u in r["units"]:
            field[u] += 1
    for r in tops:
        for u in r["units"]:
            top[u] += 1
    nf, nt = len(rs), max(1, len(tops))
    stats = {}
    for u in field:
        fr = field[u] / nf
        tr = top.get(u, 0) / nt
        stats[u] = dict(field_rate=fr, top_rate=tr, lift=tr - fr, field_n=field[u], top_n=top.get(u, 0))
    return stats, nf, len(tops)


def cmd_winrates(corpus=None):
    """Faction WIN RATES from real pairings (the hutber-style table, from our OWN data) — current-dataslate
    only: a game counts only when BOTH players' lists are current (Data Version >= MIN_DATA_VERSION)."""
    import collections as _c
    w, n = _c.Counter(), _c.Counter()
    games = 0
    for ev in all_events(placings_only=False):    # decided games are valid regardless of event format
        con = sqlite3.connect(f"data/bcp/{ev}.sqlite"); con.row_factory = sqlite3.Row
        fac = {}
        for r in con.execute("SELECT player,faction,army_text FROM lists"):
            dv = _data_version(r["army_text"])
            if r["faction"] and dv is not None and dv >= MIN_DATA_VERSION:
                fac[r["player"]] = r["faction"]
        for p in json.load(open(f"data/bcp/{ev}-pairings.json")):
            if (p.get("p1_pts") is not None and p.get("p2_pts") is not None and p["p1_pts"] != p["p2_pts"]
                    and p["p1"] in fac and p["p2"] in fac):
                f1, f2 = fac[p["p1"]], fac[p["p2"]]; p1w = p["p1_pts"] > p["p2_pts"]
                n[f1] += 1; n[f2] += 1; w[f1] += p1w; w[f2] += (not p1w); games += 1
    print(f"FACTION WIN RATES — current-dataslate ({games} games, both-sides; from our corpus)")
    print(f"  {'faction':26} {'win%':>5} {'games':>6}")
    for f in sorted([f for f in n if n[f] >= 30], key=lambda f: -w[f] / n[f]):
        print(f"  {f[:26]:26} {100*w[f]/n[f]:>4.0f}% {n[f]:>6}")
    print("  (factions with <30 current-dataslate games hidden; ~50% = balanced)")


def cmd_meta(corpus):
    perf = faction_perf(corpus)
    print(f"FACTION PERFORMANCE — current-balance 11E ({len(corpus)} lists, top = best third of event)")
    print(f"  {'faction':26} {'n':>3} {'mean finish %ile':>16} {'top-cut rate':>13}")
    for p in perf:
        if p["n"] >= 3:
            print(f"  {p['faction'][:26]:26} {p['n']:>3} {100*p['mean_pct']:>14.0f}%  {100*p['top_rate']:>11.0f}%")
    print("  (lower mean-finish %ile = better; top-cut rate vs the ~33% baseline. n<8 = low confidence.)")


def cmd_units(corpus, fac):
    stats, nf, nt = unit_stats(corpus, fac)
    if not stats:
        print("no lists for", fac); return
    print(f"UNIT INCLUSION — {fac} ({nf} lists, {nt} top): field% vs top% (+lift = winners run it MORE)")
    for u, s in sorted(stats.items(), key=lambda kv: -kv[1]["lift"])[:12]:
        print(f"  +{s['lift']*100:>4.0f}  {u[:30]:30} field {s['field_rate']*100:>3.0f}%  top {s['top_rate']*100:>3.0f}%")
    print("  --- winners run these LESS ---")
    for u, s in sorted(stats.items(), key=lambda kv: kv[1]["lift"])[:6]:
        print(f"  {s['lift']*100:>5.0f}  {u[:30]:30} field {s['field_rate']*100:>3.0f}%  top {s['top_rate']*100:>3.0f}%")


def unit_points(corpus):
    """Average points per unit NAME across the corpus (from the units tables) — for points-matched swaps."""
    tot, cnt = collections.Counter(), collections.Counter()
    for ev in all_events():
        con = sqlite3.connect(f"data/bcp/{ev}.sqlite")
        for name, pts in con.execute("SELECT name,points FROM units"):
            if pts:
                tot[name] += pts; cnt[name] += 1
    return {u: tot[u] / cnt[u] for u in tot if cnt[u]}


def _role(name):
    """Light role tag from BSData keywords (for the swap reason)."""
    try:
        import sys as _s; _s.path.insert(0, "tools"); import db
        from wh.sim import listloader as L
        for sl in ["space-marines"] + L._FALLBACK.get("space-marines", []):
            try:
                kw = [k.upper() for k in db.profile(sl, name).get("keywords", [])]
                for tag in ("CHARACTER", "VEHICLE", "MONSTER", "MOUNTED", "INFANTRY"):
                    if tag in kw:
                        return tag.lower()
            except Exception:
                continue
    except Exception:
        pass
    return "unit"


def cmd_recommend(corpus, ev, player):
    con = sqlite3.connect(f"data/bcp/{ev}.sqlite"); con.row_factory = sqlite3.Row
    row = con.execute("SELECT * FROM lists WHERE player LIKE ?", (f"%{player}%",)).fetchone()
    if not row:
        print("no list for", player); return
    mine = collections.Counter(u[0] for u in con.execute("SELECT name FROM units WHERE list_id=?", (row["list_id"],)))
    fac = row["faction"]
    perf = {p["faction"]: p for p in faction_perf(corpus)}
    fp = perf.get(fac)
    stats, nf, nt = unit_stats(corpus, fac)
    print(f"LIST vs META — {row['player']} · {fac} / {row['detachment']} · {row['disposition']}")
    if fp:
        verdict = "ABOVE" if fp["mean_pct"] < 0.5 else "below"
        print(f"\nPREDICT (aggregate, honest): {fac} across the corpus finishes at the "
              f"{100*fp['mean_pct']:.0f}th %ile on average, top-cut {100*fp['top_rate']:.0f}% "
              f"(n={fp['n']} lists) — {verdict}-average faction. (Per-GAME win% is a coin-flip; this is the meta read.)")
    if not stats:
        return
    have = set(mine)
    add = [(u, s) for u, s in stats.items() if u not in have and s["top_rate"] >= 0.30 and s["lift"] > 0.05]
    add.sort(key=lambda kv: -kv[1]["lift"])
    cut = [(u, s) for u, s in stats.items() if u in have and s["lift"] < -0.05]
    cut.sort(key=lambda kv: kv[1]["lift"])
    print(f"\nRECOMMENDATIONS (what TOP {fac} lists do differently; n={nf} lists / {nt} top):")
    print("  ADD — winners run these, you don't:")
    for u, s in add[:6]:
        print(f"    + {u[:30]:30} in {s['top_rate']*100:.0f}% of top lists ({s['field_rate']*100:.0f}% field)  [+{s['lift']*100:.0f} lift]")
    if not add:
        print("    (your list already covers the winning staples)")
    print("  RECONSIDER — you run these, winners tend not to:")
    for u, s in cut[:6]:
        print(f"    - {u[:30]:30} in only {s['top_rate']*100:.0f}% of top lists ({s['field_rate']*100:.0f}% field)  [{s['lift']*100:.0f} lift]")
    if not cut:
        print("    (nothing in your list under-indexes with winners)")
    # paired, points-matched swaps in the "replace A with B for this reason" format
    pts = unit_points(corpus)
    if cut and add:
        print("\n  SUGGESTED SWAPS (replace A -> B, points-matched):")
        used = set()
        for cu, cs in cut[:5]:
            cp = pts.get(cu, 0)
            cands = sorted([(u, s) for u, s in add if u not in used and abs(pts.get(u, 9999) - cp) <= max(40, 0.4 * cp)],
                           key=lambda kv: -kv[1]["lift"])
            if not cands:
                continue
            bu, bs = cands[0]; used.add(bu)
            print(f"    replace {cu} (~{cp:.0f}pts, {_role(cu)})  ->  {bu} (~{pts.get(bu,0):.0f}pts, {_role(bu)})")
            print(f"       WHY: top {fac} lists run {bu} in {bs['top_rate']*100:.0f}% of winning lists vs your "
                  f"{cu} at {cs['top_rate']*100:.0f}%  (+{bs['lift']*100:.0f} vs {cs['lift']*100:.0f} lift; ~same points)")
    print("\n  NOTE: aggregate/thin (small 11E sample) — pair with the mechanistic runbook (wh.sim.runbook)")
    print("  for the per-matchup WHY before swapping. Confidence grows as more current-balance GTs are pulled.")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("cmd", choices=["meta", "winrates", "units", "recommend"])
    ap.add_argument("a", nargs="?"); ap.add_argument("b", nargs="?")
    args = ap.parse_args()
    corpus = load_corpus()
    if args.cmd == "winrates":
        cmd_winrates(corpus)
    elif args.cmd == "meta":
        cmd_meta(corpus)
    elif args.cmd == "units":
        cmd_units(corpus, args.a)
    else:
        cmd_recommend(corpus, args.a, args.b)


if __name__ == "__main__":
    main()
