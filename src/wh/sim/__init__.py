"""wh.sim — a positional, turn-by-turn 40k game simulator (the real thing, not caps math).

STATUS (2026-07-28): FOUNDATION + FIRST CALIBRATION. The two teammate-flagged matchups are now
DIRECTIONALLY CORRECT (was inverted):
  * Custodes vs Necrons C'tan:  95% -> ~47% (coin-flip; team read = a loss, so slightly high — a
    candidate for finer calibration with the exact Necron list).
  * Custodes vs Drukhari Skysplinter: 74% -> ~33% (very unfavourable — calibrated to the team read).
The fixes that mattered: (1) an OBJECTIVE-CENTRIC AI (units contest/hold objectives instead of
scrumming in midfield) — the single biggest correction; (2) TRANSPORTS (embark/disembark, open-topped
firing) — Drukhari's whole tempo game; (3) C'tan necrodermis return + stronger reanimation. Still a
representative-roster / partial-special-rules model, not exact — treat win-rates as directional and
keep calibrating against the team's reads. Not wired into human-facing docs yet.

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
