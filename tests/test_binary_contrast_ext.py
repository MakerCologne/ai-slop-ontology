"""Issue #26: BinaryContrast extension — the missing variants from
deep/01-stop-slop.md §2.5 (structures.md, 11 binary-contrast variants).

Verified against the existing _BINARY_CONTRAST regexes before writing:
"It's not X, it's Y" is ALREADY covered by the first pattern
("It's not a bug, it's a feature." fires). Missing:
  - "X isn't just Y — it's Z"
  - "No longer X, now Y"
  - "Gone are the days of X, replaced by Y"
"""

import os
import sys
import unittest

SCRIPTS = os.path.join(
    os.path.dirname(__file__), "..", "skills", "ai-slop-detection", "scripts"
)
sys.path.insert(0, SCRIPTS)

from rhetorical_patterns import find_rhetorical_patterns  # noqa: E402


def ids(text):
    return {p["id"] for p in find_rhetorical_patterns(text)}


class TestBinaryContrastVariants(unittest.TestCase):
    def test_already_covered_comma_variant_still_fires(self):
        # sanity: pre-existing coverage, must not regress
        self.assertIn("BinaryContrast", ids("It's not a bug, it's a feature."))

    def test_isnt_just_em_dash_variant(self):
        self.assertIn(
            "BinaryContrast",
            ids("This isn't just a tool — it's a movement."),
        )

    def test_isnt_just_hyphen_variant(self):
        self.assertIn(
            "BinaryContrast",
            ids("The model isn't just faster - it's cheaper to run."),
        )

    def test_no_longer_now_variant(self):
        self.assertIn(
            "BinaryContrast",
            ids("The product is no longer a prototype, now it is a platform."),
        )

    def test_gone_are_the_days_variant(self):
        self.assertIn(
            "BinaryContrast",
            ids("Gone are the days of manual deploys, replaced by fully "
               "automated pipelines."),
        )

    def test_plain_statement_does_not_fire(self):
        self.assertNotIn(
            "BinaryContrast",
            ids("The deploy takes four minutes and needs one approval."),
        )

    def test_no_longer_without_contrast_does_not_fire(self):
        self.assertNotIn(
            "BinaryContrast",
            ids("This endpoint is no longer available as of March 3rd."),
        )


if __name__ == "__main__":
    unittest.main()
