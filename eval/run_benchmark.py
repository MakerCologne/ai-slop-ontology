#!/usr/bin/env python3
"""
Benchmark runner for the AI-slop detection engines.

Evaluates both engines against the labeled corpus (eval/corpus.jsonl):
  - skill scorer   (skills/ai-slop-detection/scripts/slop_scorer.py)
  - src classifier (src/classifier.py + ontology.json)

**The default run is in-sample.** The skill scorer's dimension weights were
tuned by eval/calibrate.py on this very corpus, so its headline F1 is a
training-set number and is reported as such (review 2026-08 §2.3). Use
--cross-validate for a held-out estimate: the weights are re-calibrated on
k-1 folds and scored on the fold left out.

Usage:
    python3 eval/run_benchmark.py
    python3 eval/run_benchmark.py --threshold 0.40 --json
    python3 eval/run_benchmark.py --corpus path/to/other.jsonl
    python3 eval/run_benchmark.py --cross-validate 5     # held-out estimate
"""

import argparse
import json
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, "src"))
sys.path.insert(0, os.path.join(ROOT, "skills", "ai-slop-detection", "scripts"))
sys.path.insert(0, os.path.join(ROOT, "eval"))

import slop_scorer  # skill engine
import slop_classifier as skill_classifier  # skill type classifier
from classifier import SlopClassifier  # src engine

DEFAULT_CORPUS = os.path.join(ROOT, "eval", "corpus.jsonl")
DEFAULT_THRESHOLD = 0.40
# Below this many examples a per-language accuracy is not reported at all.
MIN_LANG_N = 5


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
        # A per-language number over two sentences is noise, not evidence;
        # report the sample size and withhold the ratio below MIN_LANG_N.
        "per_language_accuracy": {
            lang: (round(s["correct"] / s["total"], 3)
                   if s["total"] >= MIN_LANG_N else None)
            for lang, s in sorted(by_lang.items())
        },
        "per_language_n": {lang: s["total"] for lang, s in sorted(by_lang.items())},
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


def cross_validate(corpus_path: str = DEFAULT_CORPUS,
                   threshold: float = DEFAULT_THRESHOLD,
                   folds: int = 5) -> list:
    """Held-out estimate for the calibrated skill scorer.

    Stratified k-fold: recalibrate the dimension weights on k-1 folds, score
    the remaining fold with those weights. This is what the tuned engine is
    worth on text it was not fitted to.
    """
    import calibrate as calibration

    items = load_corpus(corpus_path)
    slop = [i for i in items if i["label"] == "slop"]
    clean = [i for i in items if i["label"] != "slop"]
    buckets = [[] for _ in range(folds)]
    offset = 0
    for group in (slop, clean):                      # stratified, deterministic
        for n, item in enumerate(group):
            buckets[(n + offset) % folds].append(item)
        # Continue where the previous stratum stopped, so the remainders do not
        # pile into the same folds and leave the last one short.
        offset = (offset + len(group)) % folds

    clf = SlopClassifier(os.path.join(ROOT, "ontology.json"))
    scorer_folds, pipeline_folds = [], []
    for k in range(folds):
        test = buckets[k]
        train = [i for j, b in enumerate(buckets) if j != k for i in b]
        tuned = calibration.calibrate(train, verbose=False)["weights"]

        def scored(t, w=tuned):
            return slop_scorer.slop_score(t, weights=w)["slop_score"]

        def piped(t, w=tuned):
            # Same composition as the shipped pipeline: the classifier is not
            # fitted to the corpus, only the scorer's weights are.
            return max(scored(t, w), skill_classifier.classify_text(t).score)

        scorer_folds.append(evaluate(f"fold {k + 1}", scored, test, threshold))
        pipeline_folds.append(evaluate(f"fold {k + 1}", piped, test, threshold))

    def summarize(name, per_fold):
        def mean(key):
            return round(sum(r[key] for r in per_fold) / len(per_fold), 3)
        return {
            "engine": f"{name}, {folds}-fold cross-validated",
            "folds": folds,
            "n": sum(r["n"] for r in per_fold),
            "precision": mean("precision"),
            "recall": mean("recall"),
            "f1": mean("f1"),
            "accuracy": mean("accuracy"),
            "per_fold_f1": [r["f1"] for r in per_fold],
        }

    return [summarize("skill-scorer", scorer_folds),
            summarize("skill-pipeline (scorer+classifier)", pipeline_folds)]


def format_report(results: list) -> str:
    lines = ["NOTE: in-sample — the skill scorer's weights were calibrated on "
             "this corpus.", "      Run with --cross-validate for a held-out "
             "estimate.", ""]
    for r in results:
        lines.append(f"=== {r['engine']} (threshold {r['threshold']}, n={r['n']}) ===")
        lines.append(f"  Precision: {r['precision']}   Recall: {r['recall']}   "
                     f"F1: {r['f1']}   Accuracy: {r['accuracy']}")
        lines.append(f"  Confusion: TP={r['tp']} FP={r['fp']} TN={r['tn']} FN={r['fn']}")
        lines.append("  Per language: " + ", ".join(
            f"{lang}={acc}" if acc is not None
            else f"{lang}=n/a (n={r['per_language_n'][lang]})"
            for lang, acc in r["per_language_accuracy"].items()))
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
    parser.add_argument("--cross-validate", nargs="?", type=int, const=5,
                        default=None, metavar="K",
                        help="also report a K-fold held-out estimate (default 5)")
    args = parser.parse_args()

    results = run(args.corpus, args.threshold)
    cv = (cross_validate(args.corpus, args.threshold, args.cross_validate)
          if args.cross_validate else None)

    if args.json:
        print(json.dumps({"in_sample": results, "cross_validated": cv}, indent=2))
    else:
        print(format_report(results))
        for r in cv or []:
            print(f"=== {r['engine']} (threshold {args.threshold}, n={r['n']}) ===")
            print(f"  Precision: {r['precision']}   Recall: {r['recall']}   "
                  f"F1: {r['f1']}   Accuracy: {r['accuracy']}")
            print(f"  Per fold F1: {', '.join(str(f) for f in r['per_fold_f1'])}")
            print()
