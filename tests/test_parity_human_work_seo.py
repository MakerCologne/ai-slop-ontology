"""Parity-Check: extensions/human-work-seo-slop JSON ↔ TTL (Issue #86, DoD-Punkt 2).

Detect-only-Niveau: jede in der JSON-Extension deklarierte Klasse (types +
candidates) muss als owl:Class in der TTL-Fassung existieren und umgekehrt —
keine Seite darf Klassen erfinden, die der anderen fehlen. Dimensionen sind
JSON-only (Datenfelder), keine Paritätspflicht.
"""

import json
import os
import re
import unittest

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
BASE = os.path.join(ROOT, "extensions", "human-work-seo-slop")
EXT_JSON = os.path.join(BASE, "human_work_seo_slop.json")
EXT_TTL = os.path.join(BASE, "human_work_seo_slop.ttl")


class ParityHumanWorkSEOTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        with open(EXT_JSON, encoding="utf-8") as f:
            cls.data = json.load(f)
        with open(EXT_TTL, encoding="utf-8") as f:
            cls.ttl = f.read()
        # ":ClassName a owl:Class" — Wortgrenze verhindert Prefix-Verwechslung
        cls.ttl_classes = set(re.findall(r"^:(\w+) a owl:Class", cls.ttl, re.M))

    def json_class_ids(self):
        # candidates sind bewusst nicht befördert (Status 'candidate') und
        # haben daher kein TTL-Gegenstück — Paritätspflicht nur für types.
        return {t["id"] for t in self.data["types"]}

    def test_json_classes_exist_in_ttl(self):
        missing = self.json_class_ids() - self.ttl_classes
        self.assertEqual(missing, set(), f"JSON-Klassen ohne TTL-Gegenstück: {missing}")

    def test_ttl_classes_exist_in_json(self):
        # Header-Ontologie-Klasse, Dimension-Metaklasse und externe Kerne
        # sind keine Fachklassen dieser Extension
        core_external = {"SlopFamily", "ContentItemOrWorkActivity", "HumanSlop",
                         "WorkSlopFamily", "SEOSlop", "Dimension"}
        ttl_content = self.ttl_classes - core_external - {"HumanWorkSEOSlopExtension"}
        missing = ttl_content - self.json_class_ids()
        self.assertEqual(missing, set(), f"TTL-Klassen ohne JSON-Gegenstück: {missing}")

    def test_no_score_coupling_detect_only(self):
        """DoD/adr-0009: Extension darf nicht in den Scorer importiert werden."""
        src_dir = os.path.join(ROOT, "src")
        for fname in os.listdir(src_dir):
            if not fname.endswith(".py"):
                continue
            with open(os.path.join(src_dir, fname), encoding="utf-8") as f:
                self.assertNotIn(
                    "human_work_seo_slop",
                    f.read(),
                    f"src/{fname} importiert die Extension — verletzt detect-only (adr/0009)",
                )


if __name__ == "__main__":
    unittest.main()
