"""Issue #299 (btm-openclaw-platform #1269): quote exemption must cover
German quotes („…“) and Guillemets (»…«), and the slopkit engine path
(src/classifier.py) must apply the exemption like the skill scorer does.

Befund im Issue (Stand f8c4aa3):
  (a) strip_quotes() kannte nur "…" / “…” / '…' — deutsche Zitate (U+201E
      … U+201C) und Guillemets blieben stehen.
  (b) Die CLI (slop score/classify → slopkit._engine → src/classifier.py)
      wandte die Quote-Exemption nie an: quoted text scored identisch zum
      unquoted text.
"""

import os
import sys
import unittest
from unittest import mock

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SCRIPTS = os.path.join(ROOT, "skills", "ai-slop-detection", "scripts")
for p in (ROOT, SCRIPTS, os.path.join(ROOT, "src")):
    if p not in sys.path:
        sys.path.insert(0, p)

import fp_guards  # noqa: E402

DE_INNER = (
    "Heutzutage zeigen Studien eindeutig, dass es nicht nur um Technik "
    "geht. Studien zeigen außerdem, dass zusammenfassend in der heutigen "
    "Zeit vieles anders ist."
)


def _engine():
    from slopkit import Engine
    return Engine()


class GermanQuotePairsStripped(unittest.TestCase):
    def test_long_german_quote_is_stripped(self):
        text = "Der Bericht schreibt: \u201e" + DE_INNER + "\u201c Wir prüfen das."
        stripped = fp_guards.strip_quotes(text)
        self.assertNotIn("Studien zeigen", stripped)
        self.assertIn("Der Bericht schreibt:", stripped)

    def test_long_guillemet_quote_is_stripped(self):
        text = "Der Bericht schreibt: \u00bb" + DE_INNER + "\u00ab Wir prüfen das."
        stripped = fp_guards.strip_quotes(text)
        self.assertNotIn("Studien zeigen", stripped)

    def test_short_german_quote_is_kept(self):
        # Ein einzelnes Wort in deutschen Anführungszeichen bleibt ein
        # legitimes Signal-Umfeld (Parität zur ASCII/EN-Konvention).
        text = "Sie nannte das \u201edelve\u201c und ging weiter."
        stripped = fp_guards.strip_quotes(text)
        self.assertIn("delve", stripped)


class EngineAppliesQuoteExemption(unittest.TestCase):
    """Befund (b): die CLI-Engine (src/classifier.py) muss quoted slop
    nicht flaggen — alle fünf Zitierweisen verhalten sich gleich."""

    @classmethod
    def setUpClass(cls):
        cls.engine = _engine()

    def _score(self, text):
        return self.engine.classify_text(text)

    def test_quoted_slop_example_scores_clean(self):
        for name, text in (
            ("ascii", 'Der Bericht schreibt: "' + DE_INNER + '" Wir prüfen das.'),
            ("de", "Der Bericht schreibt: \u201e" + DE_INNER + "\u201c Wir prüfen das."),
            ("guill", "Der Bericht schreibt: \u00bb" + DE_INNER + "\u00ab Wir prüfen das."),
        ):
            with self.subTest(variant=name):
                result = self._score(text)
                self.assertLess(
                    result.overall_slop_score, 0.40,
                    f"{name}: quoted slop flagged: {result.overall_slop_score}")
                self.assertEqual(result.signals_detected, [])

    def test_same_slop_unquoted_is_still_flagged(self):
        result = self._score(DE_INNER)
        self.assertGreaterEqual(result.overall_slop_score, 0.40)

    def test_signal_text_survives_without_fp_guards(self):
        # Regression (Review 14.10., HORST): classify_text las `text_lower`
        # in der signal_text-Zeile, BEVOR text_lower belegt wurde. Ohne
        # fp_guards (Wheel/Deploy-Layout: weder importierbar noch Repo-
        # Datei) knallte dadurch JEDER classify_text-Aufruf mit
        # UnboundLocalError — dieselbe Bug-Klasse, die 9057b5d für den
        # os.path-Fallback fixte.
        import os as _os
        import sys as _sys
        saved_mod = _sys.modules.pop("fp_guards", None)
        saved_path = _sys.path[:]
        scripts_dir = _os.path.join(
            "skills", "ai-slop-detection", "scripts")
        fallback_suffix = _os.path.join(scripts_dir, "fp_guards.py")

        real_exists = _os.path.exists

        def fake_exists(p):
            if isinstance(p, str) and p.endswith(fallback_suffix):
                return False
            return real_exists(p)

        try:
            _sys.path = [
                p for p in _sys.path
                if not (isinstance(p, str)
                        and p.rstrip("/").endswith(scripts_dir))
            ]
            with mock.patch("os.path.exists", fake_exists):
                result = self.engine.classify_text(
                    "Wir prüfen das Setup kurz.")
        finally:
            _sys.path = saved_path
            if saved_mod is not None:
                _sys.modules["fp_guards"] = saved_mod
        self.assertIsInstance(result.overall_slop_score, float)

    def test_quoted_slop_paragraph_engine_parity(self):
        # Paritätsfall wie tests/test_fp_guards.py im Skill-Scorer: ein
        # Sachtext, der ein komplettes Slop-Beispiel zitiert, bleibt unter
        # der Decision-Schwelle.
        slop_example = (
            "In today's rapidly evolving digital landscape, it's important to note "
            "that the rich tapestry of AI tools serves as a testament to innovation. "
            "Whether you're a seasoned developer or just starting out, let's dive "
            "into how these cutting-edge solutions can unlock your potential and "
            "harness the power of transformative technology. At its core, this "
            "paradigm shift is paramount to navigating the landscape of modern "
            "software development. Furthermore, it's crucial to understand the "
            "multifaceted nature of these robust, seamless, and holistic platforms."
        )
        wrapped = (
            "The vendor pitch we received yesterday is reproduced below for the "
            'record.\n\n"' + slop_example + '"\n\nWe did not adopt any of these '
            "claims. The measured latency increase was 3 ms under load."
        )
        result = self._score(wrapped)
        self.assertLess(result.overall_slop_score, 0.40,
                        f"quoted slop flagged: {result.overall_slop_score}")


if __name__ == "__main__":
    unittest.main()
