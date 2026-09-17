#!/usr/bin/env python3
"""
Chat-paste artifacts & elision micro-signals (issue #113 / platform #1090).

Six deterministic detect-only signals for code/instruction/comment files that
betray pasted LLM chat output or silently elided content. Same interface and
schema as micro_patterns.py (issue #13); DETECT-ONLY — never scored, never
rewritten (ADR-0001 detector-only repo).

Signals (sources: mgiovani/stopslop SLOP001/002, scanaislop/aislop,
jv-k/desloper):

1. elision-comment         — "// ... rest of code unchanged" (silently
                             dropped code inside a comment marker)
2. chat-preamble           — "Certainly! Here's ..." assistant preamble
                             pasted into a file
3. fence-in-code           — stray Markdown fences inside source files
4. meta-process-comment    — comments narrating the generation process
                             ("phase 2", "agent behavior")
5. list-label-marker       — G1/NG2-style label markers glued to list items
6. placeholder-credential-shape — your-api-key / sk-XXXX / changeme shapes
                             as literal (non-placeholder-file) values

Public surface:
    find_chat_artifacts(text) -> [{id, confidence, evidence, keep_when}]
"""

import re

# ---------------------------------------------------------------------------
# Comment markers (line comments across common languages)
# ---------------------------------------------------------------------------
_LINE_COMMENT = r"(?:#|//|--|;|%)"

# 1. elision-comment: a *comment* claiming code was left unchanged/omitted.
_ELISION_COMMENT = [
    re.compile(
        r"(?im)^\s*" + _LINE_COMMENT + r".{0,80}\brest\s+of\s+the\s+"
        r"(?:code|implementation|file|logic|function|class)"
        r"(?:\s+\w+){0,4}\b(?:unchanged|the\s+same|as\s+before|stays)\b"),
    re.compile(
        r"(?im)^\s*" + _LINE_COMMENT + r".{0,80}\b(?:remaining|other)\s+"
        r"(?:code|methods?|functions?|logic)\b.{0,40}"
        r"\b(?:unchanged|omitted|elided|not\s+shown)\b"),
    re.compile(
        r"(?im)^\s*" + _LINE_COMMENT + r"\s*\.{3,}?\s*(?:rest|code|etc)"
        r"\b.{0,40}\b(?:unchanged|omitted|same)\b"),
]
# Prose elision without a comment marker is NOT this signal (keep_when), the
# regexes above require the marker at line start.

# 2. chat-preamble: assistant opener formulas pasted as the first non-empty
#    line of a file/response.
_PREAMBLE_OPENERS = [
    re.compile(r"(?i)^\s*certainly!\s"),
    re.compile(r"(?i)^\s*of\s+course!\s"),
    re.compile(r"(?i)^\s*great\s+question!\s"),
    re.compile(r"(?i)^\s*sure!\s+here'?s\b"),
    re.compile(r"(?i)^\s*here'?s\s+the\s+(?:updated|revised|complete|full)\b"),
    re.compile(r"(?i)^\s*i'?ve\s+(?:made|updated|fixed)\s+the\s+"
               r"(?:changes?|code|file)s?\s+as\s+(?:requested|discussed)\b"),
    re.compile(r"(?i)^\s*below\s+is\s+the\s+(?:updated|revised|complete)\b"),
]

# 3. fence-in-code: stray Markdown fences inside a source file.
#    Positive: a fence whose line does NOT start at column 0 or that sits
#    inside a comment/assignment (i.e. not a docstring example block opened
#    with \"\"\" ... ``` at line start).
_FENCE = re.compile(r"(?m)^(\s*)```")

# 4. meta-process-comment: comments narrating the generation process.
_META_PROCESS = [
    re.compile(r"(?im)^\s*" + _LINE_COMMENT +
               r".{0,60}\bphase\s+\d+\b.{0,60}\b(?:implementation|generation"
               r"|refactor|pass)\b"),
    re.compile(r"(?im)^\s*" + _LINE_COMMENT +
               r".{0,60}\b(?:agent|assistant|model|ai)\s+(?:behavior|response"
               r"|output|instructions?)\b"),
    re.compile(r"(?im)^\s*" + _LINE_COMMENT +
               r".{0,60}\b(?:as\s+(?:an|the)\s+(?:ai|assistant)|per\s+the\s+"
               r"(?:ai|assistant|prompt)|generated\s+by)\b"),
    # step-by-step narration inside comments (aislop `narrative-comment`):
    # "Step 2: now we add the handler" — narrative, not a structural label.
    re.compile(r"(?im)^\s*" + _LINE_COMMENT +
               r".{0,60}\b(?:now|next|then|first(?:ly)?),?\s+we\s+\w+"),
]

# 5. list-label-marker: G1/NG2-style marker glued to list items or headers
#    in prose documents (desloper). Marker directly at bullet/heading start.
_LIST_LABEL = re.compile(
    r"(?im)^(\s*(?:[-*+]\s+|#{1,6}\s+|\"?\())\s*"
    r"([A-Z]{1,3}\d{1,3}|G\d+|NG\d+)\s*[:.\)-]\s+\S")

# 6. placeholder-credential-shape: placeholder API-key/password shapes used
#    as literal values in assignments (stopslop). Env var *declarations* and
#    placeholder template files are keep_when.
_CRED_KEYS = r"(?:api[_-]?key|token|secret|password|passwd|pwd|access[_-]?key)"
_PLACEHOLDER_VALUES = (
    r"(?:your[_-][a-z-]+|your\s+[a-z-]+|"
    r"sk-[A-Za-z0-9]{3}[Xx]{3,}|"
    r"[Xx]{3,}|"
    r"changeme|change-me|\*{3,}(?![\w\]])|"
    r"<[^>\n]{3,40}key[^>\n]{0,20}>|"
    r"\{[^}\n]{0,20}(?:key|token|secret)[^}\n]{0,20}\})"
)
_CRED_PLACEHOLDER = re.compile(
    r"(?im)^\s*" + _CRED_KEYS + r"\s*[:=]\s*[\"']?" + _PLACEHOLDER_VALUES)
# require an assignment shape; bare prose "your api key" is not a hit.


def _first(lines_pred):
    """Return evidence string of the first matching line, else None."""
    for ev in lines_pred:
        return ev
    return None


def _find_elision_comment(text):
    for rx in _ELISION_COMMENT:
        m = rx.search(text)
        if m:
            return m.group(0).strip()
    return None


def _find_chat_preamble(text):
    first = next((ln for ln in text.splitlines() if ln.strip()), "")
    for rx in _PREAMBLE_OPENERS:
        if rx.match(first):
            return first.strip()
    return None


def _find_fence_in_code(text):
    """Stray fences: indented fences (not column 0, not inside a markdown
    list item — three-space indent is tolerated) are artifacts of pasted
    chat blocks. Top-level fences at column 0 are the normal markdown case
    and are ignored."""
    hits = []
    for m in _FENCE.finditer(text):
        indent = m.group(1)
        if indent and len(indent.expandtabs(4)) > 3:
            hits.append(m.group(0).strip())
    return hits[0] if hits else None


def _find_meta_process_comment(text):
    for rx in _META_PROCESS:
        m = rx.search(text)
        if m:
            return m.group(0).strip()
    return None


def _find_list_label_marker(text):
    m = _LIST_LABEL.search(text)
    if m:
        return m.group(0).strip()
    return None


def _find_placeholder_credential(text):
    m = _CRED_PLACEHOLDER.search(text)
    if m:
        return m.group(0).strip()
    return None


CHAT_ARTIFACTS = {
    "elision-comment": {
        "label": "Elision comment",
        "confidence": 0.8,
        "description": "A comment claims the rest of the code is 'unchanged' "
                       "or 'omitted' — code was silently dropped when the "
                       "answer was pasted (stopslop SLOP001).",
        "example_slop": "// ... rest of the code remains unchanged",
        "example_fix": "// (unchanged lines elided for review; full file in repo)",
  "keep_when": "Review/annotation contexts where the elision is explicitly "
                     "scoped and the full file exists elsewhere; prose "
                     "ellipsis without a code-comment marker is not this "
                     "signal.",
    },
    "chat-preamble": {
        "label": "Chat preamble",
        "confidence": 0.85,
        "description": "Assistant opener formula ('Certainly! ...', 'Here's "
                       "the updated ...') pasted as the first line of a file "
                       "(stopslop SLOP002).",
        "example_slop": "Certainly! Here's the refactored handler:",
        "example_fix": "(delete the preamble; the code starts at line 1)",
        "keep_when": "A transcript/corpus file that deliberately documents a "
                     "chat exchange (annotated as such); quoted prose in a "
                     "string that is the literal topic (a chatbot test "
                     "fixture).",
    },
    "fence-in-code": {
        "label": "Markdown fence inside code",
        "confidence": 0.7,
        "description": "An indented ``` fence inside a source file — residue "
                       "of a pasted chat block (stopslop).",
        "example_slop": "    ```\n    def run(): pass\n    ```",
        "example_fix": "(remove the fences; this is a .py file)",
        "keep_when": "Markdown files themselves; fenced examples inside "
                     "docstrings/comments where the fence line sits at "
                     "column 0 of the docstring body; nested code fences in "
                     "markdown (indented under a list item).",
    },
    "meta-process-comment": {
        "label": "Meta-process comment",
        "confidence": 0.7,
        "description": "Comment narrates the generation process ('phase 2', "
                       "'agent behavior', 'as an AI') instead of the code "
                       "(scanaislop meta-comment).",
        "example_slop": "# Phase 2: now we add the handler",
        "example_fix": "# Retry once on transient connection errors.",
        "keep_when": "Build-tooling phase labels that refer to the *pipeline* "
                     "(e.g. '# Phase 1 of the build: fetch deps') are about "
                     "the artifact, not the generation; the detector only "
                     "reports, a human judges intent.",
    },
    "list-label-marker": {
        "label": "List label marker",
        "confidence": 0.6,
        "description": "G1/NG2-style outline markers glued to list items or "
                       "headings in prose (desloper) — plan residue that "
                       "survived into the document.",
        "example_slop": "- G1: Introduce the product",
        "example_fix": "- Introduce the product",
        "keep_when": "Documents whose vocabulary *is* label-based (gap "
                     "analysis 'BS-I3', spec item IDs like 'A1: requirement "
                     "...') — the marker matches an established, consistent "
                     "numbering scheme used throughout the document.",
    },
    "placeholder-credential-shape": {
        "label": "Placeholder credential shape",
        "confidence": 0.75,
        "description": "A placeholder (your-api-key, sk-XXXX, changeme, "
                       "<your key>) assigned as the literal value of a "
                       "credential field (stopslop) — generated config slop.",
        "example_slop": 'API_KEY = "your-api-key"',
        "example_fix": 'API_KEY = os.environ["API_KEY"]  # set in .env',
        "keep_when": "Deliberate template files (config.example.yaml, "
                     ".env.template) whose entire purpose is placeholders, "
                     "and test fixtures that assert on the placeholder "
                     "shape.",
    },
}

_FINDERS = {
    "elision-comment": _find_elision_comment,
    "chat-preamble": _find_chat_preamble,
    "fence-in-code": _find_fence_in_code,
    "meta-process-comment": _find_meta_process_comment,
    "list-label-marker": _find_list_label_marker,
    "placeholder-credential-shape": _find_placeholder_credential,
}


def find_chat_artifacts(text: str) -> list:
    """Detect-only: returns [{id, confidence, evidence, keep_when}] — never scored."""
    out = []
    for pid, finder in _FINDERS.items():
        evidence = finder(text)
        if evidence:
            meta = CHAT_ARTIFACTS[pid]
            out.append({
                "id": pid,
                "confidence": meta["confidence"],
                "evidence": evidence,
                "keep_when": meta["keep_when"],
            })
    return out
