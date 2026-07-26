#!/usr/bin/env python3
"""Monte-Carlo META GAUNTLET: my two heist lists (2-Lancer / 2-Castellan) vs the documented
boogeyman archetypes (Green Tide excluded -- known auto-loss). Abstract model, UNDERDOG-tuned,
opponents piloted competently (optimal disciplines/auras, detachment stratagems, CP, hidden
deploys). 10 games per (list x enemy). Prints assumptions; the point is RELATIVE robustness.

    PYTHONPATH=src python3 tools/mc_gauntlet.py

Enemy params (calibrated from docs/meta/*.md + the mathhammer we've done):
  obj0      = objectives they reliably contest/hold at full strength (of ~6; incl OC + mobility + sticky)
  obj_floor = objectives I can NEVER take from them (unkillable OC / sticky home / immovable)
  dura      = how much my shooting is soaked stripping their scorers (1.0 soft .. 2.8 C'tan/Monolith)
  ak_dmg    = mean anti-Knight damage/turn into an exposed Knight (their optimal shooting/melee)
  ak_kill   = per-turn (R3+) chance they FOCUS a Knight to death -> cascades (I lose a gun/blade + OC)
  score     = their mean kill/mission secondary base/turn
"""
import random, statistics
from wh.mathhammer import expected_damage as ed, Target, Mods

def noisy(m, cv=0.32): return max(0.0, random.gauss(m, m*cv))

MY_LISTS = {
  # firepower = EV dmg pool/turn onto their killable scorers; my_obj = objectives I push; home = late-push odds
  "2-Lancer":   dict(blades=2, firepower=24, my_obj=3.5, sec_mob=5.0, home=0.30),
  "2-Castellan":dict(blades=1, firepower=31, my_obj=2.6, sec_mob=4.0, home=0.18),
}

ENEMIES = {
  # RE-CALIBRATED from 5 verified 11E tapestry-analysis subagents (2026-07). ak_dmg is the agents'
  # focused anti-Knight EV/turn (documentation); ak_kill is the distilled per-turn big-Knight-kill
  # chance that actually cascades in run_game. Two agent caveats folded in: (a) enemies could stack a
  # 2nd detachment (11E DP) so these are a FLOOR on enemy strength; (b) no Knight falls back+shoots --
  # an engaged gun-Knight shoots OUT at -1 (10.06), so tar-pits cost -1 to hit, not a Knight.
  #
  # FAVOURABLE: flamers/meltas thin; Land Raiders NO invuln (paper tiger) -> I strip their army fast.
  # ak spikes to ~15-22 only if I feed a Knight <12" into a Devastating flamer dump; ~2-4 if I space.
  "Salamanders":    dict(obj0=3.0, obj_floor=1.5, dura=1.2, ak_dmg=9,  ak_kill=0.08, score=4.0),
  # NEAR-EVEN / slight favour: MUTUAL-REMOVAL RACE. Monolith has NO invuln (T13 W22 2+) -> whole-army
  # focus kills ~1/turn; but 12 death rays (S12 AP-4 SusD3) delete an Armiger/turn + big Knight ~2 turns.
  # Rotate every turn + kill the Silent King (reroll-1s/+2"move engine) = win the race.
  "Necron Monolith":dict(obj0=3.0, obj_floor=1.9, dura=1.6, ak_dmg=20, ak_kill=0.33, score=4.0),
  # BAD/LOSS: 4x C'tan = 4++ AND -1 Dmg AND FNP5+ AND reanim D3 -> whole army = ~11.4 EV < 16W; can't
  # kill even ONE/turn. Void Dragon wounds any Knight on 2+ & heals off me; two C'tan = a dead big Knight.
  "Necron C'tan":   dict(obj0=3.5, obj_floor=3.1, dura=3.5, ak_dmg=16, ak_kill=0.42, score=5.5),
  # UNDERDOG/loss: soft bodies but my high-dmg/low-vol guns are the WRONG SHAPE -> can't clear the horde
  # (Avenger = ~2 koptas/turn; 18 koptas = 9 turns). Speshul Ammo (Anti-Veh 4+) + volume kill ~1 Knight/turn;
  # ~55-60 bodies + Fly + 24" Turbo out-body/out-mobile/out-score me on Disruption.
  "Ork Kult Speed": dict(obj0=3.8, obj_floor=2.8, dura=2.4, ak_dmg=20, ak_kill=0.32, score=5.5),
  # FAVOURABLE: flips the 98-31 Sisters loss. DWK bricks OC1 (brick ~OC5-8, slow M5, only 3) vs my OC10
  # big Knights -> I OUT-OC. Bricks ~un-tableable (W4 cap+4++/-1Dmg) but I don't need to: I kill the
  # KILLABLE scorers (Repulsor W16 no-invuln, Eradicators/Sternguard/Scouts W2-3). They focus 1 Knight/turn.
  "DA Deathwing":   dict(obj0=2.2, obj_floor=1.0, dura=1.5, ak_dmg=14, ak_kill=0.22, score=3.5),
  # COIN-FLIP/UNDERDOG (hardened Great Value sim, prior work): unsaveable Sternguard Dev + sticky OC10
  # Intercessors + Armour of Contempt + un-shockable OC22 brick I can never catch.
  "Great Value":    dict(obj0=3.2, obj_floor=2.2, dura=2.0, ak_dmg=18, ak_kill=0.22, score=5.0),
}

def run_game(mycfg, en):
    cfg=dict(mycfg); their_obj=en["obj0"]; my_obj=cfg["my_obj"]; k_lost=0
    me_p=me_s=him_p=him_s=0
    for rnd in range(1,6):
        # --- his turn ---
        if rnd>=3 and random.random()<en["ak_kill"] and k_lost<2:
            k_lost+=1; my_obj=max(1.0,my_obj-1.1); cfg["firepower"]*=0.75; cfg["home"]*=0.6
            if cfg["blades"]>0 and random.random()<0.5: cfg["blades"]-=1
        # his Destroyer's-Wrath-ish primary: kills my chaff most turns + objective clause if he out-controls
        outctrl = their_obj >= my_obj
        him_p += min(15, en["score"] + (5 if outctrl else 2) + (4 if k_lost>0 and rnd>=3 else 0))
        him_s += noisy(en["score"]*0.8 + (2.2 if outctrl else 0) + (1.5 if k_lost>0 else 0))
        # --- my turn ---
        # my shooting erodes their objective pressure (kill their scorers), soaked by durability
        their_obj = max(en["obj_floor"], their_obj - noisy(cfg["firepower"]/(en["dura"]*36)))
        # my Lancer blade(s) claim/threaten an objective + kill (adds obj pressure if they connect)
        for _ in range(cfg["blades"]):
            if random.randint(1,6)+random.randint(1,6) >= 6 and random.random()<0.5:
                my_obj = min(4.0, my_obj+0.2)
        # my Vital Link: score by how many more objectives I hold than he does
        adv = my_obj - their_obj
        me_p += min(15, 2 + (4 if adv>-0.3 else 0) + (4 if adv>0.4 else 0))
        me_s += noisy(cfg["sec_mob"] + (1.5 if their_obj < en["obj0"]-0.5 else 0))  # mobility deck + Bring It Down
    # late push for the opponent's home / a key objective (harder vs sticky/durable)
    if random.random() < cfg["home"]*(0.6 if en["obj_floor"]>=2.4 else 1.0): me_p += 10
    return round(min(50,me_p)+min(40,me_s)), round(min(50,him_p)+min(40,him_s))

def main():
    random.seed()
    print("="*82)
    print("META GAUNTLET — 10 games per (list x enemy), UNDERDOG-tuned, competent opponents")
    print("Green Tide EXCLUDED (known auto-loss). I go 2nd. Opponents: optimal disciplines/auras,")
    print("detachment stratagems, CP, Hidden deploys, Armour-of-Contempt/reanimation/-1-Dmg where they have it.")
    print("="*82)
    hdr = f"{'ENEMY':18}" + "".join(f"{n:>16}" for n in MY_LISTS)
    print(hdr); print("-"*len(hdr))
    totals = {n:[0,0] for n in MY_LISTS}   # [wins, games]
    for ename, en in ENEMIES.items():
        row=f"{ename:18}"
        for lname, cfg in MY_LISTS.items():
            res=[run_game(cfg,en) for _ in range(10)]
            w=sum(1 for m,h in res if m>h); am=statistics.mean(m for m,_ in res); ah=statistics.mean(h for _,h in res)
            totals[lname][0]+=w; totals[lname][1]+=10
            row+=f"  {w:2}-{10-w:<2} ({am:.0f}-{ah:.0f})"
        print(row)
    print("-"*len(hdr))
    tot=f"{'OVERALL':18}"
    for lname in MY_LISTS:
        w,g=totals[lname]; tot+=f"  {w:2}-{g-w:<2} ({100*w/g:.0f}%)     "
    print(tot)
    print("\n(cell = W-L (avg Knights VP - avg enemy VP) over 10 games)")

if __name__=="__main__": main()
