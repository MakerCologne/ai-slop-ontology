"""
Numbers the documentation asserts about the data must match the data.

The skill advertised "459 signals" against a database of 233, the README
counted 38 references where the file lists 39, and REFERENCES.md still carried
the v1.1.0 heading two releases later (review 2026-08 §3.1).
"""

import json
import os
import re
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "src"))

from classifier import SlopClassifier


def read(name):
    return (ROOT / name).read_text(encoding="utf-8")


class TestSignalCountClaims(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.stats = SlopClassifier(str(ROOT / "ontology.json")).get_signal_stats()

    def test_skill_states_the_real_signal_count(self):
        skill = read("skills/ai-slop-detection/SKILL.md")
        claimed = re.search(r"Full ontology \((\d+) scored text signals", skill)
        self.assertIsNotNone(claimed, "SKILL.md no longer states a signal count")
        self.assertEqual(int(claimed.group(1)), self.stats["total_signals"])

    def test_skill_breakdown_matches(self):
        skill = read("skills/ai-slop-detection/SKILL.md")
        for count, label in re.findall(r"(\d+) (buzzwords|phrases|structural|punctuation)", skill):
            actual = {"buzzwords": self.stats["buzzwords"],
                      "phrases": self.stats["total_phrases"],
                      "structural": self.stats["structural_indicators"],
                      "punctuation": self.stats["punctuation_indicators"]}[label]
            self.assertEqual(int(count), actual, f"{label} count in SKILL.md")


class TestReferenceClaims(unittest.TestCase):
    def test_readme_reference_count_matches_the_file(self):
        actual = len(re.findall(r"^\d+\. ", read("REFERENCES.md"), re.MULTILINE))
        claimed = re.search(r"Source list \((\d+) references\)", read("README.md"))
        self.assertIsNotNone(claimed)
        self.assertEqual(int(claimed.group(1)), actual)

    def test_references_heading_carries_the_current_version(self):
        version = re.search(r'^version: "([^"]+)"', read("AI-SLOP-ONTOLOGY.md"),
                            re.MULTILINE).group(1)
        heading = read("REFERENCES.md").splitlines()[0]
        self.assertIn(version, heading,
                      f"REFERENCES.md heading is stale: {heading!r}")


class TestOntologyMetadata(unittest.TestCase):
    def test_signal_database_version_is_explained(self):
        """signals.version differs from the ontology version — on purpose."""
        signals = json.loads(read("ontology.json"))["signals"]
        self.assertIn("version", signals)
        self.assertIn("maintained independently", signals["note"])


if __name__ == "__main__":
    unittest.main()
