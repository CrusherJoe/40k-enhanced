# BCP event data — army lists from BestCoastPairings

Local snapshot of a BestCoastPairings event's full roster + army lists, for whole-field
analysis. Everything here is derived from BCP's public roster API plus the authenticated
armylist endpoint (one logged-in bearer token; the roster itself is public).

## What's here (event: Lone Star Open 2026 — 40k Champs, `VAiZ9vjF61Rk`)

| path | what |
|---|---|
| `lso2026.json` | roster: 330 players — name, faction, detachment(disposition), team, `listUrl` |
| `lso2026-lists/*.txt` | one decklist per player (`<player>_<faction>_<listId>.txt`), header + army text |
| `lso2026-lists/_raw/*.json` | the full raw `/armylists/<id>` records (source of truth for the DB) |
| `lso2026.sqlite` | **the queryable DB** — built from `_raw/` (gitignored; rebuild with one command) |
| `../../reports/lso2026-roster.html` | filterable roster page, each name linked to its BCP list |

## Rebuild / refresh

```bash
# 1. roster + decklists (decklists need a fresh bearer token in ../../.env.bcp)
python3 tools/bcp_pull.py VAiZ9vjF61Rk \
    --store data/bcp/lso2026.json \
    --html  reports/lso2026-roster.html \
    --fetch-lists data/bcp/lso2026-lists          # resumable; skips already-saved

# 2. (re)build the SQLite DB from the raw JSONs
python3 tools/bcp_db.py build data/bcp/lso2026-lists/_raw \
    --db data/bcp/lso2026.sqlite --roster data/bcp/lso2026.json
```

Token: log into bestcoastpairings.com, DevTools Console →
`Object.entries(localStorage).filter(([k])=>/accessToken/.test(k)).forEach(([k,v])=>console.log(v))`,
put it in `.env.bcp` as `BCP_TOKEN=<token>`. Tokens expire in ~1h. `.env.bcp` is gitignored.

## DB schema (`lso2026.sqlite`)

- **`lists`** — one row per list: `list_id` (PK), `player`, `user_id`, `faction`
  (specific, e.g. "Imperial Knights"), `detachment` (e.g. "Valourstrike Lance"),
  `disposition` (Take and Hold / Priority Assets / Purge the Foe / Reconnaissance /
  Disruption), `team`, `total_points`, `game_size`, `n_units`, `list_status`, `list_url`,
  `army_text`, `army_html`, `dropped`, `parse_ok`.
- **`units`** — one row per top-level unit: `list_id`, `seq`, `name`, `points`.
- **`enhancements`** — `list_id`, `name`.

Data quality (324 lists with a submitted list): all have `disposition` + `total_points`;
1 missing detachment, 8 with no faction set by the player. **314/324 have parsed `units`**
(`parse_ok=1`); the other 10 use exotic list-builder exports and are text-only
(`parse_ok=0`) — full `army_text` is still stored, so filter `WHERE parse_ok=1` for
unit-level queries. Faction / detachment / disposition / points are populated for those 10
too (from the API + text backfill).

## Query

```bash
python3 tools/bcp_db.py stats                        # faction / detachment / disposition breakdown
python3 tools/bcp_db.py faction "Imperial Knights"   # players of a faction + their lists
python3 tools/bcp_db.py unit "Caladius"              # which lists run a unit (substring)
python3 tools/bcp_db.py show "Joe Beddoe"            # full parsed record + army text
```
Or hit `lso2026.sqlite` directly with SQL for anything ad-hoc.
