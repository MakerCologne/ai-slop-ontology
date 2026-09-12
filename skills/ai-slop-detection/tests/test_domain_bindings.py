"""Tests for Issue #35: Domain-Trigger-Metadatum je Signal (triggered_by: domain)."""

import json
import os
import subprocess
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)) + "/../scripts")

import domain_bindings  # noqa: E402
from slop_scorer import slop_score  # noqa: E402

REPO = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))


# --- Registry structure -------------------------------------------------

def test_pilot_has_five_bindings():
    assert len(domain_bindings.SIGNAL_DOMAIN_BINDINGS) == 5


def test_binding_schema():
    for sig, b in domain_bindings.SIGNAL_DOMAIN_BINDINGS.items():
        assert b["triggered_by"] == "domain"
        assert b["semantics"] in ("only-triggers-in", "suppressed-in")
        assert isinstance(b["domains"], list) and b["domains"]
        assert b.get("rationale")


def test_ssot_mirror_in_ontology():
    onto = json.load(open(os.path.join(REPO, "ontology.json")))
    db = onto["signals"]["domainBindings"]
    mirrored = {b["signal"]: b for b in db["bindings"]}
    assert len(mirrored) == 5
    for sig, b in domain_bindings.SIGNAL_DOMAIN_BINDINGS.items():
        m = mirrored[sig]
        assert m["semantics"] == b["semantics"]
        assert m["domains"] == b["domains"]


# --- Semantics ----------------------------------------------------------

def test_suppressed_in():
    inactive = domain_bindings.signals_inactive_in_domain("changelog")
    assert "list_heavy" in inactive
    assert "marketing_cta" not in inactive


def test_suppressed_in_ui_copy():
    inactive = domain_bindings.signals_inactive_in_domain("ui_copy")
    assert "marketing_cta" in inactive


def test_only_triggers_in():
    inactive = domain_bindings.signals_inactive_in_domain("changelog")
    # meta_commentary only triggers in essay/blog/review
    assert "meta_commentary" in inactive
    inactive_essay = domain_bindings.signals_inactive_in_domain("essay")
    assert "meta_commentary" not in inactive_essay


def test_unbound_domain_deactivates_only_triggers():
    # An unlisted domain deactivates only-triggers-in signals (they are
    # domain-specific indicators); suppressed-in signals stay active.
    # The CLI rejects unknown domains, this documents function semantics.
    inactive = domain_bindings.signals_inactive_in_domain("unlisted-domain")
    assert inactive == {"meta_commentary"}


# --- Scorer integration -------------------------------------------------

LANDING = ("Start your free trial today and book a demo. Trusted by "
           "startups and enterprises alike. Ready to get started? "
           "Everything stays all in one place.")


def test_marketing_cta_hits_base():
    # Sanity: the landing text actually trips marketing_cta without a domain.
    base = slop_score(LANDING)
    assert "marketing_cta" in base["signals"].get("phrase_categories", {})


def test_marketing_cta_suppressed_on_landing_page():
    base = slop_score(LANDING)
    with_domain = slop_score(LANDING, domain="ui_copy")
    assert with_domain["slop_score"] < base["slop_score"]


def test_no_domain_unchanged():
    # Without --domain the score must be identical (no regression by omission).
    a = slop_score(LANDING)
    b = slop_score(LANDING, domain=None)
    assert a["slop_score"] == b["slop_score"]


def test_list_heavy_suppressed_in_changelog():
    text = "\n".join(["- Fixed login bug %d" % i for i in range(12)])
    base = slop_score(text)
    with_domain = slop_score(text, domain="changelog")
    assert with_domain["slop_score"] < base["slop_score"]


def test_cli_rejects_unknown_domain():
    r = subprocess.run(
        [sys.executable,
         os.path.join(REPO, "skills/ai-slop-detection/scripts/slop_scorer.py"),
         "--domain", "nope", "--file", "/dev/null"],
        capture_output=True, text=True)
    assert r.returncode == 2
    assert "unknown domain" in r.stderr
