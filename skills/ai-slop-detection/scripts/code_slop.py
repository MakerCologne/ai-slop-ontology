#!/usr/bin/env python3
"""Code-slop signals (issue #9) — detect-only utility module.

Like #31/#32 (generated_docs, reinventing_wheel) this module has NO influence
on the numeric text-slop score. It reports structured findings for human
review; the CLI entry is `scripts/code_slop_check.py` (deliberately separate
from `slop_scorer.py` — see the decision note in CHANGELOG #9).

Signals (regex/token based — no AST framework, but structured with line
numbers and evidence):

  - chained_type_assertions : TypeScript `as X as Y` double casts
  - as_any_casts            : TypeScript `as any` casts (counted)
  - widen_then_assert       : `Record<string, unknown>` (or `unknown`) and a
                              subsequent `as` cast within the SAME function
  - excessive_defensive_try : >= 3 `try/except`-with-`pass` blocks in one
                              Python file (defensive swallowing)
  - module_mocking          : test-mocking density — >= 2 of
                              jest.mock()/vi.mock() in TS or monkeypatch
                              calls in Python per file

Safety-comment convention (documented per issue #9):
  A cast or defensive block that is genuinely required MUST carry a comment
  starting with `SAFETY:` explaining why the narrower/unsafe form is correct,
  e.g. `// SAFETY: API contract guarantees user.id is a string here.` The
  checker does not enforce the comment (detect-only); it is the documented
  house convention for reviewing flagged sites.

Public surface:
    analyze_code(text, lang=None) -> {"findings": [...], "counts": {...}}
    findings: {"id", "line", "evidence", "hint"}
"""

import re

MOCK_THRESHOLD = 2
DEFENSIVE_TRY_THRESHOLD = 3

_CHAINED_CAST = re.compile(r"as\s+unknown\s+as\s+\w+")
_AS_ANY = re.compile(r"\bas\s+any\b")
_RECORD_WIDEN = re.compile(r"Record<\s*string\s*,\s*unknown\s*>|\bas\s+unknown\b")
_AS_CAST = re.compile(r"\bas\s+\w+")
# Function boundaries for the widen-then-assert scope heuristic. A "function"
# spans from a `function`/`=>`-introducing line to the next top-level `}` on
# its own (column 0) — crude but sufficient for line-oriented review hints.
_FUNC_START = re.compile(r"\bfunction\b|\([^)]*\)\s*(?::\s*\w+)?\s*=>")
_JS_MOCK = re.compile(r"\b(?:jest|vi)\.mock\s*\(")
_PY_MOCK = re.compile(r"monkeypatch\.(?:setattr|setenv|delenv|chdir)\s*\(")
_DEFENSIVE_BLOCK = re.compile(
    r"try\s*:\s*\n(?:\s+.*\n)*?\s*except[^\n]*:\s*\n\s+pass", re.MULTILINE)
_ANY_AS_TS = re.compile(r"\bas\s+any\b")


def _functions(lines):
    """Yield (start, end) line-index ranges of function-shaped blocks."""
    spans = []
    start = None
    for i, line in enumerate(lines):
        if start is None and _FUNC_START.search(line):
            # one-liner function: opens and closes on the same line
            if line.rstrip().endswith("}"):
                spans.append((i, i))
            else:
                start = i
        elif start is not None and line.startswith("}"):
            spans.append((start, i))
            start = None
    if start is not None:
        spans.append((start, len(lines) - 1))
    return spans


def analyze_code(text: str, lang: str = None) -> dict:
    """Analyze source text (TypeScript or Python) for code-slop signals.

    `lang` is optional; signals are pattern-based and language-tagged by
    their syntax, so auto-detection is unnecessary.
    """
    findings = []
    counts = {"as_any_casts": 0, "mock_calls": 0, "defensive_try_pass": 0}

    lines = text.splitlines()

    def line_of(pattern, default=1):
        for i, line in enumerate(lines, start=1):
            if pattern.search(line):
                return i
        return default

    # 1. chained `as X as Y`
    for i, line in enumerate(lines, start=1):
        if _CHAINED_CAST.search(line):
            findings.append({
                "id": "chained_type_assertions", "line": i,
                "evidence": _CHAINED_CAST.search(line).group(0),
                "hint": "double cast erases the type system; validate the shape instead"})

    # 2. as-any casts
    for i, line in enumerate(lines, start=1):
        n = len(_AS_ANY.findall(line))
        if n:
            counts["as_any_casts"] += n
            if counts["as_any_casts"]:
                findings.append({
                    "id": "as_any_casts", "line": i,
                    "evidence": _AS_ANY.search(line).group(0),
                    "hint": "as any hides real type problems; see SAFETY: comment convention"})
        if counts["as_any_casts"] > 0 and i == len(lines) and not any(
                f["id"] == "as_any_casts" for f in findings):
            pass

    # 3. widen-then-assert within one function (TS)
    for start, end in _functions(lines):
        block = "\n".join(lines[start:end + 1])
        if _RECORD_WIDEN.search(block) and _AS_CAST.search(block):
            # only when the cast is not on the same line as the widening
            for j, line in enumerate(lines[start:end + 1], start=start + 1):
                if _AS_CAST.search(line) and not _RECORD_WIDEN.search(line):
                    findings.append({
                        "id": "widen_then_assert", "line": j,
                        "evidence": _AS_CAST.search(line).group(0),
                        "hint": "widen to unknown then assert back — declare the type"})
                    break

    # 4. excessive defensive try/except pass (Python)
    defensive = _DEFENSIVE_BLOCK.findall(text or "")
    counts["defensive_try_pass"] = len(defensive)
    if len(defensive) >= DEFENSIVE_TRY_THRESHOLD:
        for i, line in enumerate(lines, start=1):
            if re.match(r"\s*except[^\n]*:\s*$", line):
                findings.append({
                    "id": "excessive_defensive_try", "line": i,
                    "evidence": line.strip(),
                    "hint": f">= {DEFENSIVE_TRY_THRESHOLD} try/except-pass blocks in one file"})
                break

    # 5. module-mocking density
    mock_calls = len(_JS_MOCK.findall(text)) + len(_PY_MOCK.findall(text))
    counts["mock_calls"] = mock_calls
    if mock_calls >= MOCK_THRESHOLD:
        findings.append({
            "id": "module_mocking", "line": line_of(_JS_MOCK) if _JS_MOCK.search(text)
            else line_of(_PY_MOCK),
            "evidence": f"{mock_calls} mock calls in file",
            "hint": f">= {MOCK_THRESHOLD} module mocks/patches — high coupling to internals"})

    return {"findings": findings, "counts": counts}
