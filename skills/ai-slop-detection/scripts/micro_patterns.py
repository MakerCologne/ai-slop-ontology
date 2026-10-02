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

# --- ActorlessClaim (#248, Gap G4) ----------------------------------------
# Passive voice carrying a claim with no agent ("mistakes were made",
# "queries are validated", "it was decided that"). Convergent from unslop
# rule 29 and slopbeth "Actorless claims" (Deep-Dive #39). Closed verb list —
# only claim-bearing participles; descriptive passives ("the file was large")
# are out of scope.
AGENTLESS_CLAIM_VERBS = (
    "decided", "determined", "concluded", "agreed", "noted", "made",
    "implemented", "established", "addressed", "resolved", "mitigated",
    "optimized", "ensured", "validated", "chosen", "selected",
)
_AGENT_MARKER = re.compile(r"\bby\s+[A-Za-z]", re.IGNORECASE)
_OBLIGATION_MARKER = re.compile(r"\b(?:shall|must)\b", re.IGNORECASE)
_AGENTLESS_CLAIM = re.compile(
    r"\b(?:it|this|that)\s+(?:was|were|is|are|has been|have been)\s+"
    r"(?:" + "|".join(AGENTLESS_CLAIM_VERBS) + r")\s+(?:that|to)\b"
    r"|\b[A-Za-z ]{2,40}?\s+(?:was|were|is|are)\s+"
    r"(?:" + "|".join(AGENTLESS_CLAIM_VERBS) + r")\b"
    r"|\bmistakes\s+were\s+made\b",
    re.IGNORECASE,
)

# G6 (issue #249 / unslop #2): NameDropList — media/brand enumerations
# without statement content. Lead-ins are a closed list; the second path
# (bare enumeration, almost nothing else in the sentence) is capped by
# MAX_NON_LIST_WORDS so it only fires on genuinely content-free lists.
NAME_DROP_LEADINS = [
    "featured in", "as featured in", "seen in", "as seen in", "seen on",
    "as seen on", "covered by", "mentioned in", "praised by", "endorsed by",
    "trusted by", "recommended by", "highlighted in", "spotlighted in",
]

# If any of these content verbs shape the list, the sentence makes a real
# statement about the named things (comparison, review, interview) — not
# a bare name drop.
NAME_DROP_KEEP_VERBS = [
    "compared", "tested", "benchmark", "benchmarked", "analyzed",
    "analysed", "reviewed", "studied", "interviewed", "surveyed",
    "evaluated", "ranked", "audited", "measured", "mapped",
]
MAX_NON_LIST_WORDS = 6

# One enumerated item: capitalized word(s), optionally "The X"/"X of the Y".
_ITEM = r"(?:[Tt]he\s+)?[A-Z][\w&.'’-]*(?:\s+[A-Z][\w&.'’-]*)*"
_NAME_ENUM = re.compile(
    r"(" + _ITEM + r"(?:\s*,\s*(?:and\s+|or\s+)?" + _ITEM + r"){2,})"
)

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


def _actorless_claim(text: str):
    for s in _sentences(text):
        # keep_when guards: explicit agent named, or policy/legal register
        # where agentless obligation is intended (shall/must).
        if _AGENT_MARKER.search(s) or _OBLIGATION_MARKER.search(s):
            continue
        if re.match(r"^\s*(?:we|i|you)\b", s, re.IGNORECASE):
            continue
        m = _AGENTLESS_CLAIM.search(s)
        if m:
            return s
def _name_drop_items(enum_match: str):
    """Split an enumeration core into cleaned item strings."""
    items = [p.strip() for p in enum_match.split(",")]
    cleaned = []
    for it in items:
        it = re.sub(r"^(?:and|or)\s+", "", it, flags=re.IGNORECASE).strip()
        # trailing 'and X' inside the last comma-less segment
        parts = re.split(r"\s+(?:and|&)\s+", it)
        cleaned.extend(p.strip() for p in parts if p.strip())
    return cleaned


def _name_drop_list(text: str):
    for raw_line in text.split("\n"):
        line = raw_line.strip()
        # Reference-list conventions are legitimate enumerations by design.
        if (not line or line.startswith(("-", "*", ">", "[", "(", "#"))
                or line[0].isdigit() or "http" in line.lower()):
            continue
        for s in _sentences(line):
            low = s.lower()
            if any(v in low for v in NAME_DROP_KEEP_VERBS):
                continue
            m = _NAME_ENUM.search(s)
            if not m:
                continue
            items = _name_drop_items(m.group(1))
            if len(items) < 3:
                continue
            lead_in = next((li for li in NAME_DROP_LEADINS if li in low), None)
            remainder = (s[:m.start(1)] + " " + s[m.end(1):]).strip()
            if lead_in:
                remainder = remainder.lower().replace(lead_in, " ")
            words = [w for w in re.findall(r"[a-zA-Z']+", remainder)
                     if w.lower() not in _STOP]
            if len(words) <= MAX_NON_LIST_WORDS:
                return s
    return None


MICRO_PATTERNS = {
    "NameDropList": {
        "label": "Name-drop list",
        "confidence": 0.6,
        "description": "Enumeration of 3+ media/brand/outlet names with no statement "
                       "content — 'As featured in TechCrunch, Forbes, and Wired.' "
                       "The names ARE the sentence. FakeAuthoritySlop's list-shaped "
                       "cousin (G6, unslop #2).",
        "example_slop": "As featured in TechCrunch, Forbes, and Wired.",
        "example_fix": "TechCrunch covered the launch; the benchmark data is in the report.",
        "keep_when": "Reference lists, directories and citation sections (bullet/numbered "
                     "lines are skipped), and sentences whose verb makes a real claim "
                     "about the named things (compared/tested/interviewed/ranked…), "
                     "e.g. 'We compared React, Vue, and Angular in the benchmark.'",
    },
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
    "ActorlessClaim": {
        "label": "Actorless claim",
        "confidence": 0.6,
        "description": "Passive voice where the missing agent carries the claim "
                       "('mistakes were made', 'queries are validated', 'it was "
                       "decided that'). Name who did it.",
        "example_slop": "Mistakes were made and the release was delayed.",
        "example_fix": "The release team shipped the config too early; we rolled it back.",
        "keep_when": "The actor is genuinely unknown or irrelevant, or policy/legal "
                     "register where agentless obligation is intended (shall/must "
                     "clauses are skipped). Sentences naming an agent ('by the team') "
                     "are skipped.",
    },
}

_FINDERS = {
    "NameDropList": _name_drop_list,
    "FalseAgency": lambda text: _false_agency(_sentences(text)),
    "FalseRange": _false_range,
    "RecapEnding": _recap_ending,
    "HeadingRepeatedBelowItself": _heading_repeated,
    "ActorlessClaim": _actorless_claim,
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
