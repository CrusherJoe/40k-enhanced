#!/usr/bin/env python3
"""bcp_dashboard.py — weekly meta feed: win rate + field share by faction / disposition / detachment.

Aggregates the on-disk BCP corpus into a per-ISO-week table and (optionally) bakes it into a self-contained
HTML dashboard. Win rate = decided pairings, both-sides, CURRENT-DATASLATE only (both players' lists
>= MIN_DATA_VERSION) — same rule as `bcp_meta winrates`. Field share = # current-dataslate lists bringing
that faction/disposition/detachment that week. Single-weekend GTs only (leagues/team events excluded — a
multi-week league would dump all its players/games into one week and distort the weekly signal).

Faction + disposition come from PUBLIC roster data (scale globally cheap). Detachment comes from the army-list
TEXT (auth-gated pull) so it's only as complete as the list corpus — thin dimensions are flagged by low n.

  PYTHONPATH=src python3 tools/bcp_dashboard.py            # -> docs/meta/dashboard-data.json + index.html
  PYTHONPATH=src python3 tools/bcp_dashboard.py --json     # data only
"""
import sys, os, json, sqlite3, glob, collections, datetime as dt
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import bcp_meta as M

OUTDIR = "docs/meta"
DIMS = ["faction", "disposition", "detachment"]
LOWN = 30                       # win% below this many games is flagged as noisy
# generic / mis-entered faction labels that aren't a real BCP army (drop from the faction table)
JUNK_FACTIONS = {"", "chaos", "unaligned", "unknown", "n/a", "other", "none"}


def _week_start(iso_date):
    """ISO date string -> the WEDNESDAY that starts its 'meta week' (Wed-Tue), as YYYY-MM-DD. This matches
    community trackers (hutber): a meta week runs Wed..Tue so a whole tournament weekend sits inside one bucket."""
    d = dt.date.fromisoformat(iso_date[:10])
    return (d - dt.timedelta(days=(d.weekday() - 2) % 7)).isoformat()


def _events():
    """All single-weekend GT events on disk (exclude leagues/team events) with an event date."""
    out = []
    for pj in glob.glob("data/bcp/*.json"):
        if pj.endswith(("-placings.json", "-pairings.json")):
            continue
        ev = os.path.basename(pj)[:-5]
        if ev == "lso2026-archetypes" or M.is_league(ev):
            continue
        if not (os.path.exists(f"data/bcp/{ev}.sqlite") and os.path.exists(f"data/bcp/{ev}-pairings.json")):
            continue
        try:
            d = json.load(open(pj))["event"].get("eventDate")
        except Exception:
            d = None
        if d:
            out.append((ev, _week_start(d)))
    return out


def build_data():
    # per dimension: {value: {week: {"games":,"wins":,"players":}}}
    agg = {dim: collections.defaultdict(lambda: collections.defaultdict(lambda: {"games": 0, "wins": 0, "players": 0}))
           for dim in DIMS}
    weeks = set()
    n_events = 0
    total_games = 0
    for ev, wk in _events():
        weeks.add(wk)
        n_events += 1
        con = sqlite3.connect(f"data/bcp/{ev}.sqlite"); con.row_factory = sqlite3.Row
        # Date-bucketed weekly view: each week reflects that week's balance, so we DON'T gate on the army-list
        # Data-Version footer (it often fails to parse and would drop most games). Faction & disposition come
        # from the public roster (present for ~everyone); detachment from the parsed list text (when available).
        pdim = {}                                   # player -> {dim: value}
        for r in con.execute("SELECT player,faction,detachment,disposition FROM lists"):
            fac = r["faction"] if (r["faction"] and r["faction"].strip().lower() not in JUNK_FACTIONS) else None
            vals = {"faction": fac, "disposition": r["disposition"], "detachment": r["detachment"]}
            pdim[r["player"]] = vals
            for dim in DIMS:
                if vals[dim]:
                    agg[dim][vals[dim]][wk]["players"] += 1
        for p in json.load(open(f"data/bcp/{ev}-pairings.json")):
            if (p.get("p1_pts") is None or p.get("p2_pts") is None or p["p1_pts"] == p["p2_pts"]
                    or p["p1"] not in pdim or p["p2"] not in pdim):
                continue
            total_games += 1
            p1win = p["p1_pts"] > p["p2_pts"]
            for who, win in ((p["p1"], p1win), (p["p2"], not p1win)):
                for dim in DIMS:
                    v = pdim[who][dim]
                    if v:
                        agg[dim][v][wk]["games"] += 1
                        agg[dim][v][wk]["wins"] += win
    weeks = sorted(weeks)

    def dim_rows(dim):
        rows = []
        for val, byweek in agg[dim].items():
            tot = {"games": sum(w["games"] for w in byweek.values()),
                   "wins": sum(w["wins"] for w in byweek.values()),
                   "players": sum(w["players"] for w in byweek.values())}
            rows.append({"name": val, "total": tot,
                         "byweek": {wk: byweek[wk] for wk in byweek}})
        rows.sort(key=lambda r: -r["total"]["players"])
        return rows

    return {
        "generated_utc": dt.datetime.now(dt.timezone.utc).strftime("%Y-%m-%dT%H:%MZ"),
        "min_data_version": M.MIN_DATA_VERSION,
        "low_n": LOWN,
        "summary": {"events": n_events, "games": total_games, "weeks": len(weeks),
                    "week_range": [weeks[0], weeks[-1]] if weeks else []},
        "weeks": [{"start": w,
                   "short": dt.date.fromisoformat(w).strftime("%b %-d"),
                   "label": (dt.date.fromisoformat(w).strftime("%b %-d") + "–"
                             + (dt.date.fromisoformat(w) + dt.timedelta(days=6)).strftime("%b %-d"))}
                  for w in weeks],
        **{dim: dim_rows(dim) for dim in DIMS},
    }


def main():
    data = build_data()
    os.makedirs(OUTDIR, exist_ok=True)
    json.dump(data, open(f"{OUTDIR}/dashboard-data.json", "w"), indent=1)
    s = data["summary"]
    print(f"# {s['events']} events, {s['games']} games, {s['weeks']} weeks "
          f"({s['week_range'][0] if s['week_range'] else '-'}..{s['week_range'][-1] if s['week_range'] else '-'})")
    for dim in DIMS:
        vals = [r for r in data[dim] if r["total"]["players"]]
        print(f"  {dim:12} {len(vals):3} values; top by field share: "
              + ", ".join(f"{r['name'][:16]}({r['total']['players']}p,"
                          f"{100*r['total']['wins']/r['total']['games']:.0f}%w)" if r["total"]["games"] else
                          f"{r['name'][:16]}({r['total']['players']}p,-)" for r in vals[:4]))
    if "--json" not in sys.argv:
        from bcp_dashboard_html import render
        html = render(data)
        open(f"{OUTDIR}/index.html", "w").write(html)
        # body-only variant for publishing as a claude.ai Artifact (host provides its own <head>/<body>)
        import re as _re
        parts = [_re.search(p, html, _re.S).group(0) for p in
                 (r"<style>.*?</style>", r'<div class="wrap">.*?</div>\s*(?=<script>)', r"<script>.*?</script>")]
        open(f"{OUTDIR}/_artifact.html", "w").write("\n".join(parts) + "\n")
        print(f"# wrote {OUTDIR}/index.html ({len(html)//1024} KB, self-contained) + _artifact.html")


if __name__ == "__main__":
    main()
