"""Tests for the benchmark runner genre breakdown (issue #41).

TDD Red: run_benchmark must report per-genre false-positive rates, and the
enlarged labeled corpus (>= 300 lines) must follow the sourcing discipline
(>= 60% of the lines added after v1.8.0 backed by deep-research artifacts).
"""

import json
import os
import sys
import tempfile
import unittest

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, "eval"))

import run_benchmark  # noqa: E402

CORPUS = os.path.join(ROOT, "eval", "corpus.jsonl")


def write_fixture(path, items):
    with open(path, "w", encoding="utf-8") as f:
        for item in items:
            f.write(json.dumps(item, ensure_ascii=False) + "\n")


class BenchmarkRunnerFixtureTests(unittest.TestCase):
    """Runner behaviour verified against a tiny hand-computed fixture."""

    @classmethod
    def setUpClass(cls):
        cls.tmp = tempfile.mkdtemp(prefix="bm-fixture-")
        cls.fixture = os.path.join(cls.tmp, "fixture.jsonl")
        write_fixture(cls.fixture, [
            # slop in genre "generic" -> TP
            {"id": "f1", "label": "slop", "lang": "en", "type": "GenericSlop",
             "genre": "generic", "text": "Let's dive in! It's worth noting that "
             "harnessing robust, seamless platforms is a game-changer. At the end "
             "of the day, the possibilities are endless."},
            # clean in genre "generic" -> TN
            {"id": "f2", "label": "clean", "lang": "en", "type": "TechnicalDoc",
             "genre": "technical", "text": "The daemon reloads its config when it "
             "receives SIGHUP. Logs are written to /var/log/daemon.log."},
            # clean in genre "legal" that scores >= threshold -> FP
            {"id": "f3", "label": "clean", "lang": "en", "type": "LegalWriting",
             "genre": "legal", "text": "It's worth noting that harnessing robust, "
             "seamless platforms is a game-changer. Let's dive in! At the end of "
             "the day, the possibilities are endless."},
            # slop in genre "marketing" that scores < threshold -> FN
            {"id": "f4", "label": "slop", "lang": "en", "type": "GenericSlop",
             "genre": "marketing", "text": "We ship."},
        ])
        cls.results = run_benchmark.run(cls.fixture, threshold=0.40)

    def test_three_engines_evaluated(self):
        self.assertEqual(len(self.results), 3)

    def test_engine_metrics_match_hand_computation(self):
        # For any engine scoring f1/f3 as slop and f2/f4 as clean the counts
        # must be TP=1 FP=1 TN=1 FN=1 and derived metrics must follow.
        for r in self.results:
            self.assertEqual((r["tp"], r["fp"], r["tn"], r["fn"]), (1, 1, 1, 1))
            self.assertAlmostEqual(r["precision"], 0.5)
            self.assertAlmostEqual(r["recall"], 0.5)
            self.assertAlmostEqual(r["f1"], 0.5)
            self.assertAlmostEqual(r["accuracy"], 0.5)

    def test_genre_breakdown_reports_fp_rate_per_genre(self):
        for r in self.results:
            per_genre = r["per_genre"]
            # generic: only the slop item, correctly flagged -> TP, and no
            # clean item -> fp_rate intentionally undefined (not 0.0)
            self.assertEqual(per_genre["generic"]["tp"], 1)
            self.assertNotIn("fp_rate", per_genre["generic"])
            # legal: one clean item, incorrectly flagged -> fp_rate 1.0
            self.assertEqual(per_genre["legal"]["fp"], 1)
            self.assertAlmostEqual(per_genre["legal"]["fp_rate"], 1.0)
            # technical: clean, not flagged -> fp_rate 0.0
            self.assertAlmostEqual(per_genre["technical"]["fp_rate"], 0.0)
            # marketing has no clean item -> no fp_rate claim (None)
            self.assertNotIn("fp_rate", per_genre["marketing"])
            self.assertEqual(per_genre["marketing"]["fn"], 1)

    def test_genre_breakdown_fp_rate_denominator_is_clean_items(self):
        for r in self.results:
            self.assertEqual(r["per_genre"]["legal"]["n_clean"], 1)
            self.assertEqual(r["per_genre"]["generic"]["n_clean"], 0)

    def test_items_without_genre_are_grouped_as_unspecified(self):
        path = os.path.join(self.tmp, "nogenre.jsonl")
        write_fixture(path, [
            {"id": "g1", "label": "clean", "lang": "en", "type": "TechnicalDoc",
             "text": "See section 4.2 for the retry behaviour."},
        ])
        results = run_benchmark.run(path, threshold=0.40)
        for r in results:
            self.assertIn("unspecified", r["per_genre"])


class CorpusFileDisciplineTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        with open(CORPUS, encoding="utf-8") as f:
            cls.items = [json.loads(l) for l in f if l.strip()]

    def test_corpus_has_at_least_300_lines(self):
        self.assertGreaterEqual(len(self.items), 300)

    def test_every_line_has_required_fields(self):
        for item in self.items:
            self.assertIn(item["label"], ("slop", "clean"), item.get("id", "?"))
            for field in ("id", "label", "lang", "type", "text", "genre"):
                self.assertIn(field, item, item.get("id", "?"))
            self.assertTrue(item["text"].strip(), item["id"])
            # ids unique
        self.assertEqual(len({i["id"] for i in self.items}), len(self.items))

    def test_majority_of_corpus_is_sourced_not_handcrafted(self):
        # >= 60% of all lines must carry a non-handcrafted source (deep-research
        # artifact provenance); handcrafted lines must say so explicitly.
        sourced = [i for i in self.items
                   if i.get("source") and "handcrafted" not in i["source"]]
        handcrafted = [i for i in self.items
                       if i.get("source") and "handcrafted" in i["source"]]
        self.assertEqual(len(sourced) + len(handcrafted), len(self.items),
                         "every corpus line must carry a source field")
        self.assertGreaterEqual(
            len(sourced) / len(self.items), 0.6,
            f"sourced share {len(sourced)}/{len(self.items)} below 60%")

    def test_sourced_lines_cite_a_deep_artifact(self):
        for item in self.items:
            src = item.get("source", "")
            if "handcrafted" not in src:
                self.assertRegex(src, r"deep/\d{2}-")

    def test_clean_genres_cover_the_required_hard_negative_genres(self):
        genres = {i["genre"] for i in self.items if i["label"] == "clean"}
        for required in ("legal", "academic", "marketing", "technical",
                         "recipe", "lyric", "config"):
            self.assertIn(required, genres)

    def test_runner_on_real_corpus_reports_genre_breakdown(self):
        results = run_benchmark.run(CORPUS, threshold=0.40)
        for r in results:
            self.assertIsInstance(r["per_genre"], dict)
            self.assertTrue(r["per_genre"])
            for genre, stats in r["per_genre"].items():
                if "fp_rate" in stats:
                    self.assertGreaterEqual(stats["fp_rate"], 0.0)
                    self.assertLessEqual(stats["fp_rate"], 1.0)


if __name__ == "__main__":
    unittest.main()
