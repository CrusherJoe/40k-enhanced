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
- **The dominant remaining ERROR is NOT here** — it's the **combat-model over-strength of Custodes elite
  melee** (BA/Orks/TSons overshoot; aeldari −41). That is a research-level combat rework, separate from the
  core-mechanic coverage this matrix tracks. Anchor werr moved 25.5 (pre-tapestry) → ~20-21 across this work;
  rules-correct changes that reduce a loser's output can raise it against that single-army, combat-biased
  baseline without being wrong (see [[wh-40k-project]]).

## Two axes of completeness (standing law)
- **Rules-stack** (per list): [[tapestry-full-rules-stack]] — Army→…→Weapon/Wargear every time.
- **Core mechanics** (the engine): THIS matrix — re-audit against `core-rules.txt` after a rules update.
