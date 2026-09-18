"""Tests für Gamed Verification im Diff-Modus (issue #112, detect-only).

3/3/2-Fixtures je Signal (Positiv / Negativ / FP-Guard):
  - AssertionDelta: Verlust pos., Zuwachs neg., reine Refactor-Umbenennung guard
  - SkippedTest: hinzugefügter Skip pos., entfernter Skip neg.,
    nur Kommentar-Erwähnung guard
  - TrivialAssertion: expect(true).toBe(true) pos., echte Assertion neg.,
    assert True in String-Literal guard
Plus Integration über diff_mode.diff_scores mit Fixture-Repo.
"""

import os
import subprocess
import sys
import tempfile
import unittest

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SCRIPTS = os.path.join(ROOT, "skills", "ai-slop-detection", "scripts")
sys.path.insert(0, SCRIPTS)

from diff_verification import (  # noqa: E402
    analyze_test_diff, count_assertions_js, count_assertions_py,
    is_test_file)


def run_git(cwd, *args):
    subprocess.run(["git", *args], cwd=cwd, check=True, capture_output=True,
                   env={**os.environ, "GIT_AUTHOR_NAME": "t",
                        "GIT_COMMITTER_NAME": "t", "GIT_AUTHOR_EMAIL": "t@t",
                        "GIT_COMMITTER_EMAIL": "t@t"})


class TestFileDetection(unittest.TestCase):
    def test_paths(self):
        self.assertTrue(is_test_file("tests/test_cli.py"))
        self.assertTrue(is_test_file("src/foo_test.py"))
        self.assertTrue(is_test_file("a/b/c.test.ts"))
        self.assertTrue(is_test_file("x.spec.js"))
        self.assertFalse(is_test_file("src/cli.py"))
        self.assertFalse(is_test_file("tests/helper.ts"))


class TestAssertionDelta(unittest.TestCase):
    def test_positive_loss(self):
        old = ("def test_a():\n    assert f(1) == 2\n"
               "def test_b():\n    assert f(2) == 3\n")
        new = "def test_a():\n    pass\n"
        r = analyze_test_diff("tests/test_a.py", old, new, [])
        self.assertEqual(r["assertion_delta"], -2)
        ids = [f["signal_id"] for f in r["findings"]]
        self.assertIn("AssertionDelta", ids)

    def test_negative_gain(self):
        old = "def test_a():\n    pass\n"
        new = "def test_a():\n    assert f(1) == 2\n"
        r = analyze_test_diff("tests/test_a.py", old, new, [(3, "    assert f(1) == 2")])
        self.assertEqual(r["assertion_delta"], 1)
        self.assertNotIn("AssertionDelta",
                         [f["signal_id"] for f in r["findings"]])

    def test_fp_guard_rename_only(self):
        old = ("def test_a():\n    result = run()\n"
               "    assert result == 7\n")
        new = ("def test_a():\n    outcome = run()\n"
               "    assert outcome == 7\n")
        r = analyze_test_diff("tests/test_a.py", old, new, [])
        self.assertEqual(r["assertion_delta"], 0)
        self.assertEqual(r["findings"], [])

    def test_js_counts(self):
        self.assertGreater(count_assertions_js(
            "expect(a).toBe(1);\nassert(x);\n"), 1)


class TestSkippedTest(unittest.TestCase):
    def test_positive_added_skip(self):
        added = [(4, "    @pytest.mark.skip(reason='flaky')")]
        r = analyze_test_diff("tests/test_a.py", "", "", added)
        self.assertIn("SkippedTest", [f["signal_id"] for f in r["findings"]])

    def test_negative_removed_skip(self):
        # diff added lines enthalten keinen Skip
        added = [(4, "    assert f(1) == 2")]
        r = analyze_test_diff("tests/test_a.py", "", "", added)
        self.assertNotIn("SkippedTest",
                         [f["signal_id"] for f in r["findings"]])

    def test_fp_guard_comment_mention(self):
        added = [(4, "# TODO: remove pytest.mark.skip after fix")]
        r = analyze_test_diff("tests/test_a.py", "", "", added)
        self.assertNotIn("SkippedTest",
                         [f["signal_id"] for f in r["findings"]])

    def test_js_skip(self):
        added = [(5, "    it.skip('broken')")]
        r = analyze_test_diff("a.test.ts", "", "", added)
        self.assertIn("SkippedTest", [f["signal_id"] for f in r["findings"]])


class TestTrivialAssertion(unittest.TestCase):
    def test_positive_py(self):
        added = [(3, "    assert True"), (4, "    assertEqual(1, 1)")]
        r = analyze_test_diff("tests/test_a.py", "", "", added)
        n = sum(1 for f in r["findings"] if f["signal_id"] == "TrivialAssertion")
        self.assertEqual(n, 2)

    def test_negative_real(self):
        added = [(3, "    assert compute(2) == 4")]
        r = analyze_test_diff("tests/test_a.py", "", "", added)
        self.assertNotIn("TrivialAssertion",
                         [f["signal_id"] for f in r["findings"]])

    def test_fp_guard_string_literal(self):
        added = [(3, "    msg = \"assert True is not a real check\"")]
        r = analyze_test_diff("tests/test_a.py", "", "", added)
        self.assertNotIn("TrivialAssertion",
                         [f["signal_id"] for f in r["findings"]])

    def test_js_trivial(self):
        added = [(5, "    expect(true).toBe(true);")]
        r = analyze_test_diff("a.spec.ts", "", "", added)
        self.assertIn("TrivialAssertion",
                      [f["signal_id"] for f in r["findings"]])


class TestDiffModeIntegration(unittest.TestCase):
    def test_weakened_assertions_in_git_diff(self):
        d = tempfile.mkdtemp(prefix="diffver-")
        run_git(d, "init", "-q", "-b", "main")
        base_py = ("def test_a():\n    assert f(1) == 2\n"
                   "def test_b():\n    assert f(2) == 3\n")
        p = os.path.join(d, "test_mod.py")
        open(p, "w").write(base_py)
        run_git(d, "add", "-A")
        run_git(d, "commit", "-q", "-m", "base")
        base = subprocess.run(["git", "rev-parse", "HEAD"], cwd=d,
                              capture_output=True, text=True,
                              check=True).stdout.strip()
        open(p, "w").write("def test_a():\n    assert True\n")
        run_git(d, "add", "-A")
        run_git(d, "commit", "-q", "-m", "weaken")
        sys.path.insert(0, SCRIPTS)
        from diff_mode import diff_scores
        rep = diff_scores(base, "HEAD", repo_dir=d)
        entry = [e for e in rep if e["file"] == "test_mod.py"]
        self.assertTrue(entry, rep)
        e = entry[0]
        self.assertEqual(e["kind"], "test")
        self.assertEqual(e["assertion_delta"], -1)
        ids = {f["signal_id"] for f in e["findings"]}
        self.assertEqual(ids, {"TrivialAssertion", "AssertionDelta"})


if __name__ == "__main__":
    unittest.main()
