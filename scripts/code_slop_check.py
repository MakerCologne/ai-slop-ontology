#!/usr/bin/env python3
"""CLI for code-slop detection (issue #9).

Decision (documented per issue spec): separate script instead of
`slop_scorer.py --code` — code slop is detect-only and must have NO
dependency on (or influence on) the text scorer, so it gets its own entry
point. Exit codes: 0 = no findings, 1 = findings, 2 = usage error.

Usage:
    python3 scripts/code_slop_check.py --file path/to/source.ts
    python3 scripts/code_slop_check.py --file path/to/test_x.py --json
"""

import argparse
import json
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, "skills", "ai-slop-detection", "scripts"))

from code_slop import analyze_code  # noqa: E402


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--file", required=True, help="source file to analyze")
    parser.add_argument("--json", action="store_true", help="JSON output")
    args = parser.parse_args()

    if not os.path.isfile(args.file):
        print(f"Error: no such file: {args.file}", file=sys.stderr)
        return 2

    with open(args.file, encoding="utf-8", errors="replace") as f:
        source = f.read()

    result = analyze_code(source)
    if args.json:
        print(json.dumps(result, indent=2))
    else:
        if not result["findings"]:
            print(f"{args.file}: no code-slop findings")
        for finding in result["findings"]:
            print(f"{args.file}:{finding['line']}: [{finding['id']}] "
                  f"{finding['evidence']} — {finding['hint']}")
    return 1 if result["findings"] else 0


if __name__ == "__main__":
    sys.exit(main())
