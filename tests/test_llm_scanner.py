"""LLM-Zweit-Scanner Layer 2 (issue #57, advisory only).

Vertrag aus docs/loop-guards/57-llm-zweit-scanner.md:

- Layer 2 gegen die deterministische Schicht: nur Veto/Befund mit
  zitiertem Textabschnitt, NIE alleiniges Abbruchkriterium.
- Prompt-Rotation über >=3 Varianten (Signal-Reihenfolge + Frageform).
- Position-Swap: jede Variante läuft mit Vorwärts- und Rückwärts-
  Reihenfolge der Signale; Instabilität downgradet den Befund auf
  "unsicher" statt einen Fix zu triggern.
- Bias-Akzeptanz: vertauschte Positionen liefern stabile Befunde
  (Uebereinstimmung >= 0.9 ueber alle Laeufe eines Scans).
- Keine Selbstkorrektur-Runden ohne externes Feedback: genau ein Pass,
  deterministische, endliche Judge-Aufrufzahl.

Der Judge ist injizierbar (callable: prompt -> str) — Tests verwenden
Fake-Judges, kein Netzwerk, keine echte Modell-API im Testpfad.
"""

import json
import os
import sys
import unittest

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SCRIPTS = os.path.join(ROOT, "skills", "ai-slop-detection", "scripts")
sys.path.insert(0, SCRIPTS)

import llm_scanner  # noqa: E402
from llm_scanner import run_llm_scan  # noqa: E402


TEXT = ("In today's rapidly evolving digital landscape, it is important to "
        "note that this revolutionary platform leverages cutting-edge "
        "technology to deliver game-changing results across the board. "
        "Furthermore, the team believes that this holistic approach will "
        "ultimately reshape the entire industry going forward.")

CLEAN = ("The estimator is consistent under the stated assumptions. We "
         "prove consistency in Section 3 and report the coverage of the "
         "confidence intervals in Table 2. All code and datasets are "
         "available in the repository.")


def make_stable_judge(finding):
    """Returns findings identically, independent of prompt/order."""
    payload = json.dumps([finding])

    def judge(prompt):
        return payload
    return judge


def make_position_biased_judge(favorite_id, finding):
    """Fires only when its favorite signal is listed FIRST (position bias)."""
    def judge(prompt):
        listed = llm_scanner.extract_signal_order(prompt)
        if listed and listed[0] == favorite_id:
            return json.dumps([finding])
        return "[]"
    return judge


def make_garbage_judge():
    def judge(prompt):
        return "I am certain this text is slop!!! (no json)"
    return judge


class StableJudgeDoD(unittest.TestCase):
    """3 positive / 3 negative / 2 boundary fixtures (#64 workflow)."""

    def test_pos1_stable_finding_survives(self):
        f = {"signal_id": "template_phrases",
             "evidence_quote": "In today's rapidly evolving digital landscape"}
        result = run_llm_scan(TEXT, judge=make_stable_judge(f),
                              signals=["template_phrases", "buzzwords"])
        self.assertEqual(result["status"], "ok")
        self.assertEqual(len(result["findings"]), 1)
        out = result["findings"][0]
        self.assertEqual(out["signal_id"], "template_phrases")
        self.assertEqual(out["stability"], "stable")
        self.assertGreaterEqual(out["agreement"], 0.9)
        self.assertLessEqual(out["confidence"],
                             llm_scanner.ADVISORY_MAX_CONFIDENCE)
        self.assertIn(out["evidence_quote"], TEXT)

    def test_pos2_advisory_layer_never_score_dominant(self):
        f = {"signal_id": "buzzwords",
             "evidence_quote": "cutting-edge"}
        result = run_llm_scan(TEXT, judge=make_stable_judge(f))
        for finding in result["findings"]:
            self.assertEqual(finding["layer"], "advisory")
            self.assertFalse(finding["is_fix_trigger"])
            self.assertEqual(finding["suggested_action"], "review")

    def test_pos3_veto_semantics_clean_text(self):
        # Judge sieht nichts -> explizites clean-Votum, kein Befund
        result = run_llm_scan(CLEAN, judge=_clean_judge(),
                              signals=["template_phrases"])
        self.assertEqual(result["findings"], [])
        self.assertEqual(result["verdict"], "clean")

    def test_neg1_no_self_correction_rounds(self):
        calls = []

        def judge(prompt):
            calls.append(prompt)
            return json.dumps([{"signal_id": "buzzwords",
                                "evidence_quote": "game-changing"}])
        run_llm_scan(TEXT, judge=judge, signals=["buzzwords", "template_phrases"])
        expected = len(llm_scanner.PROMPT_VARIANTS) * 2  # forward + swapped
        self.assertEqual(len(calls), expected)

    def test_neg2_short_text_skipped(self):
        result = run_llm_scan("Zu kurz.", judge=_clean_judge())
        self.assertEqual(result["status"], "skipped_short")
        self.assertEqual(result["findings"], [])

    def test_neg3_malformed_judge_never_crashes(self):
        result = run_llm_scan(TEXT, judge=make_garbage_judge(),
                              signals=["buzzwords"])
        self.assertEqual(result["status"], "inconclusive")
        self.assertEqual(result["findings"], [])
        self.assertGreaterEqual(result["parse_failures"],
                                len(llm_scanner.PROMPT_VARIANTS))

    def test_boundary1_position_bias_downgrades_to_unsicher(self):
        # Judge feuert nur bei bevorzugter Position -> Instabilitaet
        f = {"signal_id": "buzzwords", "evidence_quote": "game-changing"}
        judge = make_position_biased_judge("buzzwords", f)
        result = run_llm_scan(TEXT, judge=judge,
                              signals=["buzzwords", "template_phrases"])
        self.assertEqual(len(result["findings"]), 1)
        out = result["findings"][0]
        self.assertEqual(out["stability"], "unsicher")
        self.assertLess(out["confidence"],
                        llm_scanner.ADVISORY_MAX_CONFIDENCE)
        self.assertFalse(out["is_fix_trigger"])

    def test_boundary2_quote_must_come_from_text(self):
        # Befund mit erfundenem Zitat wird verworfen, nicht gemeldet
        f = {"signal_id": "buzzwords", "evidence_quote": "quantum synergy flux"}
        result = run_llm_scan(TEXT, judge=make_stable_judge(f))
        self.assertEqual(result["findings"], [])


class RotationContract(unittest.TestCase):

    def test_at_least_three_variants(self):
        self.assertGreaterEqual(len(llm_scanner.PROMPT_VARIANTS), 3)

    def test_variant_prompts_differ_in_question_form(self):
        renders = set()
        for template in llm_scanner.PROMPT_VARIANTS:
            rendered = llm_scanner.render_prompt(template, TEXT,
                                                 ["a", "b"])
            renders.add(rendered)
            self.assertIn(TEXT, rendered)
            self.assertIn("a", rendered)
        self.assertGreaterEqual(len(renders), 3)

    def test_swapped_order_actually_swaps(self):
        fwd = llm_scanner.render_prompt(llm_scanner.PROMPT_VARIANTS[0], TEXT,
                                        ["buzzwords", "template_phrases"])
        rev = llm_scanner.render_prompt(llm_scanner.PROMPT_VARIANTS[0], TEXT,
                                        ["template_phrases", "buzzwords"])
        self.assertNotEqual(fwd, rev)
        fwd_pos = fwd.find("buzzwords")
        rev_pos = rev.find("buzzwords")
        self.assertLess(fwd_pos, rev_pos)


class BiasAcceptance(unittest.TestCase):
    """Akzeptanz aus dem Vertrag: >=90 % Uebereinstimmung bei getauschten
    Positionen auf dem Control-Set (hier: stabiler Fake-Judge)."""

    CONTROL_SET = [
        (TEXT, {"signal_id": "template_phrases",
                "evidence_quote": "In today's rapidly evolving digital landscape"}),
        (CLEAN + " " + "The proofs are standard.", None),
        ("Der Bericht leveragt innovative Synergien fuer alle Stakeholder, "
         "denkt outside the box und liefert einen holistic Mehrwert, der "
         "die gesamte Branche nachhaltig transformieren wird.",
         {"signal_id": "buzzwords",
          "evidence_quote": "Synergien"}),
    ]

    def test_stable_judge_hits_90_percent_on_control_set(self):
        for text, finding in self.CONTROL_SET:
            judge = _clean_judge() if finding is None \
                else make_stable_judge(finding)
            result = run_llm_scan(text, judge=judge,
                                  signals=["template_phrases", "buzzwords"])
            if finding is None:
                self.assertEqual(result["findings"], [], text[:40])
                continue
            self.assertTrue(result["findings"], text[:40])
            self.assertGreaterEqual(result["findings"][0]["agreement"], 0.9,
                                    text[:40])


class ScoreDiscipline(unittest.TestCase):

    def test_llm_findings_not_wired_into_scorer(self):
        import slop_scorer
        import inspect
        src = inspect.getsource(slop_scorer)
        self.assertNotIn("llm_scanner", src)
        self.assertNotIn("run_llm_scan", src)


def _clean_judge():
    def judge(prompt):
        return "[]"
    return judge


if __name__ == "__main__":
    unittest.main()
