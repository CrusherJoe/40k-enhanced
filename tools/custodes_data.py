# -*- coding: utf-8 -*-
"""Adeptus Custodes — "The Better Thing 2" (Meta Slayers) LSO workup data. Given the same
sim/analysis treatment as the others. Single source for the Custodes Runbook + Excel.

All rules VERIFIED from the local DB (data/bsdata/rules via tools/db.py) — the pilot corrected me:
Martial Ka'tah is the ARMY rule, and Shield Host is the (default) detachment.
  * ARMY RULE — MARTIAL KA'TAH: each unit, when it fights, picks a stance — DACATARAI ([SUSTAINED
    HITS 1]) or RENDAX ([LETHAL HITS]) — army-wide melee tech.
  * DETACHMENT — SHIELD HOST (2 DP): ASSEMBLAGE OF MIGHT (Command phase, mark one enemy unit ->
    every ADEPTUS CUSTODES CHARACTER unit gets +1 to Wound vs it) + MARTIAL MASTERY (start of battle
    round, pick a Ka'tah stance army-wide until the next round).
  * DETACHMENT — THARANATOI HAMMERBLOW (1 DP, LIONS): THE HAMMER FALLS (a Terminator unit that made
    an ingress move re-rolls charges) + Allarus tools (Mnemo-Locked Shrine Cipher = ingress T1;
    Hardened Resolve = +1 T; Electroexorcist Saturation = grenade launchers D3+3 A; Unleash the Lions
    = split into single models).
Points are the app's (v912). Regenerate: PYTHONPATH=tools:src python3 tools/gen_custodes_docx.py && ... xlsx
"""
EVENT = "Lone Star Open (LSO) — 300+ players, Swiss"
GENERATED = "2026-07-27 (11E, post-Dataslate)"

LIST_NAME = "THE BETTER THING 2 — Adeptus Custodes · Shield Host + Tharanatoi Hammerblow (Meta Slayers)"
DETACHMENTS = "Shield Host (2 DP — mark + Ka'tah) + Tharanatoi Hammerblow (1 DP — the deep-strike Allarus hammer) = 3 DP"
DISPOSITION = ("Priority Assets — a fast, durable elite army that takes and holds the priority objectives, "
               "deletes what contests them in melee, and grinds you out on quality.")
IDENTITY = (
    "A GOLDEN TIDE OF QUALITY — ~40 models that each shrug what kills whole squads. The core is durable "
    "character-led bricks (Valerian + Wardens, Blade Champion + Guard, Shield-Captain + Guard) that are all "
    "2+/4++, T6 W3, and swing S7 AP-2 D2 Guardian spears (A5 EACH) — and the ARMY rule Martial Ka'tah stacks "
    "army-wide SUSTAINED or LETHAL Hits on that melee every round, while Shield Host's Assemblage of Might adds "
    "+1 to Wound vs a marked target for the character units. That turns already-brutal spears into a wall of "
    "auto-wounding, extra-hitting D2 attacks. Around it: a DEEP-STRIKE ALLARUS HAMMER (Tharanatoi Hammerblow — "
    "deep strike from Reserves / Rapid Ingress, re-roll charges on the turn they ingress, +1 T, re-roll wounds vs CHARACTER/MONSTER/VEHICLE = anti-elite/anti-tank), "
    "fast harassers (M10 Venatari jet-packs, M12 Vertus jetbikes with a mortal-wound bomb), and cheap Sisters of "
    "Silence (Prosecutors for actions/objectives, Witchseeker flamers for hordes + ANTI-PSYKER). It is durable, "
    "mobile, hits like a truck, and has answers to everything — its only real hole is being OUT-BODIED by a "
    "true horde, because ~40 elite models can only physically cover so much board.")

# (unit, count, wargear/role, ~pts) — app v912 values.
UNITS = [
    ("Valerian + Custodian Wardens (5)", "6", "WARLORD brick. Valerian: 2+/4++/FNP6+, Golden Laurels (melee AP into his unit worsened -1), Hero of Lion's Gate (change a roll to a 6, once/battle). Wardens: 2+/4++, Feel No Pain (Living Fortress once/battle), Resolute Will (-1 to wound vs S>T while led). The unkillable anchor.", "360"),
    ("Blade Champion + Custodian Guard (4)", "5", "Blade Champion: Vaultswords S7 AP-2 D2 A6 [PRECISION] -> character-assassin; Swift Onslaught (re-roll charges) + Martial Inspiration (advance+charge). Guard: Battleline 2+/4++, S7 AP-2 D2 A5 spears.", "280"),
    ("Shield-Captain + Custodian Guard (5)", "6", "Shield-Captain: MASTER OF THE STANCES (once/battle, BOTH Ka'tah stances active for a fight = Sustained AND Lethal). Guard: Battleline, +Praesidium Shield (a 4+ FNP body) + Vexilla (+OC / anti-deep-strike).", "325"),
    ("Allarus Custodians (5)", "5", "THE HAMMER (standalone unit — NO attached leader, so not a Character unit: gets crit-5 + a Ka'tah stance + Slayers, but NOT the Assemblage mark). Terminators 2+/4++ T7 W4, Guardian spears + Balistus grenade launchers. Deep Strike from Reserves (T2+) or RAPID INGRESS at end of opp's Move; The Hammer Falls re-rolls charges on a turn they ingressed. Slayers of Tyrants (re-roll Wounds vs CHARACTER/MONSTER/VEHICLE = anti-elite/anti-tank); Hardened Resolve strat (+1 T); Electroexorcist Saturation strat (Balistus -> D3+3 A vs hordes); From Golden Light = redeploy once. (No enhancements taken, so no T1 ingress.)", "275"),
    ("Venatari Custodians (3)", "3", "FAST (M10 jet-pack). Venatari lance S4 AP-1 D2 A2 [ASSAULT] -> mobile objective-grabber / chip; can drop from reserve. (x2 in the list.)", "165"),
    ("Venatari Custodians (3)", "3", "2nd fast jet-pack unit — board control + late-objective flex.", "165"),
    ("Vertus Praetors (2)", "2", "FAST jetbikes (M12, Turbo Boost +6\"). Interceptor lance S7 AP-2 D2 A5 [LANCE] (charge threat) + hurricane bolters (S4 AP-1 D2 A3 [RF3, Twin]). Quicksilver Execution = mortal-wound bomb over a unit. (x2.)", "145"),
    ("Vertus Praetors (2)", "2", "2nd jetbike unit — fast objective + anti-infantry + the mortal bomb.", "145"),
    ("Prosecutors (4)", "4", "Sisters of Silence: cheap boltgun bodies for SECONDARIES / ACTIONS / screening. (x2 in the list.)", "45"),
    ("Prosecutors (4)", "4", "2nd cheap action/objective unit.", "45"),
    ("Witchseekers (4)", "4", "Sisters of Silence: Witchseeker flamers S4 AP0 D1 A(D6) [IGNORES COVER, TORRENT] -> auto-hit anti-horde + ANTI-PSYKER (Sisters shut down enemy Psykers). Board-clearer / screen.", "50"),
]
LIST_TOTAL = ("2,000 / 2000 (Meta Slayers' build). Points are the app's (v912). ~40 models total. Legality of the "
              "key tech verified from data/bsdata/rules: Martial Ka'tah (army rule), Shield Host (Assemblage of "
              "Might + Martial Mastery), Tharanatoi Hammerblow (The Hammer Falls + Allarus enhancements/strats); "
              "Valerian/Blade Champion/Shield-Captain lead Custodian Guard/Wardens (verified).")

RULES = [
    ("Martial Ka'tah — the ARMY rule (Sustained OR Lethal, MELEE only)", "FIGHT PHASE only. Each time a Custodes unit is selected to fight it picks the BEST stance for that target: DACATARAI ([SUSTAINED HITS 1]) or RENDAX ([LETHAL HITS]). Crossover (with Martial Mastery's crit-on-5+): the two are equal when you wound on 4+ (S=T); default to SUSTAINED, flip to LETHAL only when target Toughness > weapon Strength (wounding on 5+/6+). For the S7 Guardian spears: SUSTAINED vs T7 and below (most infantry/light vehicles), LETHAL vs T8+ (Knights, heavy vehicles, big monsters). Army-wide on every unit with this ability; Shield Host stacks on top."),
    ("Shield Host — Assemblage of Might (mark -> +1 wound)", "Command phase: mark ONE enemy unit. Until your next Command phase, each model in an ADEPTUS CUSTODES CHARACTER unit gets +1 to WOUND vs it. Per Core Rule 19.01 an attached unit is a single unit for all rules purposes and gains CHARACTER, so this covers the WHOLE led brick (all 5 spears of Valerian+Wardens / Blade-Champion+Guard / Shield-Captain+Guard) AND any solo character — NOT the standalone Allarus (no attached leader = not a Character unit; they still get crit-5 + a stance + Slayers). Point the mark at the durable thing you must crack and the bricks wound it on a much better roll."),
    ("Shield Host — Martial Mastery (crit-on-5+ / +1 AP)", "Start of the battle round, pick ONE (army-wide until next round): (a) unmodified melee Hit of 5+ scores a CRITICAL HIT, or (b) +1 AP to all melee. Option (a) is the engine — crit-on-5+ roughly DOUBLES the Ka'tah proc rate: with RENDAX every 5+ auto-wounds ([Lethal]), with DACATARAI every 5+ throws an extra hit ([Sustained]). The Shield-Captain's MASTER OF THE STANCES then gives HIS unit BOTH stances for one fight (Sustained AND Lethal at once). NOTE: applies to every model with the Martial Ka'tah ability — so the Allarus benefit from crit-5 + stance too."),
    ("Tharanatoi Hammerblow — the deep-strike Allarus hammer", "THE HAMMER FALLS: an ADEPTUS CUSTODES TERMINATOR unit that made an INGRESS MOVE this turn re-rolls charges. This list takes NO enhancements (no Mnemo-Locked Shrine Cipher), so the 5 Allarus arrive from Reserves (T2+) or via the core RAPID INGRESS stratagem at the end of the opponent's Movement phase — and re-roll the ~9\" charge on the turn they ingress. SLAYERS OF TYRANTS (re-roll Wounds vs CHARACTER/MONSTER/VEHICLE) makes them a precision anti-elite/anti-tank delete; HARDENED RESOLVE (+1 T, 1CP) makes them a T8 rock; ELECTROEXORCIST SATURATION turns the Balistus launchers into D3+3 A anti-horde; UNLEASH THE LIONS splits them into 5 single-model action/board pieces."),
    ("Durability — the whole army is a rock", "2+/4++ on EVERY model (T6 W3 Guard/Wardens, T7 W4/W5 Allarus/Vertus). Valerian's Golden Laurels (-1 AP to melee vs his unit) + Wardens' Feel No Pain + Resolute Will (-1 to wound vs S>T) make the anchor near-unkillable. AP-heavy shooting is blunted by the 4++; volume struggles against 2+. You out-LAST almost everything."),
    ("Speed + board control (the un-Custodes part)", "M10 Venatari + M12 Vertus (Turbo +6\") + deep-strike Allarus = a fast, flexible board game most Custodes lists lack. The jetbikes/jet-packs grab and flip objectives, the Vertus Quicksilver Execution drops mortals over a screen, and the Sisters of Silence (Prosecutors) do the cheap ACTIONS/secondaries a low-model army usually can't."),
    ("Sisters of Silence — anti-Psyker + cheap bodies", "Prosecutors (2x) + Witchseekers give an elite army the CHEAP OC bodies + action-doers it normally can't afford, and the Sisters are ANTI-PSYKER (shut down enemy psychic + Witchseeker Torrent flamers auto-hit hordes). A clean answer to Thousand Sons/Grey Knights/psychic decks and a screen vs everyone."),
    ("The Emperor's Champions of the meta — kill priority", "You have no shortage of quality; the discipline is TARGETING. Assemblage-mark the thing you MUST kill each turn; Ka'tah-stance to match (Lethal vs high-T, Sustained vs many/durable); send the Allarus into the enemy's biggest CHARACTER/MONSTER/VEHICLE (Slayers re-rolls wounds); Blade Champion Precisions an attached buff-character. Do NOT waste the Warden brick chasing chaff."),
    ("What genuinely beats it", "(1) A TRUE HORDE (Orks) — ~40 elite models can't out-body ~100 and physically can't cover the board, so you get out-scored on primary even while winning every fight; (2) being out-ACTIONED by an evasive objective army if your bricks get bogged in the wrong fight. It has no bad DAMAGE or DURABILITY matchups — only a body-count / tempo ceiling."),
]

MINDSET = (
    "Play it as an elite tempo-and-attrition army, not a slow brick. Its game: take the priority objectives "
    "early with the fast pieces (Venatari/Vertus + Sisters), delete whatever contests them in melee (marked "
    "target + Ka'tah stance + the Allarus hammer), and out-last everything on 2+/4++. Three disciplines: "
    "(1) TARGET with the buffs — Assemblage-mark and stance each turn on the thing that decides it, don't "
    "spread; (2) TIME the Allarus — ingress T1 to pressure or hold them to answer a threat, and re-roll the "
    "charge; (3) don't get out-actioned — use the Sisters/Vertus for secondaries so the bricks are free to "
    "fight. Accept the one bad matchup (a true horde out-bodies you) and grind everyone else on quality.")

# ---- MATCHUPS: The Better Thing 2 vs the LSO-meta archetypes (Custodes' perspective) ----
# verdict in {FAV, EVEN, COIN, UNFAV, HARD}
MATCHUPS = [
    dict(key="emperors-children", faction="Emperor's Children", archetype="Frenzied Host / Coterie (Defiler + swarm)",
         prev="High (9)", verdict="FAVOURABLE",
         deciding="You out-fight the melee swarm outright: 2+/4++ + FNP eats the Infractor/Daemonette attacks, Rendax-Lethal spears + Assemblage delete units, and the Allarus (Slayers re-roll vs VEHICLE) one-round the Defilers. Their AP-1/-2 volume is the wrong shape for your armour.",
         plan=["Mark + Allarus a Defiler each turn (their only real anti-armour); Slayers of Tyrants deletes it.",
               "Rendax (Lethal) or Dacatarai (Sustained) on the spear bricks vs the swarm; let the chaff break on the Warden anchor.",
               "Blade Champion Precisions a Lord Exultant; grind primary — they can't out-durable or out-score you."],
         watch="Fulgrim (Fights First) trading into a brick — mark him + Master-of-the-Stances the fight, or receive on the FNP Wardens."),
    dict(key="orks-green-tide", faction="Orks", archetype="Green Tide (~100 bodies)",
         prev="High (8)", verdict="UNFAVOURABLE (your hardest common matchup)",
         deciding="The one army that beats quality with QUANTITY: ~100 Boyz out-body your ~40 models on primary, and even winning every fight you can't clear the tide or cover the board. Your spears + Witchseeker flamers + grenades mow Boyz, but you get out-scored while doing it.",
         plan=["Dacatarai (Sustained) + Witchseeker flamers (Torrent, auto-hit) + Allarus grenades (D3+3) to maximise Boyz-per-turn.",
               "Hold your objectives with the 2+/4++ bricks (Boyz can't shift them); use Venatari/Vertus to contest flanks + flip.",
               "Race secondaries with the Sisters/jetbikes; accept you won't out-primary a full horde — minimise the margin."],
         watch="Getting tar-pitted + out-actioned; ~40% is real. Klaws/big-mek stuff can chip even 2+/4++ over 5 turns."),
    dict(key="admech", faction="Adeptus Mechanicus", archetype="Rad-Zone / Lords of the Forge gunline",
         prev="High (6)", verdict="FAVOURABLE",
         deciding="Their D6-damage guns over-kill your W3 bodies (waste) and the 4++ blunts the rest, while you're FASTER than they expect (Venatari/Vertus + Allarus deep-strike close the gap turn 1-2) and delete the gunline in melee. Mark + Ka'tah shreds Kataphrons.",
         plan=["Ingress the Allarus + rush the jetbikes T1-2; Slayers re-roll wounds crush the Kataphron/Kastelan bricks.",
               "Mark the biggest gun brick; Lethal/Sustained spears finish it; hold objectives their static line can't contest.",
               "Sisters screen the deep-strike lanes; out-score once their shooting is tar-pitted in melee."],
         watch="Culexus/assassins sniping Valerian/Shield-Captain (throttles the buffs) — screen the characters with bricks."),
    dict(key="tau-retaliation", faction="T'au Empire", archetype="Retaliation Cadre (fusion/rail alpha)",
         prev="High (5)", verdict="COIN-FLIP (lean favourable)",
         deciding="Their rail/fusion (AP-4/-5) ignores armour, but you're on a 4++ + Wardens FNP + Valerian's -1 AP + Resolute Will, and you're FAST enough to be in their face turn 2 (jetbikes + Allarus ingress). Once you close, T'au fold in melee. Survive the alpha, delete the suits.",
         plan=["Reserve the Allarus + hide the anchor from first-turn rail LoS; jetbikes + Venatari pressure T1.",
               "Mark a Riptide/Crisis brick; Allarus (Slayers vs MONSTER) + spears delete it; Hardened Resolve (+1T) tanks the return.",
               "Kill markerlight Pathfinders to cut their hit-buffs; hold objectives + out-score the low-body Cadre."],
         watch="Devastating-Wounds rail spikes bypassing the 4++; spread the bricks + don't clump into one fusion volley."),
    dict(key="necrons-ctan", faction="Necrons", archetype="Awakened Dynasty (C'tan + Wraiths)",
         prev="Med (4)", verdict="COIN-FLIP",
         deciding="C'tan durability (4++/-1Dmg/reanim) blunts even your output, and they out-OC with reanimating bodies. Your edge: Allarus (Slayers re-roll vs MONSTER) + marked Lethal spears chip a C'tan, and you out-fight Wraiths/Lychguard. A grind you steal on objectives, not a blowout.",
         plan=["Mark + focus ONE C'tan (Allarus + a spear brick); spread chip just reanimates away.",
               "Blade Champion Precisions a Technomancer/Cryptek (cuts reanimation); Wardens hold the middle.",
               "Win on primary + secondaries with the fast pieces; it's a grind you can steal."],
         watch="Reanimation refunding your damage + their forced-battle-shock tech; focus-remove whole units."),
    dict(key="custodes", faction="Adeptus Custodes", archetype="the MIRROR (Shield Host / elite golden)",
         prev="Med (4)", verdict="EVEN (mirror)",
         deciding="A golden mirror decided on the margins: who marks + stances better, who wins the Allarus exchange, and who plays the objectives with the fast pieces. Both sides are 2+/4++ walls, so it comes down to Ka'tah discipline (Lethal to crack 2+/4++), the Blade Champion character duel, and tempo.",
         plan=["Rendax (Lethal Hits) is king in the mirror — auto-wounds skip the tough-to-wound roll into their 2+/4++.",
               "Win the Allarus fight (Slayers vs their CHARACTERs) + Blade Champion duels their character (Precision).",
               "Out-tempo with Venatari/Vertus on objectives; the mirror is a coin-flip you tilt with better targeting."],
         watch="Their Master-of-the-Stances / Assemblage timing — mirror the buffs and don't over-commit a brick."),
    dict(key="blood-angels", faction="Blood Angels", archetype="Stormlance / Liberator jump alpha",
         prev="Med (4)", verdict="FAVOURABLE",
         deciding="A glass melee alpha into a 2+/4++/FNP wall is your matchup: DC/Sang Guard hit hard on the charge but bounce off your armour, and you RECEIVE and delete them (Ka'tah + Assemblage) or counter-charge with the Allarus. They fold once the alpha's spent; you don't.",
         plan=["Screen so the jump units land 9\"+ out; receive the charge on the FNP Wardens (Living Fortress if needed).",
               "Mark the DC; Lethal spears + Allarus delete the spent alpha; Blade Champion Precisions Lemartes/a Priest.",
               "Out-grind + out-score — you're the durable one, they're the glass one."],
         watch="Overwhelming a single brick with a full DC+character charge before you stance up; spread + mark first."),
    dict(key="dark-angels-deathwing", faction="Dark Angels", archetype="Deathwing Knights / Inner Circle",
         prev="Med (3-4)", verdict="COIN-FLIP (lean favourable)",
         deciding="Terminator mirror where you edge on OUTPUT + speed: RENDAX (Lethal) auto-wounds skip the roll into their 4++/-1Dmg mace brick, your Allarus (Slayers vs their CHARACTERs) delete the support, and you're faster (jetbikes) to the objectives. Both durable -> decided on the mission.",
         plan=["Rendax-Lethal + Assemblage-mark the Deathwing brick; auto-wounds beat the 4++ better than to-wound rolls.",
               "Allarus + Blade Champion hunt the Inner Circle characters / the Lion (a Monster -> Slayers re-rolls).",
               "Out-tempo on objectives with the fast pieces; grind the mirror on primary."],
         watch="The mace brick out-grinding a lone Warden unit; commit with the Allarus + stance, don't feed piecemeal."),
    dict(key="drukhari", faction="Drukhari", archetype="Skysplinter Assault (fast splinter + lance)",
         prev="Med (3)", verdict="FAVOURABLE",
         deciding="Rare for Custodes: you MATCH their speed (M10-12 jetbikes/jet-packs) AND tank their splinter (2+/4++, and poison/lance is the wrong shape for T6/T7 quality), then delete their paper. They can't kite what keeps pace, and they fold when they commit.",
         plan=["Jetbikes/Venatari keep pace + contest the board; Interception... no — Vertus + Allarus one-shot Ravagers/Venoms.",
               "Mark + Ka'tah delete the Incubi/Wyches when they commit; hold objectives so they can't just flip late.",
               "Screen with Sisters vs backfield raids; out-score the paper on quality."],
         watch="Getting out-actioned by their raw speed if you sit still — YOU have the speed here, so use it, don't castle."),
    dict(key="astra-militarum", faction="Astra Militarum", archetype="Steel Hammer superheavy / artillery",
         prev="Low-Med (2)", verdict="FAVOURABLE",
         deciding="Their big guns over-kill your W3 bodies (waste) and the 4++ + FNP blunt the rest, while you're fast enough to close and the Allarus (Slayers re-roll vs VEHICLE) + marked spears delete a superheavy in melee. Their infantry can't out-fight yours.",
         plan=["Ingress the Allarus onto a Russ/Shadowsword (Slayers vs VEHICLE) + mark it; delete a tank a turn.",
               "Rush the jetbikes into the gunline; carve the Guard infantry with Sustained spears; hold objectives.",
               "Out-body their low-model tank list on primary + secondaries."],
         watch="Artillery + Leontus orders chipping the bricks before you connect; screen + close fast."),
]

BANDS = {
    "FAVOURABLE (bank these)": ["Emperor's Children", "AdMech", "Blood Angels", "Drukhari", "Astra Militarum"],
    "COIN-FLIP / EVEN (practice)": ["T'au (lean fav)", "Dark Angels (lean fav)", "Necrons C'tan", "Custodes MIRROR"],
    "UNFAVOURABLE (the one hole)": ["Orks Green Tide (out-bodied)"],
}
RECORD_NOTE = (
    "The Better Thing 2 is a TOP-TIER all-comers list — ~58-60% prevalence-weighted, with a very high floor: it "
    "has NO bad damage or durability matchup (2+/4++/FNP + Ka'tah + Assemblage out-fights everything), and it "
    "adds the speed + board control + anti-Psyker + cheap actions that most Custodes lists lack (Venatari/Vertus/"
    "Allarus + Sisters of Silence). Realistic 300+ GT: a strong positive record with a genuine top-tables run. "
    "Its ONE structural hole is a true HORDE — ~40 elite models can't out-body ~100 or cover the whole board, so "
    "Orks (and other true swarms) out-score it on primary even while it wins every fight. Everything else, it "
    "out-lasts and deletes. A genuinely nasty Meta-Slayers list — the horde matchup is the only thing to fear.")

VERIFIED_PROFILES = [
    ("--- the melee engine (Guardian spears + Ka'tah) ---", "", ""),
    ("Custodian Guard / Warden / Allarus — Guardian Spear", "S7 | AP-2 | D2 | A5", "the core; +[Sustained] or [Lethal] via Martial Ka'tah, +1 wound vs the Assemblage mark."),
    ("Blade Champion — Vaultswords", "S7 | AP-2 | D2 | A6 | [PRECISION]", "the character-assassin."),
    ("Vertus Praetor — Interceptor lance", "S7 | AP-2 | D2 | A5 | [LANCE]", "+1 to wound on the charge; fast (M12)."),
    ("--- the buffs (from data/bsdata/rules) ---", "", ""),
    ("Martial Ka'tah (ARMY rule)", "each fight: DACATARAI [Sustained Hits 1] or RENDAX [Lethal Hits]", "army-wide melee tech, every unit, every fight."),
    ("Assemblage of Might (Shield Host)", "mark 1 enemy unit -> CHARACTER units +1 to Wound vs it", "point it at the thing you must crack."),
    ("The Hammer Falls (Tharanatoi Hammerblow)", "an ingressed TERMINATOR unit re-rolls charges", "the Allarus alpha (+ Slayers of Tyrants: re-roll Wounds vs CHAR/MON/VEH)."),
    ("--- durability / speed ---", "", ""),
    ("Custodian Guard / Wardens", "T6 | W3 | 2+/4++ | M6 | OC2", "Wardens add Feel No Pain; Valerian adds -1 AP to melee + FNP6+."),
    ("Venatari / Vertus", "T6 W3 2+/M10 · T7 W5 2+/M12", "the speed + board control most Custodes lists lack."),
]
