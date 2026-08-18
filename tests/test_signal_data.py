"""
Signal-database integrity and cross-engine data parity.

Covers the findings of review 2026-08 §1.2/§1.3: placeholder entries that
could never match, and signal data that had silently drifted between
ontology.json and the self-contained agent skill.
"""

import json
import os
import subprocess
import sys
import unittest

ROOT = os.path.join(os.path.dirname(__file__), "..")
sys.path.insert(0, os.path.join(ROOT, "src"))
sys.path.insert(0, os.path.join(ROOT, "skills", "ai-slop-detection", "scripts"))
sys.path.insert(0, os.path.join(ROOT, "scripts"))

import slop_scorer as skill_scorer
from scorer import find_term_matches, _term_pattern


def ontology():
    with open(os.path.join(ROOT, "ontology.json"), encoding="utf-8") as f:
        return json.load(f)


class TestPlaceholderExpansion(unittest.TestCase):
    """[X] is one word, [N] is a number — before the fix these never matched."""

    CASES = [
        ("here are [N] ways", "here are 5 ways to save money", True),
        ("here are [N] ways", "here are ways to save money", False),
        ("in the age of [X]", "in the age of automation everything changed", True),
        ("a sea of [X]", "we faced a sea of options", True),
        ("the future of [X] is bright", "the future of work is bright", True),
        ("top [N] reasons", "top 10 reasons to switch", True),
    ]

    def test_templates_match_real_text(self):
        for term, text, expected in self.CASES:
            hit = bool(find_term_matches(text, [term]))
            self.assertEqual(hit, expected, f"{term!r} vs {text!r}")

    def test_both_engines_agree_on_templates(self):
        for term, text, _ in self.CASES:
            self.assertEqual(
                find_term_matches(text, [term]),
                skill_scorer.find_term_matches(text, [term]),
                f"engines disagree on template {term!r}")

    def test_placeholder_stays_within_one_word(self):
        # [X] must not swallow the rest of the sentence
        self.assertEqual(
            find_term_matches("in the age of ai everything changed",
                              ["in the age of [X]"]),
            {"in the age of [x]": 1})

    def test_empty_term_never_matches(self):
        self.assertEqual(find_term_matches("any text at all", [""]), {})
        self.assertEqual(_term_pattern(""), r"(?!)")

    def test_no_unexpanded_placeholders_reach_the_matcher(self):
        """Every placeholder in the database uses a form the matcher knows."""
        text = ontology()["signals"]["text"]
        entries = [w for t in text["buzzwords"]["tiers"].values() for w in t["words"]]
        entries += [p for c in text["phrases"]["categories"].values() for p in c["items"]]
        entries += [p for t in text.get("typePatterns", {}).get("types", {}).values()
                    for p in t.get("patterns", [])]
        for e in entries:
            for token in set(__import__("re").findall(r"\[[^\]]*\]", e)):
                self.assertIn(token.lower(), ("[x]", "[n]"),
                              f"unknown placeholder {token} in {e!r}")


class TestSignalDatabaseHygiene(unittest.TestCase):
    def test_no_duplicate_terms_within_a_tier_or_category(self):
        text = ontology()["signals"]["text"]
        for name, tier in text["buzzwords"]["tiers"].items():
            words = [w.lower() for w in tier["words"]]
            self.assertEqual(len(words), len(set(words)), f"duplicate in {name}")
        for name, cat in text["phrases"]["categories"].items():
            items = [p.lower() for p in cat["items"]]
            self.assertEqual(len(items), len(set(items)), f"duplicate in {name}")

    def test_no_term_appears_in_two_buzzword_tiers(self):
        seen = {}
        for name, tier in ontology()["signals"]["text"]["buzzwords"]["tiers"].items():
            for w in tier["words"]:
                self.assertNotIn(w.lower(), seen,
                                 f"{w!r} in {name} and {seen.get(w.lower())}")
                seen[w.lower()] = name

    def test_multilingual_entries_are_whitespace_sane(self):
        """'aufAugenhöhe' was a lost space and could never match."""
        import re
        for lang, data in ontology()["signals"]["multilingual"].items():
            if not (isinstance(data, dict) and "buzzwords" in data):
                continue
            for w in data["buzzwords"]:
                self.assertIsNone(
                    re.search(r"[a-zäöüß][A-ZÄÖÜ]", w),
                    f"{lang}: {w!r} looks like it lost a space")


class TestEngineDataParity(unittest.TestCase):
    """The skill's inlined copies must equal what ontology.json generates."""

    def test_sync_script_reports_no_drift(self):
        import sync_skill_signals
        self.assertEqual(sync_skill_signals.main(["--check"]), 0,
                         "run python3 scripts/sync_skill_signals.py")

    def test_buzzword_tier_assignment_matches(self):
        j = {w.lower(): name for name, t in
             ontology()["signals"]["text"]["buzzwords"]["tiers"].items()
             for w in t["words"]}
        s = {w.lower(): name for name, t in skill_scorer.BUZZWORD_TIERS.items()
             for w in t["words"]}
        self.assertEqual(j, s)

    def test_phrase_category_assignment_matches(self):
        cats = ontology()["signals"]["text"]["phrases"]["categories"]
        j = {name: sorted(p.lower() for p in c["items"])
             for name, c in cats.items()}
        s = {name: sorted(p.lower() for p in c["phrases"])
             for name, c in skill_scorer.PHRASE_CATEGORIES.items()}
        # authority_claims is scored as its own dimension in the skill
        s["authority_claims"] = sorted(p.lower()
                                       for p in skill_scorer.AUTHORITY_PATTERNS)
        self.assertEqual(j, s)

    def test_confidences_match(self):
        text = ontology()["signals"]["text"]
        self.assertEqual(
            {k: v["confidence"] for k, v in text["buzzwords"]["tiers"].items()},
            {k: v["confidence"] for k, v in skill_scorer.BUZZWORD_TIERS.items()})
        for name, cat in text["phrases"]["categories"].items():
            if name == "authority_claims":
                continue
            self.assertEqual(cat["confidence"],
                             skill_scorer.PHRASE_CATEGORIES[name]["confidence"],
                             f"confidence drift in {name}")

    def test_multilingual_markers_match(self):
        j = {lang: sorted(w.lower() for w in d["buzzwords"])
             for lang, d in ontology()["signals"]["multilingual"].items()
             if isinstance(d, dict) and "buzzwords" in d}
        s = {lang: sorted(w.lower() for w in words)
             for lang, words in skill_scorer.MULTILINGUAL_BUZZWORDS.items()}
        self.assertEqual(j, s)


if __name__ == "__main__":
    unittest.main()
