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

- **Adeptus Custodes Faction Pack** (22 Jul 2026) — opponent faction (HeeYaw Game 5):
  → `docs/custodes_faction_pack.pdf`
  https://assets.warhammer-community.com/eng_22-07_warhammer_40,000_faction_pack_adeptus_custodes-9ddgakd3ms-3azheaqd6y.pdf
  - Custodes points: https://mfm.warhammer-community.com/en/adeptus-custodes (JS-rendered; use BSData costs).
  - Custodes datasheets/weapons/points/detachments: BSData `Imperium - Adeptus Custodes.json`
    (github.com/BSData/wh40k-11e — single file, no separate Library; carries costs; detachments incl.
    Shield Host, Auric Champions, Talons of the Emperor, Null Maiden, Solar Spearhead, Lions of the Emperor).

- **Current-meta opponent factions** (from listhammer.info post-Dataslate top-11, sourced 2026-07-26). Each:
  MFM `mfm.warhammer-community.com/en/<slug>` (JS-rendered → use BSData costs); BSData from
  `github.com/BSData/wh40k-11e`; Faction Pack (22 Jul 2026) URLs below. Files live in the session scratchpad.
  - **T'au Empire** — BSData `T'au Empire.json` — FP:
    https://assets.warhammer-community.com/eng_22-07_warhammer_40,000_faction_pack_tau_empire-hdrq4u64wm-xopcvjvqfu.pdf
  - **Emperor's Children** — BSData `Chaos - Emperor's Children.json` — FP:
    https://assets.warhammer-community.com/eng_22-07_warhammer_40,000_faction_pack_emperor_s_children-srspmclqtm-i8ey7hgk2s.pdf
  - **Adeptus Mechanicus** — BSData `Imperium - Adeptus Mechanicus.json` — FP:
    https://assets.warhammer-community.com/eng_22-07_warhammer_40,000_faction_pack_adeptus_mechanicus-d1ubc1apog-mpt3r8xzy4.pdf
  - **Leagues of Votann** — BSData `Leagues of Votann.json` — FP:
    https://assets.warhammer-community.com/eng_22-07_warhammer_40,000_faction_pack_leagues-of-votann-kpfosalfyb-sbqk309w4w.pdf
  - **Drukhari** — BSData `Aeldari - Drukhari.json` (roster stub) + `Aeldari - Aeldari Library.json` (data/costs) — FP:
    https://assets.warhammer-community.com/eng_22-07_warhammer_40,000_faction_pack_drukhari-8cbmbcz0ai-0bz2psrjty.pdf
  - **Chaos Knights** — BSData `Chaos - Chaos Knights.json` (stub) + `Chaos - Chaos Knights Library.json` (data) — FP:
    https://assets.warhammer-community.com/eng_22-07_warhammer_40,000_faction_pack_chaos_knights-mdwarnukhh-irpnxydqyr.pdf

- **Current-meta factions round 2** (from listhammer refresh 2026-07-26; Necrons/DA/Orks dominant, new faces).
  Same pattern: BSData self-served from github.com/BSData/wh40k-11e; FP URLs (22 Jul 2026) below. BA & SW BSData are
  CHAPTER additions that import generic SM datasheets from the base `sm11.json` — need both. Salamanders
  "Forgefather" + Librarius Conclave are base-SM detachments already in `sm11.json`.
  - **Blood Angels** — BSData `Imperium - Blood Angels.json` (units/points) + base SM + FP (detachments: Liberator
    Assault Group, The Angelic Host) — FP:
    https://assets.warhammer-community.com/eng_22-07_warhammer_40,000_faction_pack_blood_angels-l1ttsuicte-4xq8nrzqy1.pdf
  - **Thousand Sons** — BSData `Chaos - Thousand Sons.json` (self-contained; Grand Coven) — FP:
    https://assets.warhammer-community.com/eng_22-07_warhammer_40,000_faction_pack_thousand_sons-h1ysumgym3-kyfwf7cjpt.pdf
  - **Space Wolves** — BSData `Imperium - Space Wolves.json` + base SM + FP (Saga of the Beast, Champions of Fenris) — FP:
    https://assets.warhammer-community.com/eng_22-07_warhammer_40,000_faction_pack_space_wolves-vkg7nwp9ez-ldpwen5t8a.pdf
  - **Grey Knights** — BSData `Imperium - Grey Knights.json` (self-contained; Banishers, Argent Assault) — FP:
    https://assets.warhammer-community.com/eng_22-07_warhammer_40,000_faction_pack_grey_knights-dlzvusufhy-uialb3pko4.pdf
  - Necron **Awakened Dynasty** = a codex detachment already in `necrons11.json` (no new source needed).

## Live data sources (see `tools/`)

- **Dispositions + Force Disposition Matrix:** https://gdmissions.app/11th/matrix
- **Detachment DP + rules/enhancements/stratagems:** 39k.pro embedded dataset
  (faction `pzYb5fE0EgU`). NOTE: predates the faction pack; stale on a couple of
  dispositions; carries no current points.
- **Model + enhancement points, and the authoritative detachment→DP→disposition
  mapping:** Munitorum Field Manual — https://mfm.warhammer-community.com/en/imperial-knights
