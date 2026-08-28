#!/usr/bin/env python3
"""
Calibrate the skill scorer's dimension weights against a labeled corpus.

Runs coordinate ascent over the scorer's dimension weights (plus the buzzword and
phrase normalization divisors), maximizing F1 at the decision threshold while
keeping precision above a floor (default 0.95) so the tuned engine does not
start flagging human text.

Default corpus: eval/corpus.jsonl. To calibrate against the Shaib et al.
dataset (github.com/cshaib/slop), export it to JSONL with the fields
{"id", "label": "slop"|"clean", "text"} and pass --corpus.

Usage:
    python3 eval/calibrate.py
    python3 eval/calibrate.py --corpus shaib.jsonl --precision-floor 0.9
    python3 eval/calibrate.py --json           # machine-readable result
"""

import argparse
import json
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, "skills", "ai-slop-detection", "scripts"))

import slop_scorer

DEFAULT_CORPUS = os.path.join(ROOT, "eval", "corpus.jsonl")
THRESHOLD = 0.40

# Read from the scorer, not copied. The previous hardcoded list held 13 names
# while the scorer had grown a 14th (`portability`, #14), so slop_score raised
# KeyError on every call and this script could not run at all — the script the
# shipped weights cite as their provenance. Same defect class as #88.
WEIGHT_KEYS = sorted(slop_scorer.DEFAULT_WEIGHTS)
CANDIDATE_VALUES = [0.0, 0.02, 0.04, 0.06, 0.08, 0.10, 0.12, 0.15, 0.18, 0.22, 0.26, 0.30]


def load_corpus(path: str) -> list:
    items = []
    with open(path) as f:
        for line in f:
            line = line.strip()
            if line:
                items.append(json.loads(line))
    return items


def metrics(weights: dict, items: list, threshold: float = THRESHOLD) -> dict:
    tp = fp = tn = fn = 0
    for item in items:
        score = slop_scorer.slop_score(item["text"], weights=weights)["slop_score"]
        predicted = score >= threshold
        actual = item["label"] == "slop"
        if predicted and actual:
            tp += 1
        elif predicted:
            fp += 1
        elif actual:
            fn += 1
        else:
            tn += 1
    precision = tp / (tp + fp) if tp + fp else 1.0
    recall = tp / (tp + fn) if tp + fn else 0.0
    f1 = 2 * precision * recall / (precision + recall) if precision + recall else 0.0
    return {"precision": precision, "recall": recall, "f1": f1,
            "tp": tp, "fp": fp, "tn": tn, "fn": fn}


def objective(m: dict, precision_floor: float) -> float:
    # F1, but hard-penalize configurations that flag human text
    if m["precision"] < precision_floor:
        return m["f1"] - 1.0
    return m["f1"]


def calibrate(items: list, precision_floor: float = 0.95,
              rounds: int = 3, verbose: bool = True,
              initial_weights: dict = None,
              threshold: float = THRESHOLD) -> dict:
    """Coordinate ascent over the scorer's dimension weights.

    `initial_weights` defaults to the shipped weights — read from the scorer,
    so a new dimension cannot silently drop out of the search. A caller that
    must not inherit what those weights already know about the corpus (the
    cross-validation in run_benchmark.py, #85) passes its own starting point:
    ascent moves a weight only on strict improvement, so a dimension the
    previous fit already placed well simply stays put, and the fit travels
    into the result through the initialization even when the ascent itself
    never sees the held-out texts.
    """
    weights = dict(slop_scorer.DEFAULT_WEIGHTS if initial_weights is None
                   else initial_weights)
    missing = set(WEIGHT_KEYS) - set(weights)
    if missing:
        raise ValueError(
            f"initial_weights is missing {sorted(missing)} — the scorer would "
            f"raise KeyError on the first call")
    best = metrics(weights, items, threshold)
    best_score = objective(best, precision_floor)
    if verbose:
        print(f"start: F1={best['f1']:.3f} P={best['precision']:.3f} "
              f"R={best['recall']:.3f}")

    for rnd in range(rounds):
        improved = False
        for key in WEIGHT_KEYS:
            for value in CANDIDATE_VALUES:
                if value == weights[key]:
                    continue
                trial = dict(weights)
                trial[key] = value
                m = metrics(trial, items, threshold)
                s = objective(m, precision_floor)
                if s > best_score + 1e-9:
                    weights, best, best_score = trial, m, s
                    improved = True
                    if verbose:
                        print(f"round {rnd + 1}: {key}={value}  "
                              f"F1={m['f1']:.3f} P={m['precision']:.3f} "
                              f"R={m['recall']:.3f}")
        if not improved:
            break

    return {"weights": weights, "metrics": {k: round(v, 3) if isinstance(v, float) else v
                                            for k, v in best.items()}}


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--corpus", default=DEFAULT_CORPUS)
    parser.add_argument("--precision-floor", type=float, default=0.95)
    parser.add_argument("--rounds", type=int, default=3)
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args()

    items = load_corpus(args.corpus)
    result = calibrate(items, args.precision_floor, args.rounds,
                       verbose=not args.json)
    if args.json:
        print(json.dumps(result, indent=2))
    else:
        print("\nCalibrated weights:")
        for k, v in result["weights"].items():
            print(f"  {k}: {v}")
        m = result["metrics"]
        print(f"\nFinal: F1={m['f1']} P={m['precision']} R={m['recall']} "
              f"(TP={m['tp']} FP={m['fp']} TN={m['tn']} FN={m['fn']})")
