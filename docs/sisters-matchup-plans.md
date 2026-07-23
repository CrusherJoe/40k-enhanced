# Sisters — matchup battle plans vs the boogeyman meta

For `examples/best-sisters-allcomers.yaml`. Missions + scoring verified from
`data/missions.yaml`; enemy dispositions from their lists; durability/damage from
`docs/sisters-battle-plan.md`; deployment layouts from `data/layouts/`.

> **TOURNAMENT NOTE (important):** you lock **ONE** disposition for the whole event —
> it does NOT change per game. **LOCK DISRUPTION** (favoured vs 4 of the 6 boogeymen;
> suits this mobile list). The "→ I pick …" headings below show the *ideal* disposition
> per matchup — that analysis is what motivates locking Disruption — but in a real event
> your **mission is set by the opponent's disposition** under locked Disruption:
> opp Purge → *Delaying Action*; opp Recon → *Smoke and Mirrors*; opp Disruption →
> *Outmanoeuvre*; opp Take-and-Hold → *Death Trap*. The turn-ready, locked-Disruption
> version with deployment maps is in **`docs/Sisters-Battle-Plan.docx` (§4–§6)**.

**Deployment note.** Only Purge-the-Foe layouts are ingested to YAML (Knights phase),
so I frame deployment by TYPE — the three that A/B/C draw from — and default the
narrative to **Layout A ≈ diagonal**, with **B/C** = the horizontal (Dawn-of-War,
~18" zones, ~8" NML, *close*) and vertical (side-to-side) variants. The **universal**
facts hold on every layout: **6 objectives** (2 home, 2 central-NML, 2 expansion),
**16 obscuring terrain areas**, **centre packed** (no turn-1 cross-board LOS — you must
advance to open lanes and reach the two central objectives). *(Want the exact
letter→terrain per these matchups? I can ingest the Disruption/T&H Event Companion
pages like I did Purge.)*

**Universal deployment for this list (all matchups):**
- **Castle the hammer**: Vahl+Paragons + the Palatine/Imagifier MM-Retributor brick
  central-rear with LOS into the mid. The brick is 2+/4++ but VOLUME kills it — keep it
  *back*, sniping anchors, never in flamer/horde range.
- **Immolators + Dominions** mid-forward (delivery), hull-down T1 (centre blocks LOS anyway).
- **Sacresants + Canoness [Sanctified Amulet]** hold centre — the **anti-Deep-Strike
  bubble** shields your backfield; Dogmata gives them +1 OC.
- **Battle Sisters** screen the castle + sit home/expansion objectives (cheap OC, expendable).
- **Zephyrim / Seraphim**: flanks or Reserve for actions / late contest / counter-charge.
- **Castigator** rear with board-wide LOS (48", Ignores Cover) — it also *marks* AP.
- **Layout B/C (close):** short NML = fast enemy contact → screen harder, value the
  Amulet bubble more, melta gets targets a turn sooner. **Diagonal (A):** long approach →
  angle the hammer's LOS across the mid, rush the two central objectives with jump + Immolators.

---
## vs Salamanders flamer-brick  →  I pick DISRUPTION
Their disposition Recon (or Purge). **Disruption vs Recon = *Smoke and Mirrors*** (Decoy
objectives, esp. in their territory; 10 VP if 4+ decoyed) — or vs Purge = *Delaying Action*
(2 VP/kill + hold). **Why:** I have more mobility than their mid-speed brick, and I can *score
kills* — each Land Raider I melta is real tempo. Don't attrition-race their durable Infernus wall.
- **Targets:** soften + delete the **2 Land Raiders** (Immolator strips cover → Castigator +1 AP →
  Vahl+Paragons one-shot one, MM-Retributor + melta Dominion the other). Then Aggressors/Bladeguard.
- **Do NOT** walk bodies inside 12" of the pyreblasters (they auto-wipe a 10-squad). Screen,
  Decoy from range, counter-charge stragglers with Zephyrim.
- **B/C close:** their flamers reach you faster — kill a Land Raider T1, keep the castle 12"+ back.

## vs Ork Kult of Speed (dakka)  →  I pick TAKE-AND-HOLD
Their disposition Disruption (or Purge). **T&H vs Disruption = *Determined Acquisition*** (3 VP/
objective, +3 more in *their* territory; 2 VP/newly-taken). **Why:** they're *faster* than me — a
maneuver race favours them. Instead **anchor on objectives and make them come to me**, where my
melta/flamers punish their fragile T5-W2 fast units.
- **Targets:** Kill Rigs + Wazdakka with melta; **Deffkoptas/Flash Gitz with Castigator Blast +
  heavy bolters + flamers** (T5-6 multi-wound → AP-1/-2 volume, not pure AP-4).
- **Transports:** durable enough (Immolator shrugs 6 kopta rokkits) but *multiple* AT units bracket
  them over 2 turns — don't over-expose; win the objective grind while they trade inefficiently.
- **B/C close:** they reach you T1-2 — screen the backfield, hold central hard.

## vs Ork Green Tide (100 Boyz)  →  I pick DISRUPTION
Their disposition Take-and-Hold. **Disruption vs T&H = *Death Trap*** (2 VP/trapped terrain area,
+3 if it's an objective; **3 VP if enemies in a trapped terrain area are destroyed**; 4 VP hold).
**Why:** Boyz **cluster in terrain** → Booby-Trap those areas and clear the blobs there with my
flamers/Blast = double-dip VP, and I **dodge the OC race I'd lose** to 100 bodies.
- **Targets:** it's the **flamer game** — Castigator + 2 Immolation-Flamer Immolators + flamer
  Dominion + heavy bolters ≈ **37 dead Boyz/turn**. Kill *whole units* to break their OC.
- **Never get charged** (a mob wipes a 10-squad in melee): screen with Battle Sisters, flamer on
  Overwatch, fall back + shoot, hold the line with Sacresants (4++) + the mid.
- Save melta for Ghazghkull / any Battlewagon; don't waste AP-4 on Boyz.

## vs Necron Monoliths (3× T13, OC8, slow)  →  I pick DISRUPTION
Their disposition Disruption. **Disruption vs Disruption = *Outmanoeuvre*** (escalating 4→5→6 VP
per non-home objective; **10 VP for holding THEIR home**). **Why:** Monoliths are **M8" and only
three models** — I *out-maneuver* them, grab the objectives they can't reach, and race their home
with jump units, **ignoring the near-un-killable pyramids**.
- **Targets:** DON'T dogpile a Monolith (softened, Vahl+Paragons can take one, but it's not worth
  the whole game). Kill the **Lokhust Destroyers / Silent King's support / Ophydians**; deny their
  scoring; run the map.
- **Screen Ophydian deep strike** with the Amulet bubble. Zephyrim/Seraphim grab + hold the flanks.
- **B/C close:** less approach needed — good, contest their home sooner.

## vs Necron C'tan (4× T11, −1 Damage, kill-farmers)  →  I pick DISRUPTION
Their disposition Purge (or Recon). **Disruption vs Purge = *Delaying Action*** (2 VP/kill + hold) —
or vs Recon = *Smoke and Mirrors*. **Why:** C'tan are **un-killable** (7.3 dmg even fully buffed,
incl. their −1 Damage) and their Purge list **farms my dead units** — so **minimise what I feed
them** and score independently with mobility.
- **Targets:** ignore the C'tan. Melta/kill the **killable enablers** — Lychguard, Lokhust,
  Canoptek Reanimator, Plasmancer, characters (each = 2 VP on Delaying Action).
- Keep fragile units *out of C'tan threat + Drain-Life range* (6" mortal aura); trade nothing cheaply.
- Hold central + expansion; let the slow C'tan sit uselessly on their own half.

## vs Dark Angels Deathwing (3× 2+/4++ bricks, OC1)  →  I pick TAKE-AND-HOLD
Their disposition Take-and-Hold. **T&H vs T&H = *Battlefield Dominance*** (control MORE objectives;
3 VP/objective +2 more if you hold home). **Why:** the bricks are near-immortal but **OC1** — their
board control is *thin*. **I out-OC them**: flood objectives with Battle Sisters / Sacresants /
Dominion-on-foot bodies; they can't hold enough to win the primary.
- **Targets:** melta *does* work on the W4 Terminators (multi-damage past the 4++) — chip a brick
  when softened, but **don't over-commit** to tabling them; win on points. Kill the Sternguard /
  Eradicators / Repulsor / Scouts (the *scoring/killable* pieces).
- **Screen the Deep Strike** hard with the **Sanctified Amulet** bubble — Deathwing teleport into
  your lines is how the bricks reach the fragile bodies. Deny it and they walk slowly into your guns.
- **B/C close:** they arrive sooner — bubble + screens are even more important; grab central T1.

---
## The meta-pattern (how to pick a disposition vs anyone)
- **Enemy is low-OC but durable** (Deathwing) → **Take-and-Hold, out-OC them.**
- **Enemy is a high-body horde** (Green Tide) → **Disruption/Death Trap, dodge the OC race, kill blobs in terrain.**
- **Enemy is slow & few** (Monoliths) → **Disruption/Outmanoeuvre, run the map around them.**
- **Enemy is faster than me** (Ork Kult) → **Take-and-Hold, anchor and make them come.**
- **Enemy farms my deaths** (C'tan Purge) → **Disruption, mobility, feed them nothing.**
- **Enemy is a mid-speed durable gunline** (Salamanders) → **Disruption, out-position + score kills.**
