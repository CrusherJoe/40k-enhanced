# Core rules reference (11e) — mechanics the tool depends on

Verified against the official **Warhammer 40,000 Core Rules** PDF
(`docs/40k_core_rules.pdf`; section numbers cited). Captures the rules the
mathhammer/army code and list analysis rely on, so nothing is guessed from
memory. A few glossary items (notably the modifier rules) are marked **[app]** —
the PDF says that appendix is "continued in the Warhammer 40,000 app"; those
entries state the established rule and should be confirmed against the app.
(Alternative web copy, currency unknown: <https://gdmissions.app/11th/rules/core-rules>.)

## Battle round & turn structure

A **battle round** = both players take a **turn**. Games run 5 battle rounds.
Each turn has five phases, in order:
**Command → Movement → Shooting → Charge → Fight.**
Most VP is scored at the end of your turn / your Command phase (see missions).

## Command phase (01)

- **Command Points:** each player gains **1 CP** at the start of their Command phase.
- **Leadership roll (01.06):** roll **2D6**; success if ≥ a Ld characteristic in the
  unit (Ld is shown as e.g. `6+`). Used for battle-shock and some rules.
- **Battle-shock (01.07):** in the Command phase, each of your units that is
  **Below Half-strength** must take a battle-shock test (a Ld roll). Fail → the
  unit is **battle-shocked** until your next Command phase: its models' **OC
  becomes `-`** (can't control objectives), it can't use most Stratagems, and it
  uses **Desperate Escape** if it Falls Back.

## Movement phase (03, 09)

Each unit picks one move type:
- **Remain Stationary (09.04):** no move; doesn't trigger start/end-of-move rules.
- **Normal move (09.05):** up to **M"**. Must be unengaged.
- **Advance move (09.06):** **M + D6"** (roll the D6). After advancing the unit
  **cannot shoot** (unless a weapon has **[ASSAULT]**) **or charge** this turn.
- **Fall Back (09.07):** up to **M"**, only if engaged; must end unengaged. If
  battle-shocked (or you choose), **Desperate Escape**: hazard roll per model
  (each 1-2 risks losing a model). After Falling Back the unit can't shoot or
  charge unless a rule allows.

- **Coherency (03.03):** every model within **2" horizontally / 5" vertically** of
  ≥1 other model in the unit, and within **9"/5"** of every other model.
- **Engagement Range (03.04):** the area within **2" horizontally and 5" vertically**
  of a model; opposing models within it are **engaged**. (Verified 03.04 — earlier
  digest wrongly said 1"; screening/charge geometry uses 2".)
- **Strategic Reserves (20.01–04):** units set aside at Declare Battle Formations (≤50% of army pts);
  arrive **from battle round 2** via an **ingress move (20.04)** — wholly within **6" of a battlefield edge**,
  and (before round 3) **not in the opponent's deployment zone**; un-arrived reserves are **destroyed end of
  round 3**. **Rapid Ingress (15.07, core, 1CP):** ingress one reserve unit at the **end of the opponent's
  Movement phase** (reactive). **Deep Strike (24.09):** if every model has it, the unit can ingress
  **ANYWHERE** on the battlefield (not just an edge, **even inside the opponent's DZ**), set up **>8"
  horizontally** from all enemy units. **⚠ The operative number is the CHARGE: a same-turn charge out of Deep
  Strike / Rapid Ingress needs 2D6 ≥ 9 (~28%)** (user-taught 2026-07-26) — the raw set-up text reads 8", but a
  unit placed just over 8" away needs a 9 to reach Engagement Range, so DS/ingress arrivals usually **cannot
  charge on arrival**. An anti-DS bubble (Navigator Gaze, ≤12" — bigger than the 8" arrival distance) pushes
  their drop back further.

## Shooting phase (04, 10)

**Eligible to shoot if** the unit did not Advance (unless the weapon is
**[ASSAULT]**), did not Fall Back, and is not engaged — **except**:
- **[ASSAULT] (24.04):** may shoot after Advancing.
- **Close-quarters shooting (10.06):** an engaged unit may shoot **[PISTOL]/
  [CLOSE-QUARTERS]** weapons, targeting a unit it's engaged with (no [BLAST]).
- A unit can only shoot targets it can **see** (line of sight) and cannot target
  a unit it is engaged with (except close-quarters).
- **Snap shooting (15.09):** only unmodified **6s** hit; limited to one visible
  enemy within 24".

### Making an attack — the hit → wound → save → damage sequence (04, 05)

1. **Hit roll** — d6 vs the weapon's **BS** (ranged) / **WS** (melee). Unmodified
   **1 always fails**, unmodified **6 always hits** and is a **critical hit**.
2. **Wound roll** — d6 vs the S-vs-T chart: **S≥2T → 2+, S>T → 3+, S=T → 4+,
   2S≤T → 6+, else 5+**. Unmodified **6 = critical wound**.
3. **Allocate** to a model (defender's choice; a model already with lost wounds
   must be chosen first; CHARACTERs allocated last within their group).
4. **Saving throw** — d6 modified by the weapon's **AP** (AP worsens the save),
   **or** an **invulnerable save** (never modified by AP). Best save used; a **1
   always fails**.
5. **Damage** — each failed save deals **D**; **Feel No Pain** (if any) may ignore
   each lost wound.

Critical hits/wounds are still hits/wounds; abilities key off "critical" (Lethal
Hits, Sustained Hits, Devastating Wounds, Anti-).

**Fast / simultaneous rolling (07):** in each step (Hit → Wound → Save → Damage),
if there's more than one dice to roll, you **make all of those rolls at the same
time**. You cannot roll them one at a time and react between dice. This matters for
any "before you roll, substitute/modify" effect (e.g. **Miracle dice**): you must
commit it **before** the batch is rolled — you can't watch 20 shots and fix the
one that whiffed. It also caps such substitutions to one die per batch roll.

**Indirect Fire penalties (10.07):** an `[INDIRECT FIRE]` weapon shooting a target
**not visible** to it: the target has **benefit of cover**, you **can't re-roll
hits**, and **an unmodified 1–5 fails (only 6s hit)** — *unless* your unit
**Remained Stationary** this turn **and** the target is visible to one or more
friendly units, in which case 1–3 fails (4+ hits). After shooting indirectly the
unit can't start an Action. → indirect fire is unreliable without a stationary
spotter; casino weapons (variable Attacks) firing indirect are doubly swingy.

## Charge phase (11)

- Declare a charge with an eligible unit (not Advanced, not Fell Back, not already
  engaged) → select enemy target(s) **within 12"**.
- **Charge roll = 2D6** (avg 7"). The unit must be able to end **in Engagement
  Range of every** declared target and in coherency, or the charge fails.
- Opponent may respond via **Fire Overwatch (15.08)** stratagem (snap shooting —
  only unmodified 6s hit; **TORRENT auto-hits regardless**, which is why flamers
  are the premier Overwatch weapon) or **Heroic Intervention (15.11)**.
  **⚠ Fire Overwatch TARGET excludes TITANIC units** — so ALL big Imperial Knights
  CANNOT Overwatch; the unit must also be *unengaged*. (Non-TITANIC flamer armies
  like Sisters CAN, and Torrent makes it auto-hit.)
- Charging matters for **[LANCE]** (+1 wound) and Fights First.

## Fight phase (12)

- Resolve **Fights First** units first (24.13; e.g. a unit that charged, or with
  the ability), then the remaining combats **alternate**, until all eligible units
  have fought.
- **Pile-in (12.03):** up to **3"** toward the closest enemy, before attacking.
- Make melee attacks (same hit→wound→save→damage sequence, WS).
- **Consolidate (12.08):** up to **3"** after fighting, toward enemies / objectives.

## Cover & terrain (13)

**Benefit of Cover (13.08):** worsens the attacker's **BS characteristic by 1**
(numerically a −1 to hit; ranged only). A unit has it if **every** model meets one
of: (1) **INFANTRY/BEASTS/SWARM** and **within a terrain area**; or (2) **not fully
visible** to the attacker due to **intervening** terrain features / obscuring
terrain areas. Condition 2 is pervasive — cover comes from terrain the **line of
sight crosses**, not just terrain the target stands in.

- **Obscuring (13.10):** any terrain area with a **light or dense** feature is
  obscuring (grants cover). **Solid (13.11):** **dense** features also block line of
  sight at ≤3" from ground level.
- **Hidden (13.09):** an **INFANTRY/BEASTS/SWARM** model in a terrain area with a
  **dense** feature, whose unit **did not make ranged attacks this or the previous
  turn**, is hidden — **not visible** to enemies beyond its **detection range**
  (default **15"**; "unless otherwise stated", so enemy abilities can modify it).
- **Gone to Ground** [app / user-supplied]: while a model is **hidden**, **obscured
  by intervening dense terrain**, and its unit **didn't shoot this or last turn**,
  its detection range is **−3" (→ 12")**. Shooting (this or last turn) breaks it.
- **Detection range — what it blocks:** being beyond it makes the model "not
  visible", so it can't be targeted by **direct fire** (snipers included). It does
  **NOT** stop **Indirect Fire** (10.07 explicitly targets non-visible units) — but
  vs a target no friendly can see, Indirect Fire hits **only on unmodified 6s** and
  the target has **benefit of cover**, so it's practically negligible. Combined with
  an anti-Reinforcements bubble (e.g. the Navigator's Gaze, ≤12"), a hidden +
  gone-to-ground sitter is near-unremovable — see `data/allies/agents.yaml`.
- **`[IGNORES COVER]` (24.18)** removes benefit of cover, including from rules that
  grant it (e.g. **Stealth (24.33)**, which gives a unit benefit of cover). Only
  Ignores Cover or breaking the line-of-sight condition beats cover.
- **Standard event board:** 16 obscuring terrain areas on 44"×60" — cover is the
  default for most ranged attacks (see `data/layouts/`).

### ⚠ Modifiers — characteristic vs dice roll **[app]**

Two DISTINCT kinds of modifier (the glossary is continued in the app; this is the
established rule):
- **Dice-roll modifiers** apply to the die **result** after rolling; the total to a
  single roll is **capped at ±1**. Examples: Dominus Foebreakers "+1 to Hit rolls",
  [HEAVY] +1, an enemy "-1 to Hit rolls" aura.
- **Characteristic modifiers** apply to the **characteristic** (target number)
  **before** rolling; they are **not** subject to the ±1 roll cap and are a
  different category. Examples: **cover** (worsen BS by 1) and **Plunging Fire**
  (improve BS by 1).

Consequence: an ability that ignores "modifiers to the **Hit roll**" (Gate
Warden's *Against the Horde*) does **NOT** remove cover, which is a **BS
characteristic** modifier. Numerically a +1-Hit-roll bonus still offsets cover's
−1 for the affected shots, but as a separate modifier, not by "ignoring" it.

### Plunging Fire (TOWERING)

A **TOWERING** attacking model (all Knights are TOWERING), **or** any model on a
terrain feature **3"+ high**, shooting a target **within 12"** that contains
**ground-level** models, **improves the BS characteristic of those attacks by 1
(+1 BS)**. Because it's a **characteristic** modifier, it **directly offsets
cover's −1 BS** — so a Knight shooting a ground-level target within 12" negates
cover at the characteristic level (net 0 before other modifiers).

## Objectives & scoring

- **Objective markers** are flat **circular 40mm** markers; a model is **within
  range** while within **3" horizontally and 5" vertically**; measure to/from the
  **closest part**.
- You **control** an objective if the **total OC** of your models within range
  **exceeds** the enemy's total OC there. Battle-shocked models have OC `-`.
- Knights have high OC (10; damaged −5) but are few — the body/OC tradeoff drives
  list design (see MEMORY / disposition analysis).

## Core unit abilities (24) — as they affect Knights

| Ability | § | Effect |
|---|---|---|
| **Deadly Demise X** | 24.08 | when the model is destroyed, roll a D6; on a **6**, each unit within **6"** suffers **X** mortal wounds (X often D3/D6/2D6). |
| **Deep Strike** | 24.09 | set up from reserves >9" from enemies (via ingress). |
| **Benefit of Cover** | 13.08 | −1 to hit; unit qualifies if EVERY model is INFANTRY/BEASTS/SWARM in a terrain area OR **not fully visible** behind intervening/obscuring terrain. Knights (VEHICLE) don't get it from the 1st clause, but DO from the 2nd — ruin walls clip the Towering silhouette → cover is EASY for Knights (user-confirmed). |
| **Hidden** | 13.09 | INFANTRY/BEASTS/SWARM in DENSE terrain that didn't shoot this/last turn → only targetable within **detection range (15")**. Knights can't be Hidden (VEHICLE); Terminators/Sisters can. |
| **Gone to Ground** | 13.11.01 [app] | a HIDDEN model also not-fully-visible behind **dense** terrain, whose unit didn't shoot this/last turn → **−3" detection range** (15→12"). Passive (not an action); INFANTRY-only. Shooting this/last turn disqualifies it regardless of shoot-and-stay-hidden abilities. |
| **Obscuring** | 13.10 | if every LOS between two models crosses an obscuring area (that neither is within), they're not visible = can't target. |
| **Plunging Fire** | 22.05 | +1 BS if attacker is on terrain ≥3" tall OR is TOWERING and target within **12"** (so useless for a long-range gunline). |
| **Engagement Range** | 03.04 | within **2" horizontal / 5" vertical** — the number screening hangs on. |
| **Terrain & movement** | 13.06 | VEHICLES/MONSTERS (Knights) can't move THROUGH dense terrain >2" tall (go around); INFANTRY move through freely. |
| **Feel No Pain X+** | 24.12 | each lost wound: roll D6, on **X+** it is not lost (applies to mortal wounds too). |
| **Fights First** | 24.13 | fights in the Fights First step (before normal combats). |
| **Super-Heavy Walker** | 24.35 | On a normal/advance/**fall-back** move: move THROUGH models (excl TITANIC) + horizontally through terrain ≤4" tall; optional MOBILE for the move (battle-shock on a 1). **Movement only — does NOT grant fall-back-and-shoot.** BIG Knights only (Questoris/Cerastus/Dominus); **ARMIGERS have plain WALKER, not this.** No Knight can fall back and still shoot. |
| **Lone Operative** | 24.24 | not visible/targetable beyond 12" (some Armigers/characters). |
| **Stealth** | 24.33 | the unit has **benefit of cover** vs ranged attacks (−1 to be hit). |
| **Scouts / Infiltrators** | 24.31/24.20 | pre-game move / deploy 9"+ from enemies. |
| **Hover** | 24.17 | aircraft can move like a normal unit. |

**Mortal wounds:** inflicted one at a time, spilling within the unit; **bypass
saves**; **lost** if the unit is destroyed with wounds to spare; **FNP can apply**.

## Leaders, Support & Attached Units (19) — central to Sisters

- **Leader / Support (24.22 / 24.34):** a unit whose datasheet has the **Leader**
  or **Support** ability can, in the **Muster Armies** step, be attached to one
  friendly **bodyguard** unit it's allowed to lead (the legal bodyguards are listed
  per character). They form an **attached unit** — a single unit for all rules.
- A bodyguard unit can have **one Leader AND one Support** attached (so a squad can
  carry two characters). The character's aura/abilities then apply to the whole unit.
- **Defence (19.02):** when the attached unit is attacked, use the **highest T of
  the bodyguard models** — the character shelters behind the squad's toughness.
  Destroyed-triggers fire only when the **last** model of the attached unit dies,
  so characters are hard to pick out.
- **List-building consequence:** buffs are delivered by stapling the right
  character(s) to the right squad. This is a core lever for Sisters (Knights barely
  used it) — see `docs/sisters-mechanics.md`.

## Bondsman (Imperial Knights army rule)

Bondsman abilities are conferred by the big/Titanic Knights **onto friendly
ARMIGER models** — the Armiger is the recipient, the big Knight is the source. A
big Knight never benefits from its own Bondsman ability (e.g. the Cerastus
Lancer's "charge after Advancing" buffs a nearby Armiger, not the Lancer).

## Weapon abilities (section 24) — as modelled by mathhammer

| Ability | § | Effect |
|---|---|---|
| `[ANTI-X N+]` | 24.03 | vs a target with keyword X, an unmodified wound roll of N+ is a **critical wound**. |
| `[ASSAULT]` | 24.04 | can be fired even if the unit Advanced. |
| `[BLAST]` | 24.05 | +1 attack per **5 models** in the target; can't target a unit you're engaged with. |
| `[DEVASTATING WOUNDS]` | 24.10 | on a **critical wound**, the sequence ends and the target takes **mortal wounds = the D** (bypasses saves). **Critical wound = an unmodified 6 (16.7%) UNLESS a matching `[ANTI-X N+]` lowers it — and that only fires vs a target with keyword X.** So Dev Wounds do NOT bypass a non-matching invuln reliably (e.g. `[ANTI-TITANIC 4+]` does nothing vs a C'tan — a MONSTER, not TITANIC; Dev then triggers on 6 only). |
| `[HEAVY]` | 24.16 | +1 to the **Hit roll** if the unit was unengaged and **Remained Stationary**. |
| `[IGNORES COVER]` | 24.18 | target cannot have benefit of cover. |
| `[LANCE]` | 24.21 | **+1 to wound** if the unit **charged** this turn. |
| `[LETHAL HITS]` | 24.23 | a **critical hit** automatically wounds. |
| `[MELTA X]` | 24.25 | **+X Damage** at half range. |
| `[RAPID FIRE X]` | 24.30 | **+X attacks** at half range. |
| `[SUSTAINED HITS X]` | 24.36 | a **critical hit** scores **X extra hits**. |
| `[TORRENT]` | 24.37 | **auto-hits** (no hit roll — cover's −1 BS is moot). |
| `[TWIN-LINKED]` | 24.38 | **re-roll the wound roll**. |

## EV model simplifications (`src/wh/mathhammer.py`)

Works in expected values; ignores wound-pool spillover across models, per-model
damage waste, HAZARDOUS self-damage, and Indirect Fire's shooter-side penalties.
Cover is lumped into the hit modifier (exact for the common cases; the rare stack
of cover + multiple Hit-roll debuffs, where the roll cap wouldn't apply to cover,
is not separately modelled). Plunging Fire is not auto-applied (pass `--hit 1`
when a Knight shoots a ground-level target within 12").
