"""#66 — Issue-/PR-Templates mit Pflichtfeldern."""
import os

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
ISSUE_DIR = os.path.join(ROOT, ".github", "ISSUE_TEMPLATE")
SIGNAL = os.path.join(ISSUE_DIR, "signal-proposal.md")
BUG = os.path.join(ISSUE_DIR, "bug.md")
PR = os.path.join(ROOT, ".github", "PULL_REQUEST_TEMPLATE.md")


def test_template_files_exist():
    for p in (SIGNAL, BUG, PR):
        assert os.path.isfile(p), f"{p} fehlt"


def test_signal_proposal_mandatory_fields():
    text = open(SIGNAL, encoding="utf-8").read()
    for marker in ("Corpus Evidence", "Prior Art", "False Positive Analysis",
                   "FP-Analyse", "Test-Oracle", "depends-on",
                   "Graduation Criteria"):
        assert marker in text, f"signal-proposal.md: Pflichtfeld '{marker}' fehlt"


def test_bug_template_mandatory_fields():
    text = open(BUG, encoding="utf-8").read()
    for marker in ("Signal", "Input", "Erwartet", "Tatsächlich", "Evidence"):
        assert marker in text, f"bug.md: Pflichtfeld '{marker}' fehlt"


def test_pr_template_mandatory_fields():
    text = open(PR, encoding="utf-8").read()
    for marker in ("Corpus Evidence", "Prior Art", "FP-Analyse",
                   "Test-Oracle", "Signals-DoD", "SIGNAL-DOD",
                   "Messung", "vorher", "nachher"):
        assert marker in text, f"PULL_REQUEST_TEMPLATE.md: Pflichtfeld '{marker}' fehlt"
