"""#63 — METHODOLOGY.md consistency checks (docs/METHODOLOGY.md + scripts/check_methodology.py)."""
import os
import subprocess
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DOC = os.path.join(ROOT, "docs", "METHODOLOGY.md")
SCRIPT = os.path.join(ROOT, "scripts", "check_methodology.py")


def test_methodology_doc_exists():
    assert os.path.isfile(DOC), "docs/METHODOLOGY.md fehlt"


def test_methodology_doc_has_eleven_principles():
    text = open(DOC, encoding="utf-8").read()
    for i in range(1, 12):
        assert f"M{i}" in text, f"Querprinzip M{i} fehlt in METHODOLOGY.md"


def test_methodology_doc_has_signal_lifecycle():
    text = open(DOC, encoding="utf-8").read()
    for state in ("nursery", "beta", "stable", "deprecated", "retired"):
        assert state in text, f"Lebenszyklus-Zustand '{state}' fehlt"
    assert "status" in text, "status-Feld-Spezifikation fehlt"


def test_check_methodology_script_runs_green():
    assert os.path.isfile(SCRIPT), "scripts/check_methodology.py fehlt"
    proc = subprocess.run(
        [sys.executable, SCRIPT], capture_output=True, text=True, cwd=ROOT
    )
    assert proc.returncode == 0, (
        f"check_methodology.py schlug fehl:\n{proc.stdout}\n{proc.stderr}"
    )
