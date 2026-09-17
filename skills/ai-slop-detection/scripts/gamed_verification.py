#!/usr/bin/env python3
"""GAMED VERIFICATION — detect-only diff signals for test files (issue #112).

Adds the missing test criterion to the diff mode (#10): the worst agent
artifacts live in what was REMOVED or neutralized, not in what was added
(cf. jayj221/hallucinot, peeramid-labs/sloppoke "defensive theatre"):

  AssertionDelta   net loss of assertions in a changed test file
                   (weakened-assertions: 6 asserts in base -> 3 in head)
  SkippedTest      newly added skips/marks instead of a fix
                   (@pytest.mark.skip, it.skip(...), t.Skip(...), xit(...))
  TrivialAssertion newly added tautological assertions
                   (assert True, expect(true).toBe(true), assert 1 == 1)
  StubLeftBehind   newly added stub markers inside test files
                   (raise NotImplementedError, TODO: implement)

DETECT-ONLY: never rewrites anything (ADR-0001). Findings are advisory,
never part of the numeric text/code slop score (detect-only module
discipline, ADR-0006 — same class as metadata_slop / paste_artifacts).

Deterministic regex basis (no AST dependency): counting `assert`-like
patterns is engine-portable across Python/JS/TS/Go/Java test files. Known
FP edge (documented): a legitimate parametrize refactor can reduce the raw
assert count — therefore AssertionDelta severity is "medium", confidence
0.7, evidence always carries the concrete base/head counts.

Public surface:
    is_test_file(path) -> bool
    analyze_test_diff(path, base_text, head_text) -> [GamedFinding]
    gamed_verification(base, head, repo_dir=None) -> [per-file reports]
"""

import os
import re
import subprocess
from dataclasses import dataclass

# ---------------------------------------------------------------------------
# Test file identification
# ---------------------------------------------------------------------------

_TEST_SUFFIXES = (".test.ts", ".test.tsx", ".test.js", ".test.jsx",
                  ".spec.ts", ".spec.tsx", ".spec.js", ".spec.jsx",
                  "_test.go", "_test.py")


def is_test_file(path):
    """True for conventional test file names (pytest, jest, go test, junit)."""
    base = os.path.basename(path)
    if base.startswith("test_") or base.startswith("Test"):
        return True
    if base.endswith(_TEST_SUFFIXES):
        return True
    return base.endswith(".py") and base.endswith("_test.py")


# ---------------------------------------------------------------------------
# Assertion counting / added-line extraction
# ---------------------------------------------------------------------------

# One "assertion-like" occurrence per match. Python: `assert x`,
# unittest `self.assert*`, `pytest.raises`; JS/TS: `expect(`, `assert(`,
# chai `.should(`, node assert `t.equal`; Go: no assert convention is
# forced (Go tests report via t.Errorf) — t.Error/t.Fatal counted instead.
_ASSERT_RE = re.compile(
    r"(?:\bassert\s+\w|\bself\.assert\w+|\bpytest\.raises\(|\bexpect\("
    r"|\bassert\(|\.should\(|\bt\.(?:equal|deepEqual|isTrue|strictEqual)\("
    r"|\bt\.(?:Errorf|Fatal|Fatalf)\()"
)

_SKIP_ADDED_RE = re.compile(
    r"(?:@pytest\.mark\.skip|@unittest\.skip|pytest\.skip\(|"
    r"\bit\.skip\(|\btest\.skip\(|\bdescribe\.skip\(|\.skipif\(|"
    r"\bxit\(|\bxdescribe\(|\bt\.Skip\(|\bt\.Skipf\()"
)

_TRIVIAL_ASSERT_RE = re.compile(
    r"(?:\bassert\s+(?:True|1(?:\s*==\s*1)?|True\s*==\s*True)\b|"
    r"\bself\.assertTrue\(\s*True\s*\)|"
    r"\bexpect\(\s*(?:true|1)\s*\)\.\s*toBe\(\s*(?:true|1)\s*\)|"
    r"\bexpect\(\s*true\s*\)\.\s*toBeTruthy\(\s*\))"
)

_STUB_RE = re.compile(
    r"(?:raise\s+NotImplementedError|NotImplementedError\(|"
    r"(?://|#|/\*)\s*TODO:?\s*implement|/\*\s*TODO:?\s*implement)"
)


def _count_assertions(text):
    return len(_ASSERT_RE.findall(text or ""))


def _added_removed(diff_text, path):
    """Return (added_lines, removed_lines) for one file of a unified diff."""
    added, removed, current = [], [], None
    for line in diff_text.splitlines():
        if line.startswith("+++ b/"):
            current = line[6:]
        elif current == path and line.startswith("+") and not line.startswith("+++"):
            added.append(line[1:])
        elif current == path and line.startswith("-") and not line.startswith("---"):
            removed.append(line[1:])
    return added, removed


# ---------------------------------------------------------------------------
# Findings
# ---------------------------------------------------------------------------

@dataclass
class GamedFinding:
    signal_id: str        # AssertionDelta | SkippedTest | TrivialAssertion | StubLeftBehind
    file: str
    confidence: float
    evidence: str
    severity: str = "medium"  # detect-only: advisory, never hard-gated

    def __str__(self):  # pragma: no cover - debug helper
        return f"[{self.signal_id}] {self.evidence[:80]!r} (conf {self.confidence})"


def analyze_test_diff(path, base_text, head_text, added_lines=None):
    """Detect gamed-verification signals in one changed test file.

    `added_lines` (optional) restricts SkippedTest/TrivialAssertion/
    StubLeftBehind to newly added lines; without it the whole head text is
    inspected (simpler unit-test surface, same findings for typical diffs).
    """
    findings = []
    if not is_test_file(path):
        return findings
    base_n, head_n = _count_assertions(base_text), _count_assertions(head_text)
    if base_n > head_n and (head_text or "").strip():
        findings.append(GamedFinding(
            "AssertionDelta", path, 0.7,
            f"assertions weakened: {base_n} in base -> {head_n} in head "
            f"(net {head_n - base_n})",
        ))
    scope = added_lines if added_lines is not None else (head_text or "").splitlines()
    joined = "\n".join(scope)
    if _SKIP_ADDED_RE.search(joined):
        m = _SKIP_ADDED_RE.search(joined)
        findings.append(GamedFinding(
            "SkippedTest", path, 0.85, f"skip added instead of fix: {m.group(0)!r}",
        ))
    for m in _TRIVIAL_ASSERT_RE.finditer(joined):
        findings.append(GamedFinding(
            "TrivialAssertion", path, 0.9, f"tautological assertion: {m.group(0)!r}",
        ))
    if _STUB_RE.search(joined):
        m = _STUB_RE.search(joined)
        findings.append(GamedFinding(
            "StubLeftBehind", path, 0.6, f"stub marker in test file: {m.group(0)!r}",
        ))
    return findings


def _git(repo_dir, *args):
    return subprocess.run(["git", *args], cwd=repo_dir, check=True,
                          capture_output=True, text=True).stdout


def gamed_verification(base, head, repo_dir=None):
    """Run gamed-verification analysis over `git diff base..head`.

    Returns per-file report dicts:
      {file, kind: "test", findings: [GamedFinding asdict]}
    Non-test files are ignored; deleted test files are ignored (a removal
    is a review decision, not a detect-only signal).
    """
    repo_dir = repo_dir or os.getcwd()
    diff_text = _git(repo_dir, "diff", "--unified=0", base, head)
    report = []
    files = {}
    for line in diff_text.splitlines():
        if line.startswith("+++ b/"):
            files[line[6:]] = None
    for path in sorted(files):
        if not is_test_file(path):
            continue
        try:
            head_text = _git(repo_dir, "show", f"{head}:{path}")
        except subprocess.CalledProcessError:
            continue  # deleted file
        try:
            base_text = _git(repo_dir, "show", f"{base}:{path}")
        except subprocess.CalledProcessError:
            base_text = ""  # newly added file
        added, _removed = _added_removed(diff_text, path)
        findings = analyze_test_diff(path, base_text, head_text, added)
        if findings:
            report.append({"file": path, "kind": "test",
                           "findings": [f.__dict__ for f in findings]})
    return report
