"""#65 — ADR-System: adr/ mit MADR-Template + 7 Rückdokumentationen."""
import glob
import os
import subprocess
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
ADR_DIR = os.path.join(ROOT, "adr")


def test_madr_template_exists():
    assert os.path.isfile(os.path.join(ADR_DIR, "0000-madr-template.md"))


def test_seven_adrs_exist():
    for n in range(1, 8):
        files = glob.glob(os.path.join(ADR_DIR, f"000{n}-*.md"))
        assert len(files) == 1, f"adr/000{n}-*.md fehlt"


def test_each_adr_has_mandatory_fields():
    for path in sorted(glob.glob(os.path.join(ADR_DIR, "0*.md"))):
        name = os.path.basename(path)
        if name.startswith("0000-"):
            continue
        text = open(path, encoding="utf-8").read()
        for field in ("Status", "Context", "Decision", "Consequences"):
            assert field in text, f"{name}: '{field}' fehlt"
        assert "accepted" in text.lower(), f"{name}: Status nicht accepted"
        import re
        options = re.findall(r"^###?\s+Option\s+\w+", text, re.M)
        assert len(options) >= 2, f"{name}: <2 Considered Options"


def test_adrs_reference_burn_log():
    for path in sorted(glob.glob(os.path.join(ADR_DIR, "0*.md"))):
        name = os.path.basename(path)
        if name.startswith("0000-"):
            continue
        text = open(path, encoding="utf-8").read()
        assert "burn-log" in text, f"{name}: kein burn-log-Verweis"


def test_check_methodology_validates_adrs():
    proc = subprocess.run([sys.executable, "scripts/check_methodology.py"],
                          capture_output=True, text=True, cwd=ROOT)
    assert proc.returncode == 0, proc.stdout + proc.stderr
