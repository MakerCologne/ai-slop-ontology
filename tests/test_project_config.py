"""Issue #11: project-local config (deslop.toml-equivalent).

--config slop.json with disabled_signals / term_allowlist /
weight_overrides. Fail-loud validation; structural dimensions keep the
full text (allowlist affects signal matching only, like #42 exempt_terms).
"""

import json
import os
import subprocess
import sys
import tempfile
import unittest

SCRIPTS = os.path.join(
    os.path.dirname(__file__), "..", "skills", "ai-slop-detection", "scripts"
)
sys.path.insert(0, SCRIPTS)

import project_config  # noqa: E402
import slop_scorer  # noqa: E402

SCORER = os.path.join(SCRIPTS, "slop_scorer.py")

# Text with buzzwords + phrases: reliably scores above Clean without config.
SLOPPY = (
    "In today's fast-paced world, it's important to note that our "
    "cutting-edge, game-changing solution leverages best practices to "
    "deliver unparalleled value. Furthermore, notably, this robust and "
    "scalable approach is a game-changer. In conclusion, it's important "
    "to remember that the future is now."
)


class TestLoadConfig(unittest.TestCase):
    def test_valid_full_config(self):
        with tempfile.NamedTemporaryFile("w", suffix=".json", delete=False) as f:
            json.dump({
                "disabled_signals": ["portability"],
                "term_allowlist": ["harness", "robust"],
                "weight_overrides": {"buzzwords": 0.05},
            }, f)
            path = f.name
        try:
            cfg = project_config.load_config(path, slop_scorer.DEFAULT_WEIGHTS)
            self.assertEqual(cfg["disabled_signals"], ["portability"])
            self.assertEqual(cfg["term_allowlist"], ["harness", "robust"])
            self.assertEqual(cfg["weight_overrides"], {"buzzwords": 0.05})
        finally:
            os.unlink(path)

    def test_missing_file_is_error(self):
        with self.assertRaises(project_config.ConfigError):
            project_config.load_config("/nonexistent/x.json",
                                       slop_scorer.DEFAULT_WEIGHTS)

    def test_unknown_signal_fails_loud(self):
        with tempfile.NamedTemporaryFile("w", suffix=".json", delete=False) as f:
            json.dump({"disabled_signals": ["buzzwordss"]}, f)  # typo
            path = f.name
        try:
            with self.assertRaises(project_config.ConfigError):
                project_config.load_config(path, slop_scorer.DEFAULT_WEIGHTS)
        finally:
            os.unlink(path)

    def test_unknown_key_fails_loud(self):
        with tempfile.NamedTemporaryFile("w", suffix=".json", delete=False) as f:
            json.dump({"allowlist": []}, f)
            path = f.name
        try:
            with self.assertRaises(project_config.ConfigError):
                project_config.load_config(path, slop_scorer.DEFAULT_WEIGHTS)
        finally:
            os.unlink(path)

    def test_out_of_range_weight_fails_loud(self):
        with tempfile.NamedTemporaryFile("w", suffix=".json", delete=False) as f:
            json.dump({"weight_overrides": {"buzzwords": 3.0}}, f)
            path = f.name
        try:
            with self.assertRaises(project_config.ConfigError):
                project_config.load_config(path, slop_scorer.DEFAULT_WEIGHTS)
        finally:
            os.unlink(path)

    def test_invalid_json_is_error(self):
        with tempfile.NamedTemporaryFile("w", suffix=".json", delete=False) as f:
            f.write("{nope")
            path = f.name
        try:
            with self.assertRaises(project_config.ConfigError):
                project_config.load_config(path, slop_scorer.DEFAULT_WEIGHTS)
        finally:
            os.unlink(path)


class TestMergeWeights(unittest.TestCase):
    def test_disable_wins_over_override(self):
        cfg = {"disabled_signals": ["buzzwords"],
               "weight_overrides": {"buzzwords": 0.9, "phrases": 0.01},
               "term_allowlist": []}
        merged = project_config.merge_weights(cfg, slop_scorer.DEFAULT_WEIGHTS)
        self.assertEqual(merged["buzzwords"], 0.0)
        self.assertEqual(merged["phrases"], 0.01)
        # base weights untouched
        self.assertNotEqual(merged["buzzwords"],
                            slop_scorer.DEFAULT_WEIGHTS["buzzwords"])


class TestScorerAllowlist(unittest.TestCase):
    def test_allowlist_removes_buzzword_hits(self):
        base = slop_scorer.slop_score(SLOPPY)
        self.assertGreater(base["dimensions"]["buzzword_count"], 0)
        tuned = slop_scorer.slop_score(
            SLOPPY, term_allowlist=["cutting-edge", "game-changer",
                                    "game-changing", "unparalleled", "robust"])
        self.assertLess(tuned["dimensions"]["buzzword_count"],
                        base["dimensions"]["buzzword_count"])
        self.assertLessEqual(tuned["slop_score"], base["slop_score"])

    def test_allowlist_leaves_structural_dimensions_intact(self):
        base = slop_scorer.slop_score(SLOPPY)
        tuned = slop_scorer.slop_score(SLOPPY, term_allowlist=["robust"])
        self.assertEqual(tuned["dimensions"]["information_density"],
                         base["dimensions"]["information_density"])
        self.assertEqual(tuned["dimensions"]["repetition_ratio"],
                         base["dimensions"]["repetition_ratio"])


class TestCli(unittest.TestCase):
    def _run(self, *extra, config_obj=None):
        args = [sys.executable, SCORER, "--json"]
        if config_obj is not None:
            with tempfile.NamedTemporaryFile("w", suffix=".json",
                                             delete=False) as f:
                json.dump(config_obj, f)
                args += ["--config", f.name]
                cfg_path = f.name
        with tempfile.NamedTemporaryFile("w", suffix=".txt", delete=False) as f:
            f.write(SLOPPY)
            args += ["--file", f.name]
            txt_path = f.name
        try:
            proc = subprocess.run(args, capture_output=True, text=True)
            return proc
        finally:
            os.unlink(txt_path)
            if config_obj is not None:
                os.unlink(cfg_path)

    def test_cli_config_applied_and_reported(self):
        proc = self._run(config_obj={
            "disabled_signals": ["buzzwords", "phrases"],
            "term_allowlist": ["robust"],
        })
        self.assertEqual(proc.returncode, 0, proc.stderr)
        result = json.loads(proc.stdout)
        self.assertIn("project_config", result)
        self.assertEqual(result["project_config"]["disabled_signals"],
                         ["buzzwords", "phrases"])
        self.assertIn("robust",
                      result["project_config"]["term_allowlist"])
        base = json.loads(self._run().stdout)
        self.assertLess(result["slop_score"], base["slop_score"])

    def test_cli_bad_config_exits_nonzero(self):
        proc = self._run(config_obj={"disabled_signals": ["typooo"]})
        self.assertNotEqual(proc.returncode, 0)
        self.assertIn("typooo", proc.stderr)


if __name__ == "__main__":
    unittest.main()
