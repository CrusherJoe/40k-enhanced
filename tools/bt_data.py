# -*- coding: utf-8 -*-
"""Black Templars — "SEND HELP → FIXED (v2, corrected)" LSO workup data. The deliberately-bad
BT list the user handed over, rebuilt into a LEGAL, functional 2000-pt army around its REAL
engine, given the same sim/analysis treatment as Great Value.

Corrected after pilot feedback (all verified from data/bsdata + the BT faction pack):
  * Marshal's Household is the SWORD BRETHREN detachment (not the Emperor's Champion one).
  * The killing engine is Marshal + Castellan + Sword Brethren: the Marshal's INSPIRATIONAL
    EXEMPLAR makes an unmodified Hit of 5+ a CRITICAL HIT, the Sword Brethren power weapons have
    [LETHAL HITS] (crit hit -> auto-wound), the Castellan's VEHEMENT AGGRESSION re-rolls hits, and
    Slayers of Abominations (1CP) adds +2 S vs MONSTER/VEHICLE -> S7. So Marshal+Castellan+5 Sword
    Brethren one-shots an Armiger IN MELEE. That's the anti-tank, and it was there all along.
  * No BT character leads BLADEGUARD -> the original's Chaplain+Bladeguard was dead weight; cut.
  * BT Chaplains all suck except Grimaldus (the Execrator is a 50-pt Advance-and-Charge tax) -> run
    Grimaldus only. And Marines have BAD SHOOTING without Oath -> don't build a gunline; deliver
    the melee. And a 20-model Crusader brick CANNOT FIT COVER on modern terrain-dense boards ->
    run 10-model Crusader bricks that actually fit, not GW's un-hideable 20 + surge.
Points MFM-verified from data/mfm/black-templars.json where present (Marshal/EC/Grimaldus/Repulsor
Executioner not in the BT MFM slug -> app v912 values, flagged *).
Regenerate:  PYTHONPATH=tools:src python3 tools/gen_bt_docx.py && ... gen_bt_xlsx.py
"""
EVENT = "Lone Star Open (LSO) — 300+ players, Swiss"
GENERATED = "2026-07-27 (11E, post-Dataslate)"

LIST_NAME = "SEND HELP → FIXED v2 — Black Templars · Companions of Vehemence + Marshal's Household"
DETACHMENTS = "Companions of Vehemence (2 DP — surge engine) + Marshal's Household (1 DP — SWORD BRETHREN buffs) = 3 DP"
DISPOSITION = ("Take and Hold (hold with cover-fittable 10-Crusader bricks + surge; delete with the two "
               "delivered Sword Brethren spikes). NOT Purge — this list scores by holding, kills to clear contesters.")
IDENTITY = (
    "A BLACK TEMPLARS DELIVERED-SPIKE army — the corrected fix of the 'send help' list. The killing "
    "engine is TWO Sword Brethren anti-tank spikes: each is Marshal + Castellan + 5 Sword Brethren, and "
    "it MURDERS things far bigger than itself. The Marshal's Inspirational Exemplar turns unmodified "
    "Hits of 5+ into Critical Hits; the Sword Brethren's master-crafted power weapons have [LETHAL HITS] "
    "so those crits AUTO-WOUND; the Castellan re-rolls the hits; and Slayers of Abominations (1CP) adds "
    "+2 S vs MONSTER/VEHICLE. Net: at S7 with ~half its attacks auto-wounding, one spike ONE-SHOTS an "
    "Armiger in melee. The whole fix is DELIVERY — each spike now rides a Repulsor Executioner (cap 7 = "
    "Marshal+Castellan+5 = exactly 7) instead of walking. Grimaldus (the only BT Chaplain worth taking) "
    "anchors a 10-Crusader brick that ACTUALLY FITS COVER (GW's 20-brick can't hide on modern boards, so "
    "we don't run it). The Emperor's Champion is a Precision character-assassin. Honest ceiling: this is a "
    "swingy melee army with GOOD anti-tank IN MELEE but INHERENTLY BAD SHOOTING and only 2 delivery "
    "buses — it deletes what it reaches and struggles with what it can't (castled guns, Knights, speed).")

# (unit, count, wargear/role, ~pts) — MFM-verified where noted; * = not in BT MFM slug (app v912).
UNITS = [
    ("Repulsor Executioner (Spike A bus)", "1", "TRANSPORT (cap 7) for spike A + 1 Heavy Laser Destroyer (S16). The delivery + what little AT-at-range BT has.", "265*"),
    ("Marshal + Oathbound Exemplar", "1", "WARLORD; leads Spike A's Sword Brethren. INSPIRATIONAL EXEMPLAR: unmodified Hit of 5+ = Critical Hit -> the whole reason the spike works.", "95*"),
    ("Castellan (Support)", "1", "Stacks into Spike A. VEHEMENT AGGRESSION: re-roll Hits (on a Ld pass) -> more 5+ crits to convert via Lethal Hits.", "70"),
    ("Sword Brethren Squad (Spike A)", "5", "Master-crafted power weapon S5 AP-2 D2 A3 [LETHAL HITS] -> with crit-on-5 + re-rolls + Slayers of Abominations (+2 S vs Mon/Veh = S7), ONE-SHOTS an Armiger. -> Repulsor A.", "105"),
    ("Repulsor Executioner (Spike B bus)", "1", "TRANSPORT (cap 7) for spike B + 2nd Heavy Laser Destroyer.", "265*"),
    ("Marshal (Spike B)", "1", "2nd crit-on-5 enabler; leads Spike B's Sword Brethren.", "80*"),
    ("Castellan (Support)", "1", "2nd re-roll enabler; stacks into Spike B.", "70"),
    ("Sword Brethren Squad (Spike B)", "5", "The 2nd delivered anti-tank spike. -> Repulsor B.", "105"),
    ("Chaplain Grimaldus (+3 Cenobyte)", "1", "The ONLY good BT Chaplain. FNP + Litany -> the durability that lets a foot brick hold. Leads the Crusader anvil.", "100*"),
    ("Crusader Squad (Grimaldus anvil)", "10", "A 10-model brick that FITS COVER (the whole point — a 20-brick can't hide on modern boards). Sticky OC + Righteous Zeal surge.", "150"),
    ("Emperor's Champion", "1", "Duelist / character-assassin: Black Sword S8 AP-3 D3 A6 [ANTI-CHARACTER 5+, PRECISION]. Leads the 2nd Crusader brick or the Assault Intercessors.", "75*"),
    ("Crusader Squad (2nd cover-brick)", "10", "2nd cover-fittable objective holder + surge. EC or a Castellan can lead it.", "150"),
    ("Assault Intercessor Squad", "10", "Board control / actions / screen for the buses. Chainsword S4 AP-1 D1 A4.", "150"),
    ("Gladiator Lancer", "1", "The ONE efficient Oath-boosted RANGED AT: twin lascannon-class gun to reach the un-chargeable (a melee army's only long answer to castled armour).", "160"),
    ("Eradicator Squad", "3", "Melta AT backup (BT shooting is thin — this is a concession, not a gunline). Deep-strike/reposition threat.", "90"),
]
LIST_TOTAL = ("~1,930 core / 2000 — spend the last ~70 on Sword Brethren upgrades (Inheritors of Sigismund = "
              "Fights First, Fervent Exemplars = +1 charge; from Marshal's Household, so they DON'T count toward "
              "the enhancement cap) + the Oathbound Exemplar. Points MFM-verified where present; * = Marshal / EC / "
              "Grimaldus / Repulsor Executioner not in the BT MFM slug (app v912) — confirm vs your app. Transport "
              "fit verified: each Repulsor carries Marshal + Castellan + 5 Sword Brethren = 7/7. ALL attachments "
              "legality-checked vs the datasheets (Marshal & EC lead Sword Brethren; Grimaldus/EC lead Crusaders; "
              "no BT character leads Bladeguard — which is why the original's Bladeguard was dead weight).")

RULES = [
    ("The SPIKE — how BT does anti-tank (in melee)", "Marshal (INSPIRATIONAL EXEMPLAR: unmodified Hit 5+ = Critical Hit) + Sword Brethren power weapons ([LETHAL HITS]: crit = auto-wound) = Lethal Hits on 5s. + Castellan (VEHEMENT AGGRESSION: re-roll Hits) + Slayers of Abominations (1CP: +2 S vs MONSTER/VEHICLE = S7). One Marshal+Castellan+5-Sword-Brethren spike ONE-SHOTS an Armiger and badly hurts a big Knight/vehicle — in the fight phase, where Knights have no invuln. This IS the army's anti-tank."),
    ("Delivery = the whole fix (2 Repulsor Executioners)", "The spikes are M6 on foot and die on the walk unless bused. Each Repulsor (cap 7) carries a full spike (Marshal+Castellan+5 = 7) and drops it into a chosen charge, then adds a Heavy Laser Destroyer. RISK: only 2 buses -> a shooty army that pops both strands both spikes. Protect them; this is the list's single point of failure."),
    ("Oath of Moment (and BT's bad shooting)", "Marines shoot BADLY without Oath. Oath (name 1 enemy unit -> army-wide re-roll Hits into it) is what makes the thin gun package (2 Heavy Laser Destroyers + Gladiator Lancer + 3 Eradicators) do anything. Point it at the ONE big thing you must shoot; the rest of your killing is the delivered melee."),
    ("Companions of Vehemence — surge (2 DP)", "Units make surge moves (~D6\"); Crusader Squads via Righteous Zeal surge toward the CLOSEST OBJECTIVE when shot. It's the mobility patch for a slow foot army — but see the cover caveat: a surge onto an objective you can't fit into cover on just exposes the brick."),
    ("Marshal's Household — the Sword Brethren detachment (1 DP)", "Friendly SWORD BRETHREN SQUAD units have +1 OC. Strats: Slayers of Abominations (+2 S vs Mon/Veh — the spike's anti-tank switch), Blade of Detestation (mortals on the charge), Unsparing Execution (punish fall-back). Enhancements (Inheritors of Sigismund = Fights First, Fervent Exemplars = +1 charge) are Sword-Brethren-only and DON'T count toward the cap. Everything here feeds the spikes."),
    ("Grimaldus — the only Chaplain worth it", "FNP + Litany on the Crusader anvil = the staying power a foot brick needs. Every OTHER BT Chaplain is a tax (the Execrator = 50 pts for Advance-and-Charge); this list runs Grimaldus and no other."),
    ("The 20-brick trap (why we run 10s)", "GW's intended BT survivability is a 20-model Crusader brick + surge. On modern terrain-dense boards a 20-brick physically CANNOT FIT INSIDE COVER, so it eats shooting in the open and the surge just walks it into more fire. We run 10-model bricks that actually fit cover and screen — less sticky, far more survivable in practice."),
    ("Emperor's Champion — the scalpel", "Black Sword S8 AP-3 D3 A6 [PRECISION] -> he alone can pick out and kill an attached enemy Character in melee (Sigismund's Heir even lets him re-roll a charge to reach a Character within 12\"). Lone Operative until he joins a unit. Save him for the enemy's key buff-character."),
    ("What this list genuinely can't do", "(1) REACH a castled gunline/Knight army that stays back — the AT is melee, the shooting is bad; (2) out-body a horde (Orks); (3) out-run a fast army that kites the spikes. Its whole game is 'get a spike into the thing that matters.' If the buses die or the enemy refuses the fight, it has few answers."),
]

MINDSET = (
    "Play it as a delivered-scalpel melee army, honest about its holes. The plan: bus a Sword Brethren spike "
    "into the enemy's biggest threat (Knight/vehicle/monster) and DELETE it in melee, hold the middle with "
    "the cover-fittable Grimaldus brick, and use the EC to assassinate a key character. Three disciplines: "
    "(1) PROTECT THE 2 BUSES — they're the only delivery; screen and use LoS, because if both die the spikes "
    "walk and the plan dies. (2) HIDE THE BRICKS IN COVER — run 10s, not a 20, so they actually fit. (3) DON'T "
    "expect the guns to bail you out — Marines shoot badly without Oath, so Oath the one thing you must shoot "
    "and win everything else in melee. Accept the hard matchups (castled shooting, Knights that stay back, true "
    "hordes, pure speed): pick your spike targets, grind primary, and don't throw a bus into open ground.")

# ---- MATCHUPS: the corrected FIXED Black Templars vs the LSO-meta archetypes (BT's perspective) ----
# verdict in {FAVOURABLE, EVEN, COIN-FLIP, UNFAVOURABLE, HARD}
MATCHUPS = [
    dict(key="emperors-children", faction="Emperor's Children", archetype="Frenzied Host / Coterie (Defiler + swarm)",
         prev="High (9)", verdict="EVEN (slight favour)",
         deciding="A melee brawl you're built to win the exchanges of: a delivered spike (S7 + Slayers) ONE-SHOTS a Defiler, Grimaldus FNP out-lasts the Infractor/Daemonette swarm, and the EC Precision-kills a Lord Exultant. Their AP-1/-2 volume is the wrong shape for your armour.",
         plan=["Bus a spike into a Defiler each turn (their only real anti-armour) and delete it in melee.",
               "Let the chaff crash the Grimaldus brick; it holds, and the 2nd spike counter-punches.",
               "EC hunts the buff character; grind primary — you out-durable and out-fight the paper swarm."],
         watch="Fulgrim (Fights First) can kill a spike before it swings — Oath+shoot him or bait him onto the anvil first."),
    dict(key="orks-green-tide", faction="Orks", archetype="Green Tide (~100 bodies)",
         prev="High (8)", verdict="UNFAVOURABLE (your hardest common matchup)",
         deciding="The spikes are wasted here — Slayers of Abominations only fires vs MONSTER/VEHICLE, so vs 100 Boyz your S7 auto-wounds are killing 1-wound bodies with a sledgehammer. The horde out-bodies your 10-bricks and blankets the board; you can't clear 100.",
         plan=["Save the spikes for the Kill Rig/Stompa/Deffkilla (the only Mon/Veh targets); grind Boyz with the anvil + Assault Intercessors + gatling.",
               "Hold your two cover-bricks' objectives, concede the middle; race secondaries.",
               "Gladiator Lancer + Eradicators delete the Wazdakka/big wagons; don't over-commit a bus into the tide."],
         watch="Getting out-actioned and out-bodied; and a Rokkit popping a bus. Honest ~30% — this is a bad matchup, minimise the margin."),
    dict(key="admech", faction="Adeptus Mechanicus", archetype="Rad-Zone / Lords of the Forge gunline",
         prev="High (6)", verdict="EVEN (delivery race)",
         deciding="A spike deletes a Kataphron brick in melee, and their D6-damage guns over-kill your bodies (waste) — BUT their shooting can pop your buses before you arrive. Whoever wins the delivery race wins: reach them and they fold; get the buses shot and you have no reach (BT's bad shooting can't crack a gunline).",
         plan=["Advance the buses behind terrain/screens — never park in open Kataphron/ferrumite LoS turn 1.",
               "Deliver both spikes into the gunline T2-3; it has few melee bodies and folds. Oath a Kataphron brick for the guns.",
               "Surge the anvil onto mid objectives; out-score once their shooting is tar-pitted in melee."],
         watch="Both buses dying early = you can't reach them and can't out-shoot them = a loss. This matchup lives or dies on the buses surviving to deliver."),
    dict(key="tau-retaliation", faction="T'au Empire", archetype="Retaliation Cadre (fusion/rail alpha)",
         prev="High (5)", verdict="HARD (your worst matchup)",
         deciding="The nightmare shape: a shooting alpha that one-shots Repulsors before you deliver, then kites your M6 spikes forever. Strand the buses and you have a melee army with nothing in range — and BT's own shooting can't punish T'au. You often just never get to fight.",
         plan=["MAX reserves + terrain T1-2; keep BOTH buses out of first-turn rail/fusion LoS at ALL costs.",
               "If you get a bus in, delete a Riptide/Crisis brick with a spike — T'au fold in melee IF you reach.",
               "If both buses die early, pivot to holding cover-bricks + secondaries and accept a grind; don't force stranded charges into the open."],
         watch="This is a delivery race you're badly behind in, and your shooting can't bail you out. ~28% — your single worst archetype; don't spend CP on AoC vs their AP-4/-5 (it does nothing)."),
    dict(key="necrons-ctan", faction="Necrons", archetype="Awakened Dynasty (C'tan + Wraiths)",
         prev="Med (4)", verdict="COIN-FLIP (lean unfavourable)",
         deciding="A spike badly hurts a C'tan in melee (S7 + Lethal auto-wounds partly beat the 4++/-1Dmg), but you can't table 3 shards and reanimation refunds the chip; gauss pops your buses. You out-fight Wraiths/Lychguard and the EC snipes a Technomancer.",
         plan=["Bus a spike into ONE C'tan and commit — chip spread just reanimates away.",
               "EC assassinates the Technomancer/Cryptek that fuels reanimation; hammers kill the escorts.",
               "Hold cover-bricks + surge; win on sticky primary, not on the body count."],
         watch="Losing a bus to gauss + the C'tan grinding your midboard. A coin-flip you steal on objectives, not one you dominate."),
    dict(key="custodes", faction="Adeptus Custodes", archetype="Lions of the Emperor (elite melee)",
         prev="Med (4)", verdict="COIN-FLIP",
         deciding="Elite melee mirror. Note the spike's +2 S is vs MONSTER/VEHICLE, so vs Custodian INFANTRY you're at S5 (still Lethal-on-5) — good but not a one-shot. Your edge is BODIES + the EC's PRECISION Black Sword to duel their characters, and a spike deletes a Caladius/Telemon.",
         plan=["Don't feed a lone spike into Wardens head-on — gang two units or shoot them with Oath.",
               "EMPEROR'S CHAMPION vs their Blade Champion/Trajann: Precision + Anti-Character = a real melee assassination.",
               "Out-body + out-score; a spike one-shots the Caladius; hold cover-bricks."],
         watch="Their melee out-damages a single spike; commit together and let the EC take the character duel."),
    dict(key="blood-angels", faction="Blood Angels", archetype="Stormlance / Liberator jump alpha",
         prev="Med (4)", verdict="COIN-FLIP (lean unfavourable)",
         deciding="A faster melee army that gets the charge first: DC/Sang Guard M12 + Deep Strike out-deliver your 2 buses. You're durable enough to receive and counter-punch with a fresh spike, but you're behind on tempo and they can pop a bus on the drop.",
         plan=["Screen so DC/Sang Guard land 9\"+ out; gatling + Assault Intercessor overwatch thins them.",
               "RECEIVE the charge on the Grimaldus brick, then counter-charge the spent unit with a fresh spike + EC on their Priest/Lemartes.",
               "Trade evenly, out-score late — they're fragile once the alpha is spent."],
         watch="Both spikes getting charged before they swing; you want to receive here, not over-extend. Their delivery beats yours."),
    dict(key="dark-angels-deathwing", faction="Dark Angels", archetype="Deathwing Knights / Inner Circle",
         prev="Med (3-4)", verdict="EVEN",
         deciding="A good matchup for the spike: the Deathwing 4++/-1Dmg mace brick shrugs normal power weapons, but LETHAL HITS auto-wounds skip the to-wound roll and the volume grinds even Terminators — and a delivered spike + Slayers isn't needed here (they're infantry) but the Lethal-on-5 volume still bites. Melee mirror decided on primary.",
         plan=["Deliver a spike into the Deathwing brick — Lethal Hits on 5s out-grinds the 4++ better than shooting does.",
               "EC + 2nd spike hunt the softer support / characters; the Lion is a Monster -> a spike + Slayers (S7) or the Lancer.",
               "Race objectives; both armies are slow, so cover-bricks + surge decide it."],
         watch="Feeding one spike piecemeal into the mace brick; commit with support. Even, decided on primary."),
    dict(key="drukhari", faction="Drukhari", archetype="Skysplinter Assault (fast splinter + lance)",
         prev="Med (3)", verdict="UNFAVOURABLE",
         deciding="Speed kills you: they out-manoeuvre M6, kite the spikes, dark-lance the Repulsors, and flip objectives late. Your armour tanks the splinter, but you can't CATCH them and your shooting can't punish their paper at range.",
         plan=["Hold a tight castle + cover-bricks; make them commit into your bubble (their paper folds if it does).",
               "Gladiator Lancer + Eradicators + Oath one-shot Ravagers/Venoms to cut their mobility and the lance threat to the buses.",
               "Zone with screens so they can't backfield-raid; grind the secondaries you can hold."],
         watch="Out-actioned by raw speed while the spikes chase air; protect the buses from lances. ~35%."),
    dict(key="astra-militarum", faction="Astra Militarum", archetype="Steel Hammer superheavy / artillery",
         prev="Low-Med (2)", verdict="EVEN (slight favour, delivery race)",
         deciding="Their tanks are PRIME spike food — Slayers (+2 S, S7) + Lethal Hits one-shots a Russ and badly hurts a Shadowsword in melee — and their guns over-kill your bodies (waste). But their volume CAN pop a bus, so it's a delivery race again.",
         plan=["Advance behind terrain; deliver a spike into a superheavy/Russ each turn and delete it in the fight.",
               "Assault Intercessors + anvil carve the Guard infantry; surge onto objectives their tanks can't hold.",
               "Gladiator Lancer + Eradicators tax anything the spikes can't reach; out-score a low-model tank list."],
         watch="Artillery + orders chip the buses before you connect; screen them to the first melee. Slight favour if you weather T1-2."),
]

BANDS = {
    "FAVOURABLE / EVEN+ (bank these)": ["Emperor's Children", "Dark Angels Deathwing", "Astra Militarum", "AdMech"],
    "COIN-FLIP (practice these)": ["Custodes", "Necrons C'tan", "Blood Angels"],
    "UNFAVOURABLE (underdog)": ["Drukhari Skysplinter", "Orks Green Tide"],
    "HARDEST (~28%)": ["T'au Retaliation"],
}
RECORD_NOTE = (
    "The corrected fix is a SWINGY MID-TO-LOW-TIER melee-spike army — a real improvement on the original "
    "(the engine now gets delivered, the dead weight is gone), but its ceiling is capped by faction-level "
    "problems the user is right about: Marines shoot BADLY without Oath, so it can't reach a castled gunline "
    "or a Knight army that stays back; only Grimaldus is worth taking among BT Chaplains; and GW's intended "
    "20-brick survivability doesn't work on cover-dense boards (we run 10s instead). Realistic 300+ GT: below "
    "even, ~2-4 to 3-3, spiking wins where it delivers a spike into a Monster/Vehicle and grinds melee, and "
    "losing where it can't reach (T'au, castled guns, Knights) or gets out-bodied/out-run. It DELETES what it "
    "reaches; its whole risk is reaching. A rescued list that plays honestly to a fun, melee-forward game — "
    "not a GT-winner, and BT's inherent shooting/mobility gaps are why.")

VERIFIED_PROFILES = [
    ("--- the SPIKE (the anti-tank engine) ---", "", ""),
    ("Sword Brethren — Master-crafted Power Weapon", "S5 | AP-2 | D2 | A3 | [LETHAL HITS]", "the payload; S7 vs Mon/Veh with Slayers of Abominations."),
    ("Marshal — Inspirational Exemplar", "unmodified Hit of 5+ = Critical Hit (its unit)", "turns Lethal Hits into auto-wounds on 5s — the engine's trigger."),
    ("Castellan — Vehement Aggression", "re-roll Hit rolls (Ld pass) / re-roll 1s (Ld fail)", "more 5+ crits to convert; stacks onto the Marshal's unit."),
    ("Slayers of Abominations (Marshal's Household, 1CP)", "Sword Brethren melee vs MONSTER/VEHICLE: +2 S", "S5 -> S7; the anti-tank switch."),
    ("Emperor's Champion — Black Sword (Strike)", "S8 | AP-3 | D3 | A6 | [ANTI-CHARACTER 5+, PRECISION]", "the character-assassin (Precision picks out attached chars)."),
    ("--- BT's (thin) shooting ---", "", ""),
    ("Repulsor Executioner — Heavy Laser Destroyer", "S16 | AP-4 | D(D6+4) | A2 | [HEAVY]", "x2 (one per bus); wounds a Knight on 3s — the little AT-at-range there is."),
    ("Eradicator / Gladiator Lancer — melta & las", "melta S9 AP-4 D(D6) [MELTA 2]; Lancer las-class", "Oath-boosted reach for the un-chargeable — thin, because Marines shoot badly without Oath."),
]
