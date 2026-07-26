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

**★★ DETACHMENT POINTS (11E core mechanic, user-confirmed 2026-07-25) — I had a 10E-brain "ONE detachment"
assumption; WRONG. You take AS MANY detachments as your DP budget allows. A 2000-pt (Strike Force) game =
3 DP. Each detachment has a DP cost (from the MFM): e.g. Emperor's Shield 2DP, Librarius Conclave 1DP.
A list can stack several (his Great Value = Emperor's Shield 2 + Librarius Conclave 1 = 3DP), and the rules,
enhancements, AND stratagems of EVERY detachment taken apply to every model they can legally apply to — so
buffs from different detachments STACK. This applies to MY armies too (Knights get 3DP at 2000 → stack IK
detachments up to 3DP). ALWAYS check DP cost per detachment (MFM) + the game-size DP budget when list-building
or reading an opponent's list. This is THE enabler of the "tapestry" (Rule 8) — multi-detachment buff-stacking.**

**★ OBJECTIVES ARE TERRAIN, NOT MARKERS (11E, user-corrected 2026-07-26).** The 10E "objective markers" (little
tokens) DO NOT EXIST in 11E. Each objective is a specific MARKED TERRAIN PIECE (shown on the deployment map);
its FOOTPRINT is the scoring area. Control = more Objective Control within that footprint. CONTROL/CONTEST = your model's BASE TOUCHING the terrain footprint (you do NOT have to stand ON/inside it) —
higher total OC touching = controls. Only MARKED terrain scores: ~5 objectives = home ×2 + 1-2 centre + 2
expansion (No-Man's-Land); other terrain is just cover / wall-blocking. **BASE SIZES (positioning math,
user-provided 2026-07-26):** big Knights (Castellan/Crusader/etc.) = **170×105mm oval (~6.7"×4.1"; edge ~3.35"
from centre)** → can base-touch an objective while the hull sits ~3" BACK (out of a charge) + screens a huge
lane; Armigers = **100mm round (~3.9")**; Immolator = Rhino hull **~120×75mm** (GW doesn't BASE vehicles → this is
the measured HULL footprint, which is the base-touch contact surface); Sisters/Sternguard/Intercessors = 32mm;
Terminators = 40mm. **REFERENCE (user-provided, verify-current): base-size guide =
en-blastedhorizons.blogspot.com/2015/07/guide-to-40k-bases.html — despite the 2015 URL it's a LIVING ARTICLE
maintained to 2026 (current), good for OPPONENT base sizes in future matchups.** (It lists the Knight oval as
170×109mm; user measures 170×105 — negligible ~4mm; use 170×105.) This CORRECTS my "contest = point-blank death" overstatement — I hold the SAFE
objectives from a base-touch ~3" out; I only decline the ONE small footprint the OC22 brick squats (out-holding
OC22 needs OC23+ crowded onto it = inside its 2D6" charge). Terrain = cover, so **cover is
everywhere** on GW/tournament layouts. COVER = −1 to hit, RANGED ONLY (models in/behind terrain; Knights get it
too but it does NOTHING vs melee). Always model cover in BOTH directions when analysing a matchup. (LSO uses GW
terrain layouts closely; I have the maps+legends; sightlines are not an issue for a back-line gunline.)

**★ COMMAND POINTS + RESERVES/DEEP STRIKE (11E core, verified 08.02/15.07/20.x/24.09 + user-taught 2026-07-26).**
CP: **Both players gain 1 CP in the Gain Core CP step of EVERY Command phase — own AND opponent's — so each
player nets ~2 CP/battle round (~10/game)**, banking CP even on the other's turn (reactive stratagems). I'd
been under-counting at ~1/round. Spend only on Stratagems (0-3 CP); a stratagem can't be used twice in the
same phase, and one unit can't be targeted by two stratagems in a phase (unless stated). RESERVES: Strategic
Reserves (≤50% army pts) arrive from ROUND 2, ingress within 6" of a battlefield edge, NOT in opponent's DZ
before round 3, un-arrived destroyed end of round 3. **DEEP STRIKE (24.09):** if every model has it, ingress
ANYWHERE (even in opponent's DZ), set up >8" from all enemies. **RAPID INGRESS (15.07, core, 1CP):** ingress
one reserve unit at END OF OPPONENT'S MOVEMENT PHASE (reactive). **⚠ THE OPERATIVE NUMBER IS THE CHARGE: a
same-turn charge out of Deep Strike / Rapid Ingress needs 2D6 ≥ 9 (~28%)** — raw set-up text reads 8" but a
unit ~8" out needs a 9 to reach Engagement Range, so DS/ingress arrivals USUALLY CANNOT CHARGE ON ARRIVAL
(they threaten NEXT turn). Anti-DS bubbles (Navigator Gaze ≤12") push drops back further. **"40k is won/lost
in the Movement phase"** (user, from better players): win it by DENYING enemy reserve landings (dome +
screening: every drop must be >8-9" from ALL my models) + KITING slow bricks + OUT-RACING to objectives —
then the enemy's Shooting/Fight phases go impotent. His Great Value is a movement-phase list (Teleport Homers
= 0CP Rapid Ingress, Temporal Corridor/Dropship Extraction reserve-bails, Deep Strike Speeders); my standoff
is the movement-phase answer. **GAZE-OF-THE-EMPYREAN NUANCE (user-taught 2026-07-26):** the Navigator's 12"
no-Reinforcement bubble protects the NAVIGATOR (un-chargeable out of Reserves — arrival >12", charge caps at
2D6=12"), but NOT loosely-placed nearby units: a friendly model strung distance D toward the enemy is only
~(12-D)" from the nearest legal drop, so if D>3" an arrival lands ~9" from it and makes the 28% 9" charge into
it (e.g. into Battle Sisters around the Navigator). FIX: tuck bodyguard/home units WITHIN ~3" of the Navigator
so (12-D)>9" — no clean 9" charge on Navigator OR the tucked unit. Also Navigator Third Eye = battle-shock 1
enemy unit within 12" & visible in my Shooting phase (minor tool). **★ TERRAIN VISIBILITY (Core 13.06-13.11, verified PDF pp.46-51 + user-taught 2026-07-26):** (1)
BENEFIT OF COVER 13.08 = -1 to hit; qualifies if EVERY model is INFANTRY/BEASTS/SWARM in a terrain area OR
'not fully visible' behind intervening/obscuring terrain. **KNIGHTS GET COVER EASILY** via clause 2 — Towering
silhouette is clipped by ruin WALLS = not fully visible (wonky but TRUE, user-confirmed; I over-corrected to
'no cover' — WRONG). So his shooting into my Knights is usually -1. Plunging Fire (Towering +1 BS, 22.05) only
within 12" = irrelevant to a long-range gunline. (2) HIDDEN 13.09: INFANTRY/BEASTS/SWARM in DENSE terrain that
didn't shoot this/last turn → only targetable within detection range (default 15"); shooting breaks it. Knights
CAN'T be Hidden (VEHICLE, no detection range); Terminators + SISTERS can (very relevant for Sisters later). (3)
OBSCURING 13.10 fully blocks LOS (untargetable) if every LOS crosses it. (4) ENGAGEMENT RANGE = 2" horiz/5"
vert (03.04) — screening/charge geometry. (5) 13.06: VEHICLES/Knights can't move THROUGH dense terrain >2"
tall (go around); INFANTRY move through freely. GONE TO GROUND 13.11.01 (App-only, user-provided verbatim 2026-07-26): a HIDDEN model that is ALSO not-fully-
visible behind DENSE terrain, whose unit did NOT shoot this or last turn → **-3" detection range (15→12")**.
Passive state (not an action), INFANTRY-only (Knights excluded). Shooting this/last turn disqualifies it
regardless of any shoot-and-stay-hidden ability. = stronger Hidden; matters for Sisters (super-safe home
holders when not shooting) and his non-shooting infantry.
**★ SUPER-HEAVY WALKER (24.35) vs WALKER (user-corrected 2026-07-26):** SHW is MOVEMENT-ONLY (move through
non-TITANIC models + terrain ≤4" tall on normal/advance/fall-back moves; optional MOBILE, battle-shock on 1).
It does NOT grant fall-back-and-shoot (I'd INVENTED that). BIG Knights (Castellan/Crusader/Lancer/etc.) have
SHW; **ARMIGERS (Warglaive/Helverin/Moirax) have plain WALKER — NOT SHW.** ⇒ NO Knight can fall back and still
shoot; a fell-back unit can't shoot at all. Only Valourstrike's ADVANCE-and-shoot (Assault) is legal.
PRACTICAL: keep gun-Knights + Helverins OUT of combat (can't disengage-and-shoot; if engaged, a MONSTER/VEHICLE
(Knights/Armigers) can still shoot OUT of combat at ANY target (close-quarters shooting 10.06 — no [CLOSE-QUARTERS]
weapon needed), at −1 to hit; ONLY restriction = [BLAST] weapons can't target the unit it's ENGAGED with (can
fire blast at OTHER units). So a tar-pit by SOFT CHAFF (Vanguard) costs a gun-Knight just −1
to hit, NOT its shooting — screening THAT off is a preference. BUT keeping his ~50-dmg MELEE BRICK off a
gun-Knight is MANDATORY (a brick that reaches it kills it in the Fight phase; shooting-while-engaged doesn't
save it from melee) — enforced by DISTANCE/KITING (M5 brick can't cross 40"+ to a back-corner gunline), not
screen bodies. Screen BODIES actually earn their keep for (a) RESERVE DENIAL (every model forces drops >9")
and (b) protecting FORWARD grabbers (Warglaive/Immolator/Sisters) via 2" Engagement Range + no-move-through-
models. The back gunline barely needs screens — distance protects it. [I flip-flopped 4x on the engaged rule;
THIS is right.]). The Warglaive is my melee-capable screen/objective
Armiger (can FIGHT its way out). **★ DEPLOY HIDDEN (user, from experience): good players (incl Great Value, and
ME) deploy as HIDDEN/cover-max as possible to dodge alpha strikes — esp. going 2nd.** So his soft shooters are
NOT easy T1 targets even if 'on the board' (Hidden beyond 15"/behind obscuring, or reserved) — my alpha is
punish-as-they-expose, not a big T1 blow. My Towering Knights can't be Hidden but DO get cover (walls); still
minimize his firing ANGLES into them — don't over-expose to lucky anti-tank (a stray Gladiator-Lancer-type
shot can chunk a Questoris).

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
- **★ KNIGHT MINDSET (user law 2026-07-26): "Always outnumbered, rarely outgunned."** Knights are FEW models
  (~9) with huge firepower + durability but LOSE the OC/objective war by construction against durable,
  army-wide-OC, sticky-objective armies (esp. elite terminators — the archetype that 98-31'd the user's Sisters
  at HeeYaw with 3 Deathwing-Knight bricks). **Start every hard matchup from the EXPECTATION OF A LOSS and hunt
  for the HEIST — don't assume the guns bail me out.** Where the win comes from for the outnumbered-but-outgunning
  underdog: (1) FIREPOWER AS DENIAL not domination — delete his SOFT OC (each kill = OC + damage removed),
  starving his kill/objective clauses (win by subtraction). (2) SECONDARIES are the Knight's real scoreboard —
  fast Knights bank the MOBILITY deck (Engage, Behind Enemy Lines, Storm Hostile Objective) a slow wall can't;
  this is how an outnumbered army out-POINTS a superior one. (3) A few DECISIVE strikes (a Lancer/Gallant blade
  that KILLS characters / threatens the backfield+home) beats a passive extra gun. (4) NOT-DYING is the price
  of entry, not the win. **Don't over-sell my matchups; model the opponent playing OPTIMALLY** (best Psychic
  Discipline every round, Armour of Contempt on D, Wrathful Conquerors to bank objectives, Rapid Ingress timed
  to punish). [I was repeatedly too optimistic vs Great Value; corrected.]
- **★ LANCER SKEPTICISM (user law 2026-07-26): do NOT over-value double Lancers.** Lancers CAN and WILL die
  — an entire army shooting one for a turn, OR a dedicated melee-specialist unit, takes it down; the 4++ is not
  immunity. Each Cerastus Lancer is **melee-ONLY (no guns)**, so running 2 gives up a LOT of ranged output — the
  exact firepower the "firepower-as-denial" plan and the durable/horde meta (C'tan un-killable, Orks un-clearable)
  actually need. The MC gauntlet's "blades" abstraction **OVER-CREDITS** Lancers (mobile OC/contest) and IGNORES:
  screening/kiting denial, charge variance, and melee being **BLUNTED by the durable meta** (AP-3 wasted vs 4++,
  D8→D7 vs −1 Dmg, more lost to FNP). So treat the sim's double-Lancer verdict (2-Lancer 73%) as SUSPECT — it
  flatters a one-dimensional tool. **Settle Lancer-count empirically vs REAL lists, not hand-tuned enemy params.**
  A Questoris **gun** package (e.g. Bondsman-buffed Helverins: 48" S9 AP-1 D3 autocannons that shoot AND hold OC
  AND don't need a charge) is a live alternative to a 2nd melee blade. User still values ONE Lancer as a proven
  "distraction carnifex" (does work every game), but is not sold on TWO. See [Two validated list variants].
- **★ COUNTERPOINT — the Lancer's REAL premium role is DECAPITATION/assassin, not distraction (user law 2026-07-26).**
  Cerastus shock lance strike = A5 WS2+ **S20 AP-3 D8 [LANCE]** (+ a minor 12" A6 S6 Assault Sus2 gun — it's NOT
  gunless). Into a durable T9-11/4++ linchpin it punches THROUGH the invuln that guns can't crack: vs Lion (T9 W10
  4++) ≈ **17 unsaved dmg in one charge → one-rounds him even under FNP**; M14 + Valourstrike advance makes the T2
  catch. **User is 8-0 vs Lion El'Jonson and actively HUNTS him with the Lancer on sight** (do NOT advise "dodge
  Lion" — the Lancer is the answer TO him). Guns only force a 4++ model onto its invuln and grind; a Lancer's D8×LANCE
  charge kills it fast. **So Lancers SCALE with how many durable high-value melee targets (Lion, Daemon Princes, big
  characters/monsters, enemy Knights) the meta presents** — a linchpin-monster list rewards a Lancer assassin; a
  gun-heavy chaff list rewards guns. This is the real answer to "how many Lancers," not an abstract 1-vs-2. Balances
  the LANCER SKEPTICISM bullet above — both are true; pick Lancer count by the TARGET-RICHNESS of the expected field.
  - **Lancer kit detail:** Shock lance STRIKE A5 WS2+ S20 AP-3 D8 [LANCE] (single hard target: character/monster/
    Knight) vs SWEEP A10 S10 AP-2 D3 (squishier, higher-model-count squads) — flexible, pick per target. **Shock
    Charge ability = a FREE Crushing Impact** (core §15.06, normally 1CP tank-shock): after the Lancer ends a charge,
    roll D6 = its Toughness (T11 → 11D6), each **5+ = 1 MW to the target (max 6, ~3.7 avg, BYPASSES invuln)**, each
    1 = 1 MW to itself (~1.8, trivial on W28). So every Lancer charge = ~3-4 invuln-ignoring MW + the melee strike.
  - **★ COROLLARY — the Lancer CANNOT heist a faceless BRICK WALL (the 31-98 hard counter).** vs 3× Deathwing-Knight
    bricks there is NO decapitation target: killing a brick's leader changes nothing, Crushing Impact + Sweep only
    chip ~1-2 W4 models out of an un-tableable 4++/−1Dmg OC wall, and the guns are wrong-shaped (W4 cap overkill).
    It's a pure out-bodied/out-OC'd ATTRITION loss — accept it (see HARD COUNTERS principle). Lancer heist value ∝
    enemy decapitatability: linchpins (Lion/DPs) → Lancer wins solo; no-target brick wall → nothing to bite, OC loss.
- **★ TARGET-PRIORITY: kill the force-MULTIPLIER support piece before the shooters it buffs.** The mark-engine /
  buff-aura / re-roll engine converts enemy VOLUME into lethality vs Knights. Concrete (DA Darkflight+Ironstorm
  speeder list): **Storm Speeder Thunderstrike's "Thunderstrike"** = after it shoots, MARK one Monster/Vehicle it hit
  → every friendly Adeptus Astartes ranged attack vs that unit gets **+1 to WOUND** till end of phase (turns 10
  Hellblasters + 3 plasma speeders from wounding a Knight on 4+ to 3+). Kill the Storm Speeder FIRST (T9 W11 3+/6++,
  a Volcano deletes it) → plasma volume drops from "dead Knight" to "chunked Knight." Also watch **Land Speeder
  Vengeance "Storm of Vengeance"** (once/turn, in MY Shooting phase, if I destroy an Adeptus Astartes unit within 6"
  of it, that Vengeance shoots back immediately — reactive out-of-sequence plasma; punishes clustering my kills near
  it) + **Nightforged Battery** enh (re-roll shot count + Hazardous = maximized safe supercharge). Both speeders M14
  T8/T9 W10/11 3+/**6++** OC3 — killable but FAST (+ Deep Strike). Plasma storm battery supercharge = 36" ~D6+1 shots
  S9 AP-3 D3 Blast Twin-linked; Hellblaster plasma incinerator supercharge S9 AP-4 D3 RF1.
- **★ ARCHETYPE — Tyranid 5-NORN MONSTER-MASH (HeeYaw Game 4, user won 81-75; verified 2026-07-26).** Assimilation
  Swarm (HEAL/regen: Feed the Swarm = Harvester units Regenerate a friendly Tyranids unit each Command phase — heal
  OR return a destroyed model; + Norn Unstoppable Monstrosity D3/turn) **+** Talons of the Norn Queen (Higher
  Imperatives → **Protean Purpose**: each Norn re-picks its Singular Purpose ONCE per battle). **Take and Hold.**
  5 Norns (M10 T11 W16 Sv2+ OC5; 3× **Assimilator** = 4++ via Synaptoprescience + Toxinjecter Harpoon [12" shoot to
  MARK a Knight → +2 to charge it, then melee A4 S12 AP-3 D6+1] + talons A6 S9 AP-2 D3; 2× **Emissary** = NO invuln
  base 2+, psychic tendril 18" S12 AP-3 D6 Melta2 + [ANTI-CHARACTER 2+]) + Neurotyrant (heal-aura/synapse/warlord)
  + 6 Zoanthropes (Warp Blast S12 AP-3 D6+1 Lethal Hits psychic + MW) + chaff. Army: Synapse + Shadow in the Warp
  (once/game ALL my units battle-shock test → can deny my Rotate on a key turn).
  - **Singular Purpose menu (pick 1 turn-1, swap once via Protean Purpose):** (a) HUNTER = re-roll Hit AND Wound vs
    one chosen unit all game → ~DOUBLES a Norn's dmg into a Knight it names; (b) ANCHOR = while on an objective, FNP
    5+ **AND Objective Control 15**. **★ OC15 anchor is UNSHIFTABLE by OC (my Knight is OC10) → on Take and Hold I
    CANNOT out-OC it; the primary becomes a KILL-RACE — I must physically remove the Norn to take its objective.**
    Optimal enemy line: bank objectives early with OC15 anchors, then pivot Norns to Hunter to murder my Knights.
  - **How Knights fare:** the threat is MELEE + psychic (my Ion Shield 5++ is RANGED-only → in melee I'm on bare 3+;
    only the Lancer's 4++ holds). Their shooting is moderate (~13 S12 AP-3 shots). **Durability nuance that wins it:
    only the 3 Assimilators have 4++; the 2 Emissaries + support have NO invuln → my Volcano (S18 AP-5) ~one-shots an
    Emissary.** So it's a Monolith-style REMOVAL race (not a C'tan wall): focus-kill the no-invuln Emissaries/
    Zoanthropes/Neurotyrant at range, grind the 4++/FNP/heal Assimilator anchors, Lancer-assassinate (target-rich,
    ~21/charge kills a Norn), refuse the melee gang (kite M10-14, don't let 2+ Norns pile one Knight), win on kills +
    secondaries + removing enough anchors — NOT on out-bodying OC15×several. Genuine coin-flip.
  - **★ TRANSFERABLE: vs an OC-inflation anchor (OC15/sticky/FNP), "out-OC it" is OFF THE TABLE → it's a KILL-RACE;
    target priority = remove the anchor BODY, not contest the objective.** Also deepens the Ion-Shield lesson: a
    MELEE-primary army (5 Norns / Lion / DPs) bypasses my signature durability — win by shooting them off the board
    BEFORE the charge + Lancer 4++, never by tanking hits.
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

- **LSO v2 — FULL-TAPESTRY REBUILD + WHOLE-GAME SIM (2026-07-25).** After a deep re-read of every unit +
  BOTH his detachments, the picture got much richer (Rule 8 in full). His GREAT VALUE tapestry — layers I'd
  missed: (a) **Emperor's Shield STRATAGEMS**: Armour of Contempt (−1 AP def), Fury of the First (+1 Hit,+1
  Wound-if-below-strength — stacks on Oath), Disciplined Extermination (+1 AP+Ignore Cover), Obdurate Vengeance
  (fight-on-death), **Dropship Extraction** (bail ANY Terminator unit to reserves — 2nd teleport engine, no
  Telekinesis needed), Wrathful Conquerors (sticky obj); (b) **Librarius Conclave** = pick ONE Discipline/
  battle-round, ALL his ADEPTUS ASTARTES PSYKER units get it (only his 2 Librarian-led units = Sternguard +
  cyclone Termies; the TH/SS brick has NO psyker → no discipline). Disciplines: Biomancy +2"M / Divination
  rr-1s hit&wound / Pyromancy +1AP+Sustained(w/Fusillade) / Telekinesis Deep-Strike-enable+−1S-def /
  Telepathy ignore-hit-mods. Temporal Corridor (Sternguard Librarian): DS if Telekinesis + bail-to-reserves
  if unengaged at end of MY Fight. Fusillade (cyclone-Termie Librarian): Lethal Hits +Sustained-if-Pyromancy;
  (c) **UNIT Oath-synergies**: Sternguard "Sternguard Focus" = FULL wound-reroll vs Oath; cyclone Termies
  "Fury of the First" = **+1 Hit vs Oath (datasheet)**; Terminatus Assault = Battle-shock on engage; (d)
  **Lysander**: Icon of Obstinacy (his UNIT −1 to wound when S≥T5 — big def layer on the brick), Rampart (2+
  inv once), **Inspiring Commander → non-Character Terminators are OC2 WHILE NOT BATTLE-SHOCKED** (base OC1;
  OC = SUM of all models per unit [user sanity-check]) so a 10-Terminator brick = OC20 (+Lysander+Ancient
  Characters at OC1 = OC22 un-shocked). **Battle-shock is NOT a lever (user-corrected, CR 8.03/1.07): a unit
  only TESTS while Below Half-Strength [need 6+ Terminators dead first — I can't] and passes on Ld6+ ~72% — so
  the OC22 is effectively PERMANENT.** ⇒ I can't out-kill it, can't out-durable it, and can't contest its
  objective up close (markers sit in terrain = getting a Knight in OC range = in its ~50-dmg charge range =
  dead Knight; FNP 6+ ~1/6 does NOT save a Knight from ~50 melee). Fist of
  Dorn S10 AP-3 D3 A5 Dev; (e) Bladeguard Malodraxian Standard (−1 to wound when S>T4); (f) **Land Speeders
  HAVE Deep Strike** (user-confirmed 2026-07-26 — my BSData pull missed it; CORRECTED) → ingress anywhere >8"
  from me, but >8" = outside multi-melta half-range (no Melta bonus on arrival) + my 12" dome pushes them back
  + Volcanoes one-shot them. Full-stack alpha into an Oathed Castellan ≈ **34** (~10 of it UNSAVEABLE Sternguard Dev), kills it.
  MY LIST v3 (user picked "big-gun standoff", disposition Priority Assets — v2 Freeblade/FNP was REJECTED by
  user: FNP is wrong axis, and durability/proximity is a losing game) — **examples/knights-vs-greatvalue.yaml =
  Valourstrike Lance (2DP) + Dominus Foebreakers (1DP), disposition Priority Assets.** Dominus Foebreakers
  GRANTS Priority Assets + gives DOMINUS Castellans +1 to hit units in terrain (his whole army sits on terrain
  objectives). Valourstrike = **Rotate Ion Shields (4++ on the Oathed Knight)** + Advance-and-still-shoot.
  Roster: **2× Knight Castellan (both DOMINUS — 2 Volcanoes one-shot both Speeders + chunk Lysander @60"; twin
  plasma decimators wipe Sternguard) + Knight Crusader (Avenger A18 = anti-infantry deleter) + 2 Helverin
  (36" backfield autocannons grind cyclone Termies) + 1 Warglaive (fast: grabs far objectives / steals home)**
  + Navigator dome + BS(OC10 home) + Immolator(cover-strip stacks with Dominus +1 hit). PLAN = **SPEED + RANGE
  + SPREAD, NEVER enter the brick's charge threat**: gunline sits at the BACK and deletes his SOFT ranged legs
  (Sternguard T1, then 2 Speeders + cyclone Termies by T3) from 36-60"; his M5 brick can never catch it; I
  cede the ONE central objective the OC22 brick squats and take the other 3-4 + steal his undefended home R5
  (+10 Vital Link). Kill-Sternguard-T1 drops his T2 alpha ~34→~17 (→~13 w/ Rotate + my Castellan's COVER) — a
  28W Castellan shrugs it. **COVER (user: GW terrain layouts = cover EVERYWHERE; sightlines fine for standoff):
  −1 to hit, RANGED ONLY (Knights get it too but NOT vs the brick's melee).** MY cover-mitigation: 2 Castellans
  have Dominus Foebreakers +1-to-hit-in-terrain = cover-immune vs his terrain-sitting army (my reliable
  cover-punchers); Immolator Purge & Cleanse strips cover on 1 massed-fire target/turn (Sternguard T1);
  Crusader/Helverins eat −1 into still-covered targets → point them at stripped/open units. HIS shooting into my
  in-cover gunline is −1 (his cyclones cancel via Fury, Speeders eat it) → alpha further reduced. Net: cover
  slightly favors ME (better mitigation + protects my Knights). His melee ignores cover but never reaches.
  MISSION: my Priority Assets vs his Purge → I play **Vital Link**, he plays **Destroyer's Wrath** — VERIFIED
  against the GW Event Companion (scratchpad event_companion.pdf pp.33-35; my tool's mission data is CORRECT).
  **REAL BOARD (EC pp.33-35):** 3 layouts for this pairing — A (left/right zones), B (diagonal/Crucible), C
  (top/bottom); organiser picks/randomizes; standoff works on all (GW deliberately leaves firing lanes — user
  confirms sightlines fine). **SIX objectives = 2 home (opposite corners) + 2 CENTRAL (middle) + 2 expansion
  (NML)** — NOT one central. ⇒ his OC22 brick squats ONE central; I hold the OTHER central with a fast body
  (Warglaive/Immolator) → I KEEP Vital Link's central bonuses (+2 end-turn, +4 Command) every round instead of
  conceding them (upgrades the win). Terrain-layout footprint sizes (EC p.7): 6x4"×4, 10x2.5"×2, 6x2"×4,
  7x11.5"×4, 8x11.5" polygon×2 (Battlefields: Armageddon set). **SECONDARY MISSIONS (both players TACTICAL,
  user-confirmed): identical 18-card deck (VERIFIED complete vs gdmissions.app/11th/secondary-missions; my
  data/secondary-missions.yaml matches). Draw 2 each Command phase, complete for VP (3-5 ea, some 'for each'),
  KEEP uncompleted (accumulate several active), many need an ACTION (Core Rules §16 = unit forgoes shooting).
  ~40 VP of a ~90 game — I'd been hand-waving them. KEY ASYMMETRY: a mobile standoff completes the deck's
  objective/mobility cards for free (Behind Enemy Lines, Engage, Secure No Man's Land, Centre Ground, Forward
  Position=control-his-home which ALSO scores Vital Link +10, Bring It Down on his 2 Speeders, Cleanse action)
  while his best cards (Bring It Down / Assassination) need to kill MY Knights (standoff denies it).
  **BUT CORRECTED (user 2026-07-26 — I'd UNDER-scored him): OBJECTIVE CONTROL IS EXCLUSIVE (user-corrected
  2026-07-26): the HIGHER total OC in range controls an objective and ONLY that player scores it (checked
  usually in the Command phase; some secondaries specify other timing) — players do NOT both hold the same
  objective. His OC22 bricks reliably control the 1-2 objectives they SIT ON (can't out-OC a brick without
  crowding OC23 into its charge) → he banks single-objective cards there (Cleanse/hold). BUT he has only TWO
  slow bricks vs my 5+ mobile OC bodies, so I OUT-CONTROL the board's other objectives → *I* complete the
  objective-secondaries (Secure No Man's Land, etc.) + DENY his (and deny his Destroyer's Wrath 'more objectives'
  clause); I can also hand him a dead A Tempting Target by designating an objective his bricks aren't on. So his
  secondary is moderate (~15-20, mostly kill-cards on my chaff [No Prisoners/Bring It Down on Immolator/Warglaive/
  Sisters] + Defend Stronghold early + his 1-2 held objectives), NOT the ~28 I over-corrected to. **STICKY OBJECTIVES
  (user 2026-07-26): his Intercessors have OBJECTIVE SECURED** — if they control an objective at end of his
  Command phase (in range), it stays HIS even after they die/leave, UNTIL I control it (higher OC) at the start
  or end of ANY turn. **Second sticky source: Wrathful Conquerors** (Emperor's Shield strat, 1CP) makes a
  Terminator/Bladeguard/Sternguard/Vanguard unit's objective sticky → a brick can grab+sticky a central and
  move on. So I can't just 'show up after he leaves' — I must ACTIVELY OUT-CONTROL (higher OC in range than his
  remaining OC) to flip a secured objective. **HOME-STEAL SEQUENCE for the +10 (Vital Link end-of-battle):** his
  Intercessors (~OC10) secure his home → a lone Warglaive (OC6) can't flip it; I must WIPE the Intercessors
  first (Crusader Avenger kills 5×T4W2) → his OC there = 0 → my Warglaive (OC6>0) controls → flips at end of
  that turn → and I must STILL control it at end of battle (Warglaive survives on it, or a backup body). One
  turn slower than 'run a Warglaive onto his home.' **★ REALITY CHECK (user 2026-07-26 — I was TOO OPTIMISTIC):** (a) Intercessors = 5×OC2 = **OC10**;
  to flip his SECURED home I need OC>10 in the footprint — a lone Warglaive (OC6) can't, a single Castellan
  (OC10) only TIES (a tie doesn't beat a secured hold) → need TWO bodies (Knight+Armiger) OR Intercessors dead
  first. (b) Clearing the Intercessors is HARD: **Armour of Contempt (1CP) drops my Avenger AP-2→AP-1 → they
  save 4+**, + cover, so honest ≈ 3 dead / 2 left — and only IF he mis-positions; played HIDDEN behind his home
  terrain they're untargetable >15". (c) The Immolator/Sisters package DIES (ablative, not durable — don't rely
  on it for late OC). ⇒ **the +10 home-steal is UNRELIABLE**, and it was load-bearing in my ~74 estimate.
  HONEST VERDICT: this is a CLOSE game, ~**Knights 62 vs Great Value 56** (narrow win / coin-flip), NOT a
  comfortable win. His DEFENSIVE objective game (army-wide OC + STICKY objectives + Armour of Contempt + Hidden)
  is strong; my standoff wins the SHOOTING+SURVIVAL war but is TOO PASSIVE ON OBJECTIVES to close. ⇒⇒ THE LIST
  LIKELY NEEDS RETHINKING for the plan redo — the triple-gun standoff can't take/hold enough board; need more
  MOBILE OC + a way to crack a sticky, defended home (durable OC bodies, not a fragile Immo package). Stop
  over-selling the matchup — it's favorable-ish, not dominant. Honest game ≈
  Knights ~78 vs Great Value ~44 (clear ~34-VP win). Great Value is still a real army — don't dismiss it — but
  objectives are EXCLUSIVE, so my mobility/OC-spread out-scores his 2 immovable bricks. **★ CAVEAT (user 2026-07-26): ALL his models have OC, not just the bricks** — Sternguard ~OC11,
  Intercessors ~OC10 (sticky), Bladeguard ~OC7, Vanguard ~OC5 ×2, Land Speeders OC3 ×2. So his objective game is
  ARMY-WIDE and CONTESTED, esp. EARLY (all alive + M14 Speeders/M12 Vanguard reach objectives fast). I don't
  out-control by raw OC bodies — my gun-Knights (OC10) are PINNED to back-corner shooting positions and DON'T
  contest the mid-board; my forward OC is thin (Warglaive OC6 + Immolator OC3 + Sisters on home). I win the OC
  war by ATTRITION: killing his soft support (Sternguard/Speeders/cyclones/Vanguard) removes their OC too, so by
  T3-5 his control collapses to the 2 bricks + sticky Intercessors while my mobile pieces take the flanks + his
  home. Honest game ≈ **Knights ~74 vs Great Value ~50** (clear ~24-VP win but CONTESTED, not ~78-44). ⇒ LIST
  TENSION to resolve in the plan redo: the triple-gun-Knight standoff may be too light on MOBILE OC — consider
  trading 1 Castellan for 2 more Armigers to actually HOLD the board, not just kill onto it.** WHOLE-GAME
  SIM (v3): **docs/Great-Value-vs-Knights-Full-Game-Simulation.docx** (tools/gen_greatvalue_sim_docx.py) —
  5 rounds phase-by-phase, ~84-40 Knights. Verdict: win by REFUSING the fight the wall wants, deleting what can
  actually hurt me from safety, and out-mobiling M5 bricks on the mission — not by out-fighting/out-tanking.

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
- **Questoris Companions detachment (CORRECTED 2026-07-26) is an OATH / melee-hero detachment — NOT a
  Bondsman/Armiger detachment** (I wrongly grafted baseline Bondsman + other detachments' enhancements onto it).
  Rules: **Heroes of Legend** (start of your turn, if current Oath fulfilled → determine an ADDITIONAL Oath, no
  repeats — stacks Quality buffs) + **Valour's Reward** (its Enhancements are EXPENDABLE — used once then locked;
  each Oath you fulfil REFRESHES all expended ones). Enhancements (all expendable, big-Knight melee/hero flavour):
  Crushing Condemnation (after bearer fights & destroys a unit → pick enemy unit not in ER within 12"/visible, roll
  6D6, each 4+ = MW), Herald of Triumph (after a Charge, enemy units in ER take Battle-shock −1), Wyrmslayer
  Divination (Shooting: re-roll Hits vs FLY), Pennant of Silvered Fury (bearer's melee gains [SUSTAINED HITS 2] a
  phase). **Its main draw = the "Driven by the Past" stratagem: one TITANIC unit can Advance AND Charge** (user-
  confirmed). **VERDICT for a gun list: NOT worth it — keep Valourstrike Lance.** Valourstrike's army-wide
  Assault-on-Advance (whole gunline advance-and-shoot) >> one Titanic advance+charge; Assault already covers
  advance+shoot, so QC only ADDS advance+CHARGE for ONE unit (marginal — a Lancer is M14 and can usually charge).
- **Weapon profiles (BSData ik_lib.json, verified 2026-07-26) — don't confuse these two:**
  **Armiger autocannon** = 48" A4 BS3+ S9 AP-1 D3 (no keywords; the Helverin's twin guns).
  **Questoris heavy stubber** = 36" A3 BS3+ S4 AP-1 D1 [RAPID FIRE 3] (a big-Knight secondary; anti-infantry).
- **★ Rotate Ion Shields is a VALOURSTRIKE LANCE stratagem — NOT a core/universal Knight stratagem** (user-
  confirmed 2026-07-26; corroborated by ABSENCE from core army rules + faction pack + BSData library —
  detachment stratagems aren't in those extracts). So **only a Valourstrike list gets the 4++-on-the-Oathed-Knight
  every-turn survival lever** that ALL the meta analysis leans on. This is a MAJOR reason to lock Valourstrike
  (on top of Bold Gallantry's army-wide Assault). Corollary: the MC meta-gauntlet's "Rotate every turn" assumption
  is valid ONLY because both candidate lists run Valourstrike; a non-Valourstrike detachment loses Rotate entirely.
- **Rotate protects AT MOST ONE Knight vs shooting per turn (user law 2026-07-26; Core Rules §15, core.txt:2552):
  stratagems are once-per-phase.** In the opponent's Shooting phase I can Rotate exactly ONE Knight to 4++; **but
  EVERY big Knight already has a base 5++ INVULN vs shooting (Ion Shield — ranged only), so AP is largely IRRELEVANT
  vs Knights in the Shooting phase regardless of Rotate** (user law 2026-07-26). Rotate just upgrades ONE Knight
  from 5++ → 4++. (Cerastus Lancer is even better: 4++ FULL invuln, melee AND ranged, always — no Rotate needed.)
  Consequence: enemy AP-heavy shooting (Obliterators AP-3, death rays AP-4, CSM's +1-AP-near-objectives) is mostly
  WASTED into Knights — they defend on the invuln. Also §15: can't target the same unit with >1 stratagem in a
  phase. So shooting durability is "ONE Knight at 4++ + the rest at 5++", NOT "3+ armour eating full AP." Aligns fine with an enemy that
  focus-fires ONE Knight (I Rotate that one); an army with enough anti-Knight to threaten TWO Knights in a single
  phase (Necron death rays, C'tan) kills the un-Rotated one. Meta agents already modelled this ("Rotate saves one
  Knight/turn; they focus another").
- **Gate Warden Lance got NERFED in the latest Dataslate** — it was the user's HeeYaw detachment, so **the HeeYaw
  games (incl. the 90-61 win vs the CSM "Longest Night" list) were played WITHOUT Rotate Ion Shields.** Meaning:
  those matchups are even MORE favourable once we add Rotate via Valourstrike — the Knights survived that anti-Knight
  fire without their best defensive tool and still won. (This nerf is WHY the user is detachment-shopping now.)
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
