# -*- coding: utf-8 -*-
"""Shared data for the LSO Knights deliverables (Excel analysis + Word runbook).
Distilled from docs/meta/*.md + MEMORY.md (11E-verified, 2026-07-26). Single
source of truth so the .xlsx and .docx stay consistent. Regenerate the docs after
editing:  PYTHONPATH=tools python3 tools/gen_lso_xlsx.py && ... gen_lso_runbook_docx.py
"""

EVENT = "Lone Star Open (LSO) — 300+ players, Swiss"
GENERATED = "2026-07-26 (11E, post-Dataslate)"

# ---- THE LIST (user-decided: DOMINATE the shooting phase) ----------------------
LIST_NAME = "Knights — 2 Castellan / 1 Lancer / 1 Crusader (shooting-dominant)"
DETACHMENTS = "Valourstrike Lance + Dominus Foebreakers (3 DP)"
DISPOSITION = ("Purge the Foe (RECOMMENDED for the broad field) — or Priority Assets. "
               "Take-and-Hold is NOT legal for this combo (only Valourstrike's Purge + "
               "Dominus's Priority Assets are granted). Purge rewards killing (the list's "
               "identity) and only 1/5 of its missions needs an Action; Priority Assets is "
               "an action-heavy trap for a 5-6-model army (25 VP in Actions you can't spare). "
               "Lock Priority Assets ONLY if you expect the Great-Value Vital-Link home-steal.")
LIST_RATIONALE = (
    "Firepower-as-denial is the Knight win-con. TWO Volcano lances (S18 AP-5 D6+8) + "
    "plasma decimators + the Crusader's RFBC/Avenger = a shooting core that deletes "
    "no-invuln anchors and strips soft OC. The SINGLE Cerastus Lancer (4++ full invuln, "
    "M14) is the one decapitation / counter-charge blade. User law: do NOT trade a "
    "Castellan's worth of shooting for a 2nd Lancer. RE-VERIFIED (2026-07-26): 1 Lancer is "
    "correct — the shooting kills melee linchpins at range before they connect; a 2nd Lancer "
    "surrenders a Volcano the hard shooting/OC matchups need, and even 2 blades can't heist a "
    "4++ brick wall. Both Castellans carry DOMINUS, so Dominus Foebreakers actually buffs TWO "
    "Knights here (an edge over the 2-Lancer variant)."
)
# (unit, count, wargear, ~pts, role)
LIST_UNITS = [
    ("Knight Castellan", 2, "Volcano lance (D3 shots S18 AP-5 D6+8), plasma decimator (D6+3 shots), 2x twin meltagun, 2x shieldbreaker, twin siegebreaker, feet",
     "425 + 450", "The shooting core (escalating: 1st 425, 2nd 450). 2x Volcano (D3 shots ea, ~23 dmg) one-shots no-invuln anchors + snipes; plasma decimator anti-elite; +1 hit vs terrain (Dominus). #1 bears Archeotech Autoloaders (re-roll the shot count on the D3/D6+3 guns)."),
    ("Knight Crusader", 1, "Rapid-fire battle cannon (D6+3 S10, +15pts), Avenger gatling (A18 S6 AP-2 D2), heavy flamer, thermal cannon (2D3 S12 AP-4 Melta6), stubber, feet",
     "410", "395 base + 15 for the RFBC. Anti-infantry SUBTRACTION: RFBC + Avenger A18 strip soft OC; thermal for anti-tank/Speeders."),
    ("Cerastus Knight Lancer", 1, "Shock lance — strike 5A S20 AP-3 D8 [Lance] / sweep 10A S10 AP-2 D3; ranged shock lance 12\" 6A [Assault, Sus2]",
     "415", "The one blade: 4++ FULL invuln vs ALL, M14 W28. Counter-charge + assassinate buff-characters + Shock-Charge free Tank Shock on the charge."),
    ("Armiger Helverin", 1, "2x Armiger autocannon (48\" A4 S9 AP-1 D3), heavy stubber", "140",
     "Backfield 48\" autocannon platform + OC6 screen."),
    ("Navigator (Agents ally)", 1, "Gaze of the Empyrean", "75",
     "12\" anti-Deep-Strike dome (vs BA/SW/GSC/deep-strike alphas) + Hidden home-holder. Allies take no enhancement. (75 confirmed from Scott Ketcham's Tacoma roster.)"),
]
# ★ POINTS FROM MFM (user-authoritative, 2026-07-26): Castellan escalates 425/450, Crusader 395 +15 RFBC = 410.
# ALWAYS use the MFM for points — they're all there incl. enhancement costs + escalating duplicate costs.
# ALL points MFM-confirmed via the live SSR (data/mfm/imperial-knights.json). BSData was STALE (priced Castellan 400).
ENHANCEMENTS = [
    ("Archeotech Autoloaders  [TAKEN — Castellan #1]", "Knight Castellan", "25",
     "Re-roll the number of Attacks (shots) of a weapon — huge on the Volcano lance (D3 shots) and plasma decimator (D6+3), turning low shot-rolls into full salvoes. The shooting-dominant enhancement."),
    ("Blessed Plate  [TAKEN — Castellan #2]", "Knight Castellan", "30",
     "Castellan -> T13: pushes S12-13 anti-tank (rail / ferrumite / lascannon / Caladius / thermal) from wounding on 4+ to 5+ — survivability for the second Volcano platform."),
]
LIST_TOTAL = ("1,970 / 2000 (30 spare) — MFM points: Castellan 425 + 450 (escalating) + Crusader 410 (395 +15 "
              "RFBC) + Cerastus Lancer 415 + Armiger Helverin 140 + Navigator 75 = 1,915, + Archeotech Autoloaders "
              "25 + Blessed Plate 30 = 1,970. ONE Armiger (the correct build — the earlier '2 Armiger' was an "
              "error from stale BSData points). NO Lancer's Sigil. All points MFM-verified (1,970/2000 from data/mfm/imperial-knights.json).")

# ---- KEY RULES / CHEAT-SHEET ----------------------------------------------------
RULES = [
    ("Ion Shield", "5++ invuln vs SHOOTING ONLY (ranged). Does NOTHING in melee."),
    ("Rotate Ion Shields", "VALOURSTRIKE 1CP STRATAGEM: +1 to a Knight's invulnerable save vs SHOOTING (5++ -> 4++) for the phase. The core durability lever in the hard shooting matchups — cycle it onto the focused Knight each turn. (Stratagems ARE the detachment: how Valourstrike actually plays.)"),
    ("Questoris/Dominus melee", "NO melee invuln (verified — printed 5+* is 'vs ranged attacks only') — bare 3+ armour in the fight phase. Melee is the universal Knight weakness (only the Sanctuary enhancement adds a melee 5++)."),
    ("Cerastus Lancer", "VERIFIED 415pts, M14 T11 W28, 4++ invuln vs ALL attacks (no asterisk). Shock lance STRIKE 5A WS2+ S20 AP-3 D8 [Lance] (wounds anything <=T12 on 2s) / SWEEP 10A S10 AP-2 D3. Shock Charge = free Tank Shock (0CP, repeatable) on the charge = bonus MW. The universal counter-charge + character-assassin."),
    ("Volcano lance", "VERIFIED 72\" D3 SHOTS (avg 2), S18 AP-5 D6+8 [Blast] — ~23 dmg/turn; one-shots no-invuln anchors (Hammerheads T10, Land Raiders T12, Kataphrons, Shadowsword, no-invuln Norns/Emissaries). Overkill into low-W chaff. The Castellan is 425/450 pts (escalating: 1st 425, 2nd 450 — MFM)."),
    ("Bold Gallantry (Valourstrike)", "Any Knight Advances -> ALL Knight ranged weapons gain [ASSAULT] army-wide that turn (advance-and-shoot)."),
    ("Rain of Devastation (Dominus)", "Dominus Knights' attacks vs a unit in a terrain area get +1 to hit."),
    ("Super-Heavy Walker", "Movement-only. NO Knight falls back and shoots — an engaged Knight instead shoots OUT of combat at -1 to hit (tar-pit costs -1)."),
    ("What beats Knights", "(1) invuln-NEGATION: Anti-Vehicle/Monster X+ (wound regardless of S) + Devastating Wounds (crit->mortal); (2) massed AP-2+ VOLUME (5++ fails 68%); (3) MELEE into the no-invuln fight phase; (4) out-OC / out-score."),
]

MINDSET = (
    "Knights are 'always outnumbered, rarely outgunned.' At a 300+ GT, START every hard "
    "matchup from the EXPECTATION OF A LOSS and hunt the HEIST. Model the opponent playing "
    "OPTIMALLY. Realistic goal: a strong POSITIVE record + steal a couple you shouldn't win — "
    "not winning the event. The 2 Volcano lances win the shooting phase; the Lancer wins the "
    "melee phase you can't tank; you win the game on the mission (out-OC where you can)."
)

# ---- MATCHUPS / BATTLE PLANS ----------------------------------------------------
# verdict in {FAVOURABLE, COIN-FLIP, UNFAVOURABLE, HARD-LOSS, AUTO-LOSS, PRELIM}
# fields: key, faction, archetype, prev(H/M/L), verdict, deciding, heist[list], kill_priority, deploy
MATCHUPS = [
    dict(key="necrons-cursed-legion", faction="Necrons", archetype="Cursed Legion (18 Lokhust Destroyer gauss-spam)",
         prev="High", verdict="UNFAVOURABLE", disp="Purge / Recon",
         deciding="54 gauss cannons S7 AP-2 D2 Lethal (~kills a Knight/turn through Rotate) + un-killable Void Dragon (4++/-1Dmg/reanim) + reanimation refunds chip + out-OC.",
         heist=["Erase a full 6-model Destroyer unit T1 (Volcano/thermal — T6/no-invuln) — each removed = ~12 anti-Knight dmg off the table.",
                "Rotate the focused Knight every turn; body-block so a 2nd Knight is never offered.",
                "Do NOT chase the Void Dragon (tar pit that heals off your hulls) — screen it away from melee; Lancer duels/pins it.",
                "Win on tempo/objectives before the reanimate economy buries you. ~20-30% game — a heist, not a matchup."],
         kill_priority="Lokhust Destroyer units -> Reanimators -> soft characters (NOT the Void Dragon).",
         deploy="Terrain/LOS so the gunline sees ONE Knight at a time. Volcano priority = the Destroyers, not the C'tan."),
    dict(key="necrons-awakened-ctan", faction="Necrons", archetype="Awakened Dynasty (triple-C'tan spam)",
         prev="High", verdict="COIN-FLIP (lean unfavourable)", disp="Take and Hold",
         deciding="3 un-killable C'tan (4++/-1Dmg/Reanim). Nominally I out-hold OC4 with OC10 — BUT they're M10 FLY and reanimate, so 'out-OC' is shakier than it looks; win on POINTS not tabling, and don't over-trust the OC math.",
         heist=["Screen the Void Dragon (Anti-Vehicle 2+ wounds any Knight on 2s + heals off your hulls) away from melee.",
                "Lancer duels/pins the Nightbringer (4++ trades favourably; keeps the Dev scythe off a Questoris).",
                "Focus-fire ONE C'tan per turn to the floor (chip is refunded — overkill past reanimation); never split.",
                "Win the OBJECTIVE race: OC10/OC6 vs OC4, Tank Shock, out-hold. Grindy points win."],
         kill_priority="None of the 3 C'tan get tabled — out-hold. Snipe Szeras / Skorpekh Lords if they lose Lone-Op screening.",
         deploy="Play the mission, not the dice. Contest/flip the C'tan's objective with OC10."),
    dict(key="necrons-monolith", faction="Necrons", archetype="Obeisance / Monolith spam (faded)",
         prev="Low", verdict="COIN-FLIP", disp="Various",
         deciding="3x Monolith T13 W22 2+ NO invuln + reanim. Monoliths ARE killable (Volcano wounds T13 on 3+, AP-5 through 2+; shieldbreaker Anti-Titanic 4+). 12 death rays chunk.",
         heist=["Concentrate ALL fire on ONE Monolith/turn — remove it outright (~27-33 focused beats ~2 reanim); never chip.",
                "Kill the Silent King early (reroll-1s + move engine, killable T10 W16).",
                "Rotate every turn; the Monoliths are M8 slow — kite and out-manoeuvre."],
         kill_priority="One Monolith at a time -> Silent King -> the rest.",
         deploy="Concentrate-to-kill; spreading fire feeds reanimation."),
    dict(key="dark-angels-ravenwing", faction="Dark Angels", archetype="Darkflight/Ravenwing bike swarm",
         prev="High", verdict="UNFAVOURABLE", disp="Disruption",
         deciding="27 supercharged plasma talons (S9 AP-3 D2) + Chaplain 'Catechism of Fire' = Dev-Wound plasma (bypasses ion shield) + ~90 M12 bikes out-OC + fall-back-and-shoot.",
         heist=["Kill the STORM SPEEDER THUNDERSTRIKE first (Volcano) — it's the +1-to-wound MARK engine that makes the plasma volume lethal; remove it and the alpha drops from 'dead Knight' to 'chunked'.",
                "Deny the 9\" bubble: deploy behind LoS blockers >24\" back; keeping bikes >9\" drops plasma from RF (3 shots -> 2) and halves the Dev math.",
                "Delete whole Black Knight packs with Avenger/thermal/RFBC BEFORE they get Catechism range; pop the 3 ATVs + Scouts (deny actions).",
                "Lancer = backfield linebacker hunting Scouts/ATVs/Command (not a centre dive — expect it kited by fall-back-shoot). Wall lanes with the hulls; win the ONE point OC10 owns. Bottom-tier matchup."],
         kill_priority="Storm Speeder Thunderstrike (mark engine) -> Black Knight packs -> ATVs -> Scouts.",
         deploy="LoS-block deep; their alpha is huge (Recon-Hunter Scouts 9\" + M12 + Assault)."),
    dict(key="dark-angels-deathwing", faction="Dark Angels", archetype="Deathwing Terminator brick",
         prev="Medium", verdict="COIN-FLIP", disp="Take and Hold",
         deciding="3x un-tableable OC1 bricks (W4 2+/4++ -1Dmg + Armour of Contempt) — but I OUT-OC with OC10, and the killable scorers (Repulsor W16 no-invuln, Eradicators, Sternguard) die to my guns.",
         heist=["Out-OC: an OC10 Knight beats a whole OC5-8 brick on any objective — don't try to table the bricks, out-hold them.",
                "Delete the Repulsor (W16, dead in a turn), Eradicators + Sternguard + Scouts (W2-3) with volume guns.",
                "Never feed a Knight into a brick's charge — shoot OUT at -1 or fall back; Lancer counter-charges.",
                "Win the primary on raw OC."],
         kill_priority="Repulsor -> Eradicators -> Sternguard -> Scouts (the killable scorers; ignore the bricks).",
         deploy="Screen the Deathwing deep-strike (Navigator dome); out-OC bodies."),
    dict(key="space-wolves", faction="Space Wolves", archetype="Librarius Conclave Terminator/Wulfen deathstar",
         prev="Medium", verdict="UNFAVOURABLE", disp="Take and Hold",
         deciding="8 Assault-Terminator thunder hammers (S8 AP-2 D2 DEV) crack the no-melee-invuln Questoris (~12-14/charge); Sternguard Fusillade (Anti-Veh 5+ + Dev) punches the ion shield; out-bodies/out-OCs. (Half its melee is duds: Wulfen S5, Blood Claws S4.)",
         heist=["Lancer counter-charge: its 4++ survives the hammers a Questoris can't; hold it to trade INTO a landed brick.",
                "BRICK-WALL CAVEAT: assassinating Logan/Ragnar/Librarians is only MARGINAL — it doesn't collapse a faceless 4++ wall. Kill a multiplier only if it strips a real buff; otherwise don't over-commit the Lancer.",
                "Focus-kill one brick BEFORE it lands (deep-strike + Celerity advance-charge); screen the drop with the Navigator dome + Helverin.",
                "SW terminators are M5-6 on foot — refuse-flank, out-OC where you can, race secondaries. Near hard-loss."],
         kill_priority="Thunder-hammer Assault Terminators -> buff characters only if it strips a live multiplier.",
         deploy="Screen deep-strike lanes; keep Knights >9\" from Teleport Homers."),
    dict(key="blood-angels", faction="Blood Angels", archetype="Liberator Assault Group / Angelic Host jump-melee alpha",
         prev="Medium", verdict="UNFAVOURABLE", disp="Take and Hold",
         deciding="Red Thirst (+2 S/+1 A on the charge) -> Death Company S10 fists, Sanguinary Guard S8 AP-3, Dev hammers; ~15-18 into a Questoris from one DC+Lemartes charge (no melee invuln); best-in-game delivery (M12 + Deep Strike + re-roll charge + Angelic-Host re-drop).",
         heist=["Deny the alpha, don't fight it: layered chaff/bubble-wrap so DC land 9\"+ out, eat overwatch, can't reach T2. Castle T1-2.",
                "Avenger gatling OVERWATCH the drop (A18 S6 AP-2 into 2W-T4 DC) thins it before it swings.",
                "Lancer = counter-charge assassin: blank the multipliers — Lemartes (-1 Dmg), Sanguinary Priests (FNP5+/+1AP), Chaplains (strip Black Rage -> DC go OC0, can't Fall Back).",
                "Win on the MISSION: out-OC massively (OC10/6 vs OC1 infantry). Do NOT try to table them."],
         kill_priority="Lemartes -> Sanguinary Priests -> Chaplains (the buff engine) -> Death Company as it lands.",
         deploy="Navigator dome + chaff screen the deep strike; never present an unscreened Knight to a 12\"+charge."),
    dict(key="thousand-sons", faction="Thousand Sons", archetype="Grand Coven",
         prev="Medium", verdict="FAVOURABLE", disp="Priority Assets",
         deciding="Psychic-MW is THROTTLED in 11E (~5/turn via Doombolt, not spam); Rubrics are warpflamer anti-infantry (bounce off Knights); AP-2 volume is only S4. MAGNUS (T11 W16 2+/4++, S16 AP-3 Dev melee, two-rounds a Questoris) is the ONLY Knight-killer.",
         heist=["Refuse OR kill Magnus: screen and body-block his 14\"+Time-Flux threat with an Armiger, OR dump a turn of Volcano+gatling into him (4++ + Impossible Form -1Dmg stretches it to ~2 turns).",
                "Keep Ion Shields up — the rest of the list literally lacks the S/AP to punch 26-28W Knights.",
                "Kill Sorcerers (throttle Doombolt) with the Avenger/RFBC; clear Rubrics/Scarab with volume.",
                "Out-OC on Priority Assets. Best matchup on the board (~55-60/40)."],
         kill_priority="Magnus (or refuse) -> Sorcerers (the ritual engine) -> Rubric/Scarab bodies.",
         deploy="Don't feed an unscreened Knight to Magnus's melee. Watch Shadow Puppeteer (-1 to hit your best gun)."),
    dict(key="grey-knights", faction="Grey Knights", archetype="Banishers / Argent Assault (PRELIMINARY)",
         prev="Low", verdict="PRELIM", disp="Purge",
         deciding="PRELIM — not deep-verified. Elite 2+/4++ Terminators/Paladins + psychic Smite MW + best-in-game teleport/deep-strike. Likely coin-flip -> mild-unfav for Knights (MW + melee into no-invuln fight phase), hard for Sisters.",
         heist=["Kill the casters/character support to throttle the MW; screen the teleport (Navigator dome).",
                "Lancer counter-charge + assassinate a Grand Master/Librarian; out-OC (their bodies are few/OC1).",
                "NEEDS A FULL PASS before LSO — treat as provisional."],
         kill_priority="Casters/characters -> Paladins/Terminators. (Provisional.)",
         deploy="Screen deep-strike; provisional."),
    dict(key="csm-renegade-raiders", faction="Chaos Space Marines", archetype="Renegade Raiders",
         prev="Medium", verdict="COIN-FLIP", disp="Reconnaissance",
         deciding="Record built on OBJECTIVES, not killing Knights. Anti-Knight is CONCENTRATED and killable: Vashtorr (Anti-Veh 4+ Dev hammer + +2 S aura to a Daemon-Vehicle Defiler) + Lord Discordant (free MW faucet). Dark Pacts = Lethal Hits.",
         heist=["T1: Lancer + a Volcano into VASHTORR before he beds into the Defiler's 3\" Lone-Op bubble — one kill, two problems (he's the assassin AND the Defiler's +2 S battery).",
                "Kill the Lord Discordant next (T9 W10 4++) to shut off the free MW + wound-reroll enabler.",
                "Delete the killable chassis (Rhinos/bikes/Noise Marines); never sit engaged ON an objective (+1 AP near objectives).",
                "Out-tempo (you can't out-spread on Recon) — ~50/50."],
         kill_priority="Vashtorr -> Lord Discordant -> Defiler -> killable scorers.",
         deploy="Don't clump kills near a Vengeance-style reactive piece; watch Dark-Pact Lethal Hits."),
    dict(key="emperors-children", faction="Emperor's Children", archetype="Frenzied Host + Court of the Phoenician",
         prev="Medium", verdict="EXPECT-A-LOSS (winnable)", disp="Priority Assets",
         deciding="Elite MELEE. Fulgrim (T11 W16 2+/4++, -1 to hit, Fights First) deletes a Knight/turn AND shrugs your guns (~2 dmg/Volcano shot). Defiler + Flawless Blades (AP-4) butcher. Thrill Seekers = advance-and-charge threat ranges.",
         heist=["CONCEDE Fulgrim: body-block his lane with an Armiger/wreck so he reaches ONE target/turn, never the same Knight twice. Do NOT Rotate vs him (useless in melee) and do NOT try to kill him.",
                "T1-2: shoot the SUPPORT melee off before it connects — Defiler (5++, no -1-to-hit, dies to concentrated Volcano/thermal), then Flawless Blades + Noise Marines with the Avenger.",
                "Win on PRIMARY: Priority Assets, OC10 Questoris sit on objectives; Lancer runs down the cheap OC screen (Spawn/Noise Marines) — trade a Knight/turn to Fulgrim while out-scoring the defanged swarm.",
                "Close primary loss / draw-range if executed; blowout if Fulgrim reaches two Knights a turn."],
         kill_priority="Defiler -> Flawless Blades -> Noise Marines / Infractors (NOT Fulgrim).",
         deploy="Screen Fulgrim's lane; keep the Lancer for a Lord Exultant, not Fulgrim (4++ + Beguiling)."),
    dict(key="drukhari-skysplinter", faction="Drukhari", archetype="Skysplinter Assault + Exhibition of Slaughter",
         prev="Medium", verdict="FAVOURABLE", disp="Reconnaissance",
         deciding="Durability mismatch in MY favour: Volcano one-shots their no-invuln Raiders/Ravagers (T8-9); their Incubi/Exhibition Lethal Hits are NON-Vehicle (don't touch Knights); no haywire = thin invuln-bypass. 13 dark lances chip ~1 Knight/turn but can't table me.",
         heist=["Kill the two Scourge units (8 of 13 lances) first, then the Ravager (Volcano one-shots) and Lady Malys.",
                "Rotate the focused Knight (make their lances fail on 1/2, not 2/3).",
                "Contest-don't-chase: they out-spread me on Recon with ~90 fast bodies — plant OC10 on the 2-3 objectives that matter, gun their scorers off the rest.",
                "Weather the T2 lance alpha (hull-down T1) and grind their paper army off T3-5."],
         kill_priority="Scourges -> Ravager (lances) -> Lady Malys -> Raiders/Venoms.",
         deploy="Reserve/hull-down T1 to blunt the lance alpha; don't over-expose."),
    dict(key="custodes", faction="Adeptus Custodes", archetype="Lions of the Emperor + Might of the Moritoi",
         prev="Medium", verdict="FAVOURABLE", disp="Take and Hold",
         deciding="'So few models' (~40, tanky-per-model 2+/4++ but W2-4). Anti-Knight is THIN (one Caladius ~6/turn; guardian spears S7 wound me on 5+). Might of the Moritoi is Walker-only = dead (no Dreadnoughts). I OUT-OC (OC10 vs OC2) + grind them off.",
         heist=["Volume guns (Avenger A18 / RFBC / plasma) into the Custodian bodies — do NOT Volcano a W3 Custodian (overkill); save Volcano/thermal for the Caladius + characters.",
                "Lancer SWEEP (A10 S10 AP-2 D3) chews Custodes squads (wounds T6 on 2+).",
                "Out-OC every objective (OC10 vs OC2) and table their ~40 models over the game — the removal race is winnable.",
                "Just dodge their melee (S5-7 butchers if it connects)."],
         kill_priority="Caladius (their one gun) -> characters -> bodies with volume.",
         deploy="Out-body/out-OC; right gun per target (volume into bodies, big guns into the tank)."),
    dict(key="votann", faction="Leagues of Votann", archetype="Delve Assault Shift + Hearthguard Covenant / Hearthband",
         prev="Medium", verdict="COIN-FLIP", disp="Priority Assets",
         deciding="Judgement Tokens DON'T exist in 11E (army rule = Prioritised Efficiency, +1 Hit near objectives). Their SHOOTING can't crack me (2 Heavy magna-rail cannons). The danger is the deep-striking Cthonian Beserk maul-swarm — mauls have ANTI-VEHICLE 3+ (wound me on 3s) in the no-melee-invuln fight phase.",
         heist=["Never expose a lone Questoris to a 9\" Beserk drop-charge (re-rollable via Yield Points): screen with the Armiger, hug terrain, keep big Knights back T1-2.",
                "Kill BOTH Land Fortresses T1-2 (T12 W16 no-invuln — Volcano ~one-shots) -> removes their entire anti-tank; then their shooting is harmless.",
                "My guns delete the T6 W1 Beserks wholesale (feet + gatling); Lancer 4++ tanks the maul swarm and breaks blocks.",
                "Race the clock before they hit 7 Yield Points; contest, don't sit."],
         kill_priority="Land Fortresses -> Berehk / Kahl -> Beserks with volume.",
         deploy="Screen the deep-strike landing zones; a Beserk that can't charge does nothing."),
    dict(key="tyranids-norn", faction="Tyranids", archetype="Talons of the Norn Queen + Assimilation Swarm (5-Norn)",
         prev="Medium", verdict="COIN-FLIP", disp="Take and Hold",
         deciding="5 Norns (T11 W16, M10) with Singular Purpose OC15 ANCHORS (out-hold me), harpoon melee (S12 AP-3 into no-invuln Questoris), and healing. Emissaries have NO invuln (Volcano one-shots); Assimilators are 4++.",
         heist=["Focus-kill the no-invuln Emissaries at RANGE (Volcano/thermal one-shot); grind the 4++ Assimilators.",
                "OC15 anchors mean the primary is a KILL-RACE, not an OC race — I must physically remove the anchoring Norn to take its objective.",
                "Refuse the melee gang: kite on M10-14, never let 2+ Norns pile one Knight; Lancer assassinates a Norn on the charge.",
                "Kill the Neurotyrant + Zoanthropes (synapse/heal/psychic engine); win on kills + secondaries."],
         kill_priority="Emissaries (no-invuln) -> Neurotyrant / Zoanthropes -> Assimilators (grind).",
         deploy="Space to deny the harpoon hook-and-charge (+2 to their charge); don't cluster."),
    dict(key="tau-prototype-cadre", faction="T'au Empire", archetype="Experimental Prototype Cadre + Kauyon",
         prev="Medium", verdict="UNFAVOURABLE", disp="Priority Assets",
         deciding="The ceiling anti-Knight SHOOTING: railguns (S20 AP-5 D6+6 DEV WOUNDS — crit-mortals bypass the ion shield) + markerlight-boosted AP-3 volume + 6 Farsight fusion + rail rifles (Dev). A markerlit Kauyon alpha = ~30-40 into one Knight (dead, Rotated or not). Fire-and-Fade evasion neuters my melee.",
         heist=["Kill the HAMMERHEADS (2 railguns, T10 W14 NO invuln — Volcano deletes one/turn) + the Sunforge fusion suits (T5 W4) EARLY.",
                "Deny the Kauyon+markerlight alpha turn: terrain/reserves/LoS so they can't focus an un-Rotated Knight.",
                "Rotate the most-lit Knight; never present a clean focus target; their guns are the wrong-shaped for chaff but Dev/railgun bypass the invuln.",
                "Out-OC on Priority Assets IF I survive — their OC is modest. Expect to be behind; steal on tempo."],
         kill_priority="Hammerheads (railguns) -> Sunforge (6 fusion) -> Riptides/Ghostkeels -> markerlight Pathfinders.",
         deploy="Reserves + LoS-block vs the Kauyon turn; kill the mark/railgun platforms first."),
    dict(key="admech-rad-zone", faction="Adeptus Mechanicus", archetype="Lords of the Forge + Rad-Zone Corps",
         prev="Medium", verdict="UNFAVOURABLE", disp="Priority Assets",
         deciding="Kataphron Breachers' Heavy arc rifles = ANTI-VEHICLE 4+ (wound my T11-12 on 4+ regardless of S) + Lethal Hits + Cawl reroll -> 2 bricks = ~1 dead big Knight/turn, negating both my pillars (T beaten on 4+, 5++ fails 68%). Rad-Zone = chip-MW/battle-shock, NO Toughness reduction. Out-bodied.",
         heist=["Range-deny: Heavy arc rifle wants 15\" (Rapid Fire 2 doubles its shots); Kataphrons are M5\" SLOW. Deploy behind terrain, stay outside 15\" BR1, Rotate the exposed Knight.",
                "Win the race on ONE brick: Kataphrons have NO invuln/FNP -> dump all guns + a charge to remove a 6-model brick BR1-2 (cuts anti-Knight output ~40%). Don't spread fire.",
                "Lancer as a wrecking ball INTO a brick (shreds T7 W3 + pins them so they shoot the Lancer, not the gun-Knights).",
                "Concede the OC war; keep it close, need Hazardous plasma self-wounds + Rotate to swing."],
         kill_priority="One Kataphron brick at a time -> Cawl/Manipulus (if reachable).",
         deploy="Stay outside 15\"; kill the first brick before it doubles up."),
    dict(key="orks-kult-of-speed", faction="Orks", archetype="Kult of Speed / More Dakka",
         prev="Medium", verdict="UNFAVOURABLE", disp="Disruption",
         deciding="Fast dakka: 18 Deffkopta rokkits + Speshul Ammo ([Anti-Vehicle 4+] wounds T11-12 on 4s regardless of S) + Mobile Dakkastorm (+2 S). ~1 Knight/turn once koptas range in; out-BODIES + out-mobiles on Disruption; my guns are the wrong shape to clear the koptas (Avenger ~2/turn; 18 koptas = 9 turns).",
         heist=["Rotate-cycle to survive the focus (they kill a non-Rotated Knight; save one with the 4++).",
                "Kill the tough hulls (Kill Rigs T10 W16, Wazdakka, Trukks) with the big guns — the koptas you can't out-clear.",
                "Lancer contest/distraction (a 'distraction carnifex' that forces their fast wall to react).",
                "Accept the underdog; steal on mobility secondaries + a lucky Rotate run."],
         kill_priority="Kill Rigs -> Wazdakka -> Trukks (koptas are un-clearable — don't chase).",
         deploy="Underdog. Concede the body war, race the mission."),
    dict(key="orks-green-tide", faction="Orks", archetype="Green Tide (~100-165 bodies)",
         prev="Medium", verdict="AUTO-LOSS", disp="Take and Hold",
         deciding="~100-165 bodies (Mob Mentality 5++ at 10+ models, no Boyz return). 6-9 Knights CANNOT out-body / out-OC / clear it; the guns are the wrong shape. A known HARD COUNTER and a top all-comers list.",
         heist=["No reliable heist — ACCEPT it as a feature of 40k, not a list flaw.",
                "Play the mission, minimise the loss margin, and hope to dodge it in the Swiss.",
                "Do NOT warp the list to patch this at the cost of the 90% you win."],
         kill_priority="n/a — you cannot clear enough.",
         deploy="Accept the matchup; a respectable loss is the goal."),
    dict(key="salamanders", faction="Space Marines (Salamanders)", archetype="Forgefather's Seekers flamer-brick",
         prev="Low", verdict="FAVOURABLE", disp="Various",
         deciding="Their durability is a PAPER TIGER vs Knight guns: Land Raiders T12 W16 2+ NO invuln (Volcano ~one-shots), everything else W2-3. Flamers do nothing to T11-13. Anti-Knight spikes to ~15-22 ONLY if I feed a Knight <12\" into an Immolation-Protocols Dev flamer dump.",
         heist=["Kill BOTH Land Raiders T1-2 (Volcano/thermal — no invuln) -> strips their army fast.",
                "Respect the 12\" flamer bubble — space >12\" and their anti-Knight collapses to ~2-4.",
                "Grind the W2-3 bricks off with volume; out-durable + out-gun. Good-to-very-good matchup."],
         kill_priority="Land Raiders -> Vulkan / multi-meltas -> infantry.",
         deploy="Stay >12\" from the flamer bricks; delete the taxis first."),
    dict(key="chaos-knights", faction="Chaos Knights", archetype="Bastions of Tyranny + Houndpack Lance (PRELIMINARY)",
         prev="Low", verdict="PRELIM", disp="Reconnaissance",
         deciding="Mirror — same chassis (S20 shock lances both ways) + Chaos adds Dreadblades / dark rites / War Dog melee packs. User is CONFIDENT ('Chaos Knights are struggling'). Not deep-verified.",
         heist=["Mirror fundamentals: Rotate, out-shoot with the 2 Castellans, Lancer duels their Lancer/War Dogs.",
                "Out-OC with the Questoris; kill their gun-Knights first (Volcano trades up).",
                "PRELIMINARY — user-confident, low priority. Full pass only if it trends up."],
         kill_priority="Their gun-Knights -> War Dog packs. (Provisional.)",
         deploy="Mirror; provisional."),
    dict(key="tau-retaliation-cadre", faction="T'au Empire", archetype="Retaliation Cadre (deep-strike fusion/rail alpha) — TOP-5 OBSERVED",
         prev="High", verdict="UNFAVOURABLE", disp="Purge the Foe",
         deciding="The DOMINANT T'au build in the sample (5/75). Deep-strike alpha: 4-5 Commanders + Crisis Sunforge (fusion S9 AP-4 D6), Broadside heavy rail (S12+ AP-4 Dev), Twin Lance, 2x Riptide ion accelerator, markerlight support. A markerlit 9\" Sunforge/Crisis drop dumps ~25-35 into ONE Knight (fusion D6 + rail Dev bypass the ion shield). Fire-and-Fade neuters melee.",
         heist=["NAVIGATOR DOME IS LOAD-BEARING: the 12\" anti-Deep-Strike bubble denies the Sunforge/Crisis 9\" drop — the single biggest swing in the matchup. Deploy it central.",
                "Kill the Broadsides + Riptides at range (Volcano/plasma) before markerlights stack; delete Pathfinders (the mark engine) with the Avenger.",
                "Rotate the most-lit Knight each turn; never present a clean un-Rotated focus target; LoS-block the alpha turn.",
                "Out-OC on the ground (T'au OC is modest) IF you survive the alpha — steal the primary while their suits reposition."],
         kill_priority="Broadsides / Riptides (rail+ion) -> Sunforge fusion suits -> markerlight Pathfinders -> Commanders.",
         deploy="Navigator dome central; reserves + terrain vs the drop; kill mark/rail platforms first."),
    dict(key="chaos-daemons-khorne", faction="Chaos Daemons", archetype="Blood Legion — Bloodcrusher cavalry + Bloodthirster",
         prev="Medium", verdict="COIN-FLIP", disp="Purge / Disruption",
         deciding="Fast MELEE alpha: 3x Skullmaster + Bloodcrusher Juggernaut cav (T6 W4, charge bonuses) + Bloodthirster (T10 W18 FLY, great axe S16 AP-3 Dev) + Rendmasters. Daemonic 5++ everywhere; charges into the no-melee-invuln Questoris. (Nurgle variant = Plaguebearer grind, slower, out-hold problem not a kill problem.)",
         heist=["Shoot the Bloodcrushers (T6 W4, no armour help — gatling/plasma/RFBC) OFF before they charge; each un-charged Juggernaut pack is ~0 threat.",
                "Screen the Bloodthirster's lane; Lancer DUELS it (4++ trades favourably, S20 one-rounds a wounded 'Thirster) rather than eating its charge on a Castellan.",
                "Rotate the exposed Knight vs the (modest) ranged; out-OC the cav once thinned.",
                "vs Nurgle grind: ignore the tarpit, out-shoot Plaguebearers off objectives, win on tempo."],
         kill_priority="Bloodthirster (or screen) -> Bloodcrushers pre-charge -> Skullmasters / Rendmasters.",
         deploy="Layer chaff/Armiger vs the charge; keep a Lancer free to counter-punch the cav."),
    dict(key="astra-militarum-superheavy", faction="Astra Militarum", archetype="Steel Hammer superheavies / Grizzled artillery — OBSERVED",
         prev="Medium", verdict="COIN-FLIP", disp="Priority Assets",
         deciding="A SHOOTING brawl in my lane: Baneblade/Banesword/Stormsword (CHARACTER via Steel Hammer) + lascannon sponsons, or Shadowsword (Volcano cannon S16 AP-4 D6+6 — one-shots a Knight) + 3 artillery + Leman Russ. High-S anti-Knight, but the superheavies are KILLABLE (T12-14 W22-24, no invuln) and SLOW.",
         heist=["Win the gun duel: 2x Volcano (S18) out-ranges/out-damages their superheavies — delete the Shadowsword (the one thing that one-shots you) FIRST, then the lascannon platforms.",
                "Rotate vs the alpha; hull-down T1; their artillery is indirect (worse into a moving Knight in cover).",
                "Out-manoeuvre the M9-10 tanks + out-OC (Guard infantry is chaff you gun down); race the mission.",
                "This is the matchup the 2-Castellan build is BUILT for — a straight firepower race."],
         kill_priority="Shadowsword (Volcano cannon) -> lascannon superheavies -> artillery -> Leontus.",
         deploy="Hull-down + Rotate T1; concentrate Volcanoes on the biggest gun each turn."),
    dict(key="sm-iron-hands-terminators", faction="Space Marines (Iron Hands)", archetype="Hammer of Avernii — Assault Terminator hammer brick — OBSERVED",
         prev="Medium", verdict="COIN-FLIP", disp="Purge the Foe",
         deciding="10-model Assault Terminator thunder-hammer brick (S8 AP-2 D2, ~12-16 into a no-invuln Questoris on the charge) delivered by deep-strike + Celerity advance-charge, Feirros durability, Ballistus/Repulsor lascannon backfield. The brick is the only real Knight-killer; the rest is chaff/scorers.",
         heist=["Screen the deep-strike (Navigator dome) + shoot the hammer brick BEFORE it lands (Avenger/RFBC into 2W-2+ Terminators — volume forces the 4++).",
                "Lancer counter-charges the landed brick (4++ survives hammers a Castellan can't); never feed a Questoris into its charge.",
                "Delete the Repulsor/Ballistus (lascannon) + Sternguard with the big guns; out-OC the ~30 bodies.",
                "Win on the mission — the brick can't be everywhere; contest what it isn't on with OC10."],
         kill_priority="Repulsor/Ballistus (lascannon) -> hammer brick as it lands -> Sternguard -> Scouts.",
         deploy="Navigator dome vs the drop; hold the Lancer to counter-charge the brick."),
    dict(key="great-value-imperial-fists", faction="Imperial Fists", archetype="'Great Value' — Emperor's Shield + Librarius Conclave (the LSO target)",
         prev="Target", verdict="COIN-FLIP", disp="Priority Assets (opp), you play Meatgrinder",
         deciding="Unsaveable Sternguard Dev (full wound-reroll vs Oath) + sticky OC10 Intercessors + un-shockable OC22 Lysander Terminator brick + Armour of Contempt + a ~30-34 Oath-convergence alpha. Sisters 98-31 lesson: durable + sticky + volume.",
         heist=["Navigator dome (12\" anti-Deep-Strike) blunts his Teleport-Homer / Land-Speeder deep-strike alpha.",
                "BREAK the Oath convergence: Volcano/thermal the Land Speeders (deep-strike enablers) + the Sternguard FIRST; firepower-as-denial strips his soft OC.",
                "Out-mobile the M5 bricks — his OC22 brick can't be everywhere; contest the objectives it isn't on with OC10 + the Lancer threatening his home.",
                "Start from EXPECTATION OF A LOSS; steal via mobility secondaries. Honest coin-flip (~55-56 vs 62 in the hardened sim)."],
         kill_priority="Land Speeders (enablers) -> Sternguard (unsaveable Dev) -> break the brick's character support.",
         deploy="Navigator home-hold + deploy Hidden; don't over-expose to the alpha convergence."),
]

# ---- REALISM / RECORD EXPECTATION ----------------------------------------------
BANDS = {
    "FAVOURABLE": ["Thousand Sons", "Drukhari", "Custodes", "Salamanders"],
    "COIN-FLIP (practice these)": ["Necrons Awakened C'tan", "Necrons Monolith", "Dark Angels Deathwing",
                                    "CSM Renegade Raiders", "Votann", "Tyranids 5-Norn", "Great Value / Imperial Fists"],
    "UNFAVOURABLE / hard": ["Necrons Cursed Legion", "Dark Angels Ravenwing", "Space Wolves", "Blood Angels",
                            "T'au Prototype Cadre", "AdMech Rad-Zone", "Orks Kult of Speed"],
    "AUTO-LOSS (accept)": ["Orks Green Tide"],
    "PRELIM (verify before LSO)": ["Grey Knights", "Chaos Knights"],
}
RECORD_NOTE = (
    "Realistic 300+ GT expectation (re-verified): a positive-but-underdog record, roughly 3-3 to 4-2 "
    "over 5-6 rounds (~55-65% game win rate, pairing-skewed). Bank the broad early/mid field (the "
    "favourable + winnable coin-flips); slide toward losses as the top cut concentrates the filth "
    "(Necrons/T'au/Ravenwing/AdMech/SW). Correct Knight goal: strong positive + steal a couple you "
    "shouldn't win — NOT winning the event. The 2-Castellan shooting core IMPROVES this over 2-Lancer "
    "(more removal-race firepower for exactly the hard matchups). List blind spots (priority order): "
    "(1) [RESOLVED] costed to 1,970/2000 (1 Armiger + Archeotech Autoloaders + Blessed Plate); (2) only ONE 4++ Lancer into a "
    "melee-heavy field — accepted price of shooting-dominance; mitigate by killing deliverers pre-charge, "
    "NOT a 2nd blade; (3) screening deep-strike alphas (BA/SW/Votann/GSC) "
    "with only ~5 combat models — the Navigator dome is load-bearing; (4) anti-horde is moderate (accept "
    "Green Tide); (5) out-OC'd by most of the field -> lock PURGE THE FOE (kill-weighted) over Priority Assets."
)

# =================================================================================
# LSO LIST DECISION — 2 Castellan/1 Lancer (A) vs 1 Castellan/2 Lancer (B)
# Grounded in the listhammer TOP-FINISHING sample (n=70, X-1-or-better, dated ON/AFTER 2026-07-23
# post-Dataslate; pre-7/23 Tacoma/Edinburgh lists EXCLUDED — the 7/22 Dataslate reset points/rules).
# =================================================================================
OBSERVED_META_NOTE = (
    "n=70 top-finishing lists dated ON/AFTER 2026-07-23 (post-Dataslate cutoff: the 7/22 Dataslate "
    "reset points/rules, so pre-7/23 GTs incl. Tacoma 7/17 + Edinburgh 7/18 are EXCLUDED). WINNERS' meta, "
    "late July 2026 — the exact filth LSO's top tables will bring. Counts are of top lists, not "
    "raw popularity, so read them as 'what's winning', prevalence-weighted."
)
# (faction/archetype, count, threat-character, which-list-it-favours, one-line)
META = [
    ("Emperor's Children (Frenzied Host / Coterie / Court)", 9, "MELEE swarm + 1-2 Defilers (anti-tank shooting)", "EVEN",
     "#1-tie. Lord Exultant+Infractors, Daemonettes/Tormentors, Flawless Blades, Maulerfiends + Defiler pair (ectoplasma S14 AP-3). Kill Defilers at range OR counter-charge the swarm."),
    ("Orks (Green Tide / Dread Mob / Beast Snagga)", 8, "MELEE horde + OC-flood (some Stompa/Dakka)", "B (weak)",
     "#2 (behind EC). ~100 Boyz + klaws out-OC/tarpit; loss either way — 2nd Lancer sweep+4++ survives it marginally better."),
    ("Adeptus Mechanicus (Lords of the Forge / Rad-Zone / Eradication)", 6, "SHOOTING anti-tank + rad debuff", "A",
     "Resurgent. Kataphron arc rifle (Anti-Veh 4+), Ironstrider lascannon, Skorpius ferrumite, Onager — massed anti-Knight guns. Out-shoot it."),
    ("Space Marines (Salamanders melta / Iron Hands Terminators / Ultra)", 6, "MIXED (melta+lascannon / hammer brick)", "EVEN",
     "Salamanders melta+Land Raiders (shoot=A); Iron Hands 10-Terminator hammer brick (counter-charge=B). Split."),
    ("T'au Empire (Retaliation Cadre)", 5, "SHOOTING — deep-strike fusion/rail alpha", "A",
     "Dominant T'au. Crisis Sunforge fusion + Broadside rail + 2 Riptide, markerlit 9\" drop. Out-shoot + Navigator-dome the drop."),
    ("Necrons (Awakened C'tan / Cursed Legion Lokhust)", 4, "MIXED — gauss shooting / C'tan+Wraith melee", "A (slight)",
     "Cursed Legion = 18 Lokhust gauss cannons (shoot them=A); Awakened = C'tan+Wraith brick (OC race)."),
    ("Dark Angels (Deathwing bricks / Ravenwing)", 3, "MELEE 4++ bricks (3) + speed (1)", "B",
     "3 of 4 are Deathwing Knight melee bricks (counter-charge + assassinate Librarians = B); 1 Ravenwing (shoot=A)."),
    ("Adeptus Custodes (Lions of the Emperor / Shield Host)", 4, "MELEE elite 2+/4++", "B",
     "~40 elite bodies. Lancer melee (S20 vs Custodes) + character assassination beat the brick; thin anti-Knight guns."),
    ("Blood Angels (Stormlance / Rage-cursed / Angelic)", 4, "MELEE jump alpha", "B",
     "Death Company + Sanguinary Guard + Terminators, M12 + deep-strike charge. 2 counter-charge Lancers weather + punish the alpha."),
    ("Drukhari (Skysplinter Assault)", 3, "MELEE fast + dark-lance chip", "A",
     "Fragile — Volcano one-shots Raiders/Ravagers; shoot the Scourges/Venoms off. 2 Castellan removal shines."),
    ("Leagues of Votann (Hearthguard Covenant)", 2, "SHOOTING plasma bricks + rail + Beserk drop", "A",
     "Kill the Land Fortresses (rail) at range; out-shoot the plasma bricks; screen the Cthonian Beserk maul drop."),
    ("Chaos Space Marines (Renegade Raiders / Cabal Defiler)", 3, "MIXED — mobile raid / Defiler-spam", "EVEN",
     "Vashtorr/Discordant assassination (Lancer=B) vs Defiler-spam (shoot=A). Balanced."),
    ("Thousand Sons (Grand Coven / Rubricae Phalanx)", 3, "Magnus melee monster + durable Rubrics", "B (slight)",
     "Magnus (T11 2+/4++) is the only Knight-killer — Lancer assassinates him; Rubrics can't punch Knights."),
    ("Tyranids (Crusher Stampede)", 2, "MELEE monsters + gun-bugs", "EVEN",
     "Lancer S20 kills monsters in melee; Volcano one-shots no-invuln Emissaries. Slight B."),
    ("Chaos Daemons (Khorne Bloodcrusher cav / Nurgle grind)", 3, "MELEE fast cavalry / durable grind", "B",
     "Bloodcrusher Juggernaut cav + Bloodthirster — 2 Lancers counter-charge + duel the 'Thirster."),
    ("Astra Militarum (Steel Hammer superheavy / Grizzled artillery)", 2, "SHOOTING high-S anti-tank", "A",
     "Superheavies + Shadowsword volcano + lascannon. A straight gun duel the 2-Castellan build is built for."),
    ("Long tail (Aeldari Windrider, Death Guard, Chaos Knights)", 3, "one each — mixed", "EVEN", "Marginal individually; spread across characters."),
]

# ---- THE TWO CANDIDATE LISTS ----------------------------------------------------
LIST_A_NAME = "LIST A — 2 Castellan / 1 Lancer / 1 Crusader (SHOOTING-DOMINANT)"
LIST_A_UNITS = LIST_UNITS  # (defined above) 2 Castellan + Crusader + Lancer + Helverin + Navigator
LIST_A_IDENTITY = ("Two Volcano lances win the shooting phase outright; ONE Lancer is the single "
                   "counter-charge/decapitation blade. Firepower-as-denial: delete their anti-Knight "
                   "and soft OC at range before it connects. Both Castellans carry DOMINUS (so Dominus "
                   "Foebreakers buffs TWO Knights). Pilot's strong, comfortable game plan.")
LIST_B_NAME = "LIST B — 1 Castellan / 2 Lancer / 1 Crusader (COUNTER-PUNCH)"
LIST_B_UNITS = [
    ("Knight Castellan", 1, "Volcano lance, plasma decimator, 2x twin meltagun, 2x shieldbreaker, twin siegebreaker, feet",
     "~435", "The one long-gun anchor: Volcano one-shots a no-invuln target/turn + plasma anti-elite."),
    ("Cerastus Knight Lancer", 2, "Cerastus shock lance (strike S20 AP-3 D8 [Lance] / sweep A10 S10 AP-2 D3), ranged shock lance",
     "~415 ea", "TWO 4++ full-invuln M14 blades — two counter-charge monsters + two character-assassins + two free Crushing-Impact charges. Cover two melee lanes."),
    ("Knight Crusader", 1, "Rapid-fire battle cannon, Avenger gatling cannon, heavy flamer, thermal cannon, 2x stubber, feet",
     "~435", "Anti-infantry SUBTRACTION + thermal anti-tank — the shooting the single Castellan can't cover alone."),
    ("Armiger Helverin", 1, "2x Armiger autocannon (48\" A4 S9 AP-1 D3), heavy stubber", "140",
     "Backfield 48\" autocannons + cheap OC6 screen."),
    ("Navigator (Agents ally)", 1, "Gaze of the Empyrean", "~75",
     "12\" anti-Deep-Strike dome + Hidden home-holder (same load-bearing role in both lists)."),
]
LIST_B_IDENTITY = ("Two 4++ full-invuln Lancers turn the no-melee-invuln fight phase — the universal "
                   "Knight weakness — into a strength: two counter-charge blades + two assassins cover "
                   "TWO melee lanes and are near-unkillable in combat. Price: HALF the long-range firepower "
                   "(one Volcano, not two) — you lose the ranged-anti-tank duels the shooting meta forces.")

# ---- THE SIM DELTA (what the swapped model actually does per turn) ---------------
SIM_DELTA = [
    ("Extra Knight Castellan (List A gains)", "RANGED",
     "VERIFIED profiles: Volcano lance 72\" D3 shots S18 AP-5 D6+8 [Blast] = avg ~2 shots x ~11.5 = ~23 dmg into "
     "one target (one-shots a Hammerhead/Land Raider/Shadowsword/Kataphron brick/Ironstrider/Defiler and splits "
     "over) + plasma decimator 48\" D6+3 shots S9 AP-4 D3 supercharge (~6.5 shots — shreds Terminators/elites, AP-4) "
     "+ shieldbreaker S12 AP-6 D6+1 [Anti-Titanic 4+, Dev] character sniper. NET: ERASES ~1-2 extra priority "
     "targets PER TURN at range (bigger than first modelled — Volcano is D3, not 1). Wins the SHOOTING matchups."),
    ("Extra Cerastus Lancer (List B gains)", "MELEE + DURABILITY",
     "VERIFIED: on the charge, shock-lance STRIKE 5A WS2+ S20 AP-3 D8 [Lance] = ~4.2 hits, wounds <=T12 on 2s, "
     "~3.7 wounds x D8 (~4.5) minus saves ~ deletes any single non-Titanic target (Defiler, Bloodthirster, Magnus-"
     "wound-down, a Custodian character, a Terminator brick's core) + Shock Charge free Tank Shock (bonus MW). "
     "SWEEP 10A S10 AP-2 D3 = ~5-7 MEQ/turn into hordes. PLUS a 4++-vs-ALL, W28, M14 body that survives the melee "
     "that kills a bare-3+ Castellan. NET: neutralises ~1 extra MELEE lane/turn + a 2nd assassin + a near-unkillable "
     "counter-puncher. Wins the FIGHT matchups."),
    ("The trade, in one line", "DECISION",
     "List A removes ~1-2 more things per turn AT RANGE (dominates the shooting phase); List B survives + "
     "counter-punches one more MELEE lane (wins the fight phase you can't tank). Which matters more = which "
     "half of the meta you expect to face, and which losses hurt most. Points are near-identical (~1825-1840 "
     "base each; Castellan escalates 425/450, Crusader 410 w/RFBC — confirm Lancer/Armiger vs MFM)."),
]

# ---- PER-MATCHUP LEAN (which list performs better) ------------------------------
# key -> (lean in {A, B, EVEN}, why)
MATCHUP_LEANS = {
    "emperors-children":       ("EVEN",  "2 Castellan blast the Defiler pair (the real killer) off T1-2; 2 Lancer counter-charge the Infractor/Maulerfiend swarm AND hunt Defilers in melee. Genuinely balanced — the #1-tie matchup."),
    "orks-green-tide":         ("B (weak)", "Loss either way (accept it). 2nd Lancer sweep clears more Boyz + 4++ survives the inevitable tar-pit marginally better. Low decision weight."),
    "orks-kult-of-speed":      ("A",     "Shoot the tough hulls (Kill Rigs/Wazdakka/Stompa) — the Lancer can't out-clear fast dakka; more guns help."),
    "admech-rad-zone":         ("A",     "Out-shoot the gunline — 2 Castellan delete an Ironstrider/Skorpius/Kataphron brick per turn. (B's Lancer-into-a-brick is viable but you win the removal race with guns.)"),
    "tau-retaliation-cadre":   ("A",     "Pure ranged war. 2 Castellan out-gun the Crisis/Riptide/Broadside; a 2nd Lancer can't catch fire-and-fade T'au. Clear A."),
    "tau-prototype-cadre":     ("A",     "Same logic — out-shoot the rail/fusion/markerlight platforms."),
    "astra-militarum-superheavy": ("A",  "A straight firepower duel — 2x Volcano (S18) out-range/out-damage the superheavies. The matchup List A is built for."),
    "votann":                  ("A",     "Kill the Land Fortresses (rail) + plasma bricks at range; the guns clear the T6 Beserks wholesale. (1 Lancer still handles the maul drop.)"),
    "drukhari-skysplinter":    ("A",     "2 Castellan one-shot the fragile Raiders/Ravagers + gun the Scourges — removal-race shreds the paper army faster than a 2nd blade."),
    "salamanders":             ("A",     "Kill BOTH Land Raiders + the W2-3 bodies with volume — the shooting build out-guns the melta brick."),
    "necrons-cursed-legion":   ("A",     "Delete the Lokhust Destroyer gauss units at range (each removed = ~12 anti-Knight dmg gone). More guns = more removal."),
    "necrons-monolith":        ("A",     "Concentrate-to-kill Monoliths needs the 2nd Volcano's damage; spreading feeds reanimation."),
    "necrons-awakened-ctan":   ("EVEN",  "It's an OC/points race either way. 2nd Castellan chips a C'tan faster; 2nd Lancer duels/pins one. Wash."),
    "dark-angels-ravenwing":   ("A",     "Shoot the Storm Speeder mark-engine + Black Knight packs; a Lancer can't catch M12 fall-back-and-shoot bikes."),
    "dark-angels-deathwing":   ("B",     "Counter-charge the un-tableable 4++ bricks with a 2nd Lancer + assassinate the Termie Librarians; guns bounce off 2+/4++/-1Dmg."),
    "sm-iron-hands-terminators": ("B",   "2nd Lancer counter-charges the 10-model hammer brick (4++ survives the hammers a Castellan can't) + a 2nd assassin for Feirros/characters."),
    "space-wolves":            ("B",     "Counter-charge the thunder-hammer brick; 4++ Lancer trades where a Castellan dies. (Not in the n=70 sample.)"),
    "blood-angels":            ("B",     "TWO counter-charge blades vs the jump alpha — cover both drop lanes + double the assassin threat on Lemartes/Priests/Chaplains."),
    "custodes":                ("B",     "Lancer melee (S20 vs 2+/4++) + character assassination beat the elite brick where volume shooting only chips; the anti-Knight guns are thin, so you can afford to trade a Castellan."),
    "chaos-daemons-khorne":    ("B",     "2 Lancers counter-charge the Bloodcrusher cav + one duels the Bloodthirster (4++ trades). The cav out-runs a gunline read."),
    "thousand-sons":           ("B (slight)", "Lancer assassinates Magnus (the only real Knight-killer); a 2nd blade guarantees it. Otherwise the matchup is already favourable."),
    "tyranids-norn":           ("EVEN",  "2nd Volcano one-shots no-invuln Emissaries; 2nd Lancer S20 kills monsters + assassinates a Norn. Slight B on the melee, slight A on the guns."),
    "csm-renegade-raiders":    ("EVEN",  "2nd Lancer doubles the Vashtorr/Discordant assassin threat; 2nd Castellan shoots the Defiler + killable chassis. Wash."),
    "chaos-knights":           ("EVEN",  "Mirror — trade gun-Knights (A) vs duel their War Dog/Lancer packs (B). Practice-dependent."),
    "grey-knights":            ("B",     "Counter-charge + assassinate casters throttles the MW; provisional (not deep-verified)."),
    "great-value-imperial-fists": ("A",  "The LSO target: a firepower + mission race. 2nd Castellan strips the Sternguard/Land-Speeder enablers faster and breaks the Oath convergence — out-gun, out-mobile."),
}

# ---- THE DECISION ---------------------------------------------------------------
DECISION_TALLY = {
    "Clear edge to LIST A (2 Castellan — win the shooting matchups)":
        ["AdMech (6)", "T'au Retaliation (5)", "Drukhari (3)", "Votann (3)", "Astra Militarum (2)",
         "Salamanders (~3)", "Necrons Cursed-Legion (~2)", "DA Ravenwing (1)", "Imperial Fists (target)"],
    "Clear edge to LIST B (2 Lancer — win the fight matchups)":
        ["Custodes (4)", "Blood Angels (4)", "DA Deathwing (~3)", "Thousand Sons (3)",
         "Chaos Daemons Khorne (~2)", "Iron Hands Terminators (~2)", "Orks (8, but a loss either way)"],
    "EVEN (either list performs similarly)":
        ["Emperor's Children (9)", "CSM (3)", "Tyranids (3)", "Necrons C'tan (~2)", "SM mixed", "Chaos Knights (1)"],
}
DECISION = (
    "IT'S CLOSE — and that's the honest headline. Prevalence-weighted, the field splits almost evenly: "
    "~24 of 70 lean LIST A (the ranged-anti-tank half), ~17 lean LIST B plus the 8 un-winnable Orks, and "
    "~19 are EVEN (led by the #1-tie Emperor's Children). The meta is ~57% melee-forward BY BODY, which "
    "argues for the 2nd Lancer — BUT the matchups that leans decide are asymmetric.\n\n"
    "RECOMMENDATION: LIST A (2 Castellan / 1 Lancer), narrowly, for three data-grounded reasons:\n"
    "1) WORST-CASE MITIGATION. The A-favoured matchups (T'au, AdMech, Astra Militarum, Votann = ~16 "
    "prevalence of pure ranged anti-tank) are the ones that TABLE a Knight army 0-VP. You LOSE games there. "
    "List B surrenders those ranged duels (one Volcano, not two) for a fight-phase edge in matchups you can "
    "often still finesse on the MISSION.\n"
    "2) THE MELEE MAJORITY IS BEATABLE WITHOUT THE 2ND BLADE. The biggest melee chunks are hordes/chaff "
    "(EC Daemonettes, Ork Boyz) that SHOOTING thins as well as a Lancer would, and the ELITE melee "
    "(Custodes/BA/DA) you beat by OUT-OC-ing on the primary + screening the alpha (Navigator dome) + 1 Lancer "
    "counter-charging the key lane — not by trying to win the fight phase outright.\n"
    "3) PILOT FIT. 'Dominate the shooting phase' is a cleaner, more repeatable plan over a 6-round grind, and "
    "List A is the build you've practised.\n\n"
    "TAKE LIST B INSTEAD IF: you read your local LSO field as melee-dominant (lots of Custodes/BA/DA/Daemons/"
    "World Eaters), you're more comfortable in the counter-punch game, or you value the near-unkillable 2nd 4++ "
    "body as insurance against the melee alpha. List B's edge is REAL vs the elite-melee cluster — it just pays "
    "for it by losing the ranged wars that produce your ugliest losses.\n\n"
    "EITHER WAY: fix the list to a costed 2000 (add the 3 enhancements), lock PURGE THE FOE, and the Navigator "
    "dome is load-bearing in both. The gap between the two lists is small — pilot comfort is a legitimate tiebreaker."
)

# ---- VERIFIED 11E PROFILES (extracted from BSData + faction packs, 2026-07-26) ----
# (unit/weapon, profile, note) — the raw numbers behind the sim, for transparency.
VERIFIED_PROFILES = [
    ("Knight Castellan (425 / 450 escalating)", "M8 T12 Sv3+ W28 OC10, 5+ inv vs RANGED only", "No melee invuln."),
    ("  Volcano lance", "72\" | D3 | S18 | AP-5 | D6+8 | Blast", "D3 SHOTS (avg 2) — one-shots no-invuln T10-14."),
    ("  Plasma decimator (supercharge)", "48\" | D6+3 | S9 | AP-4 | D3 | Blast, Hazardous", "Anti-elite volume (~6.5 shots)."),
    ("  Shieldbreaker missile", "72\" | 1 | S12 | AP-6 | D6+1 | Anti-Titanic 4+, Dev Wounds", "Character/tank sniper."),
    ("Knight Crusader (395)", "M10 T11 Sv3+ W26 OC10, 5+ inv vs RANGED only", ""),
    ("  Rapid-fire battle cannon", "72\" | D6+3 | S10 | AP-1 | D3 | Blast, RF D6+3", "Anti-infantry/light."),
    ("  Avenger gatling cannon", "36\" | 18 | S6 | AP-2 | D2", "A18 strips soft OC."),
    ("  Thermal cannon", "24\" | 2D3 | S12 | AP-4 | D6 | Blast, Melta 6", "Anti-tank / Speeders."),
    ("Cerastus Knight Lancer (415)", "M14 T11 Sv3+ W28 OC10, 4+ inv vs ALL", "Full melee invuln — the key."),
    ("  Shock lance — strike", "Melee | 5 | WS2+ | S20 | AP-3 | D8 | Lance", "Wounds <=T12 on 2s; deletes any non-Titanic."),
    ("  Shock lance — sweep", "Melee | 10 | WS2+ | S10 | AP-2 | D3", "~5-7 MEQ/turn into hordes."),
    ("  Shock Charge", "free Tank Shock (0CP, repeatable) on the charge", "Bonus mortal wounds on the charge."),
    ("Armiger Helverin (140)", "M12 T9 Sv3+ W14 OC6", "2x autocannon 48\" 4 S9 AP-1 D3; Suppression -1 to hit."),
    ("--- KEY ENEMY ANTI-KNIGHT ---", "", ""),
    ("AdMech Kataphron heavy arc rifle", "30\" | 2 | S8 | AP-2 | D3 | Anti-Vehicle 4+, RF2", "Wounds Knights on 4s regardless of S. Range-deny (RF2 <=15\")."),
    ("AdMech Ironstrider twin cognis lascannon", "48\" | 2 | S12 | AP-3 | D6+1 | Sus1, Twin", "Volume anti-tank."),
    ("AdMech Skorpius ferrumite cannon", "48\" | 3 | S12 | AP-3 | D6+1", "+1 hit vs Mon/Veh."),
    ("T'au Hammerhead railgun", "72\" | 1 | S20 | AP-5 | D6+6 | Heavy, Dev Wounds", "Dev crit-mortals bypass the ion shield."),
    ("T'au Broadside heavy rail rifle", "60\" | 2 | S12 | AP-4 | D6+1 | Heavy, Dev", ""),
    ("T'au Crisis Sunforge fusion", "12\" | 1 | S9 | AP-4 | D6 | Melta 2", "Re-rolls wound+dmg vs Mon/Veh; the deep-strike killer."),
    ("EC Defiler ectoplasma destructor", "36\" | D6 | S12 | AP-3 | D3 | Blast", "Plus shearing claws MELEE 5A S16 AP-3 D6+1 (anti-Knight)."),
    ("EC Maulerfiend fists", "Melee | 6 | S14 | AP-2 | D6+1", "Fast melee, wounds Knights on 3-4s."),
    ("Custodes guardian spear", "Melee | 5 | WS2+ | S7 | AP-2 | D2", "Wounds Knights on 5+ — thin anti-Knight."),
    ("Custodes Caladius blaze cannon", "48\" | 4 | S12 | AP-3 | D6+2 | Twin", "Their one real gun."),
    ("Ork power klaw / Gork's Klaw", "Klaw S9 AP-2 D2 (Meganob S10) / Ghaz S14 AP-3 D4", "Klaw wounds Knights on 5s (volume); Ghaz on 3s."),
    ("Ork Squighog big choppa", "Melee | 4 | S6 | AP-1 | D2 | Anti-Vehicle 4+", "Wounds Knights on 4s."),
]
