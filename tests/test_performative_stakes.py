"""Issue #115: performative_voice + manufactured_stakes phrase categories
(ZeroSlop adaptation: 'performed voice' / 'manufactured stakes').

Detect-only via cumulative rule (>= 2 hits per category), covered by
keep_when hard-negative guards (fp_guards.mask_performative_stakes):

  (a) performative_voice phrases do not count when a first-person
      experience anchor sits within +-120 chars ("when I ...",
      "in my experience", "I lost/spent/learned/tried/failed")
      — lived voice, not performed voice.
  (b) manufactured_stakes phrases do not count when a concrete date/
      deadline/quantity follows within 120 chars ("deadline 15 October",
      "by Friday", "30%") — real urgency, not manufactured.

DoD: per category 4 positive + 4 hard-negative fixtures plus guard
end-to-end and cumulative-rule checks. Occurrence counts are asserted
through slop_scorer.phrase_category_score / find_term_matches on
guard-masked text.
"""

import os
import sys
import unittest

SCRIPTS = os.path.join(
    os.path.dirname(__file__), "..", "skills", "ai-slop-detection", "scripts"
)
sys.path.insert(0, SCRIPTS)

import fp_guards  # noqa: E402
import slop_scorer  # noqa: E402

FILLER = (
    " The team reviewed the draft twice and checked every number "
    "against the original spreadsheet before sending anything out. "
)


def _categories(text: str) -> dict:
    # Mirror the engine pipeline: quote exemption (#23) applies to the
    # full text before phrase matching (score path calls
    # phrase_category_score on signal_text).
    signal_text = fp_guards.strip_quotes(text)
    return slop_scorer.phrase_category_score(signal_text)


def _hits(text: str, category: str) -> list:
    return _categories(text).get(category, [])


class TestPerformativeVoice(unittest.TestCase):
    """#115 (a): Persoenlichkeits-Theater als Formel."""

    PV_POSITIVE = (
        "Here's the thing nobody tells you about productivity. "
        "I'm going to be honest with you: the systems all work. "
        "Let me be brutally honest about morning routines. "
        "I don't say this lightly."
    )
    PV_NEGATIVE = (
        "Nobody tells you this, and when I started out I lost three "
        "months to the same mistake. In my experience the fix is boring: "
        "I tried the fancy setup and failed, and I learned more from the "
        "plain checklist than from any framework."
    )

    def test_positive_category_fires(self):
        hits = _hits(self.PV_POSITIVE, "performative_voice")
        self.assertGreaterEqual(len(hits), 2,
                                "cumulative slop text must fire the category")

    def test_positive_phrase_coverage(self):
        hits = set(_hits(self.PV_POSITIVE, "performative_voice"))
        for phrase in ("here's the thing nobody tells you",
                       "let me be brutally honest"):
            self.assertIn(phrase, hits)

    def test_positive_short_variant(self):
        text = ("Unpopular opinion, but the roadmap is theatre. "
                "Call me old-fashioned, but shipping beats planning." +
                FILLER)
        hits = _hits(text, "performative_voice")
        self.assertGreaterEqual(len(hits), 2)

    def test_positive_nobody_tells_you(self):
        text = ("Nobody tells you that the config file is the real "
                "documentation. Nobody tells you that the on-call rota "
                "is the actual architecture diagram." + FILLER)
        masked = fp_guards.mask_performative_stakes(text.lower())
        counts = slop_scorer.find_term_matches(masked, ["nobody tells you"])
        self.assertGreaterEqual(counts.get("nobody tells you", 0), 2)
        # engine-level: category listed with the distinct term
        self.assertIn("nobody tells you",
                      _hits(text, "performative_voice"))

    def test_negative_experience_anchor_masks(self):
        hits = _hits(self.PV_NEGATIVE, "performative_voice")
        self.assertEqual(hits, [],
                         "first-person experience anchors must mask the "
                         "phrases (lived voice, keep_when)")

    def test_negative_anchor_window_is_bounded(self):
        # Anchor outside the +-120 char window must NOT mask.
        far = ("Nobody tells you this. " + "padding " * 40 +
               "Later, unrelated, when I was young, things were different.")
        hits = _hits(far, "performative_voice")
        self.assertEqual(len(hits), 1)

    def test_negative_single_hit_no_category_score(self):
        # One unmasked phrase is still reported by the engine but must
        # stay below the cumulative threshold in effective_phrase_count.
        text = ("I'm going to be honest with you: the benchmark ran "
                "clean." + FILLER)
        matches = _categories(text)
        self.assertLessEqual(len(matches.get("performative_voice", [])), 1)
        counted = fp_guards.effective_phrase_count(matches)
        self.assertEqual(counted, 0,
                         "single hit must not count (cumulative rule #23)")

    def test_negative_long_quote_exempt(self):
        # Quote exemption (#23): quoted spans > 40 chars are evidence,
        # not prose — a style guide reproducing a full slop sentence
        # must not inherit its signals.
        quoted = ("here's the thing nobody tells you, and let me be "
                  "brutally honest about what follows from that")
        text = ('The style guide bans the full opening "' + quoted +
                '" outright in marketing copy.' + FILLER)
        hits = _hits(text, "performative_voice")
        self.assertEqual(hits, [],
                         "long quoted examples are evidence, not prose (#23)")


class TestManufacturedStakes(unittest.TestCase):
    """#115 (b): Dringlichkeit ohne Sache."""

    MS_POSITIVE = (
        "In today's fast-paced market, the stakes have never been "
        "higher. Now more than ever, teams stand at a critical juncture. "
        "Time is running out — don't get left behind before it's too "
        "late."
    )

    def test_positive_category_fires(self):
        hits = _hits(self.MS_POSITIVE, "manufactured_stakes")
        self.assertGreaterEqual(len(hits), 2)

    def test_positive_phrase_coverage(self):
        hits = set(_hits(self.MS_POSITIVE, "manufactured_stakes"))
        for phrase in ("in today's fast-paced",
                       "the stakes have never been higher",
                       "before it's too late"):
            self.assertIn(phrase, hits)

    def test_positive_juncture(self):
        text = ("The industry sits at a critical juncture. Now more "
                "than ever, alignment matters." + FILLER)
        hits = _hits(text, "manufactured_stakes")
        self.assertGreaterEqual(len(hits), 2)

    def test_positive_cta(self):
        text = ("Don't get left behind. Time is running out for "
                "laggard adopters." + FILLER)
        hits = _hits(text, "manufactured_stakes")
        self.assertGreaterEqual(len(hits), 2)

    def test_negative_concrete_deadline_masks(self):
        text = ("Time is running out: the migration deadline is 15 "
                "October, and the freeze starts before it's too late "
                "to roll back — by Friday the window closes." + FILLER)
        hits = _hits(text, "manufactured_stakes")
        self.assertEqual(hits, [],
                         "concrete dates/deadlines in the follow window "
                         "must mask the phrases (real urgency, keep_when)")

    def test_negative_quantity_masks(self):
        text = ("Now more than ever, cost discipline matters: the audit "
                "found 30% waste in the staging cluster, and the stakes "
                "have never been higher for the Q3 review — cuts of "
                "12 EUR per seat are on the table." + FILLER)
        hits = _hits(text, "manufactured_stakes")
        self.assertEqual(hits, [])

    def test_negative_facts_before_phrase_not_masked(self):
        # keep_when is directional: the concrete fact must FOLLOW the
        # phrase (manufactured stakes fake the future), a fact stated
        # earlier does not absolve a later bare reprise.
        text = ("The audit found 30% waste last quarter. Now more than "
                "ever, the stakes have never been higher." + FILLER)
        hits = _hits(text, "manufactured_stakes")
        self.assertGreaterEqual(len(hits), 2)

    def test_negative_single_hit_no_category_score(self):
        text = ("At a critical juncture, the committee deferred the "
                "vote." + FILLER)
        matches = _categories(text)
        self.assertLessEqual(len(matches.get("manufactured_stakes", [])), 1)
        self.assertEqual(fp_guards.effective_phrase_count(matches), 0)


class TestGuardsDirect(unittest.TestCase):
    """fp_guards.mask_performative_stakes in isolation."""

    def test_mask_preserves_length_and_outside_text(self):
        text = ("nobody tells you. when i tried it i failed. "
                "unrelated tail sentence stays intact.")
        masked = fp_guards.mask_performative_stakes(text)
        self.assertEqual(len(masked), len(text))
        self.assertIn("unrelated tail sentence stays intact.", masked)
        self.assertNotIn("nobody tells you", masked)

    def test_no_mask_without_anchor(self):
        text = "nobody tells you anything about the cache layer."
        masked = fp_guards.mask_performative_stakes(text)
        self.assertIn("nobody tells you", masked)

    def test_ms_mask_only_when_fact_follows(self):
        text = "time is running out for the pilot."
        self.assertIn("time is running out",
                      fp_guards.mask_performative_stakes(text))
        text2 = "time is running out: 48 hours remain."
        self.assertNotIn("time is running out",
                         fp_guards.mask_performative_stakes(text2))

    def test_categories_do_not_leak_into_each_other(self):
        # performative_voice anchor must not mask manufactured_stakes
        # phrases and vice versa.
        text = ("When I started out I lost money. In today's fast-paced "
                "world the stakes have never been higher." + FILLER)
        cats = _categories(text)
        self.assertEqual(cats.get("performative_voice", []), [])
        self.assertGreaterEqual(len(cats.get("manufactured_stakes", [])), 2)


if __name__ == "__main__":
    unittest.main()
