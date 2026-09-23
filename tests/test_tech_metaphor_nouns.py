#!/usr/bin/env python3
"""Tests: tech_metaphor_nouns (#246 / unslop #26, Gap G2).

Abstract tech-metaphor nouns as buzzword substitution. DoD #1:
Positiv-/Negativ-Fixtures mit Akzeptanzschwelle; DoD #2: keep_when
(ML-Kontext-Guard) per Fixture belegt.
"""

import os
import sys

import pytest

ROOT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..")
sys.path.insert(0, os.path.join(ROOT, "skills", "ai-slop-detection", "scripts"))

from slop_scorer import PHRASE_CATEGORIES, phrase_category_score  # noqa: E402

CAT = "tech_metaphor_nouns"


def test_category_registered():
    assert CAT in PHRASE_CATEGORIES
    items = PHRASE_CATEGORIES[CAT]["phrases"]
    # Issue #246: Liste >= 14 Eintraege
    assert len(items) >= 14
    for w in ["substrate", "flywheel", "north star", "bedrock", "nexus",
              "wedge", "scaffolding", "modality", "paradigm", "ratchet",
              "evacuate", "endgame", "harness", "vector"]:
        assert w in items, w


# --- Positives: metaphorische statt konkrete Benennung -------------------

POSITIVE_SLOP = (
    "Trust is the bedrock of every team. Once retention turns into a flywheel, "
    "growth compounds. Customer success is the north star that anchors every "
    "roadmap decision."
)

def test_positive_metaphor_prose():
    hits = phrase_category_score(POSITIVE_SLOP).get(CAT, [])
    assert "bedrock" in hits
    assert "flywheel" in hits
    assert "north star" in hits


def test_positive_single_governing_paradigm():
    hits = phrase_category_score(
        "We must abandon the old governing paradigm and build on this new "
        "intellectual substrate."
    ).get(CAT, [])
    assert "paradigm" in hits and "substrate" in hits


def test_positive_vector_metaphor_no_ml_context():
    # 'vector' als Metapher ohne ML-Kontext im Satz
    hits = phrase_category_score(
        "This campaign is the main vector for cultural change. The other "
        "vector comes from grassroots organizing."
    ).get(CAT, [])
    assert "vector" in hits


# --- Hard Negatives (keep_when: ML-Terminologie-Fenster) ------------------

ML_NEGATIVES = [
    # modality als ML-Terminus im Modellkontext
    "The model was evaluated on a new modality; multimodal training "
    "covers image and audio.",
    # vector als Lineare-Algebra-Terminus
    "Each embedding is a dense vector of 1024 dimensions; the classifier "
    "uses these vectors as input features.",
    # paradigm in wissenschaftlichem Kontext (Kuhn) mit ML-Bezug
    "This training paradigm improves the transformer's loss on every "
    "benchmark dataset.",
    # harness als Test-Harness (Engineering)
    "The test harness runs the inference pipeline against the model "
    "checkpoint after every build.",
]

@pytest.mark.parametrize("text", ML_NEGATIVES)
def test_ml_context_guard_masks_terminology(text):
    hits = phrase_category_score(text)
    assert CAT not in hits or not hits[CAT], hits.get(CAT)


def test_guard_edge_metaphor_after_ml_sentence():
    # ML-Satz gefolgt von Metapher-Satz: nur der Metapher-Satz matchet
    text = (
        "We fine-tune the model on this dataset. "
        "Trust is the bedrock of the partnership, growth a flywheel."
    )
    hits = phrase_category_score(text).get(CAT, [])
    assert sorted(hits) == ["bedrock", "flywheel"]


def test_no_interference_with_other_categories():
    # Guard maskiert nur die vier ML-Nomen, andere Kategorien bleiben intakt
    text = (
        "It is worth noting that the model handles a new modality. "
        "In conclusion, the vector embeddings are dense."
    )
    hits = phrase_category_score(text)
    # 'in conclusion,' gewinnt als Longest-Match gegen 'in conclusion'
    # (closing_formulas, COLL-Analogie zu #83/#88)
    assert "closing_formulas" in hits
