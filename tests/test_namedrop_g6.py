"""G6 NameDropList (issue #249 / unslop #2) — detect-only micro signal."""

import os
import sys
import unittest

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SCRIPTS = os.path.join(ROOT, "skills", "ai-slop-detection", "scripts")
sys.path.insert(0, SCRIPTS)

from micro_patterns import find_micro_patterns


def ids(text):
    return {p["id"] for p in find_micro_patterns(text)}


class NameDropListTests(unittest.TestCase):
    # --- positives ---

    def test_positive_featured_in(self):
        self.assertIn("NameDropList", ids("As featured in TechCrunch, Forbes, and Wired."))

    def test_positive_as_seen_on(self):
        self.assertIn("NameDropList", ids("As seen on Product Hunt, Hacker News, and Reddit."))

    def test_positive_bare_enumeration(self):
        self.assertIn("NameDropList", ids("Coverage in TechCrunch, Wired, Forbes, and The Verge."))

    def test_positive_the_verge_multiword(self):
        self.assertIn(
            "NameDropList",
            ids("Featured in TechCrunch, Forbes, and The Verge this week."),
        )

    # --- negatives (guards) ---

    def test_negative_comparison_sentence(self):
        self.assertNotIn(
            "NameDropList",
            ids("We compared React, Vue, Angular, and Svelte in our benchmark."),
        )

    def test_negative_interview_claim(self):
        self.assertNotIn(
            "NameDropList",
            ids("The team interviewed the founders of Acme, Beeline, and Cordata."),
        )

    def test_negative_reference_bullet_list(self):
        self.assertNotIn(
            "NameDropList",
            ids("- TechCrunch\n- Forbes\n- Wired\n- The Verge"),
        )

    def test_negative_real_content_around_names(self):
        self.assertNotIn(
            "NameDropList",
            ids("After the launch, TechCrunch, Forbes, and The Verge each published "
                "independent reviews with detailed benchmarks and interviews."),
        )

    def test_negative_two_items_only(self):
        self.assertNotIn(
            "NameDropList",
            ids("Featured in TechCrunch and Wired."),
        )

    def test_negative_numbered_reference_list(self):
        self.assertNotIn(
            "NameDropList",
            ids("1. TechCrunch, 2. Forbes, 3. Wired"),
        )


if __name__ == "__main__":
    unittest.main()
