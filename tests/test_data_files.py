"""Sanity checks for the machine-readable data files."""

import json
import os
import unittest

ROOT = os.path.join(os.path.dirname(__file__), "..")


class TestOntologyJson(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        with open(os.path.join(ROOT, "ontology.json")) as f:
            cls.o = json.load(f)

    def test_new_slop_types_present(self):
        domain = self.o["slopTypes"]["DOMAIN_SLOP"]
        self.assertIn("SecurityReportSlop", domain)
        self.assertIn("PeerReviewSlop", domain)

    def test_newsguard_stats_current(self):
        ng = self.o["platformStats"]["newsguard"]
        self.assertEqual(ng["aiContentFarmSites"], 3749)

    def test_signal_db_structure(self):
        text = self.o["signals"]["text"]
        self.assertIn("buzzwords", text)
        self.assertIn("phrases", text)
        for tier in text["buzzwords"]["tiers"].values():
            self.assertIn("words", tier)
            self.assertIsInstance(tier["words"], list)

    def test_formatting_indicator_ids(self):
        # issue #16: refined formatting-slop indicators present
        ids = [i["id"] for i in self.o["signals"]["text"]["punctuation"]["indicators"]]
        for wanted in ("TitleCaseHeadings", "CurlyQuotes", "HyphenatedPairRate", "BoldMidSentence"):
            self.assertIn(wanted, ids)

    def test_hyper_typicality_signal(self):
        ids = [i.get("id") for i in self.o["signals"]["image"]["indicators"]]
        self.assertIn("HyperTypicality", ids)

    def test_multilingual_languages(self):
        multi = self.o["signals"]["multilingual"]
        langs = [k for k, v in multi.items()
                 if isinstance(v, dict) and "buzzwords" in v]
        self.assertEqual(
            sorted(langs),
            ["french", "german", "hindi", "spanish", "urdu", "vietnamese"],
        )


class TestYamlOntology(unittest.TestCase):
    def test_yaml_parses_and_versioned(self):
        try:
            import yaml
        except ImportError:
            self.skipTest("pyyaml not installed")
        import re
        with open(os.path.join(ROOT, "ai_slop_ontology.yaml")) as f:
            data = yaml.safe_load(f)
        # Version must be semver and match the canonical document's front
        # matter (scripts/check_consistency.py enforces the same invariant).
        self.assertRegex(data["ontology"]["version"], r"^\d+\.\d+\.\d+$")
        with open(os.path.join(ROOT, "AI-SLOP-ONTOLOGY.md")) as f:
            md_version = re.search(r'^version: "([^"]+)"', f.read(), re.MULTILINE)
        self.assertEqual(data["ontology"]["version"], md_version.group(1))
        self.assertIn("empirical_updates_2026_07", data["ontology"])


class TestDatasetSeeds(unittest.TestCase):
    """Issue #124: seed registry for the labeled corpus (BS-I2)."""

    @classmethod
    def setUpClass(cls):
        with open(os.path.join(ROOT, "eval", "dataset_seeds.json")) as f:
            cls.seeds = json.load(f)

    def test_schema(self):
        self.assertEqual(self.seeds["schema_version"], 1)
        self.assertEqual(self.seeds["issue"], 124)
        for key in ("purpose", "selection_rules", "datasets", "gaps"):
            self.assertIn(key, self.seeds)

    def test_selection_rules_pinned(self):
        rules = self.seeds["selection_rules"]
        self.assertGreaterEqual(len(rules), 5)
        self.assertTrue(any("license" in r.lower() for r in rules))
        self.assertTrue(any("dedup" in r.lower() for r in rules))

    def test_every_dataset_has_required_fields(self):
        ids = []
        for ds in self.seeds["datasets"]:
            for key in ("id", "source", "label", "label_mapping", "license", "preference", "risks"):
                self.assertIn(key, ds, f"dataset {ds.get('id')} missing {key}")
            self.assertIn(ds["label"], ("ai", "human", "both"))
            self.assertIn(ds["preference"], ("high", "medium", "low"))
            self.assertIsInstance(ds["risks"], list)
            self.assertTrue(ds["risks"])
            ids.append(ds["id"])
        self.assertEqual(len(ids), len(set(ids)), "duplicate dataset ids")

    def test_license_policy_enforced_in_manifest(self):
        # selection rule 3: no-license datasets must not be high preference
        for ds in self.seeds["datasets"]:
            lic = ds["license"].lower()
            if "none" in lic or "unverified" in lic:
                self.assertNotEqual(
                    ds["preference"], "high",
                    f"{ds['id']}: no/unclear license must not be high preference")


class TestExamples(unittest.TestCase):
    def test_example_files_parse(self):
        exdir = os.path.join(ROOT, "examples")
        for name in os.listdir(exdir):
            if name.endswith(".json"):
                with open(os.path.join(exdir, name)) as f:
                    json.load(f)


if __name__ == "__main__":
    unittest.main()
