"""Units, armies, and the board for the 40k simulator. Units are built from real DB profiles
(wh.sim.rosters) and carry live game state (position, models remaining, flags). A Unit is directly
usable as a combat target (it exposes toughness/save/invuln/keywords/fnp/damage_reduction/models)."""
from __future__ import annotations

import math
from dataclasses import dataclass, field


# Board is 44" x 60" (11e). Objectives at the standard 5-objective layout (centre + 4 flanks).
BOARD_W, BOARD_H = 44.0, 60.0
OBJECTIVES = [(22, 30), (10, 16), (34, 16), (10, 44), (34, 44)]   # (x,y): centre + 4 corners-ish
HOME_Y = {"A": 8.0, "B": 52.0}                                     # each side's home row
DEPLOY_LINE = 22.0                                                 # no-man's-land band around centre


@dataclass
class Unit:
    name: str
    models: int
    wounds: int            # per-model wounds
    move: int
    toughness: int
    save: str
    oc: int
    ld: int = 6
    invuln: str | None = None
    fnp: str | None = None
    damage_reduction: int = 0
    keywords: tuple = ()
    ranged: list = field(default_factory=list)     # weapon dicts
    melee: list = field(default_factory=list)
    abilities: dict = field(default_factory=dict)
    role: str = "line"     # line | anti_tank | anti_horde | character | fast | action | screen
    threat: float = 1.0    # rough per-model value, for target priority + kill VP weighting

    # live state
    cur_w: int = 0
    pos: tuple = (0.0, 0.0)
    side: str = "A"
    in_reserve: bool = False
    deep_strike: bool = False
    in_cover: bool = False
    battle_shocked: bool = False
    fought: bool = False
    advanced: bool = False
    fell_back: bool = False
    charged: bool = False
    reanimate: float = 0.0     # Necrons: fraction of lost wounds returned per turn
    embarked: list = field(default_factory=list)   # units this TRANSPORT is carrying
    transport: object = None   # the transport this unit is riding in (None = on the board)
    open_topped: bool = False  # embarked passengers can shoot

    def __post_init__(self):
        if not self.cur_w:
            self.cur_w = self.wounds

    @property
    def alive(self):
        return self.models > 0

    @property
    def total_w(self):
        return max(0, (self.models - 1) * self.wounds + self.cur_w)

    @property
    def start_strength(self):
        return self._start

    def snapshot_start(self):
        self._start = self.models

    def eff_oc(self):
        return 0 if self.battle_shocked else self.oc * self.models


def dist(a, b):
    return math.hypot(a[0] - b[0], a[1] - b[1])


@dataclass
class Army:
    name: str
    disposition: str
    side: str
    units: list = field(default_factory=list)
    cp: int = 0
    detachment_rules: tuple = ()
    strat: object = None       # a callable hook(game, phase) for stratagem/ability use (optional)

    def alive_units(self):
        return [u for u in self.units if u.alive and not u.in_reserve]

    def on_board(self):
        # embarked passengers (transport set) are not physically on the board
        return [u for u in self.units if u.alive and not u.in_reserve and u.transport is None]


class Board:
    """Objective control + cover. Objectives are held by whichever side has more OC within 3\"."""
    def __init__(self):
        self.objectives = list(OBJECTIVES)
        # a couple of central terrain pieces that grant cover to INFANTRY near them
        self.terrain = [(22, 30, 7.0), (14, 30, 4.0), (30, 30, 4.0)]   # (x, y, radius)

    def control(self, armies):
        """Return {objective_index: side or None} by effective OC within 3\"."""
        held = {}
        for i, o in enumerate(self.objectives):
            oc = {"A": 0, "B": 0}
            for army in armies:
                for u in army.on_board():
                    if dist(u.pos, o) <= 3.0:
                        oc[u.side] += u.eff_oc()
            held[i] = ("A" if oc["A"] > oc["B"] else "B" if oc["B"] > oc["A"] else None)
        return held, None

    def update_cover(self, armies):
        for army in armies:
            for u in army.on_board():
                u.in_cover = any(dist(u.pos, (tx, ty)) <= tr + 1 for tx, ty, tr in self.terrain) \
                    and "INFANTRY" in u.keywords

    def home_objective(self, side):
        # the objective nearest that side's home row
        y = HOME_Y[side]
        return min(range(len(self.objectives)), key=lambda i: abs(self.objectives[i][1] - y))

    def in_territory(self, pos, side):
        return (pos[1] < 30) if side == "A" else (pos[1] >= 30)
