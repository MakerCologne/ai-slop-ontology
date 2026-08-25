#!/usr/bin/env python3
"""
Naturalness-Guard (issue #81, detect-only, low confidence).

Two advisory signals against the two failure modes of automated text
cleanup (humanizer register-profile idea, architecture reference deep/11;
marker lists self-derived, no third-party pattern material copied):

  register_drift      mixed register in one text: >= 2 formal markers AND
                      >= 2 colloquial markers outside quotes (>= 30 words).
                      keep_when: quoted dialogue/fiction (colloquial inside
                      quotation marks never counts); short chat snippets.

  over_sanitized      >= 3 distinct expanded full forms ("do not", "it
                      is", ...) with ZERO contractions (>= 60 words).
                      keep_when: formal genres — callers pass genre=
                      "academic"/"legal" to suppress; possessive 's is not
                      a contraction.

  modal_particle_anomaly  EXPLICIT STUB (issue #76 owns the DE modal
                      particle inventory; until then the stub reports
                      status="stub" and never emits a finding).

DETECT-ONLY: findings never feed the numeric slop score and are capped at
confidence 0.45. FP expectation (#64): formal writing triggers
over_sanitized by design — that is why the genre guard exists and the
finding is advisory with fixed low confidence.

Public surface:
    register_drift(text) -> finding | None
    over_sanitized(text) -> finding | None
    modal_particle_anomaly(text) -> {"status": "stub", "finding": None, ...}
    find_naturalness_findings(text, genre=None) -> list[finding]
"""

import re

# Closed marker lists (EN+DE), deliberately small.
FORMAL_MARKERS = {
    "furthermore", "moreover", "in addition", "hereby", "notwithstanding",
    "thus", "hence", "consequently",
    "ferner", "mithin", "gemäß", "hierauf", "folglich", "laut",
}
COLLOQUIAL_MARKERS = {
    "yeah", "kinda", "gonna", "hey", "okay", "honestly", "stuff", "wild",
    "na ja", "irgendwie", "halt", "krass", "echt",
}

# Expanded full forms whose contraction-free accumulation reads sanitized.
FULL_FORMS = [
    "do not", "does not", "did not", "cannot", "can not", "will not",
    "would not", "it is", "we are", "they are", "that is", "there is",
    "we have", "they have", "it has",
]
_CONTRACTION_RE = re.compile(r"\b\w+['’](?:t|s|re|ve|ll|d|m)\b")
_POSSESSIVE_OK = re.compile(r"\b\w+['’]s\b")
_QUOTE_RE = re.compile(r'[„"“][^„""“”]{1,300}[”“"]')

MIN_WORDS_REGISTER = 30
MIN_WORDS_SANITIZED = 25  # fixture-calibrated (pos1/pos3/possessive fixtures in tests)
MIN_FULL_FORMS = 3

# Genres where expanded full forms are register-correct, not sanitization.
FORMAL_GENRES = {"academic", "legal"}


def _markers(text_lower: str, markers: set) -> list:
    return sorted(m for m in markers if m in text_lower)


def _strip_quotes(text: str) -> str:
    return _QUOTE_RE.sub(" ", text)


def register_drift(text: str):
    body = _strip_quotes(text)
    if len(body.split()) < MIN_WORDS_REGISTER:
        return None
    low = body.lower()
    formal = _markers(low, FORMAL_MARKERS)
    colloquial = _markers(low, COLLOQUIAL_MARKERS)
    if len(formal) >= 2 and len(colloquial) >= 2:
        return {
            "id": "RegisterDrift",
            "confidence": 0.45,
            "evidence": (f"formal {formal} vs colloquial {colloquial} "
                         "in one text (outside quotes)"),
            "keep_when": ("quoted dialogue/fiction (quotes stripped before "
                          "counting); short chat snippets < "
                          f"{MIN_WORDS_REGISTER} words"),
        }
    return None


def over_sanitized(text: str):
    if len(text.split()) < MIN_WORDS_SANITIZED:
        return None
    low = text.lower()
    full_hits = sorted({f for f in FULL_FORMS if f in low})
    has_contraction = bool(_CONTRACTION_RE.search(text) and
                           not _only_possessives(text))
    if len(full_hits) >= MIN_FULL_FORMS and not has_contraction:
        return {
            "id": "OverSanitized",
            "confidence": 0.45,
            "evidence": (f"{len(full_hits)} distinct expanded full forms "
                         f"({', '.join(full_hits[:5])}), zero contractions"),
            "keep_when": ("formal genres (pass genre='academic'/'legal' to "
                          "suppress); possessive 's is not a contraction"),
        }
    return None


def _only_possessives(text: str) -> bool:
    """True when every apostrophe token is a possessive 's (not a
    contraction) — those do not count as human-typed rhythm."""
    tokens = re.findall(r"\b\w+['’](?:t|s|re|ve|ll|d|m)\b", text)
    if not tokens:
        return True
    return all(_POSSESSIVE_OK.fullmatch(t) for t in tokens)


def modal_particle_anomaly(text: str):
    """STUB (issue #76): DE modal particle inventory pending. Never a
    finding until the DE layer lands."""
    return {
        "id": "ModalParticleAnomaly",
        "status": "stub",
        "finding": None,
        "note": ("DE-Modalpartikel-Inventar folgt mit dem DE-Layer "
                 "(issue #76); bis dahin bewusst kein Finding."),
    }


def find_naturalness_findings(text: str, genre: str = None) -> list:
    findings = []
    rd = register_drift(text)
    if rd:
        findings.append(rd)
    if genre not in FORMAL_GENRES:
        os_ = over_sanitized(text)
        if os_:
            findings.append(os_)
    return findings
