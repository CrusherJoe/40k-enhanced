"""wh.sim — a positional, turn-by-turn 40k game simulator (the real thing, not caps math).

============================================================================================
THE DELIVERABLE (2026-07-29): a tournament-prep tool, used MECHANISTICALLY (not for win%).
  python -m wh.sim.dossier <me>          -> full dossier (matchup map + per-archetype runbooks +
                                            list fixes) as reports/dossier-<me>.{md,pdf}
  python -m wh.sim.runbook <me> <opp>    -> one matchup's play guide (priority kills / play-around /
                                            protect / posture+deployment / stratagems / the trap)
  python -m wh.sim.optimize <me> <opp>   -> tested swap + detachment recommendations
  python -m wh.sim.harness                -> sim-vs-anchor scorecard (context only)
me-rosters: `custodes` (teammate's Better Thing 2) and `knights` (the user's List A). The runbook is
built on per-unit damage attribution (game.ON_DAMAGE) — who hurts you, who you can/can't remove, who
does your work. This is the value; the sim maps a matchup's DYNAMICS, it does not predict the win%.
============================================================================================
STATUS (2026-07-28): *** THE SIM DOES NOT PREDICT MATCHUP WIN RATES — proven, read the below. ***
After an exhaustive calibration effort (positional AI, adaptive strategy, combat rework, per-faction
tapestry fidelity, calibration transforms), the definitive result: the sim's Custodes-vs-X win% has
PEARSON CORRELATION ~0.0 with the real listhammer win rates (gauntlet.ANCHORS). REAL Custodes are a
BALANCED army — every matchup lands 39-58% (mean ~48). The sim SPREADS them 7-96% (BA 96, Aeldari 8,
Tau 8) with no signal. Therefore:
  * The per-matchup win% is NOT usable as a prediction. Do not quote it; do not calibrate to it.
  * WHY (proven, not guessed): real 40k win rates are compressed into a narrow band by variance /
    missions / secondaries / deployment / skill; the sim amplifies raw combat edges instead (a melee
    edge -> 96%, a shooting disadvantage -> 8%) AND mis-directs matchups (Aeldari: sim 8, real 58).
  * A calibration transform CAN'T fix it (corr ~0 => the only fit is a constant ~45, erasing all what-if
    discrimination). Per-faction tapestry CAN'T fix it either: Blood Angels with their FULL real rules
    (Red Thirst +2 S on charge, Sanguinary-Priest 5+++, Black Rage, Death Visions fight-on-death) still
    leaves Custodes at 96% (real 50) — Custodes are structurally too dominant in the sim's elite combat,
    and you can't nerf them without wrecking the matchups where they read too LOW. Whole-model limit.
STILL USEFUL (mechanistic, not predictive): the TAPESTRY report (rules from the DB), STRATAGEM/CP
modelling, WEAKNESS diagnostics (what you can't remove / your dead weight), and the optimizer's
WITHIN-matchup RELATIVE deltas where the mechanism is sound (add anti-tank vs a monster wall). The grindy
matchups (Necrons 47, Orks 40) happen to sit near the balanced band. Everything else: ranking + findings,
NEVER the %. Measure any change with `python -m wh.sim.harness`.
============================================================================================

GAME-LAYER UPGRADE (2026-08-06) — *** the 0.0-correlation ceiling was a MISSING-GAME-CONCEPTS problem, not
a combat-tuning one. *** The prior effort tried to fix win% by reworking COMBAT and proved it can't (corr
~0). Diagnosis this round (code-audited): the sim computed VP as a smooth monotone function of combat
dominance, so a combat edge flowed straight to a 96% win rate — every mechanism that DECOUPLES "winning
fights" from "winning games" in real 40k was missing or dead code. Added the four missing concepts, each
measured against the anchors (harness.py) in isolation:
  1. REAL TACTICAL SECONDARY DECK (secondaries.py) — replaced the single monotone "sec" scalar in
     mission.score_turn with a drawn 13-card Tactical deck (data/secondary-missions.yaml) scored from board
     state + per-turn kill metadata (character/big-model/on-objective), discard+redraw, 40 game-cap. The
     orthogonal ~40%-of-VP axis. Alone: werr 25.5 -> 24.5 (compressed the mid-table; extremes still ran off
     because the board-winner also scoops positional/kill secondaries — which is WHY the decision-layer
     fixes below were needed).
  2. VP-AWARE TARGET PRIORITY (game._obj_relevance, threaded into _pick/charge/mval) — fire/charge now tilt
     toward units that are actually SCORING (on/contesting an objective), not just the biggest stat-line.
     Alone: 24.5 -> 22.0 (pulled the runaway matchups in: BA 95->87, drukhari 81->73).
  3. FALL BACK (game._fall_back — revived u.fell_back, which was dead code, only ever reset). A genuinely
     fragile unit about to be wiped AND losing the exchange disengages toward home (forfeiting shoot/charge);
     durable/elite bodies stay and TRADE. Lets the trailing side preserve scoring pieces. 22.0 -> 21.4.
  4. LEADER / ATTACHED CHARACTER (attach.py + game/entities wiring) — 11E-correct: a CHARACTER embeds in a
     Bodyguard unit; TWO-WAY TAPESTRY (best-of merge of crit/re-roll/+S+A-charge/FNP/invuln into the unit);
     the character CANNOT be targeted while attached (no "Look Out Sir" in 11E — the protection is the Leader
     rule) except by PRECISION (now wired: precision shooters can snipe the embedded leader, stripping its
     buff via attach.recompute). Fixes the proven fragility swing (buff characters no longer die turn 1, so
     army-wide multipliers persist). Auto-attaches for curated rosters AND listloader/BCP lists.
  NET (250 games): WEIGHTED ERROR 25.5 -> 18.8 (~26% better; 17.3 at 150g). Matchups it NAILED, previously
  badly wrong: tau 5->26 (real 40), necrons 25->48 (47), dark_angels 25->37 (40), tyranids 11->36 (52),
  thousand_sons ->50 (39). RESIDUAL is exactly the pre-identified COMBAT-model ceiling, NOT a game-layer gap:
  aeldari still -44 (can't crack the T-heavy 2+ wraith wall while being shot), orks/drukhari overshoot
  (+28: Custodes too strong in the sim's elite combat), BA +39 (elite-melee over-read). combat.py UNTOUCHED
  (resolve_attacks mean still matches mathhammer). These four are the biggest accuracy gain since the rebuild
  and are general (help every army, not just Custodes); the win% band is materially compressed but the elite-
  combat extremes remain DIRECTIONAL. Re-measure any further change with `python -m wh.sim.harness`.
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

  POSITIONAL-MODEL UPGRADE ATTEMPT (2026-07-28) — Phase 1 SHIPPED, Phase 2 reverted:
    * Phase 1 = LoS-AWARE HOLD (game._covered_hold): units hold an objective from the adjacent spot that
      is HIDDEN from the most enemy guns (a ruin between = ZERO fire, not -1 to hit — genuine LoS denial,
      the one positional lever that isn't a no-op). SHIPPED. It nudged the grindy anchors the right way
      (Necrons 40->49 vs real 47; SM ->42; TSons ->53) and single games now show the REAL dynamic (with
      it, Custodes beat Tau 56-52 when they survive the early rounds). Cost ~2x sim time (LoS candidate
      search). Aggregate Tau still ~9% — variance is huge; they win the matchup ~9% not ~40% of the time.
    * Phase 2 = HUNT-THE-SHOOTERS (deep-strikers/bikes chase premium guns) — REVERTED. Matchup-unstable:
      helped Dark Angels (3->35) but cratered the anchors (Necrons 49->27/39, Tau ->4), because charging
      a gunline just gets you focus-fired. Deep-strike-hunt arrives exposed; fast-hunt over-aggresses.
    LESSON: a single greedy AI can't calibrate all matchups — the fast fix needs ADAPTIVE strategy
    (turtle-from-cover vs a gunline; aggress vs melee/mobile), a much larger effort with high thrash risk.
    Fast % stays DIRECTIONAL-ONLY. First turn is already a fair 50/50 roll-off (not the bias).

  ADAPTIVE-STRATEGY BUILD + FULL-ANCHOR CALIBRATION (2026-07-28) — INFRASTRUCTURE SHIPPED, ANCHORS NOT MET:
    Got the full real anchor set (gauntlet.ANCHORS, from the HAR) and built the whole layer the scope
    called for: harness.py (anchor-gated scorecard + weighted error), strategy.py (army profiler ->
    archetype classifier -> per-opponent Strategy presets, both sides), the game.py knob wiring
    (deploy_depth / own_half_bias / los_hold / commit / hunt_shooters / reserve_aggr / push_home), and a
    combat SHOOT-WARD calibration hook (rosters.CUSTODES_WARD; FNP vs AP<=-3 premium shooting only, so it
    spares the Orks/Necrons anchors). RESULT: weighted error 25.1 (baseline) -> 24.6 — WITHIN NOISE. The
    adaptive layer did NOT close the anchor gaps. Two gaps dominate and are UNREACHABLE by positioning or
    durability tuning:
      * Blood Angels +48 (sim 98 / real 50) — Custodes win ELITE MELEE too hard; giving BA the ALPHA
        strategy made it WORSE (they connect and still lose the exchange). A melee-exchange bias.
      * Aeldari -56 (sim 2 / real 58) — Custodes can't crack the wraith wall (T6-T10 2+) while being shot;
        neither durability ward nor strategy moves it (roster is clean, no inflation bug).
    VERDICT (now proven across all 9 anchors, not just Tau): the miscalibration is at the COMBAT/GAME-model
    level (too fragile vs premium shooting; too strong in elite melee; can't grind durable walls), NOT the
    positioning/policy level. Tuning has hit its ceiling (~24 weighted error). The infrastructure
    (harness/profiler/strategy/ward) is correct and is the FOUNDATION for the real fix — a combat-model
    rework — but that is research-level, not a tuning pass. Grindy anchors (Necrons 47, Orks 40) remain
    calibrated; the sim stays trustworthy there + for the tapestry/optimizer/stratagems tooling, and
    DIRECTIONAL-ONLY elsewhere. Run `python -m wh.sim.harness` for the live sim-vs-anchor scorecard.

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
