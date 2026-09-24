"""Tests for micro-pattern detect-only signals (issue #13)."""

import os
import sys
import unittest

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SCRIPTS = os.path.join(ROOT, "skills", "ai-slop-detection", "scripts")
sys.path.insert(0, SCRIPTS)

from micro_patterns import find_micro_patterns, MICRO_PATTERNS


def ids(text):
    return {p["id"] for p in find_micro_patterns(text)}


class MicroPatternTests(unittest.TestCase):
    def test_each_pattern_has_keep_when_guard_and_examples(self):
        for pid, meta in MICRO_PATTERNS.items():
            self.assertIn("keep_when", meta, f"{pid} missing keep_when guard")
            self.assertIn("example_slop", meta)
            self.assertIn("example_fix", meta)

    # --- FalseAgency ---

    def test_false_agency_positive(self):
        self.assertIn("FalseAgency", ids("The data decides what matters next quarter."))
        self.assertIn("FalseAgency", ids("The strategy believes that customers want speed."))
        self.assertIn("FalseAgency", ids("The market realizes the price is too high."))

    def test_false_agency_negative_human_subject(self):
        self.assertNotIn("FalseAgency", ids("The team decides what matters next quarter."))
        self.assertNotIn("FalseAgency", ids("She believes that customers want speed."))

    def test_false_agency_negative_inanimate_verb(self):
        self.assertNotIn("FalseAgency", ids("The data shows what matters next quarter."))

    # --- FalseRange ---

    def test_false_range_positive_grand_sweep(self):
        self.assertIn(
            "FalseRange",
            ids("This guide covers everything from the Big Bang to dark matter."),
        )

    def test_false_range_negative_same_topic_everyday(self):
        self.assertNotIn(
            "FalseRange",
            ids("We migrated the service from the old cluster to the new cluster."),
        )
        self.assertNotIn(
            "FalseRange",
            ids("The tour goes from the kitchen to the living room."),
        )

    # --- RecapEnding ---

    def test_recap_ending_positive_opener_and_restatement(self):
        text = (
            "AI agents are transforming how teams write software and ship products. "
            "Several concrete tools appeared this year. "
            "In conclusion, AI agents are transforming how teams write software."
        )
        self.assertIn("RecapEnding", ids(text))

    def test_recap_ending_negative_no_overlap(self):
        text = (
            "The committee approved the new budget for the library on Tuesday. "
            "Construction begins in March. "
            "In conclusion, the funding covers three years of operating costs."
        )
        self.assertNotIn("RecapEnding", ids(text))

    def test_recap_ending_negative_overlap_without_opener(self):
        text = (
            "AI agents are transforming how teams write software. "
            "Put plainly: AI agents are transforming how teams write software."
        )
        self.assertNotIn("RecapEnding", ids(text))

    # --- HeadingRepeatedBelowItself ---

    def test_heading_repeated_positive(self):
        text = "## Deployment Steps\nDeployment steps are straightforward once configured.\n"
        self.assertIn("HeadingRepeatedBelowItself", ids(text))

    def test_heading_repeated_negative(self):
        text = "## Deployment Steps\nRun the installer and follow the prompts.\n"
        self.assertNotIn("HeadingRepeatedBelowItself", ids(text))

    def test_heading_repeated_negative_oneword(self):
        # A single shared word is not "2+ content words" repetition
        text = "## Testing\nTesting takes time.\n"
        self.assertNotIn("HeadingRepeatedBelowItself", ids(text))


    # --- ActorlessClaim ---

    def test_actorless_claim_positive_classic(self):
        self.assertIn(
            "ActorlessClaim",
            ids("Mistakes were made and the launch was delayed."),
        )

    def test_actorless_claim_positive_it_was_decided(self):
        self.assertIn(
            "ActorlessClaim",
            ids("It was decided that the feature would be removed."),
        )

    def test_actorless_claim_positive_passive_validation(self):
        self.assertIn(
            "ActorlessClaim",
            ids("Queries are validated before execution."),
        )

    def test_actorless_claim_negative_named_agent(self):
        self.assertNotIn(
            "ActorlessClaim",
            ids("Queries are validated by the gateway before execution."),
        )

    def test_actorless_claim_negative_policy_register(self):
        self.assertNotIn(
            "ActorlessClaim",
            ids("Invoices shall be retained for ten years."),
        )

    def test_actorless_claim_negative_descriptive_passive(self):
        self.assertNotIn(
            "ActorlessClaim",
            ids("The report was long and the meeting was short."),
        )

    def test_actorless_claim_negative_first_person(self):
        self.assertNotIn(
            "ActorlessClaim",
            ids("We decided to remove the feature."),
        )

    def test_every_example_fix_is_detector_clean(self):
        """#229 meta-safety: micro example_fixes must survive the detectors."""
        from rhetorical_patterns import find_rhetorical_patterns
        from rhythm_openers import rhythm_metrics
        for pid, meta in MICRO_PATTERNS.items():
            fix = meta["example_fix"]
            self.assertEqual(ids(fix), set(), f"{pid} example_fix triggers micro signals")
            self.assertEqual(
                find_rhetorical_patterns(fix), [],
                f"{pid} example_fix triggers rhetorical signals")
            self.assertEqual(
                rhythm_metrics(fix)["signals"], [],
                f"{pid} example_fix triggers rhythm signals")


class Fallstudie97PuritySalvationTests(unittest.TestCase):
    """#97 DoD: PurityBan / VibeScapegoat / SalvationModel FP=0 on hard
    negatives; positives fire per the annotated texts
    (docs/fallstudien/97-purity-vs-slopaganda.md, eval/human_ideological.jsonl)."""

    def test_purity_ban_positive_chain_phrase(self):
        self.assertIn("PurityBan", ids("AI IS THEFT. PASS IT ON."))

    def test_purity_ban_positive_de_purity_test(self):
        self.assertIn("PurityBan", ids(
            "Wer AI-Tools nutzt, hat als Mensch schon verloren."))
        self.assertIn("PurityBan", ids(
            "Jeder, der hier ein AI-Avatar hat, ist blockiert. Nicht verhandeln."))
        self.assertIn("PurityBan", ids(
            "Wer auch nur einen ihrer Posts teilt, ist Teil des Problems."))

    def test_purity_ban_negative_provenance_disclosure(self):
        # keep_when: compliance/provenance disclosure is skipped
        self.assertNotIn("PurityBan", ids(
            "This report is watermarked as AI-generated in compliance with the contract requirements."))
        self.assertNotIn("PurityBan", ids(
            "The provenance watermark survived re-encoding; the C2PA manifest still validates."))

    def test_vibe_scapegoat_positive_adjacent_qa(self):
        self.assertIn("VibeScapegoat", ids(
            "Service down again? Vibe-coded slop devs at work, as always."))
        self.assertIn("VibeScapegoat", ids(
            "Ausfall wieder? Klar \u2014 man braucht keine Meldung, um zu wissen, wer da gefuscht hat."))

    def test_vibe_scapegoat_negative_technical_postmortem(self):
        self.assertNotIn("VibeScapegoat", ids(
            "The regression came from commit 4f2a1c; the postmortem shows the missing test, the review gap, and the rollback path."))

    def test_salvation_model_positive_rituals(self):
        self.assertIn("SalvationModel", ids(
            "Only X can save the platform; everyone else ruined it."))
        self.assertIn("SalvationModel", ids(
            "Er hat es wieder getan. Der Genius. Die L\u00fcgenpresse schweigt."))
        self.assertIn("SalvationModel", ids(
            "Nur noch X kann das Land retten \u2014 alle anderen sind Teil des Problems."))

    def test_salvation_model_negative_concrete_narrative(self):
        self.assertNotIn("SalvationModel", ids(
            "I was broke in 2024. After eight months of building a support-ticket automation, it now covers my rent."))

    def test_fallstudie_97_hard_negatives_fp_zero(self):
        """DoD: none of the three patterns fires on the 4 annotated
        hard-negatives (Energie, Postmortem, Provenienz, Eval) nor on the
        40 hard-negatives of the human_ideological corpus."""
        hard = [
            "Training-run energy for this model class is measured at 3.2 GWh with cited methodology; the audit compares two disclosure frameworks.",
            "The regression came from commit 4f2a1c; the postmortem shows the missing test, the review gap, and the rollback path.",
            "The provenance watermark survived re-encoding; the C2PA manifest still validates.",
            "Our eval set shows the model fails on dialect inputs \u2014 41 % error rate, examples in appendix.",
        ]
        target = {"PurityBan", "VibeScapegoat", "SalvationModel"}
        for t in hard:
            self.assertFalse(ids(t) & target, t[:60])
        import json
        corpus = os.path.join(ROOT, "eval", "human_ideological.jsonl")
        with open(corpus, encoding="utf-8") as fh:
            for line in fh:
                line = line.strip()
                if not line:
                    continue
                row = json.loads(line)
                if row.get("label") == "hard_negative":
                    hits = ids(row["text"]) & target
                    self.assertFalse(hits, f"{row['id']} FP: {hits}")

    def test_fallstudie_97_corpus_recall(self):
        """Every slop row of the three signals fires its own pattern."""
        import json
        corpus = os.path.join(ROOT, "eval", "human_ideological.jsonl")
        target = {"PurityBan", "VibeScapegoat", "SalvationModel"}
        n = 0
        with open(corpus, encoding="utf-8") as fh:
            for line in fh:
                line = line.strip()
                if not line:
                    continue
                row = json.loads(line)
                if row.get("label") == "slop" and row.get("signal") in target:
                    self.assertIn(
                        row["signal"], ids(row["text"]),
                        f"{row['id']} ({row['signal']}) does not fire")
                    n += 1
        self.assertGreaterEqual(n, 13)


if __name__ == "__main__":
    unittest.main()
