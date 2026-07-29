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
    def radius(self):
        """Footprint radius (inches) — a unit is a BLOB, not a point. More models = bigger footprint;
        vehicles/monsters are chunky. Used for screening (LoS/charge blocking) + engagement perimeter."""
        if any(k in self.keywords for k in ("VEHICLE", "MONSTER", "TITANIC")):
            return 2.4
        return min(3.6, 0.8 + 0.5 * (self.models ** 0.5))

    @property
    def tall(self):
        """Tall models (vehicles/monsters) are visible over an infantry screen and can see over it."""
        return any(k in self.keywords for k in ("VEHICLE", "MONSTER", "TITANIC"))

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
    slug: str = None           # BSData faction slug — for building this army's stratagem pool
    strat_dets: tuple = ()      # chosen detachment name(s) — the army gets ALL their stratagems + the core set

    def alive_units(self):
        return [u for u in self.units if u.alive and not u.in_reserve]

    def on_board(self):
        # embarked passengers (transport set) are not physically on the board
        return [u for u in self.units if u.alive and not u.in_reserve and u.transport is None]


# Terrain comes from the Warhammer Event Companion layouts (wh.sim.terrain), keyed per disposition
# matchup — a ruin is a rect (x0, y0, x1, y1). LoS is geometric (segment vs ruin).
def _inside(p, r, pad=0.0):
    return (r[0] - pad) <= p[0] <= (r[2] + pad) and (r[1] - pad) <= p[1] <= (r[3] + pad)


def _seg_hits_rect(p1, p2, r):
    """Does the segment p1->p2 pass through rectangle r=(x0,y0,x1,y1)? (Liang-Barsky clip.)"""
    x0, y0, x1, y1 = r
    dx, dy = p2[0] - p1[0], p2[1] - p1[1]
    t0, t1 = 0.0, 1.0
    for p, q in ((-dx, p1[0] - x0), (dx, x1 - p1[0]), (-dy, p1[1] - y0), (dy, y1 - p1[1])):
        if p == 0:
            if q < 0:
                return False
        else:
            t = q / p
            if p < 0:
                t0 = max(t0, t)
            else:
                t1 = min(t1, t)
            if t0 > t1:
                return False
    return True


def seg_hits_circle(p1, p2, c, r):
    """Does segment p1->p2 pass within radius r of point c? (model-screening + charge-path checks)."""
    ax, ay = p1; bx, by = p2; cx, cy = c
    dx, dy = bx - ax, by - ay
    L2 = dx * dx + dy * dy
    if L2 == 0:
        return math.hypot(cx - ax, cy - ay) <= r
    t = max(0.0, min(1.0, ((cx - ax) * dx + (cy - ay) * dy) / L2))
    px, py = ax + t * dx, ay + t * dy
    return math.hypot(cx - px, cy - py) <= r


class Board:
    """Objectives + real terrain (LoS-blocking ruins + cover) for a specific DEPLOYMENT MAP (which comes
    from the mission, which comes from the disposition matchup). Objectives held by higher OC within 3\".
    Pass a `deployment` dict (deployments.for_mission(...)) for the mission's real objectives/zones/terrain;
    a bare `ruins` list falls back to the default long-edge map (back-compat)."""
    def __init__(self, ruins=None, deployment=None):
        from . import terrain, deployments
        self.dep = deployment or deployments.for_mission("Battlefield Dominance")
        self.objectives = list(self.dep["objectives"])
        self.zone = self.dep["zone"]
        self.fwd = self.dep["fwd"]
        self.home = self.dep["home"]
        self.ruins = list(ruins) if ruins is not None else list(self.dep["ruins"])

    def has_los(self, p1, p2):
        """Line of sight p1->p2 unless a ruin blocks it. A ruin does NOT block if a shooter/target is
        effectively inside/at its edge (models on ruins can see out / be seen)."""
        for r in self.ruins:
            if _inside(p1, r, 1.5) or _inside(p2, r, 1.5):
                continue
            if _seg_hits_rect(p1, p2, r):
                return False
        return True

    def near_terrain(self, pos):
        return any(_inside(pos, r, 2.0) for r in self.ruins)

    def control(self, armies):
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
        # Benefit of Cover: any non-vehicle/monster unit within a ruin's footprint gets it. (Gating on the
        # "INFANTRY" keyword dropped cover for units the BSData cut doesn't tag — named characters, Sisters —
        # so most of a Custodes army was taking fire in the open. `not u.tall` = infantry/mounted/etc.)
        for army in armies:
            for u in army.on_board():
                u.in_cover = self.near_terrain(u.pos) and not u.tall

    def home_objective(self, side):
        # the objective nearest that side's home corner/edge (deployment-aware)
        hx, hy = self.home[side]
        return min(range(len(self.objectives)),
                   key=lambda i: (self.objectives[i][0] - hx) ** 2 + (self.objectives[i][1] - hy) ** 2)

    def in_territory(self, pos, side):
        # nearer to your home than the enemy's = your half (works for any deployment geometry)
        da = (pos[0] - self.home["A"][0]) ** 2 + (pos[1] - self.home["A"][1]) ** 2
        db = (pos[0] - self.home["B"][0]) ** 2 + (pos[1] - self.home["B"][1]) ** 2
        return (da <= db) if side == "A" else (db < da)
