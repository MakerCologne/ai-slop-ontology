"""Null-Edit-Contract (issue #79): clean input must produce clean output.

Contract (gate, runs on every commit):
  1. Every hard-negative (label=clean) corpus text scores BELOW the decision
     threshold 0.40 on BOTH engines (skill scorer, src classifier).
  2. Null edits (trailing-whitespace strip, soft linebreak reflow) never
     change the verdict or the score of a clean text.
  3. Borderline monitoring band: the 5 highest-scoring clean fixtures are
     pinned in eval/hardneg_borderline.json (snapshot, tolerance ±0.02) so
     creeping FP pressure is visible before it breaks the gate; the
     documented fast-clean borderline fixtures (dense human prose) must stay
     below threshold.
"""

import json
import os
import re
import sys
import unittest

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, "skills", "ai-slop-detection", "scripts"))
sys.path.insert(0, os.path.join(ROOT, "src"))

import slop_scorer  # noqa: E402
from classifier import SlopClassifier  # noqa: E402

CORPUS = os.path.join(ROOT, "eval", "corpus.jsonl")
BORDERLINE_REGISTER = os.path.join(ROOT, "eval", "hardneg_borderline.json")
THRESHOLD = 0.40

# Handcrafted fast-clean borderline fixtures (dense human prose, one or two
# surface slop markers each — human writing, must stay below threshold).
HANDCRAFTED_BORDERLINE = {
    "borderline-contractions": (
        "In the end the committee decided the report was important. It noted "
        "that three of the five studies were industry funded, and it is "
        "important to note the remaining two used small samples. The chair "
        "said the evidence base remains thin, so the finding stands as a "
        "provisional one, not a settled fact."),
    "borderline-metaphor": (
        "Delve into the archives and you find a rich picture of everyday "
        "life: rent books, wage slips, letters. Historians have used these "
        "sources to reconstruct household budgets, and the numbers matter "
        "more than the narrative flourishes. The archive does not speak for "
        "itself; someone always counts."),
    "borderline-audience-address": (
        "Whether you're a seasoned developer or just starting out, version "
        "control will save you hours of pain. Roll back mistakes, branch "
        "experiments, keep a clean history. This is not optional; it is "
        "basic hygiene for anyone who writes code for a living, and it is "
        "cheaper to learn now than later."),
}


def _clean_items():
    with open(CORPUS, encoding="utf-8") as f:
        return [json.loads(l) for l in f if l.strip() and
                json.loads(l).get("label") == "clean"]


def null_edit(text: str) -> str:
    """Whitespace-only rewrite: strip trailing spaces, reflow soft breaks."""
    text = re.sub(r"[ \t]+\n", "\n", text)
    text = re.sub(r"(?<!\n)\n(?!\n)", " ", text)
    return text


class NullEditContract(unittest.TestCase):
    def test_all_hard_negatives_clean_on_both_engines(self):
        items = _clean_items()
        self.assertGreaterEqual(len(items), 90)
        for item in items:
            skill = slop_scorer.slop_score(item["text"])["slop_score"]
            self.assertLess(skill, THRESHOLD,
                            f"{item['id']}: skill scorer {skill}")
        clf = SlopClassifier(os.path.join(ROOT, "ontology.json"))
        for item in items:
            score = clf.classify_text(item["text"]).overall_slop_score
            self.assertLess(score, THRESHOLD,
                            f"{item['id']}: src classifier {score}")

    def test_null_edit_keeps_verdict_and_bounded_score(self):
        """Null edits keep the clean verdict; score drift is bounded.

        Documented sensitivity (measured on hardneg-042, a changelog):
        reflowing soft linebreaks can dissolve list structure, flipping
        list_heavy and moving the score by up to ~0.04. Both values stay
        far below threshold — the CONTRACT is the verdict, plus a bounded
        drift guard (≤ 0.05) against hidden instabilities.
        """
        for item in _clean_items():
            base = slop_scorer.slop_score(item["text"])["slop_score"]
            after = slop_scorer.slop_score(null_edit(item["text"]))["slop_score"]
            self.assertLess(after, THRESHOLD, f"{item['id']}: {after}")
            self.assertLessEqual(abs(base - after), 0.05,
                                 f"{item['id']}: score drifted {base}->{after}")

    def test_borderline_register_exists_and_schema(self):
        self.assertTrue(os.path.exists(BORDERLINE_REGISTER),
                        "eval/hardneg_borderline.json missing (issue #79)")
        with open(BORDERLINE_REGISTER, encoding="utf-8") as f:
            reg = json.load(f)
        self.assertIn("generated_from", reg)
        self.assertIn("threshold", reg)
        self.assertEqual(reg["threshold"], THRESHOLD)
        self.assertEqual(len(reg["top5_clean"]), 5)
        for entry in reg["top5_clean"]:
            self.assertIn("id", entry)
            self.assertIn("score", entry)
            self.assertLess(entry["score"], THRESHOLD)
        self.assertEqual(len(reg["handcrafted"]), len(HANDCRAFTED_BORDERLINE))

    def test_borderline_register_matches_current_measurement(self):
        with open(BORDERLINE_REGISTER, encoding="utf-8") as f:
            reg = json.load(f)
        measured = sorted(
            ((slop_scorer.slop_score(i["text"])["slop_score"], i["id"])
             for i in _clean_items()), reverse=True)[:5]
        for (score, item_id), entry in zip(measured, reg["top5_clean"]):
            self.assertEqual(entry["id"], item_id)
            self.assertAlmostEqual(entry["score"], score, delta=0.02,
                                   msg=f"{item_id} drifted vs register")

    def test_handcrafted_borderline_fixtures_below_threshold(self):
        for name, text in HANDCRAFTED_BORDERLINE.items():
            score = slop_scorer.slop_score(text)["slop_score"]
            self.assertLess(score, THRESHOLD, f"{name}: {score}")
        with open(BORDERLINE_REGISTER, encoding="utf-8") as f:
            reg = json.load(f)
        for name, entry in reg["handcrafted"].items():
            self.assertLess(entry["score"], THRESHOLD)


if __name__ == "__main__":
    unittest.main()
