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
