#!/usr/bin/env python3
"""
Calibration-Drift-Register (issue #47, Messvorschrift).

Freezes the scorer's score DISTRIBUTION and per-signal hit-rates for a
frozen reference corpus into eval/calibration_reference.json, and
snapshot-compares them on re-score (quarterly cadence, see
docs/calibration-drift.md).

Motivation: weights and thresholds are calibrated once against a corpus
(eval/calibrate.py). When future models suppress the very markers the
signals rely on (e.g. GPT-5.1 suppressing em-dashes), a signal's
contribution silently decays while its weight stays — the calibration
ages without anyone noticing. This register makes that decay measurable:
if the distribution or any signal hit-rate wanders beyond the alert
thresholds, a weight review is triggered.

Drift model (all relative to the COMMITTED reference):
  score_percentile_shift  p10/p50/p90 of the slop_score distribution
                         (per label) moved more than SCORE_SHIFT_DELTA
  signal_rate_shift       per-signal hit-rate delta > SIGNAL_RATE_DELTA
  fixture_missing         reference fixture vanished from the corpus
  fixture_unknown         new corpus fixture without a reference entry
  fixture_text_changed    corpus text edited under a frozen id
                          (sha256 mismatch — reference is no longer
                          comparable; re-init required)

Complements scripts/fp_baseline.py (#80): that register pins tolerated
outputs on HARD NEGATIVES (FP pressure); this one pins the full score
distribution and signal contributions (calibration aging).

Usage:
    python3 scripts/calibration_drift.py --init      # freeze reference
    python3 scripts/calibration_drift.py --check     # alert on drift, exit 1
        [--reference PATH] [--corpus PATH]
"""

import argparse
import hashlib
import json
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, "skills", "ai-slop-detection", "scripts"))

import slop_scorer  # noqa: E402

DEFAULT_CORPUS = os.path.join(ROOT, "eval", "corpus.jsonl")
DEFAULT_REFERENCE = os.path.join(ROOT, "eval", "calibration_reference.json")
SCORE_SHIFT_DELTA = 0.05   # percentile shift on slop_score → alert
SIGNAL_RATE_DELTA = 0.10   # hit-rate delta per signal → alert
PERCENTILES = (10, 50, 90)
SCHEMA_VERSION = 1


def _score_fn(text: str) -> dict:
    return slop_scorer.slop_score(text)


def _fixture_entry(result: dict) -> dict:
    """Canonical comparable outputs: rounded score + sorted signal hits."""
    signals = sorted(result.get("signals", {}).get("buzzword_hits", []))
    for cat, phrases in sorted((result.get("signals", {})
                                .get("phrase_categories", {})).items()):
        signals.extend(f"{cat}:{p}" for p in sorted(phrases))
    return {"slop_score": round(result["slop_score"], 3),
            "signals": sorted(set(signals))}


def _percentile(values: list, p: int) -> float:
    """Nearest-rank percentile; values must be non-empty and sorted."""
    s = sorted(values)
    k = max(1, -(-p * len(s) // 100))  # ceil(p/100 * n), min rank 1
    return s[k - 1]


def distribution_stats(fixtures: dict, label: str) -> dict:
    scores = [f["slop_score"] for f in fixtures.values()
              if f.get("label") == label]
    if not scores:
        return {"n": 0, "percentiles": {}}
    return {"n": len(scores),
            "percentiles": {str(p): round(_percentile(scores, p), 3)
                            for p in PERCENTILES}}


def signal_hit_rates(fixtures: dict, label: str) -> dict:
    """Per-signal hit-rate (share of label-fixtures where signal fires)."""
    subset = [f for f in fixtures.values() if f.get("label") == label]
    if not subset:
        return {}
    rates = {}
    for sig in sorted({s for f in subset for s in f["signals"]}):
        hits = sum(1 for f in subset if sig in f["signals"])
        rates[sig] = round(hits / len(subset), 3)
    return rates


def load_corpus(corpus_path: str) -> dict:
    fixtures = {}
    with open(corpus_path, encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            item = json.loads(line)
            entry = _fixture_entry(_score_fn(item["text"]))
            entry["label"] = item.get("label", "unknown")
            entry["text_sha256"] = hashlib.sha256(
                item["text"].encode("utf-8")).hexdigest()
            fixtures[item["id"]] = entry
    return fixtures


def build_reference(corpus_path: str) -> dict:
    fixtures = load_corpus(corpus_path)
    return {
        "schema": SCHEMA_VERSION,
        "generated_from": os.path.relpath(corpus_path, ROOT),
        "engine": "skills/ai-slop-detection/scripts/slop_scorer.py",
        "thresholds": {
            "score_percentile_shift": SCORE_SHIFT_DELTA,
            "signal_rate_shift": SIGNAL_RATE_DELTA,
        },
        "note": ("Frozen reference for the quarterly calibration re-score "
                 "(issue #47). Messvorschrift: docs/calibration-drift.md. "
                 "alerts = weight-review trigger, NOT auto-tuning."),
        "labels": {
            label: {
                "distribution": distribution_stats(fixtures, label),
                "signal_hit_rates": signal_hit_rates(fixtures, label),
            }
            for label in sorted({f["label"] for f in fixtures.values()})
        },
        "fixtures": dict(sorted(fixtures.items())),
    }


def drift_report(reference: dict, current: dict) -> list:
    """All drift findings between two reference snapshots."""
    drift = []
    r_fix, c_fix = reference.get("fixtures", {}), current.get("fixtures", {})
    for fid in sorted(set(r_fix) | set(c_fix)):
        if fid not in r_fix:
            drift.append({"type": "fixture_unknown", "fixture": fid})
            continue
        if fid not in c_fix:
            drift.append({"type": "fixture_missing", "fixture": fid})
            continue
        old, new = r_fix[fid], c_fix[fid]
        if old.get("text_sha256") != new.get("text_sha256"):
            drift.append({"type": "fixture_text_changed", "fixture": fid})
            continue  # outputs not comparable after a corpus edit
        drift.extend(_compare_fixture(
            fid, old, new,
            reference.get("thresholds", {}).get(
                "score_percentile_shift", SCORE_SHIFT_DELTA)))

    r_labels = _comparable_labels(reference, current, r_fix, c_fix)
    for label in r_labels:
        drift.extend(_compare_distribution(label, reference, current))
        drift.extend(_compare_signal_rates(label, reference, current))
    return drift


def _comparable_labels(reference, current, r_fix, c_fix) -> list:
    """Labels comparable for distribution stats: no text edits in that
    label's fixtures (a single edited text invalidates its percentile)."""
    ok = []
    for label in sorted({f.get("label") for f in r_fix.values()}):
        fids = [fid for fid, f in r_fix.items()
                if f.get("label") == label]
        if any(c_fix.get(fid, {}).get("text_sha256")
               != r_fix[fid].get("text_sha256") for fid in fids):
            continue
        if label in current.get("labels", {}):
            ok.append(label)
    return ok


def _compare_fixture(fid, old, new, delta) -> list:
    out = []
    if abs(new["slop_score"] - old["slop_score"]) > delta:
        out.append({"type": "score_drift", "fixture": fid,
                    "committed": old["slop_score"],
                    "current": new["slop_score"]})
    for sig in sorted(set(new["signals"]) - set(old["signals"])):
        out.append({"type": "signal_added", "fixture": fid, "signal": sig})
    for sig in sorted(set(old["signals"]) - set(new["signals"])):
        out.append({"type": "signal_removed", "fixture": fid, "signal": sig})
    return out


def _compare_distribution(label, reference, current) -> list:
    out = []
    ref_d = reference["labels"].get(label, {}).get("distribution", {})
    cur_d = current["labels"].get(label, {}).get("distribution", {})
    delta = reference.get("thresholds", {}).get(
        "score_percentile_shift", SCORE_SHIFT_DELTA)
    for p in (str(x) for x in PERCENTILES):
        r, c = ref_d.get("percentiles", {}).get(p), cur_d.get(
            "percentiles", {}).get(p)
        if r is None or c is None:
            continue
        if abs(c - r) > delta:
            out.append({"type": "score_percentile_shift", "label": label,
                        "percentile": p, "committed": r, "current": c})
    return out


def _compare_signal_rates(label, reference, current) -> list:
    out = []
    ref_r = reference["labels"].get(label, {}).get("signal_hit_rates", {})
    cur_r = current["labels"].get(label, {}).get("signal_hit_rates", {})
    delta = reference.get("thresholds", {}).get(
        "signal_rate_shift", SIGNAL_RATE_DELTA)
    for sig in sorted(set(ref_r) | set(cur_r)):
        r, c = ref_r.get(sig, 0.0), cur_r.get(sig, 0.0)
        if abs(c - r) > delta:
            out.append({"type": "signal_rate_shift", "label": label,
                        "signal": sig, "committed": r, "current": c})
    return out


def main() -> int:
    ap = argparse.ArgumentParser(
        description="Calibration-Drift-Register (issue #47)")
    ap.add_argument("--init", action="store_true",
                    help="freeze the reference snapshot")
    ap.add_argument("--check", action="store_true",
                    help="re-score and alert on drift; exit 1 on findings")
    ap.add_argument("--corpus", default=DEFAULT_CORPUS)
    ap.add_argument("--reference", default=DEFAULT_REFERENCE)
    args = ap.parse_args()

    if not (args.init or args.check):
        ap.error("choose --init or --check")

    if args.check:
        with open(args.reference, encoding="utf-8") as f:
            reference = json.load(f)
        drift = drift_report(reference, build_reference(args.corpus))
        if drift:
            print(f"CALIBRATION DRIFT ({len(drift)} finding(s)) — "
                  "weight review required (docs/calibration-drift.md):")
            for d in drift[:25]:
                print(" ", json.dumps(d, ensure_ascii=False))
            if len(drift) > 25:
                print(f"  ... and {len(drift) - 25} more")
            return 1
        print("calibration drift check passed (distribution and signal "
              "hit-rates within thresholds)")
        return 0

    reference = build_reference(args.corpus)
    with open(args.reference, "w", encoding="utf-8") as f:
        json.dump(reference, f, indent=2, ensure_ascii=False)
        f.write("\n")
    n = len(reference["fixtures"])
    labels = ", ".join(f"{k}({v['distribution']['n']})"
                       for k, v in reference["labels"].items())
    print(f"wrote {args.reference} ({n} fixtures: {labels})")
    return 0


if __name__ == "__main__":
    sys.exit(main())
