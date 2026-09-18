"""Tests for run-audit-format (#61): standard files in runs/<runId>/.

Acceptance: a past run can be fully reconstructed from scan.md, fixes.md,
trajectory.json, report.md (signal, fix, score per iteration).
"""

import json
import os
import sys
import tempfile
import unittest

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.deslop_loop import DeslopLoop, LoopParams, Finding  # noqa: E402


def fake_detector(slop_text):
    """Detector returning one signal until the fixer's replacement appears."""
    def detect(text):
        if "sloppy template" in text:
            return 0.7, [Finding(signal="ExcessiveListicle", confidence=0.9,
                                 severity="medium",
                                 evidence="sloppy template phrase")]
        return 0.1, []
    return detect


def fake_fix(text, findings):
    return text.replace("sloppy template", "plain wording")


class TestRunAuditFormat(unittest.TestCase):

    def _run(self, runs_dir):
        loop = DeslopLoop(
            detector=fake_detector("sloppy template"),
            params=LoopParams(score_threshold=0.4, max_iter=5, voice_budget=0.6),
            runs_dir=runs_dir, run_id="testrun-001")
        return loop.run(text="a sloppy template passage", fix=fake_fix)

    def test_standard_files_exist(self):
        with tempfile.TemporaryDirectory() as tmp:
            res = self._run(tmp)
            d = res.run_dir
            for name in ("scan.md", "fixes.md", "trajectory.json",
                         "report.md"):
                self.assertTrue(os.path.isfile(os.path.join(d, name)),
                                f"{name} missing")
            # legacy artifacts still present (backward compat)
            for name in ("manifest.json", "iterations.jsonl", "result.json"):
                self.assertTrue(os.path.isfile(os.path.join(d, name)))

    def test_trajectory_is_reconstructable(self):
        with tempfile.TemporaryDirectory() as tmp:
            res = self._run(tmp)
            with open(os.path.join(res.run_dir, "trajectory.json")) as f:
                traj = json.load(f)
            self.assertEqual(traj["score_initial"], res.score_initial)
            self.assertEqual(traj["score_final"], res.score_final)
            self.assertTrue(traj["iterations"])
            rec = traj["iterations"][0]
            self.assertIn("score_before", rec)
            self.assertIn("score_after", rec)
            self.assertIn("confirmed", rec)
            self.assertIn("action", rec)

    def test_scan_documents_initial_signal(self):
        with tempfile.TemporaryDirectory() as tmp:
            res = self._run(tmp)
            scan = open(os.path.join(res.run_dir, "scan.md")).read()
            self.assertIn("ExcessiveListicle", scan)
            self.assertIn("0.7", scan)

    def test_fixes_and_report_content(self):
        with tempfile.TemporaryDirectory() as tmp:
            res = self._run(tmp)
            fixes = open(os.path.join(res.run_dir, "fixes.md")).read()
            self.assertIn("accepted", fixes)
            report = open(os.path.join(res.run_dir, "report.md")).read()
            self.assertIn(res.verdict, report)
            self.assertIn("Guarantee", report)

    def test_no_runs_dir_no_crash(self):
        loop = DeslopLoop(detector=fake_detector("x"),
                          params=LoopParams(score_threshold=0.4, max_iter=1))
        res = loop.run(text="a sloppy template passage")
        self.assertIsNone(res.run_dir)  # audit writer is a no-op


if __name__ == "__main__":
    unittest.main()
