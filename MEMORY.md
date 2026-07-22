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
- User owns **the full Knight range + 6 Warglaives + 6 Helverins** (incl. 2 Castellans, 2 Lancers).
  Only Castellan & Valiant have the DOMINUS keyword. Prefers **aggressive / kill-focused** play.
- **User's actual list** (built around Purge the Foe): 2 Castellans, 1 Crusader (rapid-fire battle
  cannon), 1 Lancer, 1 Helverin, 1 Warglaive = 1980/2000. Best home now = **Valourstrike + Dominus →
  Purge the Foe** (Bold Gallantry's [ASSAULT] lets the 8"-move Castellans Advance + fire full salvo).
  Only 20 pts spare, so multiple 25-pt enhancements require cutting a model.
- **List builder** (`build`) validates DP=3, unique-group, disposition legality,
  enhancement ownership/dupes, Rule of Three (max 3/datasheet), points budget;
  costs with escalating pricing.
- Tests: `python3 tests/test_data.py` + `python3 tests/test_army.py` (both green).

## Core rules (11e) — verified against the official PDF (docs/core-rules-reference.md)
- **COVER = −1 to HIT (worsen BS by 1), NOT a save bonus** (11e 13.08; changed from
  10e). Ranged only; [IGNORES COVER] cancels it (incl. Stealth, which in 11e GRANTS
  benefit of cover). Engine fixed (was wrongly +1 save). Cover costs a Castellan
  ~3.6 dmg/salvo.
- **Cover is granted two ways** (13.08): (1) INFANTRY/BEASTS/SWARM *in* a terrain
  area, or (2) ANY model *not fully visible* due to INTERVENING terrain (line of
  sight crosses obscuring terrain). Condition 2 is pervasive — both light AND dense
  terrain areas are "obscuring" (13.10; dense also blocks LoS via Solid 13.11).
- **Standard event board = 16 terrain areas** on 44"×60" (Event Companion manifest:
  4×6x4, 2×10x2.5, 4×6x2, 4×7x1.5, 2×8x11.5-poly), same on every layout. So cover is
  the DEFAULT for most ranged attacks, army-agnostic — ignoring cover is broadly valuable.
- **CORRECTION to an earlier claim:** Dominus's +1-hit-vs-terrain only offsets cover
  when the target is IN a terrain area (condition 1). It does NOT offset cover from
  intervening terrain (condition 2 — the common case vs non-infantry). So Judicant's
  Helm (IGNORES COVER) is NOT made redundant by Dominus. User's real concern = the
  whole non-Knight meta using terrain, not other Knights (which they kill easily).
- **Devastating Wounds** (24.10): crit wound → mortal wounds = Damage (bypass saves).
  All other weapon abilities in the engine verified correct vs the PDF.
- Rules mechanics the tool depends on are documented in docs/core-rules-reference.md;
  full PDF text extractable via pdftotext. gdmissions.app/11th/rules/core-rules is a
  web copy (currency unknown). Event Companion (docs/40k_event_companion.pdf) has the
  terrain LAYOUTS (A/B/C per matchup) as diagrams — not yet ingested.

## Disposition choice for a low-model Knight army (systematic, via practice layer)
- **Action-heavy dispositions are TRAPS for few-model armies:** Reconnaissance
  (~45 VP in mission-actions), Priority Assets (25, action 5/5), Disruption (23)
  all require spending units on Objective Actions each turn + board-spread —
  Knights (6-8 models) can't spare units for that. Avoid.
- **Take and Hold is body-hungry:** 34 VP all from holding many objectives — hard
  for a low-model army to win the objective race (vs hordes).
- **Purge the Foe is the best FIT:** rewards killing (23 VP, Knights' strength)
  + holding (23), only 1/5 missions need an action. Lets Knights convert firepower
  into VP without needing to hold everything. → Valourstrike Lance (2DP).
- Detachment-rule note: Gate Warden's Dauntless Defenders = ignore Hit-ROLL
  modifiers + Sustained Hits 1 on your defensive line. IMPORTANT: this does NOT
  beat cover — cover worsens the BS CHARACTERISTIC, which is a different modifier
  type than a Hit-ROLL modifier (see core-rules-reference.md). So Gate Warden's
  value is the Sustained Hits 1 + ignoring actual hit-roll debuffs, NOT cover
  immunity. Only [IGNORES COVER] (e.g. Judicant's Helm) or breaking LoS beats
  cover. This re-strengthens Valourstrike + Judicant over Gate Warden for the
  cover problem. Valourstrike + Dominus → Purge the Foe remains the pick (better
  disposition fit + mobility). "Best" is partly playstyle + current meta
  (post-cutoff; can't claim tournament certainty).
- **Best list (validated 2000/2000, examples/best-purge-the-foe.yaml):** 2 Castellan
  + Crusader(RFBC) + 3 Helverin + 2 Warglaive + Evanescent Ion. Body-heavy beats the
  6-model version on firepower, OC and board presence.

## Imperial Knights rules facts (affect list logic)
- **Bondsman abilities are granted to ARMIGER models only** (Warglaive/Helverin/
  Moirax), never to the big/Titanic Knights. The big Knights are the SOURCE of a
  Bondsman aura; the Armiger is the RECIPIENT. So e.g. *Lancer's Duty (Bondsman):
  "may charge after Advancing"* buffs a nearby Armiger, NOT the Lancer itself —
  the Lancer does not advance-and-charge.
- **39k.pro rules text is accurate for the FACTION-PACK detachments**, but the
  BASE-CODEX detachments got Rules Updates in the Faction Pack that supersede 39k.
  Gate Warden's Dauntless Defenders was stale (updated to: two chosen OBJECTIVES,
  place a "circular foundation marker" in each, line = closest-part to closest-part
  between markers). Valourstrike's Bold Gallantry already matched (army-wide: any IK
  unit Advances → ALL IK ranged weapons gain [ASSAULT] till end of turn — advance one
  throwaway unit and the whole army can advance-and-shoot). Always check the Faction
  Pack Rules Updates section (docs/ik_faction_pack_v1.1.pdf) for base-Codex detachments.
- **Marker sizes:** core rules define an OBJECTIVE marker as a flat circular 40mm
  marker; measure to/from its closest part. A "circular foundation marker" (Gate
  Warden) has NO explicit size defined anywhere — it inherits the 40mm circular
  convention in practice (confirm with TO for tournaments).
- **Bearer of the Lancer's Sigil** (Valourstrike, 25 pts) = "select one OTHER
  IMPERIAL KNIGHTS model within 12" — re-roll its charge." Bearer excluded, so it
  can't self-target; put it on a model near your charging threat.
- **Bearer of the Judicant's Helm** (Valourstrike, 25) = give one other IK model
  [IGNORES COVER] on its ranged weapons — stacks with Dominus Foebreakers' +1 hit
  vs units in terrain. Strong on a central Castellan feeding the Crusader/other Castellan.
- **Dispositions moved between editions/updates:** user's old list ran Gate Warden
  for Purge the Foe, but Gate Warden now grants Take and Hold; **Purge the Foe now
  comes from Valourstrike Lance.** Always trust current MFM/codex over 39k.

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
