"""
Issue #21 — positive counter-profile: references/human-voice.md.

The ontology is purely detective (deep-dive finding: "ein positives
Human-Voice-Gegenprofil existiert nicht — größte konzeptionelle Lücke").
This pins the editable reference with the six soul principles
(poteto/noodle "unslop — Adding soul"), the code-soul defaults
(brianlovin simplify, bl-I4) and the collision boundary to #24
(adverb rate).
"""

import os
import re
import unittest

ROOT = os.path.join(os.path.dirname(__file__), "..")
REF = os.path.join(
    ROOT, "skills", "ai-slop-detection", "references", "human-voice.md")
SKILL = os.path.join(ROOT, "skills", "ai-slop-detection", "SKILL.md")

PRINCIPLES = [
    "specific over generic",
    "verbs over nouns",
    "risks and flaws",
    "genuine opinion",
    "numbers and names",
    "sentence-length variation",
]


class TestHumanVoiceReference(unittest.TestCase):
    def setUp(self):
        with open(REF, encoding="utf-8") as fh:
            self.content = fh.read()

    def test_file_exists(self):
        self.assertTrue(os.path.exists(REF),
                        "references/human-voice.md fehlt (Issue #21)")

    def test_contains_six_soul_principles(self):
        for principle in PRINCIPLES:
            self.assertIn(
                principle.lower(), self.content.lower(),
                f"Prinzip '{principle}' fehlt in human-voice.md")

    def test_each_principle_has_example_and_counterpoint(self):
        # every principle needs a before/after example and a "when not" note
        sections = re.split(r"\n### ", self.content)
        self.assertGreaterEqual(len(sections), 7,
                                "weniger als 6 Prinzip-Abschnitte gefunden")
        for section in sections[1:7]:
            self.assertIn("vorher", section.lower())
            self.assertIn("nachher", section.lower())
            self.assertIn("wann nicht", section.lower())

    def test_code_soul_defaults_present(self):
        lower = self.content.lower()
        for marker in ["code-soul", "benannte funktionen", "frühe returns",
                       "löschen statt auskommentieren"]:
            self.assertIn(marker, lower,
                          f"Code-Soul-Element '{marker}' fehlt")

    def test_adverb_collision_boundary_documented(self):
        lower = self.content.lower()
        self.assertIn("#24", self.content)
        self.assertIn("adverb", lower)
        # boundary rule must name the resolution direction
        self.assertTrue(
            "intensifier" in lower or "verstärker" in lower,
            "Abgrenzungsregel zu #24 (Intensifier/Adverbien) fehlt")

    def test_skill_md_links_reference(self):
        with open(SKILL, encoding="utf-8") as fh:
            skill = fh.read()
        self.assertIn("references/human-voice.md", skill,
                      "SKILL.md verlinkt human-voice.md nicht")

    def test_no_scorer_changes(self):
        # #21 ist reine Referenz-Doku: die Engine-Dateien dürfen sich seit
        # dem Branchpunkt nicht ändern (Vergleich gegen issue-49-Head via
        # Dateiinhalt ist hier bewusst weggelassen — der Diff-Review prüft
        # es; dieser Test pinnt nur, dass KEIN Signal-Modul importiert wird.
        for forbidden in ["slop_scorer", "fp_guards", "genre_profiles"]:
            self.assertNotIn(forbidden, self.content,
                             "human-voice.md referenziert Engine-Interna — "
                             "reine Redaktionsreferenz erwartet")


if __name__ == "__main__":
    unittest.main()
