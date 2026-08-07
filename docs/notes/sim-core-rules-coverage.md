# Sim ↔ Core Rules Coverage Matrix (11E)

**Version 1.1 · 2026-08-06.** Audit of the `wh.sim` positional engine against the 11E **Core Rules**
(`data/rules/core-rules.txt` + `docs/notes/core-rules-reference.md`, section-cited). v1.1 records the
"fix everything" pass (Batches A–E) that closed most of the v1.0 gaps. This is the **mechanics-axis**
checklist; its companion is the **rules-stack** law ([[tapestry-full-rules-stack]]: Army→Detachment(s)→
Leader/Support→Enhancements→Unit→Weapon/Wargear). Legend: ✅ MODELLED · 🟡 PARTIAL · ❌ MISSING ·
⏸ DEFERRED (real but low-value/hard in the blob model) · ⚪ N/A.

## Turn & phase structure
| Mechanic | § | Status | Engine note |
|---|---|:--:|---|
| 5 battle rounds, both players' turns; phase order | 07 | ✅ | `play_game` |
| Score at end of turn / Command | 14 | ✅ | primary + secondaries end of each player-turn |

## Command phase (01, 08)
| Mechanic | § | Status | Engine note |
|---|---|:--:|---|
| +1 CP / Command phase | 08 | ✅ | `_command` |
| Leadership roll (2D6 ≥ Ld) | 01.06 | ✅ | `_ld_val`; used by battle-shock |
| **Battle-shock** (below half → Ld test → OC 0) | 01.07 | ✅ | revived — real morale variance; below-half units stop scoring |

## Movement phase (03, 09)
| Mechanic | § | Status | Engine note |
|---|---|:--:|---|
| Normal move | 09.05 | ✅ | `_move` |
| Remain Stationary (enables HEAVY) | 09.04 | ✅ | tracked; `mods.stationary` now set → HEAVY +1 fires |
| Advance (M+D6; no shoot [except ASSAULT]/charge) | 09.06 | ✅ | `_should_advance` |
| Fall Back (no shoot/charge) | 09.07 | ✅ | `_fall_back` |
| Desperate Escape (battle-shocked Fall Back) | 09.07 | ✅ | per-model 1-2 loss |
| Battle Focus / Fade Back (Fall Back and STILL act) | Aeldari | ✅ | token budget; `_faded` exempt from the ban |
| Coherency (2"/9") | 03.03 | ⏸ | blob model has no per-model coherency (low value) |
| Engagement Range = 2" | 03.04 | 🟡 | sim uses 3"+footprint (consistent across shoot/fight) |
| Strategic Reserves (edge, R2+, die end R3) | 20 | 🟡 | staggered arrival; edge/destroy constraints approximate |
| Deep Strike >9" → same-turn charge ~28% | 24.09 | ✅ | drop pushed to >9" from nearest enemy |

## Shooting phase (04, 05, 10)
| Mechanic | § | Status | Engine note |
|---|---|:--:|---|
| Eligibility (Advanced/Fell Back/engaged) | 10 | ✅ | `_can_fire` + `_engaged` |
| [ASSAULT] after Advancing | 24.04 | ✅ | `_can_fire` |
| [PISTOL] engaged infantry, at the engaging enemy | 10.06 | ✅ | `_can_fire` |
| MONSTER/VEHICLE shoot out of combat at −1 (BLAST can't hit engaged) | 10.06 | ✅ | tar-pit costs a gun-Knight −1, not its guns |
| Geometric LoS + footprint screening | 10 | ✅ | `has_los` + `_screened` |
| Plunging Fire (+1 BS, TOWERING ≤12") | 22.05 | ✅ | tall shooter vs ground-level ≤12" |
| [HEAVY] +1 if stationary | 24.16 | ✅ | now that stationary is set |
| Snap shooting | 15.09 | ⏸ | only used by Overwatch (modelled there) |
| Indirect Fire penalties | 10.07 | ⏸ | no indirect-fire units in the meta rosters |
| Vertical/true-3D LoS | 13 | 🟡 | `tall` flag proxy (blob limit) |

## Attack sequence (04, 05)
| Mechanic | § | Status | Engine note |
|---|---|:--:|---|
| Hit→Wound→Save→Damage, 1 fails / 6 crits, S-vs-T | 04-05 | ✅ | `combat.resolve_attacks`, matches mathhammer |
| FNP; no-spill damage; mortals spill | 05 | ✅ | `apply_damage` |
| All weapon keywords (Lethal/Sustained/Dev/Anti/Melta/Lance/Heavy/Twin/Blast/Torrent/RapidFire/IgnoresCover) | 24 | ✅ | `combat._kw` |
| Wound allocation order / character-last | 05 | 🟡 | via the Leader attach model (character not targetable while attached) |

## Charge phase (11)
| Mechanic | § | Status | Engine note |
|---|---|:--:|---|
| Declare ≤12"; 2D6; reach ER; not Advanced/FellBack/engaged | 11 | ✅ | `_charge_and_fight` |
| **Fire Overwatch** (snap; TORRENT auto; excl TITANIC; once/turn, 1CP) | 15.08 | ✅ | `_overwatch` |
| Counter-Offensive (fight first, 2CP) | 15 | ✅ | `wants_counter_offensive` |
| **Heroic Intervention** | 15.11 | ⏸ | niche reactive counter-charge, low value — deferred |

## Fight phase (12)
| Mechanic | § | Status | Engine note |
|---|---|:--:|---|
| Fights First then alternate; perimeter cap | 12/24.13 | ✅ | `_interleave` + `maxatk` |
| **Pile-in 3"** (12.03) / **Consolidate 3"** (12.08) | 12 | ✅ | `_pile_in` / `_consolidate` (stays on held objectives) |

## Terrain & cover (13)
| Mechanic | § | Status | Engine note |
|---|---|:--:|---|
| Benefit of Cover −1; [IGNORES COVER]; Stealth = cover | 13/24 | ✅ | `combat` cover + Stealth |
| Obscuring/dense LoS block | 13.10-11 | 🟡 | ruins as solid rects; no light/dense split |
| Hidden / Gone to Ground | 13.09/11 | ⏸ | positional-detection model absent (blob) |
| Objectives as terrain-area footprints | 14.01 | 🟡 | point + 3" control radius, not a footprint area |
| VEHICLE/MONSTER can't move through dense terrain | 13.06 | ⏸ | straight-line movement (blob) |

## Objectives & scoring (14)
| Mechanic | § | Status | Engine note |
|---|---|:--:|---|
| Level of Control (higher OC; tie = neither) | 14.02 | ✅ | `Board.control` (recompute by presence — rules-correct) |
| **Secured** (ability-granted sticky) | 14.03 | ✅ | `Board.secured`; dormant unless a unit has the ability |
| Battle-shocked OC = 0 | 14.02 | ✅ | `eff_oc` + live battle-shock |
| Primary VP capped 15/rd; real secondary deck | 14 | ✅ | `mission` + `secondaries` |

## Core abilities (24)
| Ability | § | Status | Engine note |
|---|---|:--:|---|
| **Deadly Demise X** (6 → X mortals in 6") | 24.08 | ✅ | `_deadly_demise` |
| Deep Strike | 24.09 | ✅ | >9" enforced |
| **Lone Operative** (not targetable >12") | 24.24 | ✅ | target filter |
| **Stealth** (benefit of cover) | 24.33 | ✅ | `combat` |
| FNP / Fights First / mortal wounds | 24/22 | ✅ | combat |
| Scouts / Infiltrators | 24.31/20 | 🟡 | deploy heuristics; no explicit pre-game move |
| Hover / Aircraft | 24.17/23 | ⚪ | no aircraft in the meta rosters |

## Leaders, Support & Attached Units (19)
| Mechanic | § | Status | Engine note |
|---|---|:--:|---|
| Attach (authoritative) + two-way tapestry + not-targetable + PRECISION | 19 | ✅ | `attach.py` + `tapestry` |
| Oath of Moment (+Codex +1 wound; Caanok re-select) | — | ✅ | `_select_oath` + `_mods_for` |

## What remains (honest)
Everything load-bearing for a positional VP sim is now modelled. The remainder is deliberately left:
- **⏸ Deferred (real, low-value or ill-suited to the blob model):** Coherency, Indirect Fire, standalone
  Snap shooting, Hidden / Gone to Ground, Heroic Intervention, terrain-blocks-vehicle-movement.
- **🟡 Approximations (blob limits):** Engagement Range 3" vs 2"; objectives as point+radius vs footprints;
  vertical/true-3D LoS via the `tall` flag; obscuring light/dense split; wound-allocation via the attach model.
- **⚪ N/A:** Hover/Aircraft (no such units in the meta rosters).
- **The dominant remaining ERROR is NOT here** — it's the **combat-model equilibrium**, and it is now
  DIAGNOSED (2026-08-06; `tools/sim_winmode_diag.py`):
  - Every anchor is decided on **VP/scoring, not tabling** (tabling 0–22%). `combat.resolve_attacks`
    matches mathhammer — the **dice are correct**.
  - **Overshoot** (BA 84/50, Orks 71/40, TSons 64/39): vs SLOW armies Custodes sit and OUTSCORE (BA scores
    only 27 VP). **Undershoot** (aeldari 16/58, tau 24/40, tyranids 18/52): vs FAST/durable armies Custodes
    are OUTSCORED — they survive but can't contest/hold the mid or can't crack the durable centrepiece.
  - A **CONTEST-the-mid movement posture was TESTED and REVERTED** (tau worse, DA overshot, werr 19.8→22.6):
    pushing a slow durable army forward just gets it shot or overshoots the killable ones. The archetype
    profiler also lumps overshoot (orks/TSons) and undershoot (aeldari/tyranids) both as "balanced" — no
    clean feature separates them.
  - **CONCLUSION:** this is NOT a fixable mechanics bug and NOT a tuning pass. The sim faithfully computes a
    simplified game whose (mathhammer-correct) combat equilibrium is more extreme than real 40k, which
    compresses to 40–58% via list variety, player skill, real lists differing from the curated rosters, and
    secondary nuance. No movement/durability knob closes it (confirmed here + across the prior effort). Use
    the sim **mechanistically** (its stated purpose); the win% is DIRECTIONAL for these extremes. A true fix
    is a different combat PARADIGM (research), not calibration. Anchor werr 25.5 (pre-tapestry) → **~19.8**
    across all this work — treat it as a THRASH-GUARD, not a target (see [[wh-40k-project]]).
  - **SETTLED on real games (2026-08-07, `sim-validation-results.md`):** validated against **1125 real BCP
    pairings** (whole meta, army×disposition), the sim's OUTCOME carries **no predictive signal** — AUC 0.47
    (win%) / 0.47 (VP-margin), Pearson −0.08, flat reliability (real ~50% in every sim-win% bin), no
    side/seed bias. The win% is not a prediction and cannot be calibrated into one; more data/games won't
    change that. The sim is a MECHANISTIC prep tool — trust the per-unit damage / board dynamics / tapestry,
    not the %. `runbook.calibration` now labels every runbook NOT-PREDICTIVE with this evidence.
  - (earlier) We ANNOTATE the skew instead of pretending to fix it (`runbook.calibration`). Since the
    sim amplifies edges, the real result regresses toward even and the DIRECTION follows the sim's own
    win% lean — no army classifier needed. Every runbook now prints a **CALIBRATION** line: the sim win%
    plus TRUSTWORTHY (win% 40-60, grindy midrange) / "the sim OVER-rates you" (win% >60, you out-grind a
    slow/killable foe too cleanly) / "the sim UNDER-rates you" (win% <60... <40, you're out-tempo'd or
    can't crack a durable centrepiece — real is better for you). Validated 8/9 vs the Custodes anchors
    (the miss is a borderline 37-vs-40). So the skewed win% is now self-labelling.

## Two axes of completeness (standing law)
- **Rules-stack** (per list): [[tapestry-full-rules-stack]] — Army→…→Weapon/Wargear every time.
- **Core mechanics** (the engine): THIS matrix — re-audit against `core-rules.txt` after a rules update.
