#!/usr/bin/env python3
"""
Methodology/ADR/Governance consistency checks (#63, #65, #67, #68).

Checks (offline, no API calls):

  1. docs/METHODOLOGY.md exists, contains M1-M11, all lifecycle states
     and the `status` field spec.
  2. Every issue reference (#N) in METHODOLOGY.md appears in the doc's
     own "Referenzierte Issues" list.
  3. adr/ contains ADR-0000 (MADR template) and ADR-0001..0007; each ADR
     has the mandatory fields: status, Context, Decision, Consequences,
     and >= 2 Considered Options.
  4. docs/SCORE-GOVERNANCE.md contains the mandatory sections.
  5. docs/EVALS.md maps every file under eval/ and tests/ to a level
     (L1/L2/L3) — unmapped files fail.

Run:  python3 scripts/check_methodology.py
"""

import glob
import os
import re
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

errors = []


def check(condition: bool, message: str):
    if not condition:
        errors.append(message)


def read(path: str) -> str:
    with open(os.path.join(ROOT, path), encoding="utf-8") as f:
        return f.read()


# ---------------------------------------------------------------- #63
def check_methodology_doc():
    path = os.path.join(ROOT, "docs", "METHODOLOGY.md")
    check(os.path.isfile(path), "docs/METHODOLOGY.md fehlt")
    if not os.path.isfile(path):
        return
    text = read("docs/METHODOLOGY.md")

    for i in range(1, 12):
        check(f"M{i}" in text, f"METHODOLOGY.md: Querprinzip M{i} fehlt")
    for state in ("nursery", "beta", "stable", "deprecated", "retired"):
        check(state in text, f"METHODOLOGY.md: Lebenszyklus-Zustand '{state}' fehlt")
    check("status" in text, "METHODOLOGY.md: status-Feld-Spezifikation fehlt")

    # Issue-reference consistency: every #N mentioned must be in the
    # doc's own reference list.
    mentioned = set(re.findall(r"#(\d+)", text))
    list_match = re.search(
        r"Referenzierte Issues.*?\n\s*\n(.*?)\Z",
        text,
        re.S,
    )
    check(list_match is not None,
          "METHODOLOGY.md: Abschnitt 'Referenzierte Issues' fehlt")
    if list_match:
        listed = set(re.findall(r"#(\d+)", list_match.group(1)))
        missing = sorted(mentioned - listed, key=int)
        check(not missing,
              f"METHODOLOGY.md: referenzierte Issues fehlen in der "
              f"Konsistenz-Liste: #{', #'.join(missing)}")


# ---------------------------------------------------------------- #65
ADR_REQUIRED = ("Status", "Context", "Decision", "Consequences")


def check_adrs():
    """#65 — ADR checks. Activated when the adr/ directory exists."""
    adr_dir = os.path.join(ROOT, "adr")
    if not os.path.isdir(adr_dir):
        return  # ADR system not introduced yet (#65)
    check(os.path.isfile(os.path.join(adr_dir, "0000-madr-template.md")),
          "adr/0000-madr-template.md fehlt")
    for n in range(1, 8):
        files = glob.glob(os.path.join(adr_dir, f"000{n}-*.md"))
        check(len(files) == 1, f"adr/000{n}-*.md fehlt oder mehrfach vorhanden")

    for path in sorted(glob.glob(os.path.join(adr_dir, "0*.md"))):
        name = os.path.basename(path)
        if name.startswith("0000-"):
            continue  # template, not a decision
        text = open(path, encoding="utf-8").read()
        for field in ADR_REQUIRED:
            check(field in text, f"{name}: Pflichtfeld '{field}' fehlt")
        check("accepted" in text.lower(), f"{name}: Status 'accepted' fehlt")
        options = re.findall(r"^###?\s+(?:Option\s+\d+|Option [A-Z0-9]+).*",
                             text, re.M)
        check(len(options) >= 2,
              f"{name}: weniger als 2 Considered Options dokumentiert")


# ---------------------------------------------------------------- #67
GOVERNANCE_SECTIONS = (
    "Optimierungs-Freigaben",
    "Guardrail-Pflicht",
    "Re-Baseline-Kalender",
    "Change-Protokoll",
)


def check_governance():
    """#67 — Governance checks. Activated when the doc exists."""
    path = os.path.join(ROOT, "docs", "SCORE-GOVERNANCE.md")
    if not os.path.isfile(path):
        return  # not introduced yet (#67)
    text = read("docs/SCORE-GOVERNANCE.md")
    for section in GOVERNANCE_SECTIONS:
        check(section in text,
              f"SCORE-GOVERNANCE.md: Pflicht-Abschnitt '{section}' fehlt")


# ---------------------------------------------------------------- #68
def check_evals():
    """#68 — Evals mapping checks. Activated when the doc exists."""
    path = os.path.join(ROOT, "docs", "EVALS.md")
    if not os.path.isfile(path):
        return  # not introduced yet (#68)
    text = read("docs/EVALS.md")

    eval_files = sorted(
        os.path.basename(p)
        for p in glob.glob(os.path.join(ROOT, "eval", "*.py"))
        + glob.glob(os.path.join(ROOT, "eval", "*.jsonl"))
    )
    test_files = sorted(
        os.path.basename(p)
        for p in glob.glob(os.path.join(ROOT, "tests", "test_*.py"))
    )
    for name in eval_files + test_files:
        check(name in text,
              f"EVALS.md: Datei {name} ist keiner Ebene (L1/L2/L3) zugeordnet")


def main() -> int:
    check_methodology_doc()
    check_adrs()
    check_governance()
    check_evals()
    if errors:
        print("FAIL — check_methodology:")
        for e in errors:
            print(f"  - {e}")
        return 1
    print("OK — METHODOLOGY.md, ADRs (falls vorhanden), "
          "SCORE-GOVERNANCE.md (falls vorhanden), EVALS.md (falls vorhanden) "
          "konsistent.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
