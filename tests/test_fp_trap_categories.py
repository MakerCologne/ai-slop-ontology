"""FP-trap category coverage (GL#4 / GitHub mirror #1074, Batch E 2026-10-01).

The clean side of the corpus had no FP traps for whole style families that
"sound like slop" but are human (or disclosed AI-assisted + edited):

  - ShortMessage      very short texts (email/commit/chat one-liners)
  - Checklist         list-heavy human style (runbooks, notes, shopping)
  - EmDashProse       "guter Stil, der wie Slop klingt" (em-dash lovers)
  - MixedLanguage     bilingual mixed texts (DE/EN, FR/EN)
  - AIAssistedReviewed editorially reviewed, disclosed AI-assisted texts

This gate pins the presence AND the clean verdict of every item in these
categories, so a future corpus cleanup cannot silently drop the FP traps
again (0 FP was a corpus deficit, not engine strength — GL#4).
"""

import json
import os
import sys
import unittest

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, "skills", "ai-slop-detection", "scripts"))
sys.path.insert(0, os.path.join(ROOT, "src"))

from threshold_config import load_threshold  # noqa: E402
import slop_scorer  # noqa: E402

CORPUS = os.path.join(ROOT, "eval", "corpus.jsonl")
THRESHOLD = load_threshold()

MIN_PER_CATEGORY = 3
TYPE_CATEGORIES = ("ShortMessage", "Checklist", "MixedLanguage",
                   "AIAssistedReviewed")


def _clean_items():
    with open(CORPUS, encoding="utf-8") as f:
        return [json.loads(line) for line in f
                if line.strip() and json.loads(line).get("label") == "clean"]


class FPTrapCategoryCoverage(unittest.TestCase):
    def test_all_type_categories_present(self):
        items = _clean_items()
        for cat in TYPE_CATEGORIES:
            n = sum(1 for i in items if i.get("type") == cat)
            self.assertGreaterEqual(
                n, MIN_PER_CATEGORY,
                f"FP-trap category {cat}: only {n} clean items "
                f"(need >={MIN_PER_CATEGORY}, GL#4 Batch E)")

    def test_em_dash_prose_traps_present(self):
        # Em-dash lovers: >=3 clean items with >=2 em-dashes each
        n = sum(1 for i in _clean_items()
                if i.get("type") == "PersonalBlog"
                and i.get("text", "").count("\u2014") >= 2)
        self.assertGreaterEqual(
            n, MIN_PER_CATEGORY,
            f"Em-dash FP traps: only {n} clean PersonalBlog items with >=2 "
            f"em-dashes (need >={MIN_PER_CATEGORY}, GL#4 Batch E)")

    def test_all_trap_items_below_threshold(self):
        trap_ids = {"hardneg-0%d" % n for n in range(70, 85)}
        found = [i for i in _clean_items() if i.get("id") in trap_ids]
        self.assertEqual(len(found), len(trap_ids),
                         "Batch E FP-trap items missing from corpus")
        for item in found:
            score = slop_scorer.slop_score(item["text"])["slop_score"]
            self.assertLess(score, THRESHOLD,
                            f"{item['id']}: FP-trap item scored {score}")


if __name__ == "__main__":
    unittest.main()
