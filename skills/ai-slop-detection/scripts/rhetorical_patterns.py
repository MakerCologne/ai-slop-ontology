#!/usr/bin/env python3
"""
Rhetorical / structural slop patterns (detect-only).

These are sentence- and paragraph-level *shapes* that mark AI-assisted prose,
independent of any individual buzzword. Unlike the buzzword and phrase lists in
slop_scorer, a match here is a named pattern with a quoted line of evidence — it
is NOT folded into the numeric slop score. Named patterns are evidence a human
can check; a score is a guess. Detection stays deliberately conservative and
every pattern carries a `keep_when` note so genuine human voice is not flagged.

Pattern set adapted from the "No AI slop" editing skill by Peter Yang
(github.com/petergyang/no-ai-slop, MIT). The concepts are re-expressed here as
ontology-aligned detectors with original regexes and examples.

Public surface:
    RHETORICAL_PATTERNS      # id -> metadata (mirrored in ontology.json)
    find_rhetorical_patterns(text) -> list[dict]  # {id, confidence, evidence, fix}
"""

import re
import unicodedata


# --- Pattern metadata (mirrors ontology.json signals.text.rhetoricalPatterns) ---

RHETORICAL_PATTERNS = {
    "BinaryContrast": {
        "label": "Binary contrast",
        "confidence": 0.7,
        "description": "\"It's not X. It's Y.\" / \"not just X but Y\" / \"the question "
                       "isn't X, it's Y.\" State Y directly.",
        "example_slop": "The question isn't the model. It's the eval.",
        "example_fix": "The eval matters more than the model.",
        "keep_when": "A genuine correction of a specific misconception, not a rhetorical flourish.",
    },
    "ColonReveal": {
        "label": "Colon reveal",
        "confidence": 0.55,
        "description": "A short capitalized phrase, a colon, then a lowercase dramatic "
                       "reveal. Rewrite as a plain sentence.",
        "example_slop": "The best part: it learns.",
        "example_fix": "It learns, which is the best part.",
        "keep_when": "The colon introduces a list, label, quote, ratio, or code.",
    },
    "SuperficialAnalysis": {
        "label": "Superficial analysis",
        "confidence": 0.7,
        "description": "Trailing '-ing' clause that pretends to explain meaning "
                       "(highlighting, underscoring, reflecting, showcasing).",
        "example_slop": "The launch adds file search, highlighting the team's commitment to workflows.",
        "example_fix": "The launch adds file search, so users find old drafts without leaving the editor.",
        "keep_when": "The clause states a concrete consequence, not a vague virtue.",
    },
    "NegativeListingFragmentation": {
        "label": "Negative listing & dramatic fragmentation",
        "confidence": 0.65,
        "description": "\"Not a X. Not a Y. A Z.\" or \"That's it. That's the whole thing.\" "
                       "or stacked \"X. And Y. And Z.\" Use complete sentences and say Z.",
        "example_slop": "Not a feature. Not a tool. A movement.",
        "example_fix": "It's a movement.",
        "keep_when": "Deliberate, sparing emphasis that fits the writer's spoken rhythm.",
    },
    "FakeStrongVerb": {
        "label": "Fake-strong verb",
        "confidence": 0.6,
        "description": "\"serves as / acts as / functions as a centralized hub/platform/"
                       "solution.\" Prefer a plain verb, 'is', or 'has'.",
        "example_slop": "The app serves as a centralized hub for sponsor management.",
        "example_fix": "The app tracks sponsors, drafts, due dates, and approvals in one place.",
        "keep_when": "'serves as' names a literal role and no plainer verb fits.",
    },
    "SynonymCycling": {
        "label": "Synonym cycling",
        "confidence": 0.6,
        "description": "Rotating near-synonyms for one referent across adjacent sentences "
                       "(the agent, then the assistant, then the tool). If the clear word "
                       "is right, repeat it.",
        "example_slop": "The agent reviews the draft. The assistant scores it. The tool suggests fixes.",
        "example_fix": "The agent reviews the draft, scores it, and suggests fixes.",
        "keep_when": "The different words genuinely refer to different things.",
        "synonym_groups": [
            ["agent", "assistant", "tool", "bot", "model", "system", "copilot"],
            ["app", "platform", "tool", "product", "service", "solution", "software"],
            ["company", "firm", "startup", "team", "organization", "organisation"],
            ["article", "piece", "post", "essay", "write-up", "writeup"],
        ],
    },
    "HollowKickerRecap": {
        "label": "Fake-profound kicker & summary-recap ending",
        "confidence": 0.6,
        "description": "A final 'deep' one-liner (aphorism/mic-drop) or a recap paragraph "
                       "('In conclusion', 'Ultimately', 'Overall'). End on the last concrete "
                       "point, takeaway, or next action instead.",
        "example_slop": "In conclusion, AI is changing everything, and we must adapt.",
        "example_fix": "(end on the last concrete point already in the draft)",
        "keep_when": "A genuine call to action or concrete next step, not a restatement.",
        "recap_openers": [
            "in conclusion", "ultimately", "overall", "to sum up", "in summary",
            "all in all", "at the end of the day", "when all is said and done",
            "in the end", "to wrap up", "to conclude",
        ],
        "kicker_openers": [
            "and that's", "and maybe that's", "because in the end", "that's the real",
            "and in the end", "that, ultimately, is", "and that is the",
        ],
    },
    "FormattingSlop": {
        "label": "Formatting slop",
        "confidence": 0.55,
        "description": "Emoji in headings, bold sprinkled mid-sentence for emphasis, and "
                       "em-dash clusters. Format should follow content, not decorate it.",
        "example_slop": "## \U0001F680 Key Takeaways",
        "example_fix": "## Key takeaways",
        "keep_when": "Emoji or bold is the platform's native style (e.g. a release changelog).",
    },
    "RoboticRhythm": {
        "label": "Robotic rhythm",
        "confidence": 0.5,
        "description": "Stacked punchy fragments and repeated sentence shapes — three or "
                       "more very short sentences in a row. Vary shape only when it helps.",
        "example_slop": "It works. It scales. It ships. Every time.",
        "example_fix": "It works, scales, and ships every time.",
        "keep_when": "A short burst used once, deliberately, for genuine emphasis.",
    },
    # --- Wikipedia "Signs of AI writing" additions (issue #7) ---
    "ThroatClearing": {
        "label": "Throat-clearing opener",
        "confidence": 0.6,
        "description": 'The text opens with a padded framing sentence ("In today\'s '
                       '"world...", "Look, ...", "Let\'s be honest: ...") before any concrete '
                       '"content. Start with the point.',
        "example_slop": "In today's world, effective team communication matters more than ever.",
        "example_fix": "We cut meeting time by a third last quarter.",
        "keep_when": "The opener names the specific stake or audience of what follows.",
        "openers": [
            "in today's world", "in today's day and age", "in this day and age",
            "in an era where", "in an age where", "in a world where",
            "we live in a world", "look,", "so,", "let's be honest",
            "let's face it", "here's the truth", "it goes without saying",
            "needless to say", "in our modern world",
        ],
    },
    "FauxInsightSetup": {
        "label": "Faux-insight setup",
        "confidence": 0.65,
        "description": 'A teaser that promises hidden knowledge ("Here\'s the thing nobody '
                       '"tells you...", "What most people get wrong about...") instead of '
                       '"stating the claim. State the claim, then support it.',
        "example_slop": "Here's the thing nobody tells you about remote work.",
        "example_fix": "Remote work has tradeoffs; our team measured both sides over two years.",
        "keep_when": "The hidden knowledge is genuinely non-obvious and the text delivers it immediately.",
        "setups": [
            "here's the thing nobody tells you", "nobody tells you",
            "what most people get wrong", "most people think",
            "the secret to", "the truth about", "a little-known fact",
            "nobody talks about", "what they don't tell you",
        ],
    },
    "ImportancePuffery": {
        "label": "Importance puffery",
        "confidence": 0.6,
        "description": 'Empty significance markers ("a testament to", "pivotal moment", "more '
                       '"important than ever") that assert importance instead of showing it.',
        "example_slop": "The launch is a pivotal moment for the industry.",
        "example_fix": "The API v2 launch cut customer latency by half within a week.",
        "keep_when": "A measurable historical claim (growth numbers, dates) backs the importance.",
        "markers": [
            "a testament to", "testament to", "pivotal moment", "watershed moment",
            "more important than ever", "more relevant than ever", "unprecedented",
            "ever-evolving landscape", "ever-changing landscape",
        ],
    },
    "ForcedTriad": {
        "label": "Forced triad",
        "confidence": 0.55,
        "description": 'A slogan-shaped "X, Y, and Z" list of three parallel adjectives '
                       '"(fast, reliable, and scalable)" where a triad is forced for '
                       '"rhythm, not content.',
        "example_slop": "The dashboard is fast, reliable, and scalable.",
        "example_fix": "The dashboard answers the 95th-percentile query in 80 ms.",
        "keep_when": "Three genuinely distinct, individually meaningful items — not one claim stretched to three.",
    },
    "RepeatedOpenings": {
        "label": "Repeated sentence openings",
        "confidence": 0.55,
        "description": 'Three or more sentences open with the same word ("The team... The '
                       '"team... The team..."). Vary the subjects.',
        "example_slop": "The team shipped the billing page. The team then rewrote the search. The team also fixed login.",
        "example_fix": "The team shipped the billing page, then rewrote search, then fixed login.",
        "keep_when": "Deliberate anaphora that fits the writer's rhythm, used sparingly.",
    },
    "ChatbotLeftover": {
        "label": "Chatbot leftovers",
        "confidence": 0.8,
        "description": 'Assistant-register phrases pasted into prose ("I hope this helps", "Great '
                       '"question!", "Happy to help"). Remove them; they are not content.',
        "example_slop": "The config option is documented in the README. I hope this helps!",
        "example_fix": "The config option is documented in the README.",
        "keep_when": "An actual chat transcript, not running prose.",
        "phrases": [
            "i hope this helps", "great question", "happy to help",
            "as an ai", "i'm just an ai", "you're absolutely right",
            "that's a great point", "as of my last update",
            "let me know if you have any questions",
        ],
    },
}


# --- Compiled regexes for the regex-detectable patterns ---

_BINARY_CONTRAST = [
    re.compile(r"\b(?:it'?s|it is|this is|that'?s|they'?re)\s+not\s+[^.?!]{2,60}?[.,]\s+"
               r"(?:it'?s|it is|they'?re)\b", re.IGNORECASE),
    re.compile(r"\bnot\s+just\s+[^.?!,]{2,50}?\s+but\s+(?:also\s+)?\w", re.IGNORECASE),
    re.compile(r"\bthe\s+(?:question|point|problem|issue|goal)\s+(?:isn'?t|is not|wasn'?t)\b"
               r"[^.?!]{2,60}?[.,]?\s+it'?s\b", re.IGNORECASE),
    # Issue #26 — remaining variants from deep/01 §2.5 (structures.md):
    # "X isn't just Y — it's Z" (em-dash or hyphen separator)
    re.compile(r"\b\w+\s+isn'?t\s+just\s+[^.?!]{2,60}?\s+[—–-]\s*it'?s\b",
               re.IGNORECASE),
    # "No longer X, now Y"
    re.compile(r"\bno\s+longer\s+[^.?!]{2,60}?,\s+now\b", re.IGNORECASE),
    # "Gone are the days of X, replaced by Y"
    re.compile(r"\bgone\s+are\s+the\s+days\s+(?:of\s+)?[^.?!]{2,60}?\s+replaced\s+by\b",
               re.IGNORECASE),
]

# Short Capitalized phrase, colon, lowercase reveal that is not a list (no comma).
_COLON_REVEAL = re.compile(
    r"(?:^|[.!?]\s+)([A-Z][a-z]+(?:\s+[\w'’-]+){0,5}):\s+([a-z][^,:\n]{3,60})(?=[.!?]|$)",
    re.MULTILINE,
)
# Single-word labels that legitimately precede a colon (not a dramatic reveal).
_COLON_LABELS = {
    "note", "notes", "warning", "caution", "tip", "tips", "example", "summary",
    "todo", "fixme", "update", "edit", "caveat", "disclaimer", "source", "sources",
    "author", "version", "abstract", "aside", "reminder", "important", "hint",
    "definition", "goal", "problem", "solution", "input", "output", "usage",
}

_SUPERFICIAL = re.compile(
    r",\s+(highlighting|underscoring|reflecting|showcasing|emphasizing|emphasising|"
    r"demonstrating|illustrating|signaling|signalling|marking|cementing|solidifying|"
    r"reinforcing|underlining|showing|proving)\s+[^.?!]{3,}", re.IGNORECASE,
)

_NEGATIVE_LISTING = [
    re.compile(r"\bnot\s+(?:a|an|the)?\s*\w+[.,]\s+not\s+(?:a|an|the)?\s*\w+", re.IGNORECASE),
    re.compile(r"\bthat'?s\s+it\b[.!]\s+that'?s\s+(?:the\s+)?\w+", re.IGNORECASE),
    re.compile(r"[.!?]\s+and\s+\w+[^.?!]{0,30}?[.!]\s+and\s+\w+", re.IGNORECASE),
]

_FAKE_STRONG_VERB = re.compile(
    r"\b(?:serves?|acts?|functions?|stands?)\s+as\s+(?:a|an|the)\s+"
    r"(?:centralized\s+|centralised\s+|one-stop\s+|comprehensive\s+|powerful\s+|robust\s+|"
    r"go-to\s+|single\s+|unified\s+)?"
    r"(?:hub|platform|solution|resource|cornerstone|gateway|bridge|catalyst|backbone|"
    r"foundation|framework|ecosystem|destination|powerhouse)\b", re.IGNORECASE,
)

_MID_SENTENCE_BOLD = re.compile(r"[a-z0-9,;]\s+\*\*[^*\n]{1,40}\*\*\s+[a-z]")

# Forced-triad suffix classes: two or more of the three items must share one.
_TRIAD_SUFFIXES = (
    "able", "ible", "ful", "less", "ous", "ive", "ing", "ed", "al", "ic", "ly", "y",
)

_CHATBOT_PHRASES = None  # filled from RHETORICAL_PATTERNS["ChatbotLeftover"]["phrases"]

# Words that stay lowercase in a normal sentence-case heading, so they do
# not count toward the title-case ratio.
_HEADING_STOPWORDS = {
    "a", "an", "and", "as", "at", "but", "by", "for", "from", "in", "nor",
    "of", "on", "or", "per", "the", "to", "via", "with", "without",
}
_HEADING = re.compile(r"(?m)^#{1,6}\s+(.+)$")
_EMPHASIS_BOLD_HEADING = None  # headings handled separately


def _has_emoji(s: str) -> bool:
    for ch in s:
        if ch in ("’", "‘", "—", "–"):
            continue
        code = ord(ch)
        if 0x1F000 <= code <= 0x1FAFF or 0x2600 <= code <= 0x27BF or code in (0x2705, 0x274C):
            return True
        if unicodedata.category(ch) == "So":
            return True
    return False


def _sentences(text: str):
    return [s.strip() for s in re.split(r"(?<=[.!?])\s+", text.strip()) if s.strip()]


def _snippet(text: str, start: int, end: int, width: int = 90) -> str:
    frag = text[start:end].strip()
    frag = re.sub(r"\s+", " ", frag)
    return frag[:width]


def find_rhetorical_patterns(text: str):
    """Return a list of {id, label, confidence, evidence, fix} for every rhetorical
    slop pattern found. Detect-only: does not compute or alter a slop score."""
    findings = []

    def add(pattern_id, evidence):
        meta = RHETORICAL_PATTERNS[pattern_id]
        findings.append({
            "id": pattern_id,
            "label": meta["label"],
            "confidence": meta["confidence"],
            "evidence": evidence,
            "fix": meta["example_fix"],
        })

    # 1. Binary contrast
    for rx in _BINARY_CONTRAST:
        m = rx.search(text)
        if m:
            add("BinaryContrast", _snippet(text, *m.span()))
            break

    # 2. Colon reveal
    for m in _COLON_REVEAL.finditer(text):
        lead, reveal = m.group(1), m.group(2)
        # Skip single-word labels (Note:, Warning:, Summary:, ...) — legitimate
        # labels, not dramatic reveals.
        if lead.lower() in _COLON_LABELS:
            continue
        add("ColonReveal", f"{lead}: {reveal.strip()}")
        break

    # 3. Superficial analysis
    m = _SUPERFICIAL.search(text)
    if m:
        add("SuperficialAnalysis", _snippet(text, *m.span()))

    # 4. Negative listing / dramatic fragmentation
    for rx in _NEGATIVE_LISTING:
        m = rx.search(text)
        if m:
            add("NegativeListingFragmentation", _snippet(text, *m.span()))
            break

    # 5. Fake-strong verb
    m = _FAKE_STRONG_VERB.search(text)
    if m:
        add("FakeStrongVerb", _snippet(text, *m.span()))

    # 6. Synonym cycling — two+ distinct members of one synonym group used as
    #    "the <noun>" sentence subjects within the text.
    lowered = text.lower()
    for group in RHETORICAL_PATTERNS["SynonymCycling"]["synonym_groups"]:
        hits = [w for w in group if re.search(r"\bthe\s+" + re.escape(w) + r"\b", lowered)]
        if len(set(hits)) >= 2:
            add("SynonymCycling", "cycles between: " + ", ".join(f"the {h}" for h in hits))
            break

    # 7. Hollow kicker / recap ending — inspect the final paragraph and sentence.
    paras = [p.strip() for p in re.split(r"\n\s*\n", text.strip()) if p.strip()]
    if paras:
        last_para = paras[-1].lower()
        meta = RHETORICAL_PATTERNS["HollowKickerRecap"]
        if any(last_para.startswith(op) for op in meta["recap_openers"]):
            add("HollowKickerRecap", "recap ending: " + _snippet(paras[-1], 0, 80))
        else:
            sents = _sentences(paras[-1])
            if sents:
                last = sents[-1].lower()
                if any(last.startswith(op) for op in meta["kicker_openers"]) and len(last.split()) <= 14:
                    add("HollowKickerRecap", "kicker line: " + _snippet(sents[-1], 0, 80))

    # 8. Formatting slop — emoji heading, mid-sentence bold, em-dash
    #    doctrine (issue #16: none in short copy, 1-2 in long drafts, never
    #    clusters), title-case heading rate, curly double quotes, and
    #    hyphenated-pair rate.
    formatting_evidence = None
    for m in _HEADING.finditer(text):
        if _has_emoji(m.group(1)):
            formatting_evidence = "emoji in heading: " + _snippet(m.group(1), 0, 60)
            break
    if not formatting_evidence and _MID_SENTENCE_BOLD.search(text):
        formatting_evidence = "decorative bold mid-sentence"
    if not formatting_evidence:
        # Title-case headings: >= 2 headings where most non-stopword words
        # after the first are capitalized (sentence case is the human norm).
        title_case = 0
        headings = 0
        for m in _HEADING.finditer(text):
            words = m.group(1).split()
            headings += 1
            if len(words) >= 2:
                rest = words[1:]
                major = [w for w in rest if w.lower() not in _HEADING_STOPWORDS]
                if major and sum(1 for w in major if w[:1].isupper()) / len(major) >= 0.7:
                    title_case += 1
        if title_case >= 2:
            formatting_evidence = f"title-case headings: {title_case} of {headings}"
    if not formatting_evidence:
        # Curly double quotes in plain prose (straight quotes are the default
        # in raw text; curly quotes are a typeset/AI tell).
        if '\u201c' in text or '\u201d' in text:
            formatting_evidence = "curly double quotes in plain text"
    if not formatting_evidence:
        # Hyphenated compound modifiers: >= 2 distinct lowercase pairs like
        # "cross-functional, data-driven" (a single one is normal usage).
        pairs = set(re.findall(r"(?<![\w-])([a-z]+-[a-z]+)(?![\w-])", text))
        if len(pairs) >= 2:
            formatting_evidence = "hyphenated-pair modifiers: " + ", ".join(sorted(pairs)[:4])
    if not formatting_evidence:
        em = text.count("\u2014") + text.count("\u2013")
        word_count = len(text.split())
        sent_count = max(len(_sentences(text)), 1)
        if em >= 1 and word_count <= 120:
            formatting_evidence = f"em dash in short copy: {em} in {word_count} words"
        elif em >= 3 and em / sent_count > 0.5:
            formatting_evidence = f"em-dash cluster: {em} dashes in {sent_count} sentences"
        elif em > 2 and word_count > 120:
            formatting_evidence = f"em dashes beyond long-draft allowance: {em} in {word_count} words"
    if formatting_evidence:
        add("FormattingSlop", formatting_evidence)

    # 9. Robotic rhythm — 3+ consecutive short (<= 5 word) sentences.
    sents = _sentences(text)
    run = 0
    for s in sents:
        if len(s.split()) <= 5:
            run += 1
            if run >= 3:
                add("RoboticRhythm", "3+ stacked short sentences")
                break
        else:
            run = 0

    # 10. Throat clearing — a padded opener at the very start of the text.
    first_para = re.split(r"\n\s*\n", text.strip(), maxsplit=1)[0].lstrip().lower()
    meta = RHETORICAL_PATTERNS["ThroatClearing"]
    if any(first_para.startswith(op) for op in meta["openers"]):
        add("ThroatClearing", "opening: " + _snippet(first_para, 0, 80))

    # 11. Faux-insight setup — teaser promising hidden knowledge.
    meta = RHETORICAL_PATTERNS["FauxInsightSetup"]
    for setup in meta["setups"]:
        idx = lowered.find(setup)
        if idx >= 0:
            add("FauxInsightSetup", _snippet(lowered, idx, idx + 80))
            break

    # 12. Importance puffery — empty significance markers.
    meta = RHETORICAL_PATTERNS["ImportancePuffery"]
    for marker in meta["markers"]:
        idx = lowered.find(marker)
        if idx >= 0:
            add("ImportancePuffery", _snippet(lowered, idx, idx + 80))
            break

    # 13. Forced triad — "X, Y, and Z" of one-word adjectives where at
    #     least two items share a suffix class; digits or colons before the
    #     list mark concrete content, not a slogan.
    for m in re.finditer(r"\b([a-z]+),\s+([a-z]+),\s+and\s+([a-z]+)\b", lowered):
        items = (m.group(1), m.group(2), m.group(3))
        if len(set(items)) < 3:
            continue
        prefix = lowered[max(0, m.start() - 30):m.start()]
        if ":" in prefix or re.search(r"\d", prefix):
            continue
        suffix_hits = [
            sum(1 for it in items if it.endswith(sfx)) for sfx in _TRIAD_SUFFIXES
        ]
        if max(suffix_hits, default=0) >= 2:
            add("ForcedTriad", "" + ", ".join(items))
            break

    # 14. Repeated sentence openings — 3+ sentences starting with the same word.
    opener_counts = {}
    for s in sents:
        words_in = s.split()
        if words_in:
            opener_counts.setdefault(words_in[0].lower(), []).append(words_in[0])
    for opener, occurrences in opener_counts.items():
        if len(occurrences) >= 3:
            add("RepeatedOpenings", f"{len(occurrences)} sentences start with '{opener}'")
            break

    # 15. Chatbot leftovers — assistant-register phrases in running prose.
    for phrase in RHETORICAL_PATTERNS["ChatbotLeftover"]["phrases"]:
        idx = lowered.find(phrase)
        if idx >= 0:
            add("ChatbotLeftover", _snippet(lowered, idx, idx + 80))
            break

    return findings


def format_findings(findings) -> str:
    if not findings:
        return "No rhetorical slop patterns detected."
    lines = [f"Rhetorical patterns ({len(findings)}):"]
    for f in findings:
        lines.append(f"  • {f['label']} ({f['confidence']:.0%}) — \"{f['evidence']}\"  → {f['fix']}")
    return "\n".join(lines)


if __name__ == "__main__":
    import sys
    text = sys.stdin.read() if len(sys.argv) < 2 or sys.argv[1] == "-" else " ".join(sys.argv[1:])
    print(format_findings(find_rhetorical_patterns(text)))
