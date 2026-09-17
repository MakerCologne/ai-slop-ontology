"""Issue #35 — triggered_by: domain signal metadata.

A signal with a `triggered_by: domain` binding in ontology.json
(`signalDomains.signals`) is only evaluated when classify_text receives a
matching `domain` scope. Unbound signals and the no-argument call stay
backwards compatible.
"""

import json
import os
import unittest

ROOT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..")
import sys

sys.path.insert(0, os.path.join(ROOT, "src"))

from classifier import SlopClassifier


ONTOLOGY_PATH = os.path.join(ROOT, "ontology.json")


class TestDomainTrigger(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.clf = SlopClassifier(ONTOLOGY_PATH)

    def test_signal_domains_section_exists(self):
        with open(ONTOLOGY_PATH) as f:
            onto = json.load(f)
        sd = onto.get("signalDomains", {}).get("signals", {})
        self.assertGreaterEqual(len(sd), 5,
                                "issue #35 requires >= 5 pilot signals")
        for signal_id, binding in sd.items():
            self.assertEqual(binding.get("triggered_by"), "domain",
                             f"{signal_id}: triggered_by must be 'domain'")
            self.assertTrue(binding.get("domains"),
                            f"{signal_id}: domains list must not be empty")
            self.assertIn("rationale", binding,
                          f"{signal_id}: rationale must be documented")

    def test_domain_gate_skips_bound_signal(self):
        # ExclamationExcess is bound away from ui_copy: heavy "!" usage is
        # legitimate register in UI copy and must not count as slop there.
        text = ("Wow! Amazing! Try it now! It works! Great job! "
                "Fantastic! Nice! Cool! Super! Love it! Wow!")
        base = self.clf.classify_text(text)
        self.assertTrue(
            any(s.signal_id == "ExclamationExcess" for s in base.signals_detected),
            "baseline (no domain) must detect ExclamationExcess")
        ui = self.clf.classify_text(text, domain="ui_copy")
        self.assertFalse(
            any(s.signal_id == "ExclamationExcess" for s in ui.signals_detected),
            "ui_copy scope must skip the domain-bound signal")
        self.assertTrue(
            any("domain_filter[ui_copy]" in n and "ExclamationExcess" in n
                for n in ui.notes),
            "the filter decision must be auditable via notes")

    def test_matching_domain_keeps_signal(self):
        text = ("Wow! Amazing! Try it now! It works! Great job! "
                "Fantastic! Nice! Cool! Super! Love it! Wow!")
        essay = self.clf.classify_text(text, domain="essay")
        self.assertTrue(
            any(s.signal_id == "ExclamationExcess" for s in essay.signals_detected),
            "essay is inside the binding's domains — signal must fire")

    def test_unbound_signals_unaffected(self):
        text = ("In today's rapidly evolving digital landscape, it's important "
                "to note that this rich tapestry of buzzwords is a testament "
                "to innovation. Furthermore, it's crucial to understand this.")
        base = self.clf.classify_text(text)
        scoped = self.clf.classify_text(text, domain="ui_copy")
        base_ids = {s.signal_id for s in base.signals_detected}
        scoped_ids = {s.signal_id for s in scoped.signals_detected}
        # Unbound signals (buzzword tier hits) must survive any domain scope.
        self.assertTrue(base_ids & scoped_ids,
                        "unbound signals must fire in every domain scope")

    def test_no_domain_argument_backwards_compatible(self):
        # Default call path must behave exactly as before the feature.
        text = "Delve into the realm of robust, seamless platforms."
        res = self.clf.classify_text(text)
        self.assertGreater(res.overall_slop_score, 0.0)

    def test_unknown_domain_blocks_bound_signals_only(self):
        text = ("Wow! Amazing! Try it now! It works! Great job! "
                "Fantastic! Nice! Cool! Super! Love it! Wow!")
        res = self.clf.classify_text(text, domain="changelog")
        self.assertFalse(
            any(s.signal_id == "ExclamationExcess" for s in res.signals_detected),
            "changelog is not in the binding's domains — signal must be skipped")


if __name__ == "__main__":
    unittest.main()
