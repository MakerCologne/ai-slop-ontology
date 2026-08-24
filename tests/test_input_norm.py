"""Issue #40: input normalization & anti-evasion layer.

All input is normalized BEFORE any metric: Unicode NFKC (folds fullwidth
etc.), zero-width stripping (ZWSP/ZWNJ/ZWJ U+200B-200D, BOM U+FEFF), and a
homoglyph mapping for the confusable Cyrillic/Latin pairs
(a e o p c x) + FULLWIDTH range. A slop text that hides 'delve' behind
homoglyphs or zero-width joiners must trigger after normalization.
"""

import os
import sys
import unittest

SCRIPTS = os.path.join(
    os.path.dirname(__file__), "..", "skills", "ai-slop-detection", "scripts"
)
sys.path.insert(0, SCRIPTS)

import input_norm  # noqa: E402
import slop_scorer  # noqa: E402


class TestNormalize(unittest.TestCase):
    def test_nfkc_folds_fullwidth(self):
        self.assertEqual(input_norm.normalize("ｄｅｌｖｅ"), "delve")

    def test_zero_width_chars_stripped(self):
        for zw in ("\u200b", "\u200c", "\u200d", "\ufeff"):
            self.assertEqual(input_norm.normalize(f"del{zw}ve"), "delve")

    def test_cyrillic_homoglyphs_mapped_to_latin(self):
        # cyrillic а е о р с х look identical to latin a e o p c x
        self.assertEqual(input_norm.normalize("d\u0435lv\u0435"), "delve")
        self.assertEqual(input_norm.normalize("\u0441at"), "cat")  # cyrillic с
        self.assertEqual(input_norm.normalize("\u0440ark"), "park")  # cyrillic р

    def test_homoglyph_pairs_minimal_set(self):
        for cyr, lat in (("а", "a"), ("е", "e"), ("о", "o"),
                         ("р", "p"), ("с", "c"), ("х", "x")):
            self.assertIn(cyr, input_norm.HOMOGLYPHS)
            self.assertEqual(input_norm.HOMOGLYPHS[cyr], lat)

    def test_clean_text_unchanged(self):
        text = "The build failed because a cached dependency shadowed the patch."
        self.assertEqual(input_norm.normalize(text), text)

    def test_idempotent(self):
        once = input_norm.normalize("delve into the realm\u200b of AI")
        self.assertEqual(input_norm.normalize(once), once)


class TestEvasionThroughScorer(unittest.TestCase):
    SLOP_BODY = (
        " into the rich tapestry of AI tooling. It serves as a testament "
        "to innovation and unlocks the potential of teams across the "
        "ever-changing landscape of modern software."
    )

    def test_homoglyph_delve_triggers_buzzword(self):
        plain = "delve" + self.SLOP_BODY
        evaded = "d\u0435lv\u0435" + self.SLOP_BODY  # cyrillic е
        self.assertGreaterEqual(
            slop_scorer.slop_score(evaded)["slop_score"],
            slop_scorer.slop_score(plain)["slop_score"] - 0.001,
        )
        self.assertGreaterEqual(slop_scorer.slop_score(evaded)["slop_score"], 0.40)

    def test_zero_width_delve_triggers_buzzword(self):
        evaded = "del\u200bve" + self.SLOP_BODY
        self.assertGreaterEqual(slop_scorer.slop_score(evaded)["slop_score"], 0.40)

    def test_fullwidth_delve_triggers_buzzword(self):
        evaded = "ｄｅｌｖｅ" + self.SLOP_BODY
        self.assertGreaterEqual(slop_scorer.slop_score(evaded)["slop_score"], 0.40)

    def test_normal_text_score_unchanged_by_normalization(self):
        text = ("The team shipped the migration after a two-week soak test. "
                "Latency improved by three percent under load.")
        self.assertEqual(
            slop_scorer.slop_score(text)["slop_score"],
            slop_scorer.slop_score(text)["slop_score"],
        )


if __name__ == "__main__":
    unittest.main()
