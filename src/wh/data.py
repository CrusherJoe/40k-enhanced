"""Load the YAML data files and expose them as simple typed structures.

Data lives in the repo's `data/` dir (resolved relative to this file so the CLI
works from any cwd). Everything is intentionally plain dicts/dataclasses -- the
data is small and hand-authored.
"""

from __future__ import annotations

import functools
from dataclasses import dataclass, field
from pathlib import Path

import yaml

DATA_DIR = Path(__file__).resolve().parents[2] / "data"


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

    def cost(self, copy: int = 1) -> int:
        """Points for the Nth copy (1-indexed) of this datasheet."""
        if copy <= 1 or self.points_additional is None:
            return self.points_first
        return self.points_additional


@dataclass(frozen=True)
class Mission:
    name: str
    you: str  # disposition key you play
    vs: str  # opponent disposition key
    objective: str | None = None


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


@functools.cache
def matrix() -> dict[str, dict[str, str]]:
    """cells[you_key][opponent_key] -> mission name you play."""
    return _load_yaml("matrix.yaml")["cells"]


@functools.cache
def detachments(faction_file: str = "imperial-knights.yaml") -> list[Detachment]:
    raw = _load_yaml(f"detachments/{faction_file}")
    return [Detachment(**d) for d in raw["detachments"]]


@functools.cache
def datasheets(faction_file: str = "imperial-knights.yaml") -> list[Datasheet]:
    raw = _load_yaml(f"datasheets/{faction_file}")
    out = []
    for d in raw:
        wg = tuple((w["name"], w["points"]) for w in d.get("wargear", []))
        out.append(Datasheet(
            name=d["name"],
            points_first=d["points_first"],
            points_additional=d.get("points_additional"),
            wargear=wg,
        ))
    return out


def mission_for(you: str, opponent: str) -> str:
    """The mission YOU play when your disposition faces the opponent's."""
    return matrix()[you][opponent]


def matchup(you: str, opponent: str) -> tuple[str, str]:
    """(your mission, opponent's mission) for an ordered disposition matchup."""
    return mission_for(you, opponent), mission_for(opponent, you)
