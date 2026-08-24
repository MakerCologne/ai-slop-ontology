#!/usr/bin/env python3
"""
Control-set gate for the AI-slop skill scorer (MS-I1).

Scores eval/control_set.jsonl (10 handwritten texts, 5 slop / 5 hard
negatives) and enforces:

  - every slop item (except entries marked "known_fn": true) >= 0.40
  - every clean item < 0.40

Known false negatives are listed as KNOWN-FN and keep the gate green —
each carries a documented ticket note. If a known FN starts passing,
it is reported as RESOLVED. Any unexpected result fails the gate (exit 1).

Usage:
    python3 eval/run_control_set.py
    python3 eval/run_control_set.py --threshold 0.40
"""

import argparse
import json
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, "skills", "ai-slop-detection", "scripts"))

import slop_scorer  # noqa: E402

DEFAULT_CONTROL_SET = os.path.join(ROOT, "eval", "control_set.jsonl")


def load_control_set(path: str) -> list:
    items = []
    with open(path) as f:
        for line in f:
            if line.strip():
                items.append(json.loads(line))
    return items


def run_gate(items: list, threshold: float) -> int:
    failures = []
    known_fns = []
    resolved = []
    for item in items:
        score = slop_scorer.slop_score(item["text"])["slop_score"]
        is_slop = item["label"] == "slop"
        expected_flag = is_slop and not item.get("known_fn")
        flagged = score >= threshold
        status = "ok"
        if item.get("known_fn") and is_slop:
            if flagged:
                status = "KNOWN-FN resolved"
                resolved.append((item["id"], score))
            else:
                status = "KNOWN-FN"
                known_fns.append((item["id"], score, item.get("note", "")))
        elif expected_flag and not flagged:
            status = "FAIL (false negative)"
            failures.append((item["id"], score, "expected slop >= threshold"))
        elif not is_slop and flagged:
            status = "FAIL (false positive)"
            failures.append((item["id"], score, "expected clean < threshold"))
        print(f"  {item['id']:<16} {item['label']:<6} score={score:<6} {status}")

    print()
    if known_fns:
        print(f"Known false negatives ({len(known_fns)}, documented, gate stays green):")
        for iid, score, note in known_fns:
            print(f"  KNOWN-FN {iid}: {score:.3f} — {note}")
    if resolved:
        print(f"Resolved known FNs: {[r[0] for r in resolved]}")
    if failures:
        print(f"GATE FAILED: {len(failures)} unexpected result(s)")
        for iid, score, why in failures:
            print(f"  {iid}: {score:.3f} — {why}")
        return 1
    print("GATE PASSED")
    return 0


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--control-set", default=DEFAULT_CONTROL_SET)
    parser.add_argument("--threshold", type=float, default=0.40)
    args = parser.parse_args()
    items = load_control_set(args.control_set)
    print(f"Control set: {args.control_set} (n={len(items)}, threshold={args.threshold})")
    sys.exit(run_gate(items, args.threshold))


if __name__ == "__main__":
    main()
