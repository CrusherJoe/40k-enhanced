# Imperial Knights — matchup battle plans vs the boogeyman meta

For the two lists taken forward — **C (Horde-Hardened)** and **A (Lancer
Aggressive)**. Both **LOCK Purge the Foe** (Knights can't play the action game;
"kill + hold-with-OC10" is their lane). Missions verified from `data/missions.yaml`;
deployment from `data/layouts/purge-the-foe.yaml` (already ingested); damage from
the bidirectional mathhammer.

> **Why Purge, re-confirmed vs the meta:** every alternative disposition wants
> Objective Actions and board-spread that a 6-8 model army can't spare. Purge
> rewards the two things Knights actually do — **kill** (vehicles/monsters die to
> S18/S24 guns) and **hold with OC10 while shooting**. Deployment layouts for the
> Purge player are in the layout file.

## Mission — set by the OPPONENT's disposition (you're locked Purge)
| Opponent disposition | Your mission | Shape |
|---|---|---|
| Take-and-Hold (Green Tide, Deathwing) | **Unstoppable Force** | 3/kill + 4/obj + 5/central + 3/newly-taken |
| Disruption (Monoliths, Ork Kult) | **Punishment** | 5/condemned-leaves + hold + **8 for their home** |
| Purge the Foe (C'tan, Salamanders*) | **Meatgrinder** | 3/kill + 5/kill-more-than-lost + 5/their home |
| Reconnaissance (Salamanders*, C'tan*) | **Consecrate** | consecrate objs (ACTION) + hold — *needs actions; weak for Knights* |

\* dual-disposition detachments pick one; plan for both.

## Universal Knights deployment (both lists)
- **Big Knights hold the centre & mid objectives** — 72"/48" guns dominate the board,
  and OC10-while-shooting means a single 400-pt Knight *holds an objective and fires*.
  The board centre is packed with obscuring terrain (no turn-1 cross-board LOS) → advance
  to open firing lanes turn 1.
- **Navigator on the home objective** — Hidden + the anti-Deep-Strike bubble make it
  near-unremovable (immune to sniping + deep strike; only a ground assault shifts it).
  It frees an Armiger to push. It must NOT shoot, and needs a dense terrain piece.
- **Armigers screen + flank** — block charges/deep strikes near the big Knights, contest
  expansion objectives, and add anti-horde (Warglaive sweeps) / anti-elite (Helverin).
- **Layout note (Purge player):** vs Take-and-Hold & Disruption, Layout A is diagonal
  (long approach — your guns love it); vs Reconnaissance, Layout A is horizontal (close);
  Layout letters vary — read the one you're given (`data/layouts/purge-the-foe.yaml`).

## Per-archetype plans (C = Horde-Hardened, A = Lancer Aggressive)
### Salamanders flamer-brick — you play Consecrate (vs Recon) or Meatgrinder (vs Purge)
- **Targets:** delete the 2 Land Raiders turn 1-2 (Volcano/harpoon/thermal/spears one-shot
  or two-shot them), then Aggressors/Bladeguard with Avenger + sweeps. Knights are tanky
  vs pyreblasters (T9-13 shrugs S5 AP-1). **Both lists crush this.** A's Lancer can dive the
  Infernus/characters; C's flamers out-attrition the wall.

### Ork Kult of Speed (dakka) — you play Punishment
- **Targets:** anti-tank the Kill Rigs + Wazdakka; **Avenger + sweeps for the Deffkoptas/
  Flash Gitz** (T5-6 → volume, not Volcano waste). Grab their home (8 VP) — they're fast but
  fragile. **A is best here** (Lancer M14 catches the fast units; run them down).

### Ork Green Tide (100 Boyz) — you play Unstoppable Force  ★ the test
- **Targets:** this is the anti-horde game. **C is the answer** (Valiant Conflagration +
  Warden Avenger+Heavy Flamer + Crusader Avenger + 3 Warglaive sweeps ≈ 35+ Boyz/turn vs
  A's ~23). Save the harpoon/Volcano for **Ghazghkull**. **Hold objectives with OC10 Knights**
  (Boyz can't shift a 400-pt Knight fast) and **screen the charge with Armigers** — you won't
  table 100 Boyz, so win Unstoppable Force on kills + holding while grinding the tide.

### Necron Monoliths (3× T13, OC8, slow) — you play Punishment
- **Targets:** unlike Sisters, **Knights KILL Monoliths** — Volcano (S18) wounds T13 on 3+,
  the Thundercoil harpoon (S24 AP-6 D10) deletes one. **Focus-fire one Monolith down/turn.**
  They're M8" and OC8 — grab **their home (8 VP)** and objectives they can't reach while you
  dismantle them. **A** (Volcano + Lancer) has the most single-target punch; **C** (harpoon)
  also cracks them.

### Necron C'tan (4× T11, −1 Damage) — you play Meatgrinder (vs Purge) or Consecrate (vs Recon)
- **Targets:** you can't table 4 C'tan (7-8 dmg each even with big guns; 4++ + −1 Damage).
  **Use VOLUME (Avenger), not Volcano** (AP-5 wasted on the 4++). Kill the **killable enablers**
  (Lokhust, Lychguard, Reanimator, characters). Meatgrinder rewards kill-differential — farm the
  support, don't feed the C'tan, grab their home. **C/A** (Avenger volume) beat B here.

### Dark Angels Deathwing (2+/4++ bricks, OC1) — you play Unstoppable Force
- **Targets:** the bricks are W4 — **Avenger + sweeps are efficient; Volcano/harpoon is overkill
  waste.** Chip a brick when it's exposed, but the win is **out-holding OC1 bricks**: your OC10
  Knights + Armigers take more objectives than three OC1 bricks can. **Screen the Deep Strike**
  (Navigator bubble + Armigers). **C/A** both fine; C's screens deny the teleport best.

## The C-vs-A one-liner
- **C (Horde-Hardened)** — strongest vs the two matchups that actually beat Knights (Green Tide,
  C'tan-volume) while still deleting any single tough target (harpoon). The meta-robust pick.
- **A (Lancer Aggressive)** — the aggressive/mobile pick: the 4++/M14 Lancer catches fast armies,
  the Volcano gives max single-target punch (Monoliths), and it's the most durable single model
  vs the AP-4 meta. Slightly softer into the pure horde.
