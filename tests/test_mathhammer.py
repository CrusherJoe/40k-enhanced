"""Mathhammer + dice + practice tests. Run: python3 tests/test_mathhammer.py"""

import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from wh import dice, mathhammer as mh, practice  # noqa: E402
from wh.mathhammer import Target, Mods  # noqa: E402


class Dice(unittest.TestCase):
    def test_expected(self):
        self.assertEqual(dice.expected("6"), 6)
        self.assertEqual(dice.expected("D6"), 3.5)
        self.assertEqual(dice.expected("D3"), 2)
        self.assertEqual(dice.expected("2D6"), 7)
        self.assertEqual(dice.expected("D6+3"), 6.5)
        self.assertEqual(dice.expected("D3+3"), 5)

    def test_wound_chart(self):
        self.assertEqual(dice.wound_needed(20, 10), 2)   # S >= 2T
        self.assertEqual(dice.wound_needed(11, 10), 3)   # S > T
        self.assertEqual(dice.wound_needed(10, 10), 4)   # S == T
        self.assertEqual(dice.wound_needed(5, 10), 6)    # 2S <= T
        self.assertEqual(dice.wound_needed(8, 10), 5)    # else

    def test_expected_reroll(self):
        # a D6 with an optimal single re-roll (re-roll 1-3) averages 4.25
        self.assertAlmostEqual(dice.expected_reroll("D6"), 4.25)
        self.assertAlmostEqual(dice.expected_reroll("D6+3"), 7.25)
        self.assertAlmostEqual(dice.expected_reroll("D3"), (2.5 * 2 + 2 * 1) / 3)
        self.assertEqual(dice.expected_reroll("1"), 1)  # fixed value unchanged

    def test_p_roll_clamped(self):
        self.assertAlmostEqual(dice.p_roll(3), 4 / 6)
        self.assertAlmostEqual(dice.p_roll(3, 2), 5 / 6)   # +2 clamps to 2+
        self.assertAlmostEqual(dice.p_roll(6, -1), 1 / 6)  # clamps to 6+


class Keywords(unittest.TestCase):
    def test_multiword_keyword_kept_whole(self):
        kw = mh._kw({"abilities": ["DEVASTATING WOUNDS", "LETHAL HITS", "SUSTAINED HITS 2",
                                    "ANTI-TITANIC 4+", "RAPID FIRE D6+3"]})
        self.assertTrue(kw["DEVASTATING WOUNDS"])
        self.assertTrue(kw["LETHAL HITS"])
        self.assertEqual(kw["SUSTAINED HITS"], 2)
        self.assertEqual(kw["ANTI-TITANIC"], 4)
        self.assertEqual(kw["RAPID FIRE"], "D6+3")


class Damage(unittest.TestCase):
    def test_simple_bolter(self):
        # 4 shots, BS3+, S4 vs T4 (4+), Sv3+ AP0 -> save 3+, D1
        w = {"name": "bolter", "A": 4, "BS": "3+", "S": 4, "AP": 0, "D": 1}
        d = mh.expected_damage(w, Target(toughness=4, save="3+"))
        # 4 * 2/3 hit * 1/2 wound * (1 - 2/3 save) = 4*.667*.5*.333
        self.assertAlmostEqual(d, 4 * (4 / 6) * (3 / 6) * (1 - 4 / 6), places=4)

    def test_devastating_wounds_bypass_saves(self):
        w = {"name": "x", "A": 6, "BS": "2+", "S": 6, "AP": 0, "D": 1, "abilities": ["DEVASTATING WOUNDS"]}
        # vs a 2+ save; without dev almost nothing gets through, dev crit-wounds still land
        d = mh.expected_damage(w, Target(toughness=6, save="2+"))
        self.assertGreater(d, 6 * (5 / 6) * (1 / 6) * 0.9)  # at least the crit-wound mortals

    def test_invuln_caps_save(self):
        w = {"name": "lance", "A": 2, "BS": "3+", "S": 20, "AP": -5, "D": 6}
        no_inv = mh.expected_damage(w, Target(toughness=10, save="3+"))
        inv = mh.expected_damage(w, Target(toughness=10, save="3+", invuln="4+"))
        self.assertLess(inv, no_inv)  # invuln saves some of the AP-ignoring hits

    def test_cover_is_minus_one_to_hit_not_save(self):
        # 11e (13.08): cover worsens BS by 1. A bolter into cover should lose
        # ~1/6 of its hits, and the effect must vanish vs a save-ignoring context.
        w = {"name": "bolter", "A": 6, "BS": "3+", "S": 4, "AP": 0, "D": 1}
        open_ = mh.expected_damage(w, Target(toughness=4, save="4+"))
        cover = mh.expected_damage(w, Target(toughness=4, save="4+", in_cover=True))
        self.assertLess(cover, open_)
        # the reduction is purely on the hit step: cover hits / open hits == (3/6)/(4/6)
        self.assertAlmostEqual(cover / open_, (3 / 6) / (4 / 6), places=6)

    def test_ignores_cover_negates_cover(self):
        w = {"name": "x", "A": 6, "BS": "3+", "S": 4, "AP": 0, "D": 1, "abilities": ["IGNORES COVER"]}
        t_open = Target(toughness=4, save="4+")
        t_cover = Target(toughness=4, save="4+", in_cover=True)
        self.assertAlmostEqual(mh.expected_damage(w, t_open), mh.expected_damage(w, t_cover))

    def test_torrent_ignores_cover_hit_penalty(self):
        # torrent auto-hits, so cover's -1 BS is irrelevant
        w = {"name": "flamer", "A": "D6", "BS": "N/A", "S": 4, "AP": 0, "D": 1, "abilities": ["TORRENT"]}
        t_open = Target(toughness=4, save="4+")
        t_cover = Target(toughness=4, save="4+", in_cover=True)
        self.assertAlmostEqual(mh.expected_damage(w, t_open), mh.expected_damage(w, t_cover))

    def test_melta_and_half_range(self):
        w = {"name": "melta", "A": 1, "BS": "3+", "S": 9, "AP": -4, "D": "D6", "abilities": ["MELTA 2"]}
        far = mh.expected_damage(w, Target(toughness=8, save="3+"))
        near = mh.expected_damage(w, Target(toughness=8, save="3+", half_range=True))
        self.assertGreater(near, far)


class Tactics(unittest.TestCase):
    def test_shooting_threat_adds_move_and_advance(self):
        from wh import tactics as tac
        cas = tac.data.profile_for("Knight Castellan")
        plain = {n: t for n, _, t in tac.shooting_threat(cas, assault=False)}
        asslt = {n: t for n, _, t in tac.shooting_threat(cas, assault=True)}
        # volcano lance 72" + 8" move = 80"; +3.5 advance = 83.5"
        self.assertAlmostEqual(plain["Volcano lance"], 80.0)
        self.assertAlmostEqual(asslt["Volcano lance"], 83.5)

    def test_charge_threat(self):
        from wh import tactics as tac
        lancer = tac.data.profile_for("Cerastus Knight Lancer")
        self.assertAlmostEqual(tac.charge_threat(lancer), 14 + 7 + 1)

    def test_versus_both_directions(self):
        from wh import tactics as tac
        cas = tac.data.profile_for("Knight Castellan")
        lan = tac.data.profile_for("Cerastus Knight Lancer")
        dmg = tac.unit_damage(cas, tac.target_from_profile(lan))
        self.assertGreater(dmg["total"], 0)


class Practice(unittest.TestCase):
    def test_analyse_five_missions(self):
        a = practice.analyse("priority-assets")
        self.assertEqual(len(a["missions"]), 5)
        self.assertTrue(a["themes"])
        # priority-assets is action-heavy: every mission has an Objective Action
        self.assertEqual(len(a["actions"]), 5)

    def test_classify(self):
        self.assertIn("kill-units", practice.classify("One or more enemy units were destroyed this turn."))
        self.assertIn("hold-objectives", practice.classify("For each objective you control."))


if __name__ == "__main__":
    unittest.main(verbosity=2)
