"""Practice-layer analysis: turn a chosen army disposition into "what to drill".

You pick ONE disposition but face all five opponent dispositions, so you will
play the five missions in matrix[your-disposition][*]. This module classifies
those missions' scoring conditions into skill themes, tallies the VP each theme
is worth across the five, lists the mission Objective Actions you must execute,
and suggests which secondary missions align with the same themes.
"""

from __future__ import annotations

from collections import defaultdict

from . import data

# Each theme: (label, keyword-substrings that flag a scoring condition).
THEMES = [
    ("hold-objectives", ["objective you control", "objectives you", "control one or more objective",
                         "control two or more", "control three or more", "for each objective you control"]),
    ("central-objectives", ["central objective"]),
    ("flip-objectives", ["did not control at the start", "you did not control"]),
    ("deep-strike-into-enemy", ["opponent's home objective", "opponent's territory",
                                "opponent’s home objective", "opponent’s territory",
                                "expansion objective", "no man's land", "no man’s land"]),
    ("kill-units", ["were destroyed this turn", "unit destroyed this turn", "enemy unit destroyed",
                    "enemy units were destroyed", "is destroyed", "are destroyed", "left the battlefield"]),
    ("board-spread", ["table quarter", "battlefield edge", "different table"]),
    ("mission-action", ["trapped", "decoyed", "consecrated", "surveilled", "triangulated",
                        "sensor sweep", "sabotage", "vanguard operation", "secured the asset",
                        "operation marker", "cleansed", "plundered", "extract intelligence",
                        "guarded", "beacon"]),
]


def classify(text: str) -> list[str]:
    t = text.lower()
    return [label for label, keys in THEMES if any(k in t for k in keys)]


def disposition_missions(disp_key: str) -> list[data.Mission]:
    """The five missions you play with `disp_key`, one per opponent disposition."""
    by_name = {m.name: m for m in data.missions()}
    row = data.matrix()[disp_key]
    return [by_name[row[opp]] for opp in data.dispositions()]


def analyse(disp_key: str) -> dict:
    missions = disposition_missions(disp_key)
    theme_vp: dict[str, float] = defaultdict(float)
    theme_hits: dict[str, int] = defaultdict(int)
    actions = []
    for m in missions:
        seen = set()
        for blk in m.scoring:
            for c in blk.get("conditions", []):
                for lbl in classify(c["text"]):
                    theme_vp[lbl] += c.get("vp", 0)
                    if lbl not in seen:
                        theme_hits[lbl] += 1
                        seen.add(lbl)
        if m.action:
            actions.append((m.name, m.action["name"], m.action.get("effect", "")))
    ranked = sorted(theme_vp.items(), key=lambda kv: (-theme_hits[kv[0]], -kv[1]))
    return {
        "disposition": disp_key,
        "missions": missions,
        "themes": [(lbl, theme_hits[lbl], round(vp, 1)) for lbl, vp in ranked],
        "actions": actions,
    }


def secondary_fit(themes: list[tuple]) -> list[tuple]:
    """Rank secondary missions by how well their scoring matches the top themes."""
    top = {lbl for lbl, hits, _ in themes if hits >= 2}
    scored = []
    for s in data.secondaries():
        text = " ".join(
            c["text"] for grp in ("fixed", "tactical") for blk in (s.get(grp) or [])
            for c in blk.get("conditions", []))
        labels = set(classify(text))
        overlap = labels & top
        if overlap:
            scored.append((s["name"], sorted(overlap)))
    scored.sort(key=lambda x: -len(x[1]))
    return scored
