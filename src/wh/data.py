"""Load the YAML data files and expose them as simple typed structures.

Data lives in the repo's `data/` dir (resolved relative to this file so the CLI
works from any cwd). Everything is intentionally plain dicts/dataclasses -- the
data is small and hand-authored.
"""

from __future__ import annotations

import functools
import os
from dataclasses import dataclass, field
from pathlib import Path

import yaml

DATA_DIR = Path(__file__).resolve().parents[2] / "data"

# Faction registry: short name (or alias) -> data file stem. The active faction
# is read from the WH_FACTION env var (set by the CLI's --faction flag), so the
# same faction-keyed data files work for any army.
FACTIONS = {
    "knights": "imperial-knights.yaml",
    "imperial-knights": "imperial-knights.yaml",
    "ik": "imperial-knights.yaml",
    "sisters": "adepta-sororitas.yaml",
    "sororitas": "adepta-sororitas.yaml",
    "adepta-sororitas": "adepta-sororitas.yaml",
    "sob": "adepta-sororitas.yaml",
}


def active_faction_file() -> str:
    """The data-file stem for the active faction (default Imperial Knights)."""
    key = os.environ.get("WH_FACTION", "imperial-knights").strip().lower()
    return FACTIONS.get(key, "imperial-knights.yaml")


@dataclass(frozen=True)
class Disposition:
    key: str
    name: str
    icon: str | None = None
    theme: str | None = None
    summary: str | None = None


@dataclass(frozen=True)
class Datasheet:
    name: str
    points_first: int
    points_additional: int | None = None  # cost of each 2nd+ copy; None = flat/unique
    wargear: tuple = ()  # ({name, points}, ...) optional point-costed wargear
    sizes: dict | None = None  # {models: points} per legal unit size (MFM). Takes
                               # precedence over points_first/_additional when set.

    def cost(self, copy: int = 1) -> int:
        """Points for the Nth copy (1-indexed) of this datasheet (legacy copy pricing)."""
        if copy <= 1 or self.points_additional is None:
            return self.points_first
        return self.points_additional

    def size_cost(self, models: int | None) -> tuple[int, int, str | None]:
        """(points, models_used, error). Prices a unit by model count against the
        MFM `sizes` table. models=None -> the smallest legal size."""
        if not self.sizes:
            return self.points_first, models or 1, None
        if models is None:
            models = min(self.sizes)
        if models not in self.sizes:
            opts = "/".join(str(m) for m in sorted(self.sizes))
            return 0, models, f"{models} models is not a legal size (MFM options: {opts})"
        return self.sizes[models], models, None


@dataclass
class Mission:
    name: str
    you: str  # disposition key you play
    vs: str  # opponent disposition key
    scoring: list = field(default_factory=list)  # [{phase, when, conditions:[{text,vp,rel?}]}]
    special: str | None = None
    action: dict | None = None  # Objective Action from the card reverse

    def max_vp(self) -> int:
        """Sum of every condition's VP (an upper bound; per-round caps apply in play)."""
        return sum(c.get("vp", 0) for blk in self.scoring for c in blk.get("conditions", []))


@dataclass
class Detachment:
    key: str
    name: str
    source: str
    disposition: str | None  # disposition key, or None if not yet known (TODO)
    dp: int | None  # detachment-point cost 1/2/3, or None if not yet known
    rule: dict | None = None
    enhancements: list[dict] = field(default_factory=list)
    stratagems: list[dict] = field(default_factory=list)
    unique: str | None = None
    stub: bool = False
    notes: str | None = None

    @property
    def complete(self) -> bool:
        """True once the disposition + DP data gap is filled for this detachment."""
        return self.disposition is not None and self.dp is not None


def _load_yaml(name: str):
    with open(DATA_DIR / name, encoding="utf-8") as fh:
        return yaml.safe_load(fh)


@functools.cache
def dispositions() -> dict[str, Disposition]:
    """Disposition key -> Disposition, in canonical order."""
    return {
        d["key"]: Disposition(**d)
        for d in _load_yaml("dispositions.yaml")
    }


@functools.cache
def missions() -> list[Mission]:
    return [Mission(**m) for m in _load_yaml("missions.yaml")]


def mission_by_name(name: str) -> Mission | None:
    n = name.strip().lower()
    exact = [m for m in missions() if m.name.lower() == n]
    if exact:
        return exact[0]
    hits = [m for m in missions() if n in m.name.lower()]
    return hits[0] if len(hits) == 1 else None


@functools.cache
def secondaries() -> list[dict]:
    """Secondary-mission cards (kept as plain dicts; structure varies per card)."""
    return _load_yaml("secondary-missions.yaml")


@functools.cache
def layouts(disposition: str = "purge-the-foe") -> dict:
    """Terrain-layout data for a disposition's matchups (board + per-matchup layouts)."""
    return _load_yaml(f"layouts/{disposition}.yaml")


@functools.cache
def matrix() -> dict[str, dict[str, str]]:
    """cells[you_key][opponent_key] -> mission name you play."""
    return _load_yaml("matrix.yaml")["cells"]


@functools.cache
def detachments(faction_file: str | None = None) -> list[Detachment]:
    raw = _load_yaml(f"detachments/{faction_file or active_faction_file()}")
    return [Detachment(**d) for d in raw["detachments"]]


@functools.cache
def datasheets(faction_file: str | None = None) -> list[Datasheet]:
    raw = _load_yaml(f"datasheets/{faction_file or active_faction_file()}")
    out = []
    for d in raw:
        wg = tuple((w["name"], w["points"]) for w in d.get("wargear", []))
        sizes = d.get("sizes")
        if sizes:
            sizes = {int(k): int(v) for k, v in sizes.items()}
        out.append(Datasheet(
            name=d["name"],
            # points_first stays meaningful: smallest legal size (back-compat + fallback)
            points_first=d.get("points_first", min(sizes.values()) if sizes else 0),
            points_additional=d.get("points_additional"),
            wargear=wg,
            sizes=sizes,
        ))
    return out


@functools.cache
def profiles(faction_file: str | None = None) -> dict[str, dict]:
    """Datasheet name -> full profile dict (stats/weapons/abilities) for the
    active faction (see active_faction_file / the WH_FACTION env var).
    Generated from the BSData wh40k-11e catalogue by tools/gen_profiles.py.
    """
    return {p["name"]: p for p in _load_yaml(f"profiles/{faction_file or active_faction_file()}")}


def profile_for(name: str) -> dict | None:
    return profiles().get(name)


def mission_for(you: str, opponent: str) -> str:
    """The mission YOU play when your disposition faces the opponent's."""
    return matrix()[you][opponent]


def matchup(you: str, opponent: str) -> tuple[str, str]:
    """(your mission, opponent's mission) for an ordered disposition matchup."""
    return mission_for(you, opponent), mission_for(opponent, you)
