"""List-builder validation + costing tests. Run: python3 tests/test_army.py"""

import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from wh import army  # noqa: E402


def build(**spec):
    return army.build(spec)


class Costing(unittest.TestCase):
    def test_escalating_per_copy(self):
        # Castellan 425 first, 450 each after -> 3 copies = 1325
        a = build(detachments=["questoris-companions"], disposition="take-and-hold",
                  units=[{"datasheet": "Knight Castellan", "count": 3}])
        self.assertEqual(a.lines[0].unit_cost, 425 + 450 + 450)

    def test_flat_unit_no_escalation(self):
        a = build(detachments=["questoris-companions"],
                  units=[{"datasheet": "Armiger Warglaive", "count": 3}])
        self.assertEqual(a.lines[0].unit_cost, 140 * 3)

    def test_wargear_and_enhancement_added(self):
        a = build(detachments=["gate-warden-lance", "questor-forgepact"],
                  disposition="take-and-hold",
                  units=[{"datasheet": "Knight Crusader", "count": 1,
                          "wargear": ["Rapid-fire battle cannon"]},
                         {"datasheet": "Knight Warden", "count": 1,
                          "enhancement": "Acquisitor-at-Arms"}])
        crus = next(l for l in a.lines if l.datasheet == "Knight Crusader")
        ward = next(l for l in a.lines if l.datasheet == "Knight Warden")
        self.assertEqual(crus.total, 395 + 15)
        self.assertEqual(ward.total, 375 + 15)  # Acquisitor-at-Arms = 15


class Legality(unittest.TestCase):
    def test_sample_list_is_legal(self):
        a = army.build_file(str(Path(__file__).resolve().parents[1] / "examples" / "sample-list.yaml"))
        self.assertTrue(a.legal, a.errors)
        self.assertLessEqual(a.points, a.points_limit)

    def test_dp_must_total_three(self):
        a = build(detachments=["gate-warden-lance"], disposition="take-and-hold")  # 2 DP
        self.assertFalse(a.legal)
        self.assertTrue(any("must be exactly 3" in e for e in a.errors))

    def test_disposition_must_be_granted(self):
        # Questoris Companions grants Take and Hold, not Disruption
        a = build(detachments=["questoris-companions"], disposition="disruption")
        self.assertTrue(any("not granted" in e for e in a.errors))

    def test_enhancement_must_belong_to_detachment(self):
        # Blessed Plate is a Dominus Foebreakers enhancement, not Questoris Companions
        a = build(detachments=["questoris-companions"], disposition="take-and-hold",
                  units=[{"datasheet": "Knight Castellan", "enhancement": "Blessed Plate"}])
        self.assertTrue(any("not from any chosen detachment" in e for e in a.errors))

    def test_rule_of_three(self):
        a = build(detachments=["questoris-companions"], disposition="take-and-hold",
                  units=[{"datasheet": "Knight Castellan", "count": 4}])
        self.assertTrue(any("Rule of Three" in e for e in a.errors))

    def test_rule_of_three_aggregates_entries(self):
        a = build(detachments=["questoris-companions"], disposition="take-and-hold",
                  units=[{"datasheet": "Knight Castellan", "count": 2},
                         {"datasheet": "Knight Castellan", "count": 2}])
        self.assertTrue(any("Rule of Three" in e for e in a.errors))

    def test_three_copies_ok(self):
        a = build(detachments=["questoris-companions"], disposition="take-and-hold",
                  units=[{"datasheet": "Knight Castellan", "count": 3}])
        self.assertFalse(any("Rule of Three" in e for e in a.errors))

    def test_over_budget_flagged(self):
        a = build(detachments=["questoris-companions"], disposition="take-and-hold",
                  points_limit=500,
                  units=[{"datasheet": "Acastus Knight Asterius", "count": 1}])  # 785
        self.assertTrue(any("over the" in e for e in a.errors))

    def test_unique_group_conflict(self):
        # two ARMIGERS-unique detachments would conflict -- only one exists, so
        # this just checks the sample path doesn't false-positive
        a = build(detachments=["throne-bonded-outriders", "questor-forgepact",
                               "dominus-foebreakers"], disposition="reconnaissance")
        self.assertNotIn("share a `unique` group", " ".join(a.errors))


if __name__ == "__main__":
    unittest.main(verbosity=2)
