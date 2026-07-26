# Source references

The large PDFs are gitignored to keep the repo lean. Re-download as needed:

- **Warhammer 40,000 Core Rules** (11th ed.)
  → `docs/40k_core_rules.pdf`
  https://assets.warhammer-community.com/eng_01-06_warhammer40k_new40k_core_rules-was6fbu1ix-hfewhmxyiy.pdf

- **Imperial Knights Faction Pack v1.1** (legal from 22 Jul 2026)
  → `docs/ik_faction_pack_v1.1.pdf`
  https://assets.warhammer-community.com/eng_22-07_warhammer_40,000_faction_pack_imperia_knights-0at8boavnz-vxe5grd7zi.pdf

- **Warhammer Event Companion** (22 Jul 2026) — matched-play/tournament rules:
  mission sequence, VP framework, terrain layouts, FAQ. Confirms the disposition
  system but does NOT contain per-mission scoring (see `docs/matched-play.md`).
  → `docs/40k_event_companion.pdf`
  https://assets.warhammer-community.com/eng_22-07_warhammer_40,000_event_companion-alyapl19us-b2drgwkji4.pdf

- **Chaos Space Marines Faction Pack** (v2.03, 22 Jul 2026) — opponent faction for
  HeeYaw matchup testing (Huron's Marauders et al.):
  → `docs/chaos_faction_pack.pdf`
  https://assets.warhammer-community.com/eng_22-07_warhammer_40,000_faction_pack_chaos_space_marines-att4ehoaum-8mmiunajyf.pdf
  - CSM points: https://mfm.warhammer-community.com/en/chaos-space-marines (JS-rendered;
    fall back to BSData rev-4 costs — synced from the same GW source).
  - CSM datasheets/weapons/points/detachments: BSData `Chaos - Chaos Space Marines.json`
    (github.com/BSData/wh40k-11e — single file, no separate Library; carries costs).

- **Tyranids Faction Pack** (22 Jul 2026) — opponent faction (HeeYaw Game 4):
  → `docs/tyranids_faction_pack.pdf`
  https://assets.warhammer-community.com/eng_22-07_warhammer_40000_faction_pack_tyranids-rz5ydhbpyi-a1yqdtcqcm.pdf
  - Tyranid points: https://mfm.warhammer-community.com/en/tyranids (JS-rendered; use BSData costs).
  - Tyranid datasheets/weapons/points: BSData `Tyranids.json`; **detachment rules live in the
    separate `Library - Tyranids.json`** (Invasion Fleet, Crusher Stampede, Unending Swarm,
    Assimilation Swarm, Synaptic Nexus, Vanguard Onslaught; + Shadow in the Warp, Synapse).
    (github.com/BSData/wh40k-11e)

## Live data sources (see `tools/`)

- **Dispositions + Force Disposition Matrix:** https://gdmissions.app/11th/matrix
- **Detachment DP + rules/enhancements/stratagems:** 39k.pro embedded dataset
  (faction `pzYb5fE0EgU`). NOTE: predates the faction pack; stale on a couple of
  dispositions; carries no current points.
- **Model + enhancement points, and the authoritative detachment→DP→disposition
  mapping:** Munitorum Field Manual — https://mfm.warhammer-community.com/en/imperial-knights
