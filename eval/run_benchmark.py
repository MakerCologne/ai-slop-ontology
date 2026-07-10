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
    for item in items:
        score = score_fn(item["text"])
        predicted_slop = score >= threshold
        actual_slop = item["label"] == "slop"
        lang = item.get("lang", "?")
        stats = by_lang.setdefault(lang, {"correct": 0, "total": 0})
        stats["total"] += 1
        if predicted_slop == actual_slop:
            stats["correct"] += 1
        if predicted_slop and actual_slop:
            tp += 1
        elif predicted_slop and not actual_slop:
            fp += 1
            errors.append({"id": item["id"], "kind": "false_positive", "score": round(score, 3)})
        elif not predicted_slop and actual_slop:
            fn += 1
            errors.append({"id": item["id"], "kind": "false_negative", "score": round(score, 3)})
        else:
            tn += 1

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
        "per_language_accuracy": {
            lang: round(s["correct"] / s["total"], 3) for lang, s in sorted(by_lang.items())
        },
        "errors": errors,
    }


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
    args = parser.parse_args()

    results = run(args.corpus, args.threshold)
    if args.json:
        print(json.dumps(results, indent=2))
    else:
        print(format_report(results))
