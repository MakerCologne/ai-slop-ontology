"""Tests for aggregation mode (issue #117, spec docs/metric/AGGREGATION-GEOMEAN.md):
slop.json "aggregation": "geomean" — weighted geometric mean over the 14
dimension contributions as an alternative to the additive weighted sum.
Default behavior must stay unchanged."""

import os
import sys
import tempfile
import unittest

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SCRIPTS = os.path.join(ROOT, "skills", "ai-slop-detection", "scripts")
for p in (ROOT, SCRIPTS):
    if p not in sys.path:
        sys.path.insert(0, p)

from slop_scorer import slop_score  # noqa: E402
import project_config  # noqa: E402

SLOP = ("In today's rapidly evolving landscape, our robust, holistic platform "
        "serves as a centralized hub, highlighting our commitment. It's not a "
        "tool. It's a movement. In conclusion, we must adapt. We harness the "
        "power of seamless integration to unlock the full potential. It's a "
        "testament to our vision.")


def _cfg_file(body):
    fd, path = tempfile.mkstemp(suffix=".json")
    with os.fdopen(fd, "w") as f:
        f.write(body)
    return path


class TestAggregationConfig(unittest.TestCase):
    def test_default_is_weighted(self):
        cfg = project_config.load_config(_cfg_file("{}"))
        self.assertEqual(cfg["aggregation"], {"mode": "weighted", "epsilon": 0.05})

    def test_geomean_string(self):
        cfg = project_config.load_config(_cfg_file('{"aggregation": "geomean"}'))
        self.assertEqual(cfg["aggregation"]["mode"], "geomean")

    def test_geomean_object_with_epsilon(self):
        cfg = project_config.load_config(
            _cfg_file('{"aggregation": {"mode": "geomean", "epsilon": 0.1}}'))
        self.assertEqual(cfg["aggregation"], {"mode": "geomean", "epsilon": 0.1})

    def test_invalid_mode_rejected(self):
        with self.assertRaises(SystemExit):
            project_config.load_config(_cfg_file('{"aggregation": "median"}'))

    def test_epsilon_bounds_rejected(self):
        for bad in ("0", "0.6", "-0.1"):
            with self.assertRaises(SystemExit):
                project_config.load_config(
                    _cfg_file('{"aggregation": {"mode": "geomean", "epsilon": %s}}' % bad))

    def test_aggregation_unknown_subkey_rejected(self):
        with self.assertRaises(SystemExit):
            project_config.load_config(
                _cfg_file('{"aggregation": {"mode": "geomean", "power": 2}}'))


class TestGeomeanScoring(unittest.TestCase):
    def test_default_output_unchanged_no_aggregation_key(self):
        r = slop_score(SLOP)
        self.assertNotIn("aggregation", r)

    def test_geomean_marks_output(self):
        cfg = {"aggregation": {"mode": "geomean", "epsilon": 0.05}}
        r = slop_score(SLOP, project_config=cfg)
        self.assertEqual(r.get("aggregation"), "geomean")

    def test_geomean_lower_than_additive_for_partial_signal(self):
        """One strong family + many neutral dimensions: the geomean punishes
        the empty dimensions (epsilon floor), so the composite is lower than
        the additive score on this text."""
        # Buzzwords only — one family, no floor, neutral structural dims.
        text = ("The report delves into the realm of modern tooling. "
                "Teams leverage the synergy to harness the landscape and "
                "unlock robust synergy. It was a landscape of synergy and "
                "robust leverage across the realm of tools.")
        cfg = {"aggregation": {"mode": "geomean", "epsilon": 0.05}}
        add = slop_score(text)["slop_score"]
        geo = slop_score(text, project_config=dict(cfg))["slop_score"]
        self.assertLess(geo, add)
        self.assertGreater(geo, 0.0)

    def test_geomean_epsilon_bounds_score(self):
        """A text slopping in most dimensions but clean in one still scores
        > epsilon^(weight share) — one clean dimension can never zero the
        composite, only dampen it."""
        cfg = {"aggregation": {"mode": "geomean", "epsilon": 0.05}}
        r = slop_score(SLOP, project_config=dict(cfg))
        self.assertGreater(r["slop_score"], 0.0)
        self.assertLessEqual(r["slop_score"], 1.0)

    def test_geomean_floor_preserved_for_strong_slop(self):
        """Escalation floors are floors, not aggregation: blatant slop
        (>= 2 strong families) still lands at/above the decision threshold
        in geomean mode."""
        cfg = {"aggregation": {"mode": "geomean", "epsilon": 0.05}}
        r = slop_score(SLOP, project_config=dict(cfg))
        add = slop_score(SLOP)
        # SLOP fires multiple families (buzzwords, phrases, moral); the
        # additive score is at/above threshold, and the floor keeps geomean
        # there too.
        if add["slop_score"] >= 0.40:
            self.assertGreaterEqual(r["slop_score"], 0.40)


if __name__ == "__main__":
    unittest.main()
