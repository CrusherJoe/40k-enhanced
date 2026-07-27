#!/usr/bin/env python3
"""Monte-Carlo playtest: my two heist lists vs "Great Value" (Imperial Fists) on Layout B,
Priority Assets (Vital Link) vs Purge (Destroyer's Wrath). ABSTRACT model -- real EV (mathhammer
engine) + dice variance for the combat that decides the game, a transparent parameterised
objective/secondary model for the rest. Run 10 games per list.

    PYTHONPATH=src python3 tools/mc_greatvalue.py

The point is NOT a precise VP; it's which list WINS MORE OFTEN across variance ("no plan
survives contact"). All modelling assumptions are printed at the top of the output.
"""
import random, statistics
from wh.mathhammer import expected_damage as ed, Target, Mods

def W(S,AP,D,A,ab=None): return {"S":S,"AP":AP,"D":D,"A":A,"BS":"3+","abilities":ab or []}

# ---- my weapons (EV per shot-package) ----
VOLC = W(18,-5,"D6+8","3"); PLAS = W(9,-4,"3","6",["BLAST"]); AVEN = W(6,-2,"2","18")
RFBC = W(10,-1,"3","9",["BLAST"]); THERM = W(12,-4,"D6","3",["MELTA6"]); HELV = W(9,-1,"3","4")
LANCE = {"S":20,"AP":-3,"D":"8","A":"5","WS":"2+","abilities":["LANCE"]}   # Cerastus shock lance (strike)

def noisy(mean, cv=0.35):
    """EV -> a randomised outcome (sums of many dice ~ normal; clamp >=0)."""
    return max(0.0, random.gauss(mean, mean*cv))

def kills(dmg, wounds_per_model, models_left):
    """Turn EV damage into whole models removed (with -1D-style rounding via random)."""
    return min(models_left, int(noisy(dmg)/max(1,wounds_per_model) + random.random()))

# =============================================================== HIS ARMY (Great Value)
def fresh_enemy():
    # oc = total unit OC; w = wounds/model; models; soft = killable-ish; role
    return {
      "brick1":   dict(models=10, w=4, oc=34, soft=False, on=True),  # TH/SS Lysander (unkillable), OC34
      "brick2":   dict(models=10, w=3, oc=21, soft=True,  on=False, tough=True), # cyclone Termies 2+/4++ (10 @OC2 via Inspiring Commander + Librarian OC1 = OC21), reserve
      "sternguard":dict(models=10,w=2, oc=11, soft=True,  on=False),  # reserve; the Dev-Wound alpha leg
      "speeder1": dict(models=1, w=9, oc=3,  soft=True,  on=False),   # Deep Strike
      "speeder2": dict(models=1, w=9, oc=3,  soft=True,  on=False),
      "vanguard1":dict(models=5, w=2, oc=5,  soft=True,  on=True),
      "vanguard2":dict(models=5, w=2, oc=5,  soft=True,  on=True),
      "intercess":dict(models=5, w=2, oc=10, soft=True,  on=True, sticky_home=True), # OC10 sticky his home
      "bladeguard":dict(models=6,w=3, oc=7,  soft=True,  on=True, tough=True),        # tanky (-1 wound + 4++)
    }

def enemy_oc_onboard(e):
    return sum(u["oc"]*(u["models"]/max(1,u.get("_startmodels",u["models"]))) for u in e.values()
               if u["on"] and u["models"]>0)

# =============================================================== MY LISTS
# firepower = mean 'his soft models' I can remove per turn (his stuff exposes to shoot me, or DS in).
# mobile_blades = # of Cerastus Lancers (mobile OC10, kill chars, threaten home, distraction).
# my_oc_forward = OC I can push onto contested objectives (blades + armiger; guns are pinned).
LISTS = {
  # home_prob = chance to crack his STICKY OC10 home late (hard: Intercessors + Armour of Contempt + Hidden).
  # sec_mob = mean mobility-secondary VP/turn. fwd_oc = OC I can push onto contested objectives.
  "2-Lancer":   dict(blades=2, big_guns=1, home_prob=0.30, sec_mob=5.0, fwd_oc=26),  # 2 Lancer + Cast + Crus + Helv
  "2-Castellan":dict(blades=1, big_guns=2, home_prob=0.18, sec_mob=4.0, fwd_oc=16),  # 2 Cast + Crus + Lancer + Helv
}

def my_shooting_kills(cfg, e):
    """Resolve my Shooting phase: strip his exposed soft OC. 2-Castellan kills more (2 Volcano+2 plasma)."""
    removed = []
    # Volcano one-shots a Speeder IF it's exposed (often Hidden/behind terrain -> not every turn).
    for _ in range(cfg["big_guns"]):
        for sp in ("speeder1","speeder2"):
            if e[sp]["on"] and e[sp]["models"]>0 and random.random()<0.7:
                e[sp]["models"]=0; removed.append(sp); break
    # Avenger + RFBC + plasma into the softest EXPOSED infantry. Hidden(>15")/cover/Armour of Contempt cut this
    # hard -- he only shows what he must to shoot me, so my kill pool is smaller than raw firepower suggests.
    anti_inf = 17 + 7*cfg["big_guns"]     # EV dmg pool onto whatever he exposes (Hidden/cover/AoC-discounted)
    order = ["sternguard","vanguard1","vanguard2","brick2","intercess","bladeguard"]
    pool = noisy(anti_inf)
    for name in order:
        u=e[name]
        if not (u["on"] and u["models"]>0): continue
        # tanky units (2+/4++ or -1 wound) soak ~2.2x more; intercessors get Armour of Contempt some turns
        soak = 2.2 if u.get("tough") else (1.5 if name=="intercess" else 1.0)
        dead = min(u["models"], int(pool/(soak*u["w"])))
        if dead>0:
            u["models"]-=dead; pool-=dead*soak*u["w"]
            if u["models"]==0: removed.append(name)
        if pool<=1: break
    return removed

def lancer_melee(cfg, e):
    """Lancers charge (2D6>=need) into a soft target / character; kill + distract. Returns kills + reached_home."""
    reached_home=False; removed=[]
    for _ in range(cfg["blades"]):
        # charge from range: needs ~a 7+ (they advanced up); Full Tilt (advance+charge) helps
        if random.randint(1,6)+random.randint(1,6) >= 6:
            # pick a juicy soft target to delete (Vanguard/Bladeguard/Intercessor/character proxy)
            for name in ("vanguard1","vanguard2","bladeguard","intercess"):
                u=e[name]
                if u["on"] and u["models"]>0:
                    d=kills(ed(LANCE,Target(4,"3+",u["w"],invuln="4+" if u.get("tough") else None,models=u["models"]),Mods(charged=True)), u["w"], u["models"])
                    u["models"]-=d
                    if u["models"]<=0: removed.append(name)
                    break
            if random.random()<0.55: reached_home=True   # a Lancer that lives threatens/reaches his home
    return removed, reached_home

def run_game(list_name):
    cfg = dict(LISTS[list_name]); e = fresh_enemy()
    for u in e.values(): u["_startmodels"]=u["models"]
    me_prim=me_sec=him_prim=him_sec=0
    his_units_killed=0; my_knights_lost=0
    home_is_mine=False
    for rnd in range(1,6):
        # --- HIS TURN (he goes first; I take the valuable last turn) ---
        # He plays OPTIMALLY: reserves arrive when they can shoot AND stay hidden between (R2/R3 stagger).
        if rnd==2:
            for r in ("speeder1","speeder2","brick2"): e[r]["on"]=True
        if rnd==3: e["sternguard"]["on"]=True   # Temporal-Corridor teleport in later, protected, when it counts
        # His alpha into an Oathed Knight (optimal discipline+stratagems). Sternguard Dev is unsaveable.
        alpha = noisy(8 + (10 if e["sternguard"]["on"] and e["sternguard"]["models"]>0 else 0) + 5)
        # a Knight I've had to expose (to shoot/contest) can be FOCUSED down: real kill chance if he stacks it.
        if rnd>=3 and random.random() < 0.22 and my_knights_lost < 2:
            my_knights_lost += 1
            # losing a Knight cascades: less firepower, fewer blades/guns, weaker home-steal + forward OC
            if cfg["blades"]>0 and random.random()<0.5: cfg["blades"]-=1
            else: cfg["big_guns"]=max(0,cfg["big_guns"]-1)
            cfg["fwd_oc"]-=10; cfg["home_prob"]*=0.6
        # His Destroyer's Wrath + secondaries: army-wide OC + STICKY objectives + Armour of Contempt make him
        # a strong SCORER, esp. early while his soft OC is alive.
        e_oc = enemy_oc_onboard(e)
        my_board_oc = cfg["fwd_oc"] + 8
        him_kill = 3 if (my_knights_lost>0 and rnd>=3) or random.random()<0.55 else 0  # kills my chaff most turns
        him_obj = (4 if e_oc>18 else 0) + (6 if e_oc >= my_board_oc else 0)  # he out-controls while soft OC alive
        him_prim += min(15, him_kill + him_obj + (4 if my_knights_lost>0 and rnd>=3 else 0))
        him_sec  += noisy(4.0 + (2.5 if e_oc >= my_board_oc else 0) + (2 if my_knights_lost>0 else 0))
        # --- MY TURN ---
        rem1 = my_shooting_kills(cfg, e)
        rem2, reached = lancer_melee(cfg, e)
        for name in set(rem1+rem2):
            if e[name]["models"]<=0 and not e[name].get("_counted"):
                his_units_killed+=1; e[name]["_counted"]=True
        # Vital Link primary: his OC34 brick squats a central; his broad OC contests the rest until I kill it.
        his_contest = (enemy_oc_onboard(e)-e["brick1"]["oc"])*0.6
        central = 1 if cfg["fwd_oc"] > his_contest and random.random()<0.7 else 0
        me_prim += min(15, 2*central + (4 if cfg["fwd_oc"]>8 else 0) + 4*central)
        me_sec  += noisy(cfg["sec_mob"] + 1.5*(1 if (e["speeder1"]["models"]==0 or e["speeder2"]["models"]==0) else 0))
        # home-steal: only if his Intercessors thinned to <=2 AND a surviving blade reaches+holds it, AND I keep it
        if reached and e["intercess"]["models"]<=2 and random.random() < cfg["home_prob"]:
            home_is_mine=True
        elif e["intercess"]["models"]>2:
            home_is_mine=False
    if home_is_mine: me_prim += 10
    me = min(50,me_prim) + min(40,me_sec)
    him = min(50,him_prim) + min(40,him_sec)
    return round(me), round(him)

def main():
    random.seed()  # nondeterministic across runs; Date-based seeding blocked in-tool but plain seed() ok here
    print("="*74)
    print("MONTE-CARLO PLAYTEST — 20 games/list vs Great Value, Layout B, Vital Link")
    print("="*74)
    print("MODEL ASSUMPTIONS (shred these):")
    print(" - I go SECOND. He plays OPTIMALLY: reserves/teleports his shooters in staggered (R2/R3),")
    print("   keeps his infantry HIDDEN behind terrain between shots (>15\" untargetable), uses Armour of")
    print("   Contempt on defence + Wrathful Conquerors to bank objectives.")
    print(" - His alpha into an Oathed Knight ~18-25 (Sternguard Dev is unsaveable); from R3 a ~22%/turn")
    print("   chance he FOCUSES a Knight to death -- which CASCADES (I lose a gun/blade + forward OC).")
    print(" - His army-wide OC + STICKY objectives make him a strong scorer, esp. early; his home is hard")
    print("   to steal (Intercessors OC10 + AoC + Hidden) -- home_prob 0.18-0.30, thinned-garrison only.")
    print(" - 2-Castellan = more killing/denial; 2-Lancer = 2 mobile OC10 blades (contest+home+distract).")
    print(" - Primary capped 50, secondary capped 40. Win = higher total. THIS IS TUNED TO EXPECT A HARD GAME.")
    print("="*74)
    for name in ("2-Lancer","2-Castellan"):
        res=[run_game(name) for _ in range(20)]
        wins=sum(1 for m,h in res if m>h); mine=[m for m,_ in res]; his=[h for _,h in res]
        print(f"\n### {name} ###")
        print
        (0)
        print(f"  --> record {wins}-{10-wins}   avg Knights {statistics.mean(mine):.1f}  "
              f"avg Fists {statistics.mean(his):.1f}  avg margin {statistics.mean([m-h for m,h in res]):+.1f}")

if __name__=="__main__":
    main()
