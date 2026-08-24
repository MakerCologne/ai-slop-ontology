#!/usr/bin/env python3
"""
Sentence portability measurement (issue #14).

A sentence is *portable* when it contains nothing anchoring it to a specific
context: no proper names (no capitalized token except the sentence-initial
word), no numbers, no quotes or code spans. Text whose sentences are almost
all portable could appear anywhere — a weak slop indicator (generic filler),
deliberately low-weighted (0.03) and never an escalation family.

Cross-language note: German (and other languages capitalizing nouns
mid-sentence) will rarely rate as portable by this heuristic — that is the
intended conservative behavior: we only ever claim portability when there is
no mid-sentence capital at all.

Public surface:
    portability_stats(text) -> {"portable_sentences", "total", "rate"}
"""

import re

import tokenizer

# A portable sentence contains none of: capitalized words (beyond position 0),
# digits, quote marks, code spans.
_CAPITAL = re.compile(r"\b[A-ZÄÖÜ][a-zäöüß]+")
_ANY_CAPITAL = re.compile(r"\b[A-ZÄÖÜÀ-Þ]")
_DIGIT = re.compile(r"\d")
_QUOTE_OR_CODE = re.compile(r"[\"'`«»„]|```")
# URLs, paths, emails anchor a sentence to a context too.
_LINKISH = re.compile(r"/|@|https?|www\.")


def _is_portable(sentence: str) -> bool:
    words = sentence.split()
    if not words:
        return False
    # Strip the sentence-initial word: it is legitimately capitalized.
    rest = " ".join(words[1:])
    if _ANY_CAPITAL.search(rest):
        return False
    # Sentence-initial acronym/brand (e.g. "NASA says") is still a name.
    if len(words[0]) > 1 and _ANY_CAPITAL.search(words[0][1:]):
        return False
    if _DIGIT.search(sentence) or _QUOTE_OR_CODE.search(sentence) or _LINKISH.search(sentence):
        return False
    return True


def portability_stats(text: str) -> dict:
    """Rate of sentences with no names, numbers, quotes, or code (0-1)."""
    sentences = [s for s in tokenizer.split_sentences(text) if s.strip()]
    if not sentences:
        return {"portable_sentences": 0, "total": 0, "rate": 0.0}
    portable = sum(1 for s in sentences if _is_portable(s.strip()))
    return {
        "portable_sentences": portable,
        "total": len(sentences),
        "rate": round(portable / len(sentences), 3),
    }
