"""Tests für guard/voice_drift.py (issue #56: Voice-Drift-Guardrail)."""

import unittest

from guard.voice_drift import (
    OK, SKIP, VOICE_DRIFT, VoiceDriftParams,
    burstiness, evaluate, token_change_ratio, tokenize, ttr,
)

BASELINE = (
    "Der alte Brunnen quietschte. Trotzdem. Wir blieben stehen und hörten zu, "
    "wie das Wasser in der Dunkelheit seinen Weg suchte, Stein für Stein, "
    " geduldig und ohne Eile. Nebenan klapperte ein Ladenladen. Keiner sagte etwas. "
    " Später, am Zaun, erzählte Miriam von ihrem Onkel, der Brunnen baute in Thüringen, "
    " und dass sie als Kind immer dachte, das Wasser käme von irgendwo unter dem Feld. "
    " Der Hund jaulte kurz. Dann war wieder nur das Quietschen und ein entfernter Zug."
)

# Minimal-Invasive-Edit: 1 Satz umgestellt, ein Wort ersetzt → OK
SMALL_EDIT = BASELINE.replace("geduldig und ohne Eile", "ruhig und ohne Hast")

# Full Rewrite: gleiche Infos, komplett umformuliert + geglättet → DRIFT
REWRITE = (
    "In addition, it is important to note that the historic fountain produced a "
    "squeaking sound throughout the evening. Furthermore, the group remained at the "
    "location and carefully listened to the flowing water in the surrounding darkness. "
    "Moreover, the process occurred gradually and without any unnecessary urgency. "
    "Additionally, a nearby shop sign could be heard clearly in the quiet street. "
    "Subsequently, Miriam shared a story about her uncle, who built fountains in the "
    "region, and explained that she believed the water originated beneath the fields. "
    "Ultimately, the evening concluded with the sound of a distant train."
)


class TestTokenize(unittest.TestCase):
    def test_lowercase_words(self):
        self.assertEqual(tokenize("Hello, World! hölt_1"), ["hello", "world", "hölt_1"])

    def test_empty(self):
        self.assertEqual(tokenize(""), [])


class TestTokenChangeRatio(unittest.TestCase):
    def test_identical(self):
        t = tokenize(BASELINE)
        self.assertEqual(token_change_ratio(t, t), 0.0)

    def test_empty_both(self):
        self.assertEqual(token_change_ratio([], []), 0.0)

    def test_small_edit_low_ratio(self):
        base, cur = tokenize(BASELINE), tokenize(SMALL_EDIT)
        self.assertLess(token_change_ratio(base, cur), 0.10)

    def test_full_rewrite_high_ratio(self):
        self.assertGreater(
            token_change_ratio(tokenize(BASELINE), tokenize(REWRITE)), 0.5)


class TestBurstiness(unittest.TestCase):
    def test_uniform_is_low(self):
        text = "Eins zwei drei vier. Eins zwei drei vier. Eins zwei drei vier."
        self.assertLess(burstiness(text), 0.2)

    def test_varied_is_higher(self):
        text = "Kurz. Noch kürzer. Ein sehr viel längerer Satz mit vielen Wörtern folgt jetzt hier."
        self.assertGreater(burstiness(text), burstiness("Eins zwei drei. Eins zwei drei."))

    def test_single_sentence(self):
        self.assertEqual(burstiness("Nur ein Satz."), 0.0)


class TestTTR(unittest.TestCase):
    def test_repetition_low(self):
        self.assertLess(ttr(tokenize("a b a b a b a b a b a b")), 0.3)

    def test_diverse_high(self):
        self.assertGreater(ttr(tokenize("a b c d e f g h")), 0.9)


class TestEvaluate(unittest.TestCase):
    def test_identical_ok(self):
        v = evaluate(BASELINE, BASELINE)
        self.assertEqual(v.verdict, OK)
        self.assertEqual(v.reasons, [])

    def test_small_edit_ok(self):
        v = evaluate(BASELINE, SMALL_EDIT)
        self.assertEqual(v.verdict, OK, v.reasons)

    def test_full_rewrite_drifts(self):
        v = evaluate(BASELINE, REWRITE)
        self.assertEqual(v.verdict, VOICE_DRIFT)
        self.assertTrue(any(r.startswith("TOKEN_BUDGET") for r in v.reasons))

    def test_homogenized_rhythm_drifts(self):
        # Token-Budget einhalten (kleine Edits), aber Rhythmus komplett glätten:
        # alle Sätze auf gleiche Länge kürzen würde das Budget sprengen — stattdessen
        # gezielt: Baseline mit stark variierenden Satzlängen vs. geglättete Variante
        varied = "A. " + "Wort " * 20 + ". " + "B b. " + "Wort " * 3 + ". " + "C c c. " + "Wort " * 12 + "."
        flat = " ".join([" ".join(["wort"] * 7) + "." for _ in range(5)])
        v = evaluate(varied, flat)
        self.assertEqual(v.verdict, VOICE_DRIFT)

    def test_very_short_skip(self):
        v = evaluate("kurz", "kurz anders")
        self.assertEqual(v.verdict, SKIP)

    def test_custom_beta(self):
        v = evaluate(BASELINE, SMALL_EDIT, VoiceDriftParams(beta_token_change=0.001))
        self.assertEqual(v.verdict, VOICE_DRIFT)
        self.assertTrue(v.reasons[0].startswith("TOKEN_BUDGET"))


if __name__ == "__main__":
    unittest.main()
