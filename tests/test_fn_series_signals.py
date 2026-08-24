"""FN-Serie 0101/0504/0202/0303/0403/0606: corpus-evidenced phrase signals.

Batch F (2026-08-25): the six templated FN series of eval/corpus.jsonl
(160 false negatives at threshold 0.40, baseline v2.0.0: P 1.0 / R 0.276)
are recovered with new phrase categories mined from the FN texts
themselves. Evidence discipline per METHODOLOGY M7 (Empirie-vor-Ausbau):

  - every new phrase occurs in >= 3 slop corpus texts (counted),
  - every new phrase occurs in 0 of the 103 clean corpus texts (counted,
    asserted in TestPhraseEvidenceDiscipline).

Threshold stays 0.40 (fp_guards.THRESHOLDS). Hard gate: FP must stay 0.

Red tests 2026-08-25 (batch-f, cluster C1).
"""

import json
import os
import sys
import unittest

SCRIPTS = os.path.join(
    os.path.dirname(__file__), "..", "skills", "ai-slop-detection", "scripts"
)
sys.path.insert(0, SCRIPTS)

import slop_scorer  # noqa: E402

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CORPUS = os.path.join(ROOT, "eval", "corpus.jsonl")


def corpus_items():
    with open(CORPUS) as f:
        return [json.loads(l) for l in f if l.strip()]


def series_texts(prefix):
    return [d for d in corpus_items()
            if d["label"] == "slop" and d["id"].startswith(prefix)]


def clean_texts():
    return [d for d in corpus_items() if d["label"] == "clean"]


TH = 0.40


class TestBoilerplateSignals(unittest.TestCase):
    """C3 — wiki/promo boilerplate + assistant sign-off formulas
    (series 0303/0403/0606).

    Real corpus lines (examples):
      slop-0606-001: "Of course! Here's the summary you asked for. The
        platform boasts a vibrant marketplace ... Let me know if you'd like
        more detail on any section. Certainly! Let me expand on that."
      slop-0403-001: "The festival has garnered recognition for its vibrant
        programming, setting the stage for future growth."
      slop-0303-001: "It is believed that the manuscript predates the fire.
        Based on available information, the outage lasted two hours."
    """

    def _assert_series_detected(self, prefix):
        misses = [d["id"] for d in series_texts(prefix)
                  if slop_scorer.slop_score(d["text"])["slop_score"] < TH]
        self.assertEqual(misses, [], f"undetected {prefix} items: {misses[:5]}")

    def test_series_0303_weasel_boilerplate_detected(self):
        self._assert_series_detected("slop-0303-")

    def test_series_0403_wiki_promo_detected(self):
        self._assert_series_detected("slop-0403-")

    def test_series_0606_assistant_signoff_detected(self):
        self._assert_series_detected("slop-0606-")


class TestReportHedgingSignals(unittest.TestCase):
    """C2 — business/report hedging + fake-authority formulas (series 0202).

    Real corpus lines (examples):
      slop-0202-002: "It is important to note that the data shows a clear
        trend. Studies show the payoff compounds over quarters."
      slop-0202-009: "Industry reports suggest adoption doubled ..."
    """

    def test_series_0202_report_hedging_detected(self):
        misses = [d["id"] for d in series_texts("slop-0202-")
                  if slop_scorer.slop_score(d["text"])["slop_score"] < TH]
        self.assertEqual(misses, [], f"undetected slop-0202 items: {misses[:5]}")


class TestMarketingFormulaSignals(unittest.TestCase):
    """C1 — SaaS/marketing CTA formulas + punchy insight-porn (series 0101/0504).

    Real corpus lines (examples):
      slop-0504-001: "Start your free trial today. Most Popular Book a demo
        with our team. ... But here's the catch: the API rate-limits you
        anyway. This is where things get interesting."
      slop-0101-001: "The implications are significant. ... It's worth noting
        that nothing here is new."
      slop-0101-002: "Here's the thing: nobody tells you this upfront.
        Make no mistake, the window is closing."
    """

    def test_series_0504_marketing_cta_detected(self):
        misses = [d["id"] for d in series_texts("slop-0504-")
                  if slop_scorer.slop_score(d["text"])["slop_score"] < TH]
        self.assertEqual(misses, [], f"undetected slop-0504 items: {misses[:5]}")

    def test_series_0101_punchy_insight_detected(self):
        misses = [d["id"] for d in series_texts("slop-0101-")
                  if slop_scorer.slop_score(d["text"])["slop_score"] < TH]
        self.assertEqual(misses, [], f"undetected slop-0101 items: {misses[:5]}")


class TestPhraseEvidenceDiscipline(unittest.TestCase):
    """M7 evidence rule for every batch-f phrase category: >=3 slop texts,
    0 clean texts (substring match on normalized text, 2026-08-25 count)."""

    MIN_SLOP_TEXTS = 3

    def _check(self, category):
        self.assertIn(category, slop_scorer.PHRASE_CATEGORIES)
        phrases = slop_scorer.PHRASE_CATEGORIES[category]["phrases"]
        self.assertTrue(phrases)
        clean = clean_texts()
        for p in phrases:
            slop_hits = sum(1 for d in corpus_items()
                            if d["label"] == "slop" and p in d["text"].lower())
            self.assertGreaterEqual(
                slop_hits, self.MIN_SLOP_TEXTS,
                f"phrase '{p}' lacks evidence (<3 slop texts)")
            clean_hits = [d["id"] for d in clean if p in d["text"].lower()]
            self.assertEqual(
                clean_hits, [],
                f"phrase '{p}' appears in clean texts {clean_hits}")

    def test_marketing_cta_evidence(self):
        self._check("marketing_cta")

    def test_punchy_insight_evidence(self):
        self._check("punchy_insight")

    def test_report_hedging_evidence(self):
        self._check("report_hedging")

    def test_wiki_promo_evidence(self):
        self._check("wiki_promo")

    def test_assistant_signoff_evidence(self):
        self._check("assistant_signoff")


if __name__ == "__main__":
    unittest.main()
