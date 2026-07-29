"""Deployment MAPS keyed to the MISSION (which comes from the disposition matchup). Each mission gets its
own objective layout, deployment zones, and terrain — instead of one fixed board for all 25 missions. The
Event Companion's exact deployment cards aren't in the data (separate warhammer-community downloads), so
these are the standard 44"x60" competitive geometries (long-edge / short-edge / diagonal / quarters /
centre), assigned per mission so the board VARIES the way it does across a real event.

A deployment = objectives + a zone rect per side + a 'forward' unit vector (toward the enemy) + terrain.
game.deploy spreads a unit along its zone's wide axis at a depth set by push/forward; Board reads the
objectives/zones/territory split from here."""
from __future__ import annotations

import math
from . import terrain

BOARD_W, BOARD_H = 44.0, 60.0
_C = (BOARD_W / 2, BOARD_H / 2)   # centre (22,30)


def _norm(v):
    d = math.hypot(*v) or 1.0
    return (v[0] / d, v[1] / d)


# Each map: objectives (list of (x,y)); zone per side (x0,y0,x1,y1); fwd per side (toward enemy).
# home is the back-centre of a side's zone (derived); territory split is by which zone-centre a point is nearer.
def _long_edge():   # Dawn of War: deploy along the long (top/bottom) edges, 5 objectives
    return dict(name="long-edge", objectives=[(22, 30), (10, 16), (34, 16), (10, 44), (34, 44)],
                zone={"A": (3, 3, 41, 17), "B": (3, 43, 41, 57)}, fwd={"A": (0, 1), "B": (0, -1)})


def _short_edge():  # Hammer & Anvil: deploy along the short (left/right) edges
    return dict(name="short-edge", objectives=[(22, 30), (13, 16), (13, 44), (31, 16), (31, 44)],
                zone={"A": (3, 3, 16, 57), "B": (28, 3, 41, 57)}, fwd={"A": (1, 0), "B": (-1, 0)})


def _crucible():    # Crucible of Battle: diagonal, corner to corner
    return dict(name="crucible", objectives=[(22, 30), (12, 18), (32, 42), (13, 41), (31, 19)],
                zone={"A": (2, 2, 27, 33), "B": (17, 27, 42, 58)}, fwd={"A": _norm((1, 1)), "B": _norm((-1, -1))})


def _search_destroy():  # Search & Destroy: opposite quarters
    return dict(name="search-destroy", objectives=[(22, 30), (11, 15), (33, 45), (12, 45), (32, 15)],
                zone={"A": (2, 2, 22, 30), "B": (22, 30, 42, 58)}, fwd={"A": _norm((1, 1)), "B": _norm((-1, -1))})


def _sweeping():    # Sweeping Engagement: offset long-edge, 6 objectives (denser mid)
    return dict(name="sweeping", objectives=[(16, 30), (28, 30), (10, 16), (34, 44), (34, 16), (10, 44)],
                zone={"A": (3, 4, 41, 18), "B": (3, 42, 41, 56)}, fwd={"A": (0, 1), "B": (0, -1)})


_MAPS = {m()["name"]: m() for m in (_long_edge, _short_edge, _crucible, _search_destroy, _sweeping)}

# Mission -> deployment. Assigned so each of the 25 missions gets a real map with good variety across the
# disposition matrix (the Event Companion cycles deployments across its missions; exact card pairings aren't
# published in-text, so this is a sensible, deterministic spread by mission character).
MISSION_DEPLOY = {
    # take-and-hold row (objective-dense) -> long-edge / sweeping
    "Battlefield Dominance": "long-edge", "Determined Acquisition": "sweeping", "Immovable Object": "long-edge",
    "Purge and Secure": "search-destroy", "Inescapable Dominion": "sweeping",
    # purge-the-foe row (killy, closer) -> short-edge / crucible
    "Unstoppable Force": "short-edge", "Meatgrinder": "short-edge", "Punishment": "crucible",
    "Consecrate": "long-edge", "Destroyer's Wrath": "crucible",
    # disruption row -> crucible / search-destroy (asymmetric)
    "Death Trap": "crucible", "Delaying Action": "search-destroy", "Locate and Deny": "sweeping",
    "Outmanoeuvre": "search-destroy", "Smoke and Mirrors": "crucible",
    # reconnaissance row (spread, mobile) -> search-destroy / sweeping
    "Gather Intel": "search-destroy", "Reconnaissance Sweep": "sweeping", "Search and Scour": "long-edge",
    "Surveil the Foe": "search-destroy", "Triangulation": "crucible",
    # priority-assets row -> long-edge / short-edge
    "Extract Relic": "long-edge", "Sabotage": "short-edge", "Secure Asset": "long-edge",
    "Vanguard Operation": "short-edge", "Vital Link": "sweeping",
}


def for_mission(mission_name):
    """Return a fresh deployment dict (objectives + zones + fwd + terrain ruins) for a mission."""
    dep = dict(_MAPS.get(MISSION_DEPLOY.get(mission_name, "long-edge"), _MAPS["long-edge"]))
    dep["objectives"] = list(dep["objectives"])
    dep["ruins"] = terrain.layout_for_deployment(dep["name"])
    # home = back-centre of each side's zone (the edge away from the enemy)
    home = {}
    for s in ("A", "B"):
        x0, y0, x1, y1 = dep["zone"][s]
        fx, fy = dep["fwd"][s]
        home[s] = ((x0 + x1) / 2 - fx * (x1 - x0) / 2 * 0.8, (y0 + y1) / 2 - fy * (y1 - y0) / 2 * 0.8)
    dep["home"] = home
    return dep
