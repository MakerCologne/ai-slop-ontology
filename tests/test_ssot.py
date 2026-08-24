"""
Issue #49 — SSOT: ontology.json as source of truth, enforced by a sync check.

The blind-spot audit (E1) found that the detection scripts carry their
signal lists inline instead of reading them from ontology.json. Full
migration is deliberately out of scope here (too risky for one issue);
this batch ships the two risk-free pieces:

1. scripts/generate_signal_defs.py — deterministic, data-only view of
   ontology.json as src/signal_defs_generated.py (no code, no behavior).
2. scripts/check_ssot.py — offline gate:
   - the skill's vendored copy references/ontology.json must be
     byte-identical to the root ontology.json (data SSOT),
   - src/signal_defs_generated.py must be current (regeneration drift),
   - every signal-bearing top-level constant in the detection modules
     must be registered in the SSOT register (source + status), so a new
     inline signal list cannot appear without a conscious decision.

The check runs as this test — drift becomes CI-enforced.
"""

import os
import subprocess
import sys
import unittest

ROOT = os.path.join(os.path.dirname(__file__), "..")


class TestSSOTSync(unittest.TestCase):
    def test_generated_signal_defs_exist_and_carry_ontology_version(self):
        path = os.path.join(ROOT, "src", "signal_defs_generated.py")
        self.assertTrue(
            os.path.exists(path),
            "src/signal_defs_generated.py missing — run scripts/generate_signal_defs.py",
        )
        with open(path, encoding="utf-8") as fh:
            content = fh.read()
        self.assertIn("ONTOLOGY_DATE", content)
        self.assertIn("DETECTION_SIGNALS_STRUCTURED", content)

    def test_check_ssot_passes(self):
        script = os.path.join(ROOT, "scripts", "check_ssot.py")
        self.assertTrue(os.path.exists(script), "scripts/check_ssot.py missing")
        proc = subprocess.run(
            [sys.executable, script],
            capture_output=True,
            text=True,
            cwd=ROOT,
        )
        self.assertEqual(
            proc.returncode, 0,
            f"check_ssot.py failed:\n{proc.stdout}\n{proc.stderr}",
        )
        self.assertIn("SSOT check passed", proc.stdout)

    def test_skill_ontology_copy_is_byte_identical(self):
        root = os.path.join(ROOT, "ontology.json")
        copy = os.path.join(
            ROOT, "skills", "ai-slop-detection", "references", "ontology.json"
        )
        with open(root, "rb") as fh:
            root_bytes = fh.read()
        with open(copy, "rb") as fh:
            copy_bytes = fh.read()
        self.assertEqual(root_bytes, copy_bytes)


if __name__ == "__main__":
    unittest.main()
