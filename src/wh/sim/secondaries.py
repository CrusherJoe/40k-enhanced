"""Real 11E TACTICAL secondary-objective deck — the orthogonal scoring axis that compresses win rates.

The old model folded "secondaries" into ONE monotone board-dominance scalar (kills + enemy-territory +
holding) inside mission.score_turn — so secondary VP just ADDED to whoever was already winning the combat,
amplifying the lead. Real 11E secondaries are ~40% of total VP, DRAWN with variance, and reward things the
board-loser can still do (kill a big model, sneak a unit behind enemy lines, hold the centre) — a scoring
axis only loosely correlated with combat dominance. Injecting that is the single biggest lever toward the
realistic ~40-60% band (see src/wh/sim/__init__.py STATUS).

Model (Tactical, per side): hold up to 2 active cards; at the END OF YOUR OWN TURN score each active card
from real board state + the units you destroyed THIS turn; discard cards that scored (and mulligan a
persistently-dead card) and draw replacements. Game total capped at 40 (the real 11E cap).

Only cards evaluable from the current board model are in the deck (positional + kill-metadata cards). Cards
that need unmodelled state (Cleanse/Plunder actions, Beacon/Burden/A-Tempting-Target unit selection) are
omitted — a competitive player discards a dead card anyway, so an all-live deck is the right abstraction.
`data/secondary-missions.yaml` remains the card source of record (and the runbook's advisory use of it)."""
from __future__ import annotations

from .entities import dist, BOARD_W, BOARD_H

CENTRE = (BOARD_W / 2.0, BOARD_H / 2.0)
GAME_CAP = 40.0                      # 11E total-secondary cap


def is_character(u):
    return u.role == "character" or "CHARACTER" in u.keywords


# ---- board-state helpers (all from the existing Board/Unit model) ------------
def _in_dz(board, pos, side):
    x0, y0, x1, y1 = board.zone[side]
    return x0 <= pos[0] <= x1 and y0 <= pos[1] <= y1


def _in_nml(board, pos):
    return not _in_dz(board, pos, "A") and not _in_dz(board, pos, "B")


def _quarter(pos):
    return (pos[0] < CENTRE[0], pos[1] < CENTRE[1])


def _near_edge(pos, pad=6.0):
    return pos[0] <= pad or pos[0] >= BOARD_W - pad or pos[1] <= pad or pos[1] >= BOARD_H - pad


# ---- per-card evaluators: ctx -> vp (each already capped to its card max) -----
# ctx keys: board, me, opp, held, destroyed (list of dicts: char/wounds/start_strength/on_obj),
#           my_units (me.on_board()), opp_units (opp.on_board()), my_home, opp_home.
def _assassination(c):
    killed = any(d["char"] for d in c["destroyed"])
    all_dead = not any(is_character(u) for u in c["opp"].units if u.alive)
    return 5.0 if (killed or all_dead) else 0.0


def _grievous_blow(c):
    return 5.0 if any(d["start_strength"] >= 13 for d in c["destroyed"]) else 0.0


def _bring_it_down(c):
    return 5.0 if any(d["wounds"] >= 10 for d in c["destroyed"]) else 0.0


def _no_prisoners(c):
    return min(5.0, 2.0 * len(c["destroyed"]))


def _overwhelming_force(c):
    return min(5.0, 3.0 * sum(1 for d in c["destroyed"] if d["on_obj"]))


def _behind_enemy_lines(c):
    n = sum(1 for u in c["my_units"] if _in_dz(c["board"], u.pos, c["opp"].side))
    return min(5.0, 3.0 * n)


def _engage(c):
    qs = {_quarter(u.pos) for u in c["my_units"] if dist(u.pos, CENTRE) > 6.0}
    return 5.0 if len(qs) >= 4 else 3.0 if len(qs) >= 3 else 0.0


def _secure_nml(c):
    mh = c["my_home"]
    n = sum(1 for i, s in c["held"].items()
            if s == c["me"].side and i != mh and _in_nml(c["board"], c["board"].objectives[i]))
    return 5.0 if n >= 2 else 0.0


def _display_of_might(c):
    mine = sum(1 for u in c["my_units"] if _in_nml(c["board"], u.pos))
    theirs = sum(1 for u in c["opp_units"] if _in_nml(c["board"], u.pos))
    return 3.0 if mine > theirs else 0.0


def _centre_ground(c):
    if not any(dist(u.pos, CENTRE) <= 3.0 for u in c["my_units"]):
        return 0.0
    within6 = any(dist(u.pos, CENTRE) <= 6.0 for u in c["opp_units"])
    within3 = any(dist(u.pos, CENTRE) <= 3.0 for u in c["opp_units"])
    return 5.0 if not within6 else 3.0 if not within3 else 0.0


def _outflank(c):
    n = sum(1 for u in c["my_units"]
            if _near_edge(u.pos) and not c["board"].in_territory(u.pos, c["me"].side))
    return 5.0 if n >= 2 else 3.0 if n >= 1 else 0.0


def _defend_stronghold(c):
    hold_home = c["held"].get(c["my_home"]) == c["me"].side
    if not hold_home:
        return 0.0
    clear = not any(_in_dz(c["board"], u.pos, c["me"].side) for u in c["opp_units"])
    return 5.0 if clear else 3.0


def _forward_position(c):
    return 5.0 if c["held"].get(c["opp_home"]) == c["me"].side else 0.0


EVAL = {
    "Assassination": _assassination,
    "A Grievous Blow": _grievous_blow,
    "Bring It Down": _bring_it_down,
    "No Prisoners": _no_prisoners,
    "Overwhelming Force": _overwhelming_force,
    "Behind Enemy Lines": _behind_enemy_lines,
    "Engage on All Fronts": _engage,
    "Secure No Man's Land": _secure_nml,
    "Display of Might": _display_of_might,
    "Centre Ground": _centre_ground,
    "Outflank": _outflank,
    "Defend Stronghold": _defend_stronghold,
    "Forward Position": _forward_position,
}
DECK = list(EVAL)


class Secondaries:
    """Per-army Tactical secondary state: a shuffled deck, up to 2 active cards, running total (cap 40)."""
    def __init__(self, rng):
        order = list(rng.permutation(len(DECK)))
        self.deck = [DECK[i] for i in order]
        self.hand = [self.deck.pop() for _ in range(min(2, len(self.deck)))]
        self.total = 0.0
        self._dead = {}                       # card -> consecutive turns it scored 0

    def _refill_deck(self):
        import numpy as np
        rest = [c for c in DECK if c not in self.hand]
        self.deck = rest                       # simple reshuffle-by-reuse (order not critical at this depth)

    def score(self, ctx, rng):
        """Score active cards at the end of the owner's turn; manage discard/mulligan/draw. Returns VP."""
        if self.total >= GAME_CAP:
            return 0.0
        turn_vp = 0.0
        scored = set()
        for card in self.hand:
            vp = EVAL[card](ctx)
            if vp > 0:
                turn_vp += vp
                scored.add(card)
                self._dead[card] = 0
            else:
                self._dead[card] = self._dead.get(card, 0) + 1
        turn_vp = min(turn_vp, GAME_CAP - self.total)
        self.total += turn_vp
        # discard scored cards; mulligan ONE card that has been dead >=2 turns (the free redraw)
        keep = [c for c in self.hand if c not in scored]
        mull = next((c for c in keep if self._dead.get(c, 0) >= 2), None)
        if mull is not None:
            keep.remove(mull); self._dead.pop(mull, None)
        self.hand = keep
        while len(self.hand) < 2:
            if not self.deck:
                self._refill_deck()
                if not self.deck:
                    break
            self.hand.append(self.deck.pop())
        return turn_vp


def destroyed_meta(u, on_obj):
    """Kill-record for the secondary evaluators, captured when an enemy unit dies this turn."""
    return dict(char=is_character(u), wounds=u.wounds, start_strength=u.start_strength, on_obj=on_obj)
