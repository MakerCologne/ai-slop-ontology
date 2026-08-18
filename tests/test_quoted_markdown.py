"""
Documents that quote slop must not be scored as slop (review 2026-08 §2.4).

The repository's own README and canonical document scored 0.90–0.99 because
their tables, code fences and example lists are full of marker phrases.
"""

import json
import os
import subprocess
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "src"))

from slopkit._markdown import looks_like_markdown, strip_quoted
from classifier import SlopClassifier


class TestStripping(unittest.TestCase):
    def test_fenced_code_is_removed(self):
        text = "Real prose here.\n```\ndelve into the rich tapestry\n```\nMore prose."
        out = strip_quoted(text)
        self.assertNotIn("tapestry", out)
        self.assertIn("Real prose here.", out)
        self.assertIn("More prose.", out)

    def test_blockquotes_and_tables_are_removed(self):
        text = "Intro.\n> delve into the realm\n| a | rich tapestry |\nOutro."
        out = strip_quoted(text)
        self.assertNotIn("realm", out)
        self.assertNotIn("tapestry", out)

    def test_inline_code_is_removed(self):
        self.assertNotIn("tapestry", strip_quoted("The term `rich tapestry` is a marker."))

    def test_example_enumerations_are_removed(self):
        text = "Buzzwords: *delve, realm, tapestry, leverage, synergy*"
        self.assertNotIn("tapestry", strip_quoted(text))

    def test_emphasis_without_a_list_is_kept(self):
        """Heavy formatting is itself a signal — do not blind the detector."""
        text = "This is **absolutely transformative** for the tapestry."
        self.assertIn("transformative", strip_quoted(text))
        self.assertIn("tapestry", strip_quoted(text))

    def test_line_structure_is_preserved(self):
        text = "One.\n```\nx\n```\nTwo."
        self.assertEqual(len(strip_quoted(text).splitlines()), len(text.splitlines()))

    def test_looks_like_markdown(self):
        self.assertTrue(looks_like_markdown("a/b/README.md"))
        self.assertFalse(looks_like_markdown("app.py"))


class TestRepositoryDocuments(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.clf = SlopClassifier(str(ROOT / "ontology.json"))

    def score(self, name, strip=True):
        text = (ROOT / name).read_text(encoding="utf-8")
        return self.clf.classify_text(strip_quoted(text) if strip else text).overall_slop_score

    def test_readme_is_clean_once_quotations_are_ignored(self):
        for doc in ("README.md", "README.de.md", "ONTOLOGY.md"):
            self.assertGreater(self.score(doc, strip=False), 0.7, doc)
            self.assertLess(self.score(doc), 0.4, f"{doc} still reads as slop")

    def test_detection_is_not_weakened_by_stripping(self):
        corpus = (ROOT / "eval" / "corpus.jsonl").read_text(encoding="utf-8")
        items = [json.loads(l) for l in corpus.splitlines() if l.strip()]
        false_positives = [
            i["id"] for i in items if i["label"] != "slop"
            and self.clf.classify_text(strip_quoted(i["text"])).overall_slop_score >= 0.4]
        self.assertEqual(false_positives, [])
        caught = sum(1 for i in items if i["label"] == "slop"
                     and self.clf.classify_text(strip_quoted(i["text"])).overall_slop_score >= 0.4)
        self.assertGreaterEqual(caught, 27)


class TestCli(unittest.TestCase):
    def run_cli(self, *args):
        return subprocess.run([sys.executable, "-m", "slopkit", *args],
                              cwd=ROOT, capture_output=True, text=True)

    def test_markdown_files_are_stripped_by_default(self):
        r = self.run_cli("score", "--file", "README.md", "--json")
        self.assertEqual(r.returncode, 0, r.stderr)
        payload = json.loads(r.stdout)
        self.assertTrue(payload["quoted_markdown_stripped"])
        self.assertLess(payload["slop_score"], 0.4)

    def test_verbatim_mode_still_available(self):
        r = self.run_cli("score", "--file", "README.md", "--no-strip-quotes", "--json")
        payload = json.loads(r.stdout)
        self.assertFalse(payload["quoted_markdown_stripped"])
        self.assertGreater(payload["slop_score"], 0.7)

    def test_literal_text_is_not_stripped_unless_asked(self):
        r = self.run_cli("score", "delve into the rich tapestry of the realm", "--json")
        self.assertFalse(json.loads(r.stdout)["quoted_markdown_stripped"])


if __name__ == "__main__":
    unittest.main()
