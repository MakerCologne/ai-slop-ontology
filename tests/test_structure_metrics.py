"""Struktur-Metriken M60/M61 (issue #76 Teil 2, detect-only).

M60 Synonym-Rotation: dieselbe Entitaet wird durch stetig wechselnde
    Bezeichnungen aus einer Synonym-Familie umschrieben (Organisation/
    Autor/Produkt/Nutzer) statt natuerlicher Wiederholung.
M61 Isometrie: Struktureinheiten (Ueberschriften, Listenpunkte,
    Absaetze) haben fast identische Laengen — von Menschen geschriebene
    Texte streuen.

Sprachagnostisch (DE+EN-Familien), detect-only, nie score-dominant.
Konzept aus docs/de-coverage.md (M60/M61, NEU-Kandidaten Prioritaet);
Re-Derivation aus de.wikipedia „Anzeichen fuer KI-generierte Inhalte“
(ueberstrukturierte, formelhafte Gliederung) + eigene Heuristik.
"""

import os
import sys
import unittest

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SCRIPTS = os.path.join(ROOT, "skills", "ai-slop-detection", "scripts")
sys.path.insert(0, SCRIPTS)

from structure_metrics import (  # noqa: E402
    synonym_rotation, isometry, find_structure_findings,
)

DE_BASE = ("Der Ausschuss hat die Zahlen geprüft und festgestellt, dass "
           "weitere Untersuchungen nötig sind, bevor man entscheiden kann, "
           "ob die Maßnahmen greifen oder nicht wirklich helfen werden.")

EN_BASE = ("The committee reviewed the numbers and found that more checks "
           "are needed before anyone can decide whether the measures work "
           "or quietly fail over the following winter months.")

MIN_WORDS = 40


def _pad(text: str, target: int = MIN_WORDS) -> str:
    filler = (" Der Bericht nennt Details und Fristen zu den geprüften "
              "Zahlen sowie Hinweise auf weitere Schritte des Ausschusses.")
    while len(text.split()) < target:
        text += filler
    return text


class M60SynonymRotation(unittest.TestCase):
    def test_positives(self):
        texts = (
            _pad(DE_BASE + " Das Unternehmen, der Konzern, die Firma und "
                  "der Betrieb einigten sich."),
            _pad(EN_BASE + " The company, the firm, the enterprise and the "
                  "business agreed on terms."),
            _pad(DE_BASE + " Der Autor, der Verfasser, der Schreiber und "
                  "die Autorin stritten über Details."),
        )
        for t in texts:
            f = synonym_rotation(t)
            self.assertIsNotNone(f, t)
            self.assertIn("SynonymRotation", f["id"])
            self.assertLessEqual(f["confidence"], 0.55)

    def test_negatives(self):
        for t in (
            _pad(DE_BASE + " Der Betrieb stellte die Lieferung ein."),
            _pad(DE_BASE + " Das Unternehmen einigte sich mit dem Betriebsrat; "
                  "die Belegschaft stimmte zu, der Vorstand schwieg."),
            _pad(EN_BASE + " The company settled with the union; staff "
                  "agreed, the board stayed silent."),
        ):
            self.assertIsNone(synonym_rotation(t), t)

    def test_boundaries(self):
        # Grenze 1: nur 2 verschiedene Familienmitglieder -> kein Fund
        # (FP-Erwartung: natuerliche Abwechslung mit 2 Termen ist normal).
        self.assertIsNone(synonym_rotation(
            _pad(DE_BASE + " Das Unternehmen, also der Konzern, zahlte.")))
        # Grenze 2: 3 Termine, aber kurzer Text (< MIN_WORDS) -> kein Fund.
        self.assertIsNone(synonym_rotation(
            "Die Firma, der Betrieb, das Unternehmen zahlten."))
        with self.subTest("lange Grenzfaelle feuern als advisory"):
            f = synonym_rotation(
                _pad("Die Firma, der Betrieb, das Unternehmen zahlten Steuern."))
            self.assertIsNotNone(f)


class M61Isometry(unittest.TestCase):
    def test_positives(self):
        texts = (
            "# Plan one for the team\n\nAll units drafted with care here.\n\n"
            "# Plan two for staff\n\nEvery unit drafted with care below.\n\n"
            "# Plan three for us\n\nThird unit drafted with care now.\n\n"
            "# Plan four for all\n\nLast unit drafted with care today.",
            "- Erstes Team prüft Zahlen sehr sorgfältig\n"
            "- Zweites Team prüft Texte sehr sorgfältig\n"
            "- Drittes Team prüft Pläne sehr sorgfältig\n"
            "- Viertes Team prüft Fragen sehr sorgfältig\n"
            "- Fünftes Team prüft Listen sehr sorgfältig",
            "Kapitel eins beginnt ganz ruhig mit kleinen Sätzen.\n\n"
            "Kapitel zwei beginnt ganz ruhig mit kurzen Sätzen.\n\n"
            "Kapitel drei beginnt ganz ruhig mit neuen Sätzen.\n\n"
            "Kapitel vier beginnt ganz ruhig mit zwei Sätzen.\n\n"
            "Kapitel fünf beginnt ganz ruhig mit alten Sätzen.",
        )
        for t in texts:
            f = isometry(t)
            self.assertIsNotNone(f, t)
            self.assertIn("IsometricUnits", f["id"])
            self.assertLessEqual(f["confidence"], 0.55)

    def test_negatives(self):
        for t in (
            "# Kurzer Titel\n\nHier steht ein ausführlicher Absatz mit "
            "ganz unterschiedlich langen Sätzen, die mal kurz, mal deutlich "
            "länger ausfallen und verschiedene Details nennen.\n\n"
            "# Ein anderes, deutlich längeres Kapitelthema\n\nKurz.\n\n"
            "# X\n\nUnd noch ein Absatz mittlerer Länge mit wenigen Details.",
            "- Punkt\n- Ein deutlich längerer zweiter Listenpunkt mit Zahl\n"
              "- Kurz\n- Noch ein mittellanger Punkt\n- Ende\n- Weiter\n"
              "- Ein sehr langer letzter Punkt mit vielen Einzelheiten",
            DE_BASE + " " + EN_BASE + " " + DE_BASE,
        ):
            self.assertIsNone(isometry(t), t)

    def test_boundaries(self):
        # Grenze 1: 4 statt 5 Einheiten -> kein Fund (Mindest-Stichprobe).
        self.assertIsNone(isometry(
            "- Erstes Team prüft Zahlen sehr sorgfältig\n"
            "- Zweites Team prüft Texte sehr sorgfältig\n"
            "- Drittes Team prüft Pläne sehr sorgfältig\n"
            "- Viertes Team prüft Fragen sehr sorgfältig"))
        # Grenze 2: 5 Einheiten, aber eine Laenge weicht ab -> kein Fund.
        self.assertIsNone(isometry(
            "- Erstes Team prüft Zahlen sehr sorgfältig\n"
            "- Zweites Team prüft Texte sehr sorgfältig\n"
            "- Drittes Team prüft Pläne sehr sorgfältig\n"
            "- Kurz\n"
            "- Fünftes Team prüft Fragen sehr sorgfältig"))


class Surface(unittest.TestCase):
    def test_find_structure_findings_collects_and_is_detect_only(self):
        t = _pad(DE_BASE + " Die Firma, der Betrieb, das Unternehmen und "
                 "der Konzern zahlten.")
        findings = find_structure_findings(t)
        ids = {f["id"] for f in findings}
        self.assertIn("SynonymRotation", ids)
        for f in findings:
            self.assertIn("keep_when", f)
            self.assertLessEqual(f["confidence"], 0.55)

    def test_german_gate_not_required_for_language_agnostic_signals(self):
        # M60/M61 sind sprachagnostisch: EN-Texte werden genauso geprueft.
        f = synonym_rotation(
            _pad(EN_BASE + " The company, the firm, the enterprise and the "
                  "business agreed."))
        self.assertIsNotNone(f)


if __name__ == "__main__":
    unittest.main()
