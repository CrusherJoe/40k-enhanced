# Core rules reference (11e) — mechanics the tool depends on

Verified against the official **Warhammer 40,000 Core Rules** PDF
(`docs/40k_core_rules.pdf`; section numbers below). This captures only the rules
the mathhammer/army code relies on, so the engine isn't guessing from memory.
(An alternative, possibly-less-current web copy: <https://gdmissions.app/11th/rules/core-rules>.)

## Making an attack (the hit → wound → save → damage sequence)

1. **Hit roll** — d6 vs the weapon's BS (ranged) / WS (melee). Unmodified 1 always
   fails, unmodified 6 always hits and is a **critical hit**. Modifiers to the hit
   roll are capped at ±1 total.
2. **Wound roll** — d6 vs the S-vs-T chart: S≥2T → 2+, S>T → 3+, S=T → 4+,
   2S≤T → 6+, else 5+. Unmodified 6 = **critical wound**. Modifiers capped ±1.
3. **Saving throw** — target rolls d6, modified by the weapon's **AP** (AP worsens
   the save), or uses an **invulnerable save** (never modified by AP). Best
   available save is used. A save of 1 always fails.
4. **Damage** — each failed save deals the weapon's **D**; **Feel No Pain** (if any)
   rolls to ignore each lost wound.

## Cover — 13.08  (⚠ changed from 10e)

> "Each time a ranged attack targets a unit that has the benefit of cover against
> it, **worsen the BS characteristic of that attack by 1**."

Cover is a **−1 to HIT**, not a save bonus. Ranged attacks only. `[IGNORES COVER]`
(24.18) removes it, "including from rules that give a unit the benefit of cover
(e.g. **Stealth**)" — so in 11e **Stealth grants benefit of cover** (−1 to be
hit), and Ignores Cover cancels that too.

**A unit has benefit of cover if EVERY model in it meets one or more of:**
1. has **INFANTRY / BEASTS / SWARM** and is **within a terrain area**, OR
2. is **not fully visible** to the attacker due to **intervening** terrain
   features / obscuring terrain areas.

Condition 2 is the pervasive one: cover is granted by terrain the **line of
sight crosses**, not just terrain the target stands in. So vehicles, monsters
and anything shooting *across* the board get cover routinely.

**Obscuring (13.10):** a terrain area containing **any light OR dense** feature
is obscuring. **Solid (13.11):** dense features additionally block line of sight
at ≤3" from ground level. So light vs dense both grant cover (obscuring); only
dense also blocks LoS.

**Standard event terrain manifest (Event Companion) — the same on every layout:**
**16 terrain areas** on the 44"×60" board — 4×(6"×4"), 2×(10"×2.5"), 4×(6"×2"),
4×(7"×1.5"), 2×(8"×11.5" polygon), each dense or light per the specific layout.
With 16 obscuring areas scattered about, **most ranged attacks at range draw a
line through terrain → the target has cover → −1 to hit.** Cover is the default,
not the exception, and this is army-agnostic.

**Interaction with Dominus Foebreakers (Rain of Devastation):** that rule gives
+1 to hit only vs a unit **in a terrain area** (cover condition 1, mostly
infantry). It does **NOT** offset cover from condition 2 (a target obscured by
*intervening* terrain while not standing in it) — the common case for
non-infantry. So `[IGNORES COVER]` (e.g. Judicant's Helm) is broadly valuable
even in a Dominus list; the detachment rule does not make it redundant.

## Weapon abilities (section 24) — as modelled

| Ability | § | Effect (verified) |
|---|---|---|
| `[ANTI-X N+]` | 24.03 | vs a target with keyword X, an unmodified wound roll of N+ is a **critical wound**. |
| `[ASSAULT]` | 24.04 | can be fired even if the unit Advanced this turn. |
| `[BLAST]` | 24.05 | +1 attack per **5 models** in the target unit; can't target a unit you're engaged with. |
| `[DEVASTATING WOUNDS]` | 24.10 | on a **critical wound**, the sequence ends and the target suffers **mortal wounds = the D characteristic** (bypasses saves). |
| `[HEAVY]` | 24.16 | +1 to hit if the unit is unengaged and **Remained Stationary** this turn. |
| `[IGNORES COVER]` | 24.18 | target cannot have benefit of cover against the attack. |
| `[INDIRECT FIRE]` | 24.19 | can target units not visible (with a hit penalty + cover vs the shooter — not modelled in EV). |
| `[LANCE]` | 24.21 | **+1 to wound** if the attacking unit **made a charge move** this turn. |
| `[LETHAL HITS]` | 24.23 | a **critical hit** automatically wounds. |
| `[MELTA X]` | 24.25 | **+X to Damage** if the target is within half range. |
| `[PRECISION]` | 24.28 | (attacker allocates to a CHARACTER — not damage-relevant to EV). |
| `[RAPID FIRE X]` | 24.30 | **+X attacks** if the target is within half range. |
| `[SUSTAINED HITS X]` | 24.36 | a **critical hit** scores **X additional hits**. |
| `[TORRENT]` | 24.37 | **auto-hits** (no hit roll — so cover's −1 BS is irrelevant). |
| `[TWIN-LINKED]` | 24.38 | **re-roll the wound roll**. |

Critical hit/wound default to an **unmodified 6** unless an ability lowers the
threshold (Anti). Mortal wounds and normal damage are both reduced by FNP.

## Notes / EV simplifications

The engine (`src/wh/mathhammer.py`) works in **expected values**, so it does not
model wound-pool spillover across models, per-model damage waste, HAZARDOUS
self-damage, or Indirect Fire's shooter-side penalties. It is built for
**comparing** weapons and units, which is what list analysis needs.

## Bondsman (Imperial Knights army rule)

Bondsman abilities are conferred by the big/Titanic Knights **onto friendly
ARMIGER models** — the Armiger is the recipient, the big Knight is the source. A
big Knight never benefits from its own Bondsman ability (e.g. the Cerastus
Lancer's "charge after Advancing" buffs a nearby Armiger, not the Lancer).
