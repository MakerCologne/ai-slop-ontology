"""Issue #110: conversational_fillers phrase category (Hassid list, points 4-8).

Detect-only conversational filler phrases, covered by two hard-negative
guards (fp_guards.mask_conversation_fillers):

  (a) "hope this helps" does not count when it sits in the last 100 chars
      before a sign-off (real support-mail context)
  (b) "most people" does not count when followed by a direct source
      attribution ("most people I interviewed …") or as "most people I know"

DoD: per phrase 2 positive + 2 hard-negative fixtures. Occurrence counts
are asserted through slop_scorer.find_term_matches on guard-masked text
(phrase_category_score lists distinct terms — its occurrence-count quirk
is pre-existing engine behavior, out of scope here).
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


def occ(text, term):
    """Occurrences of term in guard-masked signal text."""
    masked = fp_guards.mask_conversation_fillers(text.lower())
    return slop_scorer.find_term_matches(masked, [term]).get(term, 0)


def category_terms(text):
    return slop_scorer.phrase_category_score(text).get(
        "conversational_fillers", [])


class TestHeresTheThing(unittest.TestCase):
    def test_positive_opener_twice(self):
        t = ("Here's the thing about modern tooling. Here's the thing "
             "nobody considers: latency budget. We measured it at 3 ms.")
        self.assertEqual(occ(t, "here's the thing"), 2)
        self.assertIn("here's the thing", category_terms(t))

    def test_positive_mid_text_pair(self):
        t = ("The pipeline was slow. Here's the thing we missed in the "
             "review. Here's the thing about caches: they lie.")
        self.assertEqual(occ(t, "here's the thing"), 2)

    def test_negative_single_hit_no_category(self):
        t = ("One deployment failed. Here's the thing: the health check "
             "timed out, which we traced to a DNS refresh issue.")
        # single occurrence: reported but below the cumulative scoring bar
        self.assertEqual(occ(t, "here's the thing"), 1)
        result = slop_scorer.slop_score(t)
        self.assertLess(result["dimensions"]["phrase_match_count"], 2)

    def test_negative_bare_thing_unmatched(self):
        # "the thing" without the conversation-setup formula never matches
        t = ("The thing we measured was p99 latency, not average latency. "
             "The thing is documented in the runbook.")
        self.assertEqual(occ(t, "here's the thing"), 0)


class TestHopeThisHelps(unittest.TestCase):
    def test_positive_blog_context_pair(self):
        t = ("Hope this helps someone out there. Hope this helps you "
             "avoid the same migration trap. That's all for today.")
        self.assertEqual(occ(t, "hope this helps"), 2)

    def test_positive_far_from_signoff(self):
        t = ("Hope this helps your team. Hope this helps future readers. "
             "Let me know if anything is unclear.")
        self.assertEqual(occ(t, "hope this helps"), 2)

    def test_negative_support_mail_signoff_guard(self):
        # DoD hard negative: legit sign-off in a real support mail → no fire
        t = ("Der Fix ist im master. Hope this helps. Hope this helps "
             "auch beim naechsten Mal.\n\nBest regards,\nAlex")
        self.assertEqual(occ(t, "hope this helps"), 0)
        self.assertNotIn("hope this helps", category_terms(t))

    def test_negative_german_signoff_guard(self):
        t = ("Der Fix ist im master. Hope this helps. Hope this helps "
             "auch beim naechsten Ausfall.\n\nViele Grüße\nStefan")
        self.assertEqual(occ(t, "hope this helps"), 0)


class TestQuickUpdate(unittest.TestCase):
    def test_positive_pair(self):
        t = ("To provide a quick update: the cluster is green again. "
             "To provide a quick update on the audit: two findings open.")
        self.assertEqual(occ(t, "to provide a quick update"), 2)

    def test_positive_repeated_meta_announcement(self):
        t = ("To provide a quick update first, then the numbers. "
             "To provide a quick update on spend: we are under budget.")
        self.assertEqual(occ(t, "to provide a quick update"), 2)

    def test_negative_single_occurrence(self):
        t = ("To provide a quick update: the release shipped. The metrics "
             "are stable and the rollback path is documented in detail.")
        # single occurrence: below the >=2 cumulative bar, not scored
        self.assertEqual(occ(t, "to provide a quick update"), 1)
        result = slop_scorer.slop_score(t)
        self.assertLess(result["dimensions"]["phrase_match_count"], 2)

    def test_negative_substantive_update_without_formula(self):
        # The update given directly, without the meta-announcement formula
        t = ("Quick update: the release shipped. Update two: metrics "
             "stable. We also closed the audit findings from last week.")
        self.assertEqual(occ(t, "to provide a quick update"), 0)


class TestMostPeople(unittest.TestCase):
    def test_positive_opener_pair(self):
        t = ("Most people think caching is free. Most people skip the "
             "p99 tail. Both assumptions broke our pipeline last week.")
        self.assertEqual(occ(t, "^most people"), 2)

    def test_positive_paragraph_opener(self):
        t = ("We rewrote the ingest layer.\n\nMost people underestimate "
             "queue backpressure, and the on-call rota proves it.")
        self.assertEqual(occ(t, "^most people"), 1)
        self.assertIn("^most people", category_terms(t))

    def test_negative_attribution_interviewed(self):
        # DoD hard negative: direct source → pseudo-claim becomes real data
        t = ("Most people I interviewed reported the same outage window. "
             "Most people we surveyed use p50 dashboards only.")
        self.assertEqual(occ(t, "^most people"), 0)
        self.assertNotIn("^most people", category_terms(t))

    def test_negative_attribution_most_people_i_know(self):
        t = ("Most people I know run their own mail server. Most people "
             "in my team prefer plain SQL over any ORM for reporting.")
        self.assertEqual(occ(t, "^most people"), 0)


class TestCumulativeRule(unittest.TestCase):
    """Category contributes to phrase_slop only with >= 2 hits (#23)."""

    def test_two_distinct_phrases_score_family(self):
        t = ("Here's the thing: the health check. To provide a quick "
             "update: nothing else matched in this fixture text at all.")
        self.assertEqual(len(category_terms(t)), 2)
        result = slop_scorer.slop_score(t)
        self.assertGreaterEqual(result["dimensions"]["phrase_match_count"], 2)

    def test_single_hit_not_scored(self):
        t = ("Here's the thing: one signal hit is a stylistic accident, "
             "not a pattern, and the scorer must treat it as such.")
        result = slop_scorer.slop_score(t)
        self.assertLess(result["dimensions"]["phrase_match_count"], 2)

    def test_guard_applied_end_to_end(self):
        support = ("Hope this helps. Hope this helps twice, but the guard "
                   "must fire anyway because this is a support mail.\n\n"
                   "Kind regards,\nSupport")
        result = slop_scorer.slop_score(support)
        self.assertNotIn(
            "conversational_fillers", result["dimensions"].get(
                "phrase_categories", {}))


if __name__ == "__main__":
    unittest.main()
