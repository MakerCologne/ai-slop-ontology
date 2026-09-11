"""Tests for academic-register signals (issue #114 / BS-I3).

Drei invertierbare Signale: EpistemicMismatch, UnquantifiedScopeClaim,
VagueAttribution. Je Signal 2 Positive + 2 Hard-Negatives (Inversion:
gleiche Aussage MIT Absicherung feuert nicht).
"""

import os
import sys
import unittest

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SCRIPTS = os.path.join(ROOT, "skills", "ai-slop-detection", "scripts")
sys.path.insert(0, SCRIPTS)

from academic_register import (
    ACADEMIC_REGISTER,
    find_academic_register_findings,
)


def ids(text):
    return {f["id"] for f in find_academic_register_findings(text)}


# Padding auf >40 Woerter (MIN_WORDS-Guard), damit die Signale ueberhaupt
# pruefbar sind; Padding selbst enthaelt keine Trigger.
PAD = ("The present work examines retrieval behaviour in synthetic corpora "
       "and reports the experimental setup, the measurement procedure and "
       "the limitations of the study design across all conditions. "
       "Section two introduces the corpus construction and annotation "
       "workflow, while section three discusses threats to validity. ")


class SchemaTests(unittest.TestCase):
    def test_each_signal_has_keep_when_and_examples(self):
        for pid, meta in ACADEMIC_REGISTER.items():
            self.assertIn("keep_when", meta, f"{pid} missing keep_when")
            self.assertIn("example_slop", meta)
            self.assertIn("example_fix", meta)

    def test_detect_only_schema(self):
        for f in find_academic_register_findings(PAD + "The literature suggests this. "):
            self.assertEqual(set(f), {"id", "confidence", "evidence", "keep_when"})

    def test_short_text_guard(self):
        self.assertEqual(find_academic_register_findings("Studies show this."), [])

    def test_clean_academic_text_has_no_findings(self):
        text = PAD + (
            "We analyze 214 papers published between 2018 and 2025. "
            "Prior work reports modest gains (Smith et al., 2020). "
            "Our measurements confirm the trend (n = 42, p < .05)."
        )
        self.assertEqual(find_academic_register_findings(text), [])


class EpistemicMismatchTests(unittest.TestCase):
    POS = PAD + (
        "These results demonstrate that the approach may improve accuracy "
        "across the datasets we reviewed."
    )

    def test_positive(self):
        self.assertIn("EpistemicMismatch", ids(self.POS))
        self.assertIn("EpistemicMismatch", ids(
            PAD + "The ablation proves that the effect might be significant."))

    def test_negative_hedge_only(self):
        # Hedge ohne starkes Verb: korrekt vorsichtiges Paper.
        self.assertNotIn("EpistemicMismatch", ids(
            PAD + "These results suggest that the approach may improve accuracy."))

    def test_negative_strong_verb_with_quantifier(self):
        # Starkes Verb mit n=/Quantifizierung: belegte Staerke.
        self.assertNotIn("EpistemicMismatch", ids(
            PAD + "The ablation demonstrates a 3.2 % gain (n = 42, p < .05)."))


class UnquantifiedScopeClaimTests(unittest.TestCase):
    POS = PAD + "We provide a comprehensive analysis of the field in this report."

    def test_positive(self):
        self.assertIn("UnquantifiedScopeClaim", ids(self.POS))
        self.assertIn("UnquantifiedScopeClaim", ids(
            PAD + "This is an exhaustive survey of existing work on the topic."))

    def test_negative_with_count(self):
        self.assertNotIn("UnquantifiedScopeClaim", ids(
            PAD + "We provide a comprehensive analysis of 214 papers."))

    def test_negative_with_period(self):
        self.assertNotIn("UnquantifiedScopeClaim", ids(
            PAD + "We survey the literature from 2018 to 2025 comprehensively."))


class VagueAttributionTests(unittest.TestCase):
    POS = PAD + "The literature suggests that this method outperforms baselines."

    def test_positive(self):
        self.assertIn("VagueAttribution", ids(self.POS))
        self.assertIn("VagueAttribution", ids(
            PAD + "It is well established that this approach converges quickly."))

    def test_negative_with_numeric_citation(self):
        self.assertNotIn("VagueAttribution", ids(
            PAD + "The literature suggests gains [12], particularly on long inputs."))

    def test_negative_with_author_year(self):
        self.assertNotIn("VagueAttribution", ids(
            PAD + "Studies show consistent improvements (Smith et al., 2020)."))


if __name__ == "__main__":
    unittest.main()
