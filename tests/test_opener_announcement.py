"""Issue #230 / P3: opener_announcement + paragraph_connector_rate (detect-only).

Abnahmekriterien: >=1 True Positive + >=2 Hard Negatives je Signal.
"""
import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "skills" / "ai-slop-detection" / "scripts"))

from rhetorical_patterns import find_rhetorical_patterns  # noqa: E402
from rhythm_openers import paragraph_connector_rate, rhythm_metrics  # noqa: E402


def ids(text):
    return {p["id"] for p in find_rhetorical_patterns(text)}


class OpenerAnnouncementTest(unittest.TestCase):
    # --- True Positives ---
    def test_tp_praise_opener(self):
        self.assertIn("OpenerAnnouncement", ids(
            "Spannender Punkt. Ich denke, ein weiterer wichtiger Aspekt ist die Frage, wie viel Prozesswissen verfuegbar ist."))

    def test_tp_further_aspect(self):
        self.assertIn("OpenerAnnouncement", ids("Ein weiterer Aspekt ist die Speicherung der Zugriffe."))

    def test_tp_question_announcement(self):
        self.assertIn("OpenerAnnouncement", ids("Die spannende Frage ist, wie wir das skalieren."))

    def test_tp_text_initial_ich_approach_without_reason(self):
        self.assertIn("OpenerAnnouncement", ids(
            "Ich moechte mich kurz vorstellen und unser Angebot eroertern."))

    # --- Hard Negatives ---
    def test_hn_ich_danke_mit_begruendung(self):
        # Haltung MIT Begrundung traegt Inhalt - darf nicht feuern (keep_when).
        self.assertNotIn("OpenerAnnouncement", ids(
            "Ich denke, dass diese Entscheidung falsch war, weil die Zahlen nicht belastbar waren."))

    def test_hn_ich_mid_text(self):
        self.assertNotIn("OpenerAnnouncement", ids(
            "Zunaechst die Fakten. Ich denke dabei vor allem an das Team vor Ort, das seit Monaten warnt."))

    def test_hn_content_first_sentence(self):
        self.assertNotIn("OpenerAnnouncement", ids("Entscheidend ist hier vor allem das Prozesswissen."))


class ParagraphConnectorRateTest(unittest.TestCase):
    # --- True Positive ---
    def test_tp_connector_chain(self):
        text = ("Einfuehrung.\n\nDarueber hinaus bleibt die Frage offen.\n\n"
                "Zudem fehlen Zahlen.\n\nAbschliessend empfehlen wir Pause.")
        self.assertEqual(paragraph_connector_rate(text), 0.75)
        self.assertIn("ParagraphConnectorRate",
                      {s["id"] for s in rhythm_metrics(text)["signals"]})

    # --- Hard Negatives ---
    def test_hn_legal_single_connector(self):
        # Juristisches Genre: EIN Konnektor-Absatz unter vieren ist Konvention, kein Muster.
        text = ("Einleitung des Gutachtens.\n\nDarueber hinaus ist der Vertrag nach Paragraf 437 BGB rueckabzuwickeln.\n\n"
                "Zwischenergebnis bleibt unklar.\n\nFazit empfiehlt Klage.")
        m = rhythm_metrics(text)
        self.assertLessEqual(m["paragraph_connector_rate"], 0.3)
        self.assertNotIn("ParagraphConnectorRate", {s["id"] for s in m["signals"]})

    def test_hn_two_paragraphs_only(self):
        # Kurze Texte feuern nie (analog LowOpenerDiversity-Guard).
        m = rhythm_metrics("Text A.\n\nDarueber hinaus Text B.")
        self.assertNotIn("ParagraphConnectorRate", {s["id"] for s in m["signals"]})


if __name__ == "__main__":
    unittest.main()
