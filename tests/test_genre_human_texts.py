"""#80-Rest: Genre-Menschtexte (je Genre >= 6 verifizierte Human-Texte).

Neue Korpus-Fixtures (Quelle own:handwritten — handgeschrieben verifiziert,
Pre-LLM-Stil, keine Kopie urheberrechtlich geschützter Texte) für die
unterbesetzten Genres code/generic/nonfiction/news. Alle müssen:
  - < 0.40 auf BEIDEN Engines bleiben (skill scorer + src classifier)
  - im fp_baseline-Register gepinnt sein
  - im Quartals-Re-Score-Verfahren dokumentiert sein (#47-Anbindung)
"""

import json
import os
import subprocess
import sys
import unittest

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CORPUS = os.path.join(ROOT, "eval", "corpus.jsonl")
NEW_IDS_PREFIX = "human-"
MIN_PER_GENRE = 6


def _items():
    with open(CORPUS, encoding="utf-8") as f:
        return [json.loads(l) for l in f if l.strip()]


def _genres():
    return sorted({i["genre"] for i in _items()})


class GenreCoverage(unittest.TestCase):
    def test_every_genre_has_six_plus_clean_human_texts(self):
        counts = {}
        for i in _items():
            if i.get("label") == "clean":
                counts.setdefault(i["genre"], []).append(i)
        for genre in _genres():
            self.assertGreaterEqual(
                len(counts.get(genre, [])), MIN_PER_GENRE, genre)

    def test_new_fixtures_are_own_handwritten(self):
        new = [i for i in _items() if i["id"].startswith(NEW_IDS_PREFIX)]
        self.assertGreaterEqual(len(new), 16)
        for i in new:
            self.assertIn("own:handwritten", i["source"], i["id"])
            self.assertEqual(i["label"], "clean")


class NewFixturesStayClean(unittest.TestCase):
    def test_new_fixtures_below_threshold_both_engines(self):
        sys.path.insert(0, os.path.join(
            ROOT, "skills", "ai-slop-detection", "scripts"))
        sys.path.insert(0, os.path.join(ROOT, "src"))
        import slop_scorer  # noqa: E402
        from classifier import SlopClassifier  # noqa: E402
        clf = SlopClassifier(os.path.join(ROOT, "ontology.json"))
        for i in _items():
            if not i["id"].startswith(NEW_IDS_PREFIX):
                continue
            score = slop_scorer.slop_score(i["text"])["slop_score"]
            self.assertLess(score, 0.40, f"{i['id']}: {score}")
            verdict = clf.classify_text(i["text"])
            self.assertFalse(verdict.is_slop, i["id"])

    def test_new_fixtures_in_fp_baseline(self):
        with open(os.path.join(ROOT, "eval", "fp_baseline.json"),
                  encoding="utf-8") as f:
            baseline = json.load(f)["fixtures"]
        for i in _items():
            if i["id"].startswith(NEW_IDS_PREFIX):
                self.assertIn(i["id"], baseline, i["id"])


class QuarterlyRescoreDoc(unittest.TestCase):
    def test_quarterly_rescore_convention_documented(self):
        with open(os.path.join(ROOT, "docs", "EVALS.md"),
                  encoding="utf-8") as f:
            doc = f.read()
        self.assertIn("Quartals-Re-Score", doc)
        self.assertIn("#47", doc)
        self.assertIn("fp_baseline.py --check", doc)


if __name__ == "__main__":
    unittest.main()
