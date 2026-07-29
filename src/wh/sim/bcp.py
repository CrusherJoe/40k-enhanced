"""Load real BestCoastPairings army lists as sim opponents.

The BCP list DB (data/bcp/<event>.sqlite, built by tools/bcp_db.py) stores each list's
full `army_text` — which is the same shape listloader already parses. So this module is a
thin source-adapter: it turns a DB row into a listloader `entry` dict and hands it to
listloader.load(entry=...), reusing the whole parse -> resolve-vs-BSData -> auto role/threat
-> faction tapestry pipeline. Nothing about the modelling is BCP-specific.

  from wh.sim import bcp
  opp = bcp.load("Joe Beddoe")                 # an Army, by player-name substring or listId
  b   = bcp.builder("Joe Beddoe")              # a build_opp thunk for runbook/optimize/dossier
  for label, build in bcp.field(faction="Necrons"): ...   # sweep the field

CLI:
  python -m wh.sim.bcp list [--faction X] [--disposition Y]
  python -m wh.sim.bcp show <player|listId>
  python -m wh.sim.bcp run  <me> <player|listId> [--games N]
  python -m wh.sim.bcp field <me> [--faction X] [--games N] [--limit N]
"""
from __future__ import annotations

import os, re, sqlite3, sys

from . import listloader as _L
from . import rosters as _R

_ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
DEFAULT_DB = os.path.join(_ROOT, "data", "bcp", "lso2026.sqlite")


def _con(db=None):
    db = db or DEFAULT_DB
    if not os.path.exists(db):
        sys.exit(f"no BCP DB at {db} — build it: python3 tools/bcp_db.py build data/bcp/<event>-lists/_raw --db {db}")
    con = sqlite3.connect(db)
    con.row_factory = sqlite3.Row
    return con


def loadable_factions():
    """Faction display-names that resolve to a BSData cut (so their lists can be simmed)."""
    return set(_L._FACTION_SLUG)


def catalog(faction=None, disposition=None, loadable_only=True, parsed_only=False, db=None):
    """Light dicts for matching lists: list_id, player, faction, detachment, disposition, points, slug."""
    con = _con(db)
    q = "SELECT list_id,player,faction,detachment,disposition,total_points,n_units,parse_ok FROM lists WHERE 1=1"
    args = []
    if faction:
        q += " AND faction LIKE ?"; args.append(f"%{faction}%")
    if disposition:
        q += " AND disposition LIKE ?"; args.append(f"%{disposition}%")
    if parsed_only:
        q += " AND parse_ok=1"
    rows = con.execute(q + " ORDER BY faction, player", args).fetchall()
    out = []
    for r in rows:
        slug = _L._FACTION_SLUG.get(r["faction"])
        if loadable_only and not slug:
            continue
        out.append(dict(list_id=r["list_id"], player=r["player"], faction=r["faction"],
                        detachment=r["detachment"], disposition=r["disposition"],
                        points=r["total_points"], n_units=r["n_units"], parse_ok=r["parse_ok"], slug=slug))
    return out


def _find(sel, db=None):
    """Resolve `sel` (exact listId or player-name substring) to a single DB row."""
    con = _con(db)
    r = con.execute("SELECT * FROM lists WHERE list_id=?", (sel,)).fetchone()
    if r:
        return r
    rows = con.execute("SELECT * FROM lists WHERE player LIKE ? ORDER BY player", (f"%{sel}%",)).fetchall()
    if not rows:
        sys.exit(f"no BCP list matching '{sel}'")
    if len(rows) > 1:
        names = ", ".join(sorted({x["player"] for x in rows}))
        sys.exit(f"'{sel}' matches several players ({names}) — narrow it or use the listId")
    return rows[0]


def _entry(row):
    """A listloader entry dict from a BCP DB row (army_text IS the exported listText)."""
    return dict(faction=row["faction"], listText=row["army_text"],
                detachment=row["detachment"] or "?", disposition=row["disposition"] or "",
                wins=0, losses=0, playerName=row["player"])


def _list_name(row):
    """The list's own title (first line of the export), else a player/faction label."""
    first = (row["army_text"] or "").splitlines()[0] if row["army_text"] else ""
    title = re.sub(r"\s*\(.*?points?\)\s*$", "", first, flags=re.I).strip()
    return title or f"{row['player']} — {row['faction']}"


def load(sel, disposition=None, db=None, side="B", name=None, use_list_name=False):
    """Build an Army for the BCP list matching `sel` (listId or player substring).
    side "A" = your army (own deployment/turn), "B" (default) = opponent. `use_list_name`
    labels the Army with the list's own title (e.g. 'This List Tastes Like Death by Rock and Roll')."""
    row = _find(sel, db)
    if not _L._FACTION_SLUG.get(row["faction"]):
        sys.exit(f"{row['player']}'s faction '{row['faction']}' has no BSData cut — not sim-loadable yet")
    label = name or (_list_name(row) if use_list_name
                     else f"{row['player']} — {row['faction']} / {row['detachment'] or '?'}")
    army = _L.load(entry=_entry(row), disposition=disposition, name=label, side=side)
    if not army.units:
        raise ValueError(f"{row['player']}'s list has no parseable units "
                         f"(list-builder export format unsupported by listloader)")
    return army


def builder(sel, disposition=None, db=None, side="B", name=None, use_list_name=False):
    """A build thunk bound to a BCP list — pass to runbook.build / optimize / dossier."""
    def b():
        return load(sel, disposition=disposition, db=db, side=side, name=name, use_list_name=use_list_name)
    return b


def field(faction=None, disposition=None, db=None, limit=None):
    """(label, build_opp) pairs over the loadable field — sweep YOUR army against real lists."""
    cat = catalog(faction=faction, disposition=disposition, loadable_only=True, db=db)
    if limit:
        cat = cat[:limit]
    return [(f"{c['player']} ({c['faction']}/{c['detachment']})", builder(c["list_id"], db=db)) for c in cat]


# --------------------------------------------------------------------------- CLI
def _me(name):
    if not hasattr(_R, name):
        sys.exit(f"no roster '{name}' — options incl. knights, custodes, great_value")
    return getattr(_R, name)


def main():
    import argparse
    ap = argparse.ArgumentParser(description="Load BestCoastPairings lists as sim opponents.")
    ap.add_argument("--db", default=DEFAULT_DB)
    sub = ap.add_subparsers(dest="cmd", required=True)
    p = sub.add_parser("list"); p.add_argument("--faction"); p.add_argument("--disposition")
    p.add_argument("--all", action="store_true", help="include lists whose faction has no BSData cut")
    p = sub.add_parser("show"); p.add_argument("sel")
    p = sub.add_parser("run"); p.add_argument("me"); p.add_argument("sel"); p.add_argument("--games", type=int, default=250)
    p = sub.add_parser("field"); p.add_argument("me"); p.add_argument("--faction"); p.add_argument("--disposition")
    p.add_argument("--games", type=int, default=40); p.add_argument("--limit", type=int)
    a = ap.parse_args()

    if a.cmd == "list":
        cat = catalog(a.faction, a.disposition, loadable_only=not a.all, db=a.db)
        for c in cat:
            flag = "" if c["parse_ok"] else "  [text-only]"
            simmable = "" if c["slug"] else "  [no BSData cut]"
            print(f"  {c['player'][:24]:25} {c['faction'][:20]:21} "
                  f"{str(c['detachment'])[:24]:25} {str(c['disposition'])[:15]:16} "
                  f"{c['points']}{flag}{simmable}")
        print(f"\n# {len(cat)} lists" + (" (loadable only)" if not a.all else ""))
        return

    if a.cmd == "show":
        army = load(a.sel, db=a.db)
        print(f"{army.name}   [{army.disposition}]")
        for u in army.units:
            print(f"  {u.models:>2}x {u.name[:34]:35} role={u.role:10} threat={getattr(u,'threat','?')}")
        miss = getattr(army, "_missing", [])
        if miss:
            print(f"\n  unresolved datasheets (skipped): {', '.join(miss)}")
        return

    from . import runbook
    if a.cmd == "run":
        print(runbook.report(runbook.build(_me(a.me), builder(a.sel, db=a.db), games=a.games)))
        return

    if a.cmd == "field":
        from .runbook import _assess
        rows, skipped = [], []
        for label, build_opp in field(a.faction, a.disposition, db=a.db, limit=a.limit):
            try:
                r = runbook.build(_me(a.me), build_opp, games=a.games)
                head, _ = _assess(r)
                margin = (r["ctrl"][3] + r["ctrl"][4]) / 2 - (r["octrl"][3] + r["octrl"][4]) / 2
                rows.append((label, head.split(" —")[0].split(" ")[0], margin))
            except SystemExit:
                raise
            except Exception as ex:
                skipped.append((label, str(ex)[:60]))
        rows.sort(key=lambda x: x[2])
        print(f"\n# {a.me} vs the field ({len(rows)} simmed, {len(skipped)} skipped, "
              f"{a.games} games each) — hardest first")
        print(f"# NOTE: directional read only (see sim STATUS) — the VERDICT + board margin, not a win%\n")
        for label, verdict, margin in rows:
            print(f"  {verdict[:14]:15} board{margin:+6.2f}  {label[:60]}")
        if skipped:
            print(f"\n# skipped (unparseable list export): {len(skipped)}")
            for label, why in skipped:
                print(f"  - {label[:60]}")
        return


if __name__ == "__main__":
    main()
