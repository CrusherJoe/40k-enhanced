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
    # normalise DB keywords to UPPERCASE — the sim's footprint/tall/screening/cover checks all test
    # uppercase literals ("VEHICLE"/"MONSTER"/"INFANTRY"); BSData stores them Title-case ("Vehicle").
    kw = tuple(k.upper() for k in d.get("keywords", []))
    return Unit(name=name, models=models, wounds=int(s["W"]), move=int(s["M"]), toughness=int(s["T"]),
                save=s["Sv"], oc=int(s.get("OC", 1)), ld=ld, invuln=d.get("invuln"),
                keywords=kw, ranged=rl, melee=ml, role=role, threat=threat,
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
        # Venatari are DEEP STRIKERS / objective-grabbers / actioners (Engage on All Fronts) — NOT a
        # screen. Deep strike from reserve to grab points + do actions where they're needed.
        mk(S, "Venatari Custodians", 3, role="action", threat=1.2, deep_strike=True, in_reserve=True),
        mk(S, "Venatari Custodians", 3, role="action", threat=1.2, deep_strike=True, in_reserve=True),
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


# ---------------- DRUKHARI: the REAL 6-0 Skysplinter + Exhibition of Slaughter list (Ridvan Martinez) -
# Reconnaissance. Elite/aggressive, NOT the generic paper roster: Drazhar + 2x Incubi (Klaives shred
# Custodes in melee), 3x Scourges + 2x Ravagers (lance/disintegrator anti-tank), a 2++ Archon, and a
# swarm of fast transports/Reavers to out-tempo on Recon. Fragile but it kills + evades + out-scores.
def drukhari():
    S = "drukhari"
    inc1 = mk(S, "Incubi", 5, role="line", threat=2.2)       # Klaive S5 AP-2 D2 A3 — anti-Custodes melee
    inc2 = mk(S, "Incubi", 5, role="line", threat=2.2)
    wy1, wy2 = _wyches(), _wyches()
    kab, hand = _kabalites("Kabalite Warriors"), _kabalites("Hand of the Archon")
    # transports deliver the melee (Skysplinter): Incubi in Venoms, Wyches in Raider/Venom.
    # CORRECT 11e guns (the DB profiles are inflated): Venom = 2x splinter cannon (poison S4 AP0 D1),
    # Raider = 1 dark lance, Ravager = 3 disintegrators.
    def venom(cargo):
        return _embark(mk(S, "Venom", 1, role="fast", threat=1.0, ranged=[_splinter_cannon()]), cargo)
    v1, v2, v3 = venom([inc1]), venom([inc2]), venom([wy1])
    r1 = _embark(mk(S, "Raider", 1, role="fast", threat=1.4, ranged=[_dark_lance()]), [wy2])
    u = [
        mk(S, "Drazhar", 1, role="character", threat=3.5),   # monster-killer demiklaives
        mk(S, "Lady Malys", 1, role="character", threat=2.5),
        _shadowfield(mk(S, "Archon", 1, role="character", threat=2.0)),   # 2++ until it fails once
        mk(S, "Succubus", 1, role="character", threat=1.8),
        v1, v2, v3, r1,
        mk(S, "Ravager", 1, role="anti_tank", threat=2.6, ranged=[dict(_disintegrator(), A=9)]),
        mk(S, "Ravager", 1, role="anti_tank", threat=2.6, ranged=[dict(_disintegrator(), A=9)]),
        _scourges("dark"), _scourges("heat"), _scourges("shard"),   # 3x flying anti-tank/anti-infantry
        _reavers(),
        _mandrakes(),
        mk(S, "Cronos", 2, role="line", threat=1.0, ranged=[]),
        kab, hand,
        inc1, inc2, wy1, wy2,     # embarked
    ]
    return _deploy(Army("Drukhari — Skysplinter/EoS (6-0)", "reconnaissance", "B", u, cp=3))


def _shadowfield(u):
    u.invuln = "2+"; u.abilities = dict(u.abilities, shadowfield=True)   # 2++ until first failed save
    return u


def _splinter_cannon():
    # real 11e poison: S4 AP0 D1, ANTI-INFANTRY 4+ (NOT the DB's inflated AP-1 D2). Venom carries 2 -> A12.
    return dict(name="Splinter cannon", A=12, BS="3+", S=4, AP=0, D=1, abilities=["ANTI-INFANTRY 4+"], rng=36, slot="R")


def _disintegrator():
    return dict(name="Disintegrator cannon", A=3, BS="3+", S=5, AP=-2, D=3, abilities=[], rng=36, slot="R")


def _dark_lance():
    return dict(name="Dark lance", A=1, BS="3+", S=12, AP=-3, D="D6+1", abilities=[], rng=36, slot="R")


def _heat_lance():
    return dict(name="Heat lance", A=1, BS="3+", S=9, AP=-4, D=3, abilities=["MELTA 2"], rng=18, slot="R")


def _scourges(kind):
    # Scourges: T4 W1 4+ M12 (FLY), 5 models, heavy weapons — the list's anti-tank delivery.
    w = {"dark": _dark_lance(), "heat": _heat_lance(),
         "shard": dict(name="Shardcarbine", A=3, BS="3+", S=4, AP=0, D=1, abilities=["ANTI-INFANTRY 4+"], rng=24, slot="R")}[kind]
    # 4 heavy weapons in the unit -> model as 4 shooters carrying the weapon (its real Attacks: lances A1)
    return Unit(name=f"Scourges ({kind})", models=4, wounds=1, move=12, toughness=4, save="4+", oc=1,
                ld=7, keywords=("INFANTRY", "FLY"), role="anti_tank" if kind != "shard" else "fast", threat=1.6,
                ranged=[w],
                melee=[dict(name="Close combat weapon", A=1, WS="4+", S=3, AP=0, D=1, abilities=[], rng=0, slot="M")])


def _reavers():
    # Reaver jetbikes: fast (M14), heat lance + bladevanes, 3 models
    return Unit(name="Reavers", models=3, wounds=3, move=14, toughness=4, save="4+", oc=1, ld=7,
                keywords=("MOUNTED",), role="fast", threat=1.4,
                ranged=[_heat_lance()],
                melee=[dict(name="Bladevanes", A=2, WS="3+", S=4, AP=-1, D=1, abilities=[], rng=0, slot="M")])


def _mandrakes():
    # Mandrakes: deep-strike infiltrators, baleblast (S4 AP-1 D1 psychic), 5 models
    return Unit(name="Mandrakes", models=5, wounds=1, move=8, toughness=3, save="6+", oc=1, ld=7,
                invuln="5+", keywords=("INFANTRY",), role="action", threat=0.8, deep_strike=True, in_reserve=True,
                ranged=[dict(name="Baleblast", A=1, BS="3+", S=4, AP=-1, D=1, abilities=[], rng=18, slot="R")],
                melee=[dict(name="Glimmersteel blade", A=2, WS="3+", S=4, AP=-1, D=1, abilities=[], rng=0, slot="M")])


def _kabalites(name="Kabalite Warriors"):
    # Kabalites: T3 Sv5+ W1, splinter rifles (ANTI-INFANTRY 4+ poison) + a blaster/dark lance, 10 models
    return Unit(name=name, models=10, wounds=1, move=7, toughness=3, save="5+", oc=2,
                ld=7, keywords=("INFANTRY",), role="line", threat=0.8,
                ranged=[dict(name="Splinter rifle", A=2, BS="3+", S=4, AP=0, D=1,
                             abilities=["ANTI-INFANTRY 4+"], rng=24, slot="R")],  # (1 blaster omitted — would over-count per-model)
                melee=[dict(name="Close combat weapon", A=1, WS="4+", S=3, AP=0, D=1, abilities=[], rng=0, slot="M")])


def _wyches():
    # Wyches: fast melee, T3 W1 6+/4++(melee), poison hekatarii blades, 10 models
    return Unit(name="Wyches", models=10, wounds=1, move=8, toughness=3, save="6+", oc=2, ld=7,
                invuln="4+", keywords=("INFANTRY",), role="fast", threat=0.9,
                melee=[dict(name="Hekatarii blade", A=3, WS="3+", S=3, AP=0, D=1,
                            abilities=["ANTI-INFANTRY 4+"], rng=0, slot="M")])


# =====================================================================================================
# THE META FIELD — 8 more real winning lists from the listhammer archive (data/listhammer_archive.json),
# built like necrons()/drukhari(): real DB profiles via mk(), army rule mapped to a real engine effect
# (Oath of Moment -> reroll_hits; monster regen -> fnp; C'tan-return -> comeback; deep strike -> reserve).
# A few datasheets are absent from this BSData cut (Deffkoptas, Aeldari Warlocks, Crisis Sunforge,
# Tyranid Neurolictor) — those are hand-built as REPRESENTATIVE units and flagged inline. Each build_*
# is the actual tournament list's disposition. These are the "known-winning" opponents for what-if runs.
# =====================================================================================================

# Oath of Moment re-rolls hits vs ONE marked enemy unit per turn — NOT every unit re-rolling everything.
# Diffused across a whole army over a game, its average value is ~a re-roll of 1s, so model it army-wide
# as reroll-1s (using "fails"/full re-roll on every unit over-counts it several-fold).
OATH = {"reroll_hits": "ones"}


def _mkf(primary, name, models=1, **kw):
    """mk() with a space-marines fallback: Blood Angels / Dark Angels share most datasheets with vanilla
    Marines and only carry their UNIQUE units in their own BSData slug. Try the chapter slug, then SM."""
    try:
        return mk(primary, name, models, **kw)
    except Exception:
        return mk("space-marines", name, models, **kw)


# ---------------- ORKS: 5-0 Kult of Speed | More Dakka (Disruption) — speed + weight-of-dakka --------
def orks():
    S = "orks"
    u = [
        mk(S, "Wazdakka Gutsmek", 1, role="fast", threat=3.0),                 # T8 W10 warbike warlord
        mk(S, "Big Mek with Shokk Attack Gun", 1, role="character", threat=1.6),
        mk(S, "Zodgrod Wortsnagga", 1, role="character", threat=1.6),
        mk(S, "Big Mek Dakkarig", 1, role="anti_tank", threat=2.2),
        mk(S, "Big Mek Dakkarig", 1, role="anti_tank", threat=2.2),
        mk(S, "Flash Gitz", 5, role="line", threat=1.6),                       # heavy dakka
        mk(S, "Flash Gitz", 5, role="line", threat=1.6),
        mk(S, "Lootas", 10, role="line", threat=1.2),                          # deffgun spam
        mk(S, "Warbikers", 3, role="fast", threat=1.3),
        mk(S, "Warbikers", 3, role="fast", threat=1.3),
        mk(S, "Warbikers", 3, role="fast", threat=1.3),
        mk(S, "Wartrakk", 1, role="fast", threat=1.2),
        mk(S, "Wartrakk", 1, role="fast", threat=1.2),
        mk(S, "Mek", 1, role="character", threat=0.6),
        mk(S, "Mek", 1, role="character", threat=0.6),
        _embark(mk(S, "Trukk", 1, role="fast", threat=0.8), [_orks_gretchin("g1")]),
        _embark(mk(S, "Trukk", 1, role="fast", threat=0.8), [_orks_gretchin("g2")]),
        # Deffkoptas ×3 — now from the real datasheet (data/bsdata/_overrides/orks.json), user-supplied.
        mk(S, "Deffkoptas", 3, role="fast", threat=1.4),
        mk(S, "Deffkoptas", 3, role="fast", threat=1.4),
        mk(S, "Deffkoptas", 3, role="fast", threat=1.4),
    ]
    return _deploy(Army("Orks — Kult of Speed / More Dakka (5-0)", "disruption", "B", u, cp=3))


def _orks_gretchin(_tag):
    return mk("orks", "Gretchin", 10, role="action", threat=0.3)


# ---------------- AELDARI: 5-1 Spirit Conclave | Armoured Warhost (Reconnaissance) — wraith-construct -
# Fast, durable wraith constructs (T6-T10, 2+ saves) + Fire Prisms; Strands of Fate = dice manipulation
# (modelled as a light hit re-roll on the key guns). Battle Focus keeps it slippery on Recon.
def aeldari():
    S = "aeldari"
    FATE = {"reroll_hits": "ones"}
    u = [
        mk(S, "Autarch Wayleaper", 1, role="character", threat=1.8, abilities=FATE),
        mk(S, "Spiritseer", 1, role="character", threat=1.0),
        mk(S, "Wraithlord", 1, role="anti_tank", threat=3.2, abilities=FATE),
        mk(S, "Wraithlord", 1, role="anti_tank", threat=3.2, abilities=FATE),
        mk(S, "Wraithlord", 1, role="anti_tank", threat=3.2, abilities=FATE),
        mk(S, "Wraithblades", 5, role="line", threat=2.0),           # T6 2+ melee wall
        mk(S, "Wraithblades", 5, role="line", threat=2.0),
        mk(S, "Wraithguard", 5, role="anti_tank", threat=2.2, abilities=FATE),   # D-scythe/cannon
        mk(S, "Wraithguard", 5, role="anti_tank", threat=2.2, abilities=FATE),
        mk(S, "Fire Prism", 1, role="anti_tank", threat=3.0, abilities=FATE),
        mk(S, "Fire Prism", 1, role="anti_tank", threat=3.0, abilities=FATE),
        mk(S, "War Walkers", 2, role="line", threat=1.6, abilities=FATE),
        mk(S, "Shroud Runners", 3, role="action", threat=1.0),       # fast recon actioners
        mk(S, "Rangers", 5, role="action", threat=0.7),
        # 3x Warlock Conclave (foot) + 3x Warlock Skyrunners (jetbike) — now from the real datasheets
        # (data/bsdata/_overrides/aeldari.json, user-supplied). Destructor = Torrent psychic flamer.
        mk(S, "Warlock Conclave", 2, role="character", threat=1.1, abilities=FATE),
        mk(S, "Warlock Conclave", 2, role="character", threat=1.1, abilities=FATE),
        mk(S, "Warlock Conclave", 2, role="character", threat=1.1, abilities=FATE),
        mk(S, "Warlock Skyrunners", 1, role="fast", threat=1.1, abilities=FATE),
        mk(S, "Warlock Skyrunners", 1, role="fast", threat=1.1, abilities=FATE),
        mk(S, "Warlock Skyrunners", 1, role="fast", threat=1.1, abilities=FATE),
    ]
    return _deploy(Army("Aeldari — Spirit Conclave / Armoured Warhost (5-1)", "reconnaissance", "B", u, cp=3))


# ---------------- TYRANIDS: 5-0 Talons of the Norn Queen | Assimilation Swarm (Take and Hold) --------
# A monster wall: Norn Assimilator/Emissary (T11 W16), Maleceptors + Haruspex + Psychophages (T9-11).
# Assimilation Swarm heals the monsters -> modelled as fnp 5+ (bio-regen). Synapse steadies the swarm.
def tyranids():
    S = "tyranids"
    def monster(name, threat, heal=False):
        u = mk(S, name, 1, role="anti_tank", threat=threat)
        if heal:
            u.fnp = "5+"                               # Assimilation Swarm regen — the resilient Norns only
        return u
    u = [
        monster("Norn Assimilator", 6.0, heal=True),
        monster("Norn Emissary", 5.5, heal=True),
        monster("Maleceptor", 4.5),
        monster("Maleceptor", 4.5),
        monster("Haruspex", 4.0),
        monster("Psychophage", 3.0),
        monster("Psychophage", 3.0),
        mk(S, "Hive Tyrant", 1, role="character", threat=4.0, abilities=dict(reroll_hits="fails")),  # Synapse warlord
        mk(S, "Tyrant Guard", 3, role="line", threat=1.6),
        mk(S, "Tyranid Prime with Lash Whip", 1, role="character", threat=1.4),
        mk(S, "Hormagaunts", 20, role="fast", threat=0.8),           # fast screen/objective swarm
        mk(S, "Neurolictor", 1, role="action", threat=1.2),          # Lone Operative infiltrator/disruptor (real datasheet)
        mk(S, "Biovores", 1, role="line", threat=1.0),               # indirect spore mines
        mk(S, "Pyrovores", 2, role="line", threat=0.8),
        mk(S, "Pyrovores", 1, role="line", threat=0.8),
    ]
    return _deploy(Army("Tyranids — Talons of the Norn Queen (5-0)", "take-and-hold", "B", u, cp=3))


# ---------------- SPACE MARINES: 6-0 Librarius Conclave / Salamanders (Priority Assets) --------------
# Vulkan + Adrax (Salamanders) lead a Redeemer push: Terminators + Bladeguard deliver, Eradicators/
# Aggressors bring melta+bolt, Land Raider Redeemers are the T12 W16 delivery/firebase. Oath of Moment
# = full hit re-roll vs the marked target (given to the primary damage dealers).
def space_marines():
    S = "space-marines"
    def sala(name, **kw):        # Vulkan/Adrax live in the salamanders datasheet cut
        return mk("salamanders", name, 1, **kw)
    term = mk(S, "Terminator Squad", 5, role="anti_tank", threat=3.0, abilities=OATH,
              deep_strike=True, in_reserve=True)     # deep strikes (NOT in the Redeemer)
    bgv = mk(S, "Bladeguard Veteran Squad", 5, role="line", threat=2.2, abilities=OATH)
    u = [
        sala("Vulkan He'stan", role="character", threat=2.4, abilities=dict(OATH, reroll_wounds="ones")),
        sala("Adrax Agatone", role="character", threat=2.2, abilities=OATH),
        mk(S, "Captain in Gravis Armour", 1, role="character", threat=2.0, abilities=OATH),
        mk(S, "Librarian in Terminator Armour", 1, role="character", threat=1.6, deep_strike=True, in_reserve=True),
        mk(S, "Aggressor Squad", 5, role="line", threat=2.4, abilities=OATH),
        bgv,
        mk(S, "Eradicator Squad", 2, role="anti_tank", threat=2.0, abilities=OATH),   # melta anti-tank
        mk(S, "Eradicator Squad", 2, role="anti_tank", threat=2.0, abilities=OATH),
        mk(S, "Infernus Squad", 4, role="anti_horde", threat=1.0),   # flamers
        mk(S, "Infernus Squad", 4, role="anti_horde", threat=1.0),
        mk(S, "Scout Squad", 4, role="action", threat=0.7),
        mk(S, "Scout Squad", 4, role="action", threat=0.7),
        _embark(mk(S, "Land Raider Redeemer", 1, role="anti_tank", threat=3.4, abilities=OATH), [bgv]),
        mk(S, "Land Raider Redeemer", 1, role="anti_tank", threat=3.4, abilities=OATH),
        term,
    ]
    return _deploy(Army("Space Marines — Librarius Conclave / Salamanders (6-0)", "priority-assets", "B", u, cp=3))


# ---------------- BLOOD ANGELS: 5-0 Liberator Assault Group (Take and Hold) — jump-pack alpha --------
# Death Company + Sanguinary Guard + jump captains: a melee alpha that deep-strikes and charges. Red
# Thirst (+1 to wound on the charge) + Oath -> melee units re-roll hits & wound better when charging.
def blood_angels():
    S = "blood-angels"
    RED = dict(OATH, reroll_wounds="ones", reroll_charge=True)
    u = [
        _mkf(S, "Lemartes", 1, role="character", threat=2.2, abilities=RED, deep_strike=True, in_reserve=True),
        _mkf(S, "Death Company Marines with Jump Packs", 10, role="fast", threat=2.4, abilities=RED,
           deep_strike=True, in_reserve=True),
        _mkf(S, "Death Company Marines with Jump Packs", 10, role="fast", threat=2.4, abilities=RED,
           deep_strike=True, in_reserve=True),
        _mkf(S, "Death Company Captain with Jump Pack", 1, role="character", threat=2.2, abilities=RED,
           deep_strike=True, in_reserve=True),
        _mkf(S, "Captain with Jump Pack", 1, role="character", threat=2.0, abilities=RED,
           deep_strike=True, in_reserve=True),
        _mkf(S, "Sanguinary Guard", 3, role="line", threat=2.2, abilities=RED, deep_strike=True, in_reserve=True),
        _mkf(S, "Sanguinary Guard", 3, role="line", threat=2.2, abilities=RED, deep_strike=True, in_reserve=True),
        _mkf(S, "Chaplain", 1, role="character", threat=1.4),
        _mkf(S, "Sanguinary Priest", 1, role="character", threat=1.2),
        _mkf(S, "Sanguinary Priest", 1, role="character", threat=1.2),
        _mkf(S, "Assault Intercessor Squad", 10, role="line", threat=1.4, abilities=OATH),
        _mkf(S, "Bladeguard Veteran Squad", 5, role="line", threat=2.2, abilities=OATH),
        _mkf(S, "Intercessor Squad", 4, role="action", threat=0.9),
        _mkf(S, "Aggressor Squad", 2, role="line", threat=1.6, abilities=OATH),
        _mkf(S, "Aggressor Squad", 2, role="line", threat=1.6, abilities=OATH),
        _mkf(S, "Outrider Squad", 2, role="fast", threat=1.1),
        _mkf(S, "Scout Squad", 4, role="action", threat=0.7),
        _mkf(S, "Vanguard Veteran Squad with Jump Packs", 4, role="fast", threat=1.2, abilities=RED,
           deep_strike=True, in_reserve=True),
    ]
    return _deploy(Army("Blood Angels — Liberator Assault Group (5-0)", "take-and-hold", "B", u, cp=3))


# ---------------- T'AU: 4-0-1 Retaliation Cadre (Reconnaissance) — deep-strike battlesuit alpha -------
# For the Greater Good: Retaliation Cadre drops battlesuits that re-roll hits & wounds (guided). Crisis
# suits + Commanders bomb in; Broadsides are the T6 W8 railgun firebase; Pathfinders mark; Kroot screen.
def tau():
    S = "tau-empire"
    GUIDED = dict(reroll_hits="ones", reroll_wounds="ones")   # For the Greater Good / markerlight (diffused)
    def suit(name, models, threat, reserve=True):
        return mk(S, name, models, role="anti_tank", threat=threat, abilities=GUIDED,
                  deep_strike=reserve, in_reserve=reserve)
    u = [
        mk(S, "Commander Farsight", 1, role="character", threat=2.6, abilities=GUIDED, deep_strike=True, in_reserve=True),
        mk(S, "Commander in Enforcer Battlesuit", 3, role="character", threat=2.2, abilities=GUIDED, deep_strike=True, in_reserve=True),
        mk(S, "Commander in Coldstar Battlesuit", 2, role="character", threat=2.0, abilities=GUIDED, deep_strike=True, in_reserve=True),
        mk(S, "Commander in Coldstar Battlesuit", 4, role="character", threat=2.0, abilities=GUIDED, deep_strike=True, in_reserve=True),
        suit("Crisis Fireknife Battlesuits", 2, 2.2),
        suit("Crisis Starscythe Battlesuits", 2, 1.8),
        # Crisis Sunforge (melta anti-tank) — now from the real datasheet (data/bsdata/_overrides/tau-empire.json)
        suit("Crisis Sunforge Battlesuits", 3, 2.4),
        suit("Crisis Sunforge Battlesuits", 3, 2.4),
        mk(S, "Broadside Battlesuits", 2, role="anti_tank", threat=2.6, abilities=GUIDED),  # railgun firebase
        mk(S, "Broadside Battlesuits", 1, role="anti_tank", threat=2.6, abilities=GUIDED),
        mk(S, "Stealth Battlesuits", 4, role="action", threat=1.0),
        mk(S, "Stealth Battlesuits", 4, role="action", threat=1.0),
        mk(S, "Darkstrider", 1, role="character", threat=0.8),
        mk(S, "Pathfinder Team", 5, role="action", threat=0.6),
        mk(S, "Pathfinder Team", 5, role="action", threat=0.6),
        mk(S, "Pathfinder Team", 5, role="action", threat=0.6),
        mk(S, "Kroot Carnivores", 10, role="screen", threat=0.5),
        mk(S, "Vespid Stingwings", 4, role="fast", threat=0.7),
    ]
    return _deploy(Army("T'au — Retaliation Cadre (4-0-1)", "reconnaissance", "B", u, cp=3))


# ---------------- DARK ANGELS: 6-0 Darkflight Pursuit / Company of Hunters (Reconnaissance) ----------
# Ravenwing speed: Sammael + speeders + Black Knights zip the board; Lion + Inner Circle are the melee
# brick; Azrael buffs. Fast/outrider tempo on Recon. Oath = hit re-roll on the main guns.
def dark_angels():
    S = "dark-angels"
    def speeder(name, threat):
        return _mkf(S, name, 1, role="fast", threat=threat, abilities=OATH)
    u = [
        _mkf(S, "Lion El'Jonson", 1, role="character", threat=4.0, abilities=dict(OATH, reroll_wounds="ones")),
        _mkf(S, "Azrael", 1, role="character", threat=2.2, abilities=OATH),
        _mkf(S, "Sammael", 1, role="fast", threat=2.2, abilities=OATH),
        _mkf(S, "Inner Circle Companions", 6, role="line", threat=2.4, abilities=OATH),   # elite melee
        _mkf(S, "Ravenwing Command Squad", 3, role="fast", threat=1.6, abilities=OATH),
        _mkf(S, "Ravenwing Black Knights", 3, role="fast", threat=1.6, abilities=OATH),
        speeder("Land Speeder", 1.4),
        speeder("Land Speeder Vengeance", 1.8),
        speeder("Land Speeder Vengeance", 1.8),
        speeder("Land Speeder Vengeance", 1.8),
        _mkf(S, "Ravenwing Darkshroud", 1, role="fast", threat=1.4),      # -1 to hit aura support
        _mkf(S, "Storm Speeder Thunderstrike", 1, role="anti_tank", threat=2.0, abilities=OATH),
        _mkf(S, "Outrider Squad", 2, role="fast", threat=1.1),
        _mkf(S, "Intercessor Squad", 4, role="action", threat=0.9),
        _mkf(S, "Scout Squad", 4, role="action", threat=0.7),
        _mkf(S, "Scout Squad", 4, role="action", threat=0.7),
    ]
    return _deploy(Army("Dark Angels — Darkflight Pursuit / Company of Hunters (6-0)", "reconnaissance", "B", u, cp=3))


# ---------------- THOUSAND SONS: 5-0 Rubricae Phalanx (Take and Hold) — durable psychic grind --------
# Three bricks of Scarab Occult Terminators (T5 W4 2+/4++, All Is Dust) led by Terminator Sorcerers who
# rain mortal wounds (Cabal of Sorcerers). Forgefiends + Sekhetar for fire support; Tzaangors screen.
# All Is Dust (resist low-damage attacks) -> modelled as fnp 5+ on the Rubricae/Scarab bodies.
def thousand_sons():
    S = "thousand-sons"
    DUST = dict()   # bodies below get fnp 5+ set directly
    def scarab(pts_threat=3.0):
        u = mk(S, "Scarab Occult Terminators", 9, role="line", threat=pts_threat, abilities=dict(reroll_wounds="ones"))
        u.fnp = "5+"; u.invuln = u.invuln or "4+"       # All Is Dust + inferno-bolt reroll
        return u
    def sorc(threat):
        u = mk(S, "Sorcerer in Terminator Armour", 1, role="character", threat=threat,
               abilities=dict(reroll_hits="ones"))
        # Cabal mortal-wound output modelled as a devastating psychic bolt
        u.ranged = u.ranged + [dict(name="Doombolt (psychic)", A="D3", BS="2+", S=9, AP=-3, D="D3",
                                    abilities=["DEVASTATING WOUNDS"], rng=18, slot="psy")]
        return u
    u = [
        sorc(1.8), sorc(1.6), sorc(1.6),
        scarab(3.2), scarab(3.2), scarab(3.2),
        mk(S, "Forgefiend", 1, role="anti_tank", threat=2.6),
        mk(S, "Forgefiend", 1, role="anti_tank", threat=2.6),
        mk(S, "Sekhetar Robots", 2, role="line", threat=1.4),
        mk(S, "Sekhetar Robots", 2, role="line", threat=1.4),
        mk(S, "Tzaangor Enlightened", 2, role="fast", threat=0.9),
        mk(S, "Tzaangor Enlightened", 2, role="fast", threat=0.9),
        mk(S, "Tzaangors", 9, role="screen", threat=0.6),
    ]
    return _deploy(Army("Thousand Sons — Rubricae Phalanx (5-0)", "take-and-hold", "B", u, cp=3))
