"""Issue #35 — domain bindings (triggered_by: domain) tests.

ontology.json domainBindings is the SSOT; skills domain_bindings.py is the
accessor; scorer/classifier apply the gating opt-in via --domain /
domain= parameters. Fail-loud on unknown domains; default domain-agnostic.
"""

import json
import os
import subprocess
import sys

import pytest

ROOT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..")
SCRIPTS = os.path.join(ROOT, "skills", "ai-slop-detection", "scripts")
sys.path.insert(0, SCRIPTS)
sys.path.insert(0, os.path.join(ROOT, "src"))
sys.path.insert(0, ROOT)

import domain_bindings  # noqa: E402


# --- SSOT data sanity ------------------------------------------------------

def test_domain_bindings_present_in_ontology():
    o = json.load(open(os.path.join(ROOT, "ontology.json"), encoding="utf-8"))
    db = o["domainBindings"]
    assert db["source"].startswith("#35")
    assert len(db["signals"]) >= 5, "issue demands 5 pilot signals"
    for sid, b in db["signals"].items():
        assert b["triggered_by"] == "domain"
        assert "rationale" in b
        # whitelist XOR blacklist, never both
        assert ("applies_to" in b) ^ ("restricted_in" in b)


def test_pilot_domains_declared():
    declared = set(domain_bindings.get_domains())
    for sid, b in domain_bindings.get_bindings().items():
        for d in b.get("applies_to", []) + b.get("restricted_in", []):
            assert d in declared, f"{sid} references undeclared domain {d}"


# --- accessor semantics ----------------------------------------------------

def test_default_is_domain_agnostic():
    assert domain_bindings.signal_active_in("Workslop", None) is True
    assert domain_bindings.gated_signals(None) == []
    assert domain_bindings.weight_dims_gated(None) == []


def test_restricted_in_suppresses():
    assert domain_bindings.signal_active_in("Workslop", "changelog") is False
    assert domain_bindings.signal_active_in("Workslop", "essay") is True
    assert "Workslop" in domain_bindings.gated_signals("changelog")


def test_applies_to_whitelist_wins():
    assert domain_bindings.signal_active_in("PeerReviewSlop", "academic") is True
    assert domain_bindings.signal_active_in("PeerReviewSlop", "marketing") is False
    # unbound signal stays active everywhere
    assert domain_bindings.signal_active_in("SomeUnboundSignal", "changelog") is True


def test_weight_dims_map():
    dims = domain_bindings.weight_dims_gated("changelog")
    assert "phrases" in dims      # Workslop, FakeAuthoritySlop
    assert "fake_authority" in dims
    assert "list_heavy" in dims   # NumberedListOveruse
    assert domain_bindings.weight_dims_gated("security_report") == ["phrases"]  # only PeerReviewSlop gated


def test_validate_domain_fail_loud():
    with pytest.raises(ValueError):
        domain_bindings.validate_domain("no_such_domain")
    domain_bindings.validate_domain("essay")      # no-op
    domain_bindings.validate_domain(None)         # no-op


# --- scorer integration ----------------------------------------------------

def _run(args):
    return subprocess.run(
        [sys.executable, os.path.join(SCRIPTS, "slop_scorer.py")] + args,
        capture_output=True, text=True, cwd=SCRIPTS)


def test_scorer_domain_json_reports_gating():
    text = ("We fixed the parser. Studies show the fix improves parsing. "
            "1. Fixed parser\n2. Improved speed\n3. Added tests\n4. Docs\n")
    r = json.loads(_run(["--json", "--domain", "changelog", text]).stdout)
    assert r["domain"] == "changelog"
    assert "Workslop" in r["domain_gated_signals"]
    assert "fake_authority" in r["domain_gated_weight_dims"]
    assert r["dimension_scores"]["authority_slop"] == 0.0


def test_scorer_domain_changes_score_direction():
    text = ("We fixed the parser. Studies show the fix works. As noted by "
            "the authors, this improves things. Our team is proud. "
            "1. a\n2. b\n3. c\n4. d\n5. e\n")
    base = json.loads(_run(["--json", text]).stdout)
    gated = json.loads(_run(["--json", "--domain", "changelog", text]).stdout)
    assert base["slop_score"] >= gated["slop_score"]
    assert "domain" not in base  # default output unchanged


def test_scorer_unknown_domain_exit_2():
    p = _run(["--json", "--domain", "bogus", "x"])
    assert p.returncode == 2
    assert "Unknown domain" in p.stderr


# --- classifier integration ------------------------------------------------

def test_classifier_filters_gated_signals():
    from classifier import SlopClassifier
    clf = SlopClassifier(os.path.join(ROOT, "ontology.json"))
    text = ("We are proud to announce that our team fixed the parser. "
            "As noted by the authors, studies show it works better now.")
    base = clf.classify_text(text)
    gated = clf.classify_text(text, domain="marketing")
    ids_base = {s.signal_id for s in base.signals_detected}
    ids_gated = {s.signal_id for s in gated.signals_detected}
    assert ids_gated <= ids_base
    if ids_base & set(domain_bindings.get_bindings()):
        assert ids_gated < ids_base


def test_classifier_unknown_domain_raises():
    from classifier import SlopClassifier
    clf = SlopClassifier(os.path.join(ROOT, "ontology.json"))
    with pytest.raises(ValueError):
        clf.classify_text("hello", domain="bogus")
