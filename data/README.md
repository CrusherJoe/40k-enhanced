# `data/` — the local authoritative database

Everything the tools need for analysis, list-building, and simulation lives here as
committed, versioned data. **A fresh machine (or a new Claude Code account) just needs
`git clone` — no external lookups to get started.** Raw external sources are gitignored
(`data/_src/`, `data/mfm/raw/`) and re-fetchable; only normalized data is committed.

## ★ Golden rules
1. **Analysis READS from `data/`. Never hand-copy points/profiles into a script.** (The
   root cause of past point errors was hand-typing values into `tools/lso_data.py`.)
2. **POINTS = MFM only** (`data/mfm/`). BSData points are stale — never cost a list from them.
3. **PROFILES/weapons/abilities = BSData** (`data/bsdata/`).
4. **listhammer meta = lists dated ON/AFTER the current dataslate** (2026‑07‑23; the 7/22
   Dataslate reset points+rules). Filter `startDate >= cutoff`.

## What's here

| Path | Contents | Source | Built by | Refresh |
|---|---|---|---|---|
| `mfm/<slug>.json` | **points** (unit incl. escalating per‑model + wargear), **enhancements**, **detachments (DP)** | mfm.warhammer-community.com/en/`<slug>` | `tools/mfm_db.py` | `python3 tools/mfm_db.py <slug>` |
| `bsdata/<slug>.json` | **datasheets**: stats, invuln, ranged/melee weapon profiles (+keywords), abilities, damaged, keywords | BSData/wh40k-11e | `tools/bsdata_db.py` | `git -C data/_src/wh40k-11e pull && python3 tools/bsdata_db.py --all` |
| `datasheets/<faction>.yaml` | curated MFM points consumed by the `wh` CLI (`src/wh`) | MFM | `tools/gen_points.py` | (regenerate from MFM) |
| `detachments/<faction>.yaml` | detachment rules/enhancements/stratagems | faction packs | hand + tools | manual |
| `dispositions.yaml`, `missions.yaml`, `secondary-missions.yaml`, `matrix.yaml` | mission system + disposition↔mission matrix | rules / 39k.pro / gdmissions.app | hand | manual (TODO: builder) |
| `layouts/<disposition>.yaml` | deployment maps / layouts | rules | hand | manual (TODO: builder) |
| `allies/agents.yaml` | Agents of the Imperium (Navigator = 75, etc.) | MFM | hand | (fold into mfm/) |
| `listhammer_archive.json` + `listhammer_api_dumps/` | tournament top-lists | listhammer.info (reference-only) | `tools/listhammer_pull.py` | accumulator cron + `--from-json` |
| `_src/` (gitignored) | raw external clones (BSData) + `mfm/raw/` fetch caches | — | — | re-fetchable |

## Refresh after a Dataslate drops
```
python3 tools/refresh.py            # pulls BSData + rebuilds bsdata/ + mfm/ for all factions
```
Then re-verify anything a dataslate touched (points, detachment DP, invulns) and regenerate
the reports (`tools/gen_lso_*.py`). Bump the listhammer cutoff date in the analysis + this file.

## Coverage (2026‑07‑26)
- `bsdata/`: 34 factions, ~1,216 datasheets. (SM chapters hold only chapter-specific units —
  load `space-marines.json` for common Marine datasheets.)
- `mfm/`: 27 factions.

## Portability
Commit + push includes all normalized data + the tools that rebuild it. On a new box:
`git clone` the repo, `git clone --depth 1 https://github.com/BSData/wh40k-11e data/_src/wh40k-11e`,
run `tools/refresh.py`, and read `MEMORY.md` + this file. That's the whole handoff.
