#!/usr/bin/env python3
"""
Issue #49 — generate a data-only Python view of ontology.json.

ontology.json is the source of truth. This script projects the parts the
detection tooling may want to read at import time into
src/signal_defs_generated.py — pure data (dicts/lists/strings), no code,
no behavior. Regenerate after every ontology.json change and commit the
result; scripts/check_ssot.py fails CI when the committed file is stale.

Usage:
    python3 scripts/generate_signal_defs.py            # write src/...
    python3 scripts/generate_signal_defs.py --stdout   # print instead
"""

import argparse
import json
import os

ROOT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..")
ONTOLOGY = os.path.join(ROOT, "ontology.json")
TARGET = os.path.join(ROOT, "src", "signal_defs_generated.py")

HEADER = '''"""
GENERATED FILE — DO NOT EDIT BY HAND.

Data-only projection of ontology.json (source of truth), produced by
scripts/generate_signal_defs.py (issue #49). Regenerate with:

    python3 scripts/generate_signal_defs.py

No code, no detection behavior. Detection modules still carry their
corpus-calibrated inline lists (see scripts/check_ssot.py for the
register of conscious deviations); full migration onto this view is a
documented follow-up, not part of #49.
"""
'''


def build_defs(ontology: dict) -> dict:
    """Select the subtrees relevant to detection tooling — data only."""
    return {
        "ONTOLOGY_DATE": ontology.get("dc:date", ""),
        "ONTOLOGY_TITLE": ontology.get("dc:title", ""),
        "SLOP_TYPES": sorted(ontology.get("slopTypes", {}).keys()),
        "DETECTION_SIGNALS_STRUCTURED": ontology.get(
            "detectionSignalsStructured", {}
        ),
        "RHETORICAL_PATTERNS": sorted(
            (ontology.get("signals", {}).get("rhetoricalPatterns", {})
             or {}).keys()
        ) if isinstance(ontology.get("signals", {}).get(
            "rhetoricalPatterns", {}), dict) else [],
        "COUNTERMEASURES": sorted(ontology.get("countermeasures", {}).keys()),
    }


def render(defs: dict) -> str:
    lines = [HEADER]
    for key in sorted(defs):
        lines.append(f"{key} = {json.dumps(defs[key], indent=2, sort_keys=True, ensure_ascii=False)}")
        lines.append("")
    return "\n".join(lines)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--stdout", action="store_true",
                        help="print the generated module instead of writing it")
    args = parser.parse_args()

    with open(ONTOLOGY, encoding="utf-8") as fh:
        ontology = json.load(fh)
    content = render(build_defs(ontology))

    if args.stdout:
        print(content)
        return 0
    with open(TARGET, "w", encoding="utf-8") as fh:
        fh.write(content)
    print(f"wrote {os.path.relpath(TARGET, ROOT)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
