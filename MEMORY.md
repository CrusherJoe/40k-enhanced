# wh — project memory

Persistent context for this project. Kept **in-repo** (versioned with the code)
and deliberately **separate from the shared client-project memory** at
`~/.claude/projects/-opt-projects/memory/`. Read this + `README.md` +
`tools/README.md` when resuming.

## What this is
A Warhammer 40,000 (11th ed.) force-disposition + list tool for the armies
jbeddoe plays (currently **Imperial Knights**), to optimise list building and
guide practice. Python, plain-YAML data, stdlib CLI (`PYTHONPATH=src python3 -m wh …`),
PyYAML the only dep.

## Status (2026-07-22)
- All 8 IK detachments complete: DP, disposition, full rule/enhancements/
  stratagems, enhancement points.
- 22 datasheets with MFM points (1st-copy / each-2nd+-copy escalating, + wargear).
- Full profiles (stats/weapons/abilities/damaged/keywords) for ALL 22 datasheets
  in `data/profiles/imperial-knights.yaml`, generated from the **BSData wh40k-11e**
  catalogue by `tools/gen_profiles.py` (replaced the earlier hand-transcribed 10;
  BSData caught a transcription error -- Moirax conversion beam cannon is A1 not A2).
- 25 primary missions with full VP scoring + Objective Actions (11 have card reverses) in
  `data/missions.yaml`; 18 secondary missions in `data/secondary-missions.yaml`. Transcribed from
  gdmissions.app card PNGs (scoring is in images, not text; asset patterns in tools/README).
- Mathhammer engine (`src/wh/mathhammer.py` + `src/wh/dice.py`): EV attack resolver handling BLAST,
  RAPID FIRE, TORRENT, SUSTAINED/LETHAL HITS, TWIN-LINKED, DEVASTATING WOUNDS, ANTI-*, MELTA, LANCE,
  HEAVY. `wh damage <unit> -T -s --invuln ...`.
- Practice layer (`src/wh/practice.py`): classifies a disposition's 5 missions into skill themes
  (hold-objectives / kill-units / mission-action / deep-strike / board-spread), lists Objective
  Actions to drill + fitting secondaries. `wh practice <disposition>`.
- CLI: `dispositions, matrix, matchup, spread, mission, secondaries, secondary, practice, damage,
  detachments, show, points, profile, plan, build`.
- User owns **2 Knight Castellans** (the DOMINUS anchor for Dominus Foebreakers lists). Only Castellan
  & Valiant have the DOMINUS keyword. Collection otherwise unknown (need to ask to finalize lists).
- **List builder** (`build`) validates DP=3, unique-group, disposition legality,
  enhancement ownership/dupes, Rule of Three (max 3/datasheet), points budget;
  costs with escalating pricing.
- Tests: `python3 tests/test_data.py` + `python3 tests/test_army.py` (both green).

## Non-obvious facts / gotchas
- "Force disposition" is the formal 11e mission mechanic (5 dispositions → 5×5
  asymmetric matrix → each player's mission), NOT an archetype concept.
- **BSData wh40k-11e** (github.com/BSData/wh40k-11e) is the BEST source: per-faction
  BattleScribe catalogue in JSON, all datasheets w/ profiles+points. IK = two files
  (small catalogue + 1.1MB Library). This is the authoritative profiles source; also
  cross-validates MFM points (only Castellan lagged). New Recruit (newrecruit.eu)
  also readable: Nuxt SPA, list API = GET api.newrecruit.eu/api/rpc?m=user_get_list&key=<id>
  (returns full list JSON), but BSData is better for the underlying rules data.
- **Data sources** (full detail in `tools/README.md`):
  - gdmissions.app: matrix in page HTML; disposition/mission cards are PNGs.
  - 39k.pro: whole dataset embedded in its Vite JS bundle (string-aware parser
    in `tools/extract.py`); predates the faction pack; NO usable points.
  - **MFM is authoritative** for points AND for detachment→DP→disposition. Needs
    a browser UA (else 403). Unit/detachment names stream in client-side (not in
    raw SSR HTML) — points ride in `<div hidden id="S:N">` suspense payloads so
    `tools/gen_points.py` works off the raw fetch, but re-scraping the
    detachment→disposition mapping would need a rendered DOM.
  - 39k gave two STALE dispositions (Freeblade→Priority Assets, Gate Warden→
    Take and Hold were corrected); trust MFM / user over 39k.

## TODO
- Practice layer: mission scoring is now IN (data/missions.yaml + secondary-missions.yaml). Next:
  turn a chosen disposition into "what to drill" (analyse the 5 missions it plays into + which
  secondaries synergise). Matched-play VP framework in docs/matched-play.md (Primary 45 / Secondary
  45+20fixed / Battle Ready 10, 15/round cap).
- Codex datasheet profiles: faction-pack 10 are done; the core Codex knights
  (Paladin/Crusader/Castellan/etc.) have points but no profile (not in the pack).
- Mathhammer (expected damage / kill odds) now feasible from the profiles.
