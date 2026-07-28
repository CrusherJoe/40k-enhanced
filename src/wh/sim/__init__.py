"""wh.sim — a positional, turn-by-turn 40k game simulator (the real thing, not caps math).

============================================================================================
STATUS (2026-07-28): FORK-2 REBUILD COMPLETE + BANKED. Validated for durable/melee list-vs-list
matchups; directional (with the correct disposition ranking) for fast/tempo matchups.
============================================================================================

PURPOSE: score how a list does into KNOWN-WINNING opponent lists (post-Dataslate what-ifs that have no
head-to-head tournament data), expose the list's weaknesses, and recommend fixes. The listhammer
aggregate (data/meta/custodes-matchups.json) is historical/pre-Dataslate CONTEXT, not the calibration
target.

WHAT WORKS + IS VALIDATED
  * combat.py — dice-resolved shooting/melee (numpy), full 11e keyword set (BLAST/RAPID FIRE/TORRENT/
    SUSTAINED/LETHAL/DEVASTATING/ANTI-x/MELTA/LANCE/HEAVY/TWIN-LINKED), hit/wound/AP mods + re-rolls,
    correct 11e allocation (regular damage no-spill, mortals spill, FNP per lost wound). MEAN matches
    wh.mathhammer.expected_damage across test cases.
  * entities.py — units are BLOBS with a footprint radius (model-count / vehicle-monster sized), not
    points. Board carries real WARHAMMER EVENT COMPANION terrain (footprint set: 4x6x4, 2x10x2.5,
    4x6x2, 4x7x11.5, 2x8x11.5 tall blockers, ~28% coverage) with GEOMETRIC line-of-sight (segment-vs-
    ruin, Liang-Barsky). terrain.py keys layouts per disposition matchup (faithful reconstructions;
    swap in exact coords from the official layout PDF when available).
  * game.py — deploy -> 5 rounds (command/move/shoot/charge/fight). SPATIAL/AI pieces that made it work:
      - THREAT-TYPE-AWARE DEPLOYMENT: durable units push forward into cover to trade/close; fragile
        units shelter just outside the enemy's turn-1 melee reach (so a T1 charge only happens on a
        mistake / Infiltrators). Deep-strikers stay in reserve; embarked units ride transports.
      - ENGAGEMENT-PERIMETER LIMIT: a unit can only be attacked by as many enemy units as physically
        fit around its footprint (no dogpiling one brick).
      - MODEL-SCREENING: a non-tall unit behind an intervening blob can't be shot (vehicles/monsters
        seen over infantry).
      - objective-centric movement, efficiency-weighted target priority (wipe scorers, don't chip),
        TRANSPORTS (embark/disembark, open-topped firing), C'tan necrodermis return + reanimation.
  * mission.py — real primary VP from ACTUAL board state (data/missions.yaml + matrix.yaml), asymmetric
    per the Force-Disposition matrix, 15/round + 45 caps, + a state-driven secondary.
  * rosters.py — units from real DB profiles; REAL winning lists loaded from the listhammer archive:
    necrons() = the 5-0 triple-C'tan Awakened Dynasty (Paul Withington); drukhari() = the 6-0
    Skysplinter/EoS (Ridvan Martinez). Corrected tapestry: Shield Host = Martial Mastery (NO Assemblage
    — that's Auric Champions); Blade Champion 3 Vaultswords profiles; Shadowfield = one-and-done 2++.
  * analyze.py — THE PAYOFF LAYER. `python -m wh.sim.analyze <me> <opp> [--games N] [--disp ...]` runs
    the matchup and reports board-control curve, enemy units you CAN'T REMOVE, your DEAD WEIGHT, and
    findings + recommendations. Trustworthy where the sim is calibrated (it independently flagged the
    C'tan as unkillable vs the real Necron list).
  * run.py — Monte-Carlo (~25ms/game); builds the board from the disposition matchup's layout.

CALIBRATION vs REAL LISTS (was inverted 95%/74% before the rebuild):
  * Custodes vs Necrons Awakened Dynasty (real 5-0 C'tan): ~46%  ==  the real listhammer 47%.  NAILED.
  * Custodes vs Drukhari Skysplinter (real 6-0): Purge ~18%, Priority Assets ~10%. DIRECTIONAL: the
    disposition ranking is correct (Priority Assets worse than Purge — matching the team's lived read),
    and it improved from ~3-7%. Still below the aggregate real ~55% BUT that number is (a) vs ALL
    Drukhari lists (this specific elite 6-0 list is harder than average) and (b) pre-Dataslate.

KNOWN BOUNDARY (audited, not guessed):
  * Fast/tempo matchups read DIRECTIONALLY, not to-the-point. The residual is the KITING/TEMPO dance
    (a slow durable army can't chase a faster one; it must hold and let the glass break on it) — the
    blob/point model captures this only so far. It is NOT the roster (Drukhari per-unit output audited
    realistic) nor the spatial engine (validated on Necrons). Hunt-to-kill and hold-stickiness AI
    tweaks were tried and REVERTED (net-negative — you can't chase a faster army, and hold-stickiness
    inflates the many-unit side's scoring).
  * Partial: leader auras, stratagem/CP economy, some army rules are approximated.

HOW TO USE: trust it for durable/grindy list-vs-list what-ifs + the weakness-exposure flow on those.
For fast/alpha matchups, read the direction + the analyzer's failure-mode findings, not the exact %.
NOT wired into any human-facing doc — the (imperfect but hand-checked) mission-caps sims still back
those; wire these in only for matchups where the sim is calibrated.

TO RESUME (fast-matchup precision, sharply diminishing returns): a finer kiting/tempo AI (fall-back +
reposition + when-to-hold-vs-engage for a slow army vs a fast one), leader-aura + stratagem layers,
and exact Event-Companion layout coords per matchup. Only worth it if fast matchups become a priority.
"""
