"""Tests for reinventing-wheel detection (issue #32) — detect-only."""

import os
import sys
import unittest

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SCRIPTS = os.path.join(ROOT, "skills", "ai-slop-detection", "scripts")
sys.path.insert(0, SCRIPTS)

from reinventing_wheel import detect_reinventing_wheel


WHEEL_PY = '''
def compute_stats(values, weights=None):
    """Weighted mean and stdev of values."""
    return ...

def compute_statistics(values, weights=None):
    """Aggregate summary of the dataset."""
    return ...
'''

DELEGATING_PY = '''
def compute_stats(values, weights=None):
    """Weighted mean and stdev of values."""
    return ...

def compute_statistics(values, weights=None):
    """Compat shim; delegates to compute_stats."""
    return compute_stats(values, weights)
'''

DISSIMILAR_PY = '''
def load_config(path):
    """Load YAML config."""
    return ...

def save_config(path, data):
    """Write YAML config back to disk."""
    return ...
'''


class ReinventingWheelTests(unittest.TestCase):
    def test_similar_function_without_reference_fires(self):
        hits = detect_reinventing_wheel(WHEEL_PY)
        self.assertEqual(len(hits), 1)
        hit = hits[0]
        self.assertEqual(hit["category"], "reinventing-wheel")
        self.assertEqual(hit["new_function"], "compute_statistics")
        self.assertGreaterEqual(hit["similarity"], 0.8)
        self.assertFalse(hit["referenced_existing"])

    def test_docstring_reference_does_not_fire(self):
        self.assertEqual(detect_reinventing_wheel(DELEGATING_PY), [])

    def test_dissimilar_signatures_do_not_fire(self):
        self.assertEqual(detect_reinventing_wheel(DISSIMILAR_PY), [])

    def test_syntax_error_returns_empty(self):
        self.assertEqual(detect_reinventing_wheel("def broken(:"), [])


if __name__ == "__main__":
    unittest.main()
