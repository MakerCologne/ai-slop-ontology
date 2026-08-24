#!/usr/bin/env python3
"""
Provenance markers for the AI-slop skill scorer (issue #20).

Deterministic regex signals — artifacts left in text by AI pipelines.
High confidence by nature: no human writing contains them by accident,
so detection is reported per match and treated as strong evidence in the
scorer (provenance family in the escalation rule, floor at the decision
threshold).

Marker families:
  turn_search         r"turn\d+search\d+"          chat/search-loop references
  citation_artifact   r":contentReference\["      citation-rendering artifacts
  placeholder_date    r"\b(?:19|20)\d{2}-XX-XX\b" unfilled date template slots
  pua_characters      U+E000..U+F8FF              invisible watermark codepoints
"""

import re

PATTERNS = {
    "turn_search": re.compile(r"\bturn\d+search\d+\b"),
    "citation_artifact": re.compile(r":contentReference\["),
    "placeholder_date": re.compile(r"\b(?:19|20)\d{2}-XX-XX\b"),
    "pua_characters": re.compile(r"[\ue000-\uf8ff]"),
}


def provenance_hits(text: str) -> dict:
    """Return {family: [matched_strings]} for all provenance marker families
    (families without matches are present with empty lists so callers can
    index without KeyError)."""
    results = {}
    for family, pattern in PATTERNS.items():
        matches = pattern.findall(text)
        if matches and family == "pua_characters":
            results[family] = [f"\\u{ord(c):04x}" for c in matches]
        else:
            results[family] = matches or []
    return results


def provenance_count(text: str) -> int:
    return sum(len(v) for v in provenance_hits(text).values())
