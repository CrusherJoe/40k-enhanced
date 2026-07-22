"""Command-line interface for the wh force-disposition planner.

    python -m wh dispositions
    python -m wh matrix [you]
    python -m wh matchup <you> <opponent>
    python -m wh spread <you>
    python -m wh detachments
    python -m wh plan
"""

from __future__ import annotations

import argparse
import sys
from itertools import combinations

from . import army as army_mod
from . import data


def _resolve(part: str) -> str:
    """Resolve a user-typed disposition name/prefix to a canonical key."""
    part = part.strip().lower().replace(" ", "-")
    keys = list(data.dispositions())
    if part in keys:
        return part
    hits = [k for k in keys if k.startswith(part)] or [k for k in keys if part in k]
    if len(hits) == 1:
        return hits[0]
    if not hits:
        sys.exit(f"unknown disposition: {part!r} (known: {', '.join(keys)})")
    sys.exit(f"ambiguous disposition {part!r}: {', '.join(hits)}")


def cmd_dispositions(_args) -> None:
    for d in data.dispositions().values():
        summ = "" if d.summary in (None, "TODO") else f" -- {d.summary}"
        print(f"{d.name:<18} [{d.key}]{summ}")


def cmd_matrix(args) -> None:
    disps = data.dispositions()
    cols = list(disps)
    if args.you:
        rows = [_resolve(args.you)]
    else:
        rows = cols
    width = max(len(m.name) for m in data.missions()) + 2
    header = "you \\ opp".ljust(20) + "".join(disps[c].name[:width - 1].ljust(width) for c in cols)
    print(header)
    for r in rows:
        line = disps[r].name.ljust(20)
        for c in cols:
            line += data.mission_for(r, c)[:width - 1].ljust(width)
        print(line)


def cmd_matchup(args) -> None:
    you, opp = _resolve(args.you), _resolve(args.opponent)
    disps = data.dispositions()
    my_m, their_m = data.matchup(you, opp)
    print(f"{disps[you].name} vs {disps[opp].name}:")
    print(f"  you play : {my_m}")
    print(f"  they play: {their_m}")


def cmd_spread(args) -> None:
    """For a chosen army disposition, the mission spread vs every opponent."""
    you = _resolve(args.you)
    disps = data.dispositions()
    print(f"If you commit to '{disps[you].name}', by opponent disposition:\n")
    print(f"  {'opponent':<18}{'you play':<24}{'they play'}")
    for opp in disps:
        my_m, their_m = data.matchup(you, opp)
        tag = "  (mirror)" if opp == you else ""
        print(f"  {disps[opp].name:<18}{my_m:<24}{their_m}{tag}")


def cmd_detachments(_args) -> None:
    dets = data.detachments()
    disps = data.dispositions()
    print(f"{'detachment':<26}{'DP':<4}{'disposition':<18}{'rules':<8}source")
    for d in dets:
        dp = "?" if d.dp is None else str(d.dp)
        disp = "? (TODO)" if d.disposition is None else disps[d.disposition].name
        rules = "stub" if d.stub else "full"
        print(f"{d.name:<26}{dp:<4}{disp:<18}{rules:<8}{d.source}")
    missing = [d for d in dets if not d.complete]
    if missing:
        print(f"\n!! {len(missing)} detachment(s) still missing disposition/DP: "
              + ", ".join(d.name for d in missing))
    stubs = [d for d in dets if d.stub and d.complete]
    if stubs:
        print(f"\n({len(stubs)} detachment(s) have DP/disposition but rules text is TODO: "
              + ", ".join(d.name for d in stubs) + ")")


def _resolve_detachment(part: str):
    part = part.strip().lower().replace(" ", "-")
    dets = data.detachments()
    hits = [d for d in dets if d.key == part] or \
           [d for d in dets if part in d.key or part in d.name.lower()]
    if len(hits) == 1:
        return hits[0]
    if not hits:
        sys.exit(f"unknown detachment: {part!r}")
    sys.exit(f"ambiguous {part!r}: {', '.join(d.name for d in hits)}")


def cmd_show(args) -> None:
    """Print a detachment's full rule, enhancements and stratagems."""
    d = _resolve_detachment(args.detachment)
    disps = data.dispositions()
    disp = "?" if d.disposition is None else disps[d.disposition].name
    dp = "?" if d.dp is None else d.dp
    print(f"{d.name}  ({dp} DP | disposition: {disp} | source: {d.source})")
    if d.unique:
        print(f"  unique group: {d.unique} (cannot combine with another {d.unique} detachment)")
    if d.rule:
        print(f"\nDETACHMENT RULE -- {d.rule['name']}")
        print(_indent(d.rule.get("text", "")))
    if d.enhancements:
        print("\nENHANCEMENTS")
        for e in d.enhancements:
            pts = f" [{e['points']} pts]" if e.get("points") is not None else ""
            print(f"  - {e['name']}{pts}")
            print(_indent(e.get("text", ""), 6))
    if d.stratagems:
        print("\nSTRATAGEMS")
        for s in d.stratagems:
            typ = f" -- {s['type']}" if s.get("type") else ""
            print(f"  - {s['name']} ({s.get('cp', '?')} CP){typ}")
            for label in ("when", "target", "effect", "restriction"):
                if s.get(label):
                    print(f"      {label.upper():<9} {s[label]}")


def _indent(text: str, n: int = 2) -> str:
    pad = " " * n
    return "\n".join(pad + line for line in (text or "").splitlines())


def cmd_points(args) -> None:
    """List datasheet points, or filter to units matching a substring."""
    sheets = data.datasheets()
    q = (args.unit or "").strip().lower()
    if q:
        sheets = [s for s in sheets if q in s.name.lower()]
        if not sheets:
            sys.exit(f"no datasheet matching {args.unit!r}")
    print(f"{'datasheet':<28}{'1st':>5}{'2nd+':>6}   wargear")
    for s in sheets:
        add = str(s.points_additional) if s.points_additional is not None else "-"
        wg = ", ".join(f"{n} +{p}" for n, p in s.wargear)
        print(f"{s.name:<28}{s.points_first:>5}{add:>6}   {wg}")


def _fmt_ap(ap) -> str:
    return "0" if ap in (0, "0") else str(ap)


def _weapon_row(w: dict, melee: bool) -> str:
    rng = "Melee" if melee else f'{w["range"]}"'
    skill = w.get("WS") if melee else w.get("BS")
    ab = "  " + ", ".join(f"[{a}]" for a in w.get("abilities", [])) if w.get("abilities") else ""
    flag = "  (verify)" if w.get("verify") else ""
    return (f"    {w['name']:<40} {rng:>6} {str(w['A']):>4} {str(skill):>4} "
            f"{str(w['S']):>3} {_fmt_ap(w['AP']):>3} {str(w['D']):>4}{ab}{flag}")


def cmd_profile(args) -> None:
    """Print a full datasheet profile (stats, weapons, abilities)."""
    profs = data.profiles()
    q = args.unit.strip().lower()
    hits = [n for n in profs if n.lower() == q] or [n for n in profs if q in n.lower()]
    if not hits:
        avail = ", ".join(profs)
        sys.exit(f"no profile for {args.unit!r}. Have: {avail}")
    if len(hits) > 1:
        sys.exit(f"ambiguous {args.unit!r}: {', '.join(hits)}")
    p = profs[hits[0]]
    sheet = next((s for s in data.datasheets() if s.name == p["name"]), None)

    st = p["stats"]
    pts = ""
    if sheet:
        add = f" / {sheet.points_additional} each 2nd+" if sheet.points_additional is not None else ""
        pts = f"   {sheet.points_first} pts{add}"
    inv = f'{p["invuln"]} inv' + (" (ranged only)" if p["invuln_ranged_only"] else "")
    print(f"{p['name']}{pts}")
    print(f'  M {st["M"]}"  T {st["T"]}  Sv {st["Sv"]}  W {st["W"]}  Ld {st["Ld"]}  OC {st["OC"]}  |  {inv}')

    hdr = f'    {"weapon":<40} {"rng":>6} {"A":>4} {"Sk":>4} {"S":>3} {"AP":>3} {"D":>4}'
    if p.get("ranged"):
        print("\n  RANGED"); print(hdr)
        for w in p["ranged"]:
            print(_weapon_row(w, melee=False))
    if p.get("melee"):
        print("\n  MELEE"); print(hdr)
        for w in p["melee"]:
            print(_weapon_row(w, melee=True))

    ab = p.get("abilities", {})
    line = []
    if ab.get("core"):
        line.append("Core: " + ", ".join(ab["core"]))
    if ab.get("faction"):
        line.append("Faction: " + ", ".join(ab["faction"]))
    if line:
        print("\n  " + " | ".join(line))
    for a in ab.get("datasheet", []):
        print(f"\n  {a['name']}")
        print(_indent(a["text"], 4))

    dmg = p.get("damaged")
    if dmg:
        print(f"\n  DAMAGED ({dmg['threshold']} W): {dmg['text']}")
    for ep in p.get("extra_profiles", []):
        s = ep["stats"]
        print(f'\n  + {ep["name"]}: M {s["M"]}"  T {s["T"]}  Sv {s["Sv"]}  W {s["W"]}  Ld {s["Ld"]}  OC {s["OC"]}')
    if p.get("wargear_options"):
        print("\n  WARGEAR OPTIONS")
        for o in p["wargear_options"]:
            print(_indent(f"- {o}", 4))
    if p.get("equipped"):
        print(f"\n  Equipped: {p['equipped']}")
    print(f"\n  Keywords: {', '.join(p.get('keywords', []))}")


def cmd_plan(_args) -> None:
    """Enumerate legal detachment combinations totalling 3 DP and the
    dispositions each unlocks. Requires DP + disposition data."""
    dets = [d for d in data.detachments() if d.complete]
    disps = data.dispositions()
    if not dets:
        print("Cannot plan yet: no detachment has both a DP cost and a disposition.")
        print("Fill the `dp` and `disposition` fields in data/detachments/*.yaml")
        print("(the DATA GAP), then re-run. See `wh detachments` for status.")
        return
    print("Legal detachment combinations (total 3 DP) and the dispositions they unlock:")
    print("(distinct detachments only; respects `unique` group constraints)\n")
    count = 0
    for n in (1, 2, 3):
        for combo in combinations(dets, n):  # distinct detachments, no repeats
            if sum(d.dp for d in combo) != 3:
                continue
            if _unique_conflict(combo):
                continue
            count += 1
            names = sorted(d.name for d in combo)
            unlocked = sorted({disps[d.disposition].name for d in combo})
            print(f"  {' + '.join(names)}")
            print(f"      -> dispositions available: {', '.join(unlocked)}")
    if not count:
        print("  (none)")


def _unique_conflict(combo) -> bool:
    """True if two detachments in the combo share a `unique` group (illegal)."""
    groups = [d.unique for d in combo if d.unique]
    return len(groups) != len(set(groups))


def cmd_build(args) -> None:
    """Validate + cost an army list file."""
    a = army_mod.build_file(args.listfile)
    disps = data.dispositions()
    print(f"{a.name}  ({a.points}/{a.points_limit} pts, {a.points_limit - a.points} remaining)")

    dets = " + ".join(f"{d.name} ({d.dp}DP)" for d in a.detachments)
    print(f"\nDetachments ({a.dp_total} DP): {dets or '(none)'}")
    if a.disposition:
        print(f"Disposition: {disps[a.disposition].name}")

    print("\nUnits:")
    for l in a.lines:
        extra = []
        if l.enhancement:
            extra.append(f"+{l.enhancement} ({l.enh_cost})")
        if l.wargear:
            extra.append(f"+{', '.join(l.wargear)} ({l.wargear_cost})")
        cnt = f"{l.count}x " if l.count > 1 else ""
        tail = "  " + "  ".join(extra) if extra else ""
        print(f"  {cnt}{l.datasheet:<26} {l.total:>4} pts{tail}")

    if a.warnings:
        print("\nWarnings:")
        for w in a.warnings:
            print(f"  ~ {w}")
    if a.errors:
        print("\nILLEGAL:")
        for e in a.errors:
            print(f"  x {e}")
    else:
        print("\nLegal list.")
        if a.disposition:
            print(f"Run `wh spread {a.disposition}` to see the missions this disposition plays into.")
    if a.errors:
        sys.exit(1)


def build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(prog="wh", description=__doc__.splitlines()[0])
    sub = p.add_subparsers(dest="cmd", required=True)

    sub.add_parser("dispositions", help="list the 5 force dispositions").set_defaults(fn=cmd_dispositions)

    m = sub.add_parser("matrix", help="show the force-disposition matrix (optionally one row)")
    m.add_argument("you", nargs="?", help="limit to this disposition's row")
    m.set_defaults(fn=cmd_matrix)

    mu = sub.add_parser("matchup", help="both players' missions for a disposition matchup")
    mu.add_argument("you")
    mu.add_argument("opponent")
    mu.set_defaults(fn=cmd_matchup)

    s = sub.add_parser("spread", help="mission spread for one army disposition vs all opponents")
    s.add_argument("you")
    s.set_defaults(fn=cmd_spread)

    sub.add_parser("detachments", help="list Imperial Knights detachments + data-gap status").set_defaults(fn=cmd_detachments)

    pt = sub.add_parser("points", help="datasheet points (MFM); optional unit filter")
    pt.add_argument("unit", nargs="?", help="substring to filter datasheets")
    pt.set_defaults(fn=cmd_points)

    pr = sub.add_parser("profile", help="full datasheet profile (stats/weapons/abilities)")
    pr.add_argument("unit")
    pr.set_defaults(fn=cmd_profile)

    sh = sub.add_parser("show", help="show a detachment's full rule, enhancements and stratagems")
    sh.add_argument("detachment")
    sh.set_defaults(fn=cmd_show)

    sub.add_parser("plan", help="enumerate legal 3-DP detachment combos and unlocked dispositions").set_defaults(fn=cmd_plan)

    b = sub.add_parser("build", help="validate + cost an army list file (YAML)")
    b.add_argument("listfile")
    b.set_defaults(fn=cmd_build)
    return p


def main(argv: list[str] | None = None) -> None:
    args = build_parser().parse_args(argv)
    args.fn(args)


if __name__ == "__main__":
    main()
