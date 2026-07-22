"""Movement / threat-range analysis and unit-vs-unit resolution.

Threat range is the crux of a slow army: how far a unit projects lethality,
accounting for Move, Advance (avg D6 = 3.5"), weapon Range, and the 2D6 (avg 7")
charge. With Valourstrike's [ASSAULT] every gun can Advance-and-shoot, which
extends shooting threat by the Advance distance.
"""

from __future__ import annotations

from . import data
from . import mathhammer as mh

AVG_ADVANCE = 3.5   # D6
AVG_CHARGE = 7.0    # 2D6
ENGAGEMENT = 1.0    # models fight within 1"


def _move(profile: dict) -> float:
    return float(profile["stats"]["M"])


def shooting_threat(profile: dict, assault: bool = False) -> list[tuple]:
    """(weapon name, range, threat) where threat = Move [+Advance if assault] + Range."""
    m = _move(profile)
    reach = m + (AVG_ADVANCE if assault else 0)
    out = []
    for w in profile.get("ranged", []):
        rng = w.get("range")
        if isinstance(rng, (int, float)):
            out.append((w["name"], rng, reach + rng))
    return out

def max_shooting_threat(profile: dict, assault: bool = False) -> float:
    st = shooting_threat(profile, assault)
    return max((t for _, _, t in st), default=0.0)


def charge_threat(profile: dict, advance_charge: bool = False) -> float:
    """Move [+Advance if the model can charge after advancing] + 2D6 charge + 1" engage."""
    m = _move(profile)
    return m + (AVG_ADVANCE if advance_charge else 0) + AVG_CHARGE + ENGAGEMENT


def target_from_profile(profile: dict) -> mh.Target:
    """Build a mathhammer Target from an IK datasheet profile."""
    st = profile["stats"]
    return mh.Target(
        toughness=int(st["T"]),
        save=st["Sv"],
        wounds=int(st["W"]),
        invuln=profile.get("invuln"),
        models=1,
        keywords=tuple(k.upper() for k in profile.get("keywords", [])),
    )


def unit_damage(attacker: dict, target: mh.Target, mods: mh.Mods | None = None,
                include_melee: bool = True) -> dict:
    """Total expected damage of an attacker's ranged salvo (+ best melee) vs target."""
    ranged = sum(mh.expected_damage(w, target, mods) for w in attacker.get("ranged", []))
    melee = 0.0
    if include_melee and attacker.get("melee"):
        melee = max(mh.expected_damage(w, target, mods) for w in attacker["melee"])
    return {"ranged": ranged, "melee": melee, "total": ranged + melee}


def rounds_to_kill(dmg_per_turn: float, wounds: int) -> float:
    """Expected shooting phases to remove `wounds`, given expected dmg/turn."""
    if dmg_per_turn <= 0:
        return float("inf")
    return wounds / dmg_per_turn
