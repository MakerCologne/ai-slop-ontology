"""DE-Typografie-Signale (issue #76, Teil 1, detect-only).

Quick Wins aus dem DE-Pattern-Katalog-Mapping (docs/de-coverage.md):
  M46 falsche deutsche Anführungszeichen  „Text” statt „Text“
  M47 englische Titel-Großschreibung      „... Und Umsetzt“ (Funktionswort
                                         mittendrin groß)
  M48 englisches Dezimal-/Datumsformat    3.5 statt 3,5; May 12 statt 12. Mai
  M49 Genitiv-Apostroph                   Peter's statt Peters

Alle detect-only, nie score-dominant; DE-Sprachgate schützt englische Texte.
Konzepte re-derivierte Eigenlistung nach de.wikipedia „Anzeichen für
KI-generierte Inhalte“ — kein Pattern-Material aus CC-BY-SA-Quellen kopiert.
"""

import os
import sys
import unittest

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SCRIPTS = os.path.join(ROOT, "skills", "ai-slop-detection", "scripts")
sys.path.insert(0, SCRIPTS)

import slop_scorer  # noqa: E402
from de_typography import (  # noqa: E402
    is_german, quote_mismatch, title_case_headings, en_number_formats,
    genitive_apostrophe, find_de_typography,
)

DE_BASE = ("Der Ausschuss hat die Zahlen geprüft und dabei festgestellt, "
           "dass weitere Untersuchungen nötig sind, bevor man entscheiden "
           "kann, ob die Maßnahmen greifen oder nicht wirklich helfen.")


class GermanGate(unittest.TestCase):
    def test_gate_positive_negative(self):
        self.assertTrue(is_german(DE_BASE))
        self.assertFalse(is_german("The committee reviewed the numbers and "
                                   "found that more research is needed "
                                   "before deciding on any of this stuff."))


class M46QuoteMismatch(unittest.TestCase):
    def test_positives(self):
        for t in (
            DE_BASE + " Sie sagte: „das ist so” und ging.",
            DE_BASE + " Ein Sprecher erklärte: „der Bericht kommt” danach.",
            DE_BASE + " Es heißt: „alles klar”, so die Verwaltung.",
        ):
            f = quote_mismatch(t)
            self.assertIsNotNone(f, t)
            self.assertIn("U+201D", f["evidence"], t)

    def test_negatives(self):
        for t in (
            DE_BASE + " Sie sagte: „das ist so“ und ging.",
            DE_BASE + " Ein Sprecher erklärte: „der Bericht kommt“ danach.",
            "She said: „das ist so” and left.",  # EN gate: not German
        ):
            self.assertIsNone(quote_mismatch(t), t)

    def test_boundaries(self):
        # straight quotes are NOT M46 (different pattern family)
        self.assertIsNone(quote_mismatch(DE_BASE + ' Sie meinte: "alles gut" dazu.'))
        # one correct pair + one mismatched pair still fires (per occurrence)
        t = DE_BASE + " Richtig: „so“ — falsch: „so” Ende."
        self.assertIsNotNone(quote_mismatch(t))


class M47TitleCase(unittest.TestCase):
    def test_positives(self):
        for t in (
            "## Die Wichtigsten Erkenntnisse Über KI Und Ihre Auswirkungen\n" + DE_BASE,
            "### Wie Man Die Beste Strategie Findet Und Umsetzt\n" + DE_BASE,
            "# Tipps Für Ein Besseres Zeitmanagement Mit Weniger Stress\n" + DE_BASE,
        ):
            f = title_case_headings(t)
            self.assertIsNotNone(f, t)

    def test_negatives(self):
        for t in (
            "## Die wichtigsten Erkenntnisse und ihre Auswirkungen\n" + DE_BASE,
            "The Best Strategies And Their Impact On Results Today",
            DE_BASE,  # Fließtext ohne Kapitalisierungs-Funktionswörter
        ):
            self.assertIsNone(title_case_headings(t), t)

    def test_boundaries(self):
        # Satzbeginn „Und“ einmal = Stil, kein Muster
        self.assertIsNone(title_case_headings("Und deshalb bleibt es dabei. " + DE_BASE))
        # EN-Text mit Titelcase fällt durch das DE-Gate
        self.assertIsNone(title_case_headings("Best Practices For Teams And Their Tools"))


class M48EnNumberFormats(unittest.TestCase):
    def test_positives(self):
        for t in (
            DE_BASE + " Die Quote lag bei 2.5 Prozent.",
            DE_BASE + " Das Treffen findet am May 12, 2026 statt.",
            DE_BASE + " Ein Anstieg von 1.8 auf 3.4 Einheiten wurde gemeldet.",
        ):
            f = en_number_formats(t)
            self.assertIsNotNone(f, t)

    def test_negatives(self):
        for t in (
            DE_BASE + " Die Quote lag bei 2,5 Prozent.",
            DE_BASE + " Das Treffen findet am 12. Mai 2026 statt.",
            "The rate was 2.5 percent and the meeting is on May 12, 2026.",  # EN gate
        ):
            self.assertIsNone(en_number_formats(t), t)

    def test_boundaries(self):
        # Versionsnummern sind legitim: 3.12 ist keine Dezimalzahl
        self.assertIsNone(en_number_formats(DE_BASE + " Wir nutzen Python 3.12 und v2.5."))
        # Datum mit Punkt mitten im Satz (Ordnungszahl) ist korrektes Deutsch
        self.assertIsNone(en_number_formats(DE_BASE + " Am 1. Mai beginnt es."))


class M49GenitiveApostrophe(unittest.TestCase):
    def test_positives(self):
        for t in (
            DE_BASE + " Das ist Peter's Entscheidung gewesen.",
            DE_BASE + " Wir folgen Maria's Vorschlag für das nächste Quartal.",
            DE_BASE + " Laut Klaus's Aufzeichnungen fehlen zwei Belege.",
        ):
            f = genitive_apostrophe(t)
            self.assertIsNotNone(f, t)

    def test_negatives(self):
        for t in (
            DE_BASE + " Das ist Peters Entscheidung gewesen.",
            DE_BASE + " Wir folgen Marias Vorschlag für das nächste Quartal.",
            "That is Peter's decision, and Maria's notes agree.",  # EN gate
        ):
            self.assertIsNone(genitive_apostrophe(t), t)

    def test_boundaries(self):
        # Eingetragene Marke mit Apostroph (allowlist)
        self.assertIsNone(genitive_apostrophe(DE_BASE + " Danach geht es zu McDonald's."))
        # Plural-'s' ohne Apostroph (Faux-Plural) ist kein M49-Genitiv
        self.assertIsNone(genitive_apostrophe(DE_BASE + " Die 1980er Jahre gelten als Start."))


class ScoreDiscipline(unittest.TestCase):
    def test_detect_only_never_in_scorer_output(self):
        text = (DE_BASE + " Sie sagte: „das ist so” und meinte, das liege "
                 "bei 2.5 Prozent, was Peters's Rechnung bestätige.")
        import json
        result = slop_scorer.slop_score(text)
        serialized = json.dumps(result)
        for banned in ("QuoteMismatch", "TitleCaseHeadings", "EnNumberFormats",
                       "GenitiveApostrophe", "de_typography"):
            self.assertNotIn(banned, serialized)
        self.assertTrue(find_de_typography(text))  # advisory findings exist

    def test_all_findings_carry_keep_when(self):
        text = DE_BASE + " Sie sagte: „das ist so” und meinte 2.5 Prozent bei Peter's Rechnung."
        for f in find_de_typography(text):
            self.assertIn("keep_when", f)
            self.assertLessEqual(f["confidence"], 0.75)


if __name__ == "__main__":
    unittest.main()
