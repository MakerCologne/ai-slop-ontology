"""Tests for src/naturalness_guard.py — detect-only over-sanitization guard (#81).

Pflicht laut #81: Grenzfixtures „legitim gleichmäßig" (Guardrail, #42
Genre-Profile) müssen vorhanden sein.
"""

import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))

from naturalness_guard import NaturalnessGuard, EXEMPT_GENRES  # noqa: E402

CLF = NaturalnessGuard()

# --- 1) over_sanitized -----------------------------------------------------

UNIFORM_BLAND = (
    "The system provides functionality. The system ensures reliability. "
    "The system delivers performance. The system supports scalability. "
    "The system enables efficiency. The system maintains stability. "
    "The system offers capability. The system implements process steps. "
    "The system provides functionality. The system ensures reliability. "
    "The system delivers performance. The system supports scalability. "
    "The system enables efficiency. The system maintains stability. "
    "The system offers capability. The system implements process steps. "
) * 2


def test_over_sanitized_fires_on_uniform_bland():
    r = CLF.classify_text(UNIFORM_BLAND)
    ids = [f.signal_id for f in r.signals_detected]
    assert "over_sanitized" in ids
    assert all(f.severity == "low" for f in r.signals_detected)


def test_over_sanitized_confidence_low_advisory():
    r = CLF.classify_text(UNIFORM_BLAND)
    f = [x for x in r.signals_detected if x.signal_id == "over_sanitized"][0]
    assert f.confidence == 0.35
    assert f.confidence < 0.5  # advisory, never score-dominant


# --- 2) Grenzfixtures: legitim gleichmäßig (Guardrail Pflicht) --------------

def test_technical_genre_exempt():
    r = CLF.classify_text(UNIFORM_BLAND, genre="technical")
    assert r.signals_detected == []
    assert any("genre" in n for n in r.notes)


def test_all_exempt_genres_silent():
    for g in EXEMPT_GENRES:
        assert CLF.classify_text(UNIFORM_BLAND, genre=g).signals_detected == []


def test_human_prose_not_flagged():
    # decent human writing: quirks present, varied lengths -> no signal
    human = (
        "Honestly, I wasn't sure this would work — but it did! We shipped it "
        "on a Friday, which in hindsight was a terrible idea, and yet nothing broke. "
        "The morning after, our dashboards looked suspiciously calm. "
        "Turns out the fix held. "
        "I've kept the notes below, mostly so future-me doesn't repeat the "
        "whole saga, but also because the debugging detour taught us "
        "something about our caching layer that no postmortem ever did. "
        "Would I do it again? Probably not on a Friday. But the confidence "
        "gained was real, and honestly that counts for something around here."
    )
    r = CLF.classify_text(human)
    assert [f.signal_id for f in r.signals_detected
            if f.signal_id == "over_sanitized"] == []


# --- 3) register_drift ------------------------------------------------------

def test_register_drift_two_halves():
    casual = (
        "Honestly, this thing is kind of a mess! But we love it anyway. "
        "So let's talk about what broke — and why. It's a fun story, "
        "actually. Basically, everything was on fire, and we didn't even "
        "notice at first. To be fair, the alerts did fire. We just ignored "
        "them, which is a whole different post. Anyway: the fix worked, "
        "and the lessons were worth it."
    )
    clinical = (
        "The deployment process consists of sequential stages. Each stage "
        "validates specific criteria. The system records validation results. "
        "Operators review recorded results periodically. Documentation of "
        "each stage ensures compliance requirements. The process continues "
        "until all criteria pass. This description omits implementation "
        "details. Additional stages exist in supplementary documents. "
        "Each additional stage follows identical validation procedures. "
        "Supplementary procedures define further compliance criteria. "
        "The records include timestamps and operator identifiers. "
        "Periodic audits verify the recorded validation results again."
    )
    r = CLF.classify_text(casual + " " + clinical)
    ids = [f.signal_id for f in r.signals_detected]
    assert "register_drift" in ids


def test_uniform_text_no_false_drift():
    r = CLF.classify_text(UNIFORM_BLAND)
    assert "register_drift" not in [f.signal_id for f in r.signals_detected]


# --- 4) Kurztext / Randfälle -------------------------------------------------

def test_short_text_skipped():
    r = CLF.classify_text("Too short. Very bland. Nothing here.")
    assert r.signals_detected == []
    assert any("words" in n for n in r.notes)


def test_empty_text():
    r = CLF.classify_text("")
    assert r.signals_detected == []


def test_result_shape():
    r = CLF.classify_text(UNIFORM_BLAND)
    assert r.is_advisory is True
    assert "over_sanitized" in r.summary()
