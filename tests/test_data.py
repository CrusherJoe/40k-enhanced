"""Data-integrity + planner-invariant tests. Run: python3 tests/test_data.py

Uses only the stdlib (no pytest). Adds src/ to the path so it runs from repo root.
"""

import sys
import unittest
from itertools import combinations
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from wh import data  # noqa: E402
from wh.cli import _unique_conflict  # noqa: E402

DISPS = set(data.dispositions())


class MatrixIntegrity(unittest.TestCase):
    def test_five_dispositions(self):
        self.assertEqual(len(DISPS), 5)

    def test_matrix_is_complete_5x5(self):
        cells = data.matrix()
        self.assertEqual(set(cells), DISPS)
        for you, row in cells.items():
            self.assertEqual(set(row), DISPS, f"row {you} must cover all opponents")

    def test_matrix_missions_are_unique(self):
        names = [m for row in data.matrix().values() for m in row.values()]
        self.assertEqual(len(names), 25)
        self.assertEqual(len(set(names)), 25, "all 25 matrix missions should be distinct")

    def test_missions_yaml_matches_matrix(self):
        by_pair = {(m.you, m.vs): m.name for m in data.missions()}
        self.assertEqual(len(by_pair), 25)
        for you, row in data.matrix().items():
            for opp, mission in row.items():
                self.assertEqual(by_pair.get((you, opp)), mission,
                                 f"missions.yaml disagrees with matrix at {you} vs {opp}")

    def test_diagonal_is_mirror(self):
        # a mirror matchup gives both players the same mission
        for d in DISPS:
            my, theirs = data.matchup(d, d)
            self.assertEqual(my, theirs)


class DetachmentIntegrity(unittest.TestCase):
    def test_dispositions_reference_valid_keys(self):
        for d in data.detachments():
            if d.disposition is not None:
                self.assertIn(d.disposition, DISPS, f"{d.name} has bad disposition key")

    def test_dp_in_range(self):
        for d in data.detachments():
            if d.dp is not None:
                self.assertIn(d.dp, (1, 2, 3), f"{d.name} dp must be 1..3")

    def test_keys_unique(self):
        keys = [d.key for d in data.detachments()]
        self.assertEqual(len(keys), len(set(keys)))

    def test_all_detachments_have_full_rules(self):
        # every IK detachment should carry a named rule + enhancements + stratagems
        for d in data.detachments():
            self.assertTrue(d.rule and d.rule.get("name"), f"{d.name} missing rule")
            self.assertTrue(d.enhancements, f"{d.name} missing enhancements")
            self.assertTrue(d.stratagems, f"{d.name} missing stratagems")
            for s in d.stratagems:
                self.assertTrue(s.get("effect"), f"{d.name}/{s.get('name')} missing effect")

    def test_all_detachments_complete(self):
        # dp + disposition filled for every detachment (no data gap remaining)
        for d in data.detachments():
            self.assertTrue(d.complete, f"{d.name} still missing dp/disposition")


class PointsIntegrity(unittest.TestCase):
    def test_datasheets_have_positive_first_cost(self):
        sheets = data.datasheets()
        self.assertGreaterEqual(len(sheets), 20)
        for s in sheets:
            self.assertGreater(s.points_first, 0, s.name)
            if s.points_additional is not None:
                self.assertGreaterEqual(s.points_additional, s.points_first, s.name)

    def test_nth_copy_cost(self):
        cas = next(s for s in data.datasheets() if s.name == "Knight Castellan")
        self.assertEqual(cas.cost(1), 425)
        self.assertEqual(cas.cost(2), 450)
        self.assertEqual(cas.cost(3), 450)

    def test_wargear_parsed(self):
        cru = next(s for s in data.datasheets() if s.name == "Knight Crusader")
        self.assertEqual(cru.wargear, (("Rapid-fire battle cannon", 15),))

    def test_all_enhancements_have_points(self):
        for d in data.detachments():
            for e in d.enhancements:
                self.assertIsInstance(e.get("points"), int,
                                      f"{d.name}/{e['name']} missing points")


class ProfileIntegrity(unittest.TestCase):
    def test_profiles_load(self):
        profs = data.profiles()
        self.assertEqual(len(profs), 22)  # all IK datasheets, from BSData

    def test_profile_names_have_points(self):
        # every profiled datasheet should also have an MFM points entry
        pts_names = {s.name for s in data.datasheets()}
        for name in data.profiles():
            self.assertIn(name, pts_names, f"{name} profiled but no points")

    def test_stat_lines_complete(self):
        for name, p in data.profiles().items():
            for k in ("M", "T", "Sv", "W", "Ld", "OC"):
                self.assertIn(k, p["stats"], f"{name} missing stat {k}")
            self.assertTrue(p.get("ranged") or p.get("melee"), f"{name} has no weapons")

    def test_weapons_have_core_fields(self):
        for name, p in data.profiles().items():
            for w in p.get("ranged", []):
                for k in ("name", "range", "A", "BS", "S", "AP", "D"):
                    self.assertIn(k, w, f"{name} ranged weapon missing {k}")
            for w in p.get("melee", []):
                for k in ("name", "A", "WS", "S", "AP", "D"):
                    self.assertIn(k, w, f"{name} melee weapon missing {k}")


class PlannerInvariants(unittest.TestCase):
    def test_all_legal_combos_total_3dp_and_have_no_unique_conflict(self):
        dets = [d for d in data.detachments() if d.complete]
        found = 0
        for n in (1, 2, 3):
            for combo in combinations(dets, n):
                if sum(d.dp for d in combo) == 3 and not _unique_conflict(combo):
                    found += 1
                    self.assertEqual(sum(d.dp for d in combo), 3)
        self.assertGreater(found, 0, "should find at least one legal combo")

    def test_unique_conflict_detects_shared_group(self):
        armigers = [d for d in data.detachments() if d.unique == "ARMIGERS"]
        if len(armigers) >= 2:
            self.assertTrue(_unique_conflict(armigers[:2]))


if __name__ == "__main__":
    unittest.main(verbosity=2)
