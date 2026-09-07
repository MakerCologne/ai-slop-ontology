"""Central threshold config (issue #157 / GL #10).

The decision threshold lives in config/threshold.json and only there.
These tests pin the contract the issue demands:

1. A changed config value changes what every consumer sees (behavior
   follows the config — no silent divergence between sweep basis and
   operating scripts).
2. A missing config aborts cleanly with a hint, never falls back to a
   baked-in default (analogous to the key-hygiene test).
3. Malformed or out-of-range configs abort likewise.
4. The committed value is 0.40 — a ratchet note, not a law: the sweep
   (GL #6.3) may change it, and that change lands in the config file,
   visible in the diff, not in a script constant.
"""

import os
import sys
import tempfile
import unittest

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, "src"))

from threshold_config import load_threshold, CONFIG_PATH  # noqa: E402


class ThresholdConfigTest(unittest.TestCase):
    def test_committed_value_is_current_operating_point(self):
        # Ratchet: 0.40 until the sweep (GL #6.3) says otherwise. If this
        # fails after a sweep, the sweep updated a script constant instead
        # of the config — that is exactly the bug #157 closes.
        self.assertEqual(load_threshold(), 0.40)

    def test_behavior_follows_config(self):
        with tempfile.NamedTemporaryFile("w", suffix=".json", delete=False) as fh:
            fh.write('{"threshold": 0.41}')
            tmp = fh.name
        try:
            self.assertEqual(load_threshold(path=tmp), 0.41)
        finally:
            os.unlink(tmp)

    def test_missing_config_aborts_with_hint(self):
        with self.assertRaises(SystemExit) as ctx:
            load_threshold(path=os.path.join(tempfile.gettempdir(), "does-not-exist.json"))
        self.assertIn("missing", str(ctx.exception))
        self.assertIn("fallback", str(ctx.exception))

    def test_invalid_json_aborts(self):
        with tempfile.NamedTemporaryFile("w", suffix=".json", delete=False) as fh:
            fh.write("{not json")
            tmp = fh.name
        try:
            with self.assertRaises(SystemExit):
                load_threshold(path=tmp)
        finally:
            os.unlink(tmp)

    def test_non_numeric_field_aborts(self):
        with tempfile.NamedTemporaryFile("w", suffix=".json", delete=False) as fh:
            fh.write('{"threshold": "high"}')
            tmp = fh.name
        try:
            with self.assertRaises(SystemExit):
                load_threshold(path=tmp)
        finally:
            os.unlink(tmp)

    def test_out_of_range_aborts(self):
        for bad in (0.0, 1.0, 1.5, -0.1):
            with tempfile.NamedTemporaryFile("w", suffix=".json", delete=False) as fh:
                fh.write('{"threshold": %s}' % bad)
                tmp = fh.name
            try:
                with self.assertRaises(SystemExit):
                    load_threshold(path=tmp)
            finally:
                os.unlink(tmp)

    def test_config_file_exists_in_repo(self):
        self.assertTrue(os.path.isfile(CONFIG_PATH), CONFIG_PATH)


if __name__ == "__main__":
    unittest.main()
