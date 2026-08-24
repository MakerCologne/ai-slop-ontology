#!/usr/bin/env python3
"""
Signal-Definition-of-Done checker (#64).

Scans signal modules under skills/ai-slop-detection/scripts/ against the
8-point checklist in docs/SIGNAL-DOD.md using offline heuristics:

  - Test-Datei: wird das Modul von irgendeiner Datei in tests/ referenziert?
  - keep_when-Doku: enthaelt das Modul (oder SKILL.md) keep_when-Guards?
  - SKILL.md-Referenz: wird das Modul in SKILL.md erwaehnt?

Default mode REPORTS (exit 0) — gaps are visible, not blocking.
--strict exits 1 on FAIL-level findings (missing test coverage).

Usage:
    python3 scripts/check_signal_dod.py [--strict]
        [--scripts-dir DIR] [--tests-dir DIR] [--skill-md FILE]
"""

import argparse
import glob
import os
import re
import sys
from dataclasses import dataclass, field

# Non-signal infrastructure modules (scorer core, plumbing) — checked for
# tests only, not for signal-DoD heuristics.
INFRA_MODULES = {
    "slop_scorer",
    "slop_classifier",
    "fp_guards",
    "tokenizer",
    "input_norm",
    "genre_profiles",
    "learning_store",
    "generated_docs",
    "diff_mode",
}

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


@dataclass
class SignalReport:
    module: str
    infra: bool = False
    failures: list = field(default_factory=list)   # DoD MUST-Verstoesse
    warnings: list = field(default_factory=list)   # dokumentationsluecken

    @property
    def ok(self) -> bool:
        return not self.failures and not self.warnings


def scan_signals(scripts_dir: str, tests_dir: str, skill_md: str):
    skill_text = ""
    if os.path.isfile(skill_md):
        with open(skill_md, encoding="utf-8") as f:
            skill_text = f.read()

    test_texts = {}
    for p in glob.glob(os.path.join(tests_dir, "test_*.py")):
        try:
            with open(p, encoding="utf-8") as f:
                test_texts[os.path.basename(p)] = f.read()
        except OSError:
            pass

    reports = []
    for path in sorted(glob.glob(os.path.join(scripts_dir, "*.py"))):
        name = os.path.basename(path)[:-3]
        if name.startswith("_") or name == "__init__":
            continue
        try:
            with open(path, encoding="utf-8") as f:
                src = f.read()
        except OSError:
            continue

        r = SignalReport(module=name, infra=name in INFRA_MODULES)
        has_test = any(name in t for t in test_texts.values())
        if not has_test:
            r.failures.append(
                "DoD #1 Test-Oracle: keine Test-Datei in "
                f"{os.path.basename(tests_dir)}/ referenziert '{name}'"
            )
        if r.infra:
            reports.append(r)
            continue

        # Heuristiken fuer Signal-Module
        if "keep_when" not in src and "keep_when" not in skill_text:
            r.warnings.append(
                "DoD #2 FP-Abwaegung: keine keep_when-Doku in Modul/SKILL.md "
                "(auch 'kein Guard noetig' muss dokumentiert sein)"
            )
        if name not in skill_text:
            r.warnings.append(
                "DoD #3 SSOT/Referenz: Modul wird in SKILL.md nicht erwaehnt"
            )
        reports.append(r)
    return reports


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[1])
    ap.add_argument("--strict", action="store_true",
                    help="exit 1 bei FAIL-Findings (fehlende Tests)")
    ap.add_argument("--scripts-dir",
                    default=os.path.join(ROOT, "skills",
                                         "ai-slop-detection", "scripts"))
    ap.add_argument("--tests-dir", default=os.path.join(ROOT, "tests"))
    ap.add_argument("--skill-md",
                    default=os.path.join(ROOT, "skills",
                                         "ai-slop-detection", "SKILL.md"))
    args = ap.parse_args()

    reports = scan_signals(args.scripts_dir, args.tests_dir, args.skill_md)
    fails = sum(len(r.failures) for r in reports)
    warns = sum(len(r.warnings) for r in reports)

    print(f"Signal-DoD Report — {len(reports)} Module "
          f"({sum(1 for r in reports if r.infra)} Infra)")
    for r in reports:
        tag = "INFRA" if r.infra else ("OK  " if r.ok else "CHECK")
        print(f"[{tag}] {r.module}")
        for msg in r.failures:
            print(f"        FAIL  {msg}")
        for msg in r.warnings:
            print(f"        WARN  {msg}")
    print(f"\n{fails} FAIL, {warns} WARN — Details: docs/SIGNAL-DOD.md")

    if args.strict and fails:
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
