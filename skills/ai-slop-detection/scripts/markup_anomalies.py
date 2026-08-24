#!/usr/bin/env python3
"""
Markdown markup-structure anomalies (issue #28) — detect-only.

Five structural tells of generated Markdown, reported as named signals
(never scored):

1. HeadingLevelJump — a heading goes deeper by 2+ levels (## -> ####).
2. ExcessiveThematicBreaks — more than 2 `---` breaks per 1000 words, with
   an absolute floor of 3 breaks so short texts never fire on one divider.
3. TitleCaseHeadings — more than 70% of headings are Title Case (every
   content word capitalized).
4. SingleRowTable — a table with exactly one data row (a list pretending
   to be a table).
5. BoldMidSentenceDensity — a paragraph with more than 2 sentences
   containing inline `**bold**` emphasis.

Boundary (#46): FormattingSlop in rhetorical_patterns covers emoji headings,
bold sprinkling as a *pattern instance*, and em-dash clusters. This module
measures *document-level structure rates* over the Markdown source; there is
no overlap with the scorer's formatting signals (no score contribution).

Public surface:
    find_markup_anomalies(text) -> {
        heading_jumps, thematic_breaks, words,
        title_case_heading_rate, single_row_tables, signals
    }
"""

import re

_HEADING = re.compile(r"^(#{1,6})\s+(.+)$", re.MULTILINE)
_BREAK = re.compile(r"^(?:---+|\*\*\*+|___+)\s*$", re.MULTILINE)
_BOLD = re.compile(r"\*\*[^*\n]+\*\*")
_SMALL_WORDS = {"of", "the", "for", "to", "in", "on", "a", "an", "and", "or",
                "with", "at", "by"}


def _headings(text: str) -> list:
    return [(len(m.group(1)), m.group(2).strip())
            for m in _HEADING.finditer(text)]


def _title_case_rate(headings: list) -> float:
    if not headings:
        return 0.0
    titled = 0
    for _, title in headings:
        content_words = [w for w in re.findall(r"[A-Za-z][A-Za-z'-]*", title)
                         if w.lower() not in _SMALL_WORDS]
        if not content_words:
            continue
        caps = sum(1 for w in content_words if w[0].isupper())
        if caps / len(content_words) >= 0.7:
            titled += 1
    return titled / len(headings)


def _single_row_tables(text: str) -> int:
    count = 0
    lines = text.split("\n")
    i = 0
    while i < len(lines):
        if lines[i].strip().startswith("|"):
            block = []
            while i < len(lines) and lines[i].strip().startswith("|"):
                block.append(lines[i])
                i += 1
            # header + separator + data rows
            if len(block) >= 3 and set(block[1].replace("|", "").replace(" ", "")) <= {"-", ":"}:
                data_rows = len(block) - 2
                if data_rows == 1:
                    count += 1
        else:
            i += 1
    return count


def find_markup_anomalies(text: str) -> dict:
    headings = _headings(text)
    jumps = []
    for (lvl, title), (next_lvl, next_title) in zip(headings, headings[1:]):
        if next_lvl - lvl >= 2:
            jumps.append(f"h{lvl} '{title}' -> h{next_lvl} '{next_title}'")

    words = len(re.findall(r"\b\w+\b", text))
    breaks = len(_BREAK.findall(text))
    break_rate = breaks / words * 1000 if words else 0.0

    title_rate = _title_case_rate(headings)
    single_tables = _single_row_tables(text)

    signals = []
    if jumps:
        signals.append({
            "id": "HeadingLevelJump",
            "confidence": 0.6,
            "evidence": "; ".join(jumps),
            "keep_when": "Documents that intentionally anchor deep sections "
                         "(rare); jumps of exactly one level never fire.",
        })
    if breaks >= 3 and break_rate > 2.0:
        signals.append({
            "id": "ExcessiveThematicBreaks",
            "confidence": 0.5,
            "evidence": f"{breaks} thematic breaks in {words} words "
                        f"({break_rate:.1f} per 1000)",
            "keep_when": "Slide-deck-style docs with intentional scene cuts; "
                         "absolute floor of 3 breaks protects short texts.",
        })
    if title_rate > 0.7:
        signals.append({
            "id": "TitleCaseHeadings",
            "confidence": 0.5,
            "evidence": f"{round(title_rate * 100)}% of headings are Title Case",
            "keep_when": "Style guides that mandate Title Case headings "
                         "(some corporate/APA variants).",
        })
    if single_tables:
        signals.append({
            "id": "SingleRowTable",
            "confidence": 0.55,
            "evidence": f"{single_tables} table(s) with exactly one data row",
            "keep_when": "A genuine key/value summary table where the header "
                         "is a real schema, not decoration.",
        })

    # Bold-mid-sentence density: per paragraph, sentences with inline bold.
    for para in re.split(r"\n\s*\n", text):
        sentences = [s for s in re.split(r"(?<=[.!?])\s+", para.strip()) if s]
        bold_sentences = sum(1 for s in sentences if _BOLD.search(s))
        if bold_sentences > 2:
            signals.append({
                "id": "BoldMidSentenceDensity",
                "confidence": 0.5,
                "evidence": f"{bold_sentences} sentences with inline bold in one paragraph",
                "keep_when": "Technical docs where bold marks literal UI labels "
                             "or key terms per sentence.",
            })
            break

    return {
        "heading_jumps": jumps,
        "thematic_breaks": breaks,
        "words": words,
        "title_case_heading_rate": round(title_rate, 3),
        "single_row_tables": single_tables,
        "signals": signals,
    }
