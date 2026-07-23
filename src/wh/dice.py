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


def _pmf_ndf(n: int, faces: int) -> dict:
    """pmf of the sum of `n` dice, each 1..faces."""
    pmf = {0: 1.0}
    for _ in range(n):
        nxt: dict = {}
        for s, p in pmf.items():
            for f in range(1, faces + 1):
                nxt[s + f] = nxt.get(s + f, 0.0) + p / faces
        pmf = nxt
    return pmf


def expected_reduced(expr, bonus: int = 0, reduce: int = 0) -> float:
    """E[max(1, roll(expr) + bonus - reduce)] -- models a '-N Damage' effect that
    subtracts from the Damage characteristic (min 1) per attack instance, e.g. the
    C'tan 'subtract 1 from the Damage characteristic of that attack'. `bonus` folds
    in Melta etc. that raise the Damage characteristic before the reduction."""
    if reduce <= 0 and bonus == 0:
        return expected(expr)
    s = str(expr).strip()
    if isinstance(expr, (int, float)) or re.fullmatch(r"-?\d+", s):
        return max(1.0, float(s) + bonus - reduce)
    m = _DICE.match(s)
    if not m:
        raise ValueError(f"cannot parse dice expression: {expr!r}")
    n = int(m.group(1) or 1)
    faces = int(m.group(2))
    base = int((m.group(3) or "0").replace(" ", ""))
    return sum(p * max(1.0, tot + base + bonus - reduce)
               for tot, p in _pmf_ndf(n, faces).items())


def _reroll_die(faces: int) -> float:
    """Expected value of one fair die with an optimal single re-roll (re-roll any
    result at or below the mean)."""
    mean = (faces + 1) / 2
    kept = [v for v in range(1, faces + 1) if v > mean]
    rerolled = faces - len(kept)
    return (sum(kept) + rerolled * mean) / faces


def expected_reroll(expr) -> float:
    """Expected value of a dice expression when you may re-roll the dice (used for
    're-roll rolls to determine the Attacks', e.g. Archeotech Autoloaders). The
    fixed bonus is unchanged; each die is re-rolled optimally."""
    if isinstance(expr, (int, float)) or re.fullmatch(r"-?\d+", str(expr).strip()):
        return expected(expr)
    m = _DICE.match(str(expr).strip())
    if not m:
        raise ValueError(f"cannot parse dice expression: {expr!r}")
    n = int(m.group(1) or 1)
    faces = int(m.group(2))
    bonus = int((m.group(3) or "0").replace(" ", ""))
    return n * _reroll_die(faces) + bonus


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
