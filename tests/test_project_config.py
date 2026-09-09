"""Issue #1138 (GH #11): project-local config (--config slop.json).

disabled_signals / term_allowlist / weight_overrides — validation,
composition with defaults, and the CLI surface.
"""

import json
import os
import subprocess
import sys
import tempfile
import unittest

SCRIPTS = os.path.join(os.path.dirname(__file__), "..",
                       "skills", "ai-slop-detection", "scripts")
sys.path.insert(0, SCRIPTS)

import slop_scorer  # noqa: E402

SLOPPY = ("In today's rapidly evolving landscape, it's worth noting that "
          "we delve into a rich tapestry of cutting-edge harness signals "
          "to unlock seamless synergy.")


def _write_config(tmpdir, payload):
    path = os.path.join(tmpdir, "slop.json")
    with open(path, "w", encoding="utf-8") as f:
        json.dump(payload, f)
    return path


class TestLoadProjectConfig(unittest.TestCase):

    def test_valid_full_config(self):
        with tempfile.TemporaryDirectory() as d:
            path = _write_config(d, {
                "disabled_signals": ["buzzwords"],
                "term_allowlist": ["harness"],
                "weight_overrides": {"phrases": 0.10},
            })
            cfg = slop_scorer.load_project_config(path)
        self.assertEqual(cfg["disabled_signals"], ["buzzwords"])
        self.assertEqual(cfg["term_allowlist"], ["harness"])
        self.assertEqual(cfg["weight_overrides"], {"phrases": 0.1})

    def test_empty_config(self):
        with tempfile.TemporaryDirectory() as d:
            path = _write_config(d, {})
            cfg = slop_scorer.load_project_config(path)
        self.assertEqual(cfg, {"disabled_signals": [],
                               "term_allowlist": [],
                               "weight_overrides": {}})

    def test_unknown_signal_rejected(self):
        with tempfile.TemporaryDirectory() as d:
            path = _write_config(d, {"disabled_signals": ["nonsense"]})
            with self.assertRaises(ValueError):
                slop_scorer.load_project_config(path)

    def test_unknown_key_rejected(self):
        with tempfile.TemporaryDirectory() as d:
            path = _write_config(d, {"threshold": 0.5})
            with self.assertRaises(ValueError):
                slop_scorer.load_project_config(path)

    def test_negative_weight_rejected(self):
        with tempfile.TemporaryDirectory() as d:
            path = _write_config(d, {"weight_overrides": {"phrases": -1}})
            with self.assertRaises(ValueError):
                slop_scorer.load_project_config(path)

    def test_non_string_allowlist_rejected(self):
        with tempfile.TemporaryDirectory() as d:
            path = _write_config(d, {"term_allowlist": [42]})
            with self.assertRaises(ValueError):
                slop_scorer.load_project_config(path)


class TestConfigScoring(unittest.TestCase):

    def test_default_unchanged_without_config(self):
        result = slop_scorer.slop_score(SLOPPY)
        self.assertNotIn("config", result)

    def test_allowlist_reduces_buzzword_hits(self):
        base = slop_scorer.slop_score(SLOPPY)
        cfg = {"disabled_signals": [], "term_allowlist": ["harness"],
               "weight_overrides": {}}
        tuned = slop_scorer.slop_score(SLOPPY, config=cfg)
        self.assertIn("config", tuned)
        self.assertEqual(tuned["config"]["allowlist_terms"], 1)
        self.assertLessEqual(
            tuned["dimensions"]["buzzword_count"],
            base["dimensions"]["buzzword_count"])

    def test_disabled_signal_zeroes_weight_and_lowers_score(self):
        # Build a text whose buzzword signal dominates; disabling buzzwords
        # must not increase the score.
        text = ("seamless synergy across cutting-edge paradigms, "
                "a rich tapestry of innovative leveraging.")
        base = slop_scorer.slop_score(text)
        cfg = {"disabled_signals": ["buzzwords", "phrases"],
               "term_allowlist": [], "weight_overrides": {}}
        tuned = slop_scorer.slop_score(text, config=cfg)
        self.assertLessEqual(tuned["slop_score"], base["slop_score"])
        self.assertEqual(tuned["config"]["disabled_signals"],
                         ["buzzwords", "phrases"])

    def test_weight_override_applied(self):
        cfg = {"disabled_signals": [], "term_allowlist": [],
               "weight_overrides": {"buzzwords": 0.0}}
        tuned = slop_scorer.slop_score(SLOPPY, config=cfg)
        self.assertEqual(tuned["config"]["weight_overrides"], {"buzzwords": 0.0})
        # Zero buzzword weight must not raise the score vs. default.
        base = slop_scorer.slop_score(SLOPPY)
        self.assertLessEqual(tuned["slop_score"], base["slop_score"])

    def test_config_composes_with_genre(self):
        cfg = {"disabled_signals": [], "term_allowlist": ["harness"],
               "weight_overrides": {}}
        tuned = slop_scorer.slop_score(SLOPPY, genre="academic", config=cfg)
        self.assertIn("config", tuned)
        self.assertIn("genre", tuned)

    def test_structural_dimensions_keep_full_text(self):
        # Allowlist stripping applies to SIGNAL matching only — structural
        # dims (repetition etc.) still see the full text.
        cfg = {"disabled_signals": [], "term_allowlist": ["harness"],
               "weight_overrides": {}}
        base = slop_scorer.slop_score(SLOPPY)
        tuned = slop_scorer.slop_score(SLOPPY, config=cfg)
        self.assertEqual(tuned["dimensions"]["information_density"],
                         base["dimensions"]["information_density"])


class TestConfigCLI(unittest.TestCase):

    def _run(self, cli_args, input_text=None):
        return subprocess.run(
            [sys.executable, os.path.join(SCRIPTS, "slop_scorer.py")] + cli_args,
            capture_output=True, text=True, input=input_text)

    def test_cli_config_json_output(self):
        with tempfile.TemporaryDirectory() as d:
            path = _write_config(d, {"disabled_signals": ["buzzwords"],
                                     "term_allowlist": ["harness"]})
            proc = self._run(["--json", "--config", path, "-"],
                             input_text=SLOPPY)
        self.assertEqual(proc.returncode, 0, proc.stderr)
        data = json.loads(proc.stdout)
        self.assertIn("config", data)
        self.assertEqual(data["config"]["disabled_signals"], ["buzzwords"])

    def test_cli_invalid_config_exits_2(self):
        with tempfile.TemporaryDirectory() as d:
            path = _write_config(d, {"disabled_signals": ["bogus"]})
            proc = self._run(["--config", path, "-"], input_text=SLOPPY)
        self.assertEqual(proc.returncode, 2)
        self.assertIn("unknown signal", proc.stderr)


if __name__ == "__main__":
    unittest.main()
