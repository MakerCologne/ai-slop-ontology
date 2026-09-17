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


# --- #110: Hard-Negative-Guards fuer conversational_fillers -------------
# Zwei Phrasen der Hassid-Liste sind in konkreten menschlichen Kontexten
# legitim und duerfen einzeln nicht feuern ("Hope this helps" in echten
# Support-Mails, "Most people I interviewed ..." mit echter Quelle).
# Guards maskieren die Phrasen VOR dem Signal-Matching (kein Post-Filter
# auf Counts — Maskierung haelt Positionen und Ueberlappungs-Logik intakt).

# Grussformeln (EN + DE), die einen Support-/Mail-Kontext anzeigen.
_SIGNOFF_RE = re.compile(
    r'\b(?:best regards|kind regards|warm regards|regards|cheers|sincerely|'
    r'best wishes|many thanks|thanks(?: in advance)?|thank you|'
    r'mit freundlichen gr(?:u|\u00fc)\u00df(?:en|\b)|viele gr(?:u|\u00fc)\u00dfe|'
    r'beste gr(?:u|\u00fc)\u00dfe)\b[,.!]?'
)

# DoD #110: Phrase zaehlt nur, wenn sie NICHT in den letzten 100 Zeichen
# vor einer Grussformel steht (positionsbasiert, Empfehlung des Issues).
_SIGNOFF_WINDOW = 100

_HOPE_THIS_HELPS = "hope this helps"

# Direkte Quellenangaben nach "most people" => echte Empirie, kein
# Pseudo-Quantifikator-Mehrheitsclaim.
_MOST_PEOPLE_ATTRIBUTION_RE = re.compile(
    r'\bmost people\b[,.]?\s+(?:i|we)\s+'
    r'(?:interviewed|surveyed|asked|polled|spoke\s+(?:with|to)|heard\s+from)|'
    r'\bmost people\s+(?:i|we)\s+know\b|'
    r'\bmost people\s+(?:in|on)\s+(?:my|our)\s+'
    r'(?:survey|team|company|street|feed|timeline)\b'
)


def mask_conversation_fillers(text_lower: str) -> str:
    """Mask #110 hard negatives in (already lowercased) signal text.

    Returns text with guarded occurrences replaced by spaces so that
    phrase matching (longest-match / overlap suppression in
    slop_scorer.find_term_matches) never sees them. All other categories
    and structural metrics are unaffected.
    """
    result = text_lower
    # Collect first, then replace from the end (offsets stay valid).
    spans = []
    for m in re.finditer(re.escape(_HOPE_THIS_HELPS), result):
        # Suppress only when a sign-off starts within the following
        # _SIGNOFF_WINDOW chars (i.e. the phrase sits in the last 100
        # chars before the sign-off).
        window = result[m.end():m.end() + _SIGNOFF_WINDOW]
        if _SIGNOFF_RE.search(window):
            spans.append((m.start(), m.end()))
    for m in _MOST_PEOPLE_ATTRIBUTION_RE.finditer(result):
        # Mask only the "most people" head, not the attribution itself:
        # the attribution is the human evidence, the claim head is the
        # pattern. (Masking the full span would also be correct; keeping
        # the attribution visible preserves context for other signals.)
        spans.append((m.start(), m.start() + len("most people")))
    for start, end in sorted(spans, reverse=True):
        result = result[:start] + " " * (end - start) + result[end:]
    return result
