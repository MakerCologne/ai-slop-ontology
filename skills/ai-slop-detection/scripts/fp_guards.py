#!/usr/bin/env python3
"""
False-positive guards for the AI-slop skill scorer (issue #23).

Three systematics, all applied to *signal matching only* (buzzwords, phrase
categories, authority claims). Structural dimensions (density, burstiness,
repetition) always measure the full text.

(a) Quote exemption: quoted passages longer than QUOTE_MIN_CHARS are treated
    as quoted material — e.g. a review, documentation or meta-analysis that
    reproduces a slop example must not inherit the example's slop signals.
    Short quotes (a single word, a term) are kept: quoting "delve" in a
    discussion is a legitimate signal context.
(b) Cumulative rule: a phrase category contributes to phrase_slop only with
    >= PHRASE_MIN_HITS hits. Single hits are reported in signals but not
    scored — one "here's the thing" in an otherwise technical text is a
    stylistic accident, not a pattern.
(c) Consistent thresholds: one THRESHOLDS mapping used by the scorer for
    guard sizes and the decision threshold.
"""

import re

THRESHOLDS = {
    "DECISION_THRESHOLD": 0.40,   # >= threshold => "Suspicious" or worse
    "QUOTE_MIN_CHARS": 40,        # quoted spans longer than this are exempt
    "PHRASE_MIN_HITS": 2,         # hits per phrase category before scoring
    # FU-12: generic watchlist phrases need a raised cumulative bar —
    # they are everyday human prose when they appear once or twice.
    "GENERIC_PHRASE_MIN_HITS": 3,
}

# ASCII double/single quotes and curly variants. Nested/unbalanced quotes are
# handled by the regex fallbacks below (non-greedy pair matching).
_QUOTE_PAIRS = [
    (re.compile(r'"([^"]{' + str(THRESHOLDS["QUOTE_MIN_CHARS"]) + r',})"'), ""),
    (re.compile(r'\u201c([^\u201d]{' + str(THRESHOLDS["QUOTE_MIN_CHARS"]) + r',})\u201d'), ""),
    (re.compile(r'(?<!\w)\'([^\']{' + str(THRESHOLDS["QUOTE_MIN_CHARS"]) + r',})\'(?!\w)'), ""),
]


def strip_quotes(text: str) -> str:
    """Remove quoted passages longer than QUOTE_MIN_CHARS from the text."""
    result = text
    for pattern, _ in _QUOTE_PAIRS:
        result = pattern.sub(" ", result)
    # collapse whitespace artifacts left by removal
    result = re.sub(r"[ \t]{2,}", " ", result)
    return result


def effective_phrase_count(phrase_matches: dict, category_min_hits: dict = None) -> int:
    """Total phrase hits counting only categories that meet their minimum.

    Default minimum is PHRASE_MIN_HITS (2); FU-12 lets a category declare
    a raised minimum via PHRASE_CATEGORIES[cat]["min_hits"] (passed here
    as category_min_hits, e.g. {"generic_phrases": 3}).
    """
    category_min_hits = category_min_hits or {}
    total = 0
    for cat, hits in phrase_matches.items():
        minimum = category_min_hits.get(cat, THRESHOLDS["PHRASE_MIN_HITS"])
        if len(hits) >= minimum:
            total += len(hits)
    return total
