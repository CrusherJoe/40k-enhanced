# Combat-Model Rework — Scope + Findings

**Status:** investigated + partially built 2026-07-28 (autonomous). One real fix shipped (alternating fight
activation). The rest is scoped honestly below, because the investigation proved it is **not a bounded
"rework"** — it is per-faction rules-fidelity work, ongoing and incremental, harness-gated.

---

## 1. What the anchors demanded, and what I found

Goal was to close the anchor gaps (harness.py, gauntlet.ANCHORS) that neither positioning nor the adaptive
layer could. I drove each gap down to its root with isolation tests against the harness. The finding:
**there is no single combat lever.** Each off-anchor matchup is its own fidelity problem.

- **Blood Angels +48 (sim ~99 / real 50).** NOT a durability or fight-order bug. Alternating activation
  didn't move it; and *doubling* BA's melee attacks + full re-rolls still lost 100%. The trace shows BA
  DOES connect its jump alpha (charges 5 units R1, kills 8 Custodes) but gets wiped 18→1 in the mutual
  trade — BA units die in the alternating exchange before their output matters. To reach 50 needs BA's
  real STICKINESS + output modelled: Death Company FNP/-1-damage + not-battle-shockable, Sanguinary Guard
  2+/4++, Red Thirst (+1 to wound in melee, currently a weaker re-roll), Lemartes/Priest buffs. That's BA
  tapestry, per-unit.
- **Aeldari −56 (sim ~2 / real 58).** The wraith wall (T6–T10, 2+ saves, ~86 wounds) out-grinds Custodes
  while shooting them; neither the durability ward nor any strategy moves it. Roster is clean (no inflation
  bug). Needs the Custodes-vs-durable grind + Aeldari Strands-of-Fate/Battle-Focus + objective-tempo
  modelled — Aeldari-specific.
- **Tyranids −34, Tau −28, Drukhari −24, Dark Angels −36** — each a different mix of premium-shooting
  survival, monster durability, and tempo. The AP≤−3 shoot-ward helps the shooting ones a little without
  breaking Orks/Necrons, but nowhere near the anchor.

**Conclusion:** the sim is calibrated where the tapestry is fully modelled and the dynamics are simple
(grindy: Necrons 47, Orks 40). Elsewhere the gap is the *un-modelled rules of that specific matchup* —
army rules, detachment rules, key stratagems, unit special-rules (FNP/resurrection/fight-on-death/+1-wound),
and the game-flow that lets an army apply them (alpha connection, tempo, elite-army objective scoring).
Closing all 9 anchors ≈ modelling all of 40k faithfully. That is a large, ongoing effort — not one rework.

## 2. Shipped this pass

- **Alternating fight activation** (game._charge_and_fight + _interleave): 11e resolves fights by
  ALTERNATING between players (fights-first first, active player first in each group), not the old
  active-player-sweeps-then-defender order. This is a genuine fidelity fix (the sequential order gave the
  charger a false advantage). It didn't move the anchors much (BA is a stickiness problem, not order), and
  it shifted Necrons ~48→43 (within noise of the 47 anchor) — kept because it is correct.

## 3. The real path (incremental, harness-gated — NOT a single build)

Do it one faction at a time, lowest-error-first, each gated by `python -m wh.sim.harness`:

1. **Per-faction tapestry fidelity.** For each off-anchor faction, model its actual durability/output rules
   from the DB (data/bsdata/rules + data/strats). BA first (Death Company FNP + fight-on-death, Sang Guard
   invuln, Red Thirst +1-wound) — the biggest single gap (+48) and a clean, self-contained target. Then
   Tyranids (monster regen/synapse), Aeldari (Fate/Focus + wraith interactions), Tau (guided/markerlight).
2. **Game-flow for army identities.** Deep-strike alpha CONNECTION (BA/Custodes), fast-army TEMPO scoring
   (Aeldari/DA out-score without tabling), and elite-low-model OBJECTIVE scoring (Custodes hold with OC
   while trading) — these are how an army *applies* its tapestry.
3. **Universal fight fidelity.** Fight-on-death / interrupt / consolidate — the grindy details that make
   elite mirrors trade evenly instead of one side sweeping.

## 4. Honest expectations

Grindy anchors stay good. Each faction pass should pull its matchup toward its anchor without thrashing
others (that's what the harness enforces). But the small-sample anchors (Aeldari 24 games, Drukhari 22)
have ±10 error bars — do not expect to "nail" them, and do not overfit to them; weight Necrons(91),
Tau(86), Orks(83), Tyranids(75). The deliverable is steadily lower weighted error, not a perfect scorecard.

## 5. Decision for the user

This is genuinely open-ended fidelity work. Options: (a) fund it incrementally, one faction per session,
harness-gated — I'd start with Blood Angels (biggest, cleanest); (b) accept the current state — grindy +
tooling solid, rest directional — and stop. Either is defensible; (b) is honest about the effort/return.
