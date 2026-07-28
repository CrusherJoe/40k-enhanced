"""Build simulator rosters from real DB profiles (stats/weapons) + a weapon-range heuristic (the DB
drops ranges) + hand-set tapestry abilities (crit-on-5, deep strike, reanimation, C'tan -1 damage,
Rotate Ion Shields, etc.). Rosters are representative of the meta archetypes; refine unit lists over
time. Each build_* returns an Army with units pre-deployed along its home row."""
from __future__ import annotations

import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(
    os.path.abspath(__file__))))), "tools"))
import db

from .entities import Unit, Army, OBJECTIVES, HOME_Y, BOARD_W

# weapon-range heuristic (inches) by name fragment; default 24" ranged, 0 = melee.
_RNG = [("volcano", 48), ("las", 48), ("rail", 60), ("gauss", 30), ("plasma", 36), ("melta", 12),
        ("flamer", 12), ("torrent", 12), ("pistol", 12), ("grenade", 12), ("bolt", 24), ("blaster", 18),
        ("dark lance", 36), ("splinter", 24), ("shuriken", 24), ("lance", 0), ("cannon", 36),
        ("launcher", 24), ("gun", 24), ("rifle", 30), ("blade", 0), ("sword", 0), ("spear", 0),
        ("axe", 0), ("fist", 0), ("claw", 0), ("hammer", 0), ("talon", 0), ("misericordia", 0)]


def _range(name, is_melee_list):
    n = name.lower()
    for frag, r in _RNG:
        if frag in n:
            return 0 if (is_melee_list and r == 0) else r
    return 0 if is_melee_list else 24


def _wep(w, is_melee):
    x = dict(w)
    x["abilities"] = list(w.get("abilities") or w.get("keywords") or [])
    x["rng"] = 0 if is_melee else _range(w["name"], is_melee)
    # one slot per list unless the weapon declares its own (e.g. Blade Champion's 3 Vaultswords share
    # a slot) -> each model uses ONE ranged + ONE melee profile (the best vs the target), no over-fire.
    x["slot"] = w.get("slot", "M" if is_melee else "R")
    return x


def mk(slug, name, models, role="line", threat=1.0, abilities=None, ranged=None, melee=None, **over):
    d = db.profile(slug, name)
    s = d["stats"]
    rl = [_wep(w, False) for w in (ranged if ranged is not None else d.get("ranged", []))]
    ml = [_wep(w, True) for w in (melee if melee is not None else d.get("melee", []))]
    ld = int(str(s.get("Ld", "6+")).rstrip("+"))
    return Unit(name=name, models=models, wounds=int(s["W"]), move=int(s["M"]), toughness=int(s["T"]),
                save=s["Sv"], oc=int(s.get("OC", 1)), ld=ld, invuln=d.get("invuln"),
                keywords=tuple(d.get("keywords", [])), ranged=rl, melee=ml, role=role, threat=threat,
                abilities=abilities or {}, **over)


def _embark(transport, passengers, open_topped=True, move=14):
    transport.open_topped = open_topped
    transport.move = move
    transport.role = "fast"
    for p in passengers:
        p.transport = transport
        transport.embarked.append(p)
    return transport


def _deploy(army):
    """Spread units along the home row; forward units a bit up. Reserves stay off-board."""
    y = HOME_Y[army.side]
    on = [u for u in army.units if not u.in_reserve and u.transport is None]
    n = max(1, len(on))
    for i, u in enumerate(on):
        x = 6 + (BOARD_W - 12) * (i / max(1, n - 1)) if n > 1 else BOARD_W / 2
        fwd = 6 if u.role in ("fast", "action", "screen") else 0
        u.pos = (x, y + (fwd if army.side == "A" else -fwd))
        u.side = army.side
    for u in army.units:
        u.side = army.side
    return army


# ---------------- CUSTODES: "The Better Thing 2" (Shield Host + Tharanatoi), Priority Assets --------
# CORRECTED tapestry: Shield Host = Martial Mastery (crit-on-5, melee, army-wide for Ka'tah models).
# NO Assemblage of Might (that is the Auric Champions detachment). Blade Champion has 3 Vaultswords
# profiles (Behemor/Hurricanis/Victus) -> modelled as one melee 'slot' with 3 options, best-picked.
CRIT5 = {"crit_hit": 5}   # Martial Mastery (Shield Host); applies to melee of Martial Ka'tah models


def custodes():
    S = "adeptus-custodes"
    bc_melee = [dict(name="Vaultswords-Behemor", A=6, WS="2+", S=7, AP=-2, D=2, abilities=["PRECISION"], slot="vault"),
                dict(name="Vaultswords-Hurricanis", A=9, WS="2+", S=5, AP=-1, D=1, abilities=["SUSTAINED HITS 1"], slot="vault"),
                dict(name="Vaultswords-Victus", A=5, WS="2+", S=6, AP=-3, D=3, abilities=["DEVASTATING WOUNDS"], slot="vault")]
    spear_r = [dict(name="Guardian Spear (shooting)", A=2, BS="2+", S=4, AP=-1, D=2, abilities=["ASSAULT"])]
    balistus = [dict(name="Balistus grenade launcher", A="D6", BS="2+", S=4, AP=-1, D=1, abilities=["BLAST"])]
    u = [
        mk(S, "Custodian Wardens", 5, role="line", threat=2.4, abilities=dict(CRIT5, fnp=None),
           ranged=spear_r),
        mk(S, "Valerian", 1, role="character", threat=3.0, abilities=CRIT5),
        mk(S, "Blade Champion", 1, role="character", threat=3.0, abilities=dict(CRIT5, reroll_charge=True),
           melee=bc_melee),
        mk(S, "Custodian Guard", 4, role="line", threat=2.2, abilities=CRIT5, ranged=spear_r),
        mk(S, "Shield-Captain", 1, role="character", threat=3.0, abilities=CRIT5),
        mk(S, "Custodian Guard", 5, role="line", threat=2.2, abilities=CRIT5, ranged=spear_r),
        mk(S, "Allarus Custodians", 5, role="anti_tank", threat=3.0,
           abilities=dict(CRIT5, reroll_wounds="fails", reroll_charge=True), ranged=balistus,
           deep_strike=True, in_reserve=True),
        mk(S, "Prosecutors", 4, role="action", threat=0.5),
        mk(S, "Prosecutors", 4, role="action", threat=0.5),
        mk(S, "Venatari Custodians", 3, role="fast", threat=1.2),
        mk(S, "Venatari Custodians", 3, role="fast", threat=1.2),
        mk(S, "Vertus Praetors", 2, role="fast", threat=1.5),
        mk(S, "Vertus Praetors", 2, role="fast", threat=1.5),
        mk(S, "Witchseekers", 4, role="anti_horde", threat=0.6),
    ]
    return _deploy(Army("Custodes — The Better Thing 2", "priority-assets", "A", u, cp=3))


# ---------------- NECRONS: Awakened Dynasty — the real 5-0 "old but new" list (Paul Withington) ------
# THREE C'tan + Skorpekh Lords + characters, almost no chaff. Not a horde — a monster/character wall:
# each C'tan is T11 W16 4++ with -1 to incoming Damage (min 1) and a necrodermis return, and hits like
# a truck in melee. This is what "the C'tan roll over Custodes" means.
def necrons():
    S = "necrons"
    def ctan(name, threat=6.0):
        u = mk(S, name, 1, role="anti_tank", threat=threat)
        u.damage_reduction = 1
        u.invuln = u.invuln or "4+"
        u.fnp = "5+"; u.abilities = dict(u.abilities, comeback=0.8)
        return u
    u = [
        ctan("C'tan Shard of the Nightbringer"),
        ctan("C'tan Shard of the Void Dragon"),
        ctan("Transcendent C'tan"),
        mk(S, "Illuminor Szeras", 1, role="character", threat=3.5),
        mk(S, "Nekrosor Ammentar", 1, role="character", threat=3.0),
        mk(S, "Skorpekh Lord", 1, role="fast", threat=2.4),
        mk(S, "Skorpekh Lord", 1, role="fast", threat=2.2),
        mk(S, "Imotekh the Stormlord", 1, role="character", threat=2.0),
        _reanim(mk(S, "Immortals", 5, role="line", threat=1.0), 0.5),
        mk(S, "Psychomancer", 1, role="character", threat=1.0),
        _reanim(mk(S, "Flayed Ones", 5, role="line", threat=0.8, deep_strike=True, in_reserve=True), 0.4),
        mk(S, "Ophydian Destroyers", 3, role="line", threat=1.4, deep_strike=True, in_reserve=True),
    ]
    return _deploy(Army("Necrons — Awakened Dynasty (5-0 triple-C'tan)", "take-and-hold", "B", u, cp=3))


def _reanim(u, frac):
    u.reanimate = frac
    return u


# ---------------- DRUKHARI: Skysplinter Assault (Reconnaissance) — fast, poison volume, fragile -----
def drukhari():
    S = "drukhari"
    kab1, kab2, inc, wy = _kabalites(), _kabalites(), mk(S, "Incubi", 5, role="line", threat=1.6), _wyches()
    r1 = _embark(mk(S, "Raider", 1, role="fast", threat=1.4), [kab1])
    r2 = _embark(mk(S, "Raider", 1, role="fast", threat=1.4), [inc])
    v1 = _embark(mk(S, "Venom", 1, role="fast", threat=1.0), [wy], move=14)
    u = [
        r1, r2, v1,
        mk(S, "Ravager", 1, role="anti_tank", threat=2.2),
        mk(S, "Ravager", 1, role="anti_tank", threat=2.2),
        mk(S, "Venom", 1, role="fast", threat=1.0),
        kab2,
        mk(S, "Archon", 1, role="character", threat=1.5),
        kab1, inc, wy,     # embarked (excluded from the board until they disembark)
    ]
    return _deploy(Army("Drukhari — Skysplinter", "reconnaissance", "B", u, cp=3))


def _kabalites():
    # Kabalite Warriors: T3 Sv5+ W1, splinter rifles (ANTI-INFANTRY 4+ poison), 10 models
    return Unit(name="Kabalite Warriors", models=10, wounds=1, move=7, toughness=3, save="5+", oc=2,
                ld=7, keywords=("INFANTRY",), role="line", threat=0.7,
                ranged=[dict(name="Splinter rifle", A=2, BS="3+", S=4, AP=0, D=1,
                             abilities=["ANTI-INFANTRY 4+"], rng=24, slot="R")],
                melee=[dict(name="Close combat weapon", A=1, WS="4+", S=3, AP=0, D=1, abilities=[], rng=0, slot="M")])


def _wyches():
    # Wyches: fast melee, T3 W1 6+/4++(melee), poison hekatarii blades, 10 models
    return Unit(name="Wyches", models=10, wounds=1, move=8, toughness=3, save="6+", oc=2, ld=7,
                invuln="4+", keywords=("INFANTRY",), role="fast", threat=0.9,
                melee=[dict(name="Hekatarii blade", A=3, WS="3+", S=3, AP=0, D=1,
                            abilities=["ANTI-INFANTRY 4+"], rng=0, slot="M")])
