"""
Benchmark reporting honesty (review 2026-08 §2.3).

The headline F1 was a training-set number — the skill scorer's weights are
calibrated by eval/calibrate.py on the same corpus run_benchmark.py reports
on — and per-language accuracies were printed for languages with two examples.
"""

import os
import sys
import unittest

ROOT = os.path.join(os.path.dirname(__file__), "..")
sys.path.insert(0, os.path.join(ROOT, "eval"))
sys.path.insert(0, os.path.join(ROOT, "src"))
sys.path.insert(0, os.path.join(ROOT, "skills", "ai-slop-detection", "scripts"))

import run_benchmark


class TestInSampleLabelling(unittest.TestCase):
    def test_report_states_that_the_default_run_is_in_sample(self):
        results = run_benchmark.run()
        report = run_benchmark.format_report(results)
        self.assertIn("in-sample", report)
        self.assertIn("--cross-validate", report)

    def test_small_language_samples_are_not_reported_as_accuracy(self):
        results = run_benchmark.run()
        for r in results:
            for lang, acc in r["per_language_accuracy"].items():
                n = r["per_language_n"][lang]
                if n < run_benchmark.MIN_LANG_N:
                    self.assertIsNone(acc, f"{lang} reported an accuracy over {n}")
                else:
                    self.assertIsNotNone(acc)

    def test_report_shows_sample_size_instead_of_a_fake_ratio(self):
        report = run_benchmark.format_report(run_benchmark.run())
        self.assertIn("n/a (n=", report)


class TestCrossValidation(unittest.TestCase):
    """Wiring only — a real calibration run takes minutes and is opt-in."""

    def test_folds_are_stratified_and_cover_the_corpus(self):
        import calibrate as calibration
        original = calibration.calibrate
        seen_train_sizes = []

        def fake_calibrate(items, *a, **kw):
            seen_train_sizes.append(len(items))
            return {"weights": None, "metrics": {}}

        calibration.calibrate = fake_calibrate
        try:
            summaries = run_benchmark.cross_validate(folds=5)
        finally:
            calibration.calibrate = original

        self.assertEqual(len(summaries), 2)          # scorer and pipeline
        self.assertEqual(len(seen_train_sizes), 5)   # one calibration per fold
        total = summaries[0]["n"]
        self.assertEqual(total, 53)                  # every item held out once
        # fold sizes differ by at most one item
        self.assertLessEqual(max(seen_train_sizes) - min(seen_train_sizes), 1)


if __name__ == "__main__":
    unittest.main()
