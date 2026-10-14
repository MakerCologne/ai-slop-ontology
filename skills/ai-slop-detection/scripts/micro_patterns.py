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
    return None


# --- Fallstudie #97: PuritySlop / Slopaganda (detect-only) ---------------
# Ritual anti-AI purity declarations (Bluesky "AI IS THEFT. PASS IT ON."
# chain letters) and identity-signalling bans. Willison-test: unverlangt,
#gedankenlos skaliert — oft ohne dass ein Modell den Text schrieb.
_PURITY_RITUAL = re.compile(
    r"\bai\s+is\s+theft\b"
    r"|\bpass\s+it\s+on\b"
    r"|\bblock\s+me\s+if\s+you\s+(?:use|support|like)\s+(?:any\s+)?ai\b"
    r"|\bif\s+you\s+use\s+ai,?\s+block\s+me\b"
    r"|\b(?:100%|one\s+hundred\s+percent)\s+(?:human[- ]written|human[- ]made)\b"
    r"|\bno\s+ai\s+was\s+(?:used|involved|harmed)\b"
    # DE (Fallstudie #97, Texte 3–4): Purity-Test ohne Argument
    r"|\bai[- ]?tools?\s+nutzt,?\s+hat\s+als\s+mensch\b"
    r"|\bai[- ]?avatar\s+hat,?\s+ist\s+blockiert\b"
    r"|\bnicht\s+verhandeln\b"
    # HIS: Teil-des-Problems-Ritual (Partizipation als Position, ohne Argument)
    r"|\bwer\s+[^.!?]{0,80}\bist\s+teil\s+des\s+problems\b"
    r"|\bkeine\s+unschuldigen\s+zuschauer\b"
    r"|\bschauen\s+ist\s+schon\s+position\b",
    re.IGNORECASE,
)
# keep_when: compliance/provenance disclosure — factual statements required by
# a policy, licence, watermark or evaluation, not identity signalling.
_PURITY_DISCLOSURE = re.compile(
    r"\b(?:watermark|watermarked|provenance|disclosure|pursuant|compliance|"
    r"licence|license|verified|certified|per\s+(?:the\s+)?(?:policy|contract|"
    r"requirement|guideline)|evaluation|benchmark)\b",
    re.IGNORECASE,
)

# VibeScapegoat: "vibe coding" invoked as blanket cause of a failure without
# naming any technical mechanism (Bluesky outage discourse, Ars Technica
# 2026-04).
_VIBE_CODING = re.compile(r"\bvibe[- ]?cod(?:e|ed|er|ing)\b", re.IGNORECASE)
_VIBE_FAILURE = re.compile(
    r"\b(?:outage|broke|broke\s+down|down|downtime|incident|failure|"
    r"crashed|went\s+down|meltdown|ausfall|st\u00f6rung)\b",
    re.IGNORECASE,
)
_VIBE_EVIDENCE_DENIAL = re.compile(
    r"\b(?:keine\s+(?:meldung|logs?|untersuchung|postmortem)|"
    r"man\s+braucht\s+keine\s+meldung|no\s+logs?\s+needed|"
    r"wir\s+wissen\s+alle|we\s+all\s+know|my\s+foot)\b",
    re.IGNORECASE,
)
_VIBE_TECHNICAL = re.compile(
    r"\b(?:commit|deploy|config|database|query|migration|log|cache|regex|"
    r"race\s+condition|index|schema|load\s+balancer|dns|certificate|"
    r"token|timeout|revert|rollback|hotfix)\b",
    re.IGNORECASE,
)

# SalvationModel: monetised AI melodrama arc — injustice -> humiliation ->
# redemption (WIRED 2026-07 schema) — signalled by stacked arc markers plus
# an AI/money noun in the redemption sentence.
_SALVATION_MARKERS = re.compile(
    r"\b(?:against\s+all\s+odds|humble\s+beginnings|no\s+one\s+believed|"
    r"laughed\s+(?:at|me\s+out)|rejected\s+by\s+everyone|slept\s+in\s+(?:a|my)\s+"
    r"car|lost\s+everything|down\s+to\s+(?:my|his|her)\s+last\s+\$?\d+|"
    r"tears\s+(?:of|streamed)|cried\s+(?:when|tears|for)|"
    r"(?:never|still\s+can(?:'t|\s+not))\s+(?:believe|imagined)|"
    r"(?:life|everything)\s+(?:is|was|has\s+been)\s+(?:changed|never\s+the\s+same)|"
    r"forever\s+grateful|best\s+decision\s+(?:i|we|he|she)\s+ever\s+made)\b",
    re.IGNORECASE,
)
_SALVATION_AI_MONEY = re.compile(
    r"\b(?:ai|a\.i\.|chatgpt|gpt-?\d|grok|claude|gemini|midjourney|"
    r"automation|bot)\b|\$\s?\d",
    re.IGNORECASE,
)

# SLOPAGANDA_RITUAL (#97, Texte 5–8): unambiguous identity-regime phrases
# (Erlöser-Schema, Lösch-Mobilisierung, Lügenpresse-Frame, Loyalitätstest).
# Single marker fires — these are closed rituals, not ordinary rhetoric.
_SLOPAGANDA_RITUAL = re.compile(
    r"\bonly\s+\w+\s+can\s+save\b[^.!?]*\beveryone\s+else\b"
    r"|\bteilt\s+(?:es|das),?\s+bevor\s+es\s+gelöscht\s+wird\b"
    r"|\blügenpresse\b"
    r"|\bliken\s*(?:=|ist)\s*loyalitäts?\b"
    r"|\bwer\s+nicht\s+liked\b"
    # HIS: Erloeser-Schema DE / Einheits-Pathos
    r"|\bnur\s+noch\s+\w+\s+kann\s+[^.!?]*\bretten\b"
    r"|\balle\s+anderen\s+sind\s+teil\s+des\s+problems\b"
    r"|\beine\s+bewegung,?\s+ein\s+wille\b",
    re.IGNORECASE,
)


def _purity_ban(text: str):
    for s in _sentences(text):
        m = _PURITY_RITUAL.search(s)
        if m and not _PURITY_DISCLOSURE.search(s):
            return s
    return None


def _vibe_scapegoat(text: str):
    sentences = _sentences(text)
    for i, s in enumerate(sentences):
        if _VIBE_CODING.search(s) and _VIBE_FAILURE.search(s):
            # keep_when: a post-mortem that names the actual mechanism is
            # technical writing, not scapegoating.
            if _VIBE_TECHNICAL.search(s):
                continue
            return s
        # adjacency: failure claim and 'vibe coding' blame split across a
        # question/answer pair ("Service down again? Vibe-coded devs…")
        prev = sentences[i - 1] if i > 0 else ""
        if (_VIBE_CODING.search(s) and _VIBE_FAILURE.search(prev)
                and not _VIBE_TECHNICAL.search(s)):
            return f"{prev} {s}".strip()
        # blame-without-evidence: failure + dismissal of any investigation
        # (HIS-052/53) — scapegoating without the buzzword
        if (_VIBE_FAILURE.search(s) and _VIBE_EVIDENCE_DENIAL.search(s)
                and not _VIBE_TECHNICAL.search(s)):
            return s
        if (_VIBE_FAILURE.search(prev) and _VIBE_EVIDENCE_DENIAL.search(s)
                and not _VIBE_TECHNICAL.search(s)):
            return f"{prev} {s}".strip()
    return None


def _salvation_model(text: str):
    for s in _sentences(text):
        if _SLOPAGANDA_RITUAL.search(s):
            return s
    markers = _SALVATION_MARKERS.findall(text)
    if len(set(m.lower() for m in markers)) < 2:
        return None
    for s in _sentences(text):
        if _SALVATION_MARKERS.search(s) and _SALVATION_AI_MONEY.search(s):
            return s
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
    "PurityBan": {
        "label": "Ritual AI-purity declaration",
        "confidence": 0.55,
        "description": "Identity-signalling anti-AI ritual phrases ('AI IS THEFT. "
                       "PASS IT ON.', 'block me if you use AI', '100% human-made') "
                       "scaled mindlessly, often without any model writing the text. "
                       "Human slop: the frame is human, the mass is synthetic.",
        "example_slop": "AI IS THEFT. PASS IT ON. Block me if you use it.",
        "example_fix": "I don't want my posts used for training without my "
                       "consent; my complaint is scraping and licensing, not identity.",
        "keep_when": "Compliance or provenance disclosures required by policy, "
                     "licence or watermark rules ('this report is watermarked per "
                     "contract requirements') — sentences with disclosure/"
                     "provenance/compliance vocabulary are skipped.",
    },
    "VibeScapegoat": {
        "label": "'Vibe coding' blamed without mechanism",
        "confidence": 0.55,
        "description": "'Vibe coding' invoked as a blanket cause of an outage or "
                       "failure while naming no technical mechanism — a scapegoat "
                       "frame instead of a post-mortem.",
        "example_slop": "The site went down because they were vibe coding, plain "
                        "and simple.",
        "example_fix": "The site went down after an unreviewed config change; the "
                        "migration lacked a rollback plan.",
        "keep_when": "Post-mortems or reviews that name a concrete mechanism "
                     "(commit, deploy, database, migration, rollback…). Those "
                     "sentences are skipped by the technical-token guard.",
    },
    "SalvationModel": {
        "label": "AI salvation melodrama arc",
        "confidence": 0.6,
        "description": "Monetised AI melodrama following the arc injustice -> "
                       "humiliation -> redemption ('lost everything… now $12k a "
                       "month') — stacked arc markers plus an AI/money payoff.",
        "example_slop": "I lost everything and no one believed in me. Today the "
                        "AI bot earns me $40,000 a month and I still can't believe "
                        "it.",
        "example_fix": "I was broke in 2024. After eight months of building a "
                        "support-ticket automation, it now covers my rent; the "
                        "revenue table with numbers is below.",
        "keep_when": "Genuine personal narratives with verifiable, concrete "
                        "details (numbers, timelines, named methods) — the detector "
                        "only reports the stacked arc markers for a human to judge.",
    },
}

_FINDERS = {
    "FalseAgency": lambda text: _false_agency(_sentences(text)),
    "FalseRange": _false_range,
    "RecapEnding": _recap_ending,
    "HeadingRepeatedBelowItself": _heading_repeated,
    "ActorlessClaim": _actorless_claim,
    "PurityBan": _purity_ban,
    "VibeScapegoat": _vibe_scapegoat,
    "SalvationModel": _salvation_model,
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
