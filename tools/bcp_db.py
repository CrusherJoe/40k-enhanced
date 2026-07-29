#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""bcp_db.py — local SQLite database of a BestCoastPairings event's army lists.

Builds data/bcp/<event>.sqlite from the raw armylist JSONs pulled by bcp_pull.py
(--fetch-lists), so we can query the whole field fast without re-hitting the API or
re-parsing text every time. One row per list in `lists`; parsed top-level units in
`units`; enhancements in `enhancements`.

Provenance of the interesting fields (verified against LSO 2026 raw records):
  - faction      <- army.name        (specific, e.g. "Emperor's Children", not "Chaos")
  - detachment   <- warhammer.detachment  (e.g. "Peerless Bladesmen")
  - disposition  <- subFaction.name   (the mission disposition, e.g. "Priority Assets")
  - total_points <- first "(N points)" line of armyListText (the list's own total)
  - game_size    <- the "Strike Force/Incursion/..." line points (usually 2000)

Build:
  python3 tools/bcp_db.py build data/bcp/lso2026-lists/_raw --db data/bcp/lso2026.sqlite \
          --roster data/bcp/lso2026.json
Query:
  python3 tools/bcp_db.py stats                       # faction/detachment/disposition breakdown
  python3 tools/bcp_db.py faction "Imperial Knights"  # list players of a faction
  python3 tools/bcp_db.py unit "Caladius"             # which lists run a unit (substring)
  python3 tools/bcp_db.py show <listId|player-substr> # full parsed record + text
"""
import argparse, glob, json, os, re, sqlite3, sys

DEFAULT_DB = "data/bcp/lso2026.sqlite"
GAME_SIZES = {"Strike Force", "Incursion", "Onslaught", "Combat Patrol", "Boarding Actions"}
# A unit line = "<name> <points-token>" at the top level. Several list builders are in
# use across the field (BCP standard, New Recruit, GW app), so match several point tokens.
# Numbers may carry a thousands comma ("2,000") and "Points" may be capitalised.
UNIT_PATTERNS = [
    re.compile(r"^(.*?)\s*\((\d[\d,]*)\s*points?\)\s*$", re.I),   # Name (NNN points)   [BCP / indented]
    re.compile(r"^(.*?)\s*\[(\d[\d,]*)\s*(?:points?|pts?)\.?\]\s*$", re.I),  # Name [NNN pts]  [GW app / custom]
    re.compile(r"^(.*?)\s+(\d[\d,]*)\s*Pts?\.\s*.*$", re.I),      # Name NNN Pts. *Unit* [New Recruit]
]
# whole-text total-points fallbacks for header-block exporters (WTC "+++", "X / Y pts")
TOTAL_FALLBACKS = [
    re.compile(r"TOTAL ARMY POINTS:\s*(\d[\d,]*)", re.I),
    re.compile(r"(\d[\d,]*)\s*/\s*\d[\d,]*\s*pts", re.I),
]
ENH_RE = re.compile(r"^\s*[•◦]?\s*Enhancements?:\s*(.+?)(?:\s*\((?:Upgrade|Enhancement)\))?\s*$", re.I)
PTS_RE = re.compile(r"[(\[](\d[\d,]*)\s*points?[)\]]", re.I)
# a stripped line starting with any of these is a sub-item / component, never a unit
SUBITEM_PREFIX = ("•", "◦", "-", "*", "(", "▪", "‣", "·")
QTY_RE = re.compile(r"^x?\d+x?\b", re.I)


def _int(s):
    return int(str(s).replace(",", ""))


def _unit_line(ln):
    """If `ln` is a top-level unit line, return (name, points); else None."""
    s = ln.strip()
    if not s or s[0] in SUBITEM_PREFIX or QTY_RE.match(s):
        return None
    for rx in UNIT_PATTERNS:
        m = rx.match(s)
        if m and m.group(1).strip():
            return m.group(1).strip(), _int(m.group(2))
    return None


def parse_text(txt):
    """Return (total_points, game_size, [(seq,name,points)], [enhancement,...])."""
    total = game_size = None
    units, enh = [], []
    seq = 0
    for ln in txt.splitlines():
        e = ENH_RE.match(ln)
        if e:
            enh.append(e.group(1).strip())
            continue
        hit = _unit_line(ln)
        if not hit:
            # some builders put a bare "NNNN Points" total line with no name
            if total is None:
                mp = PTS_RE.search(ln) or re.search(r"^\s*(\d[\d,]{3,})\s*points?\s*$", ln, re.I)
                if mp:
                    total = _int(mp.group(1))
            continue
        name, pts = hit
        if total is None:                        # first points line = list total/title
            total = pts
            continue
        if name in GAME_SIZES:                   # game-size line, not a unit
            game_size = pts
            continue
        seq += 1
        units.append((seq, name, pts))
    if total is None:                            # header-block exporters (no per-line total)
        for rx in TOTAL_FALLBACKS:
            m = rx.search(txt)
            if m:
                total = _int(m.group(1))
                break
    return total, game_size, units, enh


SCHEMA = """
CREATE TABLE lists (
  list_id TEXT PRIMARY KEY, event_id TEXT, event_name TEXT,
  player TEXT, first_name TEXT, last_name TEXT, user_id TEXT,
  faction TEXT, army_id TEXT, detachment TEXT, disposition TEXT, team TEXT,
  list_status TEXT, list_type TEXT, total_points INTEGER, game_size INTEGER,
  n_units INTEGER, created_at TEXT, updated_at TEXT, list_url TEXT,
  army_text TEXT, army_html TEXT, dropped INTEGER DEFAULT 0,
  parse_ok INTEGER DEFAULT 1
);
CREATE TABLE units (
  id INTEGER PRIMARY KEY AUTOINCREMENT, list_id TEXT, seq INTEGER,
  name TEXT, points INTEGER,
  FOREIGN KEY(list_id) REFERENCES lists(list_id)
);
CREATE TABLE enhancements (
  id INTEGER PRIMARY KEY AUTOINCREMENT, list_id TEXT, name TEXT,
  FOREIGN KEY(list_id) REFERENCES lists(list_id)
);
CREATE INDEX ix_lists_faction ON lists(faction);
CREATE INDEX ix_lists_detach ON lists(detachment);
CREATE INDEX ix_lists_disp ON lists(disposition);
CREATE INDEX ix_units_list ON units(list_id);
CREATE INDEX ix_units_name ON units(name);
"""


DISPOSITIONS = ["Disruption", "Priority Assets", "Purge the Foe", "Reconnaissance", "Take and Hold"]
DETACH_PATTERNS = [
    re.compile(r"^(.+?)\s*\(\d+\s*Detachment Points?\)\s*$", re.I | re.M),   # BCP: "A and B (3 Detachment Points)"
    re.compile(r"^\s*Detachments?:\s*(.+?)\s*\(", re.I | re.M),              # GW app: "Detachments: A, B ("
    re.compile(r"DETACHMENT:\s*(.+)", re.I),                                  # WTC "+++": "+ DETACHMENT: A, B (..)"
]


def backfill_from_text(con):
    """Recover disposition + detachment for lists where the API left them null,
    from the stored army_text (several exporters carry them in-text only)."""
    dispo = detach = 0
    con.row_factory = sqlite3.Row
    for r in con.execute("SELECT list_id, disposition, detachment, army_text FROM lists "
                         "WHERE disposition IS NULL OR detachment IS NULL").fetchall():
        txt = r["army_text"] or ""
        if r["disposition"] is None:
            for d in DISPOSITIONS:
                if re.search(r"\b" + re.escape(d) + r"\b", txt, re.I):
                    con.execute("UPDATE lists SET disposition=? WHERE list_id=?", (d, r["list_id"]))
                    dispo += 1
                    break
        if r["detachment"] is None:
            for rx in DETACH_PATTERNS:
                m = rx.search(txt)
                if m and m.group(1).strip():
                    con.execute("UPDATE lists SET detachment=? WHERE list_id=?",
                                (m.group(1).strip().rstrip("+").strip(), r["list_id"]))
                    detach += 1
                    break
    con.commit()
    print(f"# backfilled from text: +{dispo} disposition, +{detach} detachment", file=sys.stderr)


def build(rawdir, dbpath, roster_path=None):
    os.makedirs(os.path.dirname(dbpath) or ".", exist_ok=True)
    if os.path.exists(dbpath):
        os.remove(dbpath)
    con = sqlite3.connect(dbpath)
    con.executescript(SCHEMA)
    team_by_list, drop_by_list, fac_by_list = {}, {}, {}
    if roster_path and os.path.exists(roster_path):
        for r in json.load(open(roster_path))["players"]:
            if r.get("listId"):
                team_by_list[r["listId"]] = r.get("team")
                drop_by_list[r["listId"]] = 1 if r.get("dropped") else 0
                fac_by_list[r["listId"]] = r.get("faction")
    files = sorted(glob.glob(os.path.join(rawdir, "*.json")))
    n = 0
    for fp in files:
        d = json.load(open(fp))
        lid = d["id"]
        u = d.get("user") or {}
        txt = d.get("armyListText") or ""
        total, game_size, units, enh = parse_text(txt)
        con.execute(
            "INSERT INTO lists VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)",
            (lid, d.get("eventId"), (d.get("event") or {}).get("name"),
             " ".join(x for x in (u.get("firstName"), u.get("lastName")) if x).strip(),
             u.get("firstName"), u.get("lastName"), d.get("userId"),
             (d.get("army") or {}).get("name") or fac_by_list.get(lid), d.get("armyId"),
             (d.get("warhammer") or {}).get("detachment"),
             (d.get("subFaction") or {}).get("name"), team_by_list.get(lid),
             d.get("listStatus"), d.get("listType"), total, game_size, len(units),
             d.get("created_at"), d.get("updated_at"),
             "https://www.bestcoastpairings.com/list/" + lid,
             txt, d.get("armyListHTML"), drop_by_list.get(lid, 0),
             1 if units else 0))
        con.executemany("INSERT INTO units(list_id,seq,name,points) VALUES (?,?,?,?)",
                        [(lid, s, nm, p) for s, nm, p in units])
        con.executemany("INSERT INTO enhancements(list_id,name) VALUES (?,?)",
                        [(lid, e) for e in enh])
        n += 1
    con.commit()
    backfill_from_text(con)
    print(f"# built {dbpath}: {n} lists, "
          f"{con.execute('SELECT COUNT(*) FROM units').fetchone()[0]} units, "
          f"{con.execute('SELECT COUNT(*) FROM enhancements').fetchone()[0]} enhancements",
          file=sys.stderr)
    con.close()


def _con(dbpath):
    if not os.path.exists(dbpath):
        sys.exit(f"no DB at {dbpath} — run: python3 tools/bcp_db.py build <rawdir>")
    con = sqlite3.connect(dbpath)
    con.row_factory = sqlite3.Row
    return con


def cmd_stats(con):
    for col, label in [("faction", "FACTION"), ("detachment", "DETACHMENT"),
                       ("disposition", "DISPOSITION")]:
        print(f"\n=== by {label} ===")
        for r in con.execute(f"SELECT {col} AS k, COUNT(*) n FROM lists "
                             f"GROUP BY {col} ORDER BY n DESC, k"):
            print(f"  {r['n']:>3}  {r['k']}")
    tp = con.execute("SELECT MIN(total_points),MAX(total_points),AVG(total_points) FROM lists").fetchone()
    print(f"\ntotal_points: min {tp[0]} / max {tp[1]} / avg {tp[2]:.0f}")


def cmd_faction(con, q):
    rows = con.execute("SELECT player,faction,detachment,disposition,total_points,list_url "
                       "FROM lists WHERE faction LIKE ? ORDER BY player", (f"%{q}%",)).fetchall()
    for r in rows:
        print(f"  {r['player'][:24]:25} {str(r['detachment'])[:26]:27} "
              f"{str(r['disposition'])[:16]:17} {r['total_points']}  {r['list_url']}")
    print(f"\n# {len(rows)} lists matching faction '{q}'")


def cmd_unit(con, q):
    rows = con.execute(
        "SELECT l.player,l.faction,u.name,u.points,l.list_url FROM units u "
        "JOIN lists l ON l.list_id=u.list_id WHERE u.name LIKE ? "
        "ORDER BY l.faction,l.player", (f"%{q}%",)).fetchall()
    for r in rows:
        print(f"  {(r['player'] or '?')[:22]:23} {(r['faction'] or '?')[:20]:21} "
              f"{r['name'][:30]:31} {r['points']}  {r['list_url']}")
    print(f"\n# {len(rows)} unit rows matching '{q}' across "
          f"{len(set(r['list_url'] for r in rows))} lists")


def cmd_show(con, q):
    r = con.execute("SELECT * FROM lists WHERE list_id=? OR player LIKE ? LIMIT 1",
                    (q, f"%{q}%")).fetchone()
    if not r:
        sys.exit(f"no list matching '{q}'")
    print(f"{r['player']} — {r['faction']} / {r['detachment']} / {r['disposition']}")
    print(f"{r['total_points']} pts (game {r['game_size']}) · {r['list_status']} · {r['list_url']}\n")
    print(r['army_text'])


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = ap.add_subparsers(dest="cmd", required=True)
    b = sub.add_parser("build"); b.add_argument("rawdir"); b.add_argument("--db", default=DEFAULT_DB)
    b.add_argument("--roster", default=None)
    for name in ("stats", "faction", "unit", "show"):
        s = sub.add_parser(name); s.add_argument("--db", default=DEFAULT_DB)
        if name != "stats":
            s.add_argument("q")
    a = ap.parse_args()
    if a.cmd == "build":
        return build(a.rawdir, a.db, a.roster)
    con = _con(a.db)
    {"stats": lambda: cmd_stats(con), "faction": lambda: cmd_faction(con, a.q),
     "unit": lambda: cmd_unit(con, a.q), "show": lambda: cmd_show(con, a.q)}[a.cmd]()


if __name__ == "__main__":
    main()
