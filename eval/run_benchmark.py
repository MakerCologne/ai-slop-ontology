#!/usr/bin/env python3
"""
Benchmark runner for the AI-slop detection engines.

Evaluates both engines against the labeled corpus (eval/corpus.jsonl):
  - skill scorer   (skills/ai-slop-detection/scripts/slop_scorer.py)
  - src classifier (src/classifier.py + ontology.json)

Usage:
    python3 eval/run_benchmark.py
    python3 eval/run_benchmark.py --threshold 0.40 --json
    python3 eval/run_benchmark.py --corpus path/to/other.jsonl
"""

import argparse
import json
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, "src"))
sys.path.insert(0, os.path.join(ROOT, "skills", "ai-slop-detection", "scripts"))

import slop_scorer  # skill engine
import slop_classifier as skill_classifier  # skill type classifier
from classifier import SlopClassifier  # src engine

DEFAULT_CORPUS = os.path.join(ROOT, "eval", "corpus.jsonl")
DEFAULT_THRESHOLD = 0.40


def load_corpus(path: str) -> list:
    items = []
    with open(path) as f:
        for line in f:
            line = line.strip()
            if line:
                items.append(json.loads(line))
    return items


def evaluate(name: str, score_fn, items: list, threshold: float) -> dict:
    tp = fp = tn = fn = 0
    errors = []
    by_lang = {}
    by_genre = {}
    for item in items:
        score = score_fn(item["text"])
        predicted_slop = score >= threshold
        actual_slop = item["label"] == "slop"
        lang = item.get("lang", "?")
        stats = by_lang.setdefault(lang, {"correct": 0, "total": 0})
        stats["total"] += 1
        # Issue #41: genre breakdown — FP rate per genre (hard-negative
        # genres like legal/academic/recipe show where the scorer
        # over-fires). Lines without a genre are grouped as "unspecified".
        genre = item.get("genre") or "unspecified"
        g = by_genre.setdefault(genre, {"n": 0, "n_clean": 0, "n_slop": 0,
                                        "tp": 0, "fp": 0, "tn": 0, "fn": 0})
        g["n"] += 1
        if predicted_slop == actual_slop:
            stats["correct"] += 1
        if predicted_slop and actual_slop:
            tp += 1
            g["tp"] += 1
        elif predicted_slop and not actual_slop:
            fp += 1
            g["fp"] += 1
            errors.append({"id": item["id"], "kind": "false_positive", "score": round(score, 3)})
        elif not predicted_slop and actual_slop:
            fn += 1
            g["fn"] += 1
            errors.append({"id": item["id"], "kind": "false_negative", "score": round(score, 3)})
        else:
            tn += 1
            g["tn"] += 1
        if actual_slop:
            g["n_slop"] += 1
        else:
            g["n_clean"] += 1

    precision = tp / (tp + fp) if tp + fp else 0.0
    recall = tp / (tp + fn) if tp + fn else 0.0
    f1 = 2 * precision * recall / (precision + recall) if precision + recall else 0.0
    accuracy = (tp + tn) / len(items) if items else 0.0
    return {
        "engine": name,
        "threshold": threshold,
        "n": len(items),
        "tp": tp, "fp": fp, "tn": tn, "fn": fn,
        "precision": round(precision, 3),
        "recall": round(recall, 3),
        "f1": round(f1, 3),
        "accuracy": round(accuracy, 3),
        # Unrounded companions. The reported figures are rounded for reading,
        # but a floor must be compared against the real value: a recall of
        # 989/999 = 0.98999 rounds to 0.990 and would slip past --min-recall
        # 0.99, which is exactly what the flag promises not to allow.
        "precision_exact": precision,
        "recall_exact": recall,
        "f1_exact": f1,
        "per_language_accuracy": {
            lang: round(s["correct"] / s["total"], 3) for lang, s in sorted(by_lang.items())
        },
        "per_genre": genre_report(by_genre),
        "errors": errors,
    }


def genre_report(by_genre: dict) -> dict:
    """Per-genre stats; fp_rate is only reported for genres that have
    clean (hard-negative) items — an fp rate without negatives is
    undefined, not zero."""
    report = {}
    for genre, g in sorted(by_genre.items()):
        entry = {"n": g["n"], "n_clean": g["n_clean"], "n_slop": g["n_slop"],
                 "tp": g["tp"], "fp": g["fp"], "tn": g["tn"], "fn": g["fn"]}
        if g["n_clean"] > 0:
            entry["fp_rate"] = round(g["fp"] / g["n_clean"], 3)
        if g["n_slop"] > 0:
            entry["fn_rate"] = round(g["fn"] / g["n_slop"], 3)
        report[genre] = entry
    return report


def run(corpus_path: str = DEFAULT_CORPUS, threshold: float = DEFAULT_THRESHOLD) -> list:
    items = load_corpus(corpus_path)
    clf = SlopClassifier(os.path.join(ROOT, "ontology.json"))

    def skill_pipeline(text: str) -> float:
        # The pipeline documented in SKILL.md: run the scorer AND the type
        # classifier; the stronger verdict wins. Type patterns catch slop the
        # dimension scorer is blind to (workslop, security reports, reviews).
        return max(slop_scorer.slop_score(text)["slop_score"],
                   skill_classifier.classify_text(text).score)

    return [
        evaluate("skill-scorer", lambda t: slop_scorer.slop_score(t)["slop_score"],
                 items, threshold),
        evaluate("src-classifier", lambda t: clf.classify_text(t).overall_slop_score,
                 items, threshold),
        evaluate("skill-pipeline (scorer+classifier)", skill_pipeline,
                 items, threshold),
    ]


def format_report(results: list) -> str:
    lines = []
    for r in results:
        lines.append(f"=== {r['engine']} (threshold {r['threshold']}, n={r['n']}) ===")
        lines.append(f"  Precision: {r['precision']}   Recall: {r['recall']}   "
                     f"F1: {r['f1']}   Accuracy: {r['accuracy']}")
        lines.append(f"  Confusion: TP={r['tp']} FP={r['fp']} TN={r['tn']} FN={r['fn']}")
        lines.append(f"  Per language: " + ", ".join(
            f"{lang}={acc}" for lang, acc in r["per_language_accuracy"].items()))
        lines.append("  Per genre FP rate (clean items): " + ", ".join(
            f"{genre}={stats.get('fp_rate', 'n/a')}"
            f"({stats['fp']}/{stats['n_clean']})"
            for genre, stats in r["per_genre"].items() if stats["n_clean"] > 0))
        if r["errors"]:
            lines.append("  Misclassified:")
            for e in r["errors"]:
                lines.append(f"    {e['kind']:>15}  {e['id']}  (score {e['score']})")
        lines.append("")
    return "\n".join(lines)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--corpus", default=DEFAULT_CORPUS)
    parser.add_argument("--threshold", type=float, default=DEFAULT_THRESHOLD)
    parser.add_argument("--json", action="store_true")
    parser.add_argument(
        "--min-precision", type=float, default=None, metavar="P",
        help="fail (exit 1) when the pipeline's precision falls below P. "
             "Without it the run stays a report (#84).")
    parser.add_argument(
        "--min-recall", type=float, default=None, metavar="R",
        help="fail (exit 1) when the pipeline's recall falls below R.")
    parser.add_argument(
        "--engine", default="skill-pipeline (scorer+classifier)",
        help="engine the floors apply to (default: the documented pipeline)")
    args = parser.parse_args()

    results = run(args.corpus, args.threshold)
    if args.json:
        print(json.dumps(results, indent=2))
    else:
        print(format_report(results))

    # Floors are opt-in: the bare report is still just a report, so local runs
    # and exploratory corpora are unaffected. CI passes them (#84).
    if args.min_precision is None and args.min_recall is None:
        sys.exit(0)

    gated = next((r for r in results if r["engine"] == args.engine), None)
    if gated is None:
        print(f"error: no engine named {args.engine!r} in the results",
              file=sys.stderr)
        sys.exit(2)

    breaches = []
    # Gate on the unrounded values; report the rounded ones.
    if args.min_precision is not None and \
            gated["precision_exact"] < args.min_precision:
        breaches.append(
            f"precision {gated['precision_exact']:.6g} < floor {args.min_precision}")
    if args.min_recall is not None and gated["recall_exact"] < args.min_recall:
        breaches.append(
            f"recall {gated['recall_exact']:.6g} < floor {args.min_recall}")
    if breaches:
        print(f"BENCHMARK GATE FAILED ({args.engine}): " + "; ".join(breaches),
              file=sys.stderr)
        sys.exit(1)
    print(f"BENCHMARK GATE PASSED ({args.engine}): "
          f"precision {gated['precision_exact']:.6g}, "
          f"recall {gated['recall_exact']:.6g}")
