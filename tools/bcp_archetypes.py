#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""bcp_archetypes.py — cluster an event's lists into archetypes + player lookup.

In 11E the DETACHMENT is the archetype signal (it sets the rules/playstyle), so each list is
keyed to `<Faction> — <primary detachment>`. The point is a RUNBOOK lookup: given a player name
across the table from you, know the archetype and how to play it.

Reads data/bcp/<event>.sqlite (built by bcp_db.py) + an editable play-notes file
data/bcp/archetype_notes.yaml (verdict + how-to-play per archetype, seeded from the meta-map).
Writes data/bcp/<event>-archetypes.json {archetypes:{...}, player_index:{name->archetype}}.

  python3 tools/bcp_archetypes.py build          # (re)build the archetype record
  python3 tools/bcp_archetypes.py list            # archetypes by size + verdict
  python3 tools/bcp_archetypes.py who "Torres"    # player -> archetype + how to play
  python3 tools/bcp_archetypes.py show "Necrons — Cursed Legion"   # roster + note
"""
import argparse, json, os, re, sqlite3, sys

DB = "data/bcp/lso2026.sqlite"
NOTES = "data/bcp/archetype_notes.yaml"
OUT = "data/bcp/lso2026-archetypes.json"


def primary_det(det):
    """The archetype-driving detachment: drop parentheticals, take the first of a stacked pair,
    normalise whitespace (text-backfill leaves non-breaking spaces that split clusters) + apostrophes."""
    if not det:
        return "(no detachment)"
    d = det.replace("\xa0", " ")                          # nbsp -> space (else 'Grizzled\xa0Company' splits)
    d = re.sub(r"\(.*?\)", "", d)                         # drop "(Command Protocols)" etc.
    d = re.split(r"\s+and\s+|,\s*", d.strip())[0].strip()  # primary of a stacked/listed pair
    d = re.sub(r"\s+", " ", d).replace("’", "'").replace("‘", "'").strip()
    return d


def _load_notes():
    """Tiny YAML reader (avoid a dep): 'Archetype Key:' then indented 'verdict:'/'play:' lines."""
    notes = {}
    if not os.path.exists(NOTES):
        return notes
    cur = None
    for ln in open(NOTES, encoding="utf-8"):
        if not ln.strip() or ln.lstrip().startswith("#"):
            continue
        if not ln.startswith(("  ", "\t")):                      # top-level key
            cur = ln.rstrip(":\n").strip().strip('"')
            notes[cur] = {"verdict": "", "play": ""}
        elif cur:
            m = re.match(r"\s+(verdict|play):\s*(.*)", ln.rstrip("\n"))
            if m:
                notes[cur][m.group(1)] = m.group(2).strip().strip('"')
    return notes


def build():
    con = sqlite3.connect(DB); con.row_factory = sqlite3.Row
    notes = _load_notes()
    rows = con.execute("SELECT player,faction,detachment,disposition,total_points,list_url,"
                       "list_id,parse_ok FROM lists").fetchall()
    # a detachment is faction-unique in 11E — recover the faction for lists that left it blank
    detfac = {}
    for r in rows:
        if r["faction"]:
            detfac.setdefault(primary_det(r["detachment"]), r["faction"])
    arch = {}
    pindex = {}
    for r in rows:
        pdet = primary_det(r["detachment"])
        faction = r["faction"] or detfac.get(pdet) or "Unknown"
        key = f"{faction} — {pdet}"
        a = arch.setdefault(key, {"faction": faction, "detachment": pdet,
                                  "players": [], "dispositions": {},
                                  "verdict": notes.get(key, {}).get("verdict", ""),
                                  "play": notes.get(key, {}).get("play", "")})
        a["players"].append({"player": r["player"], "detachment_full": r["detachment"],
                             "disposition": r["disposition"], "points": r["total_points"],
                             "list_url": r["list_url"], "list_id": r["list_id"]})
        a["dispositions"][r["disposition"]] = a["dispositions"].get(r["disposition"], 0) + 1
        pindex[r["player"]] = key
    for a in arch.values():
        a["size"] = len(a["players"])
    rec = {"event": "Lone Star Open 2026", "n_lists": sum(a["size"] for a in arch.values()),
           "n_archetypes": len(arch), "archetypes": arch, "player_index": pindex}
    json.dump(rec, open(OUT, "w", encoding="utf-8"), indent=1, ensure_ascii=False)
    named = sum(1 for a in arch.values() if a["verdict"])
    print(f"# {rec['n_lists']} lists -> {len(arch)} archetypes ({named} with a play-note) -> {OUT}",
          file=sys.stderr)
    return rec


def _load():
    if not os.path.exists(OUT):
        return build()
    return json.load(open(OUT, encoding="utf-8"))


def cmd_list(rec):
    rows = sorted(rec["archetypes"].items(), key=lambda kv: -kv[1]["size"])
    print(f"{'N':>3}  {'ARCHETYPE':52} VERDICT")
    print("-" * 80)
    for key, a in rows:
        if a["size"] < 1:
            continue
        v = a["verdict"] or ("—" if a["size"] == 1 else "(TBD)")
        print(f"{a['size']:>3}  {key[:51]:52} {v[:24]}")
    multi = sum(1 for _, a in rows if a["size"] >= 2)
    print(f"\n# {len(rows)} archetypes; {multi} have 2+ players; "
          f"{sum(1 for _,a in rows if a['verdict'])} carry a play-note")


def cmd_who(rec, q):
    hits = [(p, k) for p, k in rec["player_index"].items() if q.lower() in p.lower()]
    if not hits:
        sys.exit(f"no player matching '{q}'")
    for player, key in sorted(hits):
        a = rec["archetypes"][key]
        me = next((x for x in a["players"] if x["player"] == player), {})
        print(f"\n{player}")
        print(f"  ARCHETYPE : {key}  (n={a['size']} in field)")
        print(f"  their list: {me.get('detachment_full')} / {me.get('disposition')} / "
              f"{me.get('points')}pts  {me.get('list_url')}")
        print(f"  VERDICT   : {a['verdict'] or '(not yet assessed)'}")
        if a["play"]:
            print(f"  HOW TO PLAY: {a['play']}")


def cmd_show(rec, q):
    keys = [k for k in rec["archetypes"] if q.lower() in k.lower()]
    if not keys:
        sys.exit(f"no archetype matching '{q}'")
    for key in keys:
        a = rec["archetypes"][key]
        disp = ", ".join(f"{d} {n}" for d, n in sorted(a["dispositions"].items(), key=lambda x: -x[1]))
        print(f"\n=== {key}  (n={a['size']}) ===")
        print(f"  dispositions: {disp}")
        print(f"  VERDICT: {a['verdict'] or '(TBD)'}")
        if a["play"]:
            print(f"  PLAY: {a['play']}")
        print("  players:")
        for p in sorted(a["players"], key=lambda x: x["player"]):
            print(f"    {p['player'][:26]:27} {str(p['disposition'])[:14]:15} {p['list_url']}")


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = ap.add_subparsers(dest="cmd", required=True)
    sub.add_parser("build")
    sub.add_parser("list")
    w = sub.add_parser("who"); w.add_argument("q")
    s = sub.add_parser("show"); s.add_argument("q")
    a = ap.parse_args()
    if a.cmd == "build":
        return build()
    rec = _load()
    {"list": lambda: cmd_list(rec), "who": lambda: cmd_who(rec, a.q),
     "show": lambda: cmd_show(rec, a.q)}[a.cmd]()


if __name__ == "__main__":
    main()
