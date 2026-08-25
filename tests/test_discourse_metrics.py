"""Issue #72 — L4-Referenzkorpus + explorative Diskurs-Signale.

1. ``eval/discourse_ref.jsonl`` — versionierter, kleiner Referenzkorpus
   exemplarischer Diskursartefakte (Rank-ohne-Kriterium-Threads, virale
   Claim-Posts, identische Aufzählungen; Artefakt-Typen aus
   research/slop-ontology-gap-2026-08-24/deep/10 + deep/06).

2. ``skills/ai-slop-detection/scripts/discourse_metrics.py`` —
   explorative, detect-only Signale ``rank_without_criterion`` und
   ``identical_enumeration`` (Konfidenz 0.35, klar als explorativ
   markiert, nie im numerischen Score).
"""

import json
import os
import sys

import pytest

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SCRIPTS = os.path.join(ROOT, "skills", "ai-slop-detection", "scripts")
sys.path.insert(0, SCRIPTS)

import discourse_metrics as dm  # noqa: E402


def _ref_records():
    path = os.path.join(ROOT, "eval", "discourse_ref.jsonl")
    assert os.path.isfile(path)
    with open(path, encoding="utf-8") as f:
        return [json.loads(l) for l in f if l.strip()]


class TestReferenceCorpus:
    def test_versioned_and_wellformed(self):
        recs = _ref_records()
        assert all(r.get("version") == recs[0]["version"] for r in recs)
        for r in recs:
            for key in ("id", "kind", "text", "source_ref", "license"):
                assert key in r, (r.get("id"), key)

    def test_covers_expected_artifact_kinds(self):
        kinds = {r["kind"] for r in _ref_records()}
        assert "rank_without_criterion" in kinds
        assert "identical_enumeration" in kinds
        assert "viral_claim" in kinds

    def test_records_own_or_attributed(self):
        for r in _ref_records():
            assert r["license"] in ("own:paraphrase", "own:handwritten",
                                    "quote-attributed")

    def test_signals_fire_on_reference_examples(self):
        for r in _ref_records():
            if r["kind"] == "rank_without_criterion":
                assert dm.rank_without_criterion(r["text"]) is not None, r["id"]
            if r["kind"] == "identical_enumeration":
                assert dm.identical_enumeration(r["text"]) is not None, r["id"]


# --- rank_without_criterion -------------------------------------------------

RANK_POS1 = ("I made a rank with the anti-slop skills people need to "
             "install.\n\n1. stop-slop\n2. no-ai-slop\n3. humanizer\n"
             "4. unslop\n5. slopbeth")

RANK_POS2 = ("Top 10 tools this year:\n1) Tool A\n2) Tool B\n3) Tool C\n"
             "4) Tool D\n5) Tool E\n6) Tool F")

RANK_POS3 = ("Hier die besten Skills, Rang 1 bis 5:\n1. Alpha\n2. Beta\n"
             "3. Gamma\n4. Delta\n5. Epsilon — installiert sie einfach.")

RANK_NEG1 = ("Ranking nach Installationszahlen (skills.sh, Stand August): "
             "1. A (466k), 2. B (12,4k), 3. C (11,7k). Grund für die "
             "Reihenfolge: reine Zahl der Installationen.")

RANK_NEG2 = "Meine drei Lieblings-Skills mit Begründung: A, weil schnell; B, weil klein; C, weil frei."

RANK_NEG3 = ("Wir vergleichen vier Detektoren nach den Kriterien Präzision, "
             "Recall und Laufzeit. 1. D1 (P 0.99). 2. D2 (P 0.98) …")

RANK_BOUND1 = "1. nur ein einzelner Punkt ohne weitere"
RANK_BOUND2 = ("Eine Liste ohne Rang-Zahlen und ohne Behauptung: Skills sind "
              "stop-slop, no-ai-slop, humanizer, unslop und slopbeth.")


class TestRankWithoutCriterion:
    def test_pos1_thread_rank(self):
        f = dm.rank_without_criterion(RANK_POS1)
        assert f is not None and f["id"] == "RankWithoutCriterion"
        assert f["confidence"] <= 0.4
        assert f.get("exploratory") is True

    def test_pos2(self):
        assert dm.rank_without_criterion(RANK_POS2) is not None

    def test_pos3(self):
        assert dm.rank_without_criterion(RANK_POS3) is not None

    def test_neg1_rank_with_criterion(self):
        assert dm.rank_without_criterion(RANK_NEG1) is None

    def test_neg2_reasoned(self):
        assert dm.rank_without_criterion(RANK_NEG2) is None

    def test_neg3_criteria_named(self):
        assert dm.rank_without_criterion(RANK_NEG3) is None

    def test_boundary1_single_item(self):
        assert dm.rank_without_criterion(RANK_BOUND1) is None

    def test_boundary2_unranked_list(self):
        assert dm.rank_without_criterion(RANK_BOUND2) is None


# --- identical_enumeration --------------------------------------------------

ENUM_POS1 = ("No more em dashes. No more comparisons. No more extra "
             "examples nobody asked for.")

ENUM_POS2 = ("Kein Em-Dash mehr. Keine Vergleiche mehr. Keine überflüssigen "
             "Beispiele mehr. Kein Bullshit mehr.")

ENUM_POS3 = ("One tool to write. One tool to check. One tool to fix. "
             "One tool to rule them all.")

ENUM_NEG1 = "Wir prüfen Dichte, Rhythmus und Marker. Danach folgt der Bericht."
ENUM_NEG2 = "Kein Em-Dash. Später mehr zu Vergleichen."
ENUM_NEG3 = ("No more em dashes, no more comparisons and no more extra "
             "examples — alles in einem Satz statt drei.")

ENUM_BOUND1 = "Kein Em-Dash mehr. Keine Vergleiche mehr."
ENUM_BOUND2 = ENUM_POS1 + " " + ENUM_POS2  # Mischtext: feuert, aber nur 1 Finding


class TestIdenticalEnumeration:
    def test_pos1(self):
        f = dm.identical_enumeration(ENUM_POS1)
        assert f is not None and f["id"] == "IdenticalEnumeration"
        assert f["confidence"] <= 0.4
        assert f.get("exploratory") is True

    def test_pos2_de(self):
        assert dm.identical_enumeration(ENUM_POS2) is not None

    def test_pos3(self):
        assert dm.identical_enumeration(ENUM_POS3) is not None

    def test_neg1_normal_sentence(self):
        assert dm.identical_enumeration(ENUM_NEG1) is None

    def test_neg2_two_items(self):
        assert dm.identical_enumeration(ENUM_NEG2) is None

    def test_neg3_single_sentence_comma_list(self):
        assert dm.identical_enumeration(ENUM_NEG3) is None

    def test_boundary1_two_parallel_items(self):
        assert dm.identical_enumeration(ENUM_BOUND1) is None

    def test_boundary2_mixed_text_single_finding(self):
        findings = dm.find_discourse_findings(ENUM_BOUND2)
        assert len([f for f in findings if f["id"] == "IdenticalEnumeration"]) == 1


class TestExploratoryMarking:
    def test_all_findings_marked_exploratory_and_low_conf(self):
        for f in dm.find_discourse_findings(RANK_POS1 + "\n\n" + ENUM_POS1):
            assert f.get("exploratory") is True
            assert f["confidence"] <= 0.4
            assert "explorativ" in f["keep_when"].lower() or \
                   "explorative" in f["keep_when"].lower()
