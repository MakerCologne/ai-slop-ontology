"""Voice-Drift-Guardrail (#56).

Detect-only guard (ADR-0001: kein Rewriter) against stylistic homogenisation
through iterated rewriting (Model Collapse; arXiv:2305.17493, arXiv:2307.01850)
and against violations of Minimum-Effective-Edit.

Two independent checks, both bound to **Draft_0** (not the current draft —
per-iteration budgets alone would allow drift to accumulate unnoticed):

1. **Voice-Budget:** cumulative token-change rate draft_0 -> draft_n must not
   exceed beta (default 25%, KL-Guardrail-Analogon per Gao et al.
   arXiv:2210.10760). Edit-distance-style on token multisets:
   (inserted + replaced) / draft_0 tokens, capped at 1.0.
2. **Non-Regression:** burstiness (sentence-length variation, coefficient of
   variation) and lexical diversity (windowed type-token ratio over content
   words) of draft_n must not fall below draft_0's value x 0.9.
   Violation -> verdict "rollback".

Output is a plain dataclass (no score contribution): the deslop loop uses it
to reject/rollback candidates; callers may use it standalone.
"""

from __future__ import annotations

import re
from collections import Counter
from dataclasses import dataclass, field
from typing import List, Optional

_TOKEN_RE = re.compile(r"\b\w+\b")
_SENT_RE = re.compile(r"[^.!?]+[.!?]+|[^.!?]+$")

# window size for windowed TTR (MATTR-style); short windows make TTR
# length-robust for both tweets and long drafts
_TTR_WINDOW = 50


@dataclass
class VoiceDriftParams:
    beta: float = 0.25                 # max cumulative token change vs draft_0
    regression_floor: float = 0.9      # burstiness/TTR floor = draft_0 * floor
    min_tokens: int = 12               # below this, guard is trivially OK


@dataclass
class VoiceDriftVerdict:
    verdict: str                       # "ok" | "budget" | "regression" | "too_short"
    token_change_pct: float            # cumulative change vs draft_0 (0..1)
    burstiness_0: float
    burstiness_n: float
    burstiness_delta: float
    ttr_0: float
    ttr_n: float
    ttr_delta: float
    reasons: List[str] = field(default_factory=list)

    def __bool__(self) -> bool:
        return self.verdict == "ok"


def _tokens(text: str) -> List[str]:
    return _TOKEN_RE.findall(text.lower())


def token_change_vs(draft_0: str, draft_n: str) -> float:
    """Cumulative token-change rate vs draft_0 (0.0 identical, ~1.0 rewrite).

    (inserted + replaced) / draft_0 tokens, capped at 1.0 — an exact
    implementation of the spec formula, not the symmetric Jaccard variant
    used as loop-internal voice_budget heuristic.
    """
    a = Counter(_tokens(draft_0))
    b = Counter(_tokens(draft_n))
    n0 = sum(a.values())
    if n0 == 0:
        return 0.0 if not b else 1.0
    common = sum((a & b).values())
    removed = n0 - common          # replaced-or-deleted (replaced == removed)
    inserted = sum((b - a).values())
    return min(1.0, (removed + inserted) / n0)


def burstiness(text: str) -> float:
    """Sentence-length burstiness: coefficient of variation of sentence
    token counts (variance / mean). Higher = more human-rhythmic; uniform
    sentence machine text collapses toward 0."""
    sents = [_tokens(s) for s in _SENT_RE.findall(text)]
    lens = [len(s) for s in sents if len(s) > 0]
    if len(lens) < 2:
        return 0.0
    mean = sum(lens) / len(lens)
    if mean == 0:
        return 0.0
    var = sum((x - mean) ** 2 for x in lens) / len(lens)
    return (var ** 0.5) / mean


def _content_tokens(tokens: List[str]) -> List[str]:
    # light stopword strip: synonym diversity lives on content words
    _STOP = {
        "the", "a", "an", "and", "or", "but", "of", "to", "in", "on", "at",
        "is", "are", "was", "were", "be", "been", "it", "its", "this",
        "that", "with", "for", "as", "by", "from", "not", "der", "die",
        "das", "und", "oder", "ist", "sind", "war", "den", "dem", "ein",
        "eine", "einer", "mit", "auf", "für", "von", "nicht", "zu", "im",
    }
    return [t for t in tokens if t not in _STOP and len(t) > 2]


def lexical_diversity(text: str) -> float:
    """Windowed type-token ratio (TTR) over content words; synonym-variety
    proxy that does not shrink mechanically with text length."""
    toks = _content_tokens(_tokens(text))
    if not toks:
        return 0.0
    w = _TTR_WINDOW
    if len(toks) <= w:
        return len(set(toks)) / len(toks)
    ratios = [
        len(set(toks[i:i + w])) / w
        for i in range(0, len(toks) - w + 1, max(1, w // 2))
    ]
    return sum(ratios) / len(ratios)


def evaluate(draft_0: str, draft_n: str,
             params: Optional[VoiceDriftParams] = None) -> VoiceDriftVerdict:
    """Full voice-drift check of draft_n against draft_0."""
    p = params or VoiceDriftParams()
    reasons: List[str] = []

    b0, bn = burstiness(draft_0), burstiness(draft_n)
    t0, tn = lexical_diversity(draft_0), lexical_diversity(draft_n)
    change = token_change_vs(draft_0, draft_n)

    if len(_tokens(draft_0)) < p.min_tokens or len(_tokens(draft_n)) < p.min_tokens:
        return VoiceDriftVerdict("too_short", round(change, 4), b0, bn,
                                 round(bn - b0, 4), t0, tn, round(tn - t0, 4),
                                 ["text below min_tokens; guard not applicable"])

    verdict = "ok"
    if change > p.beta:
        verdict = "budget"
        reasons.append(
            f"token_change {change:.1%} > beta {p.beta:.0%} vs draft_0 "
            f"(Minimum-Effective-Edit verletzt, Gao et al. 2210.10760)")
    if b0 > 0 and bn < b0 * p.regression_floor:
        if verdict == "ok":
            verdict = "regression"
        reasons.append(
            f"burstiness regression {b0:.3f} -> {bn:.3f} "
            f"(< draft_0 x {p.regression_floor}); Homogenisierung")
    if t0 > 0 and tn < t0 * p.regression_floor:
        if verdict == "ok":
            verdict = "regression"
        reasons.append(
            f"TTR regression {t0:.3f} -> {tn:.3f} "
            f"(< draft_0 x {p.regression_floor}); Synonym-Vielfalt sinkt")

    return VoiceDriftVerdict(
        verdict, round(change, 4), round(b0, 4), round(bn, 4),
        round(bn - b0, 4), round(t0, 4), round(tn, 4), round(tn - t0, 4),
        reasons,
    )
