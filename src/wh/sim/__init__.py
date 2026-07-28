"""wh.sim — a positional, turn-by-turn 40k game simulator (the real thing, not caps math).

============================================================================================
STATUS (2026-07-28): FORK-2 + THE TWO PAYOFF PIECES (optimizer + full meta field) COMPLETE.
Validated for durable/grindy list-vs-list matchups; directional (correct ranking, not to-the-%)
for fast/tempo/alpha matchups. 10 opponent rosters now cover the meta; recommendations engine live.
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
  * rosters.py — units from real DB profiles; keywords normalised to UPPERCASE in mk() so the
    footprint/tall/screening/cover checks fire for DB-built vehicles & monsters (they silently didn't
    before — BSData stores keywords Title-case). THE FULL META FIELD: 10 real winning lists from the
    listhammer archive, each the actual tournament list's disposition, army rule mapped to a real engine
    effect (Oath of Moment -> reroll-1s army-wide [NOT full re-roll: OoM is one target/turn]; monster
    regen -> fnp on the resilient centrepieces; C'tan return -> comeback; jump/suit alpha -> deep-strike
    reserve). necrons() 5-0 triple-C'tan (Withington), drukhari() 6-0 Skysplinter (Martinez), plus
    orks() 5-0 Kult-of-Speed, aeldari() 5-1 Spirit-Conclave wraith, tyranids() 5-0 Norn-Queen monsters,
    space_marines() 6-0 Librarius/Salamanders, blood_angels() 5-0 jump-alpha, tau() 4-0-1 Retaliation
    Cadre, dark_angels() 6-0 Ravenwing, thousand_sons() 5-0 Rubricae. A few datasheets absent from the
    BSData cut (Deffkoptas, Aeldari Warlocks, Crisis Sunforge, Neurolictor omitted) are hand-built
    REPRESENTATIVE and flagged inline. Corrected tapestry stands: Shield Host = Martial Mastery (NO
    Assemblage — that's Auric Champions); Blade Champion 3 Vaultswords profiles; Shadowfield one-and-done.
  * stratagems.py — CP ECONOMY + a stratagem layer driven by the REAL detachment strats (db.strats) + the
    universal 11e core. Each army builds its pool from its chosen detachment(s) — Better Thing 2 runs TWO
    (Shield Host + Tharanatoi Hammerblow), so it gets BOTH sets + core — every strat is classified from its
    DB effect text into a modelled combat effect (defensive -1-to-be-hit / FNP-vs-mortals, offensive
    re-roll/Lethal-Sustained/+1A, Counter-Offensive fight-first), and a CP-spend policy fires the best
    affordable one at each trigger. +1 CP/round both sides. Plus once-per-game unit abilities (Custodian
    Wardens' 4+++). Positional/mission strats (Vigilance Eternal, Rapid Ingress) are pooled but flagged
    UNMODELLED. Toggle stratagems.ENABLED. IMPACT: grindy matchups +5-8% (Necrons 36->41, Orks 17->25) —
    Custodes durability strats + Wardens 4+++ close toward the real ~47%; fast/tempo unchanged (you can't
    strat out of being kited). Coverage: ME gets its full detachments; opponents get core only (their
    detachment strats are a documented follow-up — needs each opponent roster's slug+detachment wired).
  * gauntlet.py — the repeatable "analyze this list" runner: `python -m wh.sim.gauntlet custodes` prints
    (1) TAPESTRY (army/detachment rules + strats from the DB + the rule->engine mapping per unit), (2)
    PER-MATCHUP win% + weakness findings vs all 10 opponents (grindy to-the-point, fast directional), (3)
    optimize's tested swap + detachment recommendations. Writes reports/gauntlet-<me>.md.
  * optimize.py — THE RECOMMENDATIONS ENGINE (2nd payoff piece). `python -m wh.sim.optimize <me> <opp>`
    finds the list's dead weight (via analyze), swaps each for a gap-filling candidate, RE-SIMULATES, and
    reports the TESTED win% delta of each swap ("swap Custodian Guard -> Caladius Grav-tank for +36%").
    Screens at low games, re-verifies the top swaps at --final. Vs the C'tan Necrons it correctly
    surfaces anti-monster tools (Caladius/Telemon/Contemptor). When the winning swaps are vehicles/dreads
    it runs a DETACHMENT TEST: builds the dread-heavy list and re-simulates it under each vehicle
    detachment (via detachments.py) vs Shield Host, reporting each one's win% + DP cost — "should I change
    detachment?" answered by re-simulation, not a guess (correctly shows Might of the Moritoi = +0% for a
    Caladius build, since a Grav-tank isn't a WALKER).
  * detachments.py — Custodes detachment rules as ENGINE EFFECTS (transcribed from the faction pack's
    DETACHMENT RULES blocks): Shield Host (Martial Mastery crit-5), Might of the Moritoi (WALKER +2"M/
    +charge), Solar Spearhead (VEHICLE +2 OC/reroll-1s, 2 DP), Lions (isolated +1/+1, approx), Tharanatoi
    (TERMINATOR ingress reroll charge). apply_detachment()/under() swap an army's rule; a non-Shield-Host
    detachment strips Martial Mastery army-wide, so a swap only pays once enough vehicles are committed.
  * listloader.py — the HYBRID default for turning a real archive list into a roster: parses any full-text
    listhammer entry, resolves units vs BSData (chapter + apostrophe fallbacks), auto-assigns role/threat,
    applies a faction-default tapestry (Astartes Oath), then a per-faction OVERRIDE hook for deep tapestry.
    Datasheets absent from the BSData cut go in data/bsdata/_overrides/<slug>.json (merged by db.bsdata,
    regen-safe) — e.g. the user-supplied Deffkoptas. Curated rosters stay the validated anchors; the loader
    is how NEW opponents get built. (54 of 98 archive entries have truncated text — those need a re-fetch.)
  * analyze.py — THE PAYOFF LAYER. `python -m wh.sim.analyze <me> <opp> [--games N] [--disp ...]` runs
    the matchup and reports board-control curve, enemy units you CAN'T REMOVE, your DEAD WEIGHT, and
    findings + recommendations. Trustworthy where the sim is calibrated (it independently flagged the
    C'tan as unkillable vs the real Necron list).
  * run.py — Monte-Carlo (~25ms/game); builds the board from the disposition matchup's layout.

CALIBRATION (2026-07-28, with the CP/stratagem layer + cover/commander/alpha fixes). Custodes win%:
  * GRINDY band well-calibrated: Thousand Sons ~50, Orks ~47, Necrons ~40 (real 47), Space Marines ~40.
  * FAST/EVASIVE badly UNDER-rated — the open calibration gap: Tau ~7 (real listhammer 39.5!), Aeldari ~1,
    Dark Angels ~3, Drukhari ~13, Tyranids ~16. Real bugs were fixed here (cover was silently gated off for
    non-INFANTRY-tagged units; Tau commanders were built 3x; the reserve alpha + GUIDED were over-modelled)
    and it moved Tau 0->7 — but the RESIDUAL is systemic: slow Custodes can't catch/kill fast fliers/bikes,
    so they get out-shot and out-tempo'd to near-zero when the real matchup is ~40%. Do NOT trust the fast %.
  * Blood Angels ~98 (deep-strike melee alpha under-read — same boundary, opposite sign).
  FAST-MATCHUP INVESTIGATION (2026-07-28, vs the Tau 39.5 anchor) — CONCLUSIVE, do not re-run blind:
    Diagnosed WHY Custodes read ~7% vs Tau (real 39.5). Custodes get TABLED (0/14 by R5) while still
    scoring ~25 VP — they'd win if they survived to hold. Isolation experiments (all one-sided, 200g):
      * Custodes +5+++ FNP  -> 46%   (a ~33% damage cut nails the anchor)
      * Tau half the shots  -> 15%   (output is NOT the main lever — per-phase dmg audited at ~8 wounds)
      * Custodes -1 damage  -> 60%   (damage-PER-HIT one-shotting multi-wound models is the killer)
      * Custodes always cover (-1 hit, one-sided) -> 4%   (hit-COUNT reduction barely helps)
      * Custodes 1.4x melee -> 0% ;  turtle-own-half -> 8%   (they CAN'T reach/kill the fly suits)
    So: only DIRECT damage mitigation moves it; every positional/mechanic fix (cover, character-
    protection [tried+reverted, hurt grindy], turtling, more melee) fails in the blob model. And a
    BLANKET durability buff breaks the already-calibrated grindy anchors (FNP6+ -> necrons 49 GOOD but
    orks 47->67 BAD; FNP5+ -> tau 38 GOOD but orks ->89 BAD). No universal level fits both anchors; no
    clean damage trigger separates "Tau premium shooting" (needs mitigation) from "Ork dakka" (fine).
    VERDICT: the point/blob model structurally cannot represent the positional durability (character
    protection, screening, terrain, killing the suits) that keeps real Custodes competitive vs fast
    premium-shooting armies. Fast-matchup % is DIRECTIONAL-ONLY and reads far too low; real is ~40%.
    Closing it needs a real positional-model upgrade (LoS/screening/character-targeting + a catch-the-
    fliers AI so Custodes trade into the backline), NOT a calibration fudge (which harms the good numbers).

(historical) CALIBRATION vs REAL LISTS (was inverted 95%/74% before the rebuild). Custodes "Better Thing 2" win%:
  * GRINDY/DURABLE matchups land in a believable band ("close, Custodes slight underdog"):
      Necrons (5-0 C'tan) ~36%  |  Orks (5-0) ~40%  |  Space Marines (6-0) ~38%  |  Thousand Sons ~40%.
    (Necrons moved 46% -> 36% when the keyword fix gave the C'tan their correct MONSTER footprint — you
     genuinely can't dogpile 6 units on one C'tan now. More faithful mechanically; both readings agree
     "competitive underdog" vs the real 47%. The single ground-truth point shifted, so treat ~36-46% as
     the band, not 46% as gospel.)
  * FAST/EVASIVE-SHOOTY matchups collapse LOW — DIRECTIONAL ONLY, do NOT read the %:
      Aeldari ~0%  |  T'au ~2%  |  Dark Angels ~1%  |  Drukhari ~8%  |  Tyranids ~12% (monster-mash).
    This is the documented kiting/tempo boundary: slow Custodes can't force engagement on a faster army,
    and the blob/point model over-reads that. Confirmed structural, NOT the Oath model (Aeldari has zero
    Oath and still reads ~0%). Right verdict = "bad matchup"; wrong to quote the number.
  * DEEP-STRIKE MELEE ALPHA over-reads the OTHER way: Blood Angels ~94% FOR Custodes — the sim
    under-rates a full-reserve jump-charge alpha (units sit in reserve, charges from deep strike don't
    connect well). Directional only, same boundary, opposite sign.

KNOWN BOUNDARY (audited, not guessed):
  * Fast/tempo matchups read DIRECTIONALLY, not to-the-point. The residual is the KITING/TEMPO dance
    (a slow durable army can't chase a faster one; it must hold and let the glass break on it) — the
    blob/point model captures this only so far. It is NOT the roster (Drukhari per-unit output audited
    realistic) nor the spatial engine (validated on Necrons). Hunt-to-kill and hold-stickiness AI
    tweaks were tried and REVERTED (net-negative — you can't chase a faster army, and hold-stickiness
    inflates the many-unit side's scoring).
  * Partial: leader auras, stratagem/CP economy, some army rules are approximated.

HOW TO USE:
  * `python -m wh.sim.analyze custodes <opp> [--games N] [--disp ...]` — weakness report (default 2000
    games; 5000 is the calibrated standard). Trust it for the durable/grindy opponents; for fast/alpha
    ones read the direction + the failure-mode findings, not the exact %.
  * `python -m wh.sim.optimize custodes <opp> [--screen 600] [--final 3000]` — TESTED swap
    recommendations + the detachment note. Best on the grindy matchups where the win% is trustworthy.
  * Both take any of the 10 rosters as <opp>. Programmatic diagnose() defaults to 5000 games.
NOT wired into any human-facing doc — the (imperfect but hand-checked) mission-caps sims still back
those; wire these in only for matchups where the sim is calibrated (the grindy band).

TO RESUME (sharply diminishing returns, only if these become priorities):
  * FAST-MATCHUP + ALPHA precision — the biggest gap. A finer kiting/tempo AI (fall-back + reposition +
    when-to-hold-vs-engage for a slow army vs a fast one) AND a working deep-strike-charge alpha (so BA
    stops reading 94%). Same root: the model doesn't dance. Leader-aura + stratagem/CP layers next.
  * DETACHMENT-SWAP simulation — DONE (detachments.py + optimize's DETACHMENT TEST). To extend: model the
    detachment STRATAGEMS/enhancements too (only the army rules are modelled now), and add the other
    factions' detachments so opponents can be tested under theirs.
  * ROSTER coverage — listloader.py is the hybrid default; add the remaining meta factions by picking
    full-text archive lists (or re-fetching the 54 truncated ones). Supply any datasheet absent from the
    BSData cut via data/bsdata/_overrides/<slug>.json (the 4 known gaps — Deffkoptas, Aeldari Warlock
    Conclave + Skyrunners, Crisis Sunforge, Neurolictor — are now filled from user-supplied sheets).
  * Exact Event-Companion layout coords per matchup.
"""
