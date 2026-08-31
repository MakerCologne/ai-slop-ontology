"""Issue #104, Slice A — Doc-Drift zwischen skills/ai-slop-detection/
references/detection-signals.md und dem SSOT (ontology.json).

Zwei dokumentierte Luecken, die der neue Doc-SSOT-Gate
(scripts/check_doc_signals.py) absichert:

1. "it is worth noting" (unkontrahiert) fehlt in hedging_qualifiers —
   nur die Kontraktion "it's worth noting" ist im SSOT.
2. Template-Form "in today's [X]" fehlt in opening_formulas — im SSOT
   stehen nur konkrete Varianten ("in today's digital age" u.a.), obwohl
   die TypePattern-/Platzhalter-Mechanik (#83/#88) Templates matchen kann.

Die Issue-Beispieltexte muessen nach dem Fix Treffer liefern (RED zuerst,
dann GREEN — Test-Integritaet: Tests werden vor der Implementierung
eingefroren und committet).
"""

import json
import os
import subprocess
import sys
import unittest

ROOT = os.path.join(os.path.dirname(__file__), "..")
sys.path.insert(0, os.path.join(ROOT, "src"))

from classifier import SlopClassifier
from scorer import find_term_matches

ONTOLOGY = os.path.join(ROOT, "ontology.json")
DOC_GATE = os.path.join(ROOT, "scripts", "check_doc_signals.py")

# Issue-Beispiele (wuertlich aus #104)
GAP1_TEXT = "It is worth noting that the migration took eleven minutes."
GAP2_TEXT = "In today's fast-paced digital landscape, results matter."


class TestGap1UncontractedWorthNoting(unittest.TestCase):
    """Luecke 1: 'it is worth noting' muss im SSOT stehen und matchen."""

    @classmethod
    def setUpClass(cls):
        with open(ONTOLOGY, encoding="utf-8") as fh:
            cls.ontology = json.load(fh)
        cls.clf = SlopClassifier(ONTOLOGY)

    def test_ssot_contains_uncontracted_form(self):
        items = (self.ontology["signals"]["text"]["phrases"]["categories"]
                    ["hedging_qualifiers"]["items"])
        self.assertIn("it is worth noting", [i.lower() for i in items])

    def test_issue_example_matches_hedging_category(self):
        phrase_hits = find_term_matches(
            GAP1_TEXT.lower(), ["it is worth noting"])
        self.assertIn("it is worth noting", phrase_hits)

    def test_issue_example_classifier_hit(self):
        result = self.clf.classify_text(GAP1_TEXT)
        hit_cats = result.phrase_report.get("hedging_qualifiers", [])
        self.assertIn("it is worth noting", hit_cats)


class TestGap2TemplateInTodaysX(unittest.TestCase):
    """Luecke 2: Template 'in today's [X]' statt Varianten-Stapel."""

    @classmethod
    def setUpClass(cls):
        with open(ONTOLOGY, encoding="utf-8") as fh:
            cls.ontology = json.load(fh)
        cls.clf = SlopClassifier(ONTOLOGY)

    def test_ssot_contains_template_form(self):
        items = (self.ontology["signals"]["text"]["phrases"]["categories"]
                    ["opening_formulas"]["items"])
        self.assertIn("in today's [x]", [i.lower() for i in items])

    def test_issue_example_matches_template(self):
        phrase_hits = find_term_matches(
            GAP2_TEXT.lower(), ["in today's [x]"])
        self.assertIn("in today's [x]", phrase_hits)

    def test_issue_example_classifier_hit(self):
        result = self.clf.classify_text(GAP2_TEXT)
        hit_cats = result.phrase_report.get("opening_formulas", [])
        self.assertIn("in today's [x]", hit_cats)

    def test_template_keeps_concrete_variants(self):
        # Die konkreten SSOT-Varianten bleiben matchbar (kein Ersatz, nur
        # Ergaenzung) — Overlap-Suppression zaehlt die laengste Form.
        phrase_hits = find_term_matches(
            "in today's digital age".lower(),
            ["in today's [x]", "in today's digital age"])
        self.assertIn("in today's digital age", phrase_hits)


class TestDocSsotGate(unittest.TestCase):
    """DoD 1: Doku<->SSOT-Gate als Skript, beide Richtungen, gruen."""

    def test_gate_passes(self):
        proc = subprocess.run(
            [sys.executable, DOC_GATE], capture_output=True, text=True)
        self.assertEqual(
            proc.returncode, 0,
            f"Doc-SSOT-Gate rot:\n{proc.stdout}\n{proc.stderr}")


if __name__ == "__main__":
    unittest.main()
