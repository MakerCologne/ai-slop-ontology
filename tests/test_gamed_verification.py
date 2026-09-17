"""Tests for gamed verification diff signals (issue #112, detect-only).

Fixtures Positiv/Negativ je Signal (Signal-DoD):
  AssertionDelta   weakened assertions in a changed test file
  SkippedTest      newly added skip marks
  TrivialAssertion tautological assertions
  StubLeftBehind   stub markers inside test files
Plus: end-to-end via gamed_verification() over a real git fixture repo.
"""

import os
import subprocess
import sys
import tempfile
import unittest

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SCRIPTS = os.path.join(ROOT, "skills", "ai-slop-detection", "scripts")
sys.path.insert(0, SCRIPTS)

from gamed_verification import (  # noqa: E402
    GamedFinding, analyze_test_diff, gamed_verification, is_test_file,
)

PY_BASE = """\
import unittest


class TestCalc(unittest.TestCase):
    def test_add(self):
        self.assertEqual(1 + 1, 2)
        self.assertEqual(2 + 2, 4)

    def test_sub(self):
        self.assertEqual(3 - 1, 2)
        assert 5 - 2 == 3
"""

# head: one assertEqual removed -> AssertionDelta
PY_WEAKENED = PY_BASE.replace("        self.assertEqual(2 + 2, 4)\n", "")

# head: skip added instead of a fix
PY_SKIPPED = PY_BASE + """

    def test_mul(self):
        raise NotImplementedError  # TODO: implement
"""

# legitimately more assertions -> no AssertionDelta
PY_STRENGTHENED = PY_BASE + "        assert 3 * 3 == 9\n"

TS_BASE = """\
test('adds numbers', () => {
  expect(1 + 1).toBe(2);
  expect(2 + 2).toBe(4);
});
"""

TS_TRIVIAL = TS_BASE + """\

test('always works', () => {
  expect(true).toBe(true);
});
"""

TS_SKIPPED = TS_BASE.replace("test(", "it.skip(", 1)


def run_git(cwd, *args):
    subprocess.run(["git", *args], cwd=cwd, check=True, capture_output=True,
                   env={**os.environ, "GIT_AUTHOR_NAME": "t",
                        "GIT_AUTHOR_EMAIL": "t@t", "GIT_COMMITTER_NAME": "t",
                        "GIT_COMMITTER_EMAIL": "t@t"})


class TestFileDetection(unittest.TestCase):
    def test_conventions(self):
        for p in ("tests/test_calc.py", "src/calc_test.py", "app.test.ts",
                  "app.spec.tsx", "pkg/calc_test.go", "TestCalc.java"):
            self.assertTrue(is_test_file(p), p)
        for p in ("src/calc.py", "app.ts", "notes.md", "tests/helper.ts"):
            self.assertFalse(is_test_file(p), p)


class AssertionDelta(unittest.TestCase):
    def test_positive_weakened(self):
        f = analyze_test_diff("tests/test_calc.py", PY_BASE, PY_WEAKENED)
        self.assertTrue(any(x.signal_id == "AssertionDelta" for x in f), f)
        a = next(x for x in f if x.signal_id == "AssertionDelta")
        self.assertIn("4 in base -> 3 in head", a.evidence)

    def test_negative_strengthened(self):
        f = analyze_test_diff("tests/test_calc.py", PY_BASE, PY_STRENGTHENED)
        self.assertFalse([x for x in f if x.signal_id == "AssertionDelta"])

    def test_negative_new_file(self):
        # newly added test file: no base, no delta possible
        f = analyze_test_diff("tests/test_new.py", "", PY_BASE)
        self.assertFalse([x for x in f if x.signal_id == "AssertionDelta"])

    def test_negative_not_a_test_file(self):
        f = analyze_test_diff("src/calc.py", PY_BASE, PY_WEAKENED)
        self.assertEqual(f, [])


class SkippedTest(unittest.TestCase):
    def test_positive_pytest_skip(self):
        head = PY_BASE.replace("    def test_add(self):",
                               "    @pytest.mark.skip(reason='flaky')\n    def test_add(self):")
        f = analyze_test_diff("tests/test_calc.py", PY_BASE, head)
        self.assertTrue(any(x.signal_id == "SkippedTest" for x in f), f)

    def test_positive_jest_skip(self):
        f = analyze_test_diff("app.test.ts", TS_BASE, TS_SKIPPED)
        self.assertTrue(any(x.signal_id == "SkippedTest" for x in f), f)

    def test_negative_unchanged(self):
        f = analyze_test_diff("tests/test_calc.py", PY_BASE, PY_BASE)
        self.assertFalse([x for x in f if x.signal_id == "SkippedTest"])


class TrivialAssertion(unittest.TestCase):
    def test_positive_js_tautology(self):
        f = analyze_test_diff("app.test.ts", TS_BASE, TS_TRIVIAL)
        self.assertTrue(any(x.signal_id == "TrivialAssertion" for x in f), f)

    def test_positive_python_tautologies(self):
        head = PY_BASE + "        assert True\n        assert 1 == 1\n"
        f = analyze_test_diff("tests/test_calc.py", PY_BASE, head)
        triv = [x for x in f if x.signal_id == "TrivialAssertion"]
        self.assertEqual(len(triv), 2, f)

    def test_negative_real_assertions(self):
        f = analyze_test_diff("tests/test_calc.py", PY_BASE, PY_STRENGTHENED)
        self.assertFalse([x for x in f if x.signal_id == "TrivialAssertion"])


class StubLeftBehind(unittest.TestCase):
    def test_positive_notimplemented(self):
        f = analyze_test_diff("tests/test_calc.py", PY_BASE, PY_SKIPPED)
        self.assertTrue(any(x.signal_id == "StubLeftBehind" for x in f), f)

    def test_negative_clean(self):
        f = analyze_test_diff("tests/test_calc.py", PY_BASE, PY_BASE)
        self.assertEqual(f, [])


class EndToEnd(unittest.TestCase):
    """Real git fixture repo: base + weakened head commit."""

    @classmethod
    def setUpClass(cls):
        cls.dir = tempfile.mkdtemp(prefix="gamedver-")
        run_git(cls.dir, "init", "-q", "-b", "main")
        with open(os.path.join(cls.dir, "tests_test.py"), "w") as fh:
            fh.write(PY_BASE)
        run_git(cls.dir, "add", "-A")
        run_git(cls.dir, "commit", "-q", "-m", "base")
        cls.base = subprocess.run(["git", "rev-parse", "HEAD"], cwd=cls.dir,
                                  capture_output=True, text=True,
                                  check=True).stdout.strip()
        # head: weaken + skip + trivial + stub all at once
        # head: weaken (2 assertions removed, stub 'assert True' added
        # does NOT compensate) + skip + trivial + stub all at once
        head = PY_BASE.replace("        self.assertEqual(2 + 2, 4)\n", "")
        head = head.replace("        assert 5 - 2 == 3\n", "")
        head += "\n    def test_stub(self):\n        raise NotImplementedError  # TODO: implement\n"
        head += "        assert True\n"
        with open(os.path.join(cls.dir, "tests_test.py"), "w") as fh:
            fh.write(head)
        with open(os.path.join(cls.dir, "calc.py"), "w") as fh:
            fh.write("def add(a, b):\n    return a + b\n")
        run_git(cls.dir, "add", "-A")
        run_git(cls.dir, "commit", "-q", "-m", "head")
        cls.head = subprocess.run(["git", "rev-parse", "HEAD"], cwd=cls.dir,
                                  capture_output=True, text=True,
                                  check=True).stdout.strip()

    def test_all_four_signals_via_git(self):
        report = gamed_verification(self.base, self.head, repo_dir=self.dir)
        self.assertEqual(len(report), 1, report)
        ids = {f["signal_id"] for f in report[0]["findings"]}
        self.assertEqual(ids, {"AssertionDelta", "TrivialAssertion",
                               "StubLeftBehind"}, report)

    def test_no_diff_no_findings(self):
        report = gamed_verification(self.base, self.base, repo_dir=self.dir)
        self.assertEqual(report, [])


if __name__ == "__main__":
    unittest.main()
