#!/usr/bin/env python3
"""Full-game simulation v3: my Knights (BIG-GUN STANDOFF -- Valourstrike Lance + Dominus
Foebreakers, Priority Assets) vs the friend's "Great Value" Imperial Fists (Emperor's Shield
+ Librarius Conclave, Purge the Foe).

The durability plan is dead (Battle-shock can't drop his OC22 bricks; contesting a brick's
objective = a dead Knight; FNP 6+ doesn't save a Knight from ~50 melee). This version wins on
SPEED + RANGE + SPREAD: 3 gun-Knights delete his soft scorers from the back, fast Armigers
take the objectives his two M5 bricks can't reach, and I steal his home for +10. Never enter
his charge threat.

    PYTHONPATH=src python3 tools/gen_greatvalue_sim_docx.py
 -> docs/Great-Value-vs-Knights-Full-Game-Simulation.docx
"""
import os
os.environ.setdefault("WH_FACTION", "knights")
from docx import Document
from docx.shared import Pt, RGBColor, Inches
from docx.enum.text import WD_ALIGN_PARAGRAPH

STEEL = RGBColor(0x27, 0x3A, 0x5B)
GOLD  = RGBColor(0x8A, 0x6D, 0x1F)
FIST  = RGBColor(0x8B, 0x1A, 0x1A)
GREY  = RGBColor(0x55, 0x55, 0x55)

doc = Document()
base = doc.styles["Normal"]; base.font.name = "Calibri"; base.font.size = Pt(10.5)

def H(txt, lvl=1, color=STEEL):
    h = doc.add_heading(txt, level=lvl)
    for r in h.runs: r.font.color.rgb = color
    return h
def P(txt="", bold=False, italic=False, color=None, size=None, align=None, space=4):
    p = doc.add_paragraph(); p.paragraph_format.space_after = Pt(space)
    if align: p.alignment = align
    r = p.add_run(txt); r.bold = bold; r.italic = italic
    if color: r.font.color.rgb = color
    if size: r.font.size = Pt(size)
    return p
def rich(parts, space=4):
    p = doc.add_paragraph(); p.paragraph_format.space_after = Pt(space)
    for txt, fmt in parts:
        r = p.add_run(txt)
        r.bold = fmt.get("bold", False); r.italic = fmt.get("italic", False)
        if fmt.get("color"): r.font.color.rgb = fmt["color"]
        if fmt.get("size"): r.font.size = Pt(fmt["size"])
    return p
def bullet(txt, bold_lead=None):
    p = doc.add_paragraph(style="List Bullet"); p.paragraph_format.space_after = Pt(2)
    if bold_lead:
        r = p.add_run(bold_lead); r.bold = True
    p.add_run(txt); return p
def table(headers, rows, widths=None):
    t = doc.add_table(rows=1, cols=len(headers)); t.style = "Light Grid Accent 1"
    for i, h in enumerate(headers):
        c = t.rows[0].cells[i]; c.text = ""
        r = c.paragraphs[0].add_run(h); r.bold = True; r.font.size = Pt(9)
    for row in rows:
        cells = t.add_row().cells
        for i, v in enumerate(row):
            cells[i].text = ""; r = cells[i].paragraphs[0].add_run(str(v)); r.font.size = Pt(9)
    if widths:
        for row in t.rows:
            for i, w in enumerate(widths): row.cells[i].width = Inches(w)
    return t
def tally(me, him, note=""):
    p = doc.add_paragraph(); p.paragraph_format.space_after = Pt(8)
    r = p.add_run("   RUNNING TOTAL — "); r.bold = True
    r = p.add_run(f"Knights {me}"); r.bold = True; r.font.color.rgb = STEEL
    p.add_run("  vs  ")
    r = p.add_run(f"Imperial Fists {him}"); r.bold = True; r.font.color.rgb = FIST
    if note:
        r = p.add_run("   " + note); r.italic = True; r.font.size = Pt(9); r.font.color.rgb = GREY
def turnhead(txt, color):
    p = doc.add_paragraph(); p.paragraph_format.space_before = Pt(6); p.paragraph_format.space_after = Pt(2)
    r = p.add_run(txt); r.bold = True; r.font.size = Pt(12); r.font.color.rgb = color
def phase(name, body):
    p = doc.add_paragraph(); p.paragraph_format.space_after = Pt(3)
    r = p.add_run(name + "  "); r.bold = True; r.font.color.rgb = GOLD; r.font.size = Pt(10)
    r = p.add_run(body); r.font.size = Pt(10)

# ===================================================== TITLE
t = doc.add_paragraph(); t.alignment = WD_ALIGN_PARAGRAPH.CENTER
r = t.add_run("A COMPLETE GAME OF WARHAMMER 40,000 (11E)"); r.bold=True; r.font.size=Pt(20); r.font.color.rgb=STEEL
s = doc.add_paragraph(); s.alignment = WD_ALIGN_PARAGRAPH.CENTER
r = s.add_run("Imperial Knights (Big-Gun Standoff) vs. “Great Value” Imperial Fists"); r.font.size=Pt(13); r.italic=True; r.font.color.rgb=GREY
s2 = doc.add_paragraph(); s2.alignment = WD_ALIGN_PARAGRAPH.CENTER
r = s2.add_run("LSO practice — full model-by-model, phase-by-phase simulation to conclusion (v3 plan)"); r.font.size=Pt(10); r.font.color.rgb=GREY
P()
P("Why this plan (read first)", bold=True, color=GOLD)
P("Three earlier ideas are DEAD, and the game only makes sense once you accept why: (1) You cannot KILL his "
  "bricks — my best guns do ~6–8/turn into a 2+/4++/W4/−1-to-wound Terminator wall. (2) You cannot BATTLE-SHOCK "
  "them off an objective — they only test below half strength (6+ dead first, which I can’t do) and pass on "
  "Ld 6+ ~72% anyway, so their OC22 is permanent. (3) You cannot CONTEST their objective up close — the markers "
  "sit in terrain where the brick lives, so any Knight in range is in charge range, and the brick’s ~50-damage "
  "Oathed melee (Thunder Hammers + Fist of Dorn, all Dev Wounds) deletes any Knight it touches — Feel No Pain 6+ "
  "(~1/6) turns ~50 into ~42, still a dead Knight. So durability and proximity are losing axes.", size=10)
P("What DOES win: his bricks are M5 and there are only two of them. They can hold ~2 objectives, no more. So I "
  "keep three gun-Knights at the BACK, delete his soft scorers (Sternguard, Land Speeders, cyclone Terminators, "
  "Vanguard, Intercessors) at 36–60”, take the 3–4 objectives his wall can’t reach with fast Armigers, steal his "
  "home for the closing +10, and NEVER put a model in his charge threat. This document plays that out in full, "
  "both sides, to a conclusion. Dice are stated as expected values; variance is flagged where it matters.", size=10)

# ===================================================== 1. ARMIES
H("1. The two armies", 1)
P("His list: “Great Value” — Imperial Fists, 1985 pts", bold=True, color=FIST)
P("Detachments (3 DP): Emperor’s Shield (2 DP) + Librarius Conclave (1 DP). Disposition: Purge the Foe.", italic=True, size=9)
table(["Unit (attached)", "Key profile", "The threads that matter"],
[["Lysander + Ancient (Term.) + 10 Assault Terminators (TH/SS)",
  "T5 W4 2+/4++ ×11, M5. Fist of Dorn S10 AP-3 D3 A5 Dev; TH S8 AP-2 D2 A5 Dev",
  "Icon of Obstinacy (unit −1 to wound when S≥T5), Rampart (2+ inv once), Inspiring Commander (non-Character Terminators OC2 while not Battle-shocked → OC22 brick, permanent in practice), Champion of the Feast (+1 A), Terminatus Assault (Battle-shocks what it engages). Wrath of Dorn: FULL wound re-roll vs Oath. ~50 Oathed melee = a dead Knight. AVOID."],
 ["Bladeguard Ancient + 6 Bladeguard", "T4 W3 3+/4++",
  "Malodraxian Standard (−1 to wound when S>T4) + Bladeguard (Swords/Shields). Tanky; not a priority — it’s slow melee I just don’t feed."],
 ["Librarian [Temporal Corridor] + 10 Sternguard", "T4 W2 3+; bolt rifle S4 AP-1 Dev/Heavy/RF1",
  "PSYKER (gets the Discipline). Sternguard Focus = FULL wound re-roll vs Oath. ~10 UNSAVEABLE Dev Wounds into an Oathed Knight — the biggest alpha leg, but SOFT (T4 W2, no invuln). KILL FIRST."],
 ["Librarian (Term.) [Fusillade] + 10 Terminators (2 cyclone)", "T5 W3 2+/4++; cyclone krak S9 AP-2 D6 A2; Teleport Homer",
  "PSYKER. Fusillade (Lethal Hits). Fury of the First (+1 Hit vs Oath). The real ranged Knight-threat — but M5. Kill it after the Speeders."],
 ["2× Vanguard Vets (Jump, 5 ea)", "T4 W2 3+/4++, M12", "Vanguard Assault (Lethal on charge). Fast harassers / soft scorers to shoot off."],
 ["Intercessors (5)", "T4 W2 3+, OC2", "Sticky home. The unit sitting on the home I want to steal."],
 ["2× Land Speeder", "T8 W9 3+, M14", "Multi-melta S9 AP-4 D6 Melta2 + stormfury. Arrives from Strategic Reserve (no innate Deep Strike). Volcano one-shots each — KILL on arrival."]],
widths=[2.0, 2.1, 3.1])
P("His engine: Oath of Moment", bold=True, color=FIST)
P("Each Command phase he Oaths one of my units → his whole army re-rolls Hits AND +1 to Wound vs it, layered "
  "with Wrath of Dorn, the unit synergies, and the round’s Discipline. Fully converged = ~34 into one Knight. "
  "But ~10 of that is the SOFT Sternguard — kill them turn one and his alpha falls to ~17, which a 28-wound "
  "Castellan shrugs (and Rotate Ion Shields → ~14).", size=10)
P()
P("My list: Big-Gun Standoff — Valourstrike Lance + Dominus Foebreakers, 1975 pts", bold=True, color=STEEL)
P("Detachments (3 DP): Valourstrike Lance (2 DP) + Dominus Foebreakers (1 DP). Disposition: Priority Assets.", italic=True, size=9)
table(["Unit", "Guns", "Role in the standoff"],
[["Knight Castellan #1 (DOMINUS)", "Volcano lance S18 AP-5 D6+8; plasma decimator; siegebreaker; shieldbreaker",
  "Back-line sniper. Volcano ONE-SHOTS a Land Speeder (~19 vs 9 W) and chunks Lysander/characters at 60”. Dominus Foebreakers: +1 to hit units in terrain (i.e. his whole army)."],
 ["Knight Castellan #2 (DOMINUS)", "Volcano lance; plasma decimator; siegebreaker",
  "Second back-line sniper — the other Speeder, then Lysander/cyclone brick. Twin plasma decimators also help wipe the Sternguard T1. Also +1 to hit in terrain."],
 ["Knight Crusader", "Avenger gatling S6 AP-2 D2 A18; thermal cannon S12 Melta6; RFBC S10; Icarus",
  "The anti-INFANTRY deleter. Avenger (18 shots) wipes Sternguard / Vanguard / Intercessors; thermal + RFBC add anti-Speeder/Terminator. Stays at the back."],
 ["2× Armiger Helverin", "2× Armiger autocannon S9 AP-1 D3 A4 (36”)",
  "Back-field range. 16 autocannon shots/turn grind the cyclone Terminators and finish Speeders/soft support — never in charge threat."],
 ["Armiger Warglaive", "Thermal spear S12 AP-4 Melta4, M12",
  "The fast body: grabs far objectives, screens the gunline, and can dash for his home. Expendable at 140."],
 ["Navigator (ally)", "12” anti-Deep-Strike dome", "Denies his cyclone-Terminator Teleport-Homer drop and Land Speeder reserves landing near my gunline."],
 ["Battle Sisters (ally, split)", "OC10 foot half; melta half in the Immolator", "Cheaply LOCKS my home objective under the dome — frees every Knight to hunt/hold elsewhere."],
 ["Immolator (ally)", "Twin multi-melta; Purge & Cleanse", "Strips Benefit of Cover on a target for my WHOLE gunline — stacks with Dominus Foebreakers’ +1-to-hit-in-terrain into near-auto-hitting fire."]],
widths=[1.9, 2.4, 2.9])
P("My engine: delete his ranged legs from safety, out-spread his wall, steal his home.", bold=True, color=STEEL)
P("Dominus Foebreakers grants Priority Assets (→ I play Vital Link) and buys my Castellans +1 to hit everything "
  "in terrain. Valourstrike Lance gives Rotate Ion Shields (a 4++ on the Oathed Knight the turn his alpha lands) "
  "and Advance-and-still-shoot (I reposition the gunline to keep range without losing a turn of fire). I do not "
  "own a durability tech and I don’t need one — nothing that can kill a Knight ever gets to shoot twice, and the "
  "melee brick never gets to shoot at all.", size=10)

# ===================================================== 2. MISSION
H("2. Mission, deployment & the scoring clash", 1)
rich([("Asymmetric primaries: ", {"bold":True}), ("my Priority Assets → ", {}), ("Vital Link", {"bold":True,"color":STEEL}),
      ("; his Purge → ", {}), ("Destroyer’s Wrath", {"bold":True,"color":FIST}), (".", {})])
table(["", "Vital Link (me)", "Destroyer’s Wrath (him)"],
[["End of turn", "2 VP control a central objective (+1/operation marker)", "3 VP if he destroyed 1+ enemy unit this turn"],
 ["R2+, end of Command", "4 VP control a non-home objective; +4 if one is central", "4 VP a non-home objective; 6 VP MORE objectives than me"],
 ["R2+, end of turn", "—", "4 VP destroyed more than he lost last turn"],
 ["End of battle", "10 VP control his home", "—"]],
widths=[1.6, 2.7, 2.7])
P("The clash: his OC22 brick will squat the CENTRAL objective and deny me those central bonuses — I accept "
  "that. I win on the NON-central objectives (4 VP), the closing 10 for his home, and secondaries, while my "
  "gunline deletes the mobile scorers he’d need to out-spread me (denying his 6-VP ‘more objectives’ clause). "
  "He farms ~3 VP/turn killing my cheap bodies — capped, and worth far less than a big Knight would have been.", size=10)
P("Deployment — Crucible of Battle (diagonal). Objectives: A = his home, B = my home, C = centre, D/E = "
  "no-man’s-land flanks. I win the roll-off and take the first turn (wipe his Sternguard before he can hide them; "
  "seize objectives).", bold=True)
rich([("My deployment: ", {"bold":True,"color":STEEL}),
      ("both Castellans + the Crusader in a back-corner GUNLINE with LOS across the whole board (they never move "
       "forward). Helverins just ahead of them, also back, 36” guns covering the centre and both flanks. Battle "
       "Sisters OC10 foot half on my home B under the Navigator’s dome; Immolator + melta half central-back. "
       "Warglaive forward-right, ready to run at E and his home. Navigator by B.", {})])
rich([("His deployment: ", {"bold":True,"color":FIST}),
      ("TH/SS brick centre-front; Bladeguard near C; Sternguard mid with firing lines (exposed — they must see to "
       "shoot); one Vanguard each flank; Intercessors on home A. IN RESERVE: cyclone Terminators (Deep Strike to a "
       "Teleport Homer) and both Land Speeders (Strategic Reserve). Two Homer tokens placed mid-board, outside my "
       "dome.", {})])
P("CP: 0 to start, +1 each Command phase. Secondaries: both Tactical. His danger picks — Bring It Down (my "
  "Knights are Vehicles) and Assassination (they’re Characters); but a standoff that loses few models starves both.", size=9, color=GREY)

# ===================================================== ROUND 1
H("Battle Round 1", 1)
turnhead("▶ My Turn 1 — decapitate the ranged, seize the board", STEEL)
phase("Command.", "Gain 1 CP. Code Chivalric vow: the objective-holding vow (a kill-tally vow is worthless vs "
  "unkillable bricks). Priority Assets scores at end of turn.")
phase("Movement.", "The gunline DOES NOT MOVE — it already sees everything from the corner. Immolator advances to "
  "sit on centre C (I’ll cede it later to the brick, but I bank the early central VP now). Warglaive advances "
  "up-right toward E/D. Sisters foot half + Navigator stay on B.")
phase("Shooting.", "WIPE THE STERNGUARD. Crusader Avenger [with Immolator’s Purge & Cleanse stripping their cover] "
  "= 18 shots → ~12 hits → S6>T4 wounds on 3+ → ~8 wounds → AP-2 → ~5 unsaved × D2 = 5 dead; one Castellan’s "
  "plasma decimator (supercharge, 6 Blast shots, +1 to hit in terrain from Dominus Foebreakers) finishes the "
  "other 5. STERNGUARD GONE turn one — his ~10 unsaveable Dev Wounds are off the table for the whole game. The "
  "second Castellan’s Volcano has no Speeder yet, so it chunks the Bladeguard/​brick for chip; Helverins fire into "
  "the Vanguard (~3 dead).")
phase("Charge / Fight.", "None — nothing of mine is anywhere near his lines.")
phase("End of my turn — Vital Link.", "Control central C (Immolator) → 2 VP. Secondary (Engage on All Fronts) → 3 VP.")
tally("5", "0", "The single most important turn in the game: his best Knight-killer is dead and I never left my corner.")

turnhead("▶ His Turn 1 — advance the wall", FIST)
phase("Command.", "Gain 1 CP. Oath: my nearer Castellan — but with his shooters dead/in-reserve it does nothing "
  "this turn. Discipline: Telekinesis (to switch on the cyclone brick’s Deep Strike next round).")
phase("Movement.", "TH/SS brick advances toward C (M5+adv ~9”). Bladeguard toward C. Vanguard jump toward my "
  "right. Intercessors hold A.")
phase("Shooting / Charge / Fight.", "Almost nothing reaches my back-corner gunline. A Vanguard squad jumps at the "
  "Warglaive and charges it → ~4 wounds; Warglaive lives (survives to 10 W) and reaper-cleavers 2 Vanguard back.")
phase("End of his turn — Destroyer’s Wrath.", "0 units destroyed → 0 VP. Secondary → 3 VP.")
tally("5", "3", "His wall is a turn closer, but it has nothing to shoot me with and I’m in no hurry.")

# ===================================================== ROUND 2
H("Battle Round 2 — his alpha lands and bounces", 1)
turnhead("▶ My Turn 2 — bank objectives, keep range", STEEL)
phase("Command.", "Gain 1 CP (2). Vital Link R2+ clause: I hold C (Immolator) + D (Warglaive) → 4 VP (non-home) + "
  "4 VP (C central) = 8 VP.")
phase("Movement.", "Gunline still doesn’t move (it doesn’t need to). Warglaive FALLS BACK from the Vanguard "
  "(Super-heavy Walker: it still shoots) and repositions toward E. If I ever need to shift a Castellan for LOS, "
  "Valourstrike lets it Advance and still fire — but not needed yet.")
phase("Shooting.", "His cyclone brick + Speeders are still in reserve, so I shoot the board: both Volcanoes + "
  "Avenger into the Bladeguard and the advancing brick for chip (I do NOT dump melta into the brick’s 4++ — I "
  "just deny his Bladeguard). ~3 Bladeguard + 3 Vanguard cleared. Helverins hold fire-lanes for the reserves.")
phase("Charge / Fight.", "None.")
phase("End of my turn — Vital Link.", "End-of-turn central C control → 2 VP. Round primary = 8 + 2 = 10. "
  "Secondary (Engage) → 4 VP.")
tally("19", "3", "Objective race banked while his army is still walking and his guns are still in the box.")

turnhead("▶ His Turn 2 — THE alpha", FIST)
phase("Command.", "Gain 1 CP (~3). Oath: my nearer Castellan. Discipline: Divination (re-roll 1s) to sharpen the drop.")
phase("Movement / Reserves.", "Cyclone Terminators Deep Strike to the Homer near E — >9” from my models and "
  "OUTSIDE the Navigator dome (which covers my corner + centre-left), so they land off my right at ~9” from the "
  "Crusader. Both Land Speeders arrive from Strategic Reserve on his right edge, 14” up (still >9”, no Melta bonus). "
  "Brick keeps grinding to C.")
phase("Shooting — the converged alpha into the Oathed Castellan.", "I spend 1 CP on ROTATE ION SHIELDS → that "
  "Castellan is 4++ this turn. Cyclone Terminators (Fury +1 Hit, Oath, Fusillade Lethal, Divination) ≈ 9; Land "
  "Speeders (2 MM + stormfury, >9”, no Melta) ≈ 8. RAW ≈ 17 → 4++ shaves it to ~14. The Castellan (28 W) drops "
  "to ~14 W — bracketed but very much alive, and STILL a 60” Volcano. This is the whole game: because the "
  "Sternguard died on turn 1, the ~10 unsaveable Dev Wounds simply aren’t here.")
phase("Charge.", "The brick reaches C but there is NOTHING of mine in charge range — my Knights are a full board "
  "away in the corner, and the only nearby body is the Immolator (which I’m happy to lose). It can’t catch a "
  "gun-Knight: brick M5 vs my ability to simply not be there. It consolidates onto C.")
phase("Fight.", "None that matters.")
phase("End of his turn — Destroyer’s Wrath.", "Destroyed 0 of my units this turn → 0 on that clause (his alpha "
  "only bracketed a Castellan). Objectives: he now controls C (OC22) → 4 VP; he does NOT control more than me "
  "(I hold B + D + E-adjacent) → no 6 VP. ‘More than I lost last turn’ (I lost 0) → 0. Secondary (Bring It "
  "Down — he shot a Vehicle but destroyed none) → ~2.")
tally("19", "9", "His signature turn produced ZERO kills and 4 primary. A standoff that never exposes a Knight "
  "turns his whole plan into a slow squat on one objective.")

# ===================================================== ROUND 3
H("Battle Round 3 — delete the mobile legs", 1)
turnhead("▶ My Turn 3 — kill the Speeders and the cyclone brick", STEEL)
phase("Command.", "Gain 1 CP (2). Vital Link R2+: his brick squats C, so I take D + E instead → 4 VP (non-home, "
  "no central bonus this turn — accepted).")
phase("Movement.", "Gunline holds. Warglaive runs onto E and threatens toward his home. Nothing approaches the brick.")
phase("Shooting.", "REMOVE HIS RANGED. Castellan #1 Volcano → Land Speeder #1 one-shot (~19 vs 9 W). Castellan #2 "
  "Volcano → Land Speeder #2 one-shot. BOTH SPEEDERS DEAD. Crusader Avenger + 2 Helverins (16 autocannon shots) "
  "into the cyclone Terminators (2+/4++ W3) → ~15 damage through the 4++ → ~5 Terminators dead. His entire mobile "
  "ranged threat is now one half-strength cyclone squad.")
phase("Charge / Fight.", "None.")
phase("End of my turn — Vital Link.", "D + E held (scored 4 at Command). End-of-turn central belongs to the brick "
  "(0). Secondary (Bring It Down — 2 Speeders! + Behind Enemy Lines) → 6 VP.")
tally("29", "9", "Both Speeders and half the cyclone brick gone. After next turn, NOTHING in his army can hurt a "
  "Knight — and my Knights haven’t taken a scratch beyond one bracketed Castellan.")

turnhead("▶ His Turn 3 — squat and squeeze", FIST)
phase("Command.", "Gain 1 CP. Oath: the bracketed Castellan (finish it) or the Warglaive threatening his home. He "
  "Oaths the Warglaive to protect A. Discipline: Divination.")
phase("Movement.", "Brick stays on C (OC22 — his one real board-control tool). Bladeguard remnant shuffles to "
  "contest D. Cyclone remnant repositions to shoot.")
phase("Shooting.", "Cyclone remnant (~5) into the Oathed Warglaive → ~8 → Warglaive to ~6 W, lives. Nothing "
  "reaches my Castellans (they’re in the corner, and the brick has no ranged).")
phase("Charge / Fight.", "Bladeguard try to wall D; no profitable charge into my Knights exists.")
phase("End of his turn — Destroyer’s Wrath.", "0 destroyed → 0. Objectives: he holds C + his home A + contests "
  "D → this snapshot he may control MORE objectives than me → 6 VP + 4 VP (non-home C) = 10 VP. Secondary → 3.")
tally("29", "22", "His one big primary turn — the OC22 brick on centre plus a contested flank. I must break the "
  "objective count next turn, and I have the speed to do it.")

# ===================================================== ROUND 4
H("Battle Round 4 — win the count, take his home", 1)
turnhead("▶ My Turn 4 — out-spread the wall", STEEL)
phase("Command.", "Gain 1 CP (2). Vital Link R2+: I hold D + E → 4 VP.")
phase("Movement.", "SPREAD. Warglaive dashes onto his home A (M12 — his brick is a board away and can’t come back). "
  "The Crusader repositions using Advance-and-still-shoot (Valourstrike) to hold E while keeping its guns online. "
  "Helverins fan to cover D + centre-adjacent. Now across the board I hold B(home) + D + E + push A — more "
  "objectives than his two slow bricks can occupy.")
phase("Shooting.", "Clear his home for the Warglaive: Crusader Avenger + a Castellan plasma delete the 5 "
  "Intercessors on A. The other Castellan + Helverins finish the cyclone Terminators — his last ranged unit is "
  "gone. I still never fire melta into the brick’s 4++.")
phase("Charge.", "Warglaive contests/holds A (his home) uncontested.")
phase("Fight.", "—")
phase("End of my turn — Vital Link.", "D + E (4, scored). I now hold B + D + E + A and he holds only C → I "
  "control MORE objectives, denying his 6-VP swing from here on. Secondary (Behind Enemy Lines + Engage) → 6 VP.")
tally("39", "22", "The board has flipped: his ranged army is dead, his wall holds one square, and I’m sitting on "
  "his home for the closing 10.")

turnhead("▶ His Turn 4 — nothing left but the wall", FIST)
phase("Command.", "Gain 1 CP. Oath: the Warglaive on his home. He spends CP on Fury of the First + Disciplined "
  "Extermination trying to shift it with the brick — but the brick is on C, a board away.")
phase("Movement.", "The TH/SS brick finally turns back toward its home… at M5. It will not arrive in time. "
  "Bladeguard remnant lumbers after the Warglaive.")
phase("Shooting / Charge / Fight.", "With no ranged units left, he can only reach the Warglaive with the slow "
  "Bladeguard remnant — a charge that kills it next turn at best. This turn: nothing of mine dies.")
phase("End of his turn — Destroyer’s Wrath.", "0 destroyed → 0. Objectives: I hold more → no 6 VP; he has only "
  "C → 4 VP. Secondary → 3.")
tally("39", "29", "His army has run out of tools. From here it’s arithmetic.")

# ===================================================== ROUND 5
H("Battle Round 5 — close it out", 1)
turnhead("▶ My Turn 5 — lock every objective I can", STEEL)
phase("Command.", "Gain 1 CP. Vital Link R2+: hold D + E + A → 4 VP.")
phase("Movement.", "Consolidate. Warglaive STAYS on his home A. Gunline holds B/D/E fire-lanes; Sisters never left "
  "B (home locked all game under the dome).")
phase("Shooting.", "Thin the Bladeguard remnant and any body near A so nothing can contest his home at end of "
  "battle. Castellans keep the brick honest but don’t waste melta on it.")
phase("Charge / Fight.", "Positional — stay on objectives, out of the brick’s reach.")
phase("End of my turn — Vital Link.", "End-of-turn: D + E + A (R5 resolves the non-home clause at end of turn too) "
  "→ 4 VP + a Maintain-Control marker on E → +1. Round ≈ 5. Secondary (Behind Enemy Lines + Engage) → 6.")
tally("50", "29", "Now the end-of-battle clause is pending, and I own his home.")

turnhead("▶ His Turn 5 — the last swing", FIST)
phase("Command / Movement / Fight.", "He throws the Bladeguard remnant + whatever can reach at the Warglaive on A. "
  "It likely dies — but it has already done its job (it denied his home for the scoring windows, and I have a "
  "second body one move away to re-take A if needed). Even if he clears A on his turn, the END-OF-BATTLE check is "
  "after MY final positioning; on the average line I keep a model on A.")
phase("End of his turn — Destroyer’s Wrath.", "Destroyed ~1 unit (the Warglaive) → 3 VP; objectives mostly denied "
  "→ ~4. Secondary → 3.")
tally("50", "39", "Before the end-of-battle bonus.")

# ===================================================== RESULT
H("Result & why", 1)
P("End of Battle — Vital Link:", bold=True, color=STEEL)
P("I control his home objective A → +10 VP.", size=11)
p = doc.add_paragraph(); p.alignment = WD_ALIGN_PARAGRAPH.CENTER; p.paragraph_format.space_before = Pt(6)
r = p.add_run("FINAL:  Knights 60  —  Imperial Fists 39"); r.bold=True; r.font.size=Pt(15); r.font.color.rgb=STEEL
P("(Illustrative average-line tally. The margin is wider and safer than any durability build could produce, "
  "because the standoff simply never gives him the kills his mission is built to farm.)",
  italic=True, size=9, align=WD_ALIGN_PARAGRAPH.CENTER, color=GREY)

H("Why the standoff wins where durability loses", 2)
bullet("Kill the Sternguard T1 — same as before, but now from total safety.", bold_lead="1. ")
P("   The gunline wipes them from the back corner. That removes ~10 unsaveable Dev Wounds and turns his ~34 "
  "alpha into ~17 — a number a 28-wound Castellan (Rotate → 4++) simply lives through.", size=9)
bullet("Never enter his charge threat.", bold_lead="2. ")
P("   His ~50-damage brick is the only thing that can reliably kill a Knight, and it never gets to. M5 can’t "
  "catch a gunline that starts and stays 40”+ away. The whole ‘proximity = dead Knight’ problem is designed out.", size=9)
bullet("Delete the mobile legs on schedule.", bold_lead="3. ")
P("   Two Volcanoes one-shot both Land Speeders; Avenger + two Helverins clear the cyclone Terminators over two "
  "turns. By end of Turn 4 he has NO unit that can damage a Knight — and mine are nearly untouched.", size=9)
bullet("Deny his mission, don’t out-kill his bricks.", bold_lead="4. ")
P("   Destroyer’s Wrath wants kills and objective-majority; a standoff that loses only cheap bodies starves the "
  "kill clauses, and killing his mobile scorers lets my fast Armigers out-spread his two M5 bricks for the "
  "majority. I concede the one central square his OC22 brick squats and win everywhere else.", size=9)
bullet("Steal the home the wall marched away from.", bold_lead="5. ")
P("   His bricks advance up-field, leaving A undefended; an M12 Warglaive walks onto it for the closing +10 that "
  "his slow army can’t come back to contest.", size=9)

H("Honest failure modes", 2)
bullet("If he reserves the Sternguard instead of deploying them, I can’t alpha them T1 — they teleport in "
  "later at full strength. Counter: the Navigator dome shrinks their landing zone, and I focus them the instant "
  "they arrive before they can dump a full volley; the gunline has the range to punish any drop.")
bullet("Terrain that blocks my back-corner LOS is the real risk — a standoff only works if my guns can SEE. On a "
  "dense table I must pick a corner with lanes, and use Advance-and-still-shoot (Valourstrike) to buy angles "
  "without surrendering a turn of fire.")
bullet("If he goes first and pushes fast, or if my roll-off loses, I lose the T1 Sternguard wipe — his alpha is "
  "then live for a turn. Rotate Ion Shields + the 28-wound hull buy the time to kill the Sternguard on my T1 "
  "instead.")
bullet("This cedes the centre all game. If the mission/​terrain makes central control worth more than modelled, "
  "the margin tightens — but the home-steal + non-central objectives + secondaries still carry it.")
P()
P("Bottom line: ~60/40 Knights. Not by out-fighting an unkillable wall — by refusing the fight it wants, "
  "deleting the parts of his army that can actually hurt me, and winning the mission with speed the wall can’t "
  "match.", bold=True, color=STEEL)

out = "docs/Great-Value-vs-Knights-Full-Game-Simulation.docx"
doc.save(out)
print("WROTE", out)
