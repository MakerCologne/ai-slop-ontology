"""DE-Struktur-Signale (issue #76 Backlog NEU-Items, detect-only).

M6  HollowFazitHeading   „## Fazit“-Heading ohne Substanz (< 30 Wörter)
M17 LetterStructure      Briefschablonen-Marker (Betreff/Anrede/Grußformel)
M50 BulletCapitalization EN-Konvention bei DE-Stichpunkt-Phrasen

Alle detect-only, nie score-dominant; DE-Sprachgate schützt englische
Texte. Konzepte re-derivierte Eigenlistung nach de.wikipedia „Anzeichen
für KI-generierte Inhalte“ (Projektseite) + eigene Beispiele — kein
Pattern-Material aus CC BY-SA-Quellen kopiert (vgl. docs/de-coverage.md).
"""

import os
import sys
import unittest

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SCRIPTS = os.path.join(ROOT, "skills", "ai-slop-detection", "scripts")
sys.path.insert(0, SCRIPTS)

from de_structure import (  # noqa: E402
    hollow_fazit_heading, letter_structure, bullet_capitalization,
    find_de_structure,
)

DE_BASE = ("Der Ausschuss hat die Zahlen geprüft und dabei festgestellt, "
           "dass weitere Untersuchungen nötig sind, bevor man entscheiden "
           "kann, ob die Maßnahmen greifen oder nicht wirklich helfen.")


class M6HollowFazitHeading(unittest.TestCase):
    def test_positives(self):
        for t in (
            DE_BASE + "\n\n## Fazit\n\nAlles in allem ein wichtiger Punkt.",
            DE_BASE + "\n\n## Zusammenfassung\n\nKurz gesagt: Es kommt darauf an.",
            DE_BASE + "\n\n### Fazit\n\nGut zu wissen.\n\n## Weiteres Kapitel\n\n" + DE_BASE,
        ):
            f = hollow_fazit_heading(t)
            self.assertIsNotNone(f, t)
            self.assertIn("Wörtern Nachspann", f["evidence"], t)

    def test_negatives(self):
        long_fazit = ("Die Auswertung zeigt, dass die geprüften Maßnahmen "
                      "nicht ausreichen, weil zentrale Voraussetzungen im "
                      "Feld fehlen; künftige Vorhaben sollten daher zuerst "
                      "die Grundlagen klären und erst danach skalieren, "
                      "damit der Effekt messbar bleibt und Ressourcen "
                      "nicht gebunden werden ohne nachweisbaren Nutzen.")
        for t in (
            DE_BASE + "\n\n## Fazit\n\n" + long_fazit,
            DE_BASE + "\n\n## Methodik\n\nKurzer Absatz.",  # falsches Heading
            "The committee found this.\n\n## Fazit\n\nShort recap here.",
        ):
            self.assertIsNone(hollow_fazit_heading(t), t)


class M17LetterStructure(unittest.TestCase):
    def test_positives(self):
        for t in (
            "Betreff: Ihre Anfrage\n\n" + DE_BASE + "\n\nMit freundlichen Grüßen",
            "Sehr geehrte Damen und Herren,\n\n" + DE_BASE +
            "\n\nViele Grüße",
            "Betreff: Bericht\n\nHallo Stefan,\n\n" + DE_BASE,
        ):
            f = letter_structure(t)
            self.assertIsNotNone(f, t)
            self.assertIn("Marker", f["evidence"], t)

    def test_negatives(self):
        for t in (
            DE_BASE,                                        # keine Marker
            DE_BASE + " Wir grüßen alle Beteiligten sehr herzlich.",  # Fließtext
            "Subject: Request\n\nBest regards,\nThe team",  # EN gate
        ):
            self.assertIsNone(letter_structure(t), t)

    def test_single_marker_no_fire(self):
        t = DE_BASE + "\n\nMit freundlichen Grüßen"  # nur 1 Marker-Typ
        self.assertIsNone(letter_structure(t), t)


class M50BulletCapitalization(unittest.TestCase):
    BULLETS = ("- Klare Struktur.\n- Neue Zahlen.\n- Offene Fragen.\n"
               "- Nächste Schritte.\n")

    def test_positives(self):
        for t in (
            DE_BASE + "\n\n" + self.BULLETS,
            DE_BASE + "\n\n* Ein Punkt.\n* Noch ein Punkt.\n"
                      "* Dritter Punkt.\n* Letzter Punkt.\n",
        ):
            f = bullet_capitalization(t)
            self.assertIsNotNone(f, t)
            self.assertIn("EN-", f["evidence"], t)

    def test_negatives(self):
        for t in (
            DE_BASE + "\n\n- klare struktur\n- neue zahlen\n"
                      "- offene fragen\n- nächste schritte\n",   # dt. Konvention
            DE_BASE + "\n\n- Ein Punkt\n- Noch ein Punkt\n"      # kein Endpunkt
                      "- Dritter Punkt\n- Letzter Punkt\n",
            DE_BASE + "\n\n- Klare Struktur.\n- Neue Zahlen.\n",  # < 4 Items
            "The team found this.\n\n- Clear structure.\n"        # EN gate
            "- New numbers.\n- Open questions.\n- Next steps.\n",
        ):
            self.assertIsNone(bullet_capitalization(t), t)


class Aggregator(unittest.TestCase):
    BULLETS = M50BulletCapitalization.BULLETS

    def test_find_de_structure_combines(self):
        t = ("Betreff: Bericht\n\n" + DE_BASE + "\n\n## Fazit\n\nKurz.\n\n"
             "Viele Grüße\n\n" + self.BULLETS)
        ids = {f["id"] for f in find_de_structure(t)}
        self.assertEqual(ids, {"HollowFazitHeading", "LetterStructure",
                               "BulletCapitalization"})

    def test_english_text_empty(self):
        self.assertEqual(find_de_structure("## Fazit\n\nShort.\n\nBetreff: x"),
                         [])


if __name__ == "__main__":
    unittest.main()
