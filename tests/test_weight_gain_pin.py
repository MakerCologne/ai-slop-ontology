"""Doku-Pin für die Gewichts-Einordnung (#106, Muster: fp_baseline #80/#85).

docs/SCORE-GOVERNANCE.md und der Herkunfts-Kommentar in slop_scorer.py
nennen konkrete Zahlen für den Beitrag der 14-dimensionalen Kalibrierung
gegenüber uniformen Gewichten (1/N). Dieser Test bindet genau diese Zahlen
an ihre Messvorschrift: Wechsel der Korpuslage, des Thresholds oder der
Aggregation ändern die Zahlen — dann muss die Doku mitziehen, nicht stumm
altern (#85-Fehlerklasse).

Messvorschrift: eval/corpus.jsonl (n=331), Threshold aus
config/threshold.json, Uniform = 1/N über die Scorer-Dimensionen.
"""

import json
import os
import sys
import unittest

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, "eval"))
sys.path.insert(0, os.path.join(ROOT, "src"))
sys.path.insert(0, os.path.join(ROOT, "skills", "ai-slop-detection", "scripts"))

import slop_scorer  # noqa: E402
from threshold_config import load_threshold  # noqa: E402

import calibrate  # noqa: E402

CORPUS = os.path.join(ROOT, "eval", "corpus.jsonl")
CONTROL = os.path.join(ROOT, "eval", "control_set.jsonl")

THRESHOLD = load_threshold()

# Pin-Stand 2026-09-09 (docs/SCORE-GOVERNANCE.md, Abschnitt #106):
PIN_UNIFORM = {"tp": 216, "fp": 0, "tn": 110, "fn": 5}
PIN_DEFAULT = {"tp": 217, "fp": 0, "tn": 110, "fn": 4}
# Risik-Tier-Beitrag (der eigentliche messbare Kalibrierungseffekt):
PIN_UNIFORM_TIER2 = 0   # uniform: kein Korpus-Slop-Text erreicht 0.70
PIN_DEFAULT_TIER2 = 24  # kalibriert: 24 Texte im "Slop"-Tier (>= 0.70)


def _load(path):
    with open(path, encoding="utf-8") as f:
        return [json.loads(l) for l in f if l.strip()]


class WeightGainPin(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.items = _load(CORPUS)
        cls.control = _load(CONTROL)
        cls.uniform = calibrate.uniform_weights()
        cls.default = dict(slop_scorer.DEFAULT_WEIGHTS)

    def test_pinned_contribution_corpus(self):
        m_uni = calibrate.metrics(self.uniform, self.items, THRESHOLD)
        m_def = calibrate.metrics(self.default, self.items, THRESHOLD)
        for key, pin in PIN_UNIFORM.items():
            self.assertEqual(m_uni[key], pin,
                             f"uniform {key} driftete: {m_uni[key]} != {pin} "
                             f"— SCORE-GOVERNANCE.md #106 aktualisieren")
        for key, pin in PIN_DEFAULT.items():
            self.assertEqual(m_def[key], pin,
                             f"DEFAULT_WEIGHTS {key} driftete: {m_def[key]} "
                             f"!= {pin} — SCORE-GOVERNANCE.md #106 aktualisieren")

    def test_pinned_tier_contribution(self):
        """Binärdetektion treibt die Escalation-Gate; die Gewichte zahlen
        vor allem im Risk-Tier (>= 0.70) ein — diese Zahl steht so in der
        Doku und ist hier gepinnt."""
        t_uni = calibrate.tier_counts(self.uniform, self.items)
        t_def = calibrate.tier_counts(self.default, self.items)
        uni2 = t_uni["severe"] + t_uni["slop"]
        def2 = t_def["severe"] + t_def["slop"]
        self.assertEqual(uni2, PIN_UNIFORM_TIER2)
        self.assertEqual(def2, PIN_DEFAULT_TIER2)

    def test_control_set_weight_invariance(self):
        """Ablation auf dem Control Set (DoD #106.1): kein Eintrag wechselt
        die Klassifikation zwischen uniform und kalibriert — dort liegt
        kein versteckter Kalibrierungsgewinn."""
        for item in self.control:
            s_uni = slop_scorer.slop_score(
                item["text"], weights=self.uniform)["slop_score"]
            s_def = slop_scorer.slop_score(
                item["text"], weights=self.default)["slop_score"]
            self.assertEqual(
                s_uni >= THRESHOLD, s_def >= THRESHOLD,
                f"{item['id']} flippt zwischen uniform ({s_uni}) und "
                f"DEFAULT ({s_def}) — Doku-Ablation prüfen")

    def test_hard_negative_headroom(self):
        """Kalibrierte Gewichte erhöhen die Hard-Negative-Scores (weniger
        FP-Headroom bis zum Threshold) — dokumentierte Nebenwirkung, hier
        gepinnt, damit stiller FP-Drift auffällt."""
        cleans = [i for i in self.items if i["label"] != "slop"]
        max_uni = max(slop_scorer.slop_score(
            i["text"], weights=self.uniform)["slop_score"] for i in cleans)
        max_def = max(slop_scorer.slop_score(
            i["text"], weights=self.default)["slop_score"] for i in cleans)
        self.assertAlmostEqual(max_uni, 0.218, delta=0.01)
        self.assertAlmostEqual(max_def, 0.342, delta=0.01)
        self.assertLess(max_def, THRESHOLD,
                        "Hard-Negative-Maximum über Threshold — FP!")


if __name__ == "__main__":
    unittest.main()
