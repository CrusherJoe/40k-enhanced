# -*- coding: utf-8 -*-
"""missions.py — the 11E primary-mission scoring engine, driven by data/*.yaml (gdmissions.app +
GW Warhammer Event Companion). Shared by every sim so scoring reflects the REAL mission, not a stand-in.

Mechanic (Event Companion step 2): each player's Force Disposition is stated ON THEIR LIST. Your
PRIMARY MISSION is read off your OPPONENT's disposition via the asymmetric matrix (matrix.yaml):
    your_mission     = cells[your_disposition][opp_disposition]
    opponent_mission = cells[opp_disposition][your_disposition]
so the two players usually play DIFFERENT missions. missions.yaml gives each mission's VP blocks.

Scoring is modelled from the card structure, capped 15 VP / battle round, 45 primary total. Each
scoring condition is classified (action / kill / control-*) and scored against per-round CAPABILITY
inputs supplied by the army model:
    Caps(action_p, kill_p, control, enemy_home_p)
  * action_p  : P(you perform this mission's Objective Action this turn)   [cheap/fast unit free to act]
  * kill_p    : P(you destroy an enemy unit near an objective this turn)   [the removal engine]
  * control[r]: expected objectives you control at battle round r (0..~5)  [board presence]
  * enemy_home_p : P(you hold the opponent's home objective at end)        [fast, durable pushers]
"""
import math, os, yaml

DATA = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "data")

# Opponent contestation / friction not captured by the per-condition probabilities: even a strong
# list does not convert its theoretical primary. Calibrated so NEUTRAL caps land ~34 and a maxed
# game approaches (not pegs) the 45 cap. See __main__ self-test.
DENIAL = 0.80


def _load(name):
    return yaml.safe_load(open(os.path.join(DATA, name), encoding="utf-8"))


_MISSIONS = {m["name"]: m for m in _load("missions.yaml")}
_MATRIX = _load("matrix.yaml")["cells"]
_DISPS = {d["key"]: d for d in _load("dispositions.yaml")}


def pairing(you_disp, opp_disp):
    """(your_mission_name, opponent_mission_name) for a matchup of dispositions."""
    return _MATRIX[you_disp][opp_disp], _MATRIX[opp_disp][you_disp]


def mission(name):
    return _MISSIONS[name]


class Caps:
    """Per-matchup capability inputs the army model feeds the scorer (probabilities in [0,1];
    control is a list indexed by battle round 1..5 of the expected # objectives you control)."""
    def __init__(self, action_p, kill_p, control, enemy_home_p=0.0):
        self.action_p = action_p
        self.kill_p = kill_p
        self.control = control              # control[0] unused; use control[r] for round r
        self.enemy_home_p = enemy_home_p


# ---- classify a natural-language scoring condition into a type + its met-probability ----
def _prob(text, r, caps):
    t = text.lower()
    ctrl = caps.control[r] if r and r < len(caps.control) else (caps.control[-1] if caps.control else 0)
    if "opponent's home objective" in t or "opponent’s home objective" in t:
        return caps.enemy_home_p, "enemy_home"
    if "performed" in t or "secured the asset" in t or "committed sabotage" in t \
            or "sensor sweep" in t or "vanguard operation" in t or "operation marker" in t and "friendly" in t:
        return caps.action_p, "action"
    if "destroyed" in t or "are destroyed" in t:
        return caps.kill_p, "kill"
    if "three or more objectives" in t:
        return _at_least(ctrl, 3), "control3"
    if "central objective" in t:
        return min(1.0, ctrl / 3.0) * 0.9, "central"     # a central objective specifically
    if "excluding your home" in t or "one or more objectives" in t or "each objective you control" in t:
        return _at_least(ctrl, 1), "control1"
    if "your opponent's operation markers" in t or "operation markers" in t:
        return 0.5, "opmarker"
    return min(1.0, ctrl / 3.0), "control"


def _at_least(expected_ctrl, k):
    """P(control >= k objectives) ~ normal CDF around the expected count (sd ~1 objective, with a
    continuity correction). Fixes the old bug where 'control 3+' fired at ~0.9 for an average of 2.4."""
    z = (expected_ctrl - k + 0.5) / 1.0
    return 0.5 * (1 + math.erf(z / math.sqrt(2)))


def _rounds(phase):
    p = phase.lower()
    if "end of battle" in p:
        return ["END"]
    lo, hi = 1, 5
    if "second battle round onwards" in p or "second to fifth" in p:
        lo = 2
    elif "second to fourth" in p:
        lo, hi = 2, 4
    elif "first & second" in p or "first and second" in p:
        lo, hi = 1, 2
    elif "third" in p and "onwards" in p:
        lo = 3
    return list(range(lo, hi + 1))


def score_primary(mission_name, caps, going_first=True):
    """Expected primary VP over a game for `mission_name` given capability inputs. Caps at 15/round,
    45 total. going_first shifts the control curve slightly earlier (handled by the caller's control[])."""
    m = _MISSIONS[mission_name]
    per_round = {r: 0.0 for r in range(1, 6)}
    end_vp = 0.0
    for block in m.get("scoring", []):
        rs = _rounds(block.get("phase", "Any Battle Round"))
        for r in rs:
            rr = None if r == "END" else r
            prev_p = 1.0
            prev_ev = 0.0
            block_ev = 0.0
            for c in block.get("conditions", []):
                p, _kind = _prob(c["text"], rr, caps)
                rel = c.get("rel")
                if rel == "cumulative":
                    ev = c["vp"] * prev_p * p
                elif rel == "or":
                    ev = max(prev_ev, c["vp"] * p) - prev_ev   # replace, don't double count
                else:
                    ev = c["vp"] * p
                block_ev += ev
                prev_p, prev_ev = p, c["vp"] * p
            if r == "END":
                end_vp += block_ev
            else:
                per_round[r] += block_ev
    total = end_vp * DENIAL
    for r in range(1, 6):
        total += min(15.0, per_round[r] * DENIAL)   # damp for contestation, then the 15 VP/round cap
    return min(45.0, total)                          # 45 primary cap


if __name__ == "__main__":
    # self-test: resolve the Custodes (priority-assets) pairings + a sanity score with strong caps
    strong = Caps(action_p=0.9, kill_p=0.75, control=[0, 1.5, 2.4, 2.6, 2.6, 2.4], enemy_home_p=0.35)
    print("Custodes = priority-assets. Pairings + Custodes primary VP (strong caps):\n")
    for opp in ["take-and-hold", "purge-the-foe", "disruption", "reconnaissance", "priority-assets"]:
        mine, theirs = pairing("priority-assets", opp)
        vp = score_primary(mine, strong)
        print(f"  vs {opp:16} you play {mine:20} ({vp:4.1f} VP)   | opp plays {theirs}")
