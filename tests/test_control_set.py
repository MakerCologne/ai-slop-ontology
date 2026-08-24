"""MS-I1: CLI hardening + handwritten control set gate (5 slop / 5 hard negatives).

Red tests (2026-08-24). Documented FN before calibration:
- slop-fn-01 scored 0.279 (classic digital-age slop; buzz divisor 8 dilutes
  3 tier-2 buzzwords + 2 phrase-category hits below the escalation rule).
- slop-fn-02 scored 0.303 (business-listicle patterns not in the phrase DB).
"""

import json
import os
import subprocess
import sys
import tempfile
import unittest

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SCRIPTS = os.path.join(ROOT, "skills", "ai-slop-detection", "scripts")
sys.path.insert(0, SCRIPTS)

import slop_scorer  # noqa: E402

CONTROL_SET = os.path.join(ROOT, "eval", "control_set.jsonl")
GATE_SCRIPT = os.path.join(ROOT, "eval", "run_control_set.py")
SCORER_CLI = os.path.join(SCRIPTS, "slop_scorer.py")
THRESHOLD = 0.40


def load_control_set():
    items = []
    with open(CONTROL_SET) as f:
        for line in f:
            if line.strip():
                items.append(json.loads(line))
    return items


class TestControlSetGate(unittest.TestCase):
    def test_control_set_has_10_items_5_slop_5_clean(self):
        items = load_control_set()
        self.assertEqual(len(items), 10)
        slop = [i for i in items if i["label"] == "slop"]
        clean = [i for i in items if i["label"] == "clean"]
        self.assertEqual(len(slop), 5)
        self.assertEqual(len(clean), 5)

    def test_all_hard_negatives_below_threshold(self):
        for item in load_control_set():
            if item["label"] != "clean":
                continue
            score = slop_scorer.slop_score(item["text"])["slop_score"]
            self.assertLess(
                score, THRESHOLD,
                f"{item['id']} flagged as slop: {score}")

    def test_all_slop_above_threshold_except_known_fns(self):
        known_fns = {i["id"] for i in load_control_set() if i.get("known_fn")}
        for item in load_control_set():
            if item["label"] != "slop" or item["id"] in known_fns:
                continue
            score = slop_scorer.slop_score(item["text"])["slop_score"]
            self.assertGreaterEqual(
                score, THRESHOLD,
                f"{item['id']} is an undocumented false negative: {score}")

    def test_gate_script_exits_zero_and_reports_known_fn(self):
        proc = subprocess.run(
            [sys.executable, GATE_SCRIPT],
            capture_output=True, text=True, timeout=60,
        )
        self.assertEqual(
            proc.returncode, 0,
            f"gate failed:\n{proc.stdout}\n{proc.stderr}")
        self.assertIn("KNOWN-FN", proc.stdout)
        self.assertIn("slop-fn-02", proc.stdout)


class TestCliFileInput(unittest.TestCase):
    SLOP_TEXT = ("In today's rapidly evolving digital landscape, harnessing "
                 "the power of cutting-edge AI is paramount to unlock your "
                 "full potential. In conclusion, the possibilities are endless.")
    CLEAN_TEXT = "The median pause was 4.2 ms with a p99 of 18 ms."

    def _write_temp(self, text):
        f = tempfile.NamedTemporaryFile(
            "w", suffix=".txt", delete=False, dir=tempfile.gettempdir())
        f.write(text)
        f.close()
        self.addCleanup(os.unlink, f.name)
        return f.name

    def _run(self, *args):
        return subprocess.run(
            [sys.executable, SCORER_CLI, *args],
            capture_output=True, text=True, timeout=60,
        )

    def test_file_flag_scores_file_content(self):
        path = self._write_temp(self.CLEAN_TEXT)
        proc = self._run("--json", "--file", path)
        self.assertEqual(proc.returncode, 0, proc.stderr)
        result = json.loads(proc.stdout)
        self.assertLess(result["slop_score"], THRESHOLD)

    def test_positional_existing_path_is_autodetected_as_file(self):
        # Bug being fixed: an existing path passed as argv was previously
        # scored AS TEXT ("Avg sentence 3.0 words" symptom) instead of
        # reading the file.
        path = self._write_temp(self.SLOP_TEXT)
        proc = self._run("--json", path)
        self.assertEqual(proc.returncode, 0, proc.stderr)
        result = json.loads(proc.stdout)
        self.assertGreaterEqual(result["slop_score"], THRESHOLD)
        self.assertNotIn("Avg sentence", proc.stdout)  # --json has no report

    def test_file_flag_missing_file_errors(self):
        proc = self._run("--file", "/nonexistent/does-not-exist.txt")
        self.assertNotEqual(proc.returncode, 0)
        self.assertIn("No such file", proc.stderr + proc.stdout)

    def test_positional_text_emits_deprecation_warning(self):
        proc = self._run("--json", self.CLEAN_TEXT)
        self.assertEqual(proc.returncode, 0, proc.stderr)
        self.assertIn("deprecat", proc.stderr.lower())


if __name__ == "__main__":
    unittest.main()
