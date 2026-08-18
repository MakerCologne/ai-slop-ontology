"""Strip quoted material from Markdown before scoring.

A document *about* slop quotes slop: the ontology's own README, user guide and
research reports scored 0.90–0.99 because their tables, code fences and example
lists are full of the marker phrases the detector looks for (review 2026-08
§2.4). The same applies to style guides, moderation policies and teaching
material — the general case of "this text mentions the pattern rather than
committing it".

`strip_quoted` removes the parts of a Markdown document that quote rather than
assert: fenced code blocks, blockquotes, table rows, inline code spans, and
emphasised or quoted enumerations of example terms. Removed lines become empty
lines so sentence and paragraph boundaries — which the burstiness and structure
signals depend on — stay intact.
"""

import re

_FENCE = re.compile(r"^\s{0,3}(`{3,}|~{3,})")
_BLOCKQUOTE = re.compile(r"^\s{0,3}>")
_TABLE_ROW = re.compile(r"^\s{0,3}\|")
_INLINE_CODE = re.compile(r"`[^`\n]+`")

# Prose cites marker words as emphasised or quoted enumerations:
#   *delve, realm, tapestry, landscape, unleash, unlock, ...*
#   "in today's rapidly evolving", "it's worth noting that"
# A span with at least two commas is a list of examples, not an assertion.
# Emphasis without commas is left alone — heavy bold/italic is itself a slop
# signal (formatting slop) and must stay visible.
_QUOTE_PAIRS = [
    (r"\*\*", r"\*\*"), (r"\*", r"\*"), (r"_", r"_"),
    (r"“", r"”"), (r"„", r"“"), (r'"', r'"'),
]
_ENUMERATION = re.compile(
    "|".join(f"(?:{o}[^\\n]{{10,}}?{c})" for o, c in _QUOTE_PAIRS))


def _drop_enumerations(line: str) -> str:
    def repl(m):
        span = m.group(0)
        return " " if span.count(",") >= 2 else span
    return _ENUMERATION.sub(repl, line)


def strip_quoted(text: str) -> str:
    """Return `text` with quoted material removed."""
    out = []
    fence = None
    for line in text.splitlines():
        if fence:
            out.append("")
            if line.strip().startswith(fence):
                fence = None
            continue
        m = _FENCE.match(line)
        if m:
            fence = m.group(1)[0] * 3
            out.append("")
            continue
        if _BLOCKQUOTE.match(line) or _TABLE_ROW.match(line):
            out.append("")
            continue
        out.append(_drop_enumerations(_INLINE_CODE.sub(" ", line)))
    return "\n".join(out)


def looks_like_markdown(path) -> bool:
    return str(path).lower().endswith((".md", ".markdown", ".mdx"))
