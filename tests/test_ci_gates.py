"""CI must run what the documentation calls a gate (issue #84).

Two silent gaps, both found on master b2a7bb0:

  1. The workflow ran `python -m unittest discover tests`, which only collects
     unittest.TestCase classes. Twelve test files are written in pytest
     function style and were therefore never executed in CI — including the
     ones that guard the constitutive documents (signal DoD, SCORE-GOVERNANCE,
     METHODOLOGY, EVALS, ADRs). 420 of 539 tests ran, with no warning.

  2. docs/SCORE-GOVERNANCE.md names Control Set, benchmark and consistency as
     merge gates. The workflow enforced only the consistency check, and ran
     the benchmark "informational" — without a threshold it cannot fail.

The tests here read the workflow file, so a future edit that drops a gate
fails the suite instead of silently weakening CI.
"""

import os
import re
import subprocess
import sys
import unittest

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
WORKFLOW = os.path.join(ROOT, ".github", "workflows", "tests.yml")
TESTS_DIR = os.path.join(ROOT, "tests")


def _workflow_text() -> str:
    """The workflow without its comments — assertions are about what runs."""
    with open(WORKFLOW, encoding="utf-8") as fh:
        lines = [ln for ln in fh.read().splitlines()
                 if not ln.lstrip().startswith("#")]
    return "\n".join(lines)


class SuiteCoverageTest(unittest.TestCase):
    """Every test file must actually run in CI."""

    def test_workflow_runs_the_whole_suite(self):
        text = _workflow_text()
        self.assertNotIn(
            "unittest discover", text,
            "unittest discovery skips pytest-style files without warning (#84)",
        )
        self.assertRegex(
            text, r"\bpytest\b",
            "CI must run the suite with a runner that collects every test file",
        )

    def test_no_test_file_is_invisible_to_the_ci_runner(self):
        """The gap that hid twelve files: collected != present on disk."""
        on_disk = {
            f for f in os.listdir(TESTS_DIR)
            if f.startswith("test_") and f.endswith(".py")
        }
        proc = subprocess.run(
            [sys.executable, "-m", "pytest", "--collect-only", "-q", TESTS_DIR],
            cwd=ROOT, capture_output=True, text=True,
        )
        self.assertEqual(proc.returncode, 0, proc.stdout[-3000:] + proc.stderr[-2000:])
        collected = set(re.findall(r"(test_[A-Za-z0-9_]+\.py)::", proc.stdout))
        missing = sorted(on_disk - collected)
        self.assertEqual(
            missing, [],
            f"test files present but never collected: {missing}",
        )


class GateCoverageTest(unittest.TestCase):
    """Each documented gate is a CI step that can fail the build."""

    REQUIRED_GATES = [
        "scripts/check_consistency.py",
        "scripts/check_ssot.py",
        "scripts/check_methodology.py",
        "scripts/check_signal_dod.py",
        "scripts/fp_baseline.py",
        "eval/run_control_set.py",
        "scripts/self_check_docs.py",
        "eval/run_benchmark.py",
    ]

    def test_every_documented_gate_runs_in_ci(self):
        text = _workflow_text()
        for gate in self.REQUIRED_GATES:
            with self.subTest(gate=gate):
                self.assertIn(
                    gate, text,
                    f"{gate} is documented as a gate but never runs in CI (#84)",
                )

    def test_benchmark_is_not_informational(self):
        text = _workflow_text()
        self.assertNotIn(
            "informational", text.lower(),
            "a benchmark step without a threshold cannot fail — pin the "
            "minimum precision/recall instead (#84)",
        )
        self.assertRegex(
            text, r"--min-precision",
            "the benchmark step must enforce a floor",
        )

    def test_fp_baseline_runs_in_check_mode(self):
        self.assertRegex(
            _workflow_text(), r"fp_baseline\.py --check",
            "fp_baseline without --check reports but does not gate",
        )


class BenchmarkThresholdTest(unittest.TestCase):
    """run_benchmark can enforce a floor and exits non-zero below it."""

    def _run(self, *extra):
        return subprocess.run(
            [sys.executable, os.path.join(ROOT, "eval", "run_benchmark.py"), *extra],
            cwd=ROOT, capture_output=True, text=True,
        )

    def test_passes_at_the_current_baseline(self):
        proc = self._run("--min-precision", "1.0", "--min-recall", "0.99")
        self.assertEqual(proc.returncode, 0, proc.stdout[-2000:] + proc.stderr[-2000:])

    def test_fails_below_an_impossible_floor(self):
        # A floor above 1.0 is unreachable by definition. Using the current
        # recall gap instead would make this test fail the day the pipeline
        # reaches perfect recall — a test that punishes an improvement.
        proc = self._run("--min-precision", "1.01", "--min-recall", "1.01")
        self.assertEqual(
            proc.returncode, 1,
            "a floor the pipeline cannot meet must fail the build",
        )
        combined = (proc.stdout + proc.stderr).lower()
        self.assertIn("benchmark gate failed", combined)
        self.assertIn("precision", combined)

    def test_without_a_floor_it_stays_a_report(self):
        proc = self._run()
        self.assertEqual(proc.returncode, 0)


if __name__ == "__main__":
    unittest.main()
