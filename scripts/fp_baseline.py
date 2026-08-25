#!/usr/bin/env python3
"""
FP-Baseline-Register (issue #80).

Pins the tolerated detector outputs (slop_score + sub-threshold signal
hits) for every hard-negative (label=clean) fixture of eval/corpus.jsonl
into eval/fp_baseline.json, and snapshot-compares them in CI.

Drift model (all relative to the COMMITTED baseline):
  signal_added     a signal fires on a hard negative that the baseline
                   does not tolerate — FP pressure BEFORE threshold breach
  signal_removed   a tolerated output vanished (silent behavior change)
  score_drift      |Δ slop_score| > SCORE_TOLERANCE on a hard negative
  fixture_missing  corpus clean fixture has no baseline entry
  fixture_unknown  baseline entry without a corpus fixture

Usage:
    python3 scripts/fp_baseline.py            # write/update the baseline
    python3 scripts/fp_baseline.py --check    # CI gate: exit 1 on drift
        [--baseline PATH]                     # compare against another copy
"""

import argparse
import json
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, "skills", "ai-slop-detection", "scripts"))

import slop_scorer  # noqa: E402

CORPUS = os.path.join(ROOT, "eval", "corpus.jsonl")
DEFAULT_BASELINE = os.path.join(ROOT, "eval", "fp_baseline.json")
SCORE_TOLERANCE = 0.02  # matched to the #79 borderline register band
SCHEMA_VERSION = 1


def _score_fn(text: str) -> dict:
    return slop_scorer.slop_score(text)


def _fixture_entry(result: dict) -> dict:
    """Tolerated outputs of one fixture: rounded score + sorted signal hits
    (buzzword hits and 'category:phrase' pairs, canonical order)."""
    signals = sorted(result.get("signals", {}).get("buzzword_hits", []))
    for cat, phrases in sorted((result.get("signals", {})
                                .get("phrase_categories", {})).items()):
        signals.extend(f"{cat}:{p}" for p in sorted(phrases))
    return {"slop_score": round(result["slop_score"], 3),
            "signals": sorted(set(signals))}


def build_baseline(corpus_path: str = CORPUS) -> dict:
    fixtures = {}
    with open(corpus_path, encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            item = json.loads(line)
            if item.get("label") != "clean":
                continue
            fixtures[item["id"]] = _fixture_entry(_score_fn(item["text"]))
    return {
        "schema": SCHEMA_VERSION,
        "generated_from": os.path.relpath(corpus_path, ROOT),
        "engine": "skills/ai-slop-detection/scripts/slop_scorer.py",
        "score_tolerance": SCORE_TOLERANCE,
        "note": ("Tolerated detector outputs per hard-negative fixture "
                 "(issue #80). CI: scripts/fp_baseline.py --check fails on "
                 "new signals or score drift beyond tolerance — FP pressure "
                 "becomes visible before the 0.40 gate breaks."),
        "fixtures": dict(sorted(fixtures.items())),
    }


def drift_report(committed: dict, current: dict) -> list:
    """Full drift list between two baselines (committed -> current)."""
    return compare_baselines(committed, current)


def compare_baselines(committed: dict, current: dict) -> list:
    drift = []
    c_fix, n_fix = committed.get("fixtures", {}), current.get("fixtures", {})
    for fid in sorted(set(c_fix) | set(n_fix)):
        if fid not in c_fix:
            drift.append({"type": "fixture_unknown", "fixture": fid})
            continue
        if fid not in n_fix:
            drift.append({"type": "fixture_missing", "fixture": fid})
            continue
        old, new = c_fix[fid], n_fix[fid]
        for sig in sorted(set(new["signals"]) - set(old["signals"])):
            drift.append({"type": "signal_added", "fixture": fid,
                          "signal": sig})
        for sig in sorted(set(old["signals"]) - set(new["signals"])):
            drift.append({"type": "signal_removed", "fixture": fid,
                          "signal": sig})
        if abs(new["slop_score"] - old["slop_score"]) > SCORE_TOLERANCE:
            drift.append({"type": "score_drift", "fixture": fid,
                          "committed": old["slop_score"],
                          "current": new["slop_score"]})
    return drift


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[1])
    ap.add_argument("--check", action="store_true",
                    help="compare the committed baseline against a fresh "
                         "build; exit 1 on drift")
    ap.add_argument("--baseline", default=DEFAULT_BASELINE,
                    help="baseline file to check against (default: "
                         "eval/fp_baseline.json)")
    args = ap.parse_args()

    if args.check:
        with open(args.baseline, encoding="utf-8") as f:
            committed = json.load(f)
        drift = compare_baselines(committed, build_baseline())
        if drift:
            print(f"FP-BASELINE DRIFT ({len(drift)} finding(s)):")
            for d in drift[:20]:
                print(" ", json.dumps(d, ensure_ascii=False))
            if len(drift) > 20:
                print(f"  ... and {len(drift) - 20} more")
            return 1
        print("fp-baseline check passed (no drift against committed register)")
        return 0

    baseline = build_baseline()
    with open(args.baseline, "w", encoding="utf-8") as f:
        json.dump(baseline, f, indent=2, ensure_ascii=False)
        f.write("\n")
    print(f"wrote {args.baseline} ({len(baseline['fixtures'])} fixtures)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
