# wh — Warhammer 40,000 (11th ed.) force-disposition planner

A tool for the armies I play, to optimise **list building** and guide **what to
practice**. It models the 11th-edition army-building + mission system and helps
answer: *which detachments should I bring, which army disposition should I
commit to, and which missions will that make me play?*

## The 11e model

- An army is **2000 pts** and gets **3 Detachment Points (DP)**.
- **Detachments** cost DP (1/2/3); you fill exactly 3 DP via `3`, `2+1`, or
  `1+1+1` (distinct detachments; some carry a `unique` group that can't repeat).
- Each detachment grants army rules + enhancements **and one of 5 force
  dispositions**: Take and Hold · Purge the Foe · Reconnaissance ·
  Priority Assets · Disruption.
- You choose **one army disposition** from those your detachments unlock.
- At game time, **your disposition × opponent's disposition → each player's
  mission** via the asymmetric 5×5 **Force Disposition Matrix** (25 missions).

## Commands

```bash
export PYTHONPATH=src

python3 -m wh dispositions                 # the 5 dispositions
python3 -m wh matrix [disposition]         # full matrix, or one row
python3 -m wh matchup <you> <opponent>     # both players' missions in a matchup
python3 -m wh spread <disposition>         # your mission spread vs all opponents
python3 -m wh detachments                  # Imperial Knights detachments + status
python3 -m wh show <detachment>            # full rule, enhancements + stratagems
python3 -m wh points [unit]                # datasheet points (MFM), optional filter
python3 -m wh plan                         # legal 3-DP combos + dispositions unlocked
python3 -m wh build <list.yaml>            # validate + cost an army list
```

### Building a list

Write a list as YAML (see `examples/sample-list.yaml`) and validate it:

```bash
python3 -m wh build examples/sample-list.yaml
```

`build` checks 3-DP legality, `unique`-group conflicts, that your disposition is
granted by your detachments, enhancement ownership/duplication, the Rule of Three
(max 3 of any datasheet), and the points budget — costing units with 11e
escalating per-copy pricing (1st copy vs each 2nd+), plus enhancement and wargear
points. It exits non-zero on an illegal list.

Disposition args accept prefixes: `purge`, `take`, `recon`, `priority`, `disr`.

## Data

Hand-authored YAML in `data/`, cross-checked by `tests/`:

- `dispositions.yaml` — the 5 dispositions.
- `matrix.yaml` — the full ordered 5×5 matrix (`cells[you][opp]` = your mission).
- `missions.yaml` — the 25 missions, keyed to their disposition pairing.
- `detachments/imperial-knights.yaml` — IK detachments: DP, disposition, full
  rules/enhancements/stratagems, and enhancement points.
- `datasheets/imperial-knights.yaml` — 22 datasheets with MFM points:
  `points_first` (1st copy), `points_additional` (each 2nd+ copy, 11e escalating
  pricing), and any point-costed `wargear`.

### Sources

- **Core rules:** `docs/40k_core_rules.pdf`
- **IK faction pack v1.1:** `docs/ik_faction_pack_v1.1.pdf` — detachment rules,
  enhancements, stratagems, datasheets.
- **Dispositions + matrix:** <https://gdmissions.app/11th/matrix> (data in page
  HTML; disposition cards are PNGs under `/assets/11th/force-disposition/`).
- **Detachment DP + disposition mapping:** extracted from 39k.pro's embedded
  dataset (Vite bundle `/assets/index-*.js`; tables `force_disposition` and
  `detachment_force_disposition` joined to detachment records).

## Status

All 8 Imperial Knights detachments are complete: DP, disposition, rule,
enhancements and stratagems. The 4 faction-pack detachments were transcribed
from the PDF; the 4 base-Codex detachments (Questoris Companions, Gate Warden
Lance, Valourstrike Lance, Spearhead-at-Arms) were scraped from the 39k.pro
bundle (see `scratchpad` extractor scripts).

## Known gaps / TODO

- **Disposition + mission scoring rules** (`summary` / `objective` = TODO) —
  needed for the practice layer; pull from the gdmissions Missions section.
- **Datasheet profiles** (stats/weapons/abilities) not yet modelled — points are
  in (from the MFM) but the full profiles from the faction pack PDF are not.
- **Practice layer** — disposition/mission scoring rules (see above) to turn a
  chosen disposition into a list of what to drill.

## Tests

```bash
python3 tests/test_data.py
```
