#!/usr/bin/env python3
"""L1-Fixtures fuer den Prevention-Contract-Eval (#232).

Stellt sicher: Korpus laedt, alle absichtlich schwachen Varianten tragen
mindestens ein Flag, bekannte Heuristik-Fehltreffer sind als known-fp
dokumentiert (Judge-Register eval/JUDGE-prevention.md)."""

import json
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, "eval"))

from run_prevention_eval import evaluate_genre, evaluate_variant  # noqa: E402

CORPUS = os.path.join(ROOT, "eval", "prevention_genres.jsonl")

# known-fp laut Judge-Durchgang 2026-09-17 (JUDGE-prevention.md)
KNOWN_FP = {("pg-01-geschaeftsmail", 3): "C5_rhetorische_frage"}


def load():
    with open(CORPUS) as f:
        return [json.loads(l) for l in f if l.strip()]


def test_corpus_loads():
    items = load()
    assert len(items) == 7
    for it in items:
        assert len(it["variants"]) == 3
        assert it["own"] == "handwritten"


def test_weak_variants_flagged():
    for it in load():
        res = evaluate_genre(it)
        for v, r in zip(it["variants"], res["varianten"]):
            if v["label"] != "ok":
                assert r["flags"], f"{it['id']} v{r['index']} ({v['label']}) ohne Flag"


def test_ok_variants_clean_or_known_fp():
    for it in load():
        res = evaluate_genre(it)
        for v, r in zip(it["variants"], res["varianten"]):
            if v["label"] != "ok" or not r["flags"]:
                continue
            for flag in r["flags"]:
                key = (it["id"], r["index"])
                assert KNOWN_FP.get(key) == flag, (
                    f"unerwarteter Flag {flag} an ok-Variante {key}")


def test_opener_diversity_and_isometry_threshold():
    for it in load():
        res = evaluate_genre(it)
        assert res["C6_opener_diversitaet"] >= 2, it["id"]


if __name__ == "__main__":
    for fn in [test_corpus_loads, test_weak_variants_flagged,
               test_ok_variants_clean_or_known_fp, test_opener_diversity_and_isometry_threshold]:
        fn()
        print("PASS", fn.__name__)
