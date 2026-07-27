# -*- coding: utf-8 -*-
"""Great Value (Imperial Fists) — LSO workup data. The friend's list, given the same
sim/analysis treatment as the Knights. Single source for the GV Runbook + Excel.
List from docs/meta/great-value-imperial-fists.md; points MFM-verified where present
(SM MFM is missing Sternguard/Land Speeder/Vanguard — flagged); profiles from data/bsdata.
Regenerate:  PYTHONPATH=tools:src python3 tools/gen_gv_docx.py && ... gen_gv_xlsx.py
"""
EVENT = "Lone Star Open (LSO) — 300+ players, Swiss"
GENERATED = "2026-07-27 (11E, post-Dataslate)"

LIST_NAME = "GREAT VALUE — Imperial Fists · Emperor's Shield + Librarius Conclave"
DETACHMENTS = "Emperor's Shield (2 DP) + Librarius Conclave (1 DP) = 3 DP"
DISPOSITION = ("Purge the Foe (kill-weighted — fits the durable convergence gunline). "
               "Hidden deploy + reserve-heavy teleport/deep-strike alpha.")
IDENTITY = (
    "A REVERSE-KNIGHT: instead of 5-6 big models, ~50-60 elite bodies that are hard to "
    "kill and hard to move. The win-con is CONVERGENCE, not raw guns: Oath of Moment names "
    "ONE enemy unit/turn and the whole army re-rolls Hits + adds +1 to Wound into it — "
    "roughly DOUBLING every unit's output onto that target. Wrapped around an un-shockable "
    "OC22 Terminator brick (Lysander) that one-rounds anything in melee, an unsaveable "
    "Sternguard Dev-Wound chipper, AP-2 cyclone missiles, and mobile Land Speeder melta. "
    "Defence: 2+/4++ + Armour of Contempt (-1 AP army-wide) + sticky objectives + hidden "
    "deploy. It rarely gets tabled and rarely gets out-scored — it grinds you down and "
    "holds what it takes.")

# (unit, count, wargear/role, ~pts) — points MFM-verified where noted; ~1985 total (friend's build).
UNITS = [
    ("Terminator Assault Squad (TH/SS)", "10", "+ Darnath Lysander + Ancient in Terminator Armour = the OC22 BRICK. "
     "Thunder hammer S8 AP-2 D2 [Dev]; ~24-28 melee one-rounds ANY target. Un-shockable, M5, Teleport Homer.", "310"),
    ("Darnath Lysander", "1", "Warlord. Inspiring Commander -> non-Character Terminators become OC2 (brick = OC22, effectively permanent). Icon of Obstinacy (-1 to wound at S>=5).", "100"),
    ("Ancient in Terminator Armour", "1", "Banner: +OC + re-roll a hit/wound; keeps the brick fighting on death.", "65"),
    ("Terminator Squad (2x Cyclone)", "10", "+ Librarian in Terminator Armour [Fusillade]. #1 RANGED threat: krak missile S9 AP-2 + cyclone; Fusillade = Lethal Hits. ~one-shots an Armiger.", "320"),
    ("Librarian in Terminator Armour", "1", "Leads the cyclone brick; Fusillade (Lethal Hits) + a Conclave Discipline/round.", "75"),
    ("Sternguard Veteran Squad", "10", "+ Librarian [Temporal Corridor]. The UNSAVEABLE chipper: Sternguard bolt rifle S4 AP-1 D1 [Dev, RF1] + FULL wound-reroll vs Oath -> ~5-7 mortal wounds/turn skipping any invuln. Character/W1 sniper.", "~170*"),
    ("Librarian", "1", "Temporal Corridor (move-the-Sternguard reserve/reposition) + a Discipline.", "~65*"),
    ("Land Speeder (Multi-melta)", "2", "Multi-melta S9 AP-4 D6 [Melta 2], 2 shots ea. Armiger/vehicle killer. HAVE DEEP STRIKE (a 3rd arrival threat). M14 mobile.", "~180*"),
    ("Intercessor Squad", "5", "T4 W2 OC10 STICKY (Objective Secured / Wrathful Conquerors) — the objective stays his after they die. Bolt rifle volume.", "80"),
    ("Bladeguard Veteran Squad", "5", "3+/4++ OC + Teleport Homer; forward pressure / brick support.", "80"),
    ("Vanguard Veteran Squad (Jump)", "2", "OC5, M12, Teleport Homers — army-wide OC + forward homers that enable the teleport alpha.", "~180*"),
]
LIST_TOTAL = ("~1,985 / 2000 (the friend's actual build). Points MFM-verified where present; * = SM MFM "
              "is missing Sternguard / Land Speeder / Vanguard Veterans (same incompleteness we hit for "
              "Knights) so those are meta-doc estimates — have him confirm exact points/counts vs his app.")

RULES = [
    ("Oath of Moment (THE engine)", "Each Command phase name ONE enemy unit -> the whole army re-rolls Hits AND (mono-IF) adds +1 to Wound into it. ~DOUBLES every unit's damage onto the Oathed target. Convergence, not raw guns, is how GV kills."),
    ("Lysander — Inspiring Commander", "Non-Character Terminators in his unit become OC2 -> the 10-brick is OC20 (+Lysander +Ancient = OC22). Battle-shock only tests below half strength (need 6+ dead first) -> the OC22 is effectively PERMANENT and un-shockable."),
    ("Wrath of Dorn (Emperor's Shield)", "Re-roll a Wound-roll of 1 army-wide + FULL wound re-roll for Lysander's unit. Stacks with Oath."),
    ("Armour of Contempt (defence)", "-1 AP to incoming attacks army-wide (stratagem). Drops enemy AP-2 -> AP-1; makes the 2+/4++ bodies brutally durable."),
    ("Sternguard Focus (unsaveable)", "vs the Oathed unit, Sternguard get FULL wound re-roll -> every crit-6 = a Devastating mortal wound. ~5-7 mortals/turn that skip ANY invuln/Ion Shield. Their teleport-arrival turn is their WEAKEST shoot."),
    ("Teleport / Deep-Strike engines", "THREE arrival threats: Sternguard teleport (Temporal Corridor), Land Speeder Deep Strike, Teleport-Homer jumps (Vanguard/Bladeguard). Reserve-heavy hidden alpha lands turn 2 within homer range."),
    ("Librarius Conclave", "Pick 1 Discipline/round; ALL psyker-led units (Sternguard + cyclone Termies) get it: Divination (rr-1s) / Pyromancy (+1 AP + Sustained) / Telekinesis (deep-strike enable, -1 S def) / etc."),
    ("The alpha math", "Full-stack into an Oathed target ~30-34 (10+ unsaveable Sternguard Dev); the Lysander brick (full Wrath re-roll + Oath) ~49 melee -> one-rounds ANY single model, even a 4++."),
    ("The soft underbelly", "Everything hangs on the SOFT LEGS (Sternguard, Land Speeders, cyclone Termies, Vanguard) + the 2 SLOW M5 bricks. Kill the legs -> the convergence collapses; out-mobile the bricks -> the board opens."),
]

MINDSET = (
    "GV is 'always outnumbered by big things, never out-graunched by small ones.' You are the "
    "DURABLE, STICKY, all-comers list — you rarely get tabled and rarely get out-scored. Play the "
    "OATH like a sniper (one perfect target/turn), weather the enemy's alpha behind 2+/4++ + Armour "
    "of Contempt, and win the LONG GAME on sticky objectives + attrition. Your two failure modes: "
    "(1) getting out-BODIED/out-OC'd by a true horde, and (2) getting out-MANOEUVRED and out-scored "
    "by a faster army while your M5 bricks are stranded. Deploy your homers to control WHERE the alpha "
    "lands; never waste the Oath on a target you can't finish.")

# ---- MATCHUPS: Great Value vs the n=70 listhammer archetypes (GV's perspective) ----
# verdict in {FAVOURABLE, COIN-FLIP, UNFAVOURABLE, HARD}
MATCHUPS = [
    dict(key="emperors-children", faction="Emperor's Children", archetype="Frenzied Host / Coterie (Defiler + swarm)",
         prev="High (9)", verdict="FAVOURABLE",
         deciding="Your 2+/4++ + Armour of Contempt tanks the Infractor/Daemonette melee that shreds W1 armies; Oath + Sternguard Dev delete the Defilers and the Lord Exultants; the brick one-rounds Fulgrim/Keeper if they commit. Their AP-1/-2 volume is the wrong shape for TEQ.",
         plan=["Oath the Defiler each turn (it's the only thing that hurts your armour) — Sternguard Dev + cyclone remove one/turn.",
               "Let the Daemonette/Infractor chaff crash into the brick; it holds and swings back for ~49. Don't chase.",
               "Sticky your objectives; grind. They can't out-durable or out-score you — win on attrition."],
         watch="Fulgrim (Fights First, -1 to hit) + Maulerfiends can trade into a brick; Oath them before they charge."),
    dict(key="orks-green-tide", faction="Orks", archetype="Green Tide (~100 bodies)",
         prev="High (8)", verdict="COIN-FLIP (your hardest common matchup)",
         deciding="The ONE army that out-BODIES and out-OCs you. ~100 Boyz + 5++ + power klaws flood the board; your OC22 brick holds 1-2 objectives but they blanket the rest, and klaws crack even Terminators. Your shooting mows Boyz but can't clear 100.",
         plan=["Do NOT try to out-OC the horde — concede the middle, hold your 2 bricks' objectives + sticky what you can.",
               "Oath the biggest brick each turn (Ghazghkull's or the klaw-nob unit); shooting-focus to thin the OC where it decides an objective.",
               "Bricks counter-punch (they survive the klaws better than anything); Speeders melta the Kill Rigs/Wazdakka. Race secondaries — you won't out-primary a full horde."],
         watch="Getting tar-pitted and out-actioned; Green Tide is a genuine ~45% — accept it and minimise the margin."),
    dict(key="admech", faction="Adeptus Mechanicus", archetype="Rad-Zone / Lords of the Forge gunline",
         prev="High (6)", verdict="FAVOURABLE",
         deciding="Their anti-tank is WASTED on you: Kataphron arc rifle [Anti-Vehicle 4+] and ferrumite do nothing special to INFANTRY, and D6-damage guns over-kill W2-3 bodies. You out-durable (AoC + 2+/4++), out-volume, and Oath deletes a Kataphron brick/turn.",
         plan=["Oath a Kataphron brick each turn — Sternguard Dev + cyclone + Speeder melta erase it (no invuln/FNP).",
               "Advance into their M5 gunline; Armour of Contempt shrugs the ferrumite/lascannon. Brick eats Kastelan/Ironstriders in melee.",
               "Out-score — their bodies are few and fragile once the Kataphrons die."],
         watch="Culexus/Callidus sniping your psykers (throttles Conclave); screen the Librarians."),
    dict(key="tau-retaliation", faction="T'au Empire", archetype="Retaliation Cadre (fusion/rail alpha)",
         prev="High (5)", verdict="FAVOURABLE (survive round 1)",
         deciding="A glass alpha vs your armour: Armour of Contempt drops their AP, the 4++ eats the Dev-rail/fusion spikes, and your reserves mean the alpha has less to hit turn 1. Oath one-rounds Crisis/Riptides; the brick walks them down.",
         plan=["Reserve heavy; give the T'au alpha few juicy turn-1 targets. Armour of Contempt on the unit they focus.",
               "Oath the Retaliation Crisis bomb the turn it drops (before Fire-and-Fade) — Sternguard Dev + brick delete it.",
               "Grind forward; T'au can't out-durable or out-melee you. Kill the markerlight Pathfinders to cut their hit-buffs."],
         watch="A perfectly-piloted markerlit railgun turn can chunk the brick — spread the Termies, don't clump for Blast."),
    dict(key="necrons-ctan", faction="Necrons", archetype="Awakened Dynasty (C'tan + Wraiths)",
         prev="Med (4)", verdict="COIN-FLIP (lean unfavourable)",
         deciding="C'tan durability (4++/-1Dmg/reanim) blunts even your convergence, and they out-OC with reanimating bodies. Your edge: Sternguard Dev MORTALS partly bypass reanimation, and the brick out-fights Wraiths. But you can't table 3 C'tan and they grind objectives.",
         plan=["Oath + Sternguard Dev a C'tan each turn — mortals skip the 4++; you won't kill it but you suppress it.",
               "Don't feed the brick into the Void Dragon (Anti-Veh, heals off you); brick kills Wraiths/Lychguard instead.",
               "Win on sticky objectives + secondaries; it's a grind you can steal, not a matchup you dominate."],
         watch="Reanimation refunding your chip — focus-remove whole units, don't spread."),
    dict(key="custodes", faction="Adeptus Custodes", archetype="Lions of the Emperor (elite melee)",
         prev="Med (4)", verdict="COIN-FLIP",
         deciding="Mirror of elites: their 2+/4++ + better melee weapons vs your 2+/4++ + more bodies + Oath + unsaveable Sternguard. They out-fight the brick model-for-model; you out-number and out-shoot (Dev bypasses their 4++).",
         plan=["Do NOT brawl the Blade Champion/Wardens with the brick head-on — Oath + Sternguard Dev SHOOT them down (mortals skip the 4++).",
               "Use your body count + sticky OC to out-score; they have ~40 models, you have more.",
               "Speeders melta the Caladius; cyclone + Oath delete a Custodian unit/turn."],
         watch="Their characters (Trajann/Blade Champion) out-duel Lysander — snipe with Sternguard, don't melee."),
    dict(key="blood-angels", faction="Blood Angels", archetype="Stormlance / Liberator jump alpha",
         prev="Med (4)", verdict="FAVOURABLE",
         deciding="Glass melee alpha into your armour: Death Company/Sang Guard hit hard on the charge but fold to return fire, and Armour of Contempt + 4++ blunts their AP. Oath + overwatch thin the alpha as it lands; the brick counter-punches.",
         plan=["Screen so the DC/Sang Guard land 9\"+ out; Oath the deepest-striking unit and delete it before it swings.",
               "Weather the charge behind 2+/4++/AoC; the brick one-rounds Dante/Sanguinary Guard back.",
               "Out-grind — they're fragile once the alpha is spent."],
         watch="Lemartes/Priests keeping DC alive — Oath+Sternguard the character to strip the buffs."),
    dict(key="dark-angels-deathwing", faction="Dark Angels", archetype="Deathwing Knights / Inner Circle",
         prev="Med (3-4)", verdict="COIN-FLIP",
         deciding="Terminator mirror: their Deathwing Knights (4++, mace, Smite of the Watchers) + Lion vs your Lysander brick + Sternguard. Both durable; comes down to Oath efficiency + who out-scores. The Lion out-duels Lysander in melee.",
         plan=["SHOOT the Deathwing down with Oath + Sternguard Dev (mortals skip the 4++) — don't melee the mace brick.",
               "Race objectives; both armies are slow, so board position + sticky OC decide it.",
               "Speeders + cyclone delete the Ravenwing speeders / support first."],
         watch="The Lion — do not feed Lysander into him; Sternguard-snipe or avoid."),
    dict(key="drukhari", faction="Drukhari", archetype="Skysplinter Assault (fast splinter + lance)",
         prev="Med (3)", verdict="FAVOURABLE",
         deciding="Fragile paper into your armour: their dark lances are few and their Lethal/pain tokens are non-Vehicle (do little to TEQ); Armour of Contempt + 4++ tanks the splinter. Oath + volume deletes their transports and infantry wholesale.",
         plan=["Oath a Venom/Ravager or the Incubi each turn — shooting erases their paper.",
               "Weather the T2 lance alpha behind AoC; brick counter-charges the Incubi/Wyches.",
               "Their speed can out-manoeuvre — hold sticky objectives so they can't just flip the board late."],
         watch="Being out-actioned by their mobility; keep your homers/screens tight so they can't backfield-raid."),
    dict(key="astra-militarum", faction="Astra Militarum", archetype="Steel Hammer superheavy / artillery",
         prev="Low-Med (2)", verdict="FAVOURABLE",
         deciding="Their lascannon/volcano over-kills your W2-3 bodies (D6 into W2 = waste), and their infantry can't out-fight yours. You advance behind AoC, Oath the superheavies (or ignore and out-score), and the brick/Speeders crack the tanks.",
         plan=["Reserve vs the alpha; advance into the gunline (they're static). Oath the Shadowsword/Baneblade or just out-score around it.",
               "Speeder melta + brick delete a superheavy if it's the win-con; otherwise take objectives their tanks can't hold.",
               "Sticky OC + body count out-scores a low-model Guard tank list."],
         watch="Artillery + Leontus orders can chip; don't clump for the big blasts."),
]

BANDS = {
    "FAVOURABLE (bank these)": ["Emperor's Children", "AdMech", "T'au Retaliation", "Blood Angels", "Drukhari", "Astra Militarum"],
    "COIN-FLIP (practice)": ["Custodes", "Dark Angels Deathwing", "Necrons C'tan (lean unfav)"],
    "HARDEST (accept ~45%)": ["Orks Green Tide"],
}
RECORD_NOTE = (
    "Great Value is a STRONG all-comers list — a better raw record expectation than a Knight army "
    "because it has FEWER hard counters. Realistic 300+ GT: a solidly positive record, ~4-2 to 5-1 "
    "over 5-6 rounds, with a genuine shot at the top tables. It wins by DURABILITY + CONVERGENCE + "
    "STICKY OBJECTIVES, not by any single alpha. The two things that beat it: a true HORDE that "
    "out-bodies the OC (Orks) and a fast army that out-manoeuvres the M5 bricks and out-scores while "
    "refusing the fight (kite-and-flip). Its own discipline test: pilot the Oath perfectly (one "
    "finishable target/turn) and don't strand the bricks. Blind spots: (1) M5 bricks are slow -> "
    "board control depends on the mobile legs + homers, protect them; (2) psyker-dependent (Conclave) "
    "-> Culexus/Callidus/character-snipes throttle it, screen the Librarians; (3) reserve-heavy -> a "
    "whiffed turn-2 arrival (failed charges / scattered homers) is a lost tempo swing.")

# ---- verified profiles (data/bsdata) — the numbers behind the sim ----
VERIFIED_PROFILES = [
    ("Sternguard Bolt Rifle", "24\" | 2 | S4 | AP-1 | D1 | Assault, Dev Wounds, Heavy, RF1", "vs Oath = full wound re-roll -> ~5-7 unsaveable mortals/turn."),
    ("Cyclone missile (krak)", "S9 | AP-2 | + Lethal Hits (Fusillade)", "Persistent AP-2 anti-Knight/elite; ~one-shots an Armiger with Oath."),
    ("Thunder Hammer (brick)", "Melee | 3 | S8 | AP-2 | D2 | Dev Wounds", "10-brick + Lysander (full Wrath re-roll + Oath) ~49 dmg -> one-rounds anything."),
    ("Lysander — Fist of Dorn", "Melee | 5 | S10 | AP-3 | D3 | Dev Wounds", "The character-killer in the brick."),
    ("Land Speeder — Multi-melta", "24\" | 2 | S9 | AP-4 | D6 | Melta 2", "x2 Speeders, Deep Strike; Armiger/vehicle killer (Oath ~doubles)."),
    ("Intercessor Bolt Rifle", "24\" | 2 | S4 | AP-1 | D1 | Assault, Heavy", "Sticky OC10 body + volume chaff-clear."),
]
