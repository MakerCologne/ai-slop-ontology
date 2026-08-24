#!/usr/bin/env python3
"""Genre-register profiles for the AI-slop skill scorer (issue #42).

False-positive guards for legitimate styles: legal, academic, marketing and
technical prose use register conventions (legalese formulae, passive voice,
genre superlatives) that legitimately trip generic slop signals.

A profile is configuration only, applied explicitly via ``--genre <name>``
(no auto-detection — that is deliberately out of scope for #42):

- ``exempt_terms``: terms removed from SIGNAL matching before the metrics
  (buzzwords / phrases / authority / multilingual), analogous to the #23
  quote exemption. Structural dimensions (density, repetition, burstiness)
  keep the full text.
- ``zero_weights``: metric weights set to 0 for register-conventional
  features (e.g. uniform sentence lengths in academic prose).
- ``decision_threshold``: raised decision threshold for the genre — weaker
  evidence does not reach "Suspicious". Provenance floors and >= 2-family
  escalation still apply at their original strength.
"""

import re

GENRE_PROFILES = {
    "legal": {
        "description": "Contracts, statutes, filings — legalese formulae and "
                       "uniform formal register are convention, not slop.",
        "exempt_terms": [
            "pursuant to", "notwithstanding", "hereinafter", "heretofore",
            "aforementioned", "shall not", "shall be", "it is agreed",
            "furthermore", "moreover",
        ],
        "zero_weights": ["burstiness"],
        "decision_threshold": 0.55,
    },
    "academic": {
        "description": "Abstracts, papers — passive voice, uniform sentence "
                       "lengths and discourse connectors are convention.",
        "exempt_terms": [
            "furthermore", "moreover", "additionally", "notably",
            "importantly", "crucially", "it is important to note",
        ],
        "zero_weights": ["burstiness", "verbosity"],
        "decision_threshold": 0.55,
    },
    "marketing": {
        "description": "Product copy — superlatives are genre-conventional.",
        "exempt_terms": [
            "cutting-edge", "state-of-the-art", "game-changer", "game changing",
            "innovative", "next-generation", "best-in-class", "world-class",
        ],
        "zero_weights": [],
        "decision_threshold": 0.50,
    },
    "technical": {
        "description": "Docs, runbooks, RFCs — list-heavy layout and "
                       "engineering stock vocabulary are convention.",
        "exempt_terms": [
            "best practices", "robust", "scalable", "seamless",
        ],
        "zero_weights": ["list_heavy"],
        "decision_threshold": 0.45,
    },
}


def get_profile(name: str) -> dict:
    """Return the genre profile for ``name``; ValueError for unknown genres."""
    try:
        return GENRE_PROFILES[name]
    except KeyError:
        raise ValueError(
            f"unknown genre '{name}' (available: {', '.join(sorted(GENRE_PROFILES))})"
        ) from None


def _term_pattern(term: str) -> str:
    t = term.lower()
    left = r"\b" if t[0].isalnum() else ""
    right = r"\b" if t[-1].isalnum() else ""
    return left + re.escape(t) + right


def strip_exempt_terms(text: str, terms: list) -> str:
    """Remove genre-exempt term occurrences from the text (signal matching
    only; callers keep the full text for structural dimensions)."""
    if not terms:
        return text
    pattern = re.compile(
        "(?:" + "|".join(_term_pattern(t) for t in terms) + ")", re.IGNORECASE
    )
    result = pattern.sub(" ", text)
    return re.sub(r"[ \t]{2,}", " ", result)
