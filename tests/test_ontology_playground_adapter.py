import json
import re
import subprocess
import sys
import unittest
import xml.etree.ElementTree as ET
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CATALOGUE = ROOT / "integrations" / "ontology-playground" / "catalogue" / "community" / "hikaman"
RDF = "{http://www.w3.org/1999/02/22-rdf-syntax-ns#}"
OWL = "{http://www.w3.org/2002/07/owl#}"


def published_classes():
    for rdf in sorted(CATALOGUE.glob("*/ontology.rdf")):
        for c in ET.parse(rdf).getroot().findall(f"{OWL}Class"):
            yield rdf.parent.name, (c.attrib.get(f"{RDF}about") or "").split("#")[-1]


class OntologyPlaygroundAdapterTests(unittest.TestCase):
    def test_adapter_structure_and_manifest(self):
        validator = ROOT / "integrations" / "ontology-playground" / "validate_adapter.py"
        result = subprocess.run(
            [sys.executable, str(validator)],
            cwd=ROOT, capture_output=True, text=True)
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertIn("7 catalogue entries", result.stdout)
        self.assertIn("checked against the ontology", result.stdout)

    def test_published_classes_exist_in_the_ontology(self):
        """The catalogue is public — it must not invent names (§2.1)."""
        names = set(re.findall(r"^:([A-Za-z0-9_]+)\s",
                               (ROOT / "ontology.ttl").read_text(encoding="utf-8"),
                               re.MULTILINE))
        ext = json.loads((ROOT / "extensions" / "human-work-seo-slop" /
                          "human_work_seo_slop.json").read_text(encoding="utf-8"))
        names |= {t["id"] for t in ext["types"]}
        names |= set(re.findall(r"^:([A-Za-z0-9_]+)\s",
                                (ROOT / "extensions" / "human-work-seo-slop" /
                                 "human_work_seo_slop.ttl").read_text(encoding="utf-8"),
                                re.MULTILINE))
        scaffolding = {"SlopPhenomenon", "DetectionEvidence", "MitigationAction", "Harm"}
        for view, name in published_classes():
            self.assertTrue(name in names or name in scaffolding,
                            f"{view}: '{name}' is not an ontology name")

    def test_workslop_distinction_survives_in_the_catalogue(self):
        """WorkSlopFamily vs AIWorkslop must not be flattened again."""
        published = {name for _, name in published_classes()}
        self.assertIn("WorkSlopFamily", published)
        self.assertIn("AIWorkslop", published)
        self.assertNotIn("WorkSlop", published)
        self.assertNotIn("HumanAuthoredWorkSlop", published)

    def test_identifiers_use_readable_camel_case(self):
        """'sEOSlopId' style acronym mangling must not come back."""
        for rdf in sorted(CATALOGUE.glob("*/ontology.rdf")):
            text = rdf.read_text(encoding="utf-8")
            self.assertEqual(
                sorted(set(re.findall(r"\b[a-z][A-Z][A-Za-z]*", text))), [],
                f"{rdf.parent.name}: mangled identifier casing")


if __name__ == "__main__":
    unittest.main()
