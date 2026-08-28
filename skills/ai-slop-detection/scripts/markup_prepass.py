#!/usr/bin/env python3
"""Markdown input pre-pass (issue #69).

The scorer matches occurrences, not speech-act roles. A document *about* slop
quotes slop: its signal tables, code fences and example lists fire the very
signals they document. Measured on this repository, that put README.md at
0.90 and docs/USER-GUIDE.md at 0.995 — the detector flagging its own
documentation, and every self-application (#48) uninterpretable.

`strip_markup(text)` removes the parts of a Markdown document that carry
quoted material rather than the author's own prose:

  - fenced code blocks (``` and ~~~, closed or not) and indented code blocks
  - inline code spans
  - blockquotes
  - tables
  - list items that are catalogue entries rather than sentences

What it deliberately keeps: ordinary prose lists, headings, emphasis, links
(the link text is prose), and everything in a document without markup. The
pre-pass must never become a way to launder slop — prose stays prose.

Boundaries: #23 is the content exemption applied during analysis; #28
(markup_anomalies) detects markup irregularities without removing anything.
This module only prepares input, it produces no findings and no score.

Opt-in: nothing calls it implicitly. `slop score --strip-markup` reports the
raw and the stripped score side by side, and the corpus baseline is measured
on raw text as before — switching the default would be a re-baseline
decision (docs/SCORE-GOVERNANCE.md), not a bug fix.
"""

import re

__all__ = ["strip_markup", "strip_stats"]

_FENCE_RE = re.compile(
    r"^[ \t]{0,3}(`{3,}|~{3,})[^\n]*\n"      # opening fence + info string
    r"(?:.*?\n)??"                            # body, lazily
    r"(?:[ \t]{0,3}\1[ \t]*(?:\n|$)|\Z)",     # matching close, or end of text
    re.MULTILINE | re.DOTALL,
)

# `code`, ``code with a backtick``
_INLINE_CODE_RE = re.compile(r"(`+)(?!`)(.+?)\1", re.DOTALL)

_BLOCKQUOTE_LINE_RE = re.compile(r"^[ \t]{0,3}>.*$", re.MULTILINE)

# A table row: starts and (after trailing spaces) ends with a pipe, or is a
# delimiter row. Requires at least two pipes so prose with one pipe survives.
_TABLE_LINE_RE = re.compile(
    r"^[ \t]{0,3}\|.*\|[ \t]*$|^[ \t]{0,3}\|?[ \t]*:?-{3,}:?[ \t]*(\|[ \t]*:?-+:?[ \t]*)+\|?[ \t]*$",
    re.MULTILINE,
)

# An indented code block: four spaces or a tab, and not a list continuation.
_INDENTED_CODE_RE = re.compile(r"^(?: {4}|\t)(?![ \t]*[-*+]\s).*$", re.MULTILINE)

_LIST_ITEM_RE = re.compile(r"^[ \t]{0,6}(?:[-*+]|\d+[.)])[ \t]+(.*)$")

# A table of contents is generated navigation, not authored prose — the same
# kind of furniture as a table. Removed together with the link list under it.
_TOC_LABELS = r"table of contents|contents|inhaltsverzeichnis|inhalt|übersicht"
_TOC_BLOCK_RE = re.compile(
    r"^[ \t]{0,3}#{1,6}[ \t]*(?:" + _TOC_LABELS + r")[ \t]*#*[ \t]*$"
    r"(?:\n(?![ \t]{0,3}#).*)*",           # everything until the next heading
    re.MULTILINE | re.IGNORECASE,
)

# A catalogue entry quotes a term rather than making a statement: it opens
# with a quoted or emphasised token, and any prose after it is a gloss.
_CATALOGUE_ENTRY_RE = re.compile(
    r"""^\s*(?:
          ["“'‘]                # "delve into"
        | \*{1,3}[^*]           # **delve into**
        | _{1,2}[^_]            # _delve into_
        | `                     # already stripped, but be explicit
    )""",
    re.VERBOSE,
)

# Sentence-shaped: ends in sentence punctuation and has a few words.
_SENTENCE_END_RE = re.compile(r"[.!?…][\"'”’)\]]*\s*$")


def _blank_out(match) -> str:
    """Replace a span with the newlines it contained, so line structure and
    paragraph boundaries survive — the structural metrics read them."""
    return "\n" * match.group(0).count("\n")


def _is_catalogue_item(body: str) -> bool:
    """True when a list item is a quoted example rather than a sentence."""
    body = body.strip()
    if not body:
        return False
    if _CATALOGUE_ENTRY_RE.match(body):
        return True
    # Short, unpunctuated fragments in a list are entries, not arguments.
    words = body.split()
    return len(words) <= 4 and not _SENTENCE_END_RE.search(body)


def _strip_catalogue_items(text: str) -> str:
    out = []
    for line in text.split("\n"):
        m = _LIST_ITEM_RE.match(line)
        if m and _is_catalogue_item(m.group(1)):
            out.append("")
        else:
            out.append(line)
    return "\n".join(out)


def strip_markup(text: str) -> str:
    """Markdown document -> the author's own prose.

    Idempotent: strip_markup(strip_markup(x)) == strip_markup(x).
    """
    if not text:
        return text
    out = _FENCE_RE.sub(_blank_out, text)
    out = _TOC_BLOCK_RE.sub(_blank_out, out)
    out = _INDENTED_CODE_RE.sub("", out)
    out = _INLINE_CODE_RE.sub(" ", out)
    out = _BLOCKQUOTE_LINE_RE.sub("", out)
    out = _TABLE_LINE_RE.sub("", out)
    out = _strip_catalogue_items(out)
    # Collapse the runs of blank lines the removals left behind, but keep
    # paragraph separation.
    out = re.sub(r"\n{3,}", "\n\n", out)
    return out


def strip_stats(text: str) -> dict:
    """How much the pre-pass removed — for reports that show both scores."""
    stripped = strip_markup(text)
    raw_chars = len(text)
    return {
        "raw_chars": raw_chars,
        "stripped_chars": len(stripped),
        "removed_chars": raw_chars - len(stripped),
        "removed_ratio": round((raw_chars - len(stripped)) / raw_chars, 4)
        if raw_chars else 0.0,
    }


if __name__ == "__main__":  # pragma: no cover - manual inspection
    import sys
    src = sys.stdin.read() if len(sys.argv) < 2 else open(
        sys.argv[1], encoding="utf-8").read()
    sys.stdout.write(strip_markup(src))
