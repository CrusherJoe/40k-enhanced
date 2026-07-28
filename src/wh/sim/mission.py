"""Real primary-mission scoring from ACTUAL board state (not caps). Reads data/missions.yaml +
data/matrix.yaml. Each battle round, score_turn() evaluates the active player's mission's VP blocks
against the objectives they really hold, whether they killed / did the action this turn, etc. — capped
15/round. end_of_battle() adds the End-of-Battle blocks (e.g. holding the enemy home). A light
state-driven secondary is folded in (kills + pushing enemy territory)."""
from __future__ import annotations

import os
import yaml

from .entities import dist

_DATA = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(
    os.path.abspath(__file__))))), "data")
_MISSIONS = {m["name"]: m for m in yaml.safe_load(open(os.path.join(_DATA, "missions.yaml"), encoding="utf-8"))}
_MATRIX = yaml.safe_load(open(os.path.join(_DATA, "matrix.yaml"), encoding="utf-8"))["cells"]


def pairing(you_disp, opp_disp):
    return _MATRIX[you_disp][opp_disp], _MATRIX[opp_disp][you_disp]


def _state(held, board, me, opp):
    my_home = board.home_objective(me.side)
    enemy_home = board.home_objective(opp.side)
    mine = [i for i, s in held.items() if s == me.side]
    nonhome = [i for i in mine if i != my_home]
    enemy_terr = [i for i in mine if board.in_territory(board.objectives[i], opp.side)]
    # action: a friendly unit sitting on a non-home objective with no enemy contesting it in melee
    action = False
    for i in nonhome:
        o = board.objectives[i]
        friend = any(dist(u.pos, o) <= 3 for u in me.on_board())
        engaged = any(dist(u.pos, o) <= 3 for u in opp.on_board())
        if friend and not engaged:
            action = True
            break
    return dict(mine=len(mine), nonhome=len(nonhome), central=(held.get(0) == me.side),
                enemy_home=(held.get(enemy_home) == me.side), enemy_terr=len(enemy_terr),
                action=action)


def _cond(text, st, kills):
    t = text.lower()
    per = "for each" in t
    if "opponent's home" in t or "opponent’s home" in t:
        return (1 if st["enemy_home"] else 0)
    if any(k in t for k in ("performed", "secured the asset", "committed sabotage", "sensor sweep",
                            "vanguard operation", "maintain control", "a friendly unit")):
        return (1 if st["action"] else 0)
    if "destroyed" in t:
        return (1 if kills > 0 else 0)
    if "three or more objectives" in t:
        return (1 if st["mine"] >= 3 else 0)
    if "central objective" in t:
        return (1 if st["central"] else 0)
    if "opponent's territory" in t or "opponent’s territory" in t:
        return st["enemy_terr"]
    if "did not control at the start" in t or "you did not control" in t:
        return st["nonhome"] if per else (1 if st["nonhome"] else 0)
    if "operation marker" in t:
        return 0.5
    if "objective you control" in t or "one or more objectives" in t or "each objective" in t:
        base = st["nonhome"] if ("excluding your home" in t or "one or more" in t) else st["mine"]
        return base if per else (1 if base else 0)
    return st["nonhome"] if per else (1 if st["nonhome"] else 0)


def _rounds(phase):
    p = phase.lower()
    if "end of battle" in p:
        return "END"
    lo, hi = 1, 5
    if "second battle round onwards" in p or "second to fifth" in p:
        lo = 2
    elif "second to fourth" in p:
        lo, hi = 2, 4
    elif "fifth" in p and "second" not in p:
        lo, hi = 5, 5
    elif "first & second" in p or "first and second" in p:
        lo, hi = 1, 2
    return (lo, hi)


def _block_vp(block, st, kills):
    prev_p = 0.0
    total = 0.0
    for c in block.get("conditions", []):
        val = _cond(c["text"], st, kills) * c["vp"]
        rel = c.get("rel")
        if rel == "cumulative":
            val = val if prev_p > 0 else 0.0
        elif rel == "or":
            total = max(total, val)
            prev_p = val
            continue
        total += val
        prev_p = val
    return total


def score_turn(mission_name, held, board, me, opp, rnd, kills, going_first):
    m = _MISSIONS.get(mission_name)
    if not m:
        return 0.0
    st = _state(held, board, me, opp)
    primary = 0.0
    for block in m.get("scoring", []):
        rr = _rounds(block.get("phase", "Any Battle Round"))
        if rr == "END":
            continue
        lo, hi = rr
        if lo <= rnd <= hi:
            primary += _block_vp(block, st, kills)
    primary = min(15.0, primary)
    # state-driven secondary (~8VP/turn ceiling): kills + pushing enemy territory + holding
    sec = min(8.0, (2.0 if kills > 0 else 0) + 1.5 * st["enemy_terr"] + 1.0 * st["nonhome"])
    return primary + sec * 0.6


def end_of_battle(mission_name, held, board, me, opp):
    m = _MISSIONS.get(mission_name)
    if not m:
        return 0.0
    st = _state(held, board, me, opp)
    vp = 0.0
    for block in m.get("scoring", []):
        if _rounds(block.get("phase", "")) == "END":
            vp += _block_vp(block, st, 0)
    return vp
