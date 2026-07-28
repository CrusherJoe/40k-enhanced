"""wh.sim — a positional, turn-by-turn 40k game simulator (the real thing, not caps math).

STATUS (2026-07-28): FOUNDATION + CALIBRATED to the team's reads. Both teammate-flagged matchups now
come out Custodes-UNFAVOURABLE (was inverted 95%/74%):
  * Custodes vs Necrons Awakened Dynasty (the REAL 5-0 triple-C'tan list, Paul Withington, from the
    listhammer archive): 95% -> ~37% (a loss — matches "the C'tan roll over Custodes").
  * Custodes vs Drukhari Skysplinter: 74% -> ~39% (unfavourable; still a REPRESENTATIVE Drukhari
    roster — pull the exact list to tighten toward the team's "very unfavourable" ~30%, the same way
    the real Necron list dropped Necrons into place).
The fixes that mattered: (1) an OBJECTIVE-CENTRIC AI (units contest/hold objectives instead of
scrumming in midfield) — the biggest correction; (2) TRANSPORTS (embark/disembark, open-topped
firing) — Drukhari's tempo game; (3) C'tan resilience done right — 4++/-1 damage/5+++ FNP/full-wound
necrodermis return + a MELEE base-contact limit so the whole army can't dogpile one monster; (4) the
REAL 5-0 Necron list (3 C'tan + Skorpekh Lords + characters, not a body-horde).
Still partial special rules (leader auras, stratagem economy, C'tan powers) + representative non-Necron
rosters — treat win-rates as directional-to-calibrated and keep feeding real lists. Not wired into any
human-facing doc yet.

WHAT WORKS + IS VALIDATED
  * combat.py — dice-resolved shooting/melee, numpy-vectorized, honours the 11e keyword set
    (BLAST/RAPID FIRE/TORRENT/SUSTAINED/LETHAL/DEVASTATING/ANTI-x/MELTA/LANCE/HEAVY/TWIN-LINKED),
    hit/wound/AP mods + re-rolls, correct 11e allocation (regular damage no-spill, mortals spill,
    FNP per lost wound). Its MEAN matches wh.mathhammer.expected_damage across test cases (validated).
  * entities.py / board.py — 44x60 board, 5-objective layout, real distances, OC-based objective
    control within 3", cover from terrain.
  * mission.py — real primary VP scored from ACTUAL objective control / kills / actions each round
    (data/missions.yaml + matrix.yaml), 15/round cap; asymmetric per the Force-Disposition matrix.
  * game.py — deployment -> 5 rounds of command/move/shoot/charge/fight, greedy tactical AI.
  * rosters.py — build units from real DB profiles (+ range heuristic + hand-set tapestry abilities).
  * run.py — Monte-Carlo (~20ms/game).

WHAT IS NOT TRUSTWORTHY YET (why the win-rates are wrong, e.g. Custodes 95% vs Necrons C'tan when it
should be a loss):
  1. TACTICAL AI is too naive — it lets the fast/cheap units cheese objectives while durable bricks
     trade, and does not screen, trade objectives, or allocate targets like a real player. Biggest
     single error source.
  2. UNIT SPECIAL RULES are only partly modelled — C'tan survivability/return, full reanimation,
     Rotate Ion Shields, FNP/leader auras, transports (embark/disembark, open-topped), CP/stratagem
     use each turn are missing or approximated. Rosters are representative, not exact lists.
  3. NO CALIBRATION against known results yet. The flagged matchups (Necrons roll over Custodes;
     Drukhari very unfavourable) are the calibration targets and currently come out inverted.

NEXT PHASE to make matchups trustworthy: (a) a real target-priority + screening + objective-trading
AI; (b) per-unit special rules + transports + stratagem economy; (c) accurate meta rosters; (d)
calibrate against the team's known matchup reads. Until then, do NOT wire these numbers into the
human-facing docs — the (imperfect but hand-checked) mission-caps sims still back those.
"""
