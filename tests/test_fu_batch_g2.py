"""
FU-Register Batch G, Teil 2 — FU-5, FU-7, FU-10 (review-batch-d.md).

FU-5: #9 `as_any_casts` fired on an English COMMENT ("use this as any
      other helper") in Python — comment lines are prose, not casts.
FU-7: Dev-claim "je 9–12 Phrasen pro Text" in the CHANGELOG was
      overclaiming; measured (review-batch-d): 3–12 verbatim phrases,
      median ~7.
FU-10: README benchmark section mirrored into the skill document.
"""

import os
import re
import unittest

ROOT = os.path.join(os.path.dirname(__file__), "..")
sys_path = os.path.join(
    ROOT, "skills", "ai-slop-detection", "scripts")

import sys  # noqa: E402

sys.path.insert(0, sys_path)
import code_slop  # noqa: E402

CHANGELOG = os.path.join(ROOT, "CHANGELOG.md")
SKILL = os.path.join(ROOT, "skills", "ai-slop-detection", "SKILL.md")


class TestFU5AsAnyCommentGuard(unittest.TestCase):
    """FU-5 (#9, review-batch-d FP 1): Python comment
    "use this as any other helper" fired as_any_casts."""

    def test_comment_line_does_not_fire(self):
        code = ("def helper(x):\n"
                "    # use this as any other helper\n"
                "    return x\n")
        result = code_slop.analyze_code(code)
        ids = [f["id"] for f in result["findings"]]
        self.assertNotIn("as_any_casts", ids)

    def test_slash_comment_does_not_fire(self):
        code = "// use this as any other helper\nconst y = 2;\n"
        result = code_slop.analyze_code(code)
        ids = [f["id"] for f in result["findings"]]
        self.assertNotIn("as_any_casts", ids)

    def test_real_cast_still_fires(self):
        code = "const user = response as any;\n"
        result = code_slop.analyze_code(code)
        ids = [f["id"] for f in result["findings"]]
        self.assertIn("as_any_casts", ids)


class TestFU7ChangelogPhraseClaimCorrected(unittest.TestCase):
    """FU-7 (burn-log Batch D): 'je 9–12 Phrasen pro Text' -> gemessen
    3–12 (Median ~7). The overclaiming number must be gone from the
    CHANGELOG; the corrected range must be present."""

    def test_overclaim_removed_and_correction_present(self):
        with open(CHANGELOG, encoding="utf-8") as fh:
            content = fh.read()
        self.assertNotIn("9–12 Phrasen", content,
                         "überzogener Dev-Claim '9–12 Phrasen' noch da (FU-7)")
        self.assertNotIn("9-12 Phrasen", content,
                         "überzogener Dev-Claim '9-12 Phrasen' noch da (FU-7)")
        self.assertRegex(content, r"3[–-]12 Phrasen")


class TestFU10SkillBenchmarkMirror(unittest.TestCase):
    """FU-10 (review-batch-d #6): README-Benchmark-Sektion ins
    Skill-Dokument spiegeln — mit Messreferenz (Claim-Register)."""

    def test_skill_doc_has_benchmark_with_reference(self):
        with open(SKILL, encoding="utf-8") as fh:
            content = fh.read()
        self.assertIn("run_benchmark", content)
        self.assertIn("corpus.jsonl", content)
        # numbers must be present and pinned to the threshold
        self.assertIn("0.982", content)
        self.assertIn("0.40", content)
        # honesty: the in-sample caveat from review-batch-f must travel along
        self.assertRegex(content, r"[Ii]n-sample|in-sample")


if __name__ == "__main__":
    unittest.main()
