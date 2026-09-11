"""Tests for project-local config (issue #11): --config slop.json with
disabled_signals, term_allowlist, weight_overrides."""

import io
import json
import os
import sys
import tempfile
import unittest
from contextlib import redirect_stdout

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


class LoadConfigTests(unittest.TestCase):
    def test_valid_full_config(self):
        with tempfile.NamedTemporaryFile("w", suffix=".json", delete=False) as f:
            json.dump({"disabled_signals": ["buzzwords"],
                       "term_allowlist": ["harness"],
                       "weight_overrides": {"phrases": 0.1}}, f)
            path = f.name
        try:
            cfg = project_config.load_config(path)
            self.assertEqual(cfg["disabled_signals"], ["buzzwords"])
            self.assertEqual(cfg["term_allowlist"], ["harness"])
            self.assertEqual(cfg["weight_overrides"], {"phrases": 0.1})
        finally:
            os.unlink(path)

    def test_empty_config_defaults(self):
        with tempfile.NamedTemporaryFile("w", suffix=".json", delete=False) as f:
            f.write("{}")
            path = f.name
        try:
            cfg = project_config.load_config(path)
            self.assertEqual(cfg, {"disabled_signals": [], "term_allowlist": [],
                                   "weight_overrides": {}})
        finally:
            os.unlink(path)

    def test_unknown_signal_family_rejected(self):
        with tempfile.NamedTemporaryFile("w", suffix=".json", delete=False) as f:
            json.dump({"disabled_signals": ["nonexistent"]}, f)
            path = f.name
        try:
            with self.assertRaises(SystemExit):
                project_config.load_config(path)
        finally:
            os.unlink(path)

    def test_unknown_key_rejected(self):
        with tempfile.NamedTemporaryFile("w", suffix=".json", delete=False) as f:
            json.dump({"ban_words": []}, f)
            path = f.name
        try:
            with self.assertRaises(SystemExit):
                project_config.load_config(path)
        finally:
            os.unlink(path)

    def test_negative_weight_rejected(self):
        with tempfile.NamedTemporaryFile("w", suffix=".json", delete=False) as f:
            json.dump({"weight_overrides": {"buzzwords": -1}}, f)
            path = f.name
        try:
            with self.assertRaises(SystemExit):
                project_config.load_config(path)
        finally:
            os.unlink(path)


class ApplyConfigTests(unittest.TestCase):
    def test_baseline_scores_slop(self):
        r = slop_score(SLOP)
        self.assertGreaterEqual(r["slop_score"], 0.4)

    def test_disabled_buzzwords_zeroes_count(self):
        r = slop_score(SLOP, project_config={"disabled_signals": ["buzzwords"]})
        self.assertEqual(r["dimensions"]["buzzword_count"], 0)

    def test_allowlist_reduces_buzzword_count(self):
        base = slop_score(SLOP)["dimensions"]["buzzword_count"]
        r = slop_score(SLOP, project_config={
            "term_allowlist": ["harness", "landscape", "robust", "holistic",
                               "seamless"]})
        self.assertLess(r["dimensions"]["buzzword_count"], base)

    def test_weight_override_changes_score(self):
        # Weight-zeroing alone does NOT remove the strong-evidence escalation
        # floor (honest design): zero weights plus disabled exemptable
        # families is what takes a text to 0.0.
        exemptable = ["buzzwords", "phrases", "multilingual", "provenance",
                      "trailing_moral", "mirrored", "fake_authority",
                      "portability"]
        r = slop_score(SLOP, project_config={
            "disabled_signals": exemptable,
            "weight_overrides": {k: 0.0 for k in (
                "density", "repetition", "burstiness", "punctuation",
                "list_heavy", "verbosity", "structural", "adverb",
                "copula")}})
        self.assertEqual(r["slop_score"], 0.0)

    def test_no_config_unchanged(self):
        # None config must behave exactly like the pre-#11 default call.
        self.assertEqual(slop_score(SLOP)["slop_score"],
                         slop_score(SLOP, project_config=None)["slop_score"])


class CliTests(unittest.TestCase):
    def _run(self, argv, stdin=None):
        import subprocess
        proc = subprocess.run(
            [sys.executable, os.path.join(SCRIPTS, "slop_scorer.py")] + argv,
            input=stdin, capture_output=True, text=True)
        return proc.returncode, proc.stdout

    def test_cli_config_flag(self):
        with tempfile.TemporaryDirectory() as d:
            sample = os.path.join(d, "sample.txt")
            with open(sample, "w") as f:
                f.write(SLOP)
            cfg = os.path.join(d, "cfg.json")
            with open(cfg, "w") as f:
                json.dump({"disabled_signals": ["buzzwords"]}, f)
            _, out = self._run(["--json", "--file", sample, "--config", cfg])
            data = json.loads(out)
            self.assertEqual(data["dimensions"]["buzzword_count"], 0)

    def test_cli_config_auto_discovery(self):
        with tempfile.TemporaryDirectory() as d:
            sample = os.path.join(d, "sample.txt")
            with open(sample, "w") as f:
                f.write(SLOP)
            with open(os.path.join(d, "slop.json"), "w") as f:
                json.dump({"disabled_signals": ["buzzwords"]}, f)
            _, out = self._run(["--json", "--file", sample])
            data = json.loads(out)
            self.assertEqual(data["dimensions"]["buzzword_count"], 0)

    def test_cli_stdin_no_auto_discovery(self):
        # Piped text is environment-independent: no config auto-discovery,
        # regardless of slop.json files lying around the filesystem.
        code, out = self._run(["--json", "-"], stdin=SLOP)
        data = json.loads(out)
        self.assertGreater(data["dimensions"]["buzzword_count"], 0)

    def test_cli_missing_config_file(self):
        code, _ = self._run(["--json", "-", "--config", "/nope.json"], stdin=SLOP)
        self.assertNotEqual(code, 0)

    def test_auto_discover_walks_up(self):
        base = tempfile.mkdtemp(prefix="slopcfg-test-")
        try:
            with open(os.path.join(base, "slop.json"), "w") as f:
                f.write("{}")
            sub = os.path.join(base, "a", "b")
            os.makedirs(sub)
            self.assertEqual(project_config.auto_discover(sub),
                             os.path.join(base, "slop.json"))
        finally:
            import shutil
            shutil.rmtree(base)


if __name__ == "__main__":
    unittest.main()
