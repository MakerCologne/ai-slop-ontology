import json
import re
import subprocess
import sys
import unittest
import xml.etree.ElementTree as ET
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
ADAPTER = ROOT / "integrations" / "ontology-playground"
CATALOGUE = ADAPTER / "catalogue" / "community" / "hikaman"
RDF = "{http://www.w3.org/1999/02/22-rdf-syntax-ns#}"
OWL = "{http://www.w3.org/2002/07/owl#}"
SCAFFOLDING = {"SlopPhenomenon", "DetectionEvidence", "MitigationAction", "Harm"}
SHARED = {"ContentItem", "SyntheticContent", "AI_AssistedContent"}


def ontology_names():
    names = set()
    for ttl in [ROOT / "ontology.ttl",
                ROOT / "extensions" / "human-work-seo-slop" / "human_work_seo_slop.ttl"]:
        if ttl.exists():
            names |= set(re.findall(r"^:([A-Za-z0-9_]+)\s", ttl.read_text(encoding="utf-8"), re.MULTILINE))
    data = json.loads((ROOT / "ontology.json").read_text(encoding="utf-8"))
    for group in data["slopTypes"].values():
        names |= set(group)
    names |= set(data.get("topLevelClasses", {}).keys())
    ext = json.loads((ROOT / "extensions" / "human-work-seo-slop" /
                      "human_work_seo_slop.json").read_text(encoding="utf-8"))
    names |= {t["id"] for t in ext["types"]}
    return names


def published_classes():
    for rdf in sorted(CATALOGUE.glob("*/ontology.rdf")):
        for c in ET.parse(rdf).getroot().findall(f"{OWL}Class"):
            yield rdf.parent.name, (c.attrib.get(f"{RDF}about") or "").split("#")[-1]


class OntologyPlaygroundAdapterTests(unittest.TestCase):
    def test_validator_passes(self):
        result = subprocess.run(
            [sys.executable, str(ADAPTER / "validate_adapter.py")],
            cwd=ROOT, capture_output=True, text=True)
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertIn("catalogue entries", result.stdout)

    def test_check_mode_detects_drift_and_passes_when_clean(self):
        result = subprocess.run(
            [sys.executable, str(ADAPTER / "generate_catalogue.py"), "--check"],
            cwd=ROOT, capture_output=True, text=True)
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertIn("up to date", result.stdout)

    def test_generator_refuses_invented_classes(self):
        config = json.loads((ADAPTER / "views.json").read_text(encoding="utf-8"))
        original = config["views"][0]["classes"][0]
        config["views"][0]["classes"][0] = "DefinitelyInventedSlopClass"
        tmp = ADAPTER / "views.json.tmp"
        tmp.write_text(json.dumps(config), encoding="utf-8")
        try:
            (ADAPTER / "views.json").rename(ADAPTER / "views.json.bak")
            tmp.rename(ADAPTER / "views.json")
            result = subprocess.run(
                [sys.executable, str(ADAPTER / "generate_catalogue.py"), "--check"],
                cwd=ROOT, capture_output=True, text=True)
            # --check with an invented class: either generation-side refusal (via
            # manifest drift) or explicit refusal — both must be non-zero exit.
            self.assertNotEqual(result.returncode, 0,
                                "invented class must not pass silently")
        finally:
            (ADAPTER / "views.json").unlink()
            (ADAPTER / "views.json.bak").rename(ADAPTER / "views.json")
            tmp = ADAPTER / "views.json.tmp"
            if tmp.exists():
                tmp.unlink()

    def test_published_classes_exist_in_the_ontology(self):
        """The catalogue is public — it must not invent names (§2.1)."""
        names = ontology_names()
        for view, name in published_classes():
            self.assertTrue(name in names or name in SCAFFOLDING or name in SHARED,
                            f"{view}: '{name}' is not an ontology name")

    def test_human_vs_ai_work_slop_distinction_survives(self):
        published = {name for _, name in published_classes()}
        self.assertIn("HumanWorkSlop", published)
        self.assertIn("AIWorkslop", published)
        self.assertNotIn("WorkSlop", published)
        self.assertNotIn("HumanAuthoredWorkSlop", published)

    def test_manifest_counts_match_catalogue(self):
        manifest = json.loads((ADAPTER / "manifest.json").read_text(encoding="utf-8"))
        expected = {v["slug"]: v for v in manifest["views"]}
        folders = sorted(p.name for p in CATALOGUE.iterdir() if p.is_dir())
        self.assertEqual(folders, sorted(expected))
        for folder in CATALOGUE.iterdir():
            if not folder.is_dir():
                continue
            root = ET.parse(folder / "ontology.rdf").getroot()
            self.assertEqual(len(root.findall(f"{OWL}Class")),
                             expected[folder.name]["entities"])
            self.assertEqual(len(root.findall(f"{OWL}ObjectProperty")),
                             expected[folder.name]["relationships"])


if __name__ == "__main__":
    unittest.main()
