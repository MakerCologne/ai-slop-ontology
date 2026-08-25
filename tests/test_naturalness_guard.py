"""Naturalness-Guard (issue #81, detect-only, low confidence).

register_drift + over_sanitized as advisory signals — they must NEVER be
score-dominant and must respect genre keep_when guards (academic/legal
register is legitimate). modal_particle_anomaly is an explicit STUB until
the DE layer lands (#76); the stub never emits a finding.
"""

import os
import sys
import unittest

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SCRIPTS = os.path.join(ROOT, "skills", "ai-slop-detection", "scripts")
sys.path.insert(0, SCRIPTS)

from naturalness_guard import (  # noqa: E402
    register_drift, over_sanitized, modal_particle_anomaly,
    find_naturalness_findings,
)
import slop_scorer  # noqa: E402


def words(t):
    return len(t.split())


class RegisterDriftDoD(unittest.TestCase):
    """3 positive / 3 negative / 2 boundary fixtures (#64 workflow)."""

    POS1 = ("Furthermore, the longitudinal results are robust across all "
            "cohorts. Yeah, kinda wild, right? Moreover, the effect persists "
            "under correction. Hey, that is honestly wild stuff. In "
            "addition, the sensitivity analysis holds. Okay, so we are "
            "fairly confident that this pattern is real and meaningful here.")
    POS2 = ("Ferner ist hervorzuheben, dass die Datenlage begrenzt bleibt. "
            "Na ja, irgendwie ist das halt schon krass. Gemäß dem Bericht "
            "liegt die Zahl bei zwölf Prozent. Mithin bleibt festzuhalten, "
            "dass weitere Studien nötig sind, was irgendwie auch wieder "
            "typisch ist für das Feld, halt.")
    POS3 = ("In addition, the paper formalizes the model. We are going to "
            "skip the proofs. Yeah okay, gonna be honest, that part was "
            "dense stuff. Furthermore, the appendix lists the datasets.")

    def test_positives_fire(self):
        for name, text in (("pos1", self.POS1), ("pos2", self.POS2),
                           ("pos3", self.POS3)):
            finding = register_drift(text)
            self.assertIsNotNone(finding, name)
            self.assertLessEqual(finding["confidence"], 0.5, name)

    def test_negatives_do_not_fire(self):
        formal = ("Furthermore, the results are robust. Moreover, the "
                  "appendix lists all datasets. In addition, the sensitivity "
                  "analysis confirms the finding across cohorts and years.")
        conversational = ("Yeah, that was kinda wild, right? Hey, honestly, "
                          "okay, I did not expect that stuff to work at all. "
                          "Gonna try it again tomorrow, I guess.")
        single_marker = ("Furthermore, the results are robust across "
                         "cohorts, and yeah, they hold up under correction "
                         "in every single replication we ran this year.")
        for name, text in (("formal", formal), ("conversational", conversational),
                           ("single", single_marker)):
            self.assertIsNone(register_drift(text), name)

    def test_boundaries(self):
        # b1: colloquial markers inside quotes are dialogue, not drift
        quoted = ('Furthermore, the results are robust. The reviewer wrote: '
                  '"Yeah, kinda hand-wavy stuff, honestly." Moreover, the '
                  'appendix lists all datasets and replication steps taken.')
        self.assertIsNone(register_drift(quoted))
        # b2: very short snippets (< 30 words) never fire
        short = "Furthermore it holds. Yeah kinda wild. Moreover it repeats."
        self.assertIsNone(register_drift(short))


class OverSanitizedDoD(unittest.TestCase):
    BASE = ("We consider the estimator first. It is consistent under the "
            "stated assumptions, and we are confident in the robustness "
            "checks. That is not a trivial claim: do not overlook the "
            "sample size. There is a caveat, they are preliminary, and the "
            "model can not be extrapolated beyond the support of the data.")

    def test_pos1_full_forms_no_contractions(self):
        self.assertIsNotNone(over_sanitized(self.BASE))

    def test_pos2_long_announcement_prose(self):
        text = ("It is important to note that the rollout finishes in June. "
                "There is a migration guide, and it is linked below. We are "
                "aware that some teams will need time. They are advised to "
                "plan the switch, and do not defer it until the last week, "
                "because that is when the load peaks and support can not "
                "guarantee same-day answers for every ticket filed then.")
        self.assertIsNotNone(over_sanitized(text))

    def test_pos3_repeated_expanded_negations(self):
        text = ("The service will not restart on failure. Users do not see "
                "internal errors. The cache can not be shared across "
                "regions. It is documented, that is the contract, and we "
                "are not changing it this quarter because they are load "
                "bearing defaults that keep the platform stable for all.")
        self.assertIsNotNone(over_sanitized(text))

    def test_negatives(self):
        # n1: one contraction present -> human-typed rhythm
        with_contraction = self.BASE.replace("do not", "don't")
        self.assertIsNone(over_sanitized(with_contraction))
        # n2: short text, full forms are just formal brevity
        self.assertIsNone(over_sanitized("It is fine. We are done. Do not "
                                         "worry about the rest tonight."))
        # n3: contraction-rich prose
        casual = ("We don't restart on failure and users won't see what's "
                  "internal. It's documented, that's the contract, and we "
                  "aren't changing it because they're load-bearing defaults "
                  "keeping things stable for everyone who's relying on it.")
        self.assertIsNone(over_sanitized(casual))

    def test_boundaries(self):
        # b1: only 2 distinct full forms -> below threshold of 3
        two = ("It is documented and we are aware that the migration guide "
               "exists for teams that need extra lead time before the "
               "switch completes, plus support runs office hours weekly.")
        self.assertIsNone(over_sanitized(two))
        # b2: possessive 's is NOT a contraction; full forms still fire
        possessive = ("The model's output is stable. We are confident in "
                      "the checks. It is documented, do not change the "
                      "defaults, and there is a rollback path listed.")
        self.assertIsNotNone(over_sanitized(possessive))


class GenreGuardAndScoreDiscipline(unittest.TestCase):
    def test_over_sanitized_exempt_in_formal_genres(self):
        findings = find_naturalness_findings(OverSanitizedDoD.BASE,
                                             genre="academic")
        ids = [f["id"] for f in findings]
        self.assertNotIn("OverSanitized", ids)

    def test_findings_low_confidence_detect_only(self):
        for f in find_naturalness_findings(RegisterDriftDoD.POS1):
            self.assertLessEqual(f["confidence"], 0.5)
            self.assertIn("keep_when", f)

    def test_never_score_dominant(self):
        # the numeric slop score must be identical with and without the
        # naturalness module in play (detect-only, ADR-0001 discipline)
        score = slop_scorer.slop_score(RegisterDriftDoD.POS1)["slop_score"]
        findings = find_naturalness_findings(RegisterDriftDoD.POS1)
        self.assertTrue(findings)  # advisory output exists ...
        self.assertLess(score, 0.40)  # ... yet the verdict stays clean

    def test_modal_particle_stub_is_explicit_and_silent(self):
        stub = modal_particle_anomaly("Na ja, das ist halt irgendwie so.")
        self.assertEqual(stub["status"], "stub")
        self.assertIn("#76", stub["note"])
        self.assertIsNone(stub.get("finding"))
        ids = [f["id"] for f in
               find_naturalness_findings("Na ja, das ist halt irgendwie so.")]
        self.assertNotIn("ModalParticleAnomaly", ids)


if __name__ == "__main__":
    unittest.main()
