"""#68 — EVALS.md ordnet jede Datei unter eval/ und tests/ einer Ebene zu."""
import glob
import os
import subprocess
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DOC = os.path.join(ROOT, "docs", "EVALS.md")


def test_evals_doc_exists():
    assert os.path.isfile(DOC)


def test_evals_doc_has_three_levels():
    text = open(DOC, encoding="utf-8").read()
    for s in ("L1", "L2", "L3", "Unit-Assertion", "Control Set",
              "Quartals"):
        assert s in text, f"EVALS.md: '{s}' fehlt"


def test_every_eval_and_test_file_mapped():
    text = open(DOC, encoding="utf-8").read()
    files = [os.path.basename(p) for p in
             glob.glob(os.path.join(ROOT, "eval", "*.py"))
             + glob.glob(os.path.join(ROOT, "eval", "*.jsonl"))
             + glob.glob(os.path.join(ROOT, "tests", "test_*.py"))]
    assert files, "keine Eval-/Test-Dateien gefunden"
    for name in files:
        assert name in text, f"EVALS.md: {name} keiner Ebene zugeordnet"


def test_check_methodology_validates_evals():
    proc = subprocess.run([sys.executable, "scripts/check_methodology.py"],
                          capture_output=True, text=True, cwd=ROOT)
    assert proc.returncode == 0, proc.stdout + proc.stderr
