"""Issue #232 / P5: Prevention-Contract-Harness (L2) — L1-Tests der Messlogik."""
import sys
import unittest
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO / "eval" / "prevention-contract"))
sys.path.insert(0, str(REPO / "skills" / "ai-slop-detection" / "scripts"))

from measure_variants import criteria_vector, distance  # noqa: E402

SLOP = ("Danke fuer diesen spannenden Beitrag! Sie beschreiben, dass Prozesswissen "
        "verloren geht. Ein weiterer Aspekt ist die Speicherung. Wie sichern Sie das langfristig?")
LEGIT_WIDERSPRUCH = ("Ich widerspreche dem Fazit: Die Ausfallzeiten sind im Quartalsvergleich "
                     "gesunken, die Zahlen belegen das Gegenteil.")
LEGIT_FRAGE = ("Welche Puffergroesse verwenden Sie fuer die Synthese bei pH 7?")

class PreventionContractTest(unittest.TestCase):
    def test_tp_slop_comment_flags(self):
        v = criteria_vector(SLOP)
        self.assertTrue(v["C3_engagement_seq"] or v["C4_announce_frame"])

    def test_hn_stance_ich_is_content(self):
        # Haltung + Beleg = Inhalt, kein Anlauf (C1 darf nicht feuern)
        self.assertFalse(criteria_vector(LEGIT_WIDERSPRUCH)["C1_ich_opener"])

    def test_hn_direct_question_clean(self):
        v = criteria_vector(LEGIT_FRAGE)
        self.assertFalse(any(v[k] for k in v if k.startswith("C")))

    def test_c8_distance_separates_structures(self):
        a = criteria_vector(LEGIT_FRAGE)
        b = criteria_vector(SLOP)
        self.assertGreaterEqual(distance(a, b), 1.0)

if __name__ == "__main__":
    unittest.main()
