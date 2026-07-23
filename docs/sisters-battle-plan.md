# Adepta Sororitas — battle plan (all-comers list, mathhammer-backed)

Companion to `examples/best-sisters-allcomers.yaml` (v2). Every number here is
from the mathhammer engine (`wh damage` / `src/wh/mathhammer.py`) modelling the
FULL chain — hit (incl. cover = −1 to hit), wound, save (armour + invuln).

## The core idea: soften, then delete
Naked Sisters melta into cover is *useless* — Vahl+Paragons do only **~4.6 dmg**
to a Land Raider at BS3+ into cover. The list wins by **softening a target
first**, army-wide, then shooting it with buffed melta:

| Step | Source | Effect |
|---|---|---|
| 1. Strip cover | **Immolator — Purge & Cleanse** (auto-hits w/ Immolation Flamers) | target loses Benefit of Cover for the whole army's shooting |
| 2. Improve AP | **Castigator — Rites of Castigation** | +1 AP for every Sororitas gun into that target |
| 3. Buff the shooter | **Vahl** (re-roll hits+wounds) + **Righteous Purpose** (+1 BS on Paragons) | near-auto-hitting, re-rolling melta |
| 4. Cover-immune backup | **Palatine + Triptych of Judgement** on the MM Retributor | that unit ignores cover on its own → frees an Immolator's strip |

**Result: Vahl+Paragons alone do ~17.8 to a softened Land Raider (one-shots 16W);
the full melta suite is ~45 on one target — 3× overkill.** So spread melta across
2–3 targets, never dogpile.

## Mathhammer cheat-sheet (buffed = softened target)
| Shooter (buffed) | vs Land Raider T12/2+ | vs Monolith T13/2+ | vs Deathwing 2+/4++ |
|---|---|---|---|
| Vahl+Paragons (6 MM) | **17.8** (kills) | 17.8 (81%) | 14.3 (71%, ~3.5 Termies) |
| + MM Retributor (8) + 1 Dominion (4) | overkill | **kills** | brick dead |
| **C'tan T11/3+/4++** | 8.9 even fully buffed (56%, *before* its damage cap) → **don't bother; play the mission** |

| Anti-horde vs 20 Ork Boyz (T5 W1 5+) | dead/turn |
|---|---|
| Castigator battle cannon (Ignores Cover) | 14.6 |
| 2× Immolation Flamers | 7.8 |
| 1 Dominion (4 flamers) | 4.7 |
| Heavy-bolter Retributor (12 shots) | 6.7 |
| Zephyrim (4 hand flamers) | 3.1 |
| **≈ 37 dead Boyz/turn** — enough to break blobs off objectives |

## Attachment map (Leader + Support per unit, 19.01)
- **Vahl → Paragon Warsuits** — re-roll hits & wounds + Righteous +1 BS. The hammer.
- **Palatine [Triptych] + Imagifier → Multi-melta Retributor** — Lethal Hits +
  cover-immune + **Sv 2+/4++**. A durable, reliable 2nd anchor-killer.
- **Canoness [Sanctified Amulet] + Dogmata → Celestian Sacresants** — anti-Deep-Strike
  bubble + **+1 OC** on a 4++ / Holy-Quest (+1 BS/WS) mid-board holder.

## Per-turn shooting sequence
1. **Immolators shoot first** (Immolation Flamers auto-hit) → strip cover from your
   two priority targets. 2. **Castigator** shoots → mark the single most important
   target for +1 AP. 3. **Vahl+Paragons** delete anchor A. 4. **MM Retributor (+ a
   melta Dominion)** delete anchor B. 5. **Flamers/heavy bolters/jump** clear chaff
   and screen. Save Miracle dice / an Act of Faith (Dialogus-style guaranteed 6 if
   fielded) for a clutch melta *wound* on a high-T target (wounds T12+ on 5s).

## Per-archetype game plan
- **Salamanders flamer-brick (2× Land Raider):** strip + AP a Land Raider, delete it
  with Vahl+Paragons; the other with MM Retributor + melta Dominion. Do NOT flamer-duel
  the Infernus wall — screen with Battle Sisters, counter-charge with Zephyrim, out-position.
- **Ork Kult-of-Speed:** melta the Kill Rigs/Wazdakka; **respect their anti-tank rokkits —
  keep Immolators hull-down / behind terrain until they strike**. Contest their fast
  objective play with jump units + OC bodies.
- **Ork Green Tide (100 Boyz):** this is the flamer game — Castigator + 2 flamer Immolators +
  flamer Dominion + heavy bolters ≈ 37 dead/turn; **kill whole units to break OC**, screen
  your backfield, never get bogged in melee. Sacresants (4++) + Battle Sisters hold the line.
- **Necron Monolith / C'tan:** **do not try to table them.** One softened Monolith is killable
  (Vahl+Paragons + support); C'tan are not — ignore them, kill the killable enablers
  (Reanimator, Lokhust, Lychguard, characters) and **win on primary/secondary + OC**.
- **DA Deathwing bricks (OC1):** **out-OC them** — flood objectives with Battle Sisters /
  Sacresants / Dominion-on-foot bodies; the bricks can't hold everything. Screen the
  Deep Strike with the **Sanctified Amulet** bubble. Melta still works on W4 Terminators
  (multi-damage past the 4++) — chip a brick down, but win on points.

## The through-line
Sisters win the **mission**, not the slugfest. Melta is a *scalpel* (softened anchors,
not spam); flamers/blast clear the hordes; cheap OC + jump win the board; the un-killable
gets ignored. Transports are expendable delivery — extract value before they pop.
