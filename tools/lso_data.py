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
    ("Knight Castellan", 2, "Volcano lance, plasma decimator, 2x twin meltagun, 2x shieldbreaker, twin siegebreaker, feet",
     "435 ea", "The shooting core. 2x Volcano one-shots no-invuln anchors + snipes characters @60\"; plasma anti-elite; +1 hit vs terrain (Dominus)."),
    ("Knight Crusader", 1, "Rapid-fire battle cannon, Avenger gatling cannon, heavy flamer, thermal cannon, 2x stubber, feet",
     "~435", "Anti-infantry SUBTRACTION: RFBC (D6+3) + Avenger A18 strip soft OC; thermal for anti-tank/Speeders."),
    ("Cerastus Knight Lancer", 1, "Cerastus shock lance (strike S20 AP-3 D8 [Lance] / sweep A10 S10 AP-2 D3), ranged shock lance",
     "~415", "The one blade: 4++ FULL invuln, M14. Counter-charge melee threats + assassinate buff-characters + free Crushing Impact MW on the charge."),
    ("Armiger Helverin", 1, "2x Armiger autocannon (48\" A4 S9 AP-1 D3), heavy stubber", "140",
     "Backfield 48\" autocannons + cheap OC6 body / screen."),
    ("Navigator (Agents ally)", 1, "Gaze of the Empyrean", "~75",
     "12\" anti-Deep-Strike dome (vs BA/SW/GSC/deep-strike alphas) + Hidden home-holder. Allies take no enhancement."),
]
# ★ FIX BEFORE LSO: as written the list is ~1825-1915/2000 with ZERO enhancements. Spend the free
# points on 3 enhancements (one each on 3 different Knights). Rotate Ion Shields is FREE (a stratagem,
# not an enhancement). The costed 2000/2000 template is examples/best-purge-the-foe.yaml.
ENHANCEMENTS = [
    ("Bearer of the Lancer's Sigil", "Cerastus Knight Lancer", "25",
     "Re-roll the Lancer's charge — with only ONE decapitation blade, guaranteeing its decisive charge is the highest-value 25 pts in the list."),
    ("Blessed Plate", "Knight Castellan #1", "30", "Castellan -> T13: the Volcano platform survives the incoming longer."),
    ("Bearer of the Judicant's Helm", "Knight Castellan #2", "25", "[Ignores Cover] on a Castellan — stacks with Dominus +1-hit-in-terrain; beats intervening-terrain cover."),
]
LIST_TOTAL = ("As written ~1825-1915 / 2000 with NO enhancements = the one concrete error. "
              "Add the 3 enhancements above to reach 2000 (Rotate is free). VERIFY exact points "
              "vs LIVE MFM before submitting — BSData prices Castellan 400, the app may be 425.")

# ---- KEY RULES / CHEAT-SHEET ----------------------------------------------------
RULES = [
    ("Ion Shield", "5++ invuln vs SHOOTING ONLY (ranged). Does NOTHING in melee."),
    ("Rotate Ion Shields", "Valourstrike stratagem, once per phase -> upgrade ONE Knight to 4++ vs shooting each turn. Only one protected per shooting phase."),
    ("Questoris melee", "NO melee invuln — bare 3+ armour in the fight phase. Melee is the universal Knight weakness."),
    ("Cerastus Lancer", "4++ FULL invuln (melee AND ranged), M14. Strike S20 AP-3 D8 [Lance]; free Crushing Impact on charge (D6=T11, each 5+ = 1 MW, bypasses invuln). The universal counter-charge + character-assassin."),
    ("Volcano lance", "S18 AP-5 D6+8 — one-shots no-invuln anchors (Hammerheads, Land Raiders, Kataphrons, Monoliths, no-invuln Norns). Wasted (overkill) into low-W chaff."),
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
    "(1) ~85-175 pts unspent + ZERO enhancements = fix to 2000 first; (2) only ONE 4++ Lancer into a "
    "melee-heavy field — accepted price of shooting-dominance; mitigate by killing deliverers pre-charge "
    "+ Lancer's-Sigil charge re-roll, NOT a 2nd blade; (3) screening deep-strike alphas (BA/SW/Votann/GSC) "
    "with only ~5 combat models — the Navigator dome is load-bearing; (4) anti-horde is moderate (accept "
    "Green Tide); (5) out-OC'd by most of the field -> lock PURGE THE FOE (kill-weighted) over Priority Assets."
)
