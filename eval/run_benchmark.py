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
import contextlib
import json
import os
import random
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, "src"))
sys.path.insert(0, os.path.join(ROOT, "skills", "ai-slop-detection", "scripts"))
sys.path.insert(0, os.path.join(ROOT, "eval"))

import calibrate  # weight calibration (L3) — also the source of the search grid
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


# --------------------------------------------------------------------------- #
# Cross-validation (issue #85)
#
# calibrate.py fits the scorer's 14 dimension weights on eval/corpus.jsonl and
# this file then reports on the same corpus, so the headline figure is an
# in-sample value. A held-out estimate needs the weights of each fold to be
# fitted without ever seeing that fold's texts.
#
# Only the dimension scorer is fitted. The type-pattern classifier is not, so
# its held-out number equals its in-sample number by construction — and the
# pipeline, which takes the stronger of the two, inherits that. Reporting the
# three together without saying which is which is how the overfit stayed
# invisible; the result therefore labels every engine.
# --------------------------------------------------------------------------- #

def _default_weights() -> dict:
    """The shipped weights, read from the scorer rather than copied (#85)."""
    return dict(slop_scorer.DEFAULT_WEIGHTS)


def neutral_weights() -> dict:
    """Corpus-independent starting point for a fold's calibration (#85).

    The shipped DEFAULT_WEIGHTS were fitted on the whole corpus — every fold's
    held-out texts included. Seeding a fold's coordinate ascent with them
    leaks that fit through the *initialization*, even though the ascent itself
    only ever sees the training part: ascent moves a weight only on strict
    improvement, so a dimension the full-corpus fit already placed well simply
    stays where the full corpus put it. The held-out number would then be
    measured against weights that had, indirectly, seen the text.

    Uniform mass 1/N is the uninformative alternative: every dimension counts
    equally and no text influenced the value. It is a worse starting point, so
    the held-out estimate it produces is a conservative one — which is the
    right direction for a number whose whole purpose is to stop flattering
    the engine.
    """
    keys = sorted(slop_scorer.DEFAULT_WEIGHTS)
    return {key: 1.0 / len(keys) for key in keys}


FITTED_ENGINES = ["skill-scorer"]
UNFITTED_ENGINES = ["src-classifier"]
MIXED_ENGINES = ["skill-pipeline (scorer+classifier)"]


def engine_kind(name: str) -> str:
    """fitted / unfitted / mixed — and a hard error for anything unclassified.

    An engine added to the benchmark without being classified would otherwise
    be printed next to a held-out figure that means nothing for it. Refusing
    to guess is the point: guessing is what produced the in-sample headline.
    """
    if name in FITTED_ENGINES:
        return "fitted"
    if name in UNFITTED_ENGINES:
        return "unfitted"
    if name in MIXED_ENGINES:
        return "mixed"
    raise KeyError(
        f"engine {name!r} is in neither FITTED_ENGINES, UNFITTED_ENGINES nor "
        f"MIXED_ENGINES — classify it before reporting a held-out number (#85)")


def make_folds(items: list, k: int, seed: int = 17) -> list:
    """k stratified, deterministic folds as [(train_idx, test_idx), ...].

    Stratified because a fold without both labels cannot be scored at all;
    deterministic because a benchmark that moves between runs cannot be
    compared against a previous one (docs/METHODOLOGY.md M8).
    """
    if not isinstance(k, int) or k < 2:
        raise ValueError(f"k must be an integer >= 2, got {k!r}")
    if k > len(items):
        raise ValueError(f"k={k} exceeds corpus size {len(items)}")

    by_label = {}
    for index, item in enumerate(items):
        by_label.setdefault(item.get("label"), []).append(index)

    # `evaluate` reads every label that is not "slop" as clean, so an unknown
    # or misspelled label does not fail — it silently becomes a clean item and
    # moves the precision. Insist on the two the benchmark actually defines.
    if set(by_label) != {"slop", "clean"}:
        raise ValueError(
            f"corpus labels are {sorted(map(str, by_label))} — cross-validation "
            f"needs exactly {{'slop', 'clean'}}; anything else is scored as "
            f"clean without saying so")

    # Round-robin dealing can only stratify while every class has at least one
    # item per fold. Past that, folds come out label-free and report a
    # vacuous P/R/F1 instead of failing — so fail here, where the cause is
    # still visible. Compare by count, not by the (label, count) tuple: tuple
    # order compares the label first, so a corpus with more clean than slop
    # items would pick "clean" for being alphabetically smaller.
    smallest_label = min(by_label, key=lambda label: len(by_label[label]))
    smallest = len(by_label[smallest_label])
    if k > smallest:
        raise ValueError(
            f"k={k} exceeds the smallest class ({smallest_label}: {smallest} "
            f"items) — folds could not be stratified")

    buckets = [[] for _ in range(k)]
    for label in sorted(by_label, key=lambda x: (x is None, x)):
        indices = list(by_label[label])
        random.Random(f"{seed}:{label}").shuffle(indices)
        # Deal round-robin so every fold gets its share of each label.
        for position, index in enumerate(indices):
            buckets[position % k].append(index)

    folds = []
    everything = set(range(len(items)))
    for bucket in buckets:
        test = sorted(bucket)
        folds.append((sorted(everything - set(test)), test))
    return folds


def random_start(fold: int, index: int) -> dict:
    """A corpus-independent random point in the weight grid (#85).

    The seed is derived from the fold and restart index alone — no corpus
    content, no label, no previous fit — so a restart cannot smuggle in what
    the held-out texts look like.
    """
    keys = sorted(slop_scorer.DEFAULT_WEIGHTS)
    rng = random.Random(f"cv-start:{fold}:{index}")
    return {key: rng.choice(calibrate.CANDIDATE_VALUES) for key in keys}


def _multi_start(calibrate_fn, calibrate_mod, train, rounds, verbose,
                 threshold, starts, fold):
    """Coordinate ascent from several corpus-independent starting points.

    A single ascent from the uniform vector does not fit anything on this
    corpus: the thresholded-F1 objective is piecewise constant, the ascent
    accepts only a strict improvement from moving ONE coordinate, and the
    uniform vector sits on a plateau that needs several to move together. It
    therefore stops in round one, unchanged — and the run measures a uniform
    baseline while calling itself a refit.

    That is an optimizer failure, not a fact about the weights: the shipped
    vector beats uniform on four of the five training folds (fold 2 ties), so
    better points demonstrably exist where this ascent cannot reach them.
    Restarting elsewhere in the grid is the cheap way to give it somewhere to
    walk from. Restarts are seeded from the fold index only, never from the
    corpus.
    """
    best = None
    for index in range(starts):
        start = neutral_weights() if index == 0 else random_start(fold, index)
        result = calibrate_fn(train, rounds=rounds, verbose=verbose,
                              initial_weights=start, threshold=threshold)
        score = calibrate_mod.objective(
            calibrate_mod.metrics(result["weights"], train, threshold), 0.95)
        if best is None or score > best[0]:
            best = (score, result)
    return best[1]


def cross_validate(items: list, k: int = 5, threshold: float = DEFAULT_THRESHOLD,
                   seed: int = 17, calibrator=None, rounds: int = 3,
                   verbose: bool = False, starts: int = 4) -> dict:
    """Held-out metrics: fit the weights per fold, score the fold not seen.

    `calibrator` is injectable so the fold machinery can be tested without
    paying for coordinate ascent (roughly 200 s per round per fold — this is
    an L3 operation, not a CI gate).
    """
    if calibrator is None:
        calibrate_mod = calibrate

        def calibrator(train, **kw):
            # calibrate.py reports progress on stdout. A fold takes minutes,
            # so the progress is worth having — but not interleaved with the
            # report on the same stream, where it would break `--json` and
            # any parse of the text output. Progress to stderr, report to
            # stdout.
            with contextlib.redirect_stdout(sys.stderr):
                return _multi_start(calibrate.calibrate, calibrate_mod, train,
                                    rounds=rounds, verbose=verbose,
                                    threshold=threshold, starts=starts,
                                    fold=kw.get("fold", 0))

    clf = SlopClassifier(os.path.join(ROOT, "ontology.json"))
    folds = make_folds(items, k=k, seed=seed)

    def engines(weights):
        def pipeline(text):
            return max(slop_scorer.slop_score(text, weights=weights)["slop_score"],
                       skill_classifier.classify_text(text).score)
        return {
            "skill-scorer": lambda t: slop_scorer.slop_score(
                t, weights=weights)["slop_score"],
            "src-classifier": lambda t: clf.classify_text(t).overall_slop_score,
            "skill-pipeline (scorer+classifier)": pipeline,
        }

    engine_names = list(engines(_default_weights()))
    for name in engine_names:
        engine_kind(name)  # fail before spending an hour on coordinate ascent

    fold_reports, held_out_scores = [], {name: [] for name in engine_names}
    for number, (train_idx, test_idx) in enumerate(folds):
        train = [items[i] for i in train_idx]
        test = [items[i] for i in test_idx]
        fitted = calibrator(train, fold=number)
        # Merge over the NEUTRAL start, not the shipped defaults. The
        # calibrator is injectable and may return only the keys it tuned;
        # filling the rest from the corpus-fitted weights would re-open the
        # very leak the neutral start closes — those values were selected
        # using every held-out item. Same defect, one door further in.
        weights = neutral_weights()
        weights.update(fitted["weights"])
        per_engine = {}
        for name, scorer in engines(weights).items():
            report = evaluate(name, scorer, test, threshold)
            per_engine[name] = report
            held_out_scores[name].append(report)
        fold_reports.append({
            "fold": number,
            "n_train": len(train),
            "n_test": len(test),
            "test_ids": [item["id"] for item in test],
            "weights": weights,
            "engines": per_engine,
        })

    def pooled(reports):
        tp = sum(r["tp"] for r in reports)
        fp = sum(r["fp"] for r in reports)
        tn = sum(r["tn"] for r in reports)
        fn = sum(r["fn"] for r in reports)
        precision = tp / (tp + fp) if tp + fp else 0.0
        recall = tp / (tp + fn) if tp + fn else 0.0
        f1 = (2 * precision * recall / (precision + recall)
              if precision + recall else 0.0)
        return {"tp": tp, "fp": fp, "tn": tn, "fn": fn,
                "precision": round(precision, 3), "recall": round(recall, 3),
                "f1": round(f1, 3),
                "precision_exact": precision, "recall_exact": recall,
                "f1_exact": f1}

    in_sample = {r["engine"]: r for r in run(threshold=threshold, items=items)}
    return {
        "k": k,
        "seed": seed,
        "starts": starts,
        "n": len(items),
        "folds": fold_reports,
        "held_out": {name: pooled(reports)
                     for name, reports in held_out_scores.items()},
        "in_sample": {name: {key: report[key] for key in
                             ("tp", "fp", "tn", "fn", "precision", "recall", "f1")}
                      for name, report in in_sample.items()},
        "fitted": list(FITTED_ENGINES),
        "unfitted": list(UNFITTED_ENGINES),
        "mixed": list(MIXED_ENGINES),
    }


def format_cross_validation(result: dict) -> str:
    lines = [f"=== cross-validation: {result['k']} folds, seed {result['seed']}, "
             f"n={result['n']} ==="]
    lines.append("  weights refitted per fold; each text scored only by weights "
                 "that never saw it")
    lines.append("")
    width = max(len(name) + len(engine_kind(name)) + 3
                for name in result["in_sample"])
    lines.append(f"  {'engine':<{width}} {'in-sample':>22}   {'held-out':>22}")
    for name in result["in_sample"]:
        kind = engine_kind(name)
        a, b = result["in_sample"][name], result["held_out"][name]
        lines.append(
            f"  {name + ' [' + kind + ']':<{width}} "
            f"P{a['precision']:.3f} R{a['recall']:.3f} F1{a['f1']:.3f}   "
            f"P{b['precision']:.3f} R{b['recall']:.3f} F1{b['f1']:.3f}")
    lines.append("")
    lines.append("  Only the fitted engine's held-out figure estimates "
                 "generalization. The unfitted classifier scores the same either")
    lines.append("  way by construction, and the pipeline takes the stronger of "
                 "the two — so its held-out figure understates the overfit.")
    lines.append("")
    lines.append("  LIMIT — held out with respect to the WEIGHTS ONLY. The "
                 "scorer's feature inventories (BUZZWORD_TIERS,")
    lines.append("  PHRASE_CATEGORIES and the other corpus-calibrated "
                 "constants) were mined from the whole of")
    lines.append("  eval/corpus.jsonl, the Batch-F phrases specifically from "
                 "its false negatives. A fold can therefore be")
    lines.append("  rewarded by signals designed after looking at its own "
                 "texts. Refitting the weights per fold does not")
    lines.append("  undo that; only an evaluation corpus that never fed "
                 "feature selection would. See issue #107.")
    return "\n".join(lines)


def run(corpus_path: str = DEFAULT_CORPUS, threshold: float = DEFAULT_THRESHOLD,
        items: list = None) -> list:
    if items is None:
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
        "--cross-validate", type=int, default=None, metavar="K",
        help="held-out estimate over K stratified folds: refit the scorer's "
             "weights on each fold's training part and score only the part it "
             "never saw. Reports in-sample and held-out side by side. "
             "Expensive (L3): roughly 200 s per coordinate-ascent round per "
             "fold. Without this flag the run is the usual in-sample report "
             "(#85).")
    parser.add_argument(
        "--cv-seed", type=int, default=17, metavar="S",
        help="fold seed; the split is deterministic for a given seed (M8)")
    parser.add_argument(
        "--cv-starts", type=int, default=4, metavar="S",
        help="coordinate-ascent restarts per fold (default 4). One ascent "
             "from the uniform vector fits nothing — it sits on a plateau the "
             "one-coordinate-at-a-time search cannot leave. Starts are seeded "
             "from the fold index, never from the corpus (#85).")
    parser.add_argument(
        "--cv-rounds", type=int, default=3, metavar="R",
        help="coordinate-ascent rounds per fold (default 3, as in calibrate.py)")
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

    if args.cross_validate is not None:
        if args.min_precision is not None or args.min_recall is not None:
            # The floors gate the in-sample run. Accepting them here and then
            # exiting 0 without checking anything would turn the CI gate into
            # a pass-through the moment someone adds --cross-validate to it.
            parser.error(
                "--cross-validate reports a held-out estimate and does not "
                "apply --min-precision/--min-recall; run the two separately")
        cv = cross_validate(load_corpus(args.corpus), k=args.cross_validate,
                            threshold=args.threshold, seed=args.cv_seed,
                            rounds=args.cv_rounds, starts=args.cv_starts,
                            verbose=not args.json)
        print(json.dumps(cv, indent=2) if args.json
              else format_cross_validation(cv))
        # A held-out run reports; the floors below gate the in-sample run and
        # would compare the wrong pair of numbers here.
        sys.exit(0)

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
