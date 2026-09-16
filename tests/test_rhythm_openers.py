"""Tests for rhythm/opener metrics (issue #27) — detect-only."""

import os
import sys
import unittest

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SCRIPTS = os.path.join(ROOT, "skills", "ai-slop-detection", "scripts")
sys.path.insert(0, SCRIPTS)

from rhythm_openers import rhythm_metrics


def fired(text):
    return {s["id"] for s in rhythm_metrics(text)["signals"]}


class UniformLengthRunTests(unittest.TestCase):
    def test_three_consecutive_similar_lengths_fire(self):
        text = (
            "The pipeline failed on Tuesday night. "
            "The dashboard showed no new anomalies. "
            "The on-call engineer slept right through. "
            "Then, quite unexpectedly and against every forecast, everything exploded."
        )
        self.assertIn("UniformLengthRun", fired(text))

    def test_varied_lengths_do_not_fire(self):
        text = (
            "It broke. "
            "The pipeline failure on Tuesday night took down billing, search, and login at once. "
            "Why? Because nobody. "
            "Afterwards, the on-call engineer wrote a very detailed and honest postmortem."
        )
        self.assertNotIn("UniformLengthRun", fired(text))

    def test_two_similar_sentences_do_not_fire(self):
        text = (
            "The pipeline failed on Tuesday night. "
            "The dashboard showed no new anomalies. "
            "Then everything exploded spectacularly and without warning whatsoever, everywhere."
        )
        self.assertNotIn("UniformLengthRun", fired(text))


class SelfAnswerTests(unittest.TestCase):
    def test_why_because_fires(self):
        text = "Why does this matter? Because latency kills retention."
        self.assertIn("SelfAnsweredQuestion", fired(text))

    def test_whats_the_catch_fires(self):
        text = "What's the catch? It's simple: the free tier is capped."
        self.assertIn("SelfAnsweredQuestion", fired(text))

    def test_genuine_question_does_not_fire(self):
        text = (
            "Why did the migration stall? The audit log shows a lock held by "
            "a forgotten cron job from 2023."
        )
        self.assertNotIn("SelfAnsweredQuestion", fired(text))


class OpenerDiversityTests(unittest.TestCase):
    def test_majority_identical_openers_fire(self):
        text = (
            "The team shipped the billing page. "
            "The team rewrote search last week. "
            "The team also fixed login flows. "
            "The team then took a week off. "
            "Management noticed nothing at all."
        )
        self.assertIn("LowOpenerDiversity", fired(text))

    def test_diverse_openers_do_not_fire(self):
        text = (
            "The team shipped the billing page. "
            "Last week, search got rewritten. "
            "Meanwhile, login flows were fixed quietly. "
            "Afterwards, everyone took a week off. "
            "Management noticed nothing at all."
        )
        self.assertNotIn("LowOpenerDiversity", fired(text))

    def test_short_text_does_not_fire(self):
        text = "It works. It scales. It ships."
        self.assertNotIn("LowOpenerDiversity", fired(text))


class OpenerAnnouncementTests(unittest.TestCase):
    """Issue #230: frame-based opener announcements (detect-only)."""

    def test_german_frames_fire(self):
        text = (
            "Ich möchte kurz erklären, warum das wichtig ist. "
            "Spannender Punkt. "
            "Ein weiterer Aspekt ist die Skalierung. "
            "Die spannende Frage ist, wer das bezahlt."
        )
        self.assertIn("OpenerAnnouncement", fired(text))

    def test_english_frames_fire(self):
        text = (
            "I want to walk through the architecture. "
            "Interesting point. "
            "Another aspect is the cost model. "
            "The exciting part is the eval."
        )
        self.assertIn("OpenerAnnouncement", fired(text))

    def test_stance_with_reasoning_is_exempt(self):
        # Hard negative: "Ich denke, dass X" WITH a following justification
        # is a genuine claim, not an announcement frame.
        text = (
            "Ich denke, dass die Migration scheiterte, weil ein vergessener "
            "Cron-Job ein Lock hielt; das Audit-Log belegt es."
        )
        self.assertNotIn("OpenerAnnouncement", fired(text))

    def test_english_stance_with_reasoning_is_exempt(self):
        text = (
            "I think that the migration stalled because a forgotten cron "
            "job held a lock; the audit log proves it."
        )
        self.assertNotIn("OpenerAnnouncement", fired(text))

    def test_mid_sentence_adjective_is_not_an_opener(self):
        # Hard negative: "spannender Punkt" mid-sentence, not clause-initial.
        text = (
            "Der spannendste Punkt der Debatte war die Haftungsbegrenzung, "
            "nicht die Laufzeit des Vertrags."
        )
        self.assertNotIn("OpenerAnnouncement", fired(text))

    def test_plain_prose_does_not_fire(self):
        text = (
            "Die Rechnung vom März war falsch. Der Support brauchte vier "
            "Anläufe. Am Ende gab es eine Gutschrift."
        )
        self.assertNotIn("OpenerAnnouncement", fired(text))


class ParagraphConnectorRateTests(unittest.TestCase):
    """Issue #230: additive-connector paragraph openers (advisory rate)."""

    def test_connector_heavy_text_fires(self):
        paras = [
            "Der Vertrag tritt am 1.1. in Kraft.",
            "Darüber hinaus gilt die Verschwiegenheitsklausel.",
            "Zudem umfasst die Haftung auch Folgeschäden.",
            "Gleichzeitig erlischt die alte Vereinbarung.",
            "Abschließend sei der Streitwert erwähnt.",
            "Zusammenfassend bleiben alle Klauseln wirksam.",
        ]
        text = "\n\n".join(paras)
        self.assertIn("ParagraphConnectorRate", fired(text))
        self.assertGreater(rhythm_metrics(text)["paragraph_connector_rate"], 0.4)

    def test_legal_register_with_single_connector_does_not_fire(self):
        # Hard negative: 'Darüber hinaus' in a legal-genre text — one
        # connector-led paragraph out of many is house style, not slop.
        paras = [
            "Der Kläger trägt die Beweislast.",
            "Darüber hinaus bleibt § 823 BGB einschlägig.",
            "Das Gericht hat die Zuständigkeit bejaht.",
            "Die Kostenentscheidung folgt aus § 91 ZPO.",
            "Der Streitwert wird auf 5.000 EUR festgesetzt.",
        ]
        text = "\n\n".join(paras)
        self.assertNotIn("ParagraphConnectorRate", fired(text))
        self.assertLessEqual(rhythm_metrics(text)["paragraph_connector_rate"], 0.4)

    def test_plain_prose_paragraphs_do_not_fire(self):
        paras = [
            "Wir haben die Rechnungen geprüft.",
            "Drei Positionen waren doppelt.",
            "Der Lieferant hat es bestätigt.",
            "Die Gutschrift kommt nächste Woche.",
        ]
        text = "\n\n".join(paras)
        self.assertNotIn("ParagraphConnectorRate", fired(text))
        self.assertEqual(rhythm_metrics(text)["paragraph_connector_rate"], 0.0)

    def test_english_connectors_counted(self):
        paras = [
            "Moreover, the cache layer added latency.",
            "Furthermore, the retries duplicated writes.",
            "Additionally, the dashboard lied about both.",
        ]
        text = "\n\n".join(paras)
        self.assertIn("ParagraphConnectorRate", fired(text))


class DetectOnlyNoScoreTests(unittest.TestCase):
    """Issue #230 acceptance: no score influence (ADR-0006)."""

    def test_new_signals_have_no_score_dimension(self):
        from slop_scorer import slop_score

        slop_text = (
            "Ich möchte kurz erklären, warum das wichtig ist. "
            "Spannender Punkt."
        )
        result = slop_score(slop_text)
        self.assertNotIn("rhythm_openers", result.get("dimension_scores", {}))
        self.assertNotIn("opener_announcement", result.get("dimension_scores", {}))
        self.assertNotIn("paragraph_connector_rate", result.get("dimension_scores", {}))


if __name__ == "__main__":
    unittest.main()
