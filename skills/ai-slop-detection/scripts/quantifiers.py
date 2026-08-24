#!/usr/bin/env python3
"""
Quantifier signals (issue #25) — detect-only.

Two signals, neither folded into the numeric slop score:

1. UniversalQuantifiers — subject quantifiers that erase all nuance
   ("everyone knows", "we all", "nobody", "always", "never"). Cumulative
   threshold: >= 2 occurrences in the text fire the signal (one is human,
   two is a pattern).
2. SourceDiscrepancy — the text counts its evidence ("three studies")
   alongside an authority claim ("studies show") but contains no citation
   markers anywhere (parenthetical authors, "et al.", years, DOIs, links).

Collision boundary (#46): weasel_attribution phrases ("experts agree",
"some say") and the scoring AUTHORITY_PATTERNS ("studies have shown") are
unchanged — they already score. This module only reports the quantifier
RATE and the count-without-citation discrepancy as named, detect-only
signals.

Public surface:
    find_quantifier_signals(text) -> {
        "universal_quantifiers": {...}, "source_discrepancy": {...},
        "signals": [{id, confidence, evidence, keep_when}]
    }
"""

import re

UNIVERSAL_QUANTIFIERS = [
    "everyone knows", "everyone agrees", "we all", "nobody", "no one",
    "always", "never",
]

AUTHORITY_CLAIMS = [
    "studies show", "studies have shown", "studies suggest",
    "studies confirm", "research shows", "research suggests",
]

# "three studies", "two papers", "4 trials" ...
COUNTED_SOURCE = re.compile(
    r"\b(?:one|two|three|four|five|six|seven|eight|nine|ten|\d{1,3})\s+"
    r"(studies|papers|trials|experiments|surveys|meta-analyses)\b",
    re.IGNORECASE,
)

# Citation markers anywhere in the text count as "Belege im Text".
CITATION_MARKERS = re.compile(
    r"et al\.?|\(\s*[A-Z][a-zA-Z]+,?\s*\d{4}\s*\)|\[\d{1,3}\]|"
    r"doi\.org|10\.\d{4,}|https?://",
)


def _find_universal_quantifiers(text: str) -> list:
    hits = []
    lowered = text.lower()
    for q in UNIVERSAL_QUANTIFIERS:
        for m in re.finditer(r"\b" + re.escape(q) + r"\b", lowered):
            hits.append({"phrase": q, "offset": m.start()})
    return hits


def find_quantifier_signals(text: str) -> dict:
    quant_hits = _find_universal_quantifiers(text)
    signals = []

    if len(quant_hits) >= 2:
        signals.append({
            "id": "UniversalQuantifiers",
            "confidence": 0.6,
            "evidence": ", ".join(h["phrase"] for h in quant_hits),
            "keep_when": "Deliberate rhetorical universals in obviously "
                         "subjective prose (opinion pieces, speeches) — one "
                         "occurrence never fires anyway.",
        })

    has_authority = any(
        re.search(r"\b" + re.escape(a) + r"\b", text.lower())
        for a in AUTHORITY_CLAIMS
    )
    counted = COUNTED_SOURCE.search(text)
    discrepancy = None
    if has_authority and counted and not CITATION_MARKERS.search(text):
        discrepancy = counted.group(0)
        signals.append({
            "id": "SourceDiscrepancy",
            "confidence": 0.7,
            "evidence": f'"{counted.group(0)}" without citation markers in text',
            "keep_when": "Counts that refer to citations given elsewhere in the "
                         "same document (footnotes, references section) — this "
                         "detector only sees the passed text.",
        })

    return {
        "universal_quantifiers": {
            "count": len(quant_hits),
            "hits": [h["phrase"] for h in quant_hits],
            "fired": len(quant_hits) >= 2,
        },
        "source_discrepancy": {
            "authority_claim": has_authority,
            "counted_sources": counted.group(0) if counted else None,
            "citation_markers_present": bool(CITATION_MARKERS.search(text)),
            "fired": discrepancy is not None,
        },
        "signals": signals,
    }
