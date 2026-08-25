"""FP-Baseline-Register (issue #80): tolerated detector outputs per
hard-negative fixture, snapshot-compared in CI.

eval/fp_baseline.json pins, for every label=clean corpus fixture, the exact
slop_score and the (sub-threshold) signal hits the skill pipeline produces
today. Any NEW signal firing on a hard negative — or a score change beyond
tolerance — fails scripts/fp_baseline.py --check, BEFORE it can accumulate
into a threshold-crossing false positive. Tolerated outputs stay visible,
not hidden.
"""

import json
import os
import subprocess
import sys
import unittest

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, "skills", "ai-slop-detection", "scripts"))
sys.path.insert(0, os.path.join(ROOT, "scripts"))

SCRIPT = os.path.join(ROOT, "scripts", "fp_baseline.py")
BASELINE = os.path.join(ROOT, "eval", "fp_baseline.json")

import slop_scorer  # noqa: E402
from fp_baseline import build_baseline, compare_baselines, drift_report  # noqa: E402


def _clean_ids():
    with open(os.path.join(ROOT, "eval", "corpus.jsonl"), encoding="utf-8") as f:
        return {json.loads(l)["id"] for l in f if l.strip()
                and json.loads(l).get("label") == "clean"}


class FpBaselineBuild(unittest.TestCase):
    def test_baseline_file_covers_every_hard_negative(self):
        with open(BASELINE, encoding="utf-8") as f:
            reg = json.load(f)
        self.assertEqual(set(reg["fixtures"]), _clean_ids())

    def test_build_is_deterministic(self):
        self.assertEqual(build_baseline(), build_baseline())

    def test_committed_baseline_matches_current_build(self):
        with open(BASELINE, encoding="utf-8") as f:
            reg = json.load(f)
        drift = drift_report(reg, build_baseline())
        self.assertEqual(drift, [], f"baseline drifted: {drift[:3]}")


class FpBaselineDrift(unittest.TestCase):
    """The CI gate semantics: new FP-relevant output on a hard negative
    is reported, tolerance band respected."""

    def _base(self):
        return build_baseline()

    def test_new_signal_on_hard_negative_is_drift(self):
        current = self._base()
        victim = sorted(current["fixtures"])[0]
        current["fixtures"][victim]["signals"].append("brand_new_marker")
        drift = compare_baselines(self._base(), current)
        self.assertTrue(any(d["type"] == "signal_added" and
                            d["fixture"] == victim for d in drift), drift)

    def test_score_change_beyond_tolerance_is_drift(self):
        committed = self._base()
        current = json.loads(json.dumps(committed))
        victim = sorted(current["fixtures"])[0]
        current["fixtures"][victim]["slop_score"] += 0.05
        drift = compare_baselines(committed, current)
        self.assertTrue(any(d["type"] == "score_drift" and
                            d["fixture"] == victim for d in drift), drift)

    def test_score_change_within_tolerance_is_not_drift(self):
        committed = self._base()
        current = json.loads(json.dumps(committed))
        victim = sorted(current["fixtures"])[0]
        current["fixtures"][victim]["slop_score"] += 0.005
        self.assertEqual(compare_baselines(committed, current), [])

    def test_missing_fixture_is_drift(self):
        committed = self._base()
        current = json.loads(json.dumps(committed))
        victim = sorted(current["fixtures"])[0]
        del current["fixtures"][victim]
        drift = compare_baselines(committed, current)
        self.assertTrue(any(d["type"] == "fixture_missing" for d in drift))


class FpBaselineCLI(unittest.TestCase):
    def test_check_mode_green_on_committed_baseline(self):
        proc = subprocess.run([sys.executable, SCRIPT, "--check"],
                              cwd=ROOT, capture_output=True, text=True)
        self.assertEqual(proc.returncode, 0, proc.stdout + proc.stderr)

    def test_check_mode_red_when_baseline_stale(self):
        """Tampered copy (one extra tolerated signal removed) must fail."""
        import tempfile
        with tempfile.TemporaryDirectory() as d:
            with open(BASELINE, encoding="utf-8") as f:
                reg = json.load(f)
            victim = next(fid for fid in sorted(reg["fixtures"])
                           if reg["fixtures"][fid]["signals"])
            reg["fixtures"][victim]["signals"] = reg["fixtures"][victim]["signals"][:-1]
            tampered = os.path.join(d, "fp_baseline.json")
            with open(tampered, "w", encoding="utf-8") as f:
                json.dump(reg, f)
            proc = subprocess.run(
                [sys.executable, SCRIPT, "--check", "--baseline", tampered],
                cwd=ROOT, capture_output=True, text=True)
            self.assertNotEqual(proc.returncode, 0)
            self.assertIn("signal_added", proc.stdout + proc.stderr)


if __name__ == "__main__":
    unittest.main()
