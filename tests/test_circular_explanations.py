"""Tests for Circular Explanations (upstream #122) — detect-only.

DoD-style fixtures: positive artefacts from the PRISM research context,
hard negatives (technical reference prose, genuine definitions).
"""

import os
import sys

SCRIPTS = os.path.join(os.path.dirname(__file__), "..",
                       "skills", "ai-slop-detection", "scripts")
sys.path.insert(0, SCRIPTS)

from circular_explanations import circular_explanation, find_circular_findings


def test_prism_example_fires():
    text = ("The auth module validates authentic user authentication.")
    f = circular_explanation(text)
    assert f is not None and f["id"] == "CircularExplanation"
    assert f["confidence"] <= 0.5  # detect-only cap


def test_tautological_is_definition():
    f = circular_explanation(
        "Authentication is the process of authenticating users.")
    assert f is not None


def test_multiple_findings_collected():
    text = ("The auth module validates authentic user authentication. "
            "Security is the property of being secure. "
            "The caching layer caches cached data.")
    fs = find_circular_findings(text)
    assert len(fs) == 2


def test_hard_negative_technical_reference():
    # 'handles' is not definitional: naming inputs is legitimate spec prose
    f = circular_explanation(
        "The auth module handles authentication tokens from the gateway.")
    assert f is None


def test_hard_negative_genuine_definition():
    f = circular_explanation(
        "Authentication is the process of verifying identity against "
        "stored credentials.")
    assert f is None  # predicate brings >3 new stems


def test_hard_negative_short_sentence():
    assert circular_explanation("The cache caches data.") is None


def test_german_tautology():
    f = circular_explanation(
        "Die Authentifizierung bedeutet die authentische Prüfung der "
        "Authentifizierung.")
    assert f is not None


def test_no_definitional_verb_no_fire():
    f = circular_explanation(
        "The authentication module receives authentication requests and "
        "forwards authentication results to the audit log.")
    assert f is None
