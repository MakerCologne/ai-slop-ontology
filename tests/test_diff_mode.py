"""Tests for the diff mode (issue #10): score ONLY new/changed lines."""

import os
import subprocess
import sys
import tempfile
import unittest

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SCRIPTS = os.path.join(ROOT, "skills", "ai-slop-detection", "scripts")
SCORER = os.path.join(SCRIPTS, "slop_scorer.py")
sys.path.insert(0, SCRIPTS)

from diff_mode import diff_scores, scored_windows  # noqa: E402


def run_git(cwd, *args):
    subprocess.run(["git", *args], cwd=cwd, check=True,
                   capture_output=True, env={**os.environ,
                    "GIT_AUTHOR_NAME": "t", "GIT_AUTHOR_EMAIL": "t@t",
                    "GIT_COMMITTER_NAME": "t", "GIT_COMMITTER_EMAIL": "t@t"})


class FixtureRepo:
    """Two commits: clean base, then a head that adds slop, clean text,
    a lock-file change, a binary, and a .py file."""

    def __init__(self):
        self.dir = tempfile.mkdtemp(prefix="diffmode-")
        run_git(self.dir, "init", "-q", "-b", "main")
        base_md = ("# Notes\n\n"
                   "The service reads its port from the environment.\n"
                   "Restarts happen automatically on config change.\n")
        with open(os.path.join(self.dir, "notes.md"), "w") as f:
            f.write(base_md)
        run_git(self.dir, "add", "-A")
        run_git(self.dir, "commit", "-q", "-m", "base")
        self.base = "HEAD"
        # head commit
        with open(os.path.join(self.dir, "notes.md"), "a") as f:
            f.write("\nIn today's fast-paced world, it's worth noting that "
                    "harnessing robust synergy is a game-changer. Let's dive in "
                    "and unlock seamless potential. At the end of the day, the "
                    "possibilities are endless.\n")
        with open(os.path.join(self.dir, "clean.txt"), "w") as f:
            f.write("The backup runs at 02:15 UTC.\nRetention is 14 days for incrementals.\n")
        with open(os.path.join(self.dir, "package-lock.json"), "w") as f:
            f.write('{"lockfileVersion": 3, "packages": {"lodash": {"version": "4.17.21"}}}\n')
        with open(os.path.join(self.dir, "logo.png"), "wb") as f:
            f.write(b"\x89PNG\r\n\x1a\n\x00\x00binary\x00bytes")
        with open(os.path.join(self.dir, "helper.ts"), "w") as f:
            f.write("const user = payload as unknown as User;\n"
                    "const cached = store as unknown as Cache;\n")
        run_git(self.dir, "add", "-A")
        run_git(self.dir, "commit", "-q", "-m", "head")
        self.head = "HEAD"


class ScoredWindowsTests(unittest.TestCase):
    def test_only_changed_lines_scored(self):
        lines = ["unchanged slop intro line", "changed line two"]
        wins = scored_windows(lines, changed_indices=[1])
        self.assertEqual(len(wins), 1)
        text = "\n".join(lines[s] for s in wins[0])
        self.assertNotIn("unchanged", text)
        self.assertIn("changed line two", text)

    def test_context_window_extends_for_sentence_fragments(self):
        # The changed line is a sentence FRAGMENT: previous context line does
        # not end a sentence, so up to +-3 context lines are stitched in.
        lines = ["In today's world, it is worth noting that",   # 0 context
                 "harnessing robust synergy is a game-changer.",  # 1 changed
                 "Restarts happen automatically."]                # 2 context
        wins = scored_windows(lines, changed_indices=[1], ctx=3)
        text = "\n".join(lines[s] for s in wins[0])
        self.assertIn("In today's world", text)

    def test_no_context_stitched_when_sentence_complete(self):
        # Previous line ends with a period -> no fragment stitching upward.
        lines = ["The port comes from the environment.", "Synergy unlocked.",]
        wins = scored_windows(lines, changed_indices=[1], ctx=3)
        text = "\n".join(lines[s] for s in wins[0])
        self.assertNotIn("environment", text)

    def test_context_limited_to_three_lines(self):
        lines = [f"line {i}" for i in range(10)]
        wins = scored_windows(lines, changed_indices=[5], ctx=3)
        self.assertEqual(wins[0], (2, 8))


class DiffModeTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.repo = FixtureRepo()

    def test_report_is_per_file(self):
        report = diff_scores(self.repo.base, self.repo.head, self.repo.dir)
        names = {r["file"] for r in report}
        self.assertIn("notes.md", names)
        self.assertIn("clean.txt", names)

    def test_slop_addition_scores_above_threshold_with_top_signals(self):
        report = diff_scores(self.repo.base, self.repo.head, self.repo.dir)
        entry = next(r for r in report if r["file"] == "notes.md")
        self.assertGreaterEqual(entry["slop_score"], 0.40)
        self.assertTrue(entry["top_signals"])

    def test_clean_addition_scores_below_threshold(self):
        report = diff_scores(self.repo.base, self.repo.head, self.repo.dir)
        entry = next(r for r in report if r["file"] == "clean.txt")
        self.assertLess(entry["slop_score"], 0.40)

    def test_lock_file_skipped(self):
        report = diff_scores(self.repo.base, self.repo.head, self.repo.dir)
        self.assertNotIn("package-lock.json", {r["file"] for r in report})

    def test_binary_file_skipped(self):
        report = diff_scores(self.repo.base, self.repo.head, self.repo.dir)
        self.assertNotIn("logo.png", {r["file"] for r in report})

    def test_code_file_routed_to_code_slop(self):
        report = diff_scores(self.repo.base, self.repo.head, self.repo.dir)
        entry = next(r for r in report if r["file"] == "helper.ts")
        self.assertEqual(entry["kind"], "code")
        ids = [f["id"] for f in entry["code_findings"]]
        self.assertIn("chained_type_assertions", ids)

    def test_unchanged_slop_not_scored(self):
        # base commit alone (no changes) -> no report entries
        report = diff_scores(self.repo.base, self.repo.base, self.repo.dir)
        self.assertEqual(report, [])


class DiffModeCLITests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.repo = FixtureRepo()

    def test_cli_diff_flag_reports_per_file(self):
        p = subprocess.run(
            [sys.executable, SCORER, "--diff", f"{self.repo.base}..{self.repo.head}"],
            cwd=self.repo.dir, capture_output=True, text=True)
        self.assertEqual(p.returncode, 1)  # slop found -> exit 1
        self.assertIn("notes.md", p.stdout)
        self.assertIn("clean.txt", p.stdout)
        self.assertIn("0.", p.stdout)  # a numeric score is printed

    def test_cli_diff_no_slop_exits_zero(self):
        p = subprocess.run(
            [sys.executable, SCORER, "--diff", f"{self.repo.base}..{self.repo.base}"],
            cwd=self.repo.dir, capture_output=True, text=True)
        self.assertEqual(p.returncode, 0)

    def test_cli_diff_rejects_malformed_range(self):
        p = subprocess.run(
            [sys.executable, SCORER, "--diff", "no-dots-here"],
            cwd=self.repo.dir, capture_output=True, text=True)
        self.assertEqual(p.returncode, 2)


if __name__ == "__main__":
    unittest.main()
