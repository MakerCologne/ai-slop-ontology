#!/usr/bin/env python3
"""
Rhythm / opener metrics (issue #27) — detect-only.

Three prose-rhythm measurements reported as named signals (never scored):

1. UniformLengthRun — 3+ CONSECUTIVE sentences within ±5% of the same word
   count. Boundary (#46): distinct from the global UniformSentenceLength
   structural indicator (std-dev over the whole text) and from RoboticRhythm
   (very short fragments) — this catches a local metronome mid-text.
2. SelfAnsweredQuestion — the text asks "Why X?" / "What's the catch?" and
   immediately answers itself with a stock lead-in ("Because", "It's
   simple:", "Here's why:"). Boundary: rhetorical_setups phrases in the
   scorer's phrase DB cover the question side; this pattern requires the
   self-answer pair.
3. LowOpenerDiversity — > 30% of sentences (>= 4 sentences required) start
   with the same two-word signature. Boundary: RepeatedOpenings in
   rhetorical_patterns fires on 3+ adjacent same-WORD openings as a pattern
   instance; this is a whole-text RATE over two-word openers.

Public surface:
    rhythm_metrics(text) -> {
        max_uniform_length_run, top_opener_share,
        self_answered_questions, signals: [{id, confidence, evidence, keep_when}]
    }
"""

import re
from collections import Counter

import tokenizer

_SELF_ANSWER = re.compile(
    r"\b(?:Why|What|How|Where|Who|When)\b[^.?!\n]{2,80}\?\s*"
    r"(Because|It'?s simple|Here'?s why|The answer|Simple|Short answer)",
    re.IGNORECASE,
)


def _uniform_length_run(sentences: list) -> int:
    lengths = [len(s.split()) for s in sentences]
    best = cur = 0
    for i, n in enumerate(lengths):
        if i > 0 and abs(n - lengths[i - 1]) <= 0.05 * max(n, lengths[i - 1]):
            cur += 1
        else:
            cur = 1
        best = max(best, cur)
    return best


def _opener_share(sentences: list):
    if len(sentences) < 4:
        return ("", 0.0)
    openers = []
    for s in sentences:
        words = s.split()
        openers.append(" ".join(w.lower() for w in words[:2]))
    top, count = Counter(openers).most_common(1)[0]
    return (top, count / len(openers))


def rhythm_metrics(text: str) -> dict:
    sentences = [s.strip() for s in tokenizer.split_sentences(text) if s.strip()]
    run = _uniform_length_run(sentences) if sentences else 0
    self_answers = len(_SELF_ANSWER.findall(text))
    top_opener, share = _opener_share(sentences)

    signals = []
    if run >= 3:
        signals.append({
            "id": "UniformLengthRun",
            "confidence": 0.5,
            "evidence": f"{run} consecutive sentences within ±5% word count",
            "keep_when": "Parallel construction used deliberately (legal "
                         "documents, litany-style prose).",
        })
    if self_answers:
        signals.append({
            "id": "SelfAnsweredQuestion",
            "confidence": 0.6,
            "evidence": f"{self_answers} self-answered question(s)",
            "keep_when": "A genuine FAQ-style Q&A where the question comes "
                         "from real users, not from the author.",
        })
    if share > 0.3:
        signals.append({
            "id": "LowOpenerDiversity",
            "confidence": 0.5,
            "evidence": f"'{top_opener} ...' starts {round(share * 100)}% of sentences",
            "keep_when": "Deliberate anaphora; short texts (< 4 sentences) "
                         "never fire.",
        })

    return {
        "max_uniform_length_run": run,
        "top_opener_share": round(share, 3),
        "self_answered_questions": self_answers,
        "signals": signals,
    }
