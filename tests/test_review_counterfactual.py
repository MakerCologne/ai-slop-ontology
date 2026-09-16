"""Tests: Review/Approval-Slop Counterfactual Test (issue #122, PRISM)."""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from src.metadata_slop import MetadataSlopClassifier  # noqa: E402


def _res(comment):
    return MetadataSlopClassifier().classify_review_comment(comment)


def test_generic_lgtm_fires():
    assert _res("LGTM, looks good to me").is_slop
    assert _res("Looks good!").is_slop


def test_generic_plus_one_fires():
    assert _res("+1 ship it").is_slop
    assert _res("LGTM +1").is_slop


def test_generic_german_fires():
    assert _res("Sieht gut aus, danke!").is_slop
    assert _res("Stimme zu, passt so").is_slop


def test_generic_hedge_fires():
    # "Consider adding a test" passt auf jeden PR — counterfactual feurig
    assert _res("Consider adding a test").is_slop


def test_identifier_anchor_no_fire():
    r = _res("LGTM — the retry logic in `fetch_token()` looks solid")
    assert not r.is_slop


def test_file_path_anchor_no_fire():
    assert not _res("Looks good, nice catch in src/auth/retry.py").is_slop


def test_file_extension_anchor_no_fire():
    assert not _res("Good catch, fixed in parser.py now").is_slop


def test_issue_ref_anchor_no_fire():
    assert not _res("Approving: fixed as discussed in #118").is_slop


def test_number_anchor_no_fire():
    assert not _res("Thanks! Ran the suite locally: all green (see run 4711)").is_slop


def test_snake_case_anchor_no_fire():
    assert not _res("Looks good, especially the improved error_state handling").is_slop


def test_no_marker_no_fire():
    assert not _res("The auth module validates user authentication").is_slop


def test_specific_content_no_fire():
    assert not _res(
        "The backoff in RetryPolicy is quadratic — use exponential").is_slop


def test_evidence_and_metadata():
    r = _res("Nice work, thanks for this")
    assert r.is_slop
    f = r.signals_detected[0]
    assert f.signal_id == "ReviewApprovalSlop"
    assert f.surface == "review_comment"
    assert f.confidence == 0.4
    assert "counterfactual" in f.evidence


def test_empty_and_whitespace():
    assert not _res("").is_slop
    assert not _res("   ").is_slop
