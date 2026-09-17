"""Meta-regression (Issue #229 / P2): Anti-Slop must not seed new slop.

Every `example_fix` in RHETORICAL_PATTERNS must pass the repo's own detector
(find_rhetorical_patterns + rhythm_metrics) without a single finding. If a fix
recommendation itself trips a signal (see the RoboticRhythm case documented in
PR #225), it teaches readers a new template — exactly what the ontology exists
to prevent. This test locks the property in permanently: adding or editing an
example_fix that slops will fail CI.
"""

import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "skills" / "ai-slop-detection" / "scripts"))

from rhetorical_patterns import RHETORICAL_PATTERNS, find_rhetorical_patterns  # noqa: E402
from rhythm_openers import rhythm_metrics  # noqa: E402


def _iter_fixes():
    for pid, spec in sorted(RHETORICAL_PATTERNS.items()):
        fix = spec.get("example_fix")
        if fix:
            yield pid, fix


class ExampleFixMetaTest(unittest.TestCase):
    def test_every_example_fix_is_defined_for_every_pattern(self):
        fixes = list(_iter_fixes())
        self.assertGreaterEqual(len(fixes), 10, "example_fix inventory unexpectedly small")

    def test_no_example_fix_triggers_rhetorical_patterns(self):
        offenders = []
        for pid, fix in _iter_fixes():
            hits = {p["id"] for p in find_rhetorical_patterns(fix)}
            if hits:
                offenders.append((pid, fix, sorted(hits)))
        self.assertEqual(
            offenders, [],
            "example_fix values that trip the detector themselves: %r" % (offenders,),
        )

    def test_no_example_fix_triggers_rhythm_signals(self):
        offenders = []
        for pid, fix in _iter_fixes():
            signals = {s["id"] for s in rhythm_metrics(fix).get("signals", [])}
            if signals:
                offenders.append((pid, fix, sorted(signals)))
        self.assertEqual(
            offenders, [],
            "example_fix values with rhythm-signal findings: %r" % (offenders,),
        )


if __name__ == "__main__":
    unittest.main()
