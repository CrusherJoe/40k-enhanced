"""Expected values and simple d6 probabilities for 40k dice expressions.

Weapon characteristics are strings like "D6+3", "2D6", "D3", "6". We work in
expected values (standard for mathhammer) rather than full distributions.
"""

from __future__ import annotations

import re

_DICE = re.compile(r"^\s*(\d*)\s*[dD](\d+)\s*([+-]\s*\d+)?\s*$")


def expected(expr) -> float:
    """Expected value of a dice/number expression. `expected("D6+3") == 6.5`."""
    if isinstance(expr, (int, float)):
        return float(expr)
    s = str(expr).strip()
    if re.fullmatch(r"-?\d+", s):
        return float(s)
    m = _DICE.match(s)
    if not m:
        raise ValueError(f"cannot parse dice expression: {expr!r}")
    n = int(m.group(1) or 1)
    faces = int(m.group(2))
    bonus = int((m.group(3) or "0").replace(" ", ""))
    return n * (faces + 1) / 2 + bonus


def target_number(char) -> int:
    """Turn a '3+' / 'N/A' characteristic into the number needed on a d6."""
    s = str(char).strip()
    if not s or s.upper() in ("N/A", "-"):
        return 0
    return int(s.rstrip("+"))


def p_roll(need: int, modifier: int = 0) -> float:
    """P(d6 >= need) after a +/- modifier. A natural 1 always fails, 6 succeeds;
    the required roll is clamped to the 2..6 band per the core rules."""
    if need <= 0:
        return 0.0
    adj = max(2, min(6, need - modifier))
    return (7 - adj) / 6.0


def wound_needed(strength: int, toughness: int) -> int:
    """The d6 needed to wound: S>=2T->2, S>T->3, S==T->4, 2S<=T->6, else 5."""
    if strength >= 2 * toughness:
        return 2
    if strength > toughness:
        return 3
    if strength == toughness:
        return 4
    if strength * 2 <= toughness:
        return 6
    return 5


def with_reroll(p: float, mode: str = "none") -> float:
    """Effective success prob with a reroll. mode: 'none' | 'ones' | 'fails'."""
    if mode == "fails":
        return p + (1 - p) * p
    if mode == "ones":
        return p + (1 / 6) * p  # reroll the ~1/6 of dice that came up 1
    return p
