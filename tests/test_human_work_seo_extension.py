import json
import os
import unittest


ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
BASE = os.path.join(ROOT, "extensions", "human-work-seo-slop")
EXTENSION = os.path.join(BASE, "human_work_seo_slop.json")
EXAMPLES = os.path.join(BASE, "examples.json")

ALLOWED_STATUSES = {"established", "emerging", "grounded_extension", "candidate"}
EXTERNAL_CLASSES = {"ContentItem", "ContentItemOrWorkActivity", "SlopFamily"}


class HumanWorkSEOExtensionTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        with open(EXTENSION, encoding="utf-8") as f:
            cls.data = json.load(f)
        with open(EXAMPLES, encoding="utf-8") as f:
            cls.examples = json.load(f)["examples"]

    def test_type_ids_are_unique(self):
        ids = [item["id"] for item in self.data["types"]]
        self.assertEqual(len(ids), len(set(ids)))

    def test_statuses_are_explicit(self):
        for item in self.data["types"]:
            self.assertIn(item["status"], ALLOWED_STATUSES)

    def test_all_parents_resolve(self):
        core = {"HumanSlop", "WorkSlopFamily", "SEOSlop"}
        known = core | {item["id"] for item in self.data["types"]} | EXTERNAL_CLASSES
        unresolved = []
        for item in self.data["types"]:
            for parent in item["parents"]:
                if parent not in known:
                    unresolved.append((item["id"], parent))
        self.assertEqual(unresolved, [])

    def test_sources_resolve(self):
        source_ids = set(self.data["sources"])
        missing = []
        for item in self.data["types"]:
            for source_id in item["sources"]:
                if source_id not in source_ids:
                    missing.append((item["id"], source_id))
        self.assertEqual(missing, [])

    def test_every_type_has_false_positive_exclusion(self):
        for item in self.data["types"]:
            self.assertTrue(item["exclusion"], item["id"])

    def test_workslop_meaning_is_preserved(self):
        ai = next(item for item in self.data["types"] if item["id"] == "AIWorkslop")
        self.assertEqual(ai["status"], "established")
        self.assertEqual(ai["generation"], "AI")
        self.assertIn("ai_assisted", self.data["rules"]["AIWorkslop"])

    def test_human_and_ai_generation_are_not_collapsed(self):
        self.assertIn("human_authored", self.data["rules"]["HumanWorkSlop"])
        self.assertNotIn("fully_synthetic", self.data["rules"]["HumanWorkSlop"])
        self.assertIn("fully_synthetic", self.data["rules"]["AIWorkslop"])

    def test_seo_slop_is_generation_neutral(self):
        self.assertIn("generation mode irrelevant", self.data["rules"]["SEOSlop"])
        seo_types = [item for item in self.data["types"] if "SEOSlop" in item["parents"]]
        self.assertGreaterEqual(len(seo_types), 6)
        self.assertTrue(all(item["generation"] == "neutral" for item in seo_types))

    def test_candidates_are_not_promoted(self):
        stable_ids = {item["id"] for item in self.data["types"]}
        self.assertFalse(stable_ids.intersection(self.data["candidates"]))

    def test_examples_reference_known_types(self):
        known = {"HumanSlop", "WorkSlopFamily", "SEOSlop"} | {
            item["id"] for item in self.data["types"]
        }
        unknown = [item["label"] for item in self.examples if item["label"] not in known]
        self.assertEqual(unknown, [])

    def test_examples_include_counterexamples(self):
        outcomes = {item["expected"] for item in self.examples}
        self.assertIn("candidate", outcomes)
        self.assertIn("not_slop", outcomes)


if __name__ == "__main__":
    unittest.main()
