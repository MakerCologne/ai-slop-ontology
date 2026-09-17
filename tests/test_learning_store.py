"""Tests for the false-positive learning store (issue #29)."""

import json
import os
import subprocess
import sys
import tempfile
import unittest

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SCRIPTS = os.path.join(ROOT, "skills", "ai-slop-detection", "scripts")
sys.path.insert(0, SCRIPTS)

import learning_store
from slop_scorer import slop_score

SLOP_TEXT = (
    "In today's rapidly evolving landscape, it's worth noting that "
    "robust solutions unlock the power of synergy. Ultimately, the "
    "lesson is that innovation matters."
)
# Buzzwords only — no second strong family, so the exemption can actually
# lower the weighted sum instead of hitting the >= 2-family floor (which
# exemptions deliberately cannot wash away, see genre_profiles tests).
BUZZ_TEXT = "The synergy unleashes robust leverage and the tapestry of the realm."


class LearningStoreTests(unittest.TestCase):
    def test_add_and_load_roundtrip(self):
        with tempfile.TemporaryDirectory() as td:
            path = os.path.join(td, "not_slop.jsonl")
            learning_store.add_entry(
                path, signal_id="buzzwords", sample_text=SLOP_TEXT,
                note="legal marketing copy, buzzwords are genre", added_by="hertha",
            )
            entries = learning_store.load_store(path)
            self.assertEqual(len(entries), 1)
            e = entries[0]
            self.assertEqual(e["signal_id"], "buzzwords")
            self.assertEqual(e["sample_hash"], learning_store.sample_hash(SLOP_TEXT))
            self.assertEqual(
                sorted(e), ["added_by", "date", "note", "sample_hash", "signal_id"]
            )
            self.assertEqual(e["added_by"], "hertha")

    def test_exemption_matches_only_same_sample(self):
        with tempfile.TemporaryDirectory() as td:
            path = os.path.join(td, "not_slop.jsonl")
            learning_store.add_entry(path, "buzzwords", SLOP_TEXT)
            entries = learning_store.load_store(path)
            self.assertIn(
                "buzzwords",
                learning_store.exemptions_for(entries, learning_store.sample_hash(SLOP_TEXT)),
            )
            self.assertEqual(
                learning_store.exemptions_for(
                    entries, learning_store.sample_hash("completely different text")),
                set(),
            )


class ScorerIntegrationTests(unittest.TestCase):
    def test_exempted_signal_is_removed_and_reported(self):
        with tempfile.TemporaryDirectory() as td:
            path = os.path.join(td, "not_slop.jsonl")
            learning_store.add_entry(path, "buzzwords", BUZZ_TEXT)
            base = slop_score(BUZZ_TEXT)
            exempted = slop_score(BUZZ_TEXT, not_slop_store=path)
            self.assertIn("buzzwords", exempted["signals"]["exempted"])
            self.assertLess(
                exempted["slop_score"], base["slop_score"],
                "exemption must lower the score",
            )
            self.assertEqual(exempted["dimensions"]["buzzword_count"], 0)

    def test_no_store_no_exemptions(self):
        result = slop_score(SLOP_TEXT)
        self.assertEqual(result["signals"]["exempted"], [])
        self.assertGreater(result["dimensions"]["buzzword_count"], 0)


class CliTests(unittest.TestCase):
    SCORER = os.path.join(SCRIPTS, "slop_scorer.py")

    def test_mark_not_slop_and_score(self):
        with tempfile.TemporaryDirectory() as td:
            doc = os.path.join(td, "text.md")
            with open(doc, "w", encoding="utf-8") as f:
                f.write(BUZZ_TEXT)
            store = os.path.join(td, "not_slop.jsonl")
            mark = subprocess.run(
                [sys.executable, self.SCORER, "--mark-not-slop", "buzzwords",
                 "--file", doc, "--store", store, "--note", "genre copy",
                 "--by", "reviewer"],
                capture_output=True, text=True,
            )
            self.assertEqual(mark.returncode, 0, mark.stderr)
            self.assertTrue(os.path.isfile(store))

            score = subprocess.run(
                [sys.executable, self.SCORER, "--file", doc,
                 "--not-slop-store", store, "--json"],
                capture_output=True, text=True,
            )
            self.assertEqual(score.returncode, 0, score.stderr)
            result = json.loads(score.stdout)
            self.assertIn("buzzwords", result["signals"]["exempted"])

    def test_mark_not_slop_requires_file(self):
        mark = subprocess.run(
            [sys.executable, self.SCORER, "--mark-not-slop", "buzzwords"],
            capture_output=True, text=True,
        )
        self.assertNotEqual(mark.returncode, 0)




class LearnInputTests(unittest.TestCase):
    """Issue #120: simple learn input — freitext + optional path is enough."""

    SCORER = os.path.join(SCRIPTS, "slop_scorer.py")
    STORE_SCRIPT = os.path.join(SCRIPTS, "learning_store.py")

    def test_learn_freetext_only_appends_entry(self):
        with tempfile.TemporaryDirectory() as td:
            store = os.path.join(td, "not_slop.jsonl")
            learning_store.learn_entry(store, "false positive on src/foo.rs")
            entries = learning_store.load_store(store)
            self.assertEqual(len(entries), 1)
            self.assertEqual(entries[0]["signal_id"], "reviewed")
            self.assertIn("src/foo.rs", entries[0]["note"])

    def test_learn_empty_note_raises(self):
        with tempfile.TemporaryDirectory() as td:
            with self.assertRaises(ValueError):
                learning_store.learn_entry(os.path.join(td, "s.jsonl"), "  ")

    def test_learn_with_file_creates_exemption(self):
        with tempfile.TemporaryDirectory() as td:
            doc = os.path.join(td, "text.md")
            with open(doc, "w", encoding="utf-8") as f:
                f.write(BUZZ_TEXT)
            learning_store.learn_entry(
                os.path.join(td, "not_slop.jsonl"), "genre copy",
                signal_id="buzzwords", sample_text=BUZZ_TEXT)
            result = slop_score(
                BUZZ_TEXT, not_slop_store=os.path.join(td, "not_slop.jsonl"))
            self.assertIn("buzzwords", result["signals"]["exempted"])

    def test_cli_learn_minimal(self):
        with tempfile.TemporaryDirectory() as td:
            store = os.path.join(td, "not_slop.jsonl")
            run = subprocess.run(
                [sys.executable, self.SCORER, "--learn",
                 "false positive on src/foo.rs", "--store", store],
                capture_output=True, text=True)
            self.assertEqual(run.returncode, 0, run.stderr)
            self.assertTrue(os.path.isfile(store))

    def test_cli_learn_requires_note(self):
        run = subprocess.run(
            [sys.executable, self.SCORER, "--learn"],
            capture_output=True, text=True)
        self.assertNotEqual(run.returncode, 0)

    def test_cli_learn_store_module(self):
        with tempfile.TemporaryDirectory() as td:
            doc = os.path.join(td, "text.md")
            with open(doc, "w", encoding="utf-8") as f:
                f.write(BUZZ_TEXT)
            run = subprocess.run(
                [sys.executable, self.STORE_SCRIPT, "learn", "genre copy",
                 "--file", doc, "--signal", "buzzwords"],
                capture_output=True, text=True)
            self.assertEqual(run.returncode, 0, run.stderr)
            self.assertTrue(os.path.isfile(os.path.join(td, "not_slop.jsonl")))


if __name__ == "__main__":
    unittest.main()
