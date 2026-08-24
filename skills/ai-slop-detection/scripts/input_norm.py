#!/usr/bin/env python3
"""Input normalization & anti-evasion layer (issue #40).

Applied to ALL input BEFORE any metric, so evasions cannot slip signals past
the scorer:

1. Unicode NFKC normalization (folds FULLWIDTH and compatibility forms).
2. Zero-width stripping: ZWSP/ZWNJ/ZWJ (U+200B-200D) and BOM (U+FEFF) —
   used to break up telltale words ("del\u200bve") invisibly.
3. Homoglyph mapping for the minimal confusable Cyrillic/Latin pairs
   (а→a, е→e, о→o, р→p, с→c, х→x) — applied after NFKC because NFKC does
   not fold lookalike letters across scripts.

Idempotent: normalize(normalize(x)) == normalize(x).
"""

import unicodedata

# Minimal Cyrillic → Latin confusable table (issue #40 scope: deliberately
# NOT a full confusables.txt import — extend when a real evasion case lands).
HOMOGLYPHS = {
    "а": "a",  # U+0430 CYRILLIC SMALL LETTER A
    "е": "e",  # U+0435 CYRILLIC SMALL LETTER IE
    "о": "o",  # U+043E CYRILLIC SMALL LETTER O
    "р": "p",  # U+0440 CYRILLIC SMALL LETTER ER
    "с": "c",  # U+0441 CYRILLIC SMALL LETTER ES
    "х": "x",  # U+0445 CYRILLIC SMALL LETTER HA
}

ZERO_WIDTH = {"\u200b", "\u200c", "\u200d", "\ufeff"}

_HOMOGLYPH_TABLE = str.maketrans(HOMOGLYPHS)


def normalize(text: str) -> str:
    """NFKC + zero-width strip + homoglyph map. Runs before all metrics."""
    if not text:
        return text
    # 1. NFKC (also folds FULLWIDTH forms like ｄ -> d)
    text = unicodedata.normalize("NFKC", text)
    # 2. zero-width characters are invisible joiners/spacers, never content
    text = "".join(ch for ch in text if ch not in ZERO_WIDTH)
    # 3. lookalike Cyrillic letters become their Latin counterparts
    text = text.translate(_HOMOGLYPH_TABLE)
    return text
