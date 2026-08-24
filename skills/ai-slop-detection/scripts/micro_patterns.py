#!/usr/bin/env python3
"""
Micro-pattern detect-only signals (issue #13).

Small, closed-list sentence-level tics that mark AI-assisted prose. Like the
rhetorical patterns module, matches are named patterns with evidence — they
are NOT folded into the numeric slop score. Every pattern carries a
`keep_when` guard so genuine human voice is not flagged.

Collision boundary (#46, no double-scoring): these patterns are distinct
from rhetorical_patterns.HollowKickerRecap (which fires on the recap OPENER
alone). RecapEnding here requires opener AND measurable restatement —
content-word overlap between the concluding sentence and the first sentence
of the text. The other three have no counterpart in any existing module.

Public surface:
    MICRO_PATTERNS          # id -> metadata
    find_micro_patterns(text) -> list[dict]  # {id, confidence, evidence, keep_when}
"""

import re

# Closed lists per issue #13 — deliberately short; anything outside the lists
# is not detected (no scope creep into general NLP).
INANIMATE_SUBJECTS = ["decision", "data", "strategy", "system", "market"]
HUMAN_VERBS = ["emerges", "decides", "believes", "realizes", "knows"]

# FU-3 (#13, review-batch-c): "realizes a gain/profit/loss/return" is
# standard finance register (Fachsprache), not false agency. Closed
# finance tuples — "realizes the vision" stays a hit.
FINANCE_OBJECTS = ("gain", "gains", "profit", "profits", "loss",
                   "losses", "return", "returns", "revenue")
_FINANCE_REALIZES = re.compile(
    r"\brealiz(?:es?|ed|ing)\s+(?:a|an|the|their|its)?\s*"
    r"(?:" + "|".join(FINANCE_OBJECTS) + r")\b",
    re.IGNORECASE,
)

# Grand-sweep endpoints for FalseRange: gesture-at-scale placeholders from
# cosmology/history/tech. Both endpoints must be from this list (or a matched
# grand noun) for the pattern to fire — an everyday "from X to Y" in one
# domain does not.
GRAND_ENDPOINTS = {
    "big bang", "dark matter", "atoms", "galaxies", "dinosaurs", "quantum",
    "roman empire", "stone age", "printing press", "steam engine",
    "microchips", "cave paintings", "black holes", "fire", "the wheel",
}

RECAP_OPENERS = ["in conclusion", "overall,", "to summarize"]

_STOP = {
    "a", "an", "the", "and", "or", "but", "of", "to", "in", "on", "for",
    "with", "is", "are", "was", "were", "be", "it", "its", "this", "that",
    "these", "those", "as", "at", "by", "we", "you", "they", "how", "what",
    "which", "who", "whose", "into", "from", "are", "our", "your", "their",
}


def _content_words(text: str) -> set:
    return set(_ordered_content_words(text))


def _ordered_content_words(text: str) -> list:
    words = re.findall(r"[a-zA-Z']+", text.lower())
    return [w for w in words if w not in _STOP and len(w) > 2]


def _sentences(text: str) -> list:
    return [s.strip() for s in re.split(r"(?<=[.!?])\s+", text.strip()) if s.strip()]


def _false_agency(sentences: list):
    pat = re.compile(
        r"^the\s+(" + "|".join(INANIMATE_SUBJECTS) + r")\s+("
        + "|".join(HUMAN_VERBS) + r")\b",
        re.IGNORECASE,
    )
    for s in sentences:
        if pat.match(s):
            # FU-3: finance register — "The system realizes a gain…" is
            # bookkeeping language, not anthropomorphism.
            if _FINANCE_REALIZES.search(s):
                continue
            return s
    return None


def _false_range(text: str):
    for m in re.finditer(r"from\s+(the\s+)?([a-z][a-z\s]{2,30}?)\s+to\s+(the\s+)?([a-z][a-z\s]{2,30}?)(?=[.,;:)]|$)", text, re.IGNORECASE):
        left = m.group(2).strip().lower()
        right = m.group(4).strip().lower()
        if left in GRAND_ENDPOINTS and right in GRAND_ENDPOINTS:
            return m.group(0)
    return None


def _recap_ending(text: str):
    sentences = _sentences(text)
    if len(sentences) < 2:
        return None
    last = sentences[-1].lower()
    intro_words = _content_words(sentences[0])
    if not intro_words:
        return None
    opener = next((o for o in RECAP_OPENERS if last.startswith(o)), None)
    if opener is None:
        return None
    last_words = _content_words(sentences[-1])
    overlap = len(intro_words & last_words) / max(len(intro_words), 1)
    if overlap >= 0.3:
        return sentences[-1]
    return None


def _heading_repeated(text: str):
    lines = text.split("\n")
    for i, line in enumerate(lines):
        m = re.match(r"^#{1,6}\s+(.+)$", line.strip())
        if not m:
            continue
        heading_words = _content_words(m.group(1))
        if len(heading_words) < 2:
            continue
        for follow in lines[i + 1:]:
            if not follow.strip():
                continue
            first_two = set(_ordered_content_words(follow)[:2])
            if len(first_two) >= 2 and first_two <= heading_words:
                return f"{line.strip()} -> {follow.strip()}"
            break
    return None


MICRO_PATTERNS = {
    "FalseAgency": {
        "label": "False agency",
        "confidence": 0.6,
        "description": "Inanimate subject (decision/data/strategy/system/market) with a "
                       "human verb (emerges/decides/believes/realizes/knows). Closed "
                       "lists; say who actually did it.",
        "example_slop": "The data decides what matters next quarter.",
        "example_fix": "The growth team decides what matters next quarter.",
        "keep_when": "Deliberate, clearly marked personification (e.g. quoted or set off "
                     "as a metaphor), 'emerges' describing genuine systemic emergence "
                     "('order emerges from feedback'), and FU-3 finance register "
                     "('realizes a gain/profit/loss' — Fachsprache, not agency), which "
                     "the verb list still matches only for the named subjects.",
    },
    "FalseRange": {
        "label": "False from-X-to-Y range",
        "confidence": 0.55,
        "description": "Grandiosity sweep 'from the X to the Y' where both endpoints are "
                       "gesture-at-scale placeholders (Big Bang, dark matter, dinosaurs, "
                       "printing press). Name the actual scope.",
        "example_slop": "This guide covers everything from the Big Bang to dark matter.",
        "example_fix": "This guide covers cosmology from the early universe to structure formation.",
        "keep_when": "The endpoints are the literal topic (a cosmology lecture legitimately "
                     "spans Big Bang to dark matter) — the guard is intent, the detector "
                     "only reports the sweep for a human to judge.",
    },
    "RecapEnding": {
        "label": "Recap ending with restatement",
        "confidence": 0.6,
        "description": "Final sentence opens with 'In conclusion'/'Overall'/'To summarize' "
                       "AND restates the intro (>= 30% content-word overlap with the first "
                       "sentence). Requires opener AND overlap; opener alone is "
                       "HollowKickerRecap in rhetorical_patterns (#46 boundary).",
        "example_slop": "In conclusion, AI agents are transforming how teams write software. "
                        "(after an intro saying exactly that)",
        "example_fix": "(end on the last concrete point; cut the restated conclusion)",
        "keep_when": "A conclusion that adds a new, concrete decision or next step rather "
                     "than restating the intro.",
    },
    "HeadingRepeatedBelowItself": {
        "label": "Heading repeated below itself",
        "confidence": 0.5,
        "description": "The first sentence after a heading starts with the same 2+ content "
                       "words as the heading. The heading already said it.",
        "example_slop": "## Deployment Steps\nDeployment steps are straightforward once configured.",
        "example_fix": "## Deployment Steps\nRun the installer and follow the prompts.",
        "keep_when": "Documentation conventions that require the lead sentence to name the "
                     "section subject in full (e.g. legal or spec documents).",
    },
}

_FINDERS = {
    "FalseAgency": lambda text: _false_agency(_sentences(text)),
    "FalseRange": _false_range,
    "RecapEnding": _recap_ending,
    "HeadingRepeatedBelowItself": _heading_repeated,
}


def find_micro_patterns(text: str) -> list:
    """Detect-only: returns [{id, confidence, evidence, keep_when}] — never scored."""
    out = []
    for pid, finder in _FINDERS.items():
        evidence = finder(text)
        if evidence:
            meta = MICRO_PATTERNS[pid]
            out.append({
                "id": pid,
                "confidence": meta["confidence"],
                "evidence": evidence,
                "keep_when": meta["keep_when"],
            })
    return out
