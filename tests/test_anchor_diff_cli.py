"""CLI wiring for --anchor-diff (issue #78): diff-mode flag reporting
anchor drift between two git revisions of each changed text file."""

import os
import subprocess
import sys
import tempfile
import unittest

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SCORER = os.path.join(ROOT, "skills", "ai-slop-detection", "scripts",
                      "slop_scorer.py")


def run_git(cwd, *args):
    subprocess.run(["git", *args], cwd=cwd, check=True, capture_output=True,
                   env={**os.environ,
                        "GIT_AUTHOR_NAME": "t", "GIT_AUTHOR_EMAIL": "t@t",
                        "GIT_AUTHOR_COMITTER_NAME": "t",
                        "GIT_COMMITTER_NAME": "t", "GIT_COMMITTER_EMAIL": "t@t"})


class AnchorDiffCLI(unittest.TestCase):
    def _repo(self):
        d = tempfile.mkdtemp(prefix="anchordiff-")
        run_git(d, "init", "-q", "-b", "main")
        with open(os.path.join(d, "notes.md"), "w", encoding="utf-8") as f:
            f.write("Der Umsatz stieg 2024 um 12,4 Prozent.\n")
        run_git(d, "add", "-A")
        run_git(d, "commit", "-qm", "base")
        run_git(d, "tag", "v-base")
        with open(os.path.join(d, "notes.md"), "w", encoding="utf-8") as f:
            f.write("Der Umsatz stieg zuletzt deutlich.\n")
        run_git(d, "add", "-A")
        run_git(d, "commit", "-qm", "rewrite")
        return d

    def test_anchor_diff_reports_lost_anchor(self):
        d = self._repo()
        proc = subprocess.run(
            [sys.executable, SCORER, "--anchor-diff", "v-base..HEAD"],
            cwd=d, capture_output=True, text=True)
        self.assertEqual(proc.returncode, 0, proc.stderr)
        self.assertIn("notes.md", proc.stdout)
        self.assertIn("anchor_lost", proc.stdout)
        self.assertIn("12.4", proc.stdout)

    def test_anchor_diff_requires_range(self):
        proc = subprocess.run([sys.executable, SCORER, "--anchor-diff"],
                              capture_output=True, text=True)
        self.assertNotEqual(proc.returncode, 0)


if __name__ == "__main__":
    unittest.main()
