#!/usr/bin/env python3
"""Gamed Verification for Diff-Modus (issue #112, detect-only).

Assertion-based Prüfebene für Test-Dateien in einem Diff
(`--diff base..head`, issue #10). Liefert Findings im
Findings-Standard (#119: {signal_id, span, evidence_quote,
suggested_action}) — advisory, nie Score-wirksam (ADR-0001/ADR-0006).

Signale (Quellen: jayj221/hallucinot, peeramid-labs/sloppoke):
  - AssertionDelta: Netto-Verlust von Assertions in einer Testdatei
    (Assertions entfernt/geschwächt statt Fix geliefert)
  - SkippedTest: im Diff HINZUGEFÜGTE Skip-/xfail-Marker
    (pytest.mark.skip, @unittest.skip, it.skip, describe.skip, t.skip, xit)
  - TrivialAssertion: immer-wahre Assertions
    (assert True, assertTrue(True), expect(true).toBe(true),
     assertEqual(1, 1), expect(x).toBe(x) — beide Seiten identisch)

Analyse auf alten (base) vs. neuen (head) Inhalt der Testdatei:
  - .py per ast (Assert, pytest.raises, unittest skip decorators)
  - JS/TS per Regex (expect(, assert, should, skip/xfail-Marker)

Public surface:
    is_test_file(path) -> bool
    count_assertions_py(text) -> int          # ast-basiert
    count_assertions_js(text) -> int          # regex-basiert
    find_skips(added_lines) -> [finding]      # Zeilen (nr, text) im Diff
    find_trivial(added_lines) -> [finding]
    analyze_test_diff(path, old_text, new_text, added_diff_lines) -> result
"""

import ast
import re

# --------------------------------------------------------------------------
# Test-Datei-Erkennung
TEST_PY = re.compile(r"(^|/)(test_[^/]+\.py|[^/]+_test\.py|conftest\.py)$")
TEST_JS = re.compile(r"\.(test|spec)\.(ts|tsx|js|jsx)$")


def is_test_file(path: str) -> bool:
    return bool(TEST_PY.search(path) or TEST_JS.search(path))


# --------------------------------------------------------------------------
# Assertion-Zählung (Python: ast; JS: Regex)
class _PyAssertCounter(ast.NodeVisitor):
    def __init__(self):
        self.n = 0

    def visit_Assert(self, node):  # noqa: N802
        self.n += 1
        self.generic_visit(node)

    def visit_Call(self, node):  # noqa: N802
        f = node.func
        name = getattr(f, "attr", None) or getattr(f, "id", "")
        if name in ("assertEqual", "assertTrue", "assertIs", "assertIn",
                    "assertRaises", "assertGreater", "assertLess",
                    "assertIsNotNone", "assertFalse", "assertNotEqual"):
            self.n += 1
        if name == "raises":  # pytest.raises / unittest.mock
            self.n += 1
        self.generic_visit(node)


def count_assertions_py(text: str) -> int:
    try:
        tree = ast.parse(text)
    except SyntaxError:
        # Fallback: grobe Regex-Zählung, damit gelöschte Files zählbar bleiben
        return len(re.findall(r"^\s*assert\b|\bassert(?:Equal|True|Raises|In)\b",
                              text, re.M))
    c = _PyAssertCounter()
    c.visit(tree)
    return c.n


_JS_ASSERT = re.compile(
    r"\bexpect\s*\(|\bassert\s*[.(]|\bshould\b|\.toEqual\s*\(|\.toBe\s*\(")
_JS_TRIVIAL = re.compile(
    r"expect\s*\(\s*(?:true|1)\s*\)\s*\.\s*toBe\s*\(\s*(?:true|1)\s*\)"
    r"|assert\s*\(\s*true\s*\)"
    r"|expect\s*\(\s*(\w+)\s*\)\s*\.\s*toBe\s*\(\s*\1\s*\)", re.S)
_PY_TRIVIAL = re.compile(
    r"^\s*assert\s+(?:True|1)\s*(?:#.*)?$"
    r"|^\s*assert\s+(\w+)\s*==\s*\1\s*(?:#.*)?$"
    r"|assert(?:True|Equal)\s*\(\s*(?:True|1)\s*,\s*(?:True|1)\s*\)", re.M | re.S)
_SKIP_MARKER = re.compile(
    r"pytest\.mark\.skip|pytest\.mark\.xfail|@unittest\.skip"
    r"|\bit\.skip|\bdescribe\.skip|\bxit\s*\(|\.skip\s*\(|\bt\.skip\s*\("
    r"|\bxit\b|\.only\s*\(")


def count_assertions_js(text: str) -> int:
    return len(_JS_ASSERT.findall(text))


def _mk(signal_id, line_nr, quote, action):
    return {"signal_id": signal_id,
            "span": {"start_line": line_nr, "end_line": line_nr},
            "evidence_quote": quote.strip()[:160],
            "suggested_action": action}


def find_skips(added_lines):
    """added_lines: [(head_line_nr, line_text)] der hinzugefügten Zeilen."""
    out = []
    for nr, text in added_lines:
        stripped = text.strip()
        if stripped.startswith("#") or stripped.startswith("//"):
            continue  # Kommentar-Zeile, kein Code (FP-Guard)
        if _SKIP_MARKER.search(text):
            out.append(_mk("SkippedTest", nr, text,
                           "Skip/xfail hinzugefügt statt Fix prüfen — "
                           "detect-only: Grund dokumentieren oder Test "
                           "reparieren (issue #112)."))
    return out


def find_trivial(added_lines):
    out = []
    pat = (_PY_TRIVIAL, _JS_TRIVIAL)
    for nr, text in added_lines:
        for p in pat:
            if p.search(text):
                out.append(_mk("TrivialAssertion", nr, text,
                               "Immer-wahre Assertion hinzugefügt — echtes "
                               "Verhalten.asserten (detect-only, #112)."))
                break
    return out


def analyze_test_diff(path, old_text, new_text, added_diff_lines):
    """added_diff_lines: [(head_line_nr, line_text)] wie im Diff (+)-Zeilen.

    Rückgabe: {'file', 'kind': 'test', 'assertion_delta': int|None,
               'findings': [...]} — kein Score-Feld (ADR-0001)."""
    js = bool(TEST_JS.search(path))
    counter = count_assertions_js if js else count_assertions_py
    old_n = counter(old_text) if old_text is not None else 0
    new_n = counter(new_text) if new_text is not None else 0
    delta = new_n - old_n
    findings = find_skips(added_diff_lines) + find_trivial(added_diff_lines)
    if delta < 0:
        findings.append(_mk(
            "AssertionDelta", 0,
            f"{old_n} -> {new_n} Assertions ({delta})",
            f"Netto-Verlust von {abs(delta)} Assertions in {path} — "
            "geschwächte statt reparierte Prüfung prüfen (detect-only, #112)."))
    findings.sort(key=lambda f: f["span"]["start_line"])
    return {"file": path, "kind": "test", "assertion_delta": delta,
            "assertions_old": old_n, "assertions_new": new_n,
            "findings": findings}
