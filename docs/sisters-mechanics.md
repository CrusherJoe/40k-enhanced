# Adepta Sororitas — army mechanics reference

The Sisters-specific rules that shape list-building and mathhammer. Verified
against BSData (`Imperium - Adepta Sororitas.json`), the core rules PDF, and the
Faction Pack (`docs/adepta_sororitas_faction_pack.pdf`). Shared rules (Leaders &
Attached Units, cover, modifiers, etc.) are in `docs/core-rules-reference.md`.

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
- **Why it matters:** a Miracle 6 is a guaranteed critical hit/wound, a passed
  save, or a made charge — on demand. It converts the army's variance into
  reliability, and **rewards trading models** (dead units generate dice), which
  synergises hard with Hallowed Martyrs (below).
- Mathhammer note: the EV engine does NOT model Miracle dice (they're a discrete,
  player-timed resource). Treat them as ~a handful of guaranteed key results per
  game — most valuable spent on high-impact rolls (a Vahl/Exorcist wound, a clutch
  charge, an invuln save on a key model).

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
- **Points refinement:** Sisters MFM prices squads by model count (5/10).
