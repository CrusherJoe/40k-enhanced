# Adaptive-Strategy Layer — Scope

**Status:** proposed (not built). Scoped 2026-07-28 after the fast-matchup calibration investigation
(see the STATUS block in `__init__.py`). This is the design for the *next* effort, for review before build.

---

## 1. Problem & evidence

The AI plays the **same way regardless of opponent**, but the correct strategy is opponent-dependent and
often *opposite*:

- vs a **gunline** (Tau): turtle from LoS cover, hold objectives, don't over-commit, win on VP.
- vs a **mobile/melee** army (Dark Angels, Blood Angels): aggress, hunt the shooters, trade forward.
- vs a **grind brick** (Necrons): stand and grind on the centre.

Proven this session: a single greedy behaviour **cannot** satisfy all three. Phase-2 "hunt-the-shooters"
helped Dark Angels (3→35%) but cratered the anchors (Necrons 49→27, Tau →4) because charging a gunline
just gets you focus-fired. Every greedy tweak that fixed one matchup thrashed others. The fast-matchup
gap (Tau sim ~9% vs real **39.5%**, Aeldari/DA ~3%) is therefore a *policy* problem, not a mechanics one —
combat, missions, rosters, cover, and stratagems are all validated.

## 2. Goal & success criteria

Bring the fast/evasive matchups to their **real listhammer anchors** WITHOUT regressing the calibrated
grindy anchors. Success = **all available real anchors matched within ±5%, and no matchup thrashed** from
its current sensible value. Explicit numeric target: Custodes vs Tau in [34, 45]% while Necrons stays
[42, 52]%, Orks/SM/TSons stay in their current band.

## 3. Non-goals

Not a rules-fidelity upgrade (combat/missions are fine). No new datasheets. Not the caps sim
(`tools/sim_game.py`). Not a per-matchup hardcode — the selector must *generalise* from army profiles so
new opponents work without bespoke tuning.

## 4. Anchors — RESOLVED (listhammer, data/meta/custodes-matchups.json, in gauntlet.ANCHORS)

Real Custodes win% per opponent (sim values as of Phase-1 LoS, 150g):

| opponent | REAL | games | sim | gap | cluster |
|---|---|---|---|---|---|
| Aeldari | 58.3 | 24 | 3 | −55 | tempo (small sample) |
| Drukhari | 54.5 | 22 | 16 | −39 | shooting-durability (small sample) |
| Tyranids | 52.0 | 75 | 20 | −32 | shooting-durability |
| Blood Angels | 50.0 | 56 | 91 | +41 | melee-grind (OVER) |
| Necrons | 47.2 | 91 | 49 | +2 | calibrated ✓ |
| Dark Angels | 40.0 | 40 | 3 | −37 | tempo/kiting |
| Orks | 39.8 | 83 | 44 | +4 | calibrated ✓ |
| T'au | 39.5 | 86 | 9 | −31 | shooting-durability |
| Thousand Sons | 38.6 | 57 | 53 | +14 | melee-grind (OVER) |

**This reframes the whole effort. It's NOT just "fast matchups" — the sim has THREE distinct
miscalibration modes**, proven by testing a shooting-only Custodes FNP against every anchor:
1. **Shooting-durability (under)** — Drukhari/Tyranids/Tau. A shooting-FNP helps *partially* (Tau 9→19,
   Tyranids 20→28) but not to the anchor. Custodes get shot off the board.
2. **Tempo/kiting (under)** — Aeldari/Dark Angels. The shooting-FNP **barely moves them** (both ~8); their
   loss is being out-*scored* by a faster army, not tabled. This is the pure adaptive-strategy target.
3. **Melee-grind (OVER)** — Blood Angels/Thousand Sons. The melee-centric sim over-rewards Custodes.
Any single lever that helps one cluster harms another (the shooting-FNP inflated Orks 44→70, TSons 53→61).
So the fix genuinely needs the per-opponent policy layer below — AND a durability/melee-balance pass, not
just positioning. Caveat: Aeldari/Drukhari anchors are small samples (22–24 games) — wider error bars;
weight the large-sample anchors (Necrons 91, Tau 86, Orks 83, Tyranids 75) more in calibration.

## 5. Architecture

1. **Army profiler** (`profile.py`) — from a built `Army`, compute an archetype vector: avg Move (speed),
   %FLY, shooting-weight (Σ premium AP·D output), melee-weight, effective-durability (Σ wounds × save/inv
   factor), body-count, total OC. Pure function of the roster; cheap; computed once per game.
2. **Archetype classifier** — map the vector → a label in {`gunline`, `alpha-melee`, `mobile-skirmish`,
   `grind-brick`, `horde`, `balanced`}. Thresholded, with soft edges (don't flip on a 1" move delta).
3. **Strategy** — a named parameter set over the AI knobs (see §6), e.g. `TURTLE`, `HUNT`, `GRIND`,
   `SPREAD`, `SCREEN`. Each is ~10 numbers.
4. **Selector** — a small policy table `(my_archetype, opp_archetype) → Strategy`, hand-seeded from 40k
   theory then calibrated. E.g. (durable-elite, gunline)→TURTLE; (durable-elite, mobile)→HUNT;
   (durable-elite, grind)→GRIND. Both armies get a Strategy (symmetric).

## 6. Refactor required — extract the hardcoded knobs

The AI constants are currently inline in `game.py`. A `Strategy` struct on the `Army` must parameterise
(file:line refs current as of this scope):

- **deploy** (`_deploy` ~L226–242): `deploy_depth` (forward push), `aggressive` gate, cover-hug bias.
- **objective ambition** (`_best_objective` ~L325–334): `need` weights (flip 3.0 / claim 2.0 / hold 0.7),
  `centre_bonus` 0.6, `push_enemy_home` 0.5, `own_half_bias` (new, for turtling).
- **movement** (`_move` ~L268–285): `boost`, `los_hold_weight` (how hard to seek cover vs stand on point),
  `hunt_shooters` on/off + which roles.
- **charge/fight** (`_charge_and_fight` ~L150,171,177,184): `charge_range`, `commit_threshold`
  (when to charge vs hold back), `maxatk` engagement cap.
- **reserves** (`_arrive_reserves` ~L354–364): `reserve_split` (alpha vs staggered), `placement`
  (aggressive-near-enemy vs safe-objective).
- **targeting** (`_pick`/`mval` ~L128–131,183): `target_bias` (kill-shooters vs wipe-scorers vs chaff).

Thread `strategy` through the phase functions (they already receive `me`; read `me.strategy`). ~1 day of
careful, test-gated refactor (must be behaviour-neutral when all params = current defaults).

## 7. Calibration harness & method

- **Locked regression suite**: all 10 matchups × ≥1000 games (variance is large — saw 49% vs 57% at 150 vs
  60 games), run per change, diffed against anchors AND the previous run. **Anchor gate**: fail the change
  if any matchup moves >5% from its anchor or >8% from its prior value. This is the guardrail that makes
  iteration safe (Phase 2's thrash would have been caught instantly).
- **Held-out matchups**: tune the selector on ~6 anchors, validate on 2 held-out ones — catches
  overfitting (tuning every matchup to its number proves nothing about generalisation).
- **Method**: seed the selector table from theory → measure vs anchors → adjust *strategy params* (not
  per-matchup hacks) → re-measure. The classifier + strategy generalise; the selector table is the only
  matchup-aware surface, kept tiny.

## 8. Risks

- **Thrash** (proven high) → mitigated by the locked harness + anchor gates. Non-negotiable to build first.
- **Overfitting** to the few anchors → mitigated by held-out matchups + gathering more anchors (§4).
- **Compute**: ≥1000-game × 10-matchup regressions, already ~2× slower since Phase-1 LoS. Each full
  regression is minutes; budget for many. Consider caching / a fast smoke subset for inner-loop iterations.
- **Gamey flips**: soft classification so strategy doesn't oscillate on marginal profile differences.
- **Both-sides-adaptive** could oscillate during calibration (each side reacting to the other). Start with
  the "me" army adaptive + opponents on a fixed sensible default; add opponent-adaptive last.

## 9. Phasing & estimate (gated on §4 anchors)

| Phase | Work | Est. |
|---|---|---|
| P0 | **Gather real anchors** (user-provided listhammer win rates) | blocker |
| P1 | Army profiler + archetype classifier | ~0.5 day |
| P2 | Extract AI knobs → `Strategy` struct + thread through (behaviour-neutral refactor) | ~1 day |
| P3 | Regression harness + anchor gates + smoke subset | ~0.5 day |
| P4 | Seed selector + iterative calibration (the bulk; thrash-prone) | ~2–3 days |
| **Total** | | **~4–5 focused days**, gated on anchors |

## 10. Decisions needed from the user before build

1. **Provide the real per-matchup Custodes win rates** (≥6–8) — the blocker. Without them this overfits.
2. Scope: **"me" (Custodes) adaptive first** with opponents on a sensible fixed default (recommended), or
   all armies adaptive from the start (more oscillation risk)?
3. Accept the slower iteration / compute cost of anchor-gated regressions.

If the anchors aren't readily available, the honest alternative is to **stop here**: keep the shipped
Phase-1 LoS-hold, leave fast matchups documented as directional-only, and use the sim for the grindy
list-vs-list flow + tapestry + optimizer + stratagems, which are all solid.
