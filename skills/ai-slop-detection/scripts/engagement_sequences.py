#!/usr/bin/env python3
"""Explorative sequence signal for social comments (#231, detect-only).

`engagement_comment_default` fires when a comment follows the default
engagement-farming sequence:

    praise -> paraphrase -> addition -> question

("Great post! / In a world where speed matters, this really resonates.
/ One thing I'd add: measurement. / What are your thoughts on KPIs?")

This is an LLM-default comment template, not a human conversational
pattern: humans rarely thank, summarize, lecture and probe in one breath.
DETECT-ONLY — the finding is reported but never enters the score, so it
cannot gate anything on its own (same policy as the #230 structure
signals). Confirmed evidence pending ADR-0005 hand-written corpus growth.

Detection is deliberately conservative: all four stages must appear, in
order, in <= ~120 words. Short genuine comments ("Great post, congrats!")
lack the sequence and never fire.
"""

import re

_WORD = re.compile(r"\w[\w'-]*")

_PRAISE = re.compile(
    r"\b(?:great|excellent|fantastic|wonderful|brilliant|insightful|"
    r"powerful|valuable|timely)\s+(?:post|article|read|piece|share|point)|"
    r"\b(?:well said|couldn['’]?t agree more|so true|this resonates|"
    r"love this|thanks? (?:so much )?for sharing(?: this)?\??|"
    r"congrats(?:ulations)?[.!]?)\b",
    re.IGNORECASE,
)
_PARAPHRASE = re.compile(
    r"\b(?:this (?:post|article) (?:really )?(?:hits|nails|captures)|"
    r"you(?:'re| are)? (?:so )?right that|in (?:today'?s|a) world[^.!?]{0,40}|"
    r"this really resonates(?: with me)?|(?:so )?true[^.!?]{0,60}|"
    r"(?:this|that) is (?:exactly|precisely) (?:what|why|how))\b",
    re.IGNORECASE,
)
_ADDITION = re.compile(
    r"\b(?:one thing i(?:['’]d| would)? add|here'?s (?:what i['’]d add|my take)|"
    r"my (?:2 cents|two cents)|to (?:build|expand) on (?:this|that)|"
    r"adding to (?:this|that)|another (?:angle|perspective)|"
    r"small (?:addition|nuance)|worth (?:adding|noting))\b",
    re.IGNORECASE,
)
_QUESTION = re.compile(
    r"\b(?:what(?:'s| is| are)? (?:your|your take on|your thoughts on)|"
    r"how do you|have you (?:considered|thought about)|"
    r"curious (?:how|whether|what)|thoughts\?)\b",
    re.IGNORECASE,
)


def find_engagement_comment_default(text: str) -> list:
    """Return list of detect-only sequence findings for ``text``.

    Each finding: {"signal": "engagement_comment_default",
                   "stage_offsets": [(start, end), ...], "evidence": ...}
    Empty list for texts without the full four-stage sequence.
    """
    # Normalize typographic apostrophes/quotes so patterns stay ASCII.
    text = (text.replace("\u2019", "'").replace("\u2018", "'")
                .replace("\u201c", '"').replace("\u201d", '"'))
    words = _WORD.findall(text)
    if len(words) > 120 or len(words) < 8:
        return []

    stages = [
        ("praise", _PRAISE),
        ("paraphrase", _PARAPHRASE),
        ("addition", _ADDITION),
        ("question", _QUESTION),
    ]
    # Stages must appear in order; each stage matched after the previous
    # one's match end. Scanning sentence-chunks keeps offsets cheap.
    pos = 0
    spans = []
    for name, rx in stages:
        m = rx.search(text, pos)
        if not m:
            return []
        spans.append((name, m.start(), m.end()))
        pos = m.end()

    evidence = " -> ".join(
        f"{name}[{text[s:e].strip()[:40]!r}]" for name, s, e in spans)
    return [{
        "signal": "engagement_comment_default",
        "stage_offsets": [(s, e) for _, s, e in spans],
        "evidence": evidence,
        "policy": "detect-only (#231); not scored",
    }]
