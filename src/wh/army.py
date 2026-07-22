"""Army list builder: validate a list and cost it (11e rules).

A list is a small YAML file, e.g.:

    name: Dominus Gunline
    points_limit: 2000            # optional, defaults to 2000
    detachments: [dominus-foebreakers, gate-warden-lance]   # must total 3 DP
    disposition: priority-assets  # must be granted by one of the detachments
    units:
      - datasheet: Knight Castellan
        count: 1
        enhancement: Blessed Plate         # optional; must belong to a chosen detachment
        wargear: [Rapid-fire battle cannon] # optional; adds points
      - datasheet: Armiger Warglaive
        count: 3

Validation covers what the rules make unambiguous: 3 DP total, distinct
detachments, `unique`-group conflicts, disposition legality, enhancement
ownership/duplication, datasheet-name resolution, and the points budget with
11e escalating per-copy pricing. Rules we can't verify from current data (e.g.
which units a detachment restricts) are left to the player.
"""

from __future__ import annotations

from dataclasses import dataclass, field

import yaml

from . import data

# 11e: an army may include up to 3 Enhancements, each on a different CHARACTER,
# no Enhancement taken more than once. (Enforced as far as our data allows.)
MAX_ENHANCEMENTS = 3

# "Rule of Three": you may include at most 3 of any single datasheet (aggregated
# across all entries of that datasheet), even if points would allow more.
MAX_PER_DATASHEET = 3


@dataclass
class Line:
    datasheet: str
    count: int
    enhancement: str | None
    wargear: list[str]
    unit_cost: int          # escalating cost of `count` copies (no enhancement/wargear)
    enh_cost: int
    wargear_cost: int

    @property
    def total(self) -> int:
        return self.unit_cost + self.enh_cost + self.wargear_cost


@dataclass
class Army:
    name: str
    points_limit: int
    detachments: list
    disposition: str | None
    lines: list[Line] = field(default_factory=list)
    errors: list[str] = field(default_factory=list)
    warnings: list[str] = field(default_factory=list)

    @property
    def dp_total(self) -> int:
        return sum(d.dp for d in self.detachments if d.dp)

    @property
    def points(self) -> int:
        return sum(l.total for l in self.lines)

    @property
    def legal(self) -> bool:
        return not self.errors


def load(path: str) -> dict:
    with open(path, encoding="utf-8") as fh:
        return yaml.safe_load(fh)


def _find_detachment(key_or_name: str):
    k = key_or_name.strip().lower().replace(" ", "-")
    for d in data.detachments():
        if d.key == k or d.name.lower() == key_or_name.strip().lower():
            return d
    return None


def _find_datasheet(name: str):
    n = name.strip().lower()
    exact = [s for s in data.datasheets() if s.name.lower() == n]
    if exact:
        return exact[0]
    hits = [s for s in data.datasheets() if n in s.name.lower()]
    return hits[0] if len(hits) == 1 else None


def build(spec: dict) -> Army:
    disps = data.dispositions()
    army = Army(
        name=spec.get("name", "Untitled"),
        points_limit=int(spec.get("points_limit", 2000)),
        detachments=[],
        disposition=None,
    )

    # --- detachments ---
    seen = set()
    for entry in spec.get("detachments", []):
        d = _find_detachment(entry)
        if d is None:
            army.errors.append(f"unknown detachment: {entry!r}")
            continue
        if d.key in seen:
            army.errors.append(f"detachment taken twice: {d.name}")
            continue
        if d.dp is None:
            army.errors.append(f"{d.name} has no DP cost recorded")
        seen.add(d.key)
        army.detachments.append(d)

    if army.dp_total != 3:
        army.errors.append(f"detachments total {army.dp_total} DP, must be exactly 3")
    groups = [d.unique for d in army.detachments if d.unique]
    if len(groups) != len(set(groups)):
        army.errors.append("two detachments share a `unique` group (illegal combo)")

    # --- disposition ---
    available = {d.disposition for d in army.detachments if d.disposition}
    want = spec.get("disposition")
    if want:
        wk = want.strip().lower().replace(" ", "-")
        if wk not in disps:
            army.errors.append(f"unknown disposition: {want!r}")
        elif wk not in available:
            names = ", ".join(sorted(disps[a].name for a in available)) or "(none)"
            army.errors.append(
                f"disposition '{disps[wk].name}' is not granted by your detachments "
                f"(available: {names})")
        else:
            army.disposition = wk
    else:
        army.warnings.append("no disposition chosen")

    # enhancement catalog for the chosen detachments: name -> (points, detachment)
    enh_catalog = {}
    for d in army.detachments:
        for e in d.enhancements:
            enh_catalog[e["name"].lower()] = (e.get("points") or 0, d.name, e["name"])

    # --- units ---
    used_enh = set()
    for u in spec.get("units", []):
        name = u.get("datasheet", "")
        count = int(u.get("count", 1))
        sheet = _find_datasheet(name)
        if sheet is None:
            army.errors.append(f"unknown datasheet: {name!r}")
            continue
        unit_cost = sum(sheet.cost(i) for i in range(1, count + 1))

        # enhancement
        enh_name = u.get("enhancement")
        enh_cost = 0
        if enh_name:
            hit = enh_catalog.get(enh_name.strip().lower())
            if hit is None:
                army.errors.append(
                    f"enhancement {enh_name!r} on {sheet.name} is not from any chosen detachment")
            else:
                enh_cost = hit[0]
                if hit[2].lower() in used_enh:
                    army.errors.append(f"enhancement used more than once: {hit[2]}")
                used_enh.add(hit[2].lower())
                if count > 1:
                    army.warnings.append(
                        f"{hit[2]} is on a {count}-model entry -- an Enhancement goes on ONE model")

        # wargear
        wargear = u.get("wargear", []) or []
        wg_cost = 0
        wg_map = {n.lower(): p for n, p in sheet.wargear}
        for w in wargear:
            p = wg_map.get(w.strip().lower())
            if p is None:
                army.errors.append(f"{w!r} is not a point-costed wargear option for {sheet.name}")
            else:
                wg_cost += p * count

        army.lines.append(Line(sheet.name, count, enh_name, wargear,
                               unit_cost, enh_cost, wg_cost))

    # Rule of Three: aggregate copies per datasheet across all entries.
    per_sheet: dict[str, int] = {}
    for l in army.lines:
        per_sheet[l.datasheet] = per_sheet.get(l.datasheet, 0) + l.count
    for name, n in per_sheet.items():
        if n > MAX_PER_DATASHEET:
            army.errors.append(
                f"{n}x {name}: max {MAX_PER_DATASHEET} of any datasheet (Rule of Three)")

    if len(used_enh) > MAX_ENHANCEMENTS:
        army.errors.append(f"{len(used_enh)} enhancements used; max is {MAX_ENHANCEMENTS}")

    if army.points > army.points_limit:
        army.errors.append(
            f"army is {army.points} pts, over the {army.points_limit} pt limit "
            f"by {army.points - army.points_limit}")

    return army


def build_file(path: str) -> Army:
    return build(load(path))
