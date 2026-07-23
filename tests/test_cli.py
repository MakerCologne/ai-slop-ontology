"""Tests for the `slop` CLI toolkit (slopkit)."""

import io
import json
import os
import sys
import unittest
from contextlib import redirect_stdout

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if ROOT not in sys.path:
    sys.path.insert(0, ROOT)

from slopkit.cli import main

SLOP = ("In today's rapidly evolving landscape, our robust, holistic platform "
        "serves as a centralized hub, highlighting our commitment. It's not a "
        "tool. It's a movement. In conclusion, we must adapt.")
CLEAN = "We shipped the billing page on Tuesday. It cut checkout time from 40s to 9s."


def run(argv, stdin=None):
    """Invoke the CLI in-process, capturing stdout and the exit code."""
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


class CliTests(unittest.TestCase):
    def test_info_json_reports_signal_db(self):
        code, out = run(["info", "--json"])
        self.assertEqual(code, 0)
        data = json.loads(out)
        self.assertGreater(data["signals"]["total_signals"], 100)
        self.assertEqual(len(data["rhetorical_patterns"]), 9)
        self.assertIn("german", data["signals"]["languages"])

    def test_score_slop_vs_clean(self):
        _, slop_out = run(["score", "--json", SLOP])
        _, clean_out = run(["score", "--json", CLEAN])
        slop_score = json.loads(slop_out)["slop_score"]
        clean_score = json.loads(clean_out)["slop_score"]
        self.assertGreaterEqual(slop_score, 0.7)
        self.assertLess(clean_score, 0.25)

    def test_classify_json_shape(self):
        code, out = run(["classify", "--json", SLOP])
        self.assertEqual(code, 0)
        data = json.loads(out)
        for key in ("slop_score", "severity", "slop_types", "signals",
                    "dimensions", "countermeasures"):
            self.assertIn(key, data)

    def test_rhetoric_detects_named_patterns(self):
        code, out = run(["rhetoric", "--json", SLOP])
        self.assertEqual(code, 0)
        ids = {p["id"] for p in json.loads(out)["rhetorical_patterns"]}
        self.assertIn("BinaryContrast", ids)
        self.assertIn("FakeStrongVerb", ids)

    def test_rhetoric_clean_text_is_empty(self):
        _, out = run(["rhetoric", "--json", CLEAN])
        self.assertEqual(json.loads(out)["rhetorical_patterns"], [])

    def test_check_combines_score_and_rhetoric(self):
        _, out = run(["check", "--json", SLOP])
        data = json.loads(out)
        self.assertIn("slop_score", data)
        self.assertIn("rhetorical_patterns", data)
        self.assertTrue(data["rhetorical_patterns"])

    def test_stdin_input(self):
        _, out = run(["rhetoric", "--json", "-"],
                     stdin="It's not a model problem. It's a data problem.")
        ids = {p["id"] for p in json.loads(out)["rhetorical_patterns"]}
        self.assertIn("BinaryContrast", ids)

    def test_code_detects_hardcoded_secret(self):
        code_sample = 'api_key = "sk-abcdefgh12345678"\n'
        _, out = run(["code", "--json", code_sample])
        signals = {s["signal"] for s in json.loads(out)["signals"]}
        self.assertIn("HardcodedSecret", signals)

    def test_no_command_prints_help(self):
        code, out = run([])
        self.assertEqual(code, 0)
        self.assertIn("slop", out)

    def test_selfcheck_passes(self):
        code, out = run(["selfcheck"])
        self.assertEqual(code, 0)


if __name__ == "__main__":
    unittest.main()
