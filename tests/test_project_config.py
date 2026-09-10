"""Project-local config (upstream #11 / btm #1138): --config slop.json.

Covers the three config surfaces — term_allowlist, disabled_signals,
weight_overrides — plus validation failures and CLI wiring.
"""

import io
import json
import os
import sys
import tempfile
import unittest
from contextlib import redirect_stdout

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if ROOT not in sys.path:
    sys.path.insert(0, ROOT)

from slopkit.cli import main
from slopkit.project_config import (
    ConfigError,
    ProjectConfig,
    load_project_config,
)

SLOP = ("In today's rapidly evolving landscape, our robust, holistic platform "
        "serves as a centralized hub. Harness the synergy. It's not a tool. "
        "It's a movement. In conclusion, we must adapt.")


def _cfg_file(tmpdir, payload, name="slop.json"):
    path = os.path.join(tmpdir, name)
    with open(path, "w") as f:
        json.dump(payload, f)
    return path


def run(argv, stdin=None):
    buf = io.StringIO()
    old_stdin = sys.stdin
    if stdin is not None:
        sys.stdin = io.StringIO(stdin)
    try:
        with redirect_stdout(buf):
            code = main(argv)
    finally:
        sys.stdin = old_stdin
    return code, buf.getvalue()


class LoadConfigTests(unittest.TestCase):
    def test_minimal_file_is_inactive(self):
        with tempfile.TemporaryDirectory() as td:
            cfg = load_project_config(_cfg_file(td, {}))
        self.assertIsInstance(cfg, ProjectConfig)
        self.assertFalse(cfg.is_active)

    def test_full_file(self):
        with tempfile.TemporaryDirectory() as td:
            cfg = load_project_config(_cfg_file(td, {
                "disabled_signals": ["EmDashExcess"],
                "term_allowlist": ["Harness"],
                "weight_overrides": {"low": 0.1},
            }))
        self.assertEqual(cfg.disabled_signals, {"EmDashExcess"})
        self.assertEqual(cfg.term_allowlist, {"harness"})  # normalized
        self.assertEqual(cfg.weight_overrides, {"low": 0.1})

    def test_unknown_key_rejected(self):
        with tempfile.TemporaryDirectory() as td:
            with self.assertRaises(ConfigError):
                load_project_config(_cfg_file(td, {"foo": 1}))

    def test_bad_severity_rejected(self):
        with tempfile.TemporaryDirectory() as td:
            with self.assertRaises(ConfigError):
                load_project_config(_cfg_file(td, {"weight_overrides": {"mega": 1.0}}))

    def test_bad_weight_range_rejected(self):
        with tempfile.TemporaryDirectory() as td:
            with self.assertRaises(ConfigError):
                load_project_config(_cfg_file(td, {"weight_overrides": {"low": 2.0}}))

    def test_missing_file_rejected(self):
        with self.assertRaises(ConfigError):
            load_project_config("/nonexistent/slop.json")

    def test_non_object_rejected(self):
        with tempfile.TemporaryDirectory() as td:
            path = os.path.join(td, "arr.json")
            with open(path, "w") as f:
                f.write("[1,2]")
            with self.assertRaises(ConfigError):
                load_project_config(path)


class EngineConfigTests(unittest.TestCase):
    """End-to-end: the config actually changes classification output."""

    def _score(self, config_payload):
        with tempfile.TemporaryDirectory() as td:
            cfg_path = _cfg_file(td, config_payload)
            code, out = run(["--config", cfg_path, "classify",
                             "--json", "--file", _write_text(td)])
            self.assertEqual(code, 0, out)
            return json.loads(out)

    def test_allowlist_removes_buzzword_signals(self):
        with tempfile.TemporaryDirectory() as td:
            code, out = run(["classify", "--json", "--file", _write_text(td)])
            base = json.loads(out)
            buzz = [s for s in base["signals"]
                    if "Buzzword" in s["signal"]]
            self.assertTrue(buzz, "fixture must trigger buzzword signals")

        cfg = self._score({"term_allowlist": [
            "harness", "synergy", "robust", "holistic", "landscape",
            "in today's rapidly evolving"]})
        self.assertFalse([s for s in cfg["signals"] if "Buzzword" in s["signal"]])
        self.assertLess(cfg["slop_score"], base["slop_score"])

    def test_disabled_signals_removed_and_rescored(self):
        cfg = self._score({"disabled_signals": ["BuzzwordOveruse",
                                                "BuzzwordOveruse_Severe",
                                                "CriticalBuzzword"]})
        self.assertFalse([s for s in cfg["signals"] if "Buzzword" in s["signal"]])

    def test_weight_overrides_change_score(self):
        cfg = self._score({"weight_overrides": {"low": 0.0, "medium": 0.0,
                                                "high": 0.0, "critical": 0.0}})
        # every remaining signal weighted 0 → Noisy-OR of nothing → 0
        self.assertEqual(cfg["slop_score"], 0.0)
        self.assertEqual(cfg["severity"], "clean")

    def test_without_config_baseline_is_nonzero(self):
        with tempfile.TemporaryDirectory() as td:
            code, out = run(["classify", "--json", "--file", _write_text(td)])
            base = json.loads(out)
        self.assertGreater(base["slop_score"], 0.0)


class CliConfigTests(unittest.TestCase):
    def test_bad_config_exits_2(self):
        with tempfile.TemporaryDirectory() as td:
            cfg = _cfg_file(td, {"nope": True})
            code, out = run(["--config", cfg, "score", "hello"])
        self.assertEqual(code, 2)

    def test_missing_config_exits_2(self):
        code, out = run(["--config", "/nonexistent.json", "score", "hello"])
        self.assertEqual(code, 2)


def _write_text(td):
    path = os.path.join(td, "fixture.txt")
    with open(path, "w") as f:
        f.write(SLOP)
    return path


if __name__ == "__main__":
    unittest.main()
