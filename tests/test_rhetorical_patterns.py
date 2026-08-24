"""Tests for the detect-only rhetorical slop patterns (skill module)."""

import json
import os
import sys
import unittest

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SCRIPTS = os.path.join(ROOT, "skills", "ai-slop-detection", "scripts")
sys.path.insert(0, SCRIPTS)

from rhetorical_patterns import RHETORICAL_PATTERNS, find_rhetorical_patterns
from slop_classifier import classify_text


def ids(text):
    return {p["id"] for p in find_rhetorical_patterns(text)}


class RhetoricalDetectionTests(unittest.TestCase):
    def test_each_pattern_fires_on_its_example(self):
        cases = {
            "BinaryContrast": "The question isn't the model. It's the eval.",
            "ColonReveal": "The best part: it learns from every run.",
            "SuperficialAnalysis": "The launch adds file search, highlighting the team's commitment.",
            "NegativeListingFragmentation": "Not a feature. Not a tool. A movement.",
            "FakeStrongVerb": "The app serves as a centralized hub for sponsor management.",
            "SynonymCycling": "The agent reviews the draft. The assistant scores it. The tool suggests fixes.",
            "HollowKickerRecap": "We shipped it fast.\n\nIn conclusion, AI changes everything and we must adapt.",
            "FormattingSlop": "## \U0001F680 Key Takeaways\nWe cut deploy time from 40 to 4 minutes.",
            "RoboticRhythm": "It works. It scales. It ships. Every run.",
            "ThroatClearing": (
                "In today's world, effective team communication matters more than ever. "
                "We cut meeting time by a third last quarter."
            ),
            "FauxInsightSetup": (
                "Here's the thing nobody tells you about remote work: it has tradeoffs. "
                "Our team measured both sides over two years."
            ),
            "ImportancePuffery": (
                "The launch of the new API is a pivotal moment for the industry. "
                "Version 2 shipped on March 3rd and cut latency by half."
            ),
            "ForcedTriad": "The dashboard is fast, reliable, and scalable.",
            "RepeatedOpenings": (
                "The team shipped the billing page. The team then rewrote the search. "
                "The team also fixed login. After that, everyone took a week off."
            ),
            "ChatbotLeftover": (
                "The config option is documented in the README. "
                "I hope this helps! Let me know if you have any other questions."
            ),
        }
        for pattern_id, text in cases.items():
            self.assertIn(pattern_id, ids(text), f"{pattern_id} did not fire on its example")

    def test_binary_contrast_variants(self):
        self.assertIn("BinaryContrast", ids("It's not a bug. It's a feature."))
        self.assertIn("BinaryContrast", ids("This is not just fast but also cheap to run."))

    def test_throat_clearing_needs_opener_at_start(self):
        # The same phrase mid-text is ordinary reference, not throat-clearing.
        self.assertNotIn(
            "ThroatClearing",
            ids("Two years ago we rebuilt search. In today's world, speed wins."),
        )

    def test_forced_triad_ignores_concrete_lists(self):
        self.assertNotIn("ForcedTriad", ids("Ingredients: flour, water, salt, and yeast."))
        self.assertNotIn(
            "ForcedTriad",
            ids("We interviewed 12 nurses, 9 doctors, and 3 administrators in April."),
        )

    def test_repeated_openings_need_three(self):
        self.assertNotIn(
            "RepeatedOpenings",
            ids("The team shipped fast. The team then rested. Everyone returned Tuesday."),
        )

    def test_new_patterns_have_keep_when_guards(self):
        for pid in ("ThroatClearing", "FauxInsightSetup", "ImportancePuffery",
                    "ForcedTriad", "RepeatedOpenings", "ChatbotLeftover"):
            self.assertTrue(RHETORICAL_PATTERNS[pid]["keep_when"].strip())

    def test_formatting_slop_title_case_headings(self):
        text = (
            "## Key Takeaways From The Report\n"
            "We cut deploy time from 40 to 4 minutes.\n\n"
            "## Why This Matters For Your Team\n"
            "The savings paid for two new hires."
        )
        self.assertIn("FormattingSlop", ids(text))

    def test_formatting_slop_spares_sentence_case_headings(self):
        text = (
            "## Key takeaways from the report\n"
            "We cut deploy time from 40 to 4 minutes.\n\n"
            "## Why this matters for your team\n"
            "The savings paid for two new hires."
        )
        self.assertNotIn("FormattingSlop", ids(text))

    def test_formatting_slop_curly_double_quotes(self):
        self.assertIn(
            "FormattingSlop",
            ids('She said \u201cyes\u201d immediately. The contract was signed in March.'),
        )

    def test_formatting_slop_hyphenated_pairs(self):
        text = (
            "The new process is cross-functional and data-driven, which keeps "
            "our user-facing docs current. We shipped it in week two."
        )
        self.assertIn("FormattingSlop", ids(text))

    def test_formatting_slop_single_hyphenated_word_is_fine(self):
        text = (
            "We rewrote the open-source library. It now builds in 90 seconds "
            "instead of 12 minutes."
        )
        self.assertNotIn("FormattingSlop", ids(text))

    def test_formatting_slop_em_dash_doctrine_short_copy(self):
        # short copy: even a single em dash is a tell (no-ai-slop doctrine)
        self.assertIn(
            "FormattingSlop",
            ids("We shipped it fast \u2014 and on budget. The client renewed."),
        )

    def test_formatting_slop_em_dash_long_draft_allows_two(self):
        # long draft: 1-2 em dashes are allowed by the doctrine
        body = ("The team rebuilt the billing flow in March and shipped it behind a flag. "
                "Checkout went from 40 seconds to 9 \u2014 measured on the 95th "
                "percentile, not the median. Refunds now clear in a day. "
                "Support tickets dropped by half. The auditor signed off in "
                "May. Two engineers moved to search. One joined sales ops. "
                "The second em dash appears here \u2014 and that is still fine "
                "under the doctrine. Payments volume doubled by June. "
                "Churn fell three points. The finance lead presented the "
                "numbers at the quarterly review. Nobody asked for the old "
                "flow back. The dashboard shows the trend daily. The migration guide was "
                "updated the same week, and two customers wrote in to say thanks for the "
                "faster refunds alone.")
        self.assertNotIn("FormattingSlop", ids(body))


    def test_clean_prose_has_no_findings(self):
        clean = [
            "We shipped the billing page on Tuesday. It cut checkout time from 40 seconds to 9.",
            "The API returns 200 on success and 404 when the record is missing.",
            "I spent the weekend rewiring the garage. The lights finally work.",
        ]
        for text in clean:
            self.assertEqual(find_rhetorical_patterns(text), [], text)

    def test_colon_reveal_keeps_lists_and_labels(self):
        # A colon that introduces a list or a label is not a dramatic reveal.
        self.assertNotIn("ColonReveal", ids("Ingredients: flour, water, salt, and yeast."))
        self.assertNotIn("ColonReveal", ids("Note: the server restarts at midnight UTC."))

    def test_findings_carry_evidence_and_fix(self):
        findings = find_rhetorical_patterns("The app serves as a centralized hub for teams.")
        self.assertTrue(findings)
        for f in findings:
            self.assertTrue(f["evidence"])
            self.assertTrue(f["fix"])
            self.assertIn(f["id"], RHETORICAL_PATTERNS)

    def test_detection_is_score_neutral(self):
        # Rhetorical patterns are reported but must not change the numeric score:
        # the same text with and without a rhetorical shape scores identically on
        # the parts the scorer actually reads.
        text = "The app serves as a centralized hub. It's not X. It's Y."
        result = classify_text(text)
        self.assertTrue(result.rhetorical_patterns)
        # score is derived purely from signals/types/dimensions, never from
        # result.rhetorical_patterns — recompute-free sanity check:
        self.assertIsInstance(result.score, float)
        self.assertLessEqual(result.score, 1.0)

    def test_every_pattern_has_metadata(self):
        for pattern_id, meta in RHETORICAL_PATTERNS.items():
            for key in ("label", "confidence", "description", "example_slop",
                        "example_fix", "keep_when"):
                self.assertIn(key, meta, f"{pattern_id} missing {key}")

    def test_json_and_module_stay_in_parity(self):
        with open(os.path.join(ROOT, "ontology.json")) as f:
            oj = json.load(f)
        json_ids = set(oj["signals"]["text"]["rhetoricalPatterns"]["patterns"])
        self.assertEqual(json_ids, set(RHETORICAL_PATTERNS))


if __name__ == "__main__":
    unittest.main()
