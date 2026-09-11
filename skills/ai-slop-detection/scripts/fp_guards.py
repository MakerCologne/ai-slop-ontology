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


# --- #115: keep_when-Guards fuer performative_voice + manufactured_stakes
# Die beiden ZeroSlop-Muster sind in konkreten menschlichen Kontexten
# legitim: gelebte statt performte Stimme ("nobody tells you this — when
# I started out I lost $3k") und echte statt dramatisierter Dringlichkeit
# ("time is running out: the deadline is 15 October"). Guards maskieren
# die Phrase VOR dem Signal-Matching (gleiche Mechanik wie #110:
# Maskierung statt Post-Filter auf Counts).

_PV_PHRASES = (
    "here's the thing nobody tells you",
    "nobody tells you",
    "i'm going to be honest with you",
    "let me be brutally honest",
    "i don't say this lightly",
    "unpopular opinion, but",
    "call me old-fashioned, but",
)

# First-Person-Erfahrungs-Anker: gelebte Erfahrung im Umkreis der Phrase
# => kein performtes, sondern echtes Voice-Signal. Der Anker selbst bleibt
# sichtbar (nur der Phrase-Kopf wird maskiert).
_PV_EXPERIENCE_ANCHOR_RE = re.compile(
    r'\bwhen\s+i\b|\bin\s+my\s+(?:own\s+)?(?:experience|case)\b|'
    r'\bi\s+(?:lost|spent|learned|tried|failed|was|found)\b|'
    r'\bi(?:\u2019ve|\u2019m| have)\s+(?:seen|learned|made|been)\b',
    re.I,
)
_PV_WINDOW = 120

_MS_PHRASES = (
    "in today's fast-paced",
    "the stakes have never been higher",
    "now more than ever",
    "at a critical juncture",
    "time is running out",
    "don't get left behind",
    "before it's too late",
)

# Konkreter Termin/Fakt im Folgefenster => echte Dringlichkeit.
# Woche-/Monatsnamen mit Datum, "deadline"/"by/until <Zeit>", Ziffern mit
# Einheit (%, EUR, USD, days, weeks, hours) — Deterministischer Proxy
# fuer "hinter der Dringlichkeit steht eine Sache".
_MS_CONCRETE_RE = re.compile(
    r'\b(?:deadline|due)\b[^\n]{0,40}\b\d|'
    r'\b(?:by|until|before)\s+(?:\d{1,2}\s+)?'
    r'(?:monday|tuesday|wednesday|thursday|friday|saturday|sunday|'
    r'january|february|march|april|may|june|july|august|september|'
    r'october|november|december)\b|'
    r'\b\d{1,2}[./-]\d{1,2}(?:[./-]\d{2,4})?\b|'
    r'\b\d+(?:[.,]\d+)?\s?(?:%|eur|usd|euros?|dollars?|days?|weeks?|hours?|minutes?)(?!\w)',
    re.I,
)
_MS_WINDOW = 120


def mask_performative_stakes(text_lower: str) -> str:
    """Mask #115 keep_when occurrences in (already lowercased) signal text.

    performative_voice: phrase masked when a first-person experience
    anchor sits within +-120 chars (lived voice, not performed voice).
    manufactured_stakes: phrase masked when a concrete date/deadline/
    quantity follows within 120 chars (real urgency, not manufactured).
    Masking keeps positions and overlap logic intact for all other
    categories.
    """
    result = text_lower
    spans = []
    for phrase in _PV_PHRASES:
        for m in re.finditer(re.escape(phrase), result):
            window = result[max(0, m.start() - _PV_WINDOW):
                            m.end() + _PV_WINDOW]
            if _PV_EXPERIENCE_ANCHOR_RE.search(window):
                spans.append((m.start(), m.end()))
    for phrase in _MS_PHRASES:
        for m in re.finditer(re.escape(phrase), result):
            window = result[m.end():m.end() + _MS_WINDOW]
            if _MS_CONCRETE_RE.search(window):
                spans.append((m.start(), m.end()))
    for start, end in sorted(spans, reverse=True):
        result = result[:start] + " " * (end - start) + result[end:]
    return result
