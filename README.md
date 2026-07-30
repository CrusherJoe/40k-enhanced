# wh — Warhammer 40,000 (11th ed.) force-disposition planner

A tool for the armies I play, to optimise **list building** and guide **what to
practice**. It models the 11th-edition army-building + mission system and helps
answer: *which detachments should I bring, which army disposition should I
commit to, and which missions will that make me play?*

## Portability — moving to a new box / new Claude account

> **Moving the project to a new machine? → see [`HOW-TO-CHANGE-BOXES-JOE.md`](HOW-TO-CHANGE-BOXES-JOE.md)** —
> the plain-English, step-by-step handoff guide. The section below is the same thing in reference form.

**Everything authoritative is committed to git.** A `git clone` gives you the whole project:
all hand-authored + ingested data (MFM points, BSData profile cuts, stratagems, faction packs,
rules, the listhammer archive, the **LSO 2026 BCP field** — 324 raw list JSONs + roster), the
positional sim (`src/wh/sim`), every tool, and the project's living memory (`MEMORY.md`). Only
**derived** artifacts and **secrets** are gitignored — they rebuild from committed sources or
aren't needed (see below). Nothing important lives only on the old box.

### Fresh-box bootstrap

```bash
# 1. clone
git clone https://github.com/CrusherJoe/40k-enhanced.git wh && cd wh

# 2. deps  (Python + one system package for PDF export)
pip install -r requirements.txt
sudo apt-get install -y libreoffice-calc libreoffice-writer      # provides `soffice` for PDFs

# 3. you are already operational — the committed data drives everything:
export PYTHONPATH=src
python3 tests/test_data.py                                       # data sanity
python3 -m wh.sim.runbook knights custodes --games 30            # sim sanity (hand-built rosters, no DB)

# 4. rebuild the gitignored DERIVED artifacts (one-time, deterministic from committed data):
python3 tools/bcp_db.py build data/bcp/lso2026-lists/_raw --db data/bcp/lso2026.sqlite --roster data/bcp/lso2026.json
python3 tools/bcp_archetypes.py build                            # needs the sqlite from the line above
PYTHONPATH=src python3 tools/bcp_dossier.py death_rnr --min 1     # death_rnr + all the reports (.md/.xlsx/.pdf)
python3 tools/make_fieldguide.py                                 # -> reports/*-fieldguide.html
```

### What's gitignored, and why it's safe

| Ignored | Why it's fine |
|---|---|
| `reports/**` | derived — regenerate with step 4 |
| `data/bcp/*.sqlite`, `*-archetypes.json` | derived from the committed `_raw/` JSONs + `archetype_notes.yaml` |
| `data/_src/wh40k-11e/` (BSData clone) | only needed to **refresh** profiles after a GW dataslate — the built `data/bsdata/*.json` cuts are committed, so the sim runs without it |
| `data/mfm/raw/*.html` | SSR cache — the parsed `data/mfm/*.json` points DB is committed |
| `.env.bcp` | short-lived BCP token; only needed to **re-pull a new event's** lists (this event's are committed). See `data/bcp/README.md` |

### Refresh after a GW dataslate (not needed for the move)

```bash
git clone --depth 1 https://github.com/BSData/wh40k-11e data/_src/wh40k-11e
python3 tools/refresh.py            # re-ingest MFM points + rebuild BSData profile cuts
```

### For a fresh Claude Code session on the new box

Read **`MEMORY.md`** (the project's laws, data-provenance rules, everything learned — incl. the
BCP field pipeline, the `death_rnr` "me" list, the archetype layer) + **`data/README.md`** +
**`data/bcp/README.md`** + **`tools/README.md`**. That's the full operating context. The old
account's `~/.claude` global memory does **not** transfer and isn't needed — `MEMORY.md` is
in-repo and self-contained.

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
python3 -m wh mission <name>               # a primary mission's full VP scoring
python3 -m wh secondaries                  # list the 18 secondary missions
python3 -m wh secondary <name>             # a secondary mission's full scoring
python3 -m wh practice <disposition>       # what the disposition rewards + what to drill
python3 -m wh damage <unit> -T 12 -s 3+ --invuln 5+   # expected weapon damage vs a target
python3 -m wh detachments                  # Imperial Knights detachments + status
python3 -m wh show <detachment>            # full rule, enhancements + stratagems
python3 -m wh points [unit]                # datasheet points (MFM), optional filter
python3 -m wh profile <unit>               # full datasheet: stats, weapons, abilities
python3 -m wh plan                         # legal 3-DP combos + dispositions unlocked
python3 -m wh build <list.yaml>            # validate + cost an army list
```

### Practice layer & mathhammer

`practice <disposition>` takes the five missions that disposition plays into
(one per opponent stance) and classifies their scoring into skill themes — how
many of the five reward objective-holding vs killing vs mission-actions vs board
spread — then lists the Objective Actions to drill and the secondaries that fit.

`damage <unit>` runs an expected-value mathhammer resolver (`src/wh/mathhammer.py`)
over a datasheet's weapons vs a target profile (`-T`/`-s`/`--invuln`/`--models`/
`--half-range`/`--charged` …), handling BLAST, RAPID FIRE, TORRENT, SUSTAINED/
LETHAL HITS, TWIN-LINKED, DEVASTATING WOUNDS, ANTI-*, MELTA, LANCE, HEAVY.

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
- `missions.yaml` — the 25 primary missions with full VP scoring (round-keyed
  blocks, cumulative/or conditions), plus each mission's special rule and
  Objective Action (from the card reverse). From the gdmissions Mission Deck cards.
- `secondary-missions.yaml` — the 18 secondary missions (Fixed + Tactical
  scoring, When-Drawn rules, Objective Actions).
- `detachments/imperial-knights.yaml` — IK detachments: DP, disposition, full
  rules/enhancements/stratagems, and enhancement points.
- `datasheets/imperial-knights.yaml` — 22 datasheets with MFM points:
  `points_first` (1st copy), `points_additional` (each 2nd+ copy, 11e escalating
  pricing), and any point-costed `wargear`.
- `profiles/imperial-knights.yaml` — full datasheet profiles (stat line, ranged
  & melee weapons with A/BS-WS/S/AP/D + abilities, unit abilities, damaged
  bracket, keywords) for **all 22 datasheets**, generated from the BSData
  wh40k-11e catalogue (`tools/gen_profiles.py`).

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

- **Disposition `summary`** fields are still TODO (minor; the missions carry the
  actual scoring now).
- **Practice layer** — disposition/mission scoring rules (see above) to turn a
  chosen disposition into a list of what to drill.
- **Mathhammer** — with full profiles in for all 22 datasheets, expected-damage /
  kill-odds is now feasible (parse the dice-valued A/D fields).

## Tests

```bash
python3 tests/test_data.py
```
