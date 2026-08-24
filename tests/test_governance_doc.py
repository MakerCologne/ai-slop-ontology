"""#67 — SCORE-GOVERNANCE.md Pflicht-Abschnitte (validiert via check_methodology.py)."""
import os
import subprocess
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DOC = os.path.join(ROOT, "docs", "SCORE-GOVERNANCE.md")


def test_governance_doc_exists():
    assert os.path.isfile(DOC)


def test_governance_mandatory_sections():
    text = open(DOC, encoding="utf-8").read()
    for s in ("Optimierungs-Freigaben", "Guardrail-Pflicht",
              "Re-Baseline-Kalender", "Change-Protokoll"):
        assert s in text, f"SCORE-GOVERNANCE.md: Abschnitt '{s}' fehlt"


def test_governance_references_praxisfaelle():
    text = open(DOC, encoding="utf-8").read()
    assert "0.982" in text and "0.476" in text, "F1-Praxisfall fehlt"
    assert "0.03" in text and "0.02" in text, "#14-Gewichtungsreduktion fehlt"


def test_check_methodology_validates_governance():
    proc = subprocess.run([sys.executable, "scripts/check_methodology.py"],
                          capture_output=True, text=True, cwd=ROOT)
    assert proc.returncode == 0, proc.stdout + proc.stderr
