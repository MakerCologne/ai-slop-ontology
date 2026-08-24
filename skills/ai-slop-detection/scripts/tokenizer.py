#!/usr/bin/env python3
"""CJK-capable tokenization for the metric basis (issue #43).

Whitespace tokenization remains the default for space languages. Text
containing CJK characters has no whitespace word boundaries — a naive
``\\b\\w+\\b`` over such text yields one mega-token per sentence, making
word counts, density, repetition and burstiness meaningless. This module
provides:

- ``tokenize_words(text)``: per-character tokens for CJK runs, whitespace
  word tokens elsewhere, CJK punctuation excluded.
- ``split_sentences(text)``: splits on ASCII ``.!?`` AND CJK sentence
  enders ``。！？``.

Scope guard: no new language signals here (that is issue #53) — this only
makes the existing metrics meaningful for CJK input.
"""

import re

# CJK Unicode blocks: Hiragana + Katakana, CJK Ext A, CJK Unified, CJK
# Compat Ideographs. (Hangul is syllable-blocked and out of the minimal set.)
_CJK_RANGES = (
    (0x3040, 0x30FF),   # Hiragana / Katakana
    (0x3400, 0x4DBF),   # CJK Extension A
    (0x4E00, 0x9FFF),   # CJK Unified Ideographs
    (0xF900, 0xFAFF),   # CJK Compatibility Ideographs
)

_CJK_PUNCTUATION = set("。，、；：？！「」『』（）《》…—·") | {
    "\u3000",  # ideographic space
    "\u3001",  # 、
    "\u3002",  # 。
}

_ASCII_WORD = re.compile(r"\b\w+\b")
_SENTENCE_SPLIT = re.compile(r"[.!?。！？]+")


def is_cjk_char(ch: str) -> bool:
    code = ord(ch)
    return any(lo <= code <= hi for lo, hi in _CJK_RANGES)


def has_cjk(text: str) -> bool:
    return any(is_cjk_char(ch) for ch in text)


def tokenize_words(text: str) -> list:
    """Word tokens: whitespace words for space languages, per-character
    tokens for CJK runs (punctuation excluded), lowercase."""
    tokens = []
    run = []  # current CJK-free run
    for ch in text:
        if is_cjk_char(ch):
            if run:
                tokens.extend(w.lower() for w in _ASCII_WORD.findall("".join(run)))
                run = []
            tokens.append(ch.lower())
        else:
            run.append(ch)
    if run:
        tokens.extend(w.lower() for w in _ASCII_WORD.findall("".join(run)))
    return [t for t in tokens if t not in _CJK_PUNCTUATION]


def split_sentences(text: str) -> list:
    """Sentences delimited by ASCII .!? and CJK 。！？ (stripped)."""
    return [s.strip() for s in _SENTENCE_SPLIT.split(text) if s.strip()]
