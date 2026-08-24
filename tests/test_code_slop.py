"""Tests for code-slop signals (issue #9) — detect-only module, no score impact."""

import os
import subprocess
import sys
import tempfile
import unittest

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SCRIPTS = os.path.join(ROOT, "skills", "ai-slop-detection", "scripts")
sys.path.insert(0, SCRIPTS)

from code_slop import analyze_code  # noqa: E402
from slop_scorer import slop_score  # noqa: E402

TS_CHAINED = """const data = await res.json();
const user = data as unknown as User;
const account = user as unknown as Account;
console.log(account.id);
"""

TS_AS_ANY = """function load(cfg: Config) {
  const raw = JSON.parse(cfg.blob) as any;
  const alt = readCache() as any;
  return raw ?? alt;
}
"""

TS_WIDEN_ASSERT = """function handle(evt: Event) {
  const wide: Record<string, unknown> = JSON.parse(evt.payload);
  const typed = wide as HandlerOptions;
  return typed;
}
"""

TS_CLEAN = """export function sum(values: number[]): number {
  let total = 0;
  for (const v of values) {
    total += v;
  }
  return total;
}
"""

PY_DEFENSIVE = """def process(rows):
    total = 0
    for row in rows:
        try:
            total += int(row["amount"])
        except (KeyError, ValueError):
            pass
        try:
            note = row["note"]
        except KeyError:
            pass
        try:
            date = row["date"]
        except KeyError:
            pass
    return total
"""

PY_CLEAN = """def parse_amount(row):
    try:
        return int(row["amount"])
    except (KeyError, ValueError) as exc:
        raise DataError(row) from exc
"""

TS_MOCKING = """import { vi } from "vitest";
import { send } from "./mailer";

vi.mock("./mailer");
vi.mock("./logger");
test("sends", () => { send({}); });
"""

PY_MONKEYPATCH_DENSE = """import pytest

def test_one(monkeypatch):
    monkeypatch.setattr("app.config.DEBUG", True)
    monkeypatch.setattr("app.db.connect", fake_connect)
    monkeypatch.setenv("ENV", "test")
    assert run()
"""

TS_MOCKING_SINGLE = """import { vi } from "vitest";
vi.mock("./logger");
test("x", () => { expect(1).toBe(1); });
"""


def ids(findings):
    return [f["id"] for f in findings]


class CodeSlopModuleTests(unittest.TestCase):
    def test_chained_type_assertions_detected_with_line(self):
        r = analyze_code(TS_CHAINED)
        hits = [f for f in r["findings"] if f["id"] == "chained_type_assertions"]
        self.assertEqual(len(hits), 2)
        for f in hits:
            self.assertGreaterEqual(f["line"], 1)
            self.assertLessEqual(f["line"], 3)
            self.assertIn("as unknown as", f["evidence"])

    def test_as_any_casts_counted(self):
        r = analyze_code(TS_AS_ANY)
        self.assertEqual(r["counts"]["as_any_casts"], 2)
        self.assertIn("as_any_casts", ids(r["findings"]))

    def test_widen_then_assert_detected(self):
        r = analyze_code(TS_WIDEN_ASSERT)
        self.assertIn("widen_then_assert", ids(r["findings"]))

    def test_widen_assert_requires_same_function(self):
        # Record<string, unknown> in one function, the cast in another -> no hit
        text = ("function a(x: string) { const w: Record<string, unknown> = {}; "
                "return w; }\n"
                "function b(o: object) { const t = o as Options; return t; }\n")
        r = analyze_code(text)
        self.assertNotIn("widen_then_assert", ids(r["findings"]))

    def test_excessive_defensive_try_except_detected(self):
        r = analyze_code(PY_DEFENSIVE)
        self.assertIn("excessive_defensive_try", ids(r["findings"]))
        self.assertEqual(r["counts"]["defensive_try_pass"], 3)

    def test_single_honest_try_except_not_flagged(self):
        r = analyze_code(PY_CLEAN)
        self.assertNotIn("excessive_defensive_try", ids(r["findings"]))

    def test_module_mocking_density_detected(self):
        r = analyze_code(TS_MOCKING)
        self.assertIn("module_mocking", ids(r["findings"]))
        self.assertEqual(r["counts"]["mock_calls"], 2)

    def test_pytest_monkeypatch_density_detected(self):
        r = analyze_code(PY_MONKEYPATCH_DENSE)
        self.assertIn("module_mocking", ids(r["findings"]))

    def test_single_mock_call_below_threshold_not_flagged(self):
        r = analyze_code(TS_MOCKING_SINGLE)
        self.assertNotIn("module_mocking", ids(r["findings"]))

    def test_clean_code_has_no_findings(self):
        for src in (TS_CLEAN, PY_CLEAN):
            r = analyze_code(src)
            self.assertEqual(r["findings"], [], src)

    def test_safety_comment_convention_documented(self):
        # The safety_comment_required convention must be documented in the
        # module (docstring or dedicated constant), per issue #9 spec.
        import code_slop
        self.assertIn("SAFETY:", code_slop.__doc__)

    def test_detect_only_no_score_influence(self):
        # code_slop must NOT add a dimension/family to the text scorer
        result = slop_score(TS_CHAINED)
        self.assertNotIn("code_slop", result["dimensions"])
        self.assertNotIn("code_slop", result["dimension_scores"])


class CodeSlopCLITests(unittest.TestCase):
    def run_cli(self, content, suffix):
        with tempfile.NamedTemporaryFile("w", suffix=suffix, delete=False) as f:
            f.write(content)
            path = f.name
        try:
            return subprocess.run(
                [sys.executable, os.path.join(ROOT, "scripts", "code_slop_check.py"),
                 "--file", path],
                capture_output=True, text=True)
        finally:
            os.unlink(path)

    def test_cli_reports_findings_and_exits_one(self):
        p = self.run_cli(TS_CHAINED, ".ts")
        self.assertEqual(p.returncode, 1)
        self.assertIn("chained_type_assertions", p.stdout)

    def test_cli_clean_file_exits_zero(self):
        p = self.run_cli(TS_CLEAN, ".ts")
        self.assertEqual(p.returncode, 0)

    def test_cli_requires_file_argument(self):
        p = subprocess.run(
            [sys.executable, os.path.join(ROOT, "scripts", "code_slop_check.py")],
            capture_output=True, text=True)
        self.assertEqual(p.returncode, 2)


if __name__ == "__main__":
    unittest.main()
