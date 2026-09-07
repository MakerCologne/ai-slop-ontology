"""
#156 FP guard: 'Best Practices' is a common legitimate term in German dev
docs and release notes. It must only count as a German AI marker when
coupled with a generic intensifier ('allen', 'branchenweit', 'modernen',
'gängigen', 'sämtlichen'); plain references must not push the multilingual
signal over the >=2-hit threshold.
"""
import sys
import unittest

sys.path.insert(0, ".")
try:
    from classifier import SlopClassifier
except ImportError:
    from src.classifier import SlopClassifier

# One plain german marker (from buzzwords) + 'Best Practices'
FP_TEXT = (
    "Das Migrationsskript folgt den Best Practices für Versionierte "
    "Migrationen und ist im Wiki dokumentiert. Ein tiefgreifender Wandel "
    "war das nicht, aber der Prozess ist jetzt stabil."
)

TP_TEXT = (
    "Wir folgen allen Best Practices der Branche, und im heutigen "
    "schnelllebigen digitalen Zeitalter ist das ein Muss."
)


class TestBestPracticesContextGuard(unittest.TestCase):
    def setUp(self):
        self.clf = SlopClassifier()

    def test_plain_best_practices_is_not_a_marker(self):
        result = self.clf.classify_text(FP_TEXT)
        self.assertFalse(
            any(s.signal_id == "Multilingual_german" for s in result.signals_detected),
            f"'Best Practices' must not count as german marker without intensifier; "
            f"got {[s.signal_id for s in result.signals_detected]}",
        )

    def test_intensifier_coupled_best_practices_counts(self):
        result = self.clf.classify_text(TP_TEXT)
        self.assertTrue(
            any(s.signal_id == "Multilingual_german" for s in result.signals_detected),
            f"expected german signal with 'allen Best Practices' + second marker; "
            f"got {[s.signal_id for s in result.signals_detected]}",
        )

    def test_conditional_marker_in_ontology(self):
        import json
        ontology = json.load(open("ontology.json"))
        german = ontology["signals"]["multilingual"]["german"]
        self.assertNotIn("Best Practices", german["buzzwords"])
        rule = german["conditional_buzzwords"]["Best Practices"]
        self.assertIn("modernen", [i.lower() for i in rule["intensifiers"]])
        self.assertGreater(rule.get("window_chars", 0), 0)
        self.assertTrue(rule.get("keep_when"))


if __name__ == "__main__":
    unittest.main()
