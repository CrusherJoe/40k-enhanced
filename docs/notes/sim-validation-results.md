# Sim validation vs real tournament results (11E)

**2026-08-07.** The definitive test of whether the `wh.sim` engine's game OUTCOME (win% / VP margin)
predicts real games — measured against real BCP results, not one army's aggregate anchors.

## Method
`tools/bcp_validate.py`. Every DECIDED, fully-simmable pairing from the pulled events is a real game with
a known winner + score, using **both players' real decklists AND real Force Dispositions** (army×disposition
vs army×disposition, asymmetric via `matrix.yaml`). For each, sim p1(side A) vs p2(side B) and compare the
sim's prediction to the actual result. **AUC is the key metric** (rank-based: does the sim rank real winners
above losers?) — immune to any calibration offset. 0.5 = no signal, >0.5 predictive, <0.5 anti-predictive.

## Result — 1125 real pairings, LSO 2026 + NM2026 + Denver Aug '26 (@30 games each)
```
directional accuracy (win%>50 == real winner): 49%   (coin-flip 50)
AUC  sim win%      -> real winner : 0.472
AUC  sim VP-margin -> real winner : 0.470
Pearson(sim VP-margin, real VP-margin): -0.08
bias: mean predicted p1-win% 53  vs  real p1-win-rate 51%   (no side/seed bias)
reliability (sim win% bin -> real win%): FLAT
   0-9 -> 56% | 10-19 -> 49 | 20-29 -> 48 | 30-39 -> 52 | 40-49 -> 47
   50-59 -> 57 | 60-69 -> 61 | 70-79 -> 44 | 80-89 -> 50 | 90-99 -> 47
```

## Conclusion
**The sim's game outcome carries NO predictive signal** for real 40k. AUC ≈ 0.47 (indistinguishable from
0.5), Pearson ≈ 0, and real win% is ~50% in *every* sim-win% bin — a sim "90%+ favourite" wins ~47% of real
games. It is **not a bug**: the predicted-vs-real p1-win-rate (53 vs 51) shows no side/seed bias, and BCP
mirrors are ~symmetric. It is **not fixable by more data or more games** — a signal that isn't there over
1125 games won't appear with more; and it can't be calibrated into a predictor (nothing to calibrate).

This is the strongest possible statement of the combat-model wall (see `sim-core-rules-coverage.md`): the
sim faithfully computes a *simplified* game whose outcome diverges from real 40k, where the result is
dominated by list variety, player skill, deployment/first-turn, terrain, and secondary play the sim can't
model. Real 40k is close to a coin-flip across the meta, and the sim's confident %s don't track it.

## What IS valid (use these)
The sim's **mechanistic** outputs — per-unit damage dealt/taken (matches `wh.mathhammer`), what you can/can't
remove, board-control DYNAMICS, the assembled tapestry (army→detachment→leader→enhancements→unit→weapon) —
are correct and useful for PREP. The win%/verdict is **not** a prediction (`runbook.calibration` now says so
on every runbook).

## Does the BCP subscription help?
Not for finding an outcome signal — that's settled (absent). More events would help for OTHER things: more
opponent decklists for mechanistic matchup prep, broader meta/archetype coverage, list-building trends. If a
*different* modelling paradigm is ever built, `bcp_validate.py` + more events is the ready-made test rig.
