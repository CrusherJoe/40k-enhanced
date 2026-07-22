# tools — 39k.pro data extractor

How the base-Codex detachment rules (and the DP + disposition mapping) were
scraped from **39k.pro**, whose entire dataset ships embedded in its Vite JS
bundle.

## Reproduce

```bash
# 1. Download the app bundle (path may change when the site redeploys; grab it
#    from the <script src> in https://39k.pro page source).
curl -sL https://39k.pro/assets/index-2fa34fec.js -o app.js

# 2. Run the extractor from this dir (needs PyYAML; app.js must be alongside).
python3 gen_base.py          # -> base_detachments.yaml
```

`gen_base.py` produces the four base detachments (Questoris Companions, Gate
Warden Lance, Valourstrike Lance, Spearhead-at-Arms) as YAML; that output was
indented and spliced into `../data/detachments/imperial-knights.yaml`.

## How the bundle is structured

Minified JS object-literal "tables" (not JSON: unquoted keys, `!0/!1` booleans,
`'`/`"` strings, and rules text containing `[BRACKETS]`/`{braces}`). Key tables:

- `detachment` — `id`, `publicationId` (faction; IK = `pzYb5fE0EgU`),
  `detachmentPointsCost`, `localisations.en.name`
- `force_disposition` — disposition `id` → name
- `detachment_force_disposition` — `detachmentId` → `forceDispositionId`
- `detachment_rule` — `detachmentId` → rule name (body is elsewhere ↓)
- `rule_container_component` — `detachmentRuleId` → `en.textContent`
  (`type:"text"` = rules, `type:"loreAccordion"` = flavour)
- `enhancement` — `detachmentId`, `basePointsCost`, `en.{name,lore,rules}`
- `stratagem` — `detachmentId`, `cpCost`, `key` (phase), `category`,
  `en.{name,lore,whenRules,targetRules,effectRules,restrictionRules}`

`extract.py` is a **string-aware** bracket matcher (respects JS string literals
so `[SUSTAINED HITS 1]` inside a rule doesn't break brace counting), plus helpers
to pull a table array, split records, and read scalar / `en`-localisation fields.

Note: the 39k.pro snapshot predates the IK Faction Pack v1.1, so it lacks
Dominus Foebreakers and had two stale dispositions (corrected from the user's
authoritative list). Treat it as a convenient source, not ground truth. 39k also
carries NO current model points (its `datasheet_points_step` holds only
increment rows, not base costs) — points come from the MFM instead.

## gen_points.py — MFM datasheet points

```bash
# Fetch the MFM faction page (needs a browser User-Agent or it 403s).
curl -sL -A "Mozilla/5.0" https://mfm.warhammer-community.com/en/imperial-knights -o mfm.html
python3 gen_points.py         # -> datasheets.yaml
```

The MFM page is React streaming SSR: unit names and points arrive as
`<div hidden id="S:N">` suspense payloads in hex order — a NAME slot, then one
or two UNIT-COST slots (1st-copy cost, then each-2nd+-copy cost), then optional
WARGEAR-OPTION cost slots (`<span>per <name></span><template id="P:N">` maps the
wargear name to slot S:N). A `▲ (+N)` prefix flags a *recent points increase*,
not a cost to add — it is stripped. Output was written to
`../data/datasheets/imperial-knights.yaml`. Enhancement points also come from
the MFM (and matched 39k's values, cross-checking both sources).

## Mission cards (primary + secondary) — gdmissions.app card PNGs

The 25 primary + 18 secondary mission scoring rules were transcribed from the
gdmissions.app Chapter Approved Mission Deck **card images** (there is no text
API — the scoring lives in the PNGs, so this step needs visual reading; OCR gets
the wording but not the stylised VP numbers).

Asset URL patterns:
- Primary front:  `/assets/11th/primary-missions/<disposition>/<mission>.png`
- Primary reverse (Objective Action, 11 of 25): `<mission>-back.png`
- Secondary:      `/assets/11th/secondary-missions/defender/<slug>.png`
  (attacker and defender variants are identical — one is enough)

Slugs are listed on `https://gdmissions.app/11th/{primary,secondary}-missions`.
Output lives in `../data/missions.yaml` and `../data/secondary-missions.yaml`;
each block's scoring cross-checks against `../data/matrix.yaml`.

## gen_profiles.py — BSData datasheet profiles (authoritative)

All 22 IK datasheet profiles come from the **BSData wh40k-11e** community
catalogue (https://github.com/BSData/wh40k-11e), which is far better than
transcribing PDFs — it's structured, complete (incl. the core Codex knights),
and self-validating.

```bash
# Download the IK library JSON (gitignored; ~1.1 MB).
curl -sL "https://raw.githubusercontent.com/BSData/wh40k-11e/main/Imperium%20-%20Imperial%20Knights%20-%20Library.json" -o ik_lib.json
python3 gen_profiles.py        # -> profiles_bsdata.yaml, spliced to ../data/profiles/imperial-knights.yaml
```

BattleScribe/BSData structure the resolver handles:
- datasheet = a `model`/`unit` sharedSelectionEntry; the `unit` wrapper
  (Canis Rex) holds its stat line on nested `model` sub-entries (knight + pilot).
- stat line = the "Unit" typeName profile (M/T/Sv/W/LD/OC/InSv; `*` = invuln
  vs ranged only).
- weapons = "Ranged/Melee Weapons" profiles reached by walking the wargear tree
  (selectionEntries + selectionEntryGroups + entryLinks → shared entries/groups).
- abilities = "Abilities" profiles + `infoGroups` (Bondsman Duties) + rule
  infoLinks. Only `Deadly Demise`/`Lone Operative` (core) and `Code Chivalric`/
  `Super-Heavy Walker` (faction) are kept; other rule links are weapon keywords.
  The Deadly Demise VALUE is an `append` name-modifier on the infoLink.
- damaged = a "Damaged: N-M …" profile infoLink; keywords = categoryLinks;
  points = costs.pts (cross-checked vs MFM — all match except a lagging
  Castellan; MFM stays the points source of truth).
