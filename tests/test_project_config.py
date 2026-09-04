"""Tests for project-local config (issue #11): disabled_signals,
term_allowlist, weight_overrides."""

import json
import os
import subprocess
import sys
import tempfile
import unittest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..",
                                "skills", "ai-slop-detection", "scripts"))

import project_config  # noqa: E402
from slop_scorer import slop_score  # noqa: E402

SLOPPY = ("In today's rapidly evolving landscape, it's worth noting that "
          "we must leverage the power of AI to unlock seamless synergy. "
          "In the grand scheme of things, this serves as a testament to "
          "the robust ecosystem. At the end of the day, harnessing "
          "cutting-edge technology is paramount.")


class TestValidate(unittest.TestCase):
    def test_unknown_signal_rejected(self):
        with self.assertRaises(project_config.ConfigError):
            project_config.validate(
                {"disabled_signals": ["buzzwordz"]})

    def test_unknown_key_rejected(self):
        with self.assertRaises(project_config.ConfigError):
            project_config.validate({"foo": 1})

    def test_weight_range(self):
        with self.assertRaises(project_config.ConfigError):
            project_config.validate({"weight_overrides": {"a": 1.5}},
                                    known_weight_keys=frozenset({"a"}))
        with self.assertRaises(project_config.ConfigError):
            project_config.validate({"weight_overrides": {"a": "x"}},
                                    known_weight_keys=frozenset({"a"}))

    def test_valid(self):
        cfg = project_config.validate(
            {"disabled_signals": ["mirrored"], "term_allowlist": ["Harness"],
             "weight_overrides": {"a": 0.1}},
            known_weight_keys=frozenset({"a"}))
        self.assertEqual(cfg["disabled_signals"], {"mirrored"})
        self.assertEqual(cfg["term_allowlist"], ["harness"])


class TestScoreIntegration(unittest.TestCase):
    def test_disabled_signals_lowers_score(self):
        base = slop_score(SLOPPY)
        cfg = slop_score(SLOPPY, config={
            "disabled_signals": ["buzzwords", "phrases"]})
        self.assertIn("config", cfg)
        self.assertEqual(
            cfg["config"]["disabled_signals"], ["buzzwords", "phrases"])
        self.assertLess(cfg["slop_score"], base["slop_score"])

    def test_term_allowlist(self):
        base = slop_score(SLOPPY)
        cfg = slop_score(SLOPPY, config={"term_allowlist": ["synergy", "ecosystem",
                                                            "cutting-edge"]})
        self.assertLess(cfg["dimensions"]["buzzword_count"],
                        base["dimensions"]["buzzword_count"])
        self.assertLessEqual(cfg["slop_score"], base["slop_score"])

    def test_weight_override(self):
        cfg = slop_score(SLOPPY, config={
            "weight_overrides": {"buzzwords": 0.0}})
        self.assertLess(cfg["slop_score"], slop_score(SLOPPY)["slop_score"])

    def test_invalid_weight_key_raises(self):
        with self.assertRaises(project_config.ConfigError):
            slop_score(SLOPPY, config={"weight_overrides": {"nope": 0.1}})


class TestCli(unittest.TestCase):
    def _cli(self, *extra):
        script = os.path.join(os.path.dirname(__file__), "..",
                              "skills", "ai-slop-detection", "scripts",
                              "slop_scorer.py")
        out = subprocess.run(
            [sys.executable, script, "--json", *extra, "-"],
            input=SLOPPY, capture_output=True, text=True)
        return out

    def test_cli_config(self):
        with tempfile.NamedTemporaryFile("w", suffix=".json",
                                         delete=False) as f:
            json.dump({"disabled_signals": ["buzzwords"],
                       "term_allowlist": ["synergy"],
                       "weight_overrides": {"phrases": 0.05}}, f)
            path = f.name
        try:
            out = self._cli("--config", path)
            self.assertEqual(out.returncode, 0, out.stderr)
            import json as j
            result = j.loads(out.stdout)
            self.assertIn("config", result)
            self.assertEqual(result["config"]["disabled_signals"],
                             ["buzzwords"])
        finally:
            os.unlink(path)

    def test_cli_bad_config_fails(self):
        with tempfile.NamedTemporaryFile("w", suffix=".json",
                                         delete=False) as f:
            f.write('{"disabled_signals": ["bogus"]}')
            path = f.name
        try:
            out = self._cli("--config", path)
            self.assertEqual(out.returncode, 2)
            self.assertIn("unknown signal families", out.stderr)
        finally:
            os.unlink(path)


if __name__ == "__main__":
    unittest.main()
