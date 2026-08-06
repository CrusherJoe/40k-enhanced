# Sim ↔ Core Rules Coverage Matrix (11E)

**Version 1.0 · 2026-08-06.** Audit of the `wh.sim` positional engine against the 11E **Core Rules**
(`data/rules/core-rules.txt` + `docs/notes/core-rules-reference.md`, section numbers cited). Status is
against the engine as committed at this date. This is the **mechanics-axis** checklist; its companion is
the **rules-stack** law ([[tapestry-full-rules-stack]]: Army→Detachment(s)→Leader/Support→Enhancements→
Unit→Weapon/Wargear). Legend: ✅ MODELLED · 🟡 PARTIAL · ❌ MISSING · ⚪ N/A for a positional VP sim.

## Turn & phase structure
| Mechanic | § | Status | Engine note |
|---|---|:--:|---|
| 5 battle rounds, both players' turns | 07 | ✅ | `game.play_game` loops rnd 1-5, both armies |
| Phase order Command→Move→Shoot→Charge→Fight | 07 | ✅ | fixed per-turn sequence |
| Score at end of turn / Command | 14 | ✅ | primary + secondaries scored end of each player-turn |

## Command phase (01, 08)
| Mechanic | § | Status | Engine note |
|---|---|:--:|---|
| +1 CP / Command phase | 08 | ✅ | `_command` `me.cp += 1` |
| Leadership roll (2D6 ≥ Ld) | 01.06 | 🟡 | Ld stored; only used ad hoc, no general test |
| **Battle-shock** (below half → Ld test → OC 0, no strats, Desperate Escape) | 01.07 | ❌ | **DEAD CODE** — `_command` always sets `battle_shocked=False`; `eff_oc()` honours the flag but it never fires. High-impact: chipped hordes never stop scoring, no morale variance. |

## Movement phase (03, 09)
| Mechanic | § | Status | Engine note |
|---|---|:--:|---|
| Normal move (M") | 09.05 | ✅ | `_move` steps toward objective at `u.move` |
| Remain Stationary (enables HEAVY) | 09.04 | 🟡 | HEAVY bonus keys off `mods.stationary` but the AI never sets it |
| **Advance** (M + D6; no shoot [except ASSAULT]/charge) | 09.06 | ✅ | `_should_advance` + D6 in `_move`; blocks non-Assault shooting + charge |
| **Fall Back** (only if engaged, end unengaged; no shoot/charge) | 09.07 | ✅ | `_fall_back`; `u.fell_back` gates shooting (game.py:142) + charge (game.py:252) |
| Desperate Escape (battle-shock / forced) | 09.07 | ❌ | no hazard roll on Fall Back |
| **Coherency** (2"/9") | 03.03 | ❌ | blob model has no per-model coherency |
| **Engagement Range = 2"** | 03.04 | 🟡 | sim uses ~3" (+footprint); slightly generous, and the engaged-target line (game.py:155) still uses both radii — **tighten to `3+t.radius`** |
| Strategic Reserves (arrive R2+, edge, not enemy DZ pre-R3, die end R3) | 20 | 🟡 | `_arrive_reserves` staggers R2/R3 but ignores the edge/DZ/destroy-end-R3 constraints |
| **Deep Strike** set up >9", **charge needs 2D6≥9 (~28%)** | 24.09 | 🟡 | reserves drop ~9-15" out; no explicit >9" set-up rule and DS arrivals can still charge freely (should be ~28%) |

## Shooting phase (04, 05, 10)
| Mechanic | § | Status | Engine note |
|---|---|:--:|---|
| Eligibility (not Advanced unless ASSAULT / not Fell Back / not engaged) | 10 | ✅ | `_can_fire` + `_engaged` |
| **[ASSAULT]** shoot after Advancing | 24.04 | ✅ | `_can_fire` |
| **[PISTOL]** engaged unit shoots pistols at the engaging enemy | 10.06 | ✅ | `_can_fire` + engaged-target restriction |
| MONSTER/VEHICLE shoot out of combat at −1 (not pistol-locked) | 10.06 | ❌ | big models are pistol-locked like infantry — **a tar-pit wrongly shuts off a gun-Knight** |
| Geometric line of sight (ruins block) | 10 | ✅ | `Board.has_los` (Liang-Barsky) |
| Model-screening (footprint on the line) | — | ✅ | `_screened` |
| Vertical LoS / true 3D (`tall` flag proxy) | 13 | 🟡 | height faked with a `tall` boolean; no real 3D |
| Snap shooting (only 6s) | 15.09 | ❌ | not modelled |
| Indirect Fire penalties | 10.07 | ❌ | not modelled (no indirect weapons handled) |
| **[HEAVY]** +1 hit if stationary | 24.16 | 🟡 | combat honours it, but AI never Remains Stationary |
| VP-aware target priority | — | ✅ | `_obj_relevance` |

## Attack sequence (04, 05)
| Mechanic | § | Status | Engine note |
|---|---|:--:|---|
| Hit → Wound → Save → Damage, 1 fails / 6 crits | 04-05 | ✅ | `combat.resolve_attacks`; mean matches mathhammer |
| S-vs-T wound chart | 05 | ✅ | `dice.wound_needed` |
| AP worsens save; invuln unmodified; best save | 05 | ✅ | `combat` save calc |
| Feel No Pain (incl. mortals) | 24.12 | ✅ | `apply_damage` per lost wound |
| Regular damage no-spill; **mortals spill** | 05 | ✅ | `apply_damage` |
| **Wound allocation order** (wounded model first; CHARACTER last) | 05 | 🟡 | blob pool has no per-model allocation; character-last is instead handled by the Leader attach model (below) |
| Fast/simultaneous rolling (batch) | 07 | ✅ | vectorised per batch |
| Keyword abilities (LETHAL/SUSTAINED/DEV/ANTI/MELTA/LANCE/HEAVY/TWIN/BLAST/TORRENT/RAPID FIRE/IGNORES COVER) | 24 | ✅ | `combat._kw` consumes all of these |

## Charge phase (11)
| Mechanic | § | Status | Engine note |
|---|---|:--:|---|
| Declare within 12"; charge = 2D6; must reach ER of all targets | 11 | ✅ | `_charge_and_fight` roll + leash |
| Not eligible if Advanced/Fell Back/engaged | 11 | ✅ | charge loop skips those |
| VP-aware charge target | — | ✅ | `_obj_relevance` |
| **Fire Overwatch** (snap; TORRENT auto-hits; excl. TITANIC) | 15.08 | 🟡 | listed in `stratagems` pool but the reactive snap-shot isn't resolved |
| **Heroic Intervention** | 15.11 | 🟡 | listed but not resolved as a reactive move |
| Counter-Offensive (fight first, 2CP) | 15 | ✅ | `stratagems.wants_counter_offensive` |

## Fight phase (12)
| Mechanic | § | Status | Engine note |
|---|---|:--:|---|
| Fights First then alternate | 12, 24.13 | ✅ | `_interleave` + FF group |
| Engagement-perimeter cap (no dogpiling one unit) | — | ✅ | `maxatk` in `_charge_and_fight` |
| **Pile-in 3"** (before attacking) | 12.03 | ❌ | charger snaps to target; no pile-in |
| **Consolidate 3"** (after fighting, toward enemy/objective) | 12.08 | ❌ | not modelled — misses grabbing/holding an objective post-combat |
| Death Visions / fight-on-death | — | ✅ | modelled for BA |

## Terrain & cover (13)
| Mechanic | § | Status | Engine note |
|---|---|:--:|---|
| Benefit of Cover −1 to hit | 13.08 | 🟡 | flat −1 if `near_terrain`; no "not fully visible / intervening terrain" clause, no INFANTRY-clause gating |
| Obscuring / Solid / dense LoS block | 13.10-11 | 🟡 | ruins block LoS as solid rects; no light/dense distinction |
| **Hidden** (dense terrain, didn't shoot → detection range) | 13.09 | ❌ | not modelled |
| **Gone to Ground** (−3" detection) | 13.11 | ❌ | not modelled |
| **[IGNORES COVER]** | 24.18 | ✅ | combat honours it |
| **Plunging Fire** / TOWERING +1 BS ≤12" | 22.05 | ❌ | not modelled |
| Characteristic vs dice-roll modifiers (±1 cap) | app | 🟡 | combat lumps modifiers; the cover-vs-cap edge not separated |
| VEHICLE/MONSTER can't move through dense terrain | 13.06 | ❌ | units move in straight lines through terrain |
| Objectives are **terrain areas** (models within the footprint) | 14.01 | 🟡 | modelled as a point with a 3" control radius, not a footprint area |

## Objectives & scoring (14)
| Mechanic | § | Status | Engine note |
|---|---|:--:|---|
| Level of Control (higher OC total; tie = neither) | 14.02 | ✅ | `Board.control` |
| Battle-shocked OC = 0 | 14.02 | 🟡 | `eff_oc` honours it, but battle-shock never triggers (above) |
| **Secured / sticky** (stays yours until opponent's control exceeds) | 14.03 | ❌ | **control recomputed purely by presence every turn** — grab-and-leave impossible; over-rewards sitting. High scoring impact. |
| Primary VP from real board state, capped 15/rd | 14 | ✅ | `mission.score_turn` |
| Secondary deck (real 13-card Tactical) | 14 | ✅ | `secondaries.py` |

## Core abilities (24)
| Ability | § | Status | Engine note |
|---|---|:--:|---|
| Deep Strike | 24.09 | 🟡 | reserve/flag only (see Movement) |
| **Deadly Demise X** (6 → X mortals in 6" on death) | 24.08 | ❌ | not modelled — big-model explosions absent |
| Feel No Pain | 24.12 | ✅ | combat |
| Fights First | 24.13 | ✅ | fight phase |
| **Lone Operative** (not targetable > 12") | 24.24 | ❌ | not modelled — hurts character survivability modelling |
| **Stealth** (benefit of cover) | 24.33 | ❌ | not modelled (only a unit name) |
| Scouts / Infiltrators (pre-game / 9" deploy) | 24.31/20 | 🟡 | deploy heuristics exist; no explicit pre-game move |
| Super-Heavy Walker (move through; NOT fall-back-and-shoot) | 24.35 | ⚪ | movement-through only; low value for current rosters |
| Hover / Aircraft | 24.17/23 | ❌ | not modelled (no aircraft in the meta rosters) |
| **Mortal wounds** (spill, bypass saves, FNP applies) | 22 | ✅ | `apply_damage` |

## Leaders, Support & Attached Units (19)
| Mechanic | § | Status | Engine note |
|---|---|:--:|---|
| Attach Leader/Support to a legal bodyguard (authoritative from export) | 19, 24.22/34 | ✅ | `attach.py` (parses `Attached unit N` / `Attached as:`) |
| One Leader + one Support per unit | 19 | ✅ | export groups honoured (e.g. Caanok + Ancient on Terminators) |
| Two-way tapestry (leader auras → unit) | 19 | ✅ | `attach` + `tapestry.apply_fx` (Feirros FNP, Biologis Lethal, Eye Precision) |
| Character can't be targeted while attached; **PRECISION** exception | 19.02 | ✅ | embedded → off `on_board`; precision shooters snipe |
| Defence uses **highest T of the bodyguard** | 19.02 | 🟡 | bodyguard's own T used (character shelters); not an explicit max-T recompute |
| Destroyed-trigger only when last model dies | 19 | ✅ | leader detaches on host death |
| **Army rule Oath of Moment** (+ Codex +1 wound; Caanok re-select) | — | ✅ | `_select_oath` + `_mods_for` |
| Bondsman (Knights → Armigers) | — | ⚪ | Knights-specific; not currently wired (Death v2 is Iron Hands) |

## Prioritised fix list (by impact on a positional VP sim)
1. **Secured / sticky objectives (14.03)** — ❌ → changes how *both* sides score; biggest scoring-fidelity gap.
2. **Battle-shock (01.07)** — ❌ dead trigger → below-half hordes stop scoring + morale variance; likely pulls the Ork/TSons overshoot down.
3. **Battle Focus / Fall-back-and-act faction exceptions** — ❌ → the Aeldari −44 (they kite-and-shoot). A rules-stack pull, not a combat change.
4. **Objectives as terrain-area footprints (14.01)** — 🟡 → point+3" vs real footprints changes body/OC tradeoffs.
5. **Pile-in / Consolidate 3" (12.03/08)** — ❌ → post-combat objective grabs; multi-charge geometry.
6. **MONSTER/VEHICLE shoot-out-of-combat at −1 (10.06)** — ❌ → tar-pitting a gun-Knight should cost −1, not its guns.
7. **Deadly Demise (24.08)** + **Deep-strike charge ~28% (24.09)** — ❌/🟡 → big-model explosions; alpha-charge realism.
8. **Lone Operative (24.24)**, **Overwatch/Heroic resolution (15.08/11)** — character survivability + reactive play.
9. Lower value for the current meta: coherency, indirect/snap, plunging fire, hidden/gone-to-ground, hover/aircraft.

## Two axes of completeness (standing law)
- **Rules-stack** (per list): [[tapestry-full-rules-stack]] — pull Army→…→Weapon/Wargear every time.
- **Core mechanics** (the engine): THIS matrix — implement every core rule the sim depends on; re-audit
  against `core-rules.txt` after a rules update. A ❌/🟡 here is a known gap to close in priority order,
  not a silent approximation.
