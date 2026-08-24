#!/usr/bin/env python3
"""
Fabricated proof-metrics detection (issue #34) — detect-only.

Percentage/score numbers tied to a QUALITY claim ("98% accuracy", "F1 0.89",
"zero false positives") without any source reference within ±200 characters
("corpus", "eval", links, DOIs, "et al.", years in parentheses). Numbers
without a quality-claim word never fire (the FP guard — "42 artifacts" is
fine).

Irony discipline: this repo's own CHANGELOG contains F1/precision claims;
every one of them carries its "eval/corpus.jsonl" reference, and the test
suite enforces that the detector stays silent on our own claims.

Public surface:
    find_fabricated_proof_metrics(text) -> {
        "claims": [{match, claim, offset}], "signals": [{id, confidence,
        evidence, keep_when}]
    }
"""

import re

CONTEXT_RADIUS = 200  # characters around a claim checked for source refs

CLAIM_CONTEXT = re.compile(
    r"\b(accuracy|precision|recall|f1|f-score|false positives|"
    r"error rate|success rate|uptime)\b",
    re.IGNORECASE,
)

METRIC_NUMBERS = [
    # "98% accuracy" / "accuracy of 98%"
    re.compile(r"\b\d{1,3}(?:[.,]\d+)?\s*%"),
    # "F1 0.89" / "F1 of 0.89"
    re.compile(r"\bF1(?:[- ]score)?(?:\s+of)?\s*\d[.,]\d{1,3}", re.IGNORECASE),
    # "zero/no false positives"
    re.compile(r"\b(?:zero|no)\s+false\s+positives\b", re.IGNORECASE),
    # "accuracy of 0.9" style decimals
    re.compile(r"\b(?:of|is|reaches|at)\s+\d[.,]\d{1,3}\b", re.IGNORECASE),
]

SOURCE_REFS = re.compile(
    r"(?i)(corpus|korpus)|\beval(?:uation)?\b|https?://|doi\.org|10\.\d{4,}|"
    r"et al\.|\(\s*\d{4}\s*\)|\b\d{4}\b",
)


def find_fabricated_proof_metrics(text: str) -> dict:
    claims = []
    spans = []
    for pat in METRIC_NUMBERS:
        for m in pat.finditer(text):
            start = max(0, m.start() - CONTEXT_RADIUS)
            end = min(len(text), m.end() + CONTEXT_RADIUS)
            context = text[start:end]
            if not CLAIM_CONTEXT.search(context):
                continue
            if SOURCE_REFS.search(context):
                continue
            claims.append({"match": m.group(0), "offset": m.start()})
            spans.append((start, end, m.group(0)))

    signals = []
    if claims:
        evidence = "; ".join(
            f"'{c['match']}' (+{c['offset']}) without source ref "
            f"in ±{CONTEXT_RADIUS} chars"
            for c in claims[:5]
        )
        signals.append({
            "id": "fabricated-proof-metrics",
            "confidence": 0.75,
            "evidence": evidence,
            "keep_when": "Marketing copy whose numbers are backed by a linked "
                         "report elsewhere in the same document — any eval/"
                         "corpus/link/year within ±200 chars suppresses the "
                         "signal.",
        })

    return {"claims": claims, "signals": signals}
