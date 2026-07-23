# Adepta Sororitas — army mechanics reference

The Sisters-specific rules that shape list-building and mathhammer. Verified
against BSData (`Imperium - Adepta Sororitas.json`), the core rules PDF, and the
Faction Pack (`docs/adepta_sororitas_faction_pack.pdf`). Shared rules (Leaders &
Attached Units, cover, modifiers, etc.) are in `docs/core-rules-reference.md`.

## Combat fundamentals — the three things that decide a Sisters list

These override "cool unit" instincts. Ingested from BSData weapon/stat profiles.

### 1. AP is KING — the AP cliff

An unsaved wound is worth many saved ones. Sisters weapons fall into hard tiers;
build around the top, treat the bottom as chaff-clearing only:

| AP | Weapons | Verdict |
|---|---|---|
| **-4** | **Meltagun, Multi-melta, Inferno pistol** (S8-9, Melta 2, D6/D3) | **Premium.** Vs 3+ save = no save at all. The soul-leaving-the-body weapon. Melta 2 → +2 dmg within half range. |
| **-3** | Exorcist ML, Hunter-killer, Plasma (supercharge) | Strong but: Exorcist = casino + indirect nerf; plasma Hazardous kills its own bearer. |
| **-2** | Melta missile, Paragon launchers, Plasma (standard), Ardent Blade | Solid workhorse AP. |
| **-1** | **Heavy bolter, Heavy flamer, Immolation flamers, Castigator guns** | Marks a save. Volume/Sustained Hits matter here. |
| **0** | **Flamer, Boltgun, Storm bolter, Bolt pistol** | **Opponent gets full save.** Flamers auto-hit (Torrent, Ignore Cover) but AP0 = they *save*. Good vs hordes/no-cover chaff, weak vs anything with armour. |

**Implication:** "put melta everywhere you can" is not just habit — it's the AP argument.
Flamers earn a slot for *auto-hit reliability vs swarms / on overwatch*, not for damage
through armour. **Don't mix in a unit** — an all-melta Dominion squad concentrates AP-4;
a mixed squad dilutes it and wastes the transport slot.

### 2. GIRLS DIE. A LOT. — the glass-cannon durability table

The crux. Core infantry are **T3 W1 Sv3+** — they evaporate to bolters, chainswords,
stiff breezes. Every point of the roster's durability (from the ingest):

| Body | T | W | Sv | Inv | Reality |
|---|---|---|---|---|---|
| Battle Sisters / Dominions / Retributors / Novitiates | 3 | 1 | 3+ | 6+ (Shield of Faith) | Die to *anything*. 6++ is nearly nothing. |
| Seraphim / Zephyrim | 3 | 1 | 3+ | 5+ | Jump = delivery, still 1 wound. |
| Sacresants | 3 | 1 | 3+ | **4+** | The one *durable* Battle line body — 4++ + Ld buffs. |
| Characters (Canoness/Palatine/Dogmata/…) | 3 | 3-4 | 3+ | 4+ | Fragile — must hide in a squad (Leader) or they get sniped. |
| Paragon Warsuits | 7 | 4 | 2+ | 4+ | The durable hammer. 3 models, 12 W, 2+/4++. |
| Junith / Vahl / Celestine / Triumph | 5-7 | 8-18 | 2+ | 4+ | Genuinely tanky centrepieces. |
| Immolator / Castigator / Exorcist / Rhino | 9-10 | 10-11 | 3+ | — | Vehicles; the Immolator doubles as ablative delivery. |

**Implication:** the game is *delivery and durability*, not aggression. Walking T3 W1
bodies up the board = handing the opponent free Miracle dice (1 per unit *you* lose —
cold comfort). Favour: transports (ablative wounds + speed), Sacresants/Paragons where
you need a body that survives, and killing *their* stuff before it shoots back. An
all-in aggressive flamer gunline (Bringers/Purge) walks the fragile bodies into their
own graves — the reason to be sceptical of the "obvious" hyper-aggressive build.

### 3. Transports are hard constraints — and the split

- **Immolator = 6** ADEPTA SORORITAS INFANTRY (no JUMP PACK). **Rhino = 12** INFANTRY.
- **The split:** Battle Sisters & Dominion squads deploy as **two 5-model halves** — put
  the "good half" (all-melta + the Superior) in the **Immolator**, leave the other 5 on
  foot / objective-sitting. This is the standard mobile-melta delivery: a 5-melta Dominion
  half + Superior rides the Immolator (fits in 6), pops out at half-range for AP-4 Melta 2.
- **Retributors = 5 models** (4 + Superior) → fit an Immolator whole (4 heavy weapons).
- **Paragons = 3**, Seraphim/Zephyrim/Sacresants = 5-10, characters count against capacity.
- **Match the passenger to the hull before you fall in love with a combo** — a full
  10-model squad + a character does *not* fit an Immolator; it needs a Rhino (and even
  then 12 is the ceiling, characters included).

## Acts of Faith & Miracle Dice (the army rule)

The signature mechanic — a pool of **pre-rolled dice you substitute on demand**
for reliability and clutch moments.

- **Gaining Miracle dice:** you gain **1 at the start of each battle round**, and
  **1 each time an ADEPTA SORORITAS unit is destroyed** (yours). Roll a D6 for each
  — that fixed value is the die (can't be changed/re-rolled unless a rule says).
  Keep them in your **Miracle dice pool**.
- **Performing an Act of Faith:** *before* making a dice roll for a unit with the
  **Acts of Faith** ability, substitute one Miracle die from the pool for that roll
  — its value is used **as an unmodified roll of that value**. Multi-die rolls
  (Charge, Battle-shock) → substitute **one** die, roll the rest. Each die is used
  once. Valid rolls: **Advance, Battle-shock, Charge, Damage, Hit, Save, Wound.**
- **One Act of Faith per unit per phase** (→ **two** with the Army of Faith
  detachment's *Sacred Rites* rule).
- **⚠ FAST-ROLLING DEVALUES THEM (11e).** You must substitute the Miracle die
  **before** the roll, and identical attacks are **fast-rolled as one batch**
  (all Hits together, all Wounds together — core rules 07). So you commit **one**
  die **up front** and can't react to results — you can't watch a unit's shots
  and rescue the one crit that missed. Net: a Miracle die guarantees **one** die's
  worth at a chosen value, committed blind. That makes them **much weaker than a
  reactive substitution** would be.
- **Best uses (given the above):** a **single high-value roll** — a single-shot
  weapon's Hit or Wound (multi-melta/las), a **save on a key model**, a **Charge**
  or **Advance** roll, a **Battle-shock** test. Poor value spread over high-volume
  shooting (one guaranteed hit among 20 is marginal).
- **Generation is low** (1/round + 1 per own unit destroyed), so **you rarely have
  enough dice to exploit "two Acts of Faith per phase" (Army of Faith / Sacred
  Rites)** — that rule is over-rated for it. Don't build around double-AoF.
- Mathhammer note: the EV engine does NOT model Miracle dice — treat them as ~a
  handful of guaranteed *single* key results per game.

## Detachments (8) — rules summary (all apply army-wide, even in a 2+1 mix)

| Detachment | DP | Disposition | Rule (gist) |
|---|---|---|---|
| **Hallowed Martyrs** | 3 | Priority Assets | *Blood of Martyrs*: +1 Hit while a unit is **below Starting Strength**, +1 Wound too while **below Half-strength** — rewards taking casualties (and each dead unit = a Miracle die). |
| **Bringers of Flame** | 3 | Purge the Foe | *Fervent Purgation*: all SORORITAS ranged weapons gain **[ASSAULT]**; **+1 Strength** vs targets within **6"**. Aggressive flamer/close-range gunline. |
| **Champions of Faith** | 2 | Disruption | *Righteous Purpose*: pick up to 3 units → **Righteous** (+1" Move, +1 Ld, and **+1 WS/BS** for Battle Sisters / Celestian Sacresants / Paragon Warsuits). |
| **Army of Faith** | 2 | Take and Hold | *Sacred Rites*: **two Acts of Faith per unit per phase** — doubles your Miracle-dice throughput. |
| **Penitent Host** | 2 | Take and Hold | *Desperate for Redemption*: choose a **Vow of Atonement** each round; buffs **PENITENT** models (extra Move / Attacks+Strength on the charge / etc.). |
| **Chorus of Condemnation** | 1 | Reconnaissance | *Angelic Judgement* (1DP support detachment). |
| **Sanctified Orators** | 1 | Purge the Foe | *Hymns of Battle* (minimal 1DP; 1 enhancement, no stratagems). |
| **Sacred Champions** | 1 | Take and Hold | *Holy Quest* (1DP support detachment). |

Full rule/enhancement/stratagem text is in `data/detachments/adepta-sororitas.yaml`.
**Rich combo space** (see `wh --faction sisters plan`): the three 1DP detachments
unlock the 2DP ones, so you can reach **any of the 5 dispositions**, and — as with
Knights — **all your detachments' rules stack army-wide**. This matters far more
for Sisters: e.g. Army of Faith (double Acts of Faith) + a 1DP detachment gives
you both that detachment's rule AND double Miracle throughput.

## KEYWORDS gate the buffs — read them carefully

Detachment rules and buffs frequently apply only to models with a **specific
keyword or unit name**, not the whole army:
- *Righteous Purpose* improves WS/BS only for **Battle Sisters Squad, Celestian
  Sacresants, Paragon Warsuits** (not everything).
- *Desperate for Redemption* buffs only **PENITENT** models.
- Some detachments/enhancements **grant** a keyword to widen who benefits (e.g. an
  enhancement: "the bearer gains the **PENITENT** keyword"). So keyword-granting is
  a deliberate lever — you can pull a non-Penitent character into the PENITENT buffs.

When evaluating a detachment for a unit, always check: does the buff key off a
keyword/unit-name my unit actually has?

## Leaders & Support — the buff-delivery system

(General rule in `core-rules-reference.md`.) Sisters lean on this heavily. A squad
can carry **one Leader + one Support**; the characters' auras apply to the whole
attached unit and they shelter behind the squad's Toughness.

- **Support characters → Battle Sisters Squad:** Dialogus, Dogmata, Hospitaller,
  Imagifier (each buffs the squad it joins — Ld/Sacred-Rites/heal/Miracle-dice utility).
- **Leader characters** attach to core squads (Battle Sisters / Celestian Sacresants
  / Dominion / Retributor / Novitiate): Canoness, Palatine, Junith Eruita, etc.
  (full bodyguard mapping is a refinement pass — pull each character's Leader ability.)
- **Reliquant Knight → Paragon Warsuits.** **Saint Celestine, Morvenn Vahl,
  Triumph of St Katherine** are their own high-impact pieces.

## Open items / TODO
- **Cross-check detachment stratagems vs the Faction Pack Rules Updates** — the FP
  revises several (Army of Faith's Light of the Emperor → 2CP and Blinding Radiance;
  Hallowed Martyrs' Suffering & Sacrifice and Divine Intervention — the latter
  *resurrects a destroyed CHARACTER* by discarding 1–3 Miracle dice). My 39k text
  may be pre-update.
- **Full Leader→bodyguard mapping** for the codex characters (Canoness/Palatine/
  Junith/Dogmata/etc.).
- ~~Points refinement: Sisters MFM prices squads by model count (5/10).~~ **DONE** —
  datasheets carry MFM `sizes: {models: points}` + per-model weapon taxes; list
  entries specify `models: N`; the engine prices exactly. Units are **5 or 10 only**.
  **Always defer to MFM for points.** (Open: confirm Dominion 10-model cost — used
  180 by inference; 5-model = 90 is MFM-clean and what the list uses.)
