"""Issue #249/G8 (BriefLeak): briefing/instruction register leaking into
the artefact ("as per your request", "per your request", "as requested").

Concept-mapped into meta_commentary (not a new signal) per deep-dive #39 G8:
the corpus contains no briefing texts, so a dedicated signal has no
calibration base — a phrase-list extension under the existing
meta_commentary category is the honest scope.

DoD: per phrase 2 positives; hard negatives = legitimate request references
that quote the request itself in quotes, and clean prose that merely uses
"requested" as a normal verb.
"""

import os
import sys
import unittest

SCRIPTS = os.path.join(
    os.path.dirname(__file__), "..", "skills", "ai-slop-detection", "scripts"
)
sys.path.insert(0, SCRIPTS)

import slop_scorer  # noqa: E402


def occ(text, term):
    return slop_scorer.find_term_matches(text.lower(), [term]).get(term, 0)


class BriefLeakG8Tests(unittest.TestCase):
    def test_as_per_your_request_hits(self):
        t = "As per your request, I have summarized the findings below."
        self.assertGreaterEqual(occ(t.lower(), "as per your request"), 1)

    def test_per_your_request_hits(self):
        t = "Per your request, the document was shortened to two pages."
        self.assertGreaterEqual(occ(t.lower(), "per your request"), 1)

    def test_as_requested_hits(self):
        t = "As requested, here is the revised timeline for the rollout."
        self.assertGreaterEqual(occ(t.lower(), "as requested"), 1)

    def test_as_requested_prefix_of_longer_no_false_extra(self):
        # "as requested" must not double-fire with meta framing beyond count 1
        t = "As requested, the changes were applied."
        self.assertEqual(occ(t.lower(), "as requested"), 1)

    def test_quoted_request_reference_is_still_a_leak_but_single(self):
        # Quoting the request does not make the briefing tell disappear,
        # but it must count exactly once (no substring double counts).
        t = 'As requested: "please shorten section 2" has been applied.'
        self.assertEqual(occ(t.lower(), "as requested"), 1)

    def test_clean_normal_verb_usage_no_hit(self):
        t = "The team requested more time for testing, and we agreed."
        self.assertEqual(occ(t.lower(), "as requested"), 0)
        self.assertEqual(occ(t.lower(), "as per your request"), 0)

    def test_category_registered_in_ontology_mirror(self):
        import json

        ont = json.load(
            open(
                os.path.join(
                    os.path.dirname(__file__), "..", "ontology.json"
                )
            )
        )
        items = ont["signals"]["text"]["phrases"]["categories"][
            "meta_commentary"
        ]["items"]
        for p in ("as per your request", "per your request", "as requested"):
            self.assertIn(p, items)

    def test_scorer_phrases_registered(self):
        phrases = slop_scorer.PHRASE_CATEGORIES["meta_commentary"]["phrases"]
        for p in ("as per your request", "per your request", "as requested"):
            self.assertIn(p, phrases)


if __name__ == "__main__":
    unittest.main()
