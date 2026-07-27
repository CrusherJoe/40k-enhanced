# Rules text (11th edition)

Committed plain-text conversions of the official GW PDFs (the PDFs themselves are
gitignored under `docs/*.pdf` — large; re-download from warhammer-community.com).
These are the AUTHORITATIVE rules reference for analysis.

- `core-rules.txt` — Warhammer 40,000 Core Rules (11th ed).
- `event-companion.txt` — Warhammer Event Companion (matched-play/tournament rules +
  deployment maps). Machine-derived from the mission/deployment/map data lives in
  `data/missions.yaml`, `data/secondary-missions.yaml`, `data/matrix.yaml`,
  `data/layouts/`. Faction detachment rules/stratagems/enhancements: `data/faction-packs/`.

Note: 39k.pro (stratagems) and gdmissions.app (missions/maps) are community tools that
DIGEST these same official sources — their derived data is already captured in the yaml
above + faction-packs, so we source from the official PDFs, not their Firebase backends.
