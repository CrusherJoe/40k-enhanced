"""Matchup RUNBOOK generator — the tournament-player deliverable. For your list into an opponent (or a
meta archetype), it simulates the game hundreds of times and turns the mechanics into an actionable plan:
how the game is won/lost, which enemy units to KILL first (the ones actually hurting you, that you CAN
remove), which to play AROUND (can't remove — don't waste effort), your workhorses to leverage and your
liabilities to protect, the deployment/tempo posture, the stratagems that matter, and the failure mode to
avoid. Built on wh.sim.analyze (per-unit damage attribution) + the strategy read + the DB tapestry.

Not a win% oracle (the sim doesn't predict published win rates — see the sim STATUS). It's a mechanistic
map of the matchup's dynamics, which is what you actually use to prep.

  python -m wh.sim.runbook custodes tau [--games 300]
"""
from __future__ import annotations

import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(
    os.path.abspath(__file__))))), "tools"))
import db

from . import analyze, rosters, strategy as St
from ..mathhammer import expected_damage, Mods


def _rep_durable(army):
    """A representative durable body of `army` (for scoring how much an enemy weapon threatens you)."""
    bodies = [u for u in army.units if u.role in ("line", "anti_tank") and u.wounds >= 2] or army.units
    return max(bodies, key=lambda u: u.total_w)


def _unit_output(u, target):
    """Expected wounds `u` deals to `target` in a turn (ranged + melee best case), via mathhammer."""
    out = 0.0
    for pool, melee in ((u.ranged, False), (u.melee, True)):
        if not pool:
            continue
        best = 0.0
        for w in pool:
            try:
                best = max(best, expected_damage(w, target, Mods(charged=melee)) * u.models)
            except Exception:
                pass
        out += best
    return out


def build(build_me, build_opp, games=300, seed=11):
    d = analyze.diagnose(build_me, build_opp, games=games, seed=seed)
    from . import deployments
    d["deployment"] = deployments.for_mission(d["my_mission"])["name"]
    me0, opp0 = build_me(), build_opp()
    St.equip(me0, opp0); St.equip(opp0, me0)
    g = d["games"]
    my_target = _rep_durable(me0)
    opp_target = _rep_durable(opp0)

    # --- enemy units: how much they hurt YOU (real attributed dmg) + can you remove them (survival) ---
    seen = {}
    enemy = []
    for u in opp0.units:
        if u.name in seen:
            continue
        seen[u.name] = 1
        cnt = d["opp_counts"][u.name]
        dmg = d["taken"].get(u.name, 0) / g / max(1, cnt)     # wounds/game to you, per copy
        surv = d["survivors"].get(u.name, 0) / (g * cnt)      # how often it lives to the end
        enemy.append(dict(u=u, name=u.name, cnt=cnt, dmg=dmg, surv=surv))
    # --- your units: workhorses (dmg dealt) vs liabilities (die early) ---
    mine = []
    for u in me0.units:
        if any(m["name"] == u.name for m in mine):
            continue
        cnt = d["me_counts"][u.name]
        dealt = d["dealt"].get(u.name, 0) / g / max(1, cnt)
        surv = d["my_survivors"].get(u.name, 0) / (g * cnt)
        mine.append(dict(u=u, name=u.name, cnt=cnt, dealt=dealt, surv=surv))

    ctrl = [d["ctrl"][r][0] / g for r in range(1, 6)]
    octrl = [d["ctrl"][r][1] / g for r in range(1, 6)]
    return dict(d=d, me=me0, opp=opp0, g=g, enemy=enemy, mine=mine, ctrl=ctrl, octrl=octrl,
                my_strategy=getattr(me0, "strategy", None), my_target=my_target, opp_target=opp_target)


# ---- narrative synthesis -------------------------------------------------------------------------
def _assess(r):
    ctrl, octrl = r["ctrl"], r["octrl"]
    # late-game board margin (R4-5 average) + the attrition margin (do you out-survive?)
    board_margin = (ctrl[3] + ctrl[4]) / 2 - (octrl[3] + octrl[4]) / 2
    my_surv = sum(m["surv"] for m in r["mine"]) / max(1, len(r["mine"]))
    opp_surv = sum(e["surv"] for e in r["enemy"]) / max(1, len(r["enemy"]))
    surv_margin = my_surv - opp_surv
    collapse = ctrl[0] - ctrl[4] >= 1.0 and board_margin <= -0.6      # held early, then swept off
    if board_margin >= 0.3 or (board_margin >= -0.2 and surv_margin >= 0.08):
        head = "FAVOURED — you hold the board and out-last them; the game grinds your way."
        wincon = "Grind: trade your durable bodies into theirs and sit on the objectives. Time is on your side."
    elif collapse:
        head = "HARD — you take the board early then get swept off it. You're behind on tempo."
        wincon = "Deny, don't chase: hold your primary from cover and make THEM come dig you out."
    elif surv_margin <= -0.18:
        head = "ATTRITION-NEGATIVE — they remove you faster than you remove them. Win on tempo, not kills."
        wincon = "Score fast and early; do NOT get drawn into a straight trade you lose."
    else:
        head = "EVEN / GRINDY — decided by the objective play and who commits better."
        wincon = "Win the secondary + primary math; pick your fights, hold the middle, out-score."
    return head, wincon


def _play_around(r):
    """Enemy units that survive most games AND hurt you — don't waste effort killing them; screen/avoid."""
    return sorted([e for e in r["enemy"] if e["surv"] >= 0.6 and e["dmg"] >= 1.0],
                  key=lambda e: -e["dmg"])


def _priority_kills(r):
    """High damage-to-you AND actually removable (survives <55%) — kill these first. Un-removable threats
    are NOT here (they go to PLAY AROUND). score = dmg weighted by how reliably you can remove it."""
    out = []
    for e in r["enemy"]:
        if e["dmg"] < 1.0 or e["surv"] >= 0.55:
            continue
        out.append((e, e["dmg"] * (1.0 - e["surv"])))
    return [e for e, _ in sorted(out, key=lambda x: -x[1])]


def report(r):
    head, wincon = _assess(r)
    d = r["d"]
    L = [f"RUNBOOK — {d['me_name']}  vs  {d['opp_name']}",
         f"  you play {d['my_mission']}  |  they play {d['opp_mission']}  |  deployment: {d.get('deployment','-')}"
         f"  ({r['g']} games simulated)",
         "",
         f"READ: {head}",
         f"WIN CONDITION: {wincon}",
         f"POSTURE: play {r['my_strategy'].name if r['my_strategy'] else 'balanced'} — "
         + _posture_text(r["my_strategy"]),
         f"DEPLOYMENT: {_deploy_advice(r)}",
         "",
         "BOARD CONTROL you vs them (avg objectives, R1->R5):",
         "   you : " + " ".join(f"{v:.1f}" for v in r["ctrl"]),
         "   them: " + " ".join(f"{v:.1f}" for v in r["octrl"]),
         ""]

    pk = _priority_kills(r)
    L.append("PRIORITY KILLS (they hurt you AND you can remove them — kill in this order):")
    L += [f"   {i+1}. {e['name']:30} deals {e['dmg']:.1f} w/turn to you, you remove it {100*(1-e['surv']):.0f}% of games"
          for i, e in enumerate(pk[:5])] or ["   (nothing both threatening and removable)"]

    pa = _play_around(r)
    L += ["", "PLAY AROUND (you CAN'T reliably remove these — screen / avoid / out-score, don't feed them):"]
    L += [f"   - {e['name']:30} survives {100*e['surv']:.0f}%, deals {e['dmg']:.1f} w/turn" for e in pa[:4]] \
        or ["   (none — you can remove their key pieces)"]

    work = sorted([m for m in r["mine"] if m["dealt"] >= 1.0], key=lambda m: -m["dealt"])[:4]
    trade = "" if any(m["surv"] > 0.3 for m in work) else "  (they trade hard and die doing it — that's the plan here, keep them earning until they drop)"
    L += ["", "YOUR WORKHORSES (do the damage — leverage + protect these):" + trade]
    L += [f"   - {m['name']:30} {m['dealt']:.1f} w/turn, survives {100*m['surv']:.0f}%" for m in work]

    weak = sorted([m for m in r["mine"] if m["surv"] < 0.35 and m["dealt"] < 3.0], key=lambda m: m["surv"])
    L += ["", "YOUR LIABILITIES (die before earning their points — protect, hold back, or reconsider):"]
    L += [f"   - {m['name']:30} survives only {100*m['surv']:.0f}%" for m in weak[:4]] or ["   (none — your list holds up)"]

    lean, avoid = _secondaries(r)
    L += ["", "SECONDARIES to lean into (you draw 2/turn — keep+score these, discard the rest):"]
    L += [f"   + {s}" for s in lean] or ["   + (draw-dependent — no strong steer)"]
    if avoid:
        L += ["   DISCARD when drawn: " + ", ".join(avoid)]

    L += ["", "KEY STRATAGEMS this matchup: " + _strat_advice(r)]
    L += ["", f"THE TRAP: {_trap(r, pa)}"]
    return "\n".join(L)


def _secondaries(r):
    """Which of the 18 tactical secondaries suit THIS matchup — from the kill exchange, board hold, and
    the enemy's composition (you draw 2/turn, so this is what to keep+score vs discard)."""
    enemy = r["opp"].units
    g = r["g"]
    kill_rate = 1 - (sum(e["surv"] for e in r["enemy"]) / max(1, len(r["enemy"])))   # how well you remove things
    board_margin = (r["ctrl"][3] + r["ctrl"][4]) / 2 - (r["octrl"][3] + r["octrl"][4]) / 2
    posture = r["my_strategy"].name if r["my_strategy"] else "balanced"
    has_char = any(u.role == "character" and not u.tall for u in enemy)
    # a big model you actually remove often enough for Bring It Down to pay
    big = [e for e in r["enemy"] if any(w >= 10 for w in [e["u"].wounds]) and e["u"].tall]
    kill_big = any(e["surv"] < 0.5 for e in big)
    unkillable_big = any(e["surv"] >= 0.6 for e in big)
    horde = sum(u.models for u in enemy) >= 55
    lean, avoid = [], []
    if kill_rate >= 0.55:                       # you out-kill -> kill secondaries pay
        lean += ["No Prisoners", "Overwhelming Force"]
        if has_char:
            lean.append("Assassination (you can reach their characters)")
    else:                                       # you get out-traded -> don't bank on kills
        avoid += ["No Prisoners", "Overwhelming Force"]
        lean += ["Secure No Man's Land", "Engage on All Fronts"]     # board/action instead
    if kill_big:
        lean.append("Bring It Down (you crack their big models)")
    elif unkillable_big:
        avoid.append("Bring It Down")
    if horde:
        lean.append("A Grievous Blow (anti-horde)")
    if board_margin >= 0.3:
        lean += ["Display of Might", "Centre Ground"]
    if posture in ("kite", "hold") or (r["ctrl"][0] - r["ctrl"][4] >= 0.8):
        lean.append("Behind Enemy Lines")      # you're playing the board/tempo, not the trade
    # de-dupe preserving order, cap
    seen = set(); out = []
    for s in lean:
        k = s.split(" (")[0]
        if k not in seen:
            seen.add(k); out.append(s)
    return out[:5], list(dict.fromkeys(avoid))[:3]


def _deploy_advice(r):
    me, opp = r["me"], r["opp"]
    posture = r["my_strategy"].name if r["my_strategy"] else "balanced"
    ds = [u.name for u in me.units if u.deep_strike]
    fast_enemy = any(u.move >= 11 or "FLY" in u.keywords for u in opp.units if u.role != "action")
    shooty_enemy = sum(len(u.ranged) for u in opp.units) > sum(len(u.melee) for u in opp.units) * 1.5
    parts = []
    if posture in ("turtle", "hold", "gunline", "brace"):
        parts.append("deploy BACK, in/behind cover near your primary — deny a turn-1 alpha and make them come to you")
    elif posture == "grind":
        parts.append("deploy centrally; push your durable bodies onto the mid-board objectives and trade forward")
    elif posture == "kite":
        parts.append("deploy spread for mobility; take objectives and reposition, never sit in the open")
    else:
        parts.append("deploy to contest the board")
    if ds:
        parts.append(f"keep {', '.join(ds[:2])}{' +' if len(ds) > 2 else ''} in reserve — drop them onto objectives or the enemy backfield when it swings the game")
    if fast_enemy or shooty_enemy:
        parts.append("screen your home objectives (they'll try to get behind you)")
    return "; ".join(parts) + "."


def _posture_text(s):
    if s is None:
        return "contest the board and trade."
    return {"turtle": "hold your half from cover; make them walk into you — don't over-extend.",
            "brace": "meet the alpha from cover; counter-punch after their charge lands.",
            "hold": "anchor the objectives; let their speed spend itself against your durability.",
            "grind": "advance and trade; you win the attrition on the objectives.",
            "gunline": "hold range and cover; thin them before they arrive.",
            "kite": "score and reposition; never sit still for their guns.",
            "alpha": "commit hard and fast; you need the alpha to land.",
            "balanced": "contest the board and trade."}.get(s.name, "contest the board and trade.")


def _strat_advice(r):
    dets = getattr(r["me"], "strat_dets", ()) or ()
    getting_shot = r["ctrl"][0] - r["ctrl"][-1] >= 0.8
    if "Shield Host" in dets and getting_shot:
        return "Arcane Genetic Alchemy (4+++ vs mortals) + Unwavering Sentinels (-1 to be hit in melee) to survive; hold with Vigilance Eternal."
    if dets:
        return f"lean on your {dets[0]} defensive strats early, save CP for Counter-Offensive on their key charge."
    return "hold CP for Counter-Offensive vs their best charge; spend defensively when a key unit is focused."


def _trap(r, pa):
    if r["ctrl"][0] - r["ctrl"][-1] >= 0.8:
        return "over-committing forward, taking the board R1-2, then getting shot/swept off it by R4. Hold, don't chase."
    if pa:
        return f"pouring attacks into {pa[0]['name']} (you can't kill it) instead of scoring — ignore it and take points."
    weak = [m for m in r["mine"] if m["surv"] < 0.3]
    if weak:
        return f"exposing {weak[0]['name']} — it dies for nothing. Screen it or hold it back until it matters."
    return "trading your workhorses too early — keep them alive to close the game."


def main():
    import argparse
    ap = argparse.ArgumentParser(description="Generate a matchup runbook for your list vs an opponent.")
    ap.add_argument("me"); ap.add_argument("opp")
    ap.add_argument("--games", type=int, default=300)
    a = ap.parse_args()
    print(report(build(getattr(rosters, a.me), getattr(rosters, a.opp), games=a.games)))


if __name__ == "__main__":
    main()
