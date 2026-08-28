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
  - a table-of-contents heading and the navigation list under it
  - list items that are catalogue entries rather than sentences

What it deliberately keeps: ordinary prose lists and their indented
continuations, headings, emphasis, links (the link text is prose), and
everything in a document without markup. The pre-pass must never become a way
to launder slop — prose stays prose. Where a construct is ambiguous the
tie-break is to keep the text: a false keep costs a score point, a false
removal hides the passage that should have been scored.

Implementation note. This is one line-wise scan, not a chain of regex
substitutions over the whole document. Chained passes make context-sensitive
decisions unstable: blanking a table row turns the line after it into
"preceded by a blank line", so a second pass classifies it differently and
`strip_markup` stops being idempotent. The scan therefore carries the context
it needs — whether the last *kept* non-blank line was a list item, and whether
anything separates it from the current line.

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

_FENCE_OPEN_RE = re.compile(r"^[ \t]{0,3}(`{3,}|~{3,})")

# `code`, ``code with a backtick``. Deliberately bounded to a single line and
# NOT re.DOTALL: an unbalanced backtick in prose would otherwise swallow every
# word up to the next one — which in a document about slop deletes the very
# passage that should have been scored.
_INLINE_CODE_RE = re.compile(r"(`+)(?!`)([^\n]+?)\1")

_BLOCKQUOTE_RE = re.compile(r"^[ \t]{0,3}>")

# A table row starts and ends with a pipe, or is a delimiter row. Requires two
# pipes so prose containing a single one survives.
_TABLE_RE = re.compile(
    r"^[ \t]{0,3}\|.*\|[ \t]*$"
    r"|^[ \t]{0,3}\|?[ \t]*:?-{3,}:?[ \t]*(?:\|[ \t]*:?-+:?[ \t]*)+\|?[ \t]*$"
)

_HEADING_RE = re.compile(r"^[ \t]{0,3}#{1,6}[ \t]")

# Only the unambiguous labels. "Contents", "Inhalt" and "Übersicht" are
# ordinary section headings in plenty of documents, and deleting a whole
# section on that guess would hide prose rather than quotes.
_TOC_HEADING_RE = re.compile(
    r"^[ \t]{0,3}#{1,6}[ \t]*(?:table of contents|inhaltsverzeichnis)"
    r"[ \t]*#*[ \t]*$",
    re.IGNORECASE,
)
# Under that heading only navigation is removed: blank lines and link list
# items. The first line that is neither ends the block.
_TOC_NAV_RE = re.compile(
    r"^(?:[ \t]*$|[ \t]{0,6}(?:[-*+]|\d+[.)])[ \t]+\[[^\]]*\])"
)

_LIST_ITEM_RE = re.compile(r"^[ \t]{0,6}(?:[-*+]|\d+[.)])[ \t]+(.*)$")
_INDENTED_RE = re.compile(r"^(?: {4}|\t)")
_CONTINUATION_RE = re.compile(r"^(?: {2,}|\t)\S")

# A catalogue entry quotes a term rather than making a statement: it opens
# with a quoted or emphasised token, and any prose after it is a gloss.
_CATALOGUE_ENTRY_RE = re.compile(
    r"""^\s*(?:
          ["“'‘]                # "delve into"
        | \*{1,3}[^*]           # **delve into**
        | _{1,2}[^_]            # _delve into_
        | `                     # `delve into`
    )""",
    re.VERBOSE,
)

def _strip_inline(line: str) -> str:
    """Remove code spans from a kept line.

    Leftover backticks are dropped too: an odd number of them on one line
    would pair up differently on a second pass, so the result would keep
    changing. A lone backtick carries no prose meaning.
    """
    return _INLINE_CODE_RE.sub(" ", line).replace("`", "")


def _is_catalogue_item(body: str) -> bool:
    """True when a list item marks itself as a quoted example.

    Only an explicit marker counts — quotation marks, emphasis, a code span.
    An earlier version also treated any short unpunctuated fragment as an
    entry, and that guess was wrong twice over: it removed real prose (a
    four-word bullet is often an argument in note form), and it was unstable,
    because removing a list item's inline code shortens it and can push it
    over the length threshold on a second pass. Guessing from length is the
    kind of heuristic this pre-pass must not make — a false removal hides the
    passage that should have been scored.
    """
    body = body.strip()
    if not body:
        return False
    return bool(_CATALOGUE_ENTRY_RE.match(body))


def strip_markup(text: str) -> str:
    """Markdown document -> the author's own prose.

    Removed lines become empty rather than disappearing, so line and paragraph
    structure survives — the structural metrics read it.

    Idempotent: strip_markup(strip_markup(x)) == strip_markup(x).
    """
    if not text:
        return text

    lines = text.split("\n")
    out = []

    fence_marker = None         # inside a fenced block, and with which marker
    in_toc = False              # inside a table-of-contents block
    last_kept_was_list = False  # last kept non-blank line was a list item
    separated = True            # a blank or removed line since that line

    i = 0
    while i < len(lines):
        line = lines[i]

        # --- fenced code, closed or not --------------------------------------
        if fence_marker is not None:
            out.append("")
            if re.match(r"^[ \t]{0,3}" + re.escape(fence_marker) + r"[ \t]*$",
                        line):
                fence_marker = None
            separated = True
            i += 1
            continue

        opening = _FENCE_OPEN_RE.match(line)
        if opening:
            fence_marker = opening.group(1)
            out.append("")
            separated = True
            i += 1
            continue

        # --- table of contents ------------------------------------------------
        if _TOC_HEADING_RE.match(line):
            in_toc = True
            out.append("")
            separated = True
            i += 1
            continue
        if in_toc:
            if _TOC_NAV_RE.match(line):
                out.append("")
                separated = True
                i += 1
                continue
            in_toc = False  # fall through and judge this line normally

        # --- blockquotes and tables -------------------------------------------
        if _BLOCKQUOTE_RE.match(line) or _TABLE_RE.match(line):
            out.append("")
            separated = True
            i += 1
            continue

        # --- list items --------------------------------------------------------
        item = _LIST_ITEM_RE.match(line)
        if item:
            if _is_catalogue_item(item.group(1)):
                # Take the indented continuations along: they gloss the entry
                # that was just removed, so they are part of the same quote.
                out.append("")
                i += 1
                while i < len(lines) and _CONTINUATION_RE.match(lines[i]):
                    out.append("")
                    i += 1
                separated = True
                continue
            out.append(_strip_inline(line))
            last_kept_was_list = True
            separated = False
            i += 1
            continue

        # --- indented block -----------------------------------------------------
        # Code only when it stands apart from the last kept prose and that prose
        # was not a list item. Otherwise it is a continuation — of a paragraph or
        # of a list entry — and continuations are the author's own voice.
        if _INDENTED_RE.match(line) and line.strip():
            if separated and not last_kept_was_list:
                while (i < len(lines) and _INDENTED_RE.match(lines[i])
                       and lines[i].strip()):
                    out.append("")
                    i += 1
                separated = True
                continue
            out.append(_strip_inline(line))
            separated = False
            i += 1
            continue

        # --- blank line ----------------------------------------------------------
        if not line.strip():
            out.append("")
            separated = True
            i += 1
            continue

        # --- ordinary prose ------------------------------------------------------
        stripped = _strip_inline(line)
        if not stripped.strip():
            # The line was nothing but a code span. It leaves no prose behind,
            # so it must count as a separator — otherwise the next indented
            # line is read as a continuation now and as code on a second pass.
            out.append("")
            separated = True
            i += 1
            continue
        out.append(stripped)
        # A heading does not end a list for continuation purposes only if the
        # list was already open; any other prose line does.
        last_kept_was_list = last_kept_was_list and bool(_HEADING_RE.match(line))
        separated = False
        i += 1

    result = "\n".join(out)
    # Collapse the runs of blank lines the removals left behind, but keep
    # paragraph separation.
    return re.sub(r"\n{3,}", "\n\n", result)


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
