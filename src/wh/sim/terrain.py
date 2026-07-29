"""Battlefield terrain for the simulator — the Warhammer Event Companion layouts (NOT WTC).

The Event Companion uses one standard TERRAIN FOOTPRINT SET across every layout (data/rules/
event-companion.txt, "Recommended Terrain Area Footprints"):
    4x 6"x4"   2x 10"x2.5"   4x 6"x2"   4x 7"x11.5"   2x 8"x11.5"(polygon)
The 7"x11.5" / 8"x11.5" pieces are the tall LoS-blockers; the set is ~28% board coverage. Each
Force-Disposition-vs-Disposition matchup has three recommended layouts (A/B/C) that rearrange this
same set. The per-layout POSITIONS in the companion are OCR'd tape-measurements, so these are FAITHFUL
RECONSTRUCTIONS (real pieces, correct density, big blockers placed to cut the intended sightlines,
symmetric about centre) keyed per matchup — upgrade to exact coords when the official layout PDF is
available. Board is 44"(x) x 60"(y); centre (22,30).

A ruin is a rect (x0, y0, x1, y1). layout_for(dispA, dispB) -> list of ruins for that matchup.
"""

# The standard footprint set as (w, h) — used to keep reconstructions honest to the real pieces.
FOOTPRINTS = [(6, 4)] * 4 + [(10, 2.5)] * 2 + [(6, 2)] * 4 + [(7, 11.5)] * 4 + [(8, 11.5)] * 2


def _rect(cx, cy, w, h):
    return (cx - w / 2, cy - h / 2, cx + w / 2, cy + h / 2)


def _base_layout():
    """A faithful competitive reconstruction using the real footprint set, symmetric about (22,30).
    The six 11.5"-tall blockers are placed to break the long cross-board sightlines (so a turn-1 alpha
    across the 44"-deep board mostly lacks LoS) while leaving lanes onto the objectives."""
    r = []
    # 4x 7"x11.5" tall blockers — the main sightline breakers (two per half, offset from centre)
    r += [_rect(12, 22, 7, 11.5), _rect(32, 22, 7, 11.5),
          _rect(12, 38, 7, 11.5), _rect(32, 38, 7, 11.5)]
    # 2x 8"x11.5" central polygons flanking the middle objective
    r += [_rect(22, 21, 8, 11.5), _rect(22, 39, 8, 11.5)]
    # 4x 6"x4" — near the flank objectives / deployment approaches
    r += [_rect(9, 13, 6, 4), _rect(35, 13, 6, 4), _rect(9, 47, 6, 4), _rect(35, 47, 6, 4)]
    # 2x 10"x2.5" long low walls across no-man's-land
    r += [_rect(22, 11, 10, 2.5), _rect(22, 49, 10, 2.5)]
    # 4x 6"x2" small light pieces
    r += [_rect(22, 30, 6, 2), _rect(4, 30, 6, 2), _rect(40, 30, 6, 2), _rect(22, 30, 2, 6)]
    return r


# Per-matchup layouts. Keyed by an unordered pair of disposition keys. Start: every matchup uses the
# faithful base reconstruction (correct pieces + density + LoS behaviour); differentiate per matchup
# (A/B/C) once exact coords land. TODO: exact positions from the official Event Companion layout PDF.
_DISPS = ("take-and-hold", "purge-the-foe", "reconnaissance", "priority-assets", "disruption")
LAYOUTS = {frozenset((a, b)): _base_layout() for a in _DISPS for b in _DISPS}


def layout_for(disp_a, disp_b):
    return LAYOUTS.get(frozenset((disp_a, disp_b)), _base_layout())


def layout_for_deployment(name):
    """Terrain for a deployment map. The Event Companion uses ONE footprint set; positions here are the
    faithful reconstruction. (Orienting the blockers to each deployment's sightline axis is a refinement;
    the base set already gives ~28% coverage + LoS breaks around the objectives for every map.)"""
    return _base_layout()
