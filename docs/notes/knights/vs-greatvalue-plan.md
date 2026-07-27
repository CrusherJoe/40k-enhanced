# Battle plan — Knights vs "Great Value" (Emperor's Shield + Librarius Conclave Imperial Fists)

> **⚠ SUPERSEDED BY THE v3 REBUILD (2026-07-26).** After a full re-read of every unit + BOTH his detachments
> (Emperor's Shield 2DP **+** Librarius Conclave 1DP — 11E stacks detachments up to your DP budget; 2000pts=3DP)
> AND correcting the durability plan, the whole approach changed. **The durability axis is DEAD:** his bricks
> the Lysander brick is OC34 (Inspiring Commander SETS Terminators to OC2 army-wide + the Ancient's Astartes Banner +1 to the whole unit; not shock-immune, but a Knight army has no way to FORCE a test),
> ~unkillable (2+/4++/W4/−1-to-wound), and ~50-dmg melee; FNP 6+ (~1/6) does NOT save a Knight from that, and
> contesting a brick's objective = a Knight in its charge range = dead. **Current list & plan:**
> `examples/knights-vs-greatvalue.yaml` = **Valourstrike Lance + Dominus Foebreakers (3DP), Priority Assets —
> a BIG-GUN STANDOFF**: 3 gun-Knights (2× Castellan Volcano + Crusader Avenger) delete his soft ranged legs
> (Sternguard T1, then Speeders + cyclone Termies) from 36–60"; fast Armigers take the objectives his two M5
> bricks can't reach + steal his home (+10); I NEVER enter his charge threat. **Full turn-by-turn game:**
> `docs/Great-Value-vs-Knights-Full-Game-Simulation.docx` (~60/40 Knights). The threat-analysis below (his
> tapestry, Oath stack, "kill the soft legs first") still holds; the *numbers* are the older partial-stack pass
> and the *list/plan* here (pin-the-brick) is retired.

Practice game for the LSO. Core data verified 11E (BSData/wh40k-11e + SM Faction Pack v1.1).

## What he is (and the ONE thing that beats him)
**~155 wounds of 2+/4++** — 10 TH/SS Terminators (T5 W4) + 10 Terminators (T5 W3) + Lysander (T5 W7)
+ 6 Bladeguard + 10 Sternguard + 10 Vanguard + Intercessors + 2 Land Speeders. His **two Terminator bricks are OC2-3** (Inspiring Commander sets Terminators to OC2 army-wide; the Ancient's banner lifts the Lysander brick to 10x OC3 + Lysander/Ancient OC2 = **OC34**, the cyclone brick ~OC21), Intercessors **OC10** sticky, Bladeguard OC7, Vanguard OC5; the rest OC1. Emperor's Shield adds **no save-buff** (Wrath of Dorn is *offensive* — re-roll a Wound-of-1
army-wide vs his Oath target, full wound re-roll for Lysander's unit; this stacks on top of base Oath's
re-roll Hits + **+1 to Wound**). Librarius Conclave picks **one Discipline/round**
(Telekinesis = the switch for Temporal Corridor **Deep Strike** + −1 S to wound his psyker units;
Biomancy +2"M; Divination re-roll 1s; Pyromancy +1 AP + Sustained; Telepathy ignore-hit-mods).

**His mobility is NOT one teleporting brick — it's four arrival threats, re-ranked by the mathhammer:**
- **Terminator Squad (10, storm bolters + 2 cyclones) + Librarian [Fusillade]** — **a top ranged threat, but
  only when Oathed.** Fusillade = Lethal Hits; 2 krak cyclones (S9) + storm-bolter volume = **~6 into a big
  Knight un-Oathed, ~11.5 Oathed** (~13 into an Armiger). Slow M5, but has a Teleport Homer.
- **2× Land Speeder** — 2 multi-meltas S9 AP-4 D6 **Melta 2** + 2 stormfury. **The Armiger-killer:** ~8 into a
  Warglaive → **15.3 Oathed (one-shots it)**; only ~4.6 into a big Knight un-Oathed, ~10.7 Oathed. **Melta bonus
  needs <9"** — deep-struck at >9" they do even less, so they're worst the turn *after* they land, in melta range.
- **Sternguard (10) + Librarian [Temporal Corridor]** — **NOT the alpha-killer I first billed.** vs a big
  Knight their bolt rifles only wound on 6s — but every 6 is a **Devastating Wound (unsaveable), ~4/turn un-Oathed, ~8 Oathed.**
  So they're a **persistent invuln-ignoring *chipper* + finisher of hurt Knights + anti-Sisters/character
  sniper** (Precision pistol). They **teleport** — but their teleport turn is their *weakest* shooting turn
  (Deep Struck ≠ stationary → no Heavy +1; the Conclave must run Telekinesis to enable the teleport → no
  Divination/Pyromancy offense that round). Dangerous to a *bracketed* Knight, a slow bleed on a healthy one.
- **TH/SS Assault Terminators (10) + Lysander + Ancient** — **no psyker, walks M5** (Teleport Homer = one
  mid-board jump). TH + Fist of Dorn are **Dev Wounds → ~49 in melee (Oathed, full Wrath re-roll) = one-rounds ANY Knight** (even the
  Lancer's 4++ only survives to ~4W). This is the *melee* deleter; keep every premium Knight out of it.

**You cannot table 155W of 2+/4++. Don't try. He is OC1 — you WIN BY OUT-SCORING while the Navigator dome
denies his four arrival threats and you refuse to feed the hammers.**

## Mathhammer (11E, corrected model — all buffs stacked)
Expected damage/turn. My Knights: Castellan T13 (Blessed Plate) 28W 3+/5++, Crusader T11 26W 3+/5++,
**Armigers T9 14W 3+/5++** (5++ is Ion Shield = **ranged only**). **OATH OF MOMENT** (SM army rule, 11E-updated, verified in the SM faction pack): each Command phase he names
ONE of my units; until his next Command phase, his **whole army re-rolls HIT rolls AND gets +1 to the WOUND
roll** against it (the +1 applies because he's mono-Codex Imperial Fists — no BA/DA/DW/SW). **Wrath of Dorn**
(Emperor's Shield) adds **re-roll a Wound roll of 1** army-wide vs that target, and **full** wound re-roll for
**Lysander's unit only** (the melee brick). So the *Oathed* Knight eats a very different number than an
un-Oathed one — that gap is the whole game.

| Threat → (weapon counts: **2 cyclone launchers, 2 multi-meltas**) | un-Oathed big Knight | **OATHED big Knight** | Armiger (14W) |
|---|---|---|---|
| Cyclone Termies (unit: 2 launchers + 10 storm bolters, Fusillade) | 6.4 | **11.5** | 7 → **13** |
| 2× Land Speeder (2 multi-meltas + 2 stormfury, in melta) | 4.6 | **10.7** | 8 → **15.3 (one-shot)** |
| Sternguard Dev Wounds (unsaveable core) | 4.2 | 8.1 | 4 → 8 |
| **TH/SS brick (melee, Oathed — full Wrath re-roll)** | — | **~49 — one-rounds ALL** | ~49 — one-rounds |
| **ALL his ranged focused on ONE Oathed Knight** | — | **~30 → KILLS a healthy Castellan (28W) or Crusader (26W)** | ~36 (overkill) |
| **My guns → 10 Sternguard** | Avenger+Helverin+plasma = **~7 dead** (T1 wipe *if he deploys them*) | | |

Takeaways: (1) **Oath (re-roll Hits + +1 Wound) lets him CONCENTRATE ~30 onto one Knight** — enough to
**kill a healthy Castellan (28W) or Crusader (26W)** in a turn if all three ranged legs converge. It's a real
**one-Knight-per-turn pick** (and one-shots any Armiger). Durability doesn't save the Oathed target. (2)
**Win by BREAKING the convergence:** kill a leg (Land Speeders first — Oath ~doubles them to ~11/15 and
they're mobile; then cyclones), stay **>9" from Speeder drops** (kills their melta bonus), and use terrain so
cyclones + Sternguard can't all see the Oathed target. Removing any leg drops the alpha below a Castellan's
wounds. (3) **Bait the Oath** onto an Armiger or an already-hurt Knight, not the Castellan. (4) The **melee
brick does ~49 Oathed — one-rounds anything** → never feed it a premium Knight.

## Four hard rules (from the real 11E rules)
1. **NEVER melee the hammers with a premium Knight.** TH/SS + Fist of Dorn are **Dev Wounds** — ~49 in a
   round (Oathed, full Wrath re-roll), one-rounds ANY of my Knights (even the Lancer's 4++). Pin/screen the
   brick only with **expendable Armigers** (one to eat a round), never a big Knight.
2. **Break his Oath convergence — kill the Land Speeders first.** His way to drop a big Knight is Oath (re-roll
   Hits + +1 Wound) + cyclones + Speeders + Sternguard all on one target (~30 → **kills a healthy Castellan
   or Crusader**). Remove any leg and the alpha falls below a Castellan's wounds. **Land Speeders are the
   priority** (Oath ~doubles them to ~11, and 15.3 = a one-shot on an Armiger; they're the mobile leg), then
   the cyclone Terminators. Delete the Sternguard T1 only if he deploys them (Avenger+Helverin+plasma = ~7
   dead); reserved, they're just a chipper.
3. **Bait the Oath + protect the Armigers, but accept Armigers trade.** Every turn his Oath+alpha lands on a
   140-pt Armiger (or an already-hurt Knight) instead of the Castellan, I win the exchange — so present the
   *affordable* target as the tempting one. Meanwhile Armigers are **glass to his ranged** (cyclones/close
   Speeders one-shot one), so use them as pin/screen/bait trades, not gun platforms; keep the Helverin (5++
   + range) back, push the melta Warglaives (which want to be close anyway). Stay **>9" from Speeder drops**.
4. **The Navigator's 12" anti-Deep-Strike dome is the linchpin.** It denies his arrival positioning:
   Sternguard teleport, Land Speeder drops, and both Terminator bricks' Teleport-Homer jumps must land
   **outside** it. Keep it over your scoring. (Temporal Corridor also needs the Sternguard **unengaged** to
   bail — tag them with an Armiger and they can't leave.)

## The list (1985/2000)
- **Knight Castellan** [Blessed Plate, T13] — Volcano *chunks Lysander* (6.4/7W), plasma decimator (D3)
  kills W3 Terminators. Durable mid-board anchor, OC10.
- **Cerastus Knight Lancer** — **NOT for the brick.** Fast (M14) 4++ that **hunts the backline**
  (Sternguard survivors, characters, his home) — D8 lance one-shots characters. Stays out of the hammers.
- **Knight Crusader** [RFBC] — Avenger (A18) kills Sternguard/W3; thermal (D6 melta) kills W4 Terminators.
- **2× Armiger Warglaive** — thermal spears (D6 melta) grind the brick from range; the *screen/pin bodies*.
- **Armiger Helverin** — autocannons into Sternguard/Bladeguard.
- **Navigator** [ally] — the **anti-Deep-Strike dome** over your home; denies Temporal Corridor re-drops.
- **Battle Sisters + Immolator** [ally, Requisitioned] — forced split → **OC10 Sisters half holds home**
  under the dome; melta half + Immolator **twin-multi-melta** (not flamers) grind Terminators; Immolator
  **Purge & Cleanse = +33%** into whatever you focus.

## Deployment
- **Home = OC10 Battle Sisters half under the Navigator dome.** That objective is locked; his teleport
  can't land near it, and OC10 shrugs footslog contest. (Your home scores *you* nothing under Purge, but
  it denies *him* 4-5 VP.)
- **Castellan + Crusader central-mid** with LOS — grind from range, hold the middle at OC10-while-shooting.
- **Armigers spread forward as pin/screen bodies** — they're glass to his ranged (a cyclone volley or a
  closed-in Speeder pair one-shots one), so treat them as tradeable OC/screens, not gun platforms. Keep
  the Helverin (5++ + range) further back than the melta Warglaives (which want to be close to pin anyway).
- **Lancer on a flank**, angled at his backline (Sternguard survivors / characters), NOT the brick.
- **Two Teleport Homer tokens go down at start** (both Terminator bricks) — expect a mid-board terminator
  drop. Leave no 9" gaps near your key units **outside** the dome; keep the dome over what you actually
  need to hold, and screen the open mid-board with Armiger bodies so a homer drop can't land clean + charge.

## Turn by turn
**T1 — priority = the cyclone Terminators + Land Speeders (the real anti-Knight ranged), then Sternguard.**
Whatever's deployed of those, focus it: Avenger + Helverin + Castellan plasma + RFBC. If the Sternguard are
on the board, they're an efficient wipe (~7 dead) — take it. If he reserved his mobile guns, hold nothing
back on the walking bricks / Bladeguard and keep the dome tight for the arrivals. Lancer repositions toward
his flank/backline. Grab the central objectives with OC10 Knights.
**T2 — grind + out-position.** Volcano onto Lysander (chunk him, finish next turn). Thermal + spears +
Immo twin-MM (cover-strip'd) into the TH/SS brick — ~6-8 Terminators over T1-2. Lancer dives the backline
(characters / his home). **If the brick charges you, receive it with an ARMIGER** (pins it → no teleport
→ eats the Dev-Wound hammers for a round; a 140-pt trade for a 360-pt brick's turn).
**T3-4 — score the crater.** He's bleeding Terminators and can't out-OC you; Meatgrinder rewards your
kill-differential (dead Sternguard/Bladeguard/Terminators + his home). Expect him to Oath-focus **one**
Knight per turn (~30 if his legs converge — enough to kill a healthy Castellan/Crusader) — accept ~one loss/turn max, and make it the *cheapest* Knight in
the Oath by then (bait with an Armiger, break LOS with the Castellan). If you killed the Speeders/cyclones
early, his alpha can't reach a healthy Knight at all. Keep feeding cheap Armigers to pin the brick near your
scoring; Lancer takes his home.
**T5 — close.** Hold central + expansion, contest his home, tally the kill-differential.

## Watch-outs
- **Oath of Moment (his army rule) is the engine of the whole threat.** Each Command phase he names one of
  my units; his **entire army re-rolls Hit rolls AND gets +1 to Wound** against it (the +1 because he's
  mono-Codex Imperial Fists), and **Wrath of Dorn** stacks **re-roll a Wound-of-1** army-wide (full wound
  re-roll for Lysander's melee unit). It's what turns ~4.6-dmg Speeders into ~10.7 and lets him assemble a
  ~30-dmg alpha on one Knight (enough to kill a healthy Castellan). Watch which unit he Oaths in his Command
  phase — that names his kill target for the turn. **Counter-play:** the Oath is one unit/turn, so spread;
  bait it onto something cheap; and if he Oaths a Knight, that's the one to pull back / break LOS / keep >9"
  from his melta this turn.
- **His Discipline is a per-round choice:** teleport turn (Telekinesis) = he gives up Divination re-rolls
  and Biomancy speed that round — punish the trade. Telekinesis also gives his psyker units **−1 S to be
  wounded** — so on that turn your S9 melta wounds his terminators on 3+ still (unchanged), fine.
- **Sternguard Dev-Wound math (revised down):** vs a big Knight they only wound on 6s — but each 6 is an
  **unsaveable Dev Wound, ~4/turn (~8 Oathed).** That won't drop a healthy Knight on its own, but it **finishes a bracketed one**
  and shreds my Sisters/characters (Precision). Don't leave a *degraded* Knight or a lone character in their
  teleport arc. Their **teleport turn is their weakest** (no Heavy, no offense Discipline) — the danger turn
  is the one *after* they land, once they're stationary and the Conclave switches to Divination/Pyromancy.
- **Land Speeders (2× multi-melta S9 AP-4 D6 Melta 2, M14 FLY, arrive from reserve):** the mobile melta
  that snipes your Knights' rear. One won't kill; **two into a bracketed Knight will.** Dome-deny their
  drop, and kill them with Helverin autocannons / Avenger the turn they show — don't leave a hurt Knight
  exposed to both.
- **Teleport Homers:** even the M5 TH/SS brick can jump mid-board once. A mid-board Armiger screen + the
  dome force the drop far from your scoring; then it still has to *walk/charge* in — kite it.

## The five reminders (table card)
1. **Watch his Oath every Command phase — that's his kill target.** Oath (re-roll Hits + **+1 Wound**, whole
   army) + Wrath of Dorn (re-roll Wound-of-1) lets him focus ~30 dmg on ONE Knight = **kills a healthy
   Castellan or Crusader.** **Break the convergence; don't tank it.**
2. **Kill order: Land Speeders > cyclone Termies > Sternguard.** Speeders are the mobile leg Oath doubles
   (~11 into a Knight, 15.3 = one-shot an Armiger); remove any leg and his alpha drops below a Castellan's
   wounds. Sternguard = an ~8 unsaveable chipper.
3. **NEVER melee the hammers with a big Knight** (Dev-Wound TH/SS + Fist of Dorn = ~49 Oathed, one-rounds all) —
   pin with Armigers; **and keep Armigers out of cyclone LOS / <9" of Speeder drops** (they're glass).
4. **Navigator dome is the linchpin** — it denies Sternguard teleport, Land Speeder melta drops, AND both
   Teleport-Homer jumps. Keep it over your scoring.
5. **Lancer hunts the backline, not the hammers.** Screen the mid-board (homers) with Armiger bodies.
