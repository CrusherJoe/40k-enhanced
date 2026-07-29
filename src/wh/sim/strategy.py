"""Adaptive strategy layer. Each army is PROFILED (speed / shooting / melee / durability / bodies) and
CLASSIFIED into an archetype; a SELECTOR then hands it a Strategy (a small parameter set over the game AI's
knobs). Both armies get one — so a gunline holds at range instead of suiciding into melee, a melee-alpha
deep-strikes and commits, a fast army holds-and-evades, and a durable elite turtles-from-cover vs guns but
grinds vs a brick. This is the fix for the multi-mode miscalibration (see ADAPTIVE_STRATEGY.md): a single
greedy AI can't calibrate all matchups; opponent-aware policy can.

The game phase functions read `army.strategy.<knob>`; strategy.equip(army) attaches one lazily."""
from __future__ import annotations

from dataclasses import dataclass


@dataclass
class Strategy:
    name: str = "balanced"
    deploy_depth: float = 0.0     # +forward / -back at deployment (fraction of the no-man's band)
    own_half_bias: float = 0.0    # +prefer own-half objectives (turtle) ; 0 = contest everywhere
    los_hold: float = 1.0         # weight on holding an objective from LoS cover (0 = stand on the open point)
    commit: float = 1.0           # >1 charge eagerly / <1 cagey (hold back, don't overextend into fire)
    hunt_shooters: bool = False   # fast melee run down the enemy's guns
    reserve_aggr: float = 0.0     # +deep-strike CLOSE to charge (assault) / -arrive safe at range (shooty)
    push_home: float = 1.0        # eagerness to push into the enemy half (fast/actioners)


# ---- named presets ---------------------------------------------------------------------------------
BALANCED = Strategy("balanced")
TURTLE   = Strategy("turtle",   deploy_depth=-0.25, own_half_bias=0.8, los_hold=1.7, commit=0.55, push_home=0.4)
GRIND    = Strategy("grind",    deploy_depth=0.0,   own_half_bias=0.2, los_hold=1.1, commit=1.0,  push_home=0.8)
BRACE    = Strategy("brace",    deploy_depth=-0.1,  own_half_bias=0.5, los_hold=1.3, commit=0.8,  push_home=0.6)  # vs melee alpha
HOLD     = Strategy("hold",     deploy_depth=-0.1,  own_half_bias=0.4, los_hold=1.4, commit=0.7,  push_home=0.5)  # durable vs fast
GUNLINE  = Strategy("gunline",  deploy_depth=-0.35, own_half_bias=0.9, los_hold=1.5, commit=0.4,  push_home=0.2, reserve_aggr=-0.6)
KITE     = Strategy("kite",     deploy_depth=-0.1,  own_half_bias=0.35, los_hold=1.2, commit=0.5, push_home=0.9, reserve_aggr=-0.3)
ALPHA    = Strategy("alpha",    deploy_depth=0.25,  own_half_bias=0.0, los_hold=0.7, commit=1.5,  push_home=1.2, reserve_aggr=1.0, hunt_shooters=True)


# ---- army profiler ---------------------------------------------------------------------------------
def _wdmg(w):
    d = str(w.get("D", 1))
    return 4 if "D6" in d else 3 if "D3" in d else (int(d) if d.isdigit() else 2)


def _shots(w):
    a = str(w.get("A", 1))
    return 4 if "D6" in a else 2 if "D3" in a else (int(a) if a.isdigit() else 2)


def profile(army):
    units = [u for u in army.units if u.alive]
    combat = [u for u in units if u.role not in ("action", "screen")] or units
    n = max(1, len(combat))
    speed = sum(u.move for u in combat) / n
    fly = sum(1 for u in units if "FLY" in u.keywords) / max(1, len(units))
    shoot = melee = 0.0
    for u in units:
        for w in u.ranged:
            S = int(w.get("S", 4)); ap = -int(w.get("AP", 0))
            shoot += u.models * _shots(w) * _wdmg(w) * (1.4 if S >= 7 else 1.0) * (1 + 0.4 * ap)
        for w in u.melee:
            S = int(w.get("S", 4)); ap = -int(w.get("AP", 0))
            melee += u.models * _shots(w) * _wdmg(w) * (1.3 if S >= 6 else 1.0) * (1 + 0.4 * ap)
    dura = sum(u.total_w * (2.2 if (u.invuln and int(str(u.invuln)[0]) <= 4) else 1.0) *
               (1.3 if u.toughness >= 7 else 1.0) for u in units)
    bodies = sum(u.models for u in units)
    return dict(speed=speed, fly=fly, shoot=shoot, melee=melee, dura=dura, bodies=bodies)


def archetype(army):
    p = profile(army)
    r = p["shoot"] / max(1.0, p["melee"])            # shooting-to-melee ratio
    if r >= 2.0 and p["speed"] <= 9:                 # shooting-dominant + not super-mobile = GUNLINE (Tau)
        return "gunline"
    if p["melee"] > p["shoot"] * 1.1 and (p["speed"] >= 9 or p["fly"] >= 0.3):
        return "alpha-melee"                         # mobile, melee-heavy = ALPHA (Blood Angels, Drukhari)
    if p["speed"] >= 11 or p["fly"] >= 0.4:
        return "mobile"                              # fast skirmish (Dark Angels)
    if p["bodies"] >= 55:
        return "horde"                               # board-flooding body count (Green Tide) — before grind
    if p["melee"] >= p["shoot"] and p["speed"] <= 8:
        return "grind"                               # slow durable brick (Necrons, Tyranids, Thousand Sons)
    return "balanced"                                # mixed (Aeldari, Orks)


# ---- selector: (my archetype, opp archetype) -> Strategy --------------------------------------------
# rows = the acting army's archetype; picks how IT should play given the opponent.
def select(me_arch, opp_arch):
    if me_arch == "durable-elite":                   # Custodes
        return {"gunline": TURTLE, "mobile": HOLD, "alpha-melee": BRACE,
                "grind": GRIND, "horde": GRIND, "balanced": GRIND}.get(opp_arch, GRIND)
    if me_arch == "gunline":
        return GUNLINE
    if me_arch == "alpha-melee":
        return ALPHA
    if me_arch in ("mobile",):
        return KITE
    if me_arch == "grind":
        return GRIND
    if me_arch == "horde":
        return GRIND
    return BALANCED


def _me_archetype(army):
    # Custodes / Knights are durable-elite (few, tough, elite) — they get the adaptive posture selection;
    # otherwise classify generically.
    if army.slug in ("adeptus-custodes", "imperial-knights"):
        return "durable-elite"
    return archetype(army)


def equip(army, opp):
    """Attach army.strategy given the opponent. Idempotent per (army,opp) pair; recompute if opp changed."""
    key = id(opp)
    if getattr(army, "_strat_for", None) == key and getattr(army, "strategy", None) is not None:
        return
    army.strategy = select(_me_archetype(army), archetype(opp))
    army._strat_for = key
