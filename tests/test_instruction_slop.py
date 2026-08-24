"""Tests for instruction-slop analysis (issue #33) — CLAUDE.md/AGENTS.md-like files."""

import os
import sys
import unittest

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SCRIPTS = os.path.join(ROOT, "skills", "ai-slop-detection", "scripts")
sys.path.insert(0, SCRIPTS)

from instruction_slop import analyze_instructions


def ids(text):
    return {s["id"] for s in analyze_instructions(text)["signals"]}


SLOPPY = """# Agent Instructions

Always write clean code and be thorough.
Follow best practices in everything you do.
Use git for version control and commit your changes.
Improve quality continuously.
Always run the tests before pushing.
Never run the tests before pushing.
"""

TIGHT = """# Agent Instructions

Run `pytest tests -q` before every push; a red suite blocks the merge.
Escalate scope changes to the human instead of widening tool permissions.
For dependency additions, verify the package exists in the registry first.
"""


class InstructionSlopTests(unittest.TestCase):
    def test_generic_advice_fires(self):
        self.assertIn("generic-advice", ids("Always write clean code. Be thorough."))

    def test_generic_advice_negative(self):
        result = analyze_instructions(
            "Run `ruff check .` and fix every finding before commit.")
        self.assertNotIn("generic-advice", {s["id"] for s in result["signals"]})

    def test_obvious_fires(self):
        self.assertIn("obvious", ids("Use git for version control."))

    def test_obvious_negative(self):
        self.assertNotIn(
            "obvious",
            ids("Sign every release tag with the release key from the vault."),
        )

    def test_too_vague_fires(self):
        self.assertIn("too-vague", ids("Improve quality."))

    def test_too_vague_negative(self):
        self.assertNotIn(
            "too-vague",
            ids("Raise mutation coverage of fp_guards.py above 80 percent."),
        )

    def test_contradiction_fires(self):
        text = "Always run the tests before pushing.\nNever run the tests before pushing.\n"
        self.assertIn("contradiction", ids(text))

    def test_contradiction_negative(self):
        self.assertNotIn(
            "contradiction",
            ids("Always run the tests before pushing.\nNever push directly to main.\n"),
        )

    def test_tight_instructions_score_few_signals(self):
        sloppy = analyze_instructions(SLOPPY)["signals"]
        tight = analyze_instructions(TIGHT)["signals"]
        self.assertGreater(len(sloppy), len(tight))
        self.assertEqual(len(tight), 0)

    def test_each_signal_carries_evidence_and_keep_when(self):
        for s in analyze_instructions(SLOPPY)["signals"]:
            self.assertIn("evidence", s)
            self.assertIn("keep_when", s)


if __name__ == "__main__":
    unittest.main()
