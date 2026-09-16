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
        self_answered_questions, paragraph_connector_rate,
        signals: [{id, confidence, evidence, keep_when}]
    }

Issue #230 additions (detect-only, advisory):
4. OpenerAnnouncement — frame-based two-word announcements that open a
   sentence to announce what it does ("Ich möchte ...", "Spannender Punkt.",
   "Ein weiterer Aspekt ist ...", "Die spannende Frage ist ..."). Frames are
   anchored to clause openings (#88-style) and use small [X]-style slots
   (#83-style) instead of a growing word list. keep_when: a genuine stance
   differentiation ("Ich denke, dass X" WITH a following justification is a
   claim, not an announcement) — those are excluded by guard.
5. ParagraphConnectorRate — share of paragraphs that OPEN with an additive
   connector (Darüber hinaus / Zudem / Ein weiterer Punkt / Gleichzeitig /
   Abschließend / Zusammenfassend, EN analogues). Advisory rate; fires as a
   signal only when >= 3 paragraphs do it AND rate > 0.4. keep_when: legal /
   academic register, where connector-led paragraphs are house style.
"""

import re
from collections import Counter

import tokenizer

_SELF_ANSWER = re.compile(
    r"\b(?:Why|What|How|Where|Who|When)\b[^.?!\n]{2,80}\?\s*"
    r"(Because|It'?s simple|Here'?s why|The answer|Simple|Short answer)",
    re.IGNORECASE,
)

# --- Issue #230: opener announcements (frame templates, not word lists) ---
#
# Each frame is anchored to a clause opening (leading "^"): the start of a
# paragraph, after sentence punctuation, or after a line break. Slots are
# minimal ([X] = 1-4 words) so frames describe shapes, not vocabulary.
# Lowercase matching on the lowercased text.
_CLAUSE_OPEN = re.compile(
    r"(?:^|(?<=[.!?\n]))"          # start, or after sentence end / newline
    r"[ \t]*(?:[#>*\u2013-]+[ \t]*)*"  # markup lead-ins (bold, bullets)
    r"(?:(?:[-*+]\|\d+[.)])[ \t]+)?"
)

_OPENER_ANNOUNCEMENT_FRAMES = [
    # German
    r"ich möchte",
    r"ich möchte hier",
    r"ich denke",
    r"spannender punkt",
    r"spannende frage",
    r"die spannende frage ist",
    r"ein weiterer (?:aspekt|punkt|gedanke) ist",
    r"gute frage",
    # English
    r"i want to",
    r"i'?d like to",
    r"let me",
    r"interesting (?:point|question)",
    r"another (?:aspect|point|thought) is",
    r"the (?:interesting|exciting) (?:part|question) is",
    r"great question",
]

# keep_when guard: "Ich denke/glaube, dass ..." (subordinate clause) or
# "I think that ..." carries an actual claim, often with a justification —
# that is stance differentiation, not an announcement. Excluded.
_OPENER_ANNOUNCEMENT_EXEMPT = re.compile(
    r"\b(?:ich (?:denke|glaube)\b[^.!?\n]{0,20}\bdass|"
    r"i (?:think|believe)\b[^.!?\n]{0,20}\bthat|"
    r"meiner meinung nach)\b",
    re.IGNORECASE,
)

# --- Issue #230: additive paragraph connectors (advisory rate) ---
_PARAGRAPH_CONNECTORS = re.compile(
    r"^\s*(?:[#>*\u2013-]+\s*)*(?:[-*+]|\d+[.)])?\s*(?:"
    r"darüber hinaus|darueber hinaus|zudem|zusätzlich|außerdem|ausserdem|"
    r"ein weiterer (?:aspekt|punkt)|gleichzeitig|abschließend|abschliessend|"
    r"zusammenfassend|fazit:|"
    r"moreover|furthermore|additionally|in addition|another (?:aspect|point)|"
    r"finally|in conclusion|to summarize|to summarise"
    r")\b",
    re.IGNORECASE,
)


_FRAME_ANCHOR = re.compile(
    r"(?:^|(?<=[.!?\u2026\n\"\u201c\u201e]))"
    r"[ \t]*(?:[#>*_\u2014\u2013-]+[ \t]*)*"
    r"(?:(?:[-*+]|\d+[.)])[ \t]+)?"
)


def _opener_announcements(text: str) -> list:
    """Frame-based sentence-opening announcements (issue #230).

    Anchored to clause openings; exempt frames that carry a real claim
    ("Ich denke, dass ... with justification").
    """
    lowered = text.lower()
    hits = []
    for frame in _OPENER_ANNOUNCEMENT_FRAMES:
        rx = _FRAME_ANCHOR.pattern + frame
        for m in re.finditer(rx, lowered):
            # Evidence quote: up to ~12 words from the match start.
            tail = lowered[m.start():m.start() + 120]
            words = tail.split()
            quote = " ".join(words[:12])
            if _OPENER_ANNOUNCEMENT_EXEMPT.search(tail):
                continue
            hits.append(quote)
    return hits


def _paragraph_connector_rate(text: str):
    """Share of paragraphs opening with an additive connector (issue #230)."""
    paragraphs = [p for p in re.split(r"\n\s*\n|\r\n\s*\r\n", text) if p.strip()]
    if not paragraphs:
        return (0, 0.0)
    opened = sum(1 for p in paragraphs if _PARAGRAPH_CONNECTORS.search(p))
    return (opened, opened / len(paragraphs))



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

    # Issue #230: opener announcements + paragraph connector rate (advisory).
    announcements = _opener_announcements(text)
    if announcements:
        signals.append({
            "id": "OpenerAnnouncement",
            "confidence": 0.5,
            "evidence": f"{len(announcements)} announcement-style opener(s): "
                        f"'{announcements[0]}'",
            "keep_when": "Genuine stance differentiation is exempt: "
                         "'Ich denke, dass X' (with a following justification) "
                         "and 'I think that ...' carry a claim, not a frame.",
        })
    connector_opened, connector_rate = _paragraph_connector_rate(text)
    if connector_opened >= 3 and connector_rate > 0.4:
        signals.append({
            "id": "ParagraphConnectorRate",
            "confidence": 0.45,
            "evidence": f"{connector_opened} paragraphs open with an additive "
                        f"connector (rate {round(connector_rate * 100)}%)",
            "keep_when": "Legal or academic register, where connector-led "
                         "paragraphs are house style ('Darüber hinaus' in "
                         "statutes, pleadings, papers).",
        })

    return {
        "max_uniform_length_run": run,
        "top_opener_share": round(share, 3),
        "self_answered_questions": self_answers,
        "paragraph_connector_rate": round(connector_rate, 3),
        "signals": signals,
    }
