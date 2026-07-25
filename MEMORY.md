# wh — project memory

Persistent context for this project. Kept **in-repo** (versioned with the code)
and deliberately **separate from the shared client-project memory** at
`~/.claude/projects/-opt-projects/memory/`. Read this + `README.md` +
`tools/README.md` when resuming.

## What this is
A Warhammer 40,000 (11th ed.) force-disposition + list tool for the armies
jbeddoe plays (**Imperial Knights** + **Adepta Sororitas**), to optimise list
building and guide practice. Python, plain-YAML data, stdlib CLI
(`PYTHONPATH=src python3 -m wh …`), PyYAML the only dep.

## ⚠⚠ DATA-SOURCING PROTOCOL — 11E ONLY (user law, 2026-07-24). READ FIRST, EVERY SESSION. ⚠⚠
**This game is 11th EDITION. 10E is DEAD. Do not use 10E links, files, or memory — ever.**
1. **FORGET all 10E links + knowledge.** If a fact "feels" remembered, it's 10E-suspect → verify or discard.
   Tainted 10E scratchpad files from earlier (DO NOT USE): sm.json, orks.json, necrons.json, da.json, sal.json,
   the first if.cat/if.json (all from BSData/wh40k-10e). Clean 11e: sm11.json, if11.json (from wh40k-11e).
2. **CORE RULES:** the 11E Core Rules PDF is pulled (scratchpad 40k_core_rules.pdf); the verified digest is
   **docs/core-rules-reference.md**. For ANY ability/keyword/concept you don't have VERIFIED 11E knowledge of,
   look it up there / in the PDF — don't infer. (Slips this session were all inference: C'tan cap, TITANIC-
   Overwatch, Anti-X/Dev-Wounds crit, Knight-Overwatch — all avoidable with a lookup.)
3. **UNITS / MODELS / WEAPONS = github.com/BSData/wh40k-11e** (source of truth). Publishes JSON DIRECTLY
   (no .cat conversion): raw.githubusercontent.com/BSData/wh40k-11e/main/<Faction>.json. Detachment CORE rules
   are often BLANK in BSData (enhancements are present) → get the core rule from the FACTION PACK (rule 4/6).
4. **POINTS = MFM** (mfm.warhammer-community.com/en/<faction-slug>, e.g. /adepta-sororitas). MFM also
   occasionally dictates which SUPPORT/LEADER units can join which BODYGUARD units (ask GW why). ⚠ MFM 403s
   automated fetch → scrape the SSR when it allows (tools/gen_points.py style) or ask the user (rule 6).
   Detachment→DP→disposition mapping also from MFM.
5. **STRATAGEMS + some other data = 39k.pro** — try it when the info isn't in BSData/MFM/faction-pack.
6. **IF YOU LACK SOLID 11E DATA — ASK THE USER.** He'll find + provide it. Never guess to fill a gap.
7. **FACTION PACKS = source of truth ON PAR WITH MFM.** This is where GW publishes UPDATES to armies/
   factions/DETACHMENTS/enhancements/stratagems — the latest info direct from GW. Have one for EVERY army
   we work with. BSData leaves detachment CORE rules blank → the faction pack is the authoritative source
   for detachment rules + enhancements + chapter detachments (e.g. SM pack contains Emperor's Shield /
   Librarius Conclave). Faction packs are VERSIONED (v1.0/1.1/1.2…) — a points/rules update = a new version,
   so CONFIRM the pack is the current version (the Wednesday update may have bumped some).
   - **FACTION-PACK INVENTORY (scratchpad, ALL 7 present, all v1.1 — current per user-provided live URLs):**
     sisters_fp.pdf (Sisters), ik_faction_pack.pdf (Imperial Knights), agents_fp.pdf (Agents), orks_fp.pdf,
     necrons_fp.pdf, **da_fp.pdf (Dark Angels — SEPARATE pack; Deathwing/Ravenwing/Unforgiven)**, and
     **sm_fp.pdf = base Space Marines + SALAMANDERS (Forgefather's Seekers, Firestorm Coordinators) +
     IMPERIAL FISTS (Emperor's Shield) + Librarius Conclave — but NOT Dark Angels** (DA has its own pack).
     + 40k_core_rules.pdf + event_companion.pdf. COMPLETE coverage of the whole meta + both my armies.
     (Chapters with their own detachments = own pack, e.g. DA; SM pack bundles some chapters, e.g. Salamanders/IF.)
   - **MFM per-faction URLs** = mfm.warhammer-community.com/en/<slug> (Sisters=adepta-sororitas, DA=dark-angels;
     dig other slugs from the /en index). NOTE (re-verify sweep): Orks pack hints Boyz "can always come back" —
     confirm the Green Tide return mechanic (affects the Knights-vs-Green-Tide verdict).
8. **MODEL THE FORCE-MULTIPLIERS, not just the statline (user law, 2026-07-24).** When modeling ANY army,
   fully ingest every rule — unit abilities, LEADER/SUPPORT buffs, weapon keywords, enhancements, detachment
   rule, stratagems, discipline/aura choices — that turns a **"zero" unit into a "hero" unit.** A base
   statline lies: judge a unit at its BUFFED ceiling. Canonical example: **Great Value's Sternguard** —
   plain S4 bolt rifles look like anti-infantry chaff, but **Dev Wounds + a Librarian + a Conclave Discipline
   (Divination re-rolls / Pyromancy Sustained) + Wrath-of-Dorn Oath re-rolls** stack them into a volley that
   **ignores my Knights' invuln** = the list's #1 ranged Knight-killer. This buff-stacking is the hard part
   (and the fun) of both list-building AND threat-assessment — always resolve it before you rate a unit.
   **A good list is a TAPESTRY: rule-combinations interwoven throughout to maximize ONE thing** (usually
   damage output or speed). So (a) when BUILDING my lists, don't just sum unit points — look for the threads
   that compound (a delivery piece + a re-roll aura + a Dev/Lethal weapon + a Discipline all pointed at the
   same axis), and (b) when ASSESSING an opponent, find the thread they're weaving and CUT it (kill/deny the
   multiplier, not just the carrier). Rate lists by their combos, not their statlines.
- **TODO:** the earlier META INGEST (SM/Salamanders/Orks/Necrons/DA archetypes in docs/meta/) was 10E-sourced —
  concepts hold, but re-verify STATS (wh40k-11e) + detachment rules (faction packs) against 11E before the GT.

## Analysis principles (user guidance — apply to ALL list/matchup work)
- **HARD COUNTERS ARE A FEATURE OF 40k, NOT A LIST FLAW.** Almost every army has a
  matchup it can't fix by tuning (e.g. **Green Tide hard-counters Knights** — 8-9 elite
  models can't out-body/out-OC 165 disposable ones; Green Tide also grinds down basically
  everyone, so it's a top all-comers list). **Identify the hard counter, quantify it,
  ACCEPT it — do NOT keep engineering to "solve" the unsolvable** (I over-did this with
  Overwatch / Dev-Wounds / "more anti-horde"). Optimise for the FIELD you'll actually
  face, be respectable into the bad matchup, and treat knowing your worst matchup as
  intel (plan around it / hope to dodge it / accept variance), not failure.
- Corollary: don't warp a list to patch one bad matchup at the cost of the 90% you win.
- **VERIFY 11E data every time** (units/rules/points/keyword INTERACTIONS) — don't trust
  edition-memory; **defer to MFM for points.** (See the C'tan −1 Damage and the
  TITANIC-no-Overwatch and Anti-X/Dev-Wounds corrections — all edition-memory slips.)

## Multi-faction support
- Faction-keyed data files: `data/{detachments,datasheets,profiles}/<faction>.yaml`.
  Missions/matrix/mathhammer/tools are edition-wide (shared, faction-agnostic).
- **`--faction`/`-F` flag** (or `$WH_FACTION`) selects the army; registry in
  `data.py FACTIONS` (knights/ik → imperial-knights; sisters/sororitas/sob → adepta-sororitas).
  Default = knights. e.g. `wh --faction sisters plan`.

## Adepta Sororitas (2026-07-23) — meta-derived all-comers list COMPLETE
**STANDING RULE (user, all factions): ALWAYS pull/verify 11E data — units, rules, points,
wargear, EVERYTHING — from the live source every time. Treat anything from edition-memory as
10E-suspect and WRONG until confirmed against 11E (BSData / MFM / faction pack). User has played
since 4th ed and explicitly warned about cross-edition contamination (I fabricated a C'tan "damage
cap" from 10E memory — it's actually −1 Damage). Generalises "defer to MFM for points."**

User owns ALL Sisters models (any build/wargear); "let the analysis decide the best list."
`--faction sisters`. 8 detachments span all 5 dispositions (Hallowed Martyrs 3DP/Priority
Assets, Bringers of Flame 3DP/Purge, Champions of Faith 2/Disruption, Army of Faith 2/T&H,
Penitent Host 2/T&H, Chorus of Condemnation 1/Recon, Sanctified Orators 1/Purge, Sacred
Champions 1/T&H). Rules STACK army-wide.

- **COMBAT FUNDAMENTALS ingested (docs/sisters-mechanics.md) — the 3 things that decide a list:**
  1. **AP IS KING** — melta AP-4 (Melta 2) premium; flamer AP0 bounces off armour. AP-tier table in doc.
  2. **GLASS CANNON — girls die a lot** — core bodies T3 W1 Sv3+ (6++). Durable exceptions:
     Sacresants (4++), Paragons (T7 2+/4++), Vahl/Junith/Celestine, vehicles. Durability table in doc.
  3. **TRANSPORTS + THE SPLIT** — Immolator=6, Rhino=12. Battle Sisters/Dominion 10-squads split 5+5
     (melta half + Superior rides the Immolator); a 5-model all-melta Dominion (4 meltas) fits an Immo.
  Plus: Acts of Faith / Miracle Dice devalued by FAST-ROLLING (commit before a batch roll → best only
  on single high-value rolls; double-AoF over-rated). Leaders/Support/keywords gate detachment buffs.
- **META INGEST (docs/meta/) — 5 factions / 7 boogeyman archetypes, grounded in LIVE BSData**
  (BSData/wh40k-10e `.cat` → JSON via scratchpad `cat2json.py`; MFM blocks WebFetch w/ 403):
  - **SM/Salamanders flamer-brick** — 2× Land Raider (T12 W16 **2+**) + ~20 pyreblasters (Torrent). The
    AP-is-king + "don't try to out-flamer them" lesson. Bringers/mono-flamer LOSES this.
  - **Orks — two poles:** Kult-of-Speed dakka (Kill Rig T10/W16, 18 Deffkoptas, anti-tank rokkits that
    POP my transports) vs **Green Tide** (100 Boyz T5 W1 → FLAMER/Blast/volume; melta wasted).
  - **Necrons — un-killable:** 3× Monolith (T13 W22 2+, melta wounds on **5s**) / 4× C'tan (T11 W16 +
    4++). CAN'T table them → **play the MISSION**; don't over-invest melta chasing the un-killable.
  - **Dark Angels Deathwing brick** — 3× Terminator bricks (2+/4++) but **OC1** → **out-OC them**;
    melta still works on W4 via multi-damage past the 4++. Key: **judge melta by target WOUNDS/model.**
- **STRATEGIC THESIS (holds across all 5): Sisters win the MISSION, not the slugfest.** Balanced
  melta+flamer+blast toolkit on a transport/mobility chassis: out-melta anchors, out-flame hordes,
  out-OC elites, never chase un-killable invuln monsters. Transports = expendable delivery (everyone
  packs anti-tank). Durable ≠ scoring (elite bricks are low-OC).
- **DERIVED BEST LIST v2 — examples/best-sisters-allcomers.yaml, 1985/2000** (mathhammer-revised;
  docs/sisters-battle-plan.md). Champions of Faith (2DP, Disruption) + Sacred Champions (1DP, T&H).
  Chosen over Hallowed Martyrs (win-the-slugfest rule) + Bringers (mono-flamer loses half the field —
  SUPERSEDES old best-sisters-purge). Chassis = **Vahl+3-MM Paragons melta HAMMER**; MM-Retributor
  (Palatine[Triptych]+Imagifier → Lethal Hits + cover-immune + Sv2+/4++); Castigator; **2 Immolators
  w/ IMMOLATION FLAMERS** (not twin-MM); 1 melta + 1 flamer Dominion(10); HB-Retributor; Sacresants(10)
  + Canoness[Sanctified Amulet, anti-DS] + Dogmata[+1 OC]; 2 Battle Sisters(10); Zephyrim + Seraphim.
- **THE BUFF/SOFTENING STACK (this is how Sisters melta actually works — cover=−1 to HIT in 11e):**
  naked melta into cover ~4.6 vs a Land Raider → **~4× multiplier when softened**: (1) **Immolator
  Purge & Cleanse** strips Benefit of Cover army-wide (auto-hits w/ Immolation Flamers = reliable
  trigger — REASON to run flamers not twin-MM); (2) **Castigator Rites of Castigation** = +1 AP
  army-wide vs a marked target; (3) **Vahl** re-roll hits+wounds (her Paragon unit + herself ONLY);
  (4) **Righteous Purpose** +1 BS (Paragons); (5) **Palatine+Triptych** = a unit ignores cover;
  (6) **SUPPORT chars** (1 Leader + 1 Support/unit, 19.01): **Imagifier=unit Sv2+/4++**, Dialogus=an
  Act-of-Faith die becomes a guaranteed 6, Hospitaller=FNP5+, Dogmata=+1 OC. Flamers/Castigator/
  Exorcist have IGNORES COVER natively.
- **MATHHAMMER FINDINGS (wh damage, full hit→wound→save chain):** buffed Vahl+Paragons one-shot a
  Land Raider (17.8 vs 16W); melta was OVER-invested (~45 on one target = 3× overkill) → trimmed 2
  packages into anti-horde flamers (~37 dead Boyz/turn now) + durability (Imagifier). C'tan uncrackable
  even buffed (7.3 of 16W, incl. its VERIFIED −1 Damage — NOT a "cap"; I'd wrongly recalled a 10E-ish
  cap, user corrected) → play the mission. Anchors killable only when softened first — enablers ARE
  the anti-tank. Engine now models −1 Damage (Target.damage_reduction; dice.expected_reduced).
- **MATCHUP BATTLE PLANS (docs/sisters-matchup-plans.md):** per-archetype disposition choice +
  mission + deployment + target priority. Disposition-pick meta-pattern: low-OC-durable (Deathwing)
  → **Take-and-Hold, out-OC**; high-body horde (Green Tide) → **Disruption/Death Trap** (kill blobs
  in terrain, dodge OC race); slow-few (Monoliths) → **Disruption/Outmanoeuvre** (run the map);
  faster-than-me (Ork Kult) → **Take-and-Hold, anchor**; death-farmers (C'tan Purge) → **Disruption,
  feed nothing**; durable gunline (Salamanders) → **Disruption, out-position + score kills**.
- **TOURNAMENT: you LOCK ONE disposition for the whole event (user) — doesn't change per game.**
  **LOCK DISRUPTION** (best vs 4/6 of the field; suits the mobile list). Mission is then set by the
  OPPONENT's disposition: opp Purge→Delaying Action, Recon→Smoke and Mirrors, Disruption→Outmanoeuvre,
  Take-and-Hold→Death Trap. (So the earlier "pick per game" plans are reframed to locked Disruption.)
- **LAYOUTS INGESTED** from the Event Companion (deployment TYPE + notes per matchup, geometry approx,
  like the Knights purge ingest): **data/layouts/disruption.yaml** (my lock — ALL 5 matchups verified
  page-by-page incl. the Disruption-mirror at EC pp.36-38 = diagonal/diagonal/vertical) +
  **take-and-hold.yaml** (secondary, 3/5 read). Deployment type is a property of the MATCHUP PAIR +
  layout letter, verified per page (NOT a by-opponent table); the book puts each disposition's MIRROR
  FIRST in its block. Universal: 6 obj (2 home/2 central-NML/2 expansion), 16 obscuring areas, centre packed.
- **WORD DOCS (python-docx, pull live roster/points + layouts — regenerate after changes):**
  **docs/Sisters-Battle-Plan.docx** (tools/gen_sisters_docx.py) — full plan: list, soften-then-delete
  engine, mathhammer+durability cheat-sheet, LOCK DISRUPTION, deployment layouts, 6 per-archetype plans.
  **docs/Sisters-Quick-Reference.docx** (tools/gen_sisters_qref_docx.py) — printable tabletop card:
  mission-by-opponent table, deploy, per-shooting-phase softening sequence, target priority, per-round, don'ts.
- **DOMINION = 10-MODEL ONLY** (user): exactly 4 take melta/flamer upgrades; deployed via the SPLIT
  (4-melta + Superior half rides an Immolator (cap 6), the other 5 bolter-Doms walk). Battle Sisters
  also split 10→5+5. Base 10-model = 90 (MFM, ▼-10 from 100), +5/meltagun → 110 with 4 meltas.
- **ENGINE FIX — size + tax aware pricing (root-cause of earlier wrong points).** Datasheets carry
  MFM `sizes: {models: points}` (units are **5 or 10 ONLY**) + per-model weapon TAXES (Paragon
  multi-melta +10, Retributor multi-melta +5, Dominion meltagun +5). List entries use `models: N` +
  `wargear: [{name, count}]`; build prices exactly (data.py `Datasheet.size_cost`, army.py). IK legacy
  copy-pricing path UNTOUCHED (regression-checked). **⇒ ALWAYS DEFER TO MFM for points (user rule).**
- Data/sources: 8 detachments, ~44 BSData profiles, datasheets w/ MFM sizes+taxes. MFM adepta-sororitas,
  Faction Pack, BSData Imperium-Adepta-Sororitas + opponent `.cat`s, 39k bundle. Extractors:
  tools/gen_*_sisters.py; opponent cat→JSON converter (scratchpad cat2json.py).

## Knights META RE-VISIT (2026-07-24) — re-analysed vs the Sisters-ingested meta
- **Bidirectional mathhammer vs the real boogeyman lists** (not abstract disposition theory).
  KEY FINDING: **anti-tank is REDUNDANT on every Knight build** (all >1.7× a Land Raider; Knights
  even table Monoliths via S18 Volcano / S24 harpoon — the thing Sisters couldn't). The axes that
  actually decide games vs this meta are **ANTI-HORDE + DURABILITY** → the "classic" twin-Castellan
  gunline is the WEAKEST meta pick (least anti-horde; 2 Volcanos are the WORST guns into a 4++ C'tan).
- **New anti-horde big Knights discovered** (from the collection): **Knight Valiant** (DOMINUS!
  Conflagration torrent flamer + S24 AP-6 D10 Thundercoil harpoon) and **Knight Warden** (Avenger +
  Heavy Flamer). **Lancer's 4++ full invuln = premium vs the AP-4-saturated meta** (melee AND ranged);
  Blessed Plate (T13) drops S12 death-ray/lascannon damage ~⅓. Judge big guns by target WOUNDS/model
  (Volcano into W1/W4 = overkill waste → use Avenger/sweeps on multi-model units).
- **3-LIST SLATE (examples/knights-{A,B,C}-*.yaml, all LOCK Purge the Foe):**
  A Lancer-Aggressive (Castellan T13 + Cerastus Lancer 4++/M14 + Crusader + Armigers; AT36/horde23;
  aggressive+mobile+durable, 1965/2000); B Twin-Castellan Gunline (classic; AT35/horde17; weakest vs
  hordes+C'tan); C Horde-Hardened (Valiant + Warden + Crusader + 3 Warglaive screens; AT27/**horde32**;
  the Green-Tide + invuln-spam answer, 1990/2000). **C = meta-robust pick, A = aggressive pick.**
- **ALLIES NOW VALIDATE** (was an unvalidated 75-pt hole): data.allies() loads agents.yaml (ally_type
  from Character keyword); build() `allies:` block costs them + enforces the Agents allowance (2 Char +
  2 Retinue + 1 wildcard) + rejects enhancements on allies; prints "(ally)". A/C include a validated
  Navigator. **This is the general ally mechanism** — reusable for any Imperium ally.
- **DOCS:** docs/knights-matchup-plans.md (locked Purge, mission-by-opponent, per-archetype, C-vs-A) +
  **Knights-C-Battle-Plan.docx** + **Knights-A-Battle-Plan.docx** (tools/gen_knights_docx.py, pulls live
  roster+allies+Purge layouts). Purge lock re-confirmed vs the meta (Knights can't play the action game).
- **STRESS-TEST (docs/knights-C-vs-greentide-stresstest.md):** vs ~100 Boyz C wins ~54-34 but it's a
  disciplined GRIND, swinging on (1) first turn, (2) Armiger screen discipline, (3) killing Ghaz R2 with
  the harpoon, (4) Fall-Back-and-shoot. **⚠ BUT vs the MAX horde ("The Greenback": ~165 bodies — 120 Boyz
  + 22 Zodgrod-Gretchin[Scouts 9"+1 Hit] + Stormboyz + Kommandos[Snikrot backfield-raid] + 3 Painboys
  FNP) the ~54-34 does NOT hold** — C clears only ~135/157 chaff over 5 turns, the OC race (240+ vs ~65)
  is unwinnable, and it becomes **~coin-flip / slight-Ork-favour**. C is the best Knight answer but NO
  list tweak solves it: 8-9 Knights can't clear+out-hold 165 bodies. **The horde is the Knights' worst
  matchup; a MAXED horde is a bad matchup, full stop.** Two key rules: **Super-Heavy Walker** (big Knights
  Fall Back + still shoot → horde CAN'T tarpit them) and **⚠ TITANIC units CANNOT Fire Overwatch (15.08)**
  — so ALL big Knights get NO auto-hit flamer on the charge (unlike non-TITANIC Sisters). Validates C as
  the list; edge is in the PLAN not the roster. (I'd wrongly credited Knight Overwatch — user corrected;
  rule now in docs/core-rules-reference.md. Reinforces: VERIFY 11E rules, don't trust memory.)
- **EXAMPLE-LIST COMPARISON (docs/knights-list-comparison.md):** two user tournament lists vs the slate.
  EX1 Big-Five (5 big Knights, NO Armigers) = strong firepower but only 5 bodies → the classic Knight
  board-control trap. EX2 "Poon Table" (2 Valiant harpoons + 6 shieldbreaker missiles) = ANTI-TITANIC
  specialist (mirror + Monoliths). My C = best anti-horde + bodies (take-all-comers).
- **⚠ DEV WOUNDS / ANTI-X CORRECTION (user catch):** Devastating Wounds fire on a CRITICAL WOUND =
  **unmodified 6 (16.7%)**; **[ANTI-X N+] lowers the crit threshold to N+ ONLY vs a target with keyword X.**
  Verified: **Monolith IS Titanic, C'tan is NOT (Monster)** → shieldbreakers' [ANTI-TITANIC 4+] does
  NOTHING vs C'tan (Dev on 6 only → ~1.9 dmg from 2 SBs). So I was WRONG that shieldbreakers/Dev-Wounds
  are anti-C'tan tech (retracted "add SBs to C"); they're **anti-TITANIC** (enemy Knights + Monoliths).
  **C'tan = play-the-mission for EVERY Knight list** (no one out-guns 4× 16W 4++/−1Dmg Monsters).
  Rule pinned in docs/core-rules-reference.md (Dev Wounds row). Lesson: verify keyword interactions, not just weapon lines.

- **ALLY TECH — Immolator "Purge & Cleanse" cover-strip for KNIGHTS (CONFIRMED LEGAL, user-vetted, IMPLEMENTED):**
  the allies "Sisters of Battle Squad" has the **REQUISITIONED** keyword (≤2 Requisitioned allowed); its
  **Immolator is a Dedicated Transport = FREE** (points count, but does NOT count vs the Requisitioned cap).
  BS special/heavy weapons (meltagun + multi-melta) are FREE → package = **100 + 110 = 210 pts**. The Immo
  keeps Purge & Cleanse (army-wide strip Benefit of Cover on a hit unit). VALUE: cover=−1 hit + Knight BS3+
  → **+33% to the battery's focus-fire** (+7-9 dmg on a covered LR/Monolith/Gorkanaut) + 20 OC of board
  bodies (the Knight low-model weakness) + a melta half + expendable hull. Range ~18-24" → deploy the Immo
  FORWARD to de-cover the MID-BOARD focus target (not back with the Navigator). Army-wide strip makes the
  single-model **Judicant's Helm redundant** → drop it to help pay. IMPLEMENTED: agents.yaml has
  BS(requisitioned)+Immolator(transport); build() caps = ≤2 each of char/retinue/requisitioned, transports
  free; sample **examples/knights-A-coverstrip.yaml** (1985/2000). ≥1 package is worth it for a shooting Knight list.

- **HOME OBJECTIVE under a PURGE lock (verified from missions.yaml) + tournament framing:**
  BOTH players LOCK their disposition for the WHOLE EVENT (opponent does NOT pick at the table — they
  registered their one disposition pre-event, same as you). You build ONE Purge list for a FIELD of
  fixed-disposition opponents. FINDING: holding YOUR home scores YOU **nothing** in every Purge mission
  ("excluding your home objective" throughout) — it's PURELY denial. But the opponent scores off your
  home in **4 of 5 matchups**: T&H/Immovable Object (5 VP/obj, recurring), Purge/Meatgrinder (4 + 5
  "opponent's home"), Recon/Triangulation (4), Priority/Vital Link (4 + **10** "opponent's home");
  ONLY Disruption/Delaying Action rewards it 0. ⇒ Home = a high-value DENIAL battleground (4-10 VP to
  them). Hold it with the forced-split **BS OC10 half** (body) + the **Navigator 12" anti-DS dome**
  (stops the Deep-Strike play that flips an OC10 home). Keep the Navigator in a DS-heavy / home-scoring
  FIELD (the current meta); cut it only for a known Disruption-heavy or DS-light field. (I'd sloppily
  said the opponent "chooses at the table" — WRONG, both locked for the event; corrected.)

- **LSO PRACTICE — Knights vs friend's "Great Value" (Imperial Fists, Emperor's Shield + Librarius
  Conclave, 1985):** counter list `examples/knights-vs-greatvalue.yaml` + plan `docs/knights-vs-greatvalue-plan.md`
  (Valourstrike + Dominus, LOCK **Purge the Foe** → play **Meatgrinder** vs his Purge). CORRECTED THREAT
  MODEL + MATHHAMMER (my first pass mislabeled + mis-ranked — see Rule 8). Four arrival threats, RE-RANKED
  by expected dmg/turn (all buffs stacked; my Knights: Castellan T13/28W 3+/5++, Crusader T11/26W 3+/5++,
  **Armiger T9/14W 3+/5++ = Ion Shield ranged-only** [user-confirmed; FIXED a data bug where Warglaive had
  invuln:None in profiles yaml]):
  (1) **Cyclone Termies(10)+Librarian[Fusillade=Lethal Hits]** = REAL #1 ranged Knight-threat, **~13/big
  Knight, ~14 one-shots an Armiger** (krak S9 AP-2 negates the Armiger 5++); slow M5, Teleport Homer;
  (2) **2× Land Speeder** MM S9 AP-4 D6 Melta2 (A2 ea=4 shots) = **Armiger-killer** (~12 within 9", ~9 big
  Knight); **melta bonus needs <9" so a DS arrival >9" only does ~6-9 — worst the turn AFTER landing**;
  (3) **Sternguard(10)+Librarian[Temporal Corridor]** = NOT the alpha-killer I first billed — vs big Knights
  they only wound on 6s but each 6 = **unsaveable Dev Wound, ~5-7/turn** → a persistent CHIPPER/finisher +
  anti-Sisters/character sniper; **their teleport turn is their WEAKEST shoot** (DS≠stationary=no Heavy;
  Conclave must run Telekinesis to enable the teleport = no Divination/Pyromancy that round); (4) **TH/SS
  Assault Termies(10)+Lysander+Ancient** = NO psyker, walks M5 (Teleport Homer=1 jump) — TH+Fist of Dorn
  Dev Wounds = **~24-28 melee, one-rounds ANY Knight** (even Lancer 4++ → ~4W left). MY GUNS: Avenger+
  Helverin+plasma = ~14W into 10 Sternguard = 7 dead (T1 wipe IF he deploys them). PLAN:
  can't table 155W of 2+/4++ → **out-score** (he's OC1). **Navigator 12" anti-DS dome is the linchpin** —
  denies ALL four (Sternguard teleport, Speeder drops, both homer jumps must land outside it). Kill Sternguard
  T1 if on board / spread Knights if reserved. NEVER melee the hammers with a premium Knight (Dev Wounds bypass
  invuln) — pin with expendable Armigers. Both Termie units place Teleport Homers at start → screen mid-board.
  Immolator Purge&Cleanse + BS OC10 half hold home under the dome.
  **★ OATH OF MOMENT is the engine (see SM-RULES note below):** correct stack into the OATHED Knight = Oath
  (re-roll HITS **+ +1 to WOUND**, army-wide vs 1 unit — the +1 because mono-Codex IF) + Wrath of Dorn
  (re-roll a WOUND-of-1 army-wide; FULL wound re-roll only for Lysander's melee unit). His numbers into the
  OATHED Knight ~double: Speeders 4.6→10.7, cyclone unit 6.4→11.5, Sternguard 4.2→8.1; **ALL his ranged on
  ONE Oathed Knight = ~30 dmg → KILLS a healthy T13 Castellan (28W) or T11 Crusader (26W) in a turn** (Armiger
  15.3 = one-shot). [TWO corrections the user caught: (a) a 2× harness bug — I'd multiplied the A2
  cyclone/multi-melta weapon by SHOT count (4) not WEAPON count (2 launchers/2 MMs), doubling both threats;
  (b) I'd OMITTED base Oath's +1-to-Wound and over-applied Wrath as FULL wound re-roll to all units when it's
  only re-roll-Wound-of-1 army-wide (full only for Lysander's unit). Net after both fixes: alpha ~30, not the
  ~40 (bug) or ~28 (bug-fixed but +1 missing).] So durability does NOT save the Oathed target; **WIN BY
  BREAKING THE CONVERGENCE, not tanking it.** KILL ORDER: **Land Speeders FIRST** (Oath ~doubles them,
  one-shot Armigers, mobile leg), then cyclone Termies, then Sternguard — remove any leg and the alpha falls
  below a Castellan's W. NOTE the melee brick (Lysander unit, full Wrath re-roll + Oath +1 wound) = ~49,
  one-rounds ANY Knight.
  BAIT the Oath onto a cheap Armiger / already-hurt Knight (it's 1 target/turn). Armigers are GLASS to his
  ranged (cyclones/close Speeders one-shot one) → pin/screen/bait trades, not gun platforms; keep them out
  of cyclone LOS / >9" from Speeder drops. My initial errors (all corrected): mislabeled Sternguard as
  "Fusillade", treated TH/SS brick as the teleporter, under-weighted the Speeders, over-hyped Sternguard as
  an alpha-killer (they're a ~7/turn unsaveable chipper), AND omitted Oath of Moment entirely (the big one).

- **SM-RULES — OATH OF MOMENT (Space Marine army rule, 11E-updated per SM faction pack; applies to EVERY
  SM-chapter matchup: SM/Salamanders/Imperial Fists/Dark Angels):** start of his Command phase he names ONE
  of my units; until his next Command phase, each attack from his army vs that unit: (a) **re-roll the HIT
  roll**, AND (b) **+1 to the WOUND roll** IF his army is a Codex: Space Marines detachment with NO
  BLOOD ANGELS/DARK ANGELS/DEATHWATCH/SPACE WOLVES units (so mono-SM/Salamanders/Imperial Fists GET the +1;
  a DA army does NOT). **So base Oath = re-roll Hits + +1 Wound (usually) — NOT hits-only.** Detachments/
  enhancements add MORE: **Wrath of Dorn** (Emperor's Shield) = re-roll a WOUND-of-1 army-wide + FULL wound
  re-roll for Lysander's unit; others add "re-roll Wound of 1" / "+1 to Wound (again)" / a SECOND Oath target.
  IMPLICATION: **always model opp damage into the ONE Oathed unit with re-roll hits + +1 wound (+ detach
  extras)** — it ~2×'s a unit's output and lets him CONCENTRATE a whole army to delete one durable model/turn.
  1 target/turn → counter = SPREAD + BAIT the Oath onto something cheap + break the convergence (kill/deny a
  leg). Concrete instance of Rule 8 (force-multipliers). MY Knights have NO equivalent army-wide re-roll —
  a real asymmetry to respect vs all Astartes. [Missed the +1-Wound on first pass; user caught it.]

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
- **Devastating Wounds** (24.10): crit wound → mortal wounds = Damage (bypass saves). **Crit wound =
  unmodified 6 unless a MATCHING [ANTI-X N+] lowers it (only vs keyword X)** — so Dev Wounds do NOT
  reliably beat a non-matching invuln (e.g. Anti-Titanic ≠ help vs a non-Titanic C'tan; Dev on 6 only).
  All other weapon abilities in the engine verified correct vs the PDF.
- **docs/core-rules-reference.md is now comprehensive** — all 5 phases, combat
  sequence, cover/terrain, modifiers, objectives, and core unit/weapon abilities,
  verified vs the PDF. The MODIFIER GLOSSARY (dice-roll vs characteristic) is
  "continued in the app" (not in the PDF) — doc states the established rule, marked [app].
- **PLUNGING FIRE:** a TOWERING model (ALL Knights) — or any model on 3"+ terrain —
  shooting a target WITHIN 12" with ground-level models gets **+1 BS characteristic**.
  Because it's a CHARACTERISTIC modifier, it DIRECTLY OFFSETS cover's −1 BS (net 0)
  at close range. But Knights are long-range (56-80"), so it only helps <12" shots.
  Not auto-applied in the engine — pass `--hit 1` for that case.
- Event Companion (docs/40k_event_companion.pdf) terrain LAYOUTS: the 5 Purge-the-Foe
  matchups are ingested (data/layouts/purge-the-foe.yaml); other 10 matchup-pairs only
  matter if the army disposition changes (you're always in a Purge-the-Foe matchup).

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
- **FINAL list (examples/best-purge-the-foe.yaml, 1985/2000):** Castellan A (Archeotech
  Autoloaders = variance fix), Castellan B (Blessed Plate = T13), Crusader (RFBC +
  Judicant's Helm → feeds IGNORES COVER to a Castellan), 2 Helverin, 2 Warglaive, +
  Navigator ally (75, home anchor) → army = exactly 2000/2000. Enhancement placement:
  DOMINUS enh (Archeotech/Blessed Plate) must go on Castellans; Judicant (buffs ANOTHER
  model, needs a Character bearer — NOT an Armiger) goes on the Crusader so both Castellans
  keep self-buffs. Swapping an Armiger→Navigator freed points to fit RFBC + all 3
  enhancements. Tool validates the Knights portion (1925); it can't validate the Navigator ally.

## Two validated list variants (user's playstyle = aggressive → leans Lancer)
- **Body-heavy** (examples/best-purge-the-foe.yaml): 2 Cast + Crusader + 4 Armigers + Navigator.
  More screening/board coverage, safer objective grind. "Textbook" per raw damage/OC math.
- **Threat-saturation** (examples/threat-saturation-purge.yaml): 2 Cast + Crusader + Cerastus
  LANCER + 1 Armiger + Navigator, 1995/2000. Trades 3 Armigers for the Lancer as a "distraction
  carnifex": 28W behind a **4+ FULL invuln** (vs everything) = a reliable resource sink that
  demands a response while the rest repositions/shoots/scores. KEY CORRECTION to my earlier
  "need bodies to hold" claim: Knights hold objectives with **OC 10 while shooting** (56-80"
  range), so the big Knights double as holders — Armigers' real edge is screening, not holding.
  This factor (durability + threat saturation + playstyle) is real and NOT captured by damage/OC
  math. Caveat: the Lancer's threat is melee (can be screened/kited); fewer bodies = less coverage.

## Imperial Agents allies (data/allies/agents.yaml)
- Knights (IMPERIUM) can take **Assigned Agents** allies. The allowance is a UNIT-TYPE
  cap, NOT points: at 2000 pts = **2 Retinue units + 2 Characters + 1 Requisitioned unit**
  (~5 cheap units available). Allies don't get the Knights detachment rule/enhancements.
  Navigator/Inquisitor/Priest = Characters; Voidsmen/Inquisitorial Agents = Retinue.
- **Navigator (75 pts** — MFM/BSData say 60, the 40k app says 75; use 75 to be safe) = the premier cheap home-sitter. HIDDEN (INFANTRY in dense terrain, not
  shooting) = not visible beyond detection range (default 15"); **GONE TO GROUND** (hidden +
  obscured by dense terrain + didn't shoot this/last turn) = −3" → **detection range 12"**. So
  DIRECT fire (snipers) can't target it from >12"; its **Gaze into the Empyrean** stops enemy
  Reinforcements within 12" (no Deep Strike/ingress inside 12"). NUANCE (detection range fully
  understood): Indirect Fire CAN target a not-visible model but hits only on unmod 6s + with cover
  → negligible into a 3W/4++ model; and "unless otherwise stated" detection range can be raised by
  enemy detectors. Net: immune to sniping + deep strike, effectively safe from indirect; only a
  ground assault into your backfield removes it. Must NOT shoot; needs dense terrain. OC1 (holds
  uncontested home). Frees an Armiger to push.
- **List impact:** swapping an Armiger (140) → Navigator (60) frees 80 pts, which RESOLVES the
  RFBC-vs-Archeotech tension (fit both) and stacks enhancements. See below.

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
