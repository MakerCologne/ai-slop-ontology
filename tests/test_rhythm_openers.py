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
            "The dashboard showed nothing unusual. "
            "The on-call engineer slept through it. "
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
            "The dashboard showed nothing unusual. "
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


if __name__ == "__main__":
    unittest.main()
