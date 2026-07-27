# -*- coding: utf-8 -*-
"""Black Templars — "TEMPLAR BASTION" LSO workup data. The friend's Bastion Task Force list, given
the same sim/analysis treatment as the others. Single source for the BT-Bastion Runbook + Excel.

Everything below is VERIFIED from data/bsdata + the SM/BT faction packs (the pilot corrected several
of my first-pass assumptions — all folded in here):
  * Detachment = BASTION TASK FORCE (generic SM defensive/auspex detachment, 3 DP for BT), run with
    BT units + Templar Vows.
  * BT army rule = TEMPLAR VOWS (NOT Oath of Moment). Default pick = ACCEPT ANY CHALLENGE (+1 to
    Wound in melee when S <= target's T); switch to Uphold the Honour (sticky objectives) only vs a
    majority-T3 army.
  * Repulsor Executioner INTERCEPTION STRIKE (BT datasheet rule): full Hit re-roll vs a target within
    12" of a friendly Astartes unit -> near-always on in a brick list.
  * Grimaldus: FNP 5+ is HIM + Cenobyte Servitors ONLY (not the led brick); the brick gets re-roll ALL
    melee Hits (Litanies) + one Temple Relic each Command phase (default: +1 AP via Water from the
    Stoup; alts +1 T / +1 Advance&Charge).
  * Hero of the Chapter (Marshal): the bearer gains BATTLELINE -> the Sword Brethren brick counts as
    Battleline (unlocks the whole detachment for it). Blades of Valour (EC): +1 AP melee for his
    Battleline unit. Combi-Lieutenant: Lone Operative + FNP 5+ + Priority Objective (army re-rolls
    Wound-1s near a nominated objective) + Evade and Survive (a reactive move in the enemy turn).
Points are the app's (v912). Regenerate: PYTHONPATH=tools:src python3 tools/gen_bt_bastion_docx.py && ... xlsx
"""
EVENT = "Lone Star Open (LSO) — 300+ players, Swiss"
GENERATED = "2026-07-27 (11E, post-Dataslate)"

LIST_NAME = "TEMPLAR BASTION — Black Templars · Bastion Task Force"
DETACHMENTS = "Bastion Task Force (3 DP) — the generic SM defensive/auspex detachment, run with BT units + Templar Vows"
DISPOSITION = ("Take and Hold — a hold-the-line brick army. It scores by HOLDING objectives and grinds the "
               "enemy down under stacked debuffs; it does not alpha or deliver.")
IDENTITY = (
    "A BLACK TEMPLARS HOLD-AND-GRIND CONTROL army — the opposite of the delivered-spike list. Lots of "
    "durable BATTLELINE bricks push onto objectives, generate AUSPEX SCANS, and the whole army re-rolls into "
    "the scanned target while the debuff toolkit (pin -2M/-2 charge, suppress -1 hit) blunts the enemy. Its "
    "removal is RELIABLE and needs no delivery: two Repulsor Executioners with INTERCEPTION STRIKE (full Hit "
    "re-rolls vs anything near your line) do the ranged work, and a crit-on-5 Lethal-Hits Sword Brethren brick "
    "(Marshal + Castellan, made Battleline by Hero of the Chapter) is the melee that cracks vehicles/monsters "
    "in the fight phase. Grimaldus's relic-buffed 20-Crusader anvil holds the middle; the Emperor's Champion "
    "is a Precision character-assassin; a Lone-Operative Combi-Lieutenant limpets a key objective. The Templar "
    "Vow (Accept Any Challenge) gives +1 to Wound when wounding UP, so the melee bites into tough targets. "
    "Durable + reliable + few bad matchups — its whole game is out-lasting and out-scoring, and its only real "
    "holes are being SLOW (a fast/kiting gun army out-manoeuvres it) and getting OUT-BODIED by a true horde.")

# (unit, count, wargear/role, ~pts) — app v912 values.
UNITS = [
    ("Emperor's Champion + Blades of Valour", "1", "WARLORD. Leads the 10 Assault Intercessors. Black Sword S8 AP-3->AP-4 D3 A6 [ANTI-CHARACTER 5+, PRECISION] -> character-assassin. Blades of Valour = +1 AP melee for his Battleline unit (chainswords AP-1->AP-2).", "105"),
    ("Assault Intercessor Squad", "10", "Bodyguard (Battleline). AP-2 chainswords (Blades of Valour), auspex-scan generator, advance-and-charge (Interlocking Tactics). Mobile scanning melee brick + the EC.", "150"),
    ("Chaplain Grimaldus (+3 Cenobyte)", "1", "Leads the 20-Crusader anvil. Litanies = re-roll ALL melee Hits (unit); Temple Relics (Command phase, default +1 AP / alt +1 T / +1 Adv&Charge). FNP 5+ on HIM + Cenobytes only.", "100"),
    ("Lieutenant (Support)", "1", "Stacks into the Crusader anvil — a support wound-buff character.", "45"),
    ("Crusader Squad", "20", "Bodyguard (Battleline). THE ANVIL: 20 bodies, 4 power fists (S8 AP-2->AP-3 w/ relic) + master-crafted power weapon. Re-roll all melee Hits (Grimaldus), +1 AP relic, Angels Defiant (-1 to wound). Sticky, hard to shift.", "290"),
    ("Marshal + Hero of the Chapter", "1", "Leads the Sword Brethren. INSPIRATIONAL EXEMPLAR: unmodified Hit of 5+ = Critical Hit. HERO OF THE CHAPTER: the Marshal gains BATTLELINE -> the whole Sword Brethren brick counts as Battleline (unlocks Interlocking Tactics + Bastion strats for it).", "100"),
    ("Castellan (Support)", "1", "Stacks into the Sword Brethren. VEHEMENT AGGRESSION: re-roll Hits -> more 5+ crits to convert via Lethal Hits.", "70"),
    ("Sword Brethren Squad", "10", "Bodyguard. THE HAMMER: 6 master-crafted power weapons [LETHAL HITS] + 2 thunder hammers (S8 [DEV]) + 2 twin lightning claws. With crit-on-5 + re-rolls + Accept vow (+1 wound up), it deletes vehicles/monsters IN MELEE (no invuln vs Questoris/Dominus). Battleline via Hero of the Chapter -> Light of Vengeance adds Sustained.", "260"),
    ("Lieutenant with Combi-weapon", "1", "LONE OPERATIVE + FNP 5+. Priority Objective Identified: nominate 1 objective -> the whole army re-rolls Wound-1s vs enemies near it. Evade and Survive: a REACTIVE move (Normal move in the enemy's turn when they end a move within 9\"). A near-unkillable objective limpet.", "95"),
    ("Intercessor Squad", "5", "Battleline objective holder + scanner; advance-and-shoot (Interlocking Tactics).", "80"),
    ("Assault Intercessors w/ Jump Packs", "5", "Battleline, deep-strike + advance-and-charge -> a mobile scanner / objective-grabber (x2 in the list).", "85"),
    ("Assault Intercessors w/ Jump Packs", "5", "2nd jump squad — reserve pressure / late-objective flex.", "85"),
    ("Repulsor Executioner", "1", "The gun: Heavy Laser Destroyer (S16 AP-4 D6+4) AT + Heavy Onslaught Gatling (A12 [Dev]) anti-infantry + multi-melta. INTERCEPTION STRIKE = full Hit re-roll vs anything within 12\" of a friendly unit. Reliable removal, every turn.", "265"),
    ("Repulsor Executioner", "1", "2nd gun platform (2nd Heavy Laser Destroyer + gatling). Two Interception-Strike RepExes = the army's dependable damage.", "265"),
]
LIST_TOTAL = ("1,995 / 2000 (the friend's build). EC 105 = base + Blades of Valour; Marshal 100 = base + Hero of "
              "the Chapter. Points are the app's (v912). Legality of the key tech verified: Hero of the Chapter "
              "grants BATTLELINE (Sword Brethren -> Battleline), Marshal & EC & Grimaldus & Lieutenant all legally "
              "lead their bricks, Combi-Lieutenant is a Lone Operative. Templar Vow = Accept Any Challenge.")

RULES = [
    ("Templar Vows — ACCEPT ANY CHALLENGE (the army rule; NOT Oath)", "BT don't get Oath of Moment; they pick ONE Templar Vow army-wide. Default = Accept Any Challenge: each melee attack where the attacker's S <= the target's T gets +1 to Wound. It helps you wound UP into tough things (vehicles/monsters/elites) — exactly where the melee bricks need help. Switch to Uphold the Honour (INFANTRY sticky objectives) only vs a majority-T3 army (where S>T means Accept does nothing)."),
    ("Interlocking Tactics (detachment rule) + AUSPEX", "BATTLELINE units can Advance/Fall Back and still shoot + declare a charge (+ do Actions). And whenever a Battleline unit attacks, pick one enemy unit it hit -> it's AUSPEX SCANNED; every model in your army re-rolls Hit rolls of 1 vs a scanned target. That's your army-wide accuracy engine (this list's substitute for Oath) + the mobility that lets the bricks reposition."),
    ("Interception Strike — the RELIABLE guns (Repulsor Executioner)", "BT datasheet rule: each RepEx re-rolls ALL Hit rolls when it targets a unit within 12\" of a friendly Astartes unit — in a brick army that's basically always on. So both Heavy Laser Destroyers (S16 AP-4 D6+4) + gatlings + multi-meltas fire re-rolling every turn: dependable ranged AT + anti-infantry with NO delivery risk. This is why the list is consistent."),
    ("The Sword Brethren HAMMER (crit-5 Lethal, made Battleline)", "Marshal (INSPIRATIONAL EXEMPLAR: unmodified Hit 5+ = Critical Hit) + Sword Brethren power weapons [LETHAL HITS] (crit -> auto-wound) + Castellan (VEHEMENT AGGRESSION re-roll) + Accept vow (+1 wound up) + 2 thunder hammers (S8 Dev). Hero of the Chapter makes it BATTLELINE, so LIGHT OF VENGEANCE (1CP) can bolt [SUSTAINED HITS 1] on top -> more crit-5s -> more auto-wounds. It cracks vehicles/monsters IN MELEE (Questoris/Dominus have no melee invuln). NOTE: no Slayers +2S here — that's Marshal's Household, a different detachment."),
    ("Grimaldus — the relic anvil (no unit FNP)", "Litanies of the Devout: the led unit re-rolls ALL melee Hits. Temple Relics (each Command phase, needs the Cenobytes): default WATER FROM THE STOUP = +1 AP for the unit's melee (power fists AP-2->AP-3, chainswords AP-1->AP-2); alts COLUMN = +1 Toughness (defensive pivot), BANNER = +1 Advance & Charge. FNP 5+ is Grimaldus + Cenobytes ONLY — the brick's durability is bodies + the relic + Angels Defiant, not FNP."),
    ("The debuff / control toolkit (Bastion stratagems)", "Layer onto the auspex scan: GUIDED DISRUPTION (pin: -2\" Move, -2 Charge), SHOCK BOMBARDMENT (suppress: -1 to Hit), CODEX DISCIPLINE (re-roll Hits, +Wound-1s vs scanned), LIGHT OF VENGEANCE (Lethal or Sustained vs scanned), ANGELS DEFIANT (a Battleline unit gets -1 to Wound vs attacks where S>T -> the key defensive tech), HERESY UNDONE (a non-Battleline unit advance+charge). ~1 strat/turn (CP-limited); pick the priority."),
    ("The Emperor's Champion — the scalpel", "Black Sword S8 AP-3 (AP-4 with Blades of Valour) D3 A6 [ANTI-CHARACTER 5+, PRECISION]. He alone picks out and kills an attached enemy Character in melee (Sigismund's Heir re-rolls a charge to reach a Character within 12\"). Save him for the enemy's key buff-character."),
    ("The Combi-Lieutenant — the objective limpet", "LONE OPERATIVE (can't be shot >12\") + FNP 5+ + Priority Objective (army re-rolls Wound-1s vs enemies near his nominated objective) + Evade and Survive (a REACTIVE Normal move in the enemy's turn when a unit ends a move within 9\"). Nearly impossible to shift; anchors a corner and buffs the army's wounding there."),
    ("What this list genuinely can't do", "(1) CATCH a fast/kiting gun army — everything is M6 foot bricks (advance-and-charge helps, but a Drukhari or a shooting-Knight list out-manoeuvres and shoots it off); (2) out-BODY a true horde (Orks) on primary. It's durable and reliable, so it has few bad matchups — but it wins the LONG game, not the tempo game."),
]

MINDSET = (
    "Play it as a patient CONTROL grinder, not a race. The plan: hold objectives with durable Battleline bricks, "
    "auspex-scan whatever's in front of you so the whole army re-rolls into it, and stack the debuffs (pin the "
    "melee threats off you, suppress the shooters) while the Interception-Strike RepExes and the crit-5 Sword "
    "Brethren delete the priority piece. Three disciplines: (1) DON'T over-extend the bricks — you win by holding "
    "and out-lasting, so make the enemy come to you and grind them under −1-to-wound (Angels Defiant) + the +1 T/AP "
    "relic; (2) SPEND the debuff strats on the thing that decides the turn (pin the charge that would break a brick, "
    "suppress the alpha); (3) use the EC + Combi-Lieutenant as scalpels — assassinate a key character, limpet a key "
    "objective. Accept the two bad matchups (fast kiting gun lists, true hordes) and grind everyone else.")

# ---- MATCHUPS: Templar Bastion vs the LSO-meta archetypes (BT's perspective) ----
# verdict in {FAV, EVEN, COIN, UNFAV, HARD} (matches the mc_bt_bastion_sim verdicts)
MATCHUPS = [
    dict(key="emperors-children", faction="Emperor's Children", archetype="Frenzied Host / Coterie (Defiler + swarm)",
         prev="High (9)", verdict="FAVOURABLE",
         deciding="You out-durable and out-grind the paper swarm: the +1 T/-1-to-wound bricks eat the Infractor/Daemonette melee, Interception guns delete a Defiler/turn (their only real anti-armour), and the crit-5 Sword Brethren + Accept vow crush the elites. Their AP-1/-2 volume is the wrong shape for your armour.",
         plan=["Interception RepExes delete a Defiler each turn; pin/suppress the Infractors off your line.",
               "Let the chaff break on the Grimaldus anvil (re-roll hits + relic + Angels Defiant); Sword Brethren counter-punch.",
               "EC Precision-kills a Lord Exultant/buff-char; hold primary and grind — they can't out-durable or out-score you."],
         watch="Fulgrim (Fights First) can trade into a brick before it swings — pin him (-2 charge) or bait him onto the anvil first."),
    dict(key="orks-green-tide", faction="Orks", archetype="Green Tide (~100 bodies)",
         prev="High (8)", verdict="UNFAVOURABLE (your hardest common matchup)",
         deciding="The one thing that beats a durable brick army: raw BODIES. ~100 Boyz out-score your holders on primary, and the flood blankets objectives your M6 bricks can't all cover. Your gatlings + Sword Brethren mow Boyz in bulk, but you can't clear 100 or out-body the tide.",
         plan=["Gatlings (A12 Dev, Interception re-rolls) + Sword Brethren + anvil mow Boyz; suppress the klaw-nob brick that cracks your armour.",
               "Hold 2-3 objectives hard (relic +1T anvil), concede the middle; the Combi-Lieutenant limpets a corner.",
               "Interception guns delete the Kill Rig/Stompa; race secondaries — you won't win the primary body-count."],
         watch="Getting out-actioned and out-bodied. Honest ~22% — minimise the margin, don't chase kills."),
    dict(key="admech", faction="Adeptus Mechanicus", archetype="Rad-Zone / Lords of the Forge gunline",
         prev="High (6)", verdict="FAVOURABLE",
         deciding="Their D6-damage anti-tank OVER-kills your bodies (waste) and Angels Defiant blunts the rest, while your Interception guns + Sword Brethren delete a Kataphron brick/turn and you out-body their low-model gunline. Advance-and-charge (Interlocking Tactics) closes the distance and their line folds in melee.",
         plan=["Interception RepExes delete a Kataphron brick each turn; suppress/pin the shooters (-1 hit, -2 move).",
               "Advance the Battleline bricks into the gunline (few melee bodies); Sword Brethren + power-fist Crusaders carve it.",
               "Out-score — hold with bodies once their shooting is tar-pitted in melee."],
         watch="Culexus/Callidus sniping your buff characters (Marshal/Grimaldus) — screen them with the bricks."),
    dict(key="tau-retaliation", faction="T'au Empire", archetype="Retaliation Cadre (fusion/rail alpha)",
         prev="High (5)", verdict="COIN-FLIP",
         deciding="This is where Bastion shines vs a melee list: you SURVIVE the alpha (2+ saves + Angels Defiant -1 to wound vs their high-S rail/fusion) AND you shoot BACK reliably (Interception RepExes, no delivery to strand). Suppress the suits, out-body, and grind — T'au fold in melee if you reach, and your guns punish them if they don't.",
         plan=["Weather the alpha behind durability; do NOT waste CP on nothing (their AP-4/-5 ignores armour anyway — lean on Angels Defiant + bodies).",
               "Interception guns delete a Riptide/Crisis brick each turn; SUPPRESS the markerlight Pathfinders + the alpha (-1 to hit).",
               "Advance the bricks; Sword Brethren crush anything that lingers; hold primary with bodies they can't shift fast enough."],
         watch="Rail/fusion Devastating Wounds spike through saves; spread bricks to limit mortal spillover. A real coin-flip — practise it."),
    dict(key="necrons-ctan", faction="Necrons", archetype="Awakened Dynasty (C'tan + Wraiths)",
         prev="Med (4)", verdict="COIN-FLIP",
         deciding="C'tan durability (4++/-1Dmg/reanim) blunts your removal and they out-grind on reanimating bodies; you can't table 3 shards. Your edge: reliable guns + the crit-5 Sword Brethren (Accept vow +1 wound) chip a C'tan, and you out-durable the rest. A grind you steal on objectives.",
         plan=["Focus ONE C'tan with guns + the Sword Brethren brick (spread chip just reanimates); EC snipes a Technomancer.",
               "Hold with the relic anvil + bodies; suppress the gauss to cut their return fire.",
               "Win on sticky primary + secondaries, not on the body-count."],
         watch="Reanimation refunding your chip, and their forced-battle-shock C'tan strat (test at -1 + mortals) hitting a key holder — focus-remove whole units."),
    dict(key="custodes", faction="Adeptus Custodes", archetype="Lions of the Emperor (elite melee)",
         prev="Med (4)", verdict="COIN-FLIP (lean favourable)",
         deciding="Elite mirror you edge on VOLUME + reliability: you have far more bodies, the Interception guns + crit-5 Sword Brethren delete a Caladius/Custodian brick, and the EC's PRECISION Black Sword duels their characters where their own attached chars can't cleanly answer. Angels Defiant + the anvil out-last their few models.",
         plan=["Guns + Sword Brethren delete a Custodian brick/turn; PIN the Wardens/Blade Champion off your line.",
               "EMPEROR'S CHAMPION vs their character (Precision + Anti-Character) = a real melee assassination.",
               "Out-body + hold; they have ~40 models, you have more + the auspex debuffs."],
         watch="Their melee out-damages a single brick head-on; gang two units + pin before you commit."),
    dict(key="blood-angels", faction="Blood Angels", archetype="Stormlance / Liberator jump alpha",
         prev="Med (4)", verdict="FAVOURABLE",
         deciding="A glass melee alpha into a durable hold-and-punish army is a good matchup for you: you RECEIVE the charge behind 2+/Angels Defiant + Grimaldus re-roll-hits, overwatch thins the drop, and you counter-punch with a fresh Sword Brethren brick + the EC. They fold once the alpha is spent; you don't.",
         plan=["Screen so DC/Sang Guard land 9\"+ out; gatling + Assault Intercessor overwatch thins them; SUPPRESS the alpha.",
               "Weather the charge on the anvil (Angels Defiant -1 wound); counter-charge the spent unit with the Sword Brethren + EC on their Priest/Lemartes.",
               "Out-grind and out-score — you're the durable one here."],
         watch="Getting a key brick charged before it can Angels-Defiant; hold the strat for the swing charge."),
    dict(key="dark-angels-deathwing", faction="Dark Angels", archetype="Deathwing Knights / Inner Circle",
         prev="Med (3-4)", verdict="COIN-FLIP (lean favourable)",
         deciding="Terminator mirror decided on primary: your Interception HLDs + the crit-5 Sword Brethren (Lethal auto-wounds SKIP the to-wound roll, grinding the 4++/-1Dmg mace brick better than normal attacks) chew the Deathwing, and you out-body + out-shoot. Both slow -> board position + the sticky anvil decide it.",
         plan=["Guns + Sword Brethren focus the Deathwing brick (Lethal-on-5 volume beats the 4++); the Lion is a Monster -> shoot him.",
               "PIN/suppress the mace brick to slow its advance; hold objectives + grind.",
               "Race primary; your body-count + reliable guns edge the mirror."],
         watch="Feeding a single brick piecemeal into the mace; commit with support + pin first."),
    dict(key="drukhari", faction="Drukhari", archetype="Skysplinter Assault (fast splinter + lance)",
         prev="Med (3)", verdict="UNFAVOURABLE",
         deciding="Speed is your kryptonite: they out-manoeuvre M6, kite the bricks, dark-lance the RepExes, and flip objectives late. Your armour + Angels Defiant tank the splinter fine and your guns shoot their paper down when they're near your line — but you CAN'T catch them, and a durable slow army loses the tempo game to pure speed.",
         plan=["Hold a tight castle + the Combi-Lieutenant limpet; make them commit into your bubble (their paper folds if it does).",
               "Interception guns one-shot Ravagers/Venoms to cut mobility + the lance threat; PIN what you can.",
               "Zone with screens + the jump squads so they can't backfield-raid; grind the secondaries you can hold."],
         watch="Out-actioned and out-scored by raw speed while the bricks chase air. ~34% — a real underdog game."),
    dict(key="astra-militarum", faction="Astra Militarum", archetype="Steel Hammer superheavy / artillery",
         prev="Low-Med (2)", verdict="FAVOURABLE",
         deciding="Their tanks are Interception-Strike food (2 Heavy Laser Destroyers re-rolling hits + multi-meltas delete a Russ/superheavy a turn) and their D6-damage guns over-kill your bodies (waste). You out-body the low-model tank line, advance-and-charge into the infantry, and hold.",
         plan=["Interception RepExes + Sword Brethren delete a Russ/Shadowsword each turn; suppress the artillery.",
               "Advance the bricks; power-fist Crusaders + Sword Brethren carve the Guard infantry.",
               "Out-body and out-score once the shooting is tar-pitted in melee."],
         watch="Artillery + Leontus orders chipping the bricks early; screen them to the first melee. Slight favour if you weather T1-2."),
]

BANDS = {
    "FAVOURABLE (bank these)": ["Emperor's Children", "AdMech", "Astra Militarum", "Blood Angels"],
    "COIN-FLIP (practice these)": ["Custodes (lean fav)", "Dark Angels (lean fav)", "T'au Retaliation", "Necrons C'tan"],
    "UNFAVOURABLE (underdog)": ["Drukhari Skysplinter (speed)", "Orks Green Tide (bodies)"],
    "STRUCTURAL BOGEY (off-meta)": ["Shooting-dominant Knights that KITE the slow bricks — same axis as Drukhari"],
}
RECORD_NOTE = (
    "Templar Bastion is a STRONG, CONSISTENT hold-and-grind list — ~55% prevalence-weighted, and notably more "
    "reliable than the delivered-spike BT build because its removal (Interception guns) needs no delivery and its "
    "durability (Angels Defiant + relic + bodies) has few bad matchups. Realistic 300+ GT: a solidly positive "
    "record with a high floor — it rarely gets blown out. It wins by DURABILITY + RELIABLE REMOVAL + auspex "
    "control, holding primary and grinding the enemy under debuffs. Its ceiling is capped by ONE axis: SPEED. "
    "Everything is M6 foot bricks, so a fast/kiting gun army (Drukhari in the meta; a shooting-dominant Knight "
    "list off-meta) out-manoeuvres it and plays the objectives it can't reach — and a true horde (Orks) out-bodies "
    "it. Against everything that stands and fights, it grinds them down. A genuine tournament list, not a gimmick.")

VERIFIED_PROFILES = [
    ("--- reliable guns (Interception Strike, full Hit re-roll) ---", "", ""),
    ("Repulsor Executioner — Heavy Laser Destroyer", "S16 | AP-4 | D(D6+4) | A2 | [HEAVY]", "x2; wounds a Knight on 3s. Interception Strike = re-roll ALL hits vs targets near your line."),
    ("Repulsor Executioner — Heavy Onslaught Gatling", "S6 | AP0 | D1 | A12 | [DEVASTATING WOUNDS]", "anti-infantry volume; Dev crits = mortals."),
    ("Repulsor / Eradicator — Multi-melta", "S9 | AP-4 | D(D6) | [MELTA 2]", "close-range AT top-up."),
    ("--- the melee hammer (Sword Brethren brick) ---", "", ""),
    ("Sword Brethren — Master-crafted Power Weapon", "S5 | AP-2 | D2 | A3 | [LETHAL HITS]", "crit-on-5 (Marshal) -> auto-wounds; +1 to wound up (Accept vow)."),
    ("Sword Brethren — Thunder Hammer", "S8 | AP-2 | D2 | A3 | [DEVASTATING WOUNDS]", "x2; Dev crit-wounds = mortals into tough targets."),
    ("Marshal — Inspirational Exemplar", "unmodified Hit of 5+ = Critical Hit (its unit)", "the crit-5 trigger for Lethal Hits."),
    ("Emperor's Champion — Black Sword (Strike)", "S8 | AP-4 (Blades) | D3 | A6 | [ANTI-CHARACTER 5+, PRECISION]", "the character-assassin."),
    ("--- the vow + the control layer ---", "", ""),
    ("Templar Vow — Accept Any Challenge", "melee: +1 to Wound when S <= target's T", "helps you wound UP into vehicles/monsters/elites."),
    ("Bastion strats", "Guided Disruption (pin -2M/-2chg), Shock Bombardment (suppress -1 hit), Angels Defiant (-1 to wound vs S>T), Light of Vengeance (Lethal/Sustained)", "the debuff/control toolkit on the auspex scan."),
]
