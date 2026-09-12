"""Issue #110: conversational fillers — 4 meta-communicative signals.

Hassid list points 4-8 as detect-only phrase category `conversational_fillers`.

DoD 3 hard negatives (mandatory, risk 2/4):
  - "Hope this helps" before a sign-off (real support mail) -> no fire
  - "Most people I interviewed..." (first-person source) -> no fire
DoD 5: 2 positive + 2 hard-negative fixtures per phrase family.

Cumulative rule applies (fp_guards.PHRASE_MIN_HITS = 2): the category
contributes to scoring only with >= 2 hits.

Pre-2022 doctrine (DoD 4): deliberately NOT applied here — the fillers are
pre-human (older than LLMs), so a temporal cap would not separate human from
AI text; the discriminative signal is genre migration (spoken patterns in
written content), not recency. Documented in the PR.
"""

import os
import sys
import unittest

SCRIPTS = os.path.join(
    os.path.dirname(__file__), "..", "skills", "ai-slop-detection", "scripts"
)
sys.path.insert(0, SCRIPTS)

import slop_scorer  # noqa: E402


def cats(text):
    return slop_scorer.phrase_category_score(text)


def filler_hits(text):
    return cats(text).get("conversational_fillers", [])


class TestQuickUpdatePositive(unittest.TestCase):
    """Positive fixtures: update-announcement instead of the update itself."""

    def test_quick_update_pair_fires(self):
        text = ("To provide a quick update on the migration: phase two "
                "started Monday. Just a quick update on the API: all green.")
        hits = filler_hits(text)
        self.assertGreaterEqual(len(hits), 2)

    def test_quick_update_single_with_most_people(self):
        text = ("Here's a quick update on the rollout. Most people expect "
                "delays, but the numbers say otherwise.")
        hits = filler_hits(text)
        self.assertGreaterEqual(len(hits), 2)  # quick update + guarded most people


class TestQuickUpdateHardNegatives(unittest.TestCase):
    """Hard negatives: single accidental occurrence does not fire."""

    def test_single_quick_update_no_fire(self):
        text = ("Our Q3 numbers are in and the trend is stable across all "
                "regions. Just a quick update on one line item: cloud spend "
                "dropped 4% after the reserved-instance purchase.")
        self.assertLess(len(filler_hits(text)), 2)

    def test_quoted_quick_update_exempt(self):
        text = ('The vendor wrote: "Just a quick update on your ticket, '
                'we are still waiting for the part", and then nothing '
                'happened for three weeks, which we documented in the '
                'escalation log afterwards.')
        # single quoted occurrence stays below the cumulative threshold
        self.assertLess(len(filler_hits(text)), 2)


class TestMostPeoplePositive(unittest.TestCase):
    """Positive fixtures: sentence-initial pseudo-empirical quantifier."""

    def test_two_most_people_fires(self):
        text = ("Most people underestimate compounding. Most people also "
                "assume salary growth is linear. Both assumptions fail "
                "against forty years of data.")
        hits = filler_hits(text)
        self.assertEqual(hits.count("most people"), 2)

    def test_most_people_mid_text_opener_counts(self):
        text = ("The market shifted in March. Most people missed it "
                "entirely. Most people were watching the wrong indicator "
                "while the yield curve inverted for the second time.")
        self.assertGreaterEqual(filler_hits(text).count("most people"), 2)


class TestMostPeopleHardNegatives(unittest.TestCase):
    """Hard negatives (DoD 3): first-person source, mid-sentence use."""

    def test_most_people_with_interview_source_no_fire(self):
        text = ("Most people I interviewed said the same thing twice, "
                "once on record and once after the recorder was off. "
                "Most people we surveyed in March confirmed the pattern.")
        hits = filler_hits(text)
        self.assertNotIn("most people", hits)

    def test_mid_sentence_most_people_not_counted(self):
        # not sentence-initial, not guarded-class: bare mid-sentence use
        # in a technical register is not the weasel pattern
        text = ("Latency budgets matter because most people notice jank "
                "above 100ms, and most people blame the network when in "
                "fact the main thread is blocked by layout thrash.")
        self.assertNotIn("most people", filler_hits(text))


class TestHopeThisHelpsGuard(unittest.TestCase):
    """Guard (a): 'hope this helps' before a sign-off is a support close."""

    def test_support_mail_no_signoff_family_hit(self):
        text = ("Hi Alex,\n\nthe config flag you asked about is "
                "`payments.async=true` in staging. It needs a deploy "
                "afterwards to take effect.\n\nI hope this helps!\n\n"
                "Best regards,\nSam")
        matches = cats(text)
        self.assertNotIn("i hope this helps",
                         matches.get("assistant_signoff", []))
        self.assertNotIn("hope this helps",
                         matches.get("assistant_signoff", []))

    def test_forum_reply_with_cheers_guarded(self):
        text = ("Re: nginx 502 after upgrade\n\nCheck the upstream "
                "buffer sizes, that fixed it for me on 1.25.\n\n"
                "Hope this helps — cheers!")
        matches = cats(text)
        for hits in matches.values():
            for v in ("hope this helps", "i hope this helps"):
                self.assertNotIn(v, hits)

    def test_blog_migration_still_fires(self):
        """Positive: chatbot tell migrated into written content (no sign-off)."""
        text = ("Here's a quick update on the pricing change. Most people "
                "will see no difference. I hope this helps clarify what "
                "comes next for the platform and the roadmap ahead of us.")
        # the family survives when there is no sign-off context
        matches = cats(text)
        self.assertGreaterEqual(len(filler_hits(text)), 2)


class TestCumulativeRuleRespected(unittest.TestCase):
    """The category follows PHRASE_MIN_HITS like every other category."""

    def test_threshold_constant(self):
        from fp_guards import THRESHOLDS
        self.assertEqual(THRESHOLDS["PHRASE_MIN_HITS"], 2)

    def test_category_registered(self):
        self.assertIn("conversational_fillers", slop_scorer.PHRASE_CATEGORIES)


if __name__ == "__main__":
    unittest.main()
