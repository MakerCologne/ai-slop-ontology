#!/usr/bin/env python3
"""Eval-Runner für den Human/Ideological-Slop-Korpus (Issue #98, adr/0005).

Eigener Korpuspfad (KEIN Mixing mit eval/corpus.jsonl AI-Slop):
    python3 eval/run_human_ideological.py
    python3 eval/run_human_ideological.py --json
    python3 eval/run_human_ideological.py --min-precision-neg 0.95

Gates:
  1. Integrität  — 40/40 Minimum, 5 Slop-Segmente je >=8, eindeutige IDs,
                   source == "own:handwritten", keine doppelten Texte.
  2. Leak-Check  — jede positive Zeile braucht >=1 Merkmal außerhalb der
                   Marker-Phrase (features mit "structure:"-Präfix), damit keine
                   Trainingsphrase das einzige Positiv-Merkmal ist (#98 DoD).
  3. Precision-Pin auf Hard-Negatives — die DE-Rhetorik-Signalgruppe
                   (rhetoric detect-only, #92) darf auf den 40 Negativen mit
                   Precision >= 0.95 laufen (FP-Schutz, adr/0008: polemic_risk
                   existiert nicht vor diesem Korpus).

Die Rhetorik-Gruppe ist heute die Teilmenge der detect-only de_*-Kategorien mit
ideologienahen Mustern. #92 (Option B) erweitert diese Zuordnung; der Pin bleibt
bestehen und wird mit jedem neuen Rhetorik-Signal automatisch strenger geprüft.
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
CORPUS = REPO / "eval" / "human_ideological.jsonl"

# Segment-Zuordnung (Sampling-Plan, eval/SAMPLING-human-ideological.md)
SEGMENTS = {
    "Ritual-Brandmauer": {"RitualFirewall"},
    "Kollektivframe": {"CollectiveOther", "ReplacementKicker"},
    "Purity-Kette": {"PurityBan", "VibeScapegoat"},
    "Salvation-Kette": {"SalvationModel", "MartyrCartel"},
    "Ethnopluralismus-Rebrand": {"EthnopluralistRebrand"},
}
# Signale außerhalb der Kern-Segmente bleiben erlaubt (Bonus-Korpus).
SEGMENT_SIGNALS = {s for v in SEGMENTS.values() for s in v}

# Rhetorik-Signalgruppe (detect-only, siehe Modul-Docstring): ideologienahe
# de_*-Kategorien aus dem DE-Layer, gegen die das FP-Gate läuft.
# #92 (Option B) erweitert diese Zuordnung um dedizierte Ritual-/Purity-Signale.
RHETORIC_CATEGORIES = (
    "de_binary_contrast",
    "de_false_range",
    "de_vague_authority",
    "de_authority_floskel",
    "de_symbolik",
    "de_meta_comment",
    "de_superlativ",
)


def load(path: Path) -> list[dict]:
    rows = []
    with path.open(encoding="utf-8") as fh:
        for line in fh:
            line = line.strip()
            if line:
                rows.append(json.loads(line))
    return rows


def check_integrity(rows: list[dict]) -> list[str]:
    errors: list[str] = []
    ids = [r["id"] for r in rows]
    texts = [r["text"] for r in rows]
    if len(ids) != len(set(ids)):
        errors.append(f"doppelte IDs: {len(ids) - len(set(ids))}")
    if len(texts) != len(set(texts)):
        errors.append("doppelte Texte im Korpus")
    bad_src = [r["id"] for r in rows if r.get("source") != "own:handwritten"]
    if bad_src:
        errors.append(f"source != own:handwritten: {bad_src}")
    for field in ("id", "signal", "label", "lang", "text"):
        miss = [r["id"] for r in rows if not r.get(field)]
        if miss:
            errors.append(f"leeres Pflichtfeld {field}: {miss}")

    pos = [r for r in rows if r["label"] == "slop"]
    neg = [r for r in rows if r["label"] == "hard_negative"]
    if len(pos) < 40:
        errors.append(f"positiv {len(pos)} < 40")
    if len(neg) < 40:
        errors.append(f"negativ {len(neg)} < 40")
    for name, sigs in SEGMENTS.items():
        n = sum(1 for r in pos if r["signal"] in sigs)
        if n < 8:
            errors.append(f"Segment {name}: {n} < 8")
    return errors  # Signale außerhalb der Kern-Segmente bleiben erlaubt (Bonus-Korpus)


def check_leak(pos: list[dict]) -> list[str]:
    """Keine positive Zeile darf allein von einer Marker-Phrase getragen werden."""
    errors = []
    for r in pos:
        feats = r.get("features") or []
        if not any(f.startswith("structure:") for f in feats):
            errors.append(f"{r['id']}: kein structure-Merkmal außerhalb der Phrase")
    return errors


def rhetoric_hits(rows: list[dict]) -> tuple[int, int]:
    """Läuft die Rhetorik-Gruppe gegen den Korpus. Rückgabe (fp, tp).

    Phrasen stammen aus ontology.json (SSOT); eine Kategorie feuert ab >=2
    Phrasen-Treffern (Standard-Schwelle der Phrase-Signale).
    """
    onto = json.loads((REPO / "ontology.json").read_text(encoding="utf-8"))
    cats = onto["signals"]["text"]["phrases"]["categories"]
    group = {c: [p.lower() for p in cats[c]["items"]] for c in RHETORIC_CATEGORIES
             if c in cats}
    if not group:
        print("SKIP rhetoric-Gate (keine Rhetorik-Kategorien in ontology.json)")
        return 0, 0
    fp = tp = 0
    for r in rows:
        text = r["text"].lower()
        hit = any(
            sum(1 for p in phrases if p in text) >= 2
            for phrases in group.values()
        )
        if hit:
            if r["label"] == "hard_negative":
                fp += 1
            else:
                tp += 1
    return fp, tp


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--corpus", default=str(CORPUS))
    ap.add_argument("--min-precision-neg", type=float, default=0.95)
    ap.add_argument("--json", action="store_true")
    args = ap.parse_args()

    rows = load(Path(args.corpus))
    pos = [r for r in rows if r["label"] == "slop"]
    neg = [r for r in rows if r["label"] == "hard_negative"]

    integrity_errors = check_integrity(rows)
    leak_errors = check_leak(pos)
    fp, tp = rhetoric_hits(rows)
    # Precision auf Negativen: Anteil der Nicht-Auslösungen an allen Negativen.
    precision_neg = (len(neg) - fp) / len(neg) if neg else 0.0

    report = {
        "corpus": args.corpus,
        "n": len(rows),
        "pos": len(pos),
        "neg": len(neg),
        "integrity": "FAIL" if integrity_errors else "PASS",
        "integrity_errors": integrity_errors,
        "leak_check": "FAIL" if leak_errors else "PASS",
        "leak_errors": leak_errors,
        "rhetoric": {"fp_neg": fp, "tp_pos": tp,
                     "precision_neg": round(precision_neg, 4),
                     "threshold": args.min_precision_neg,
                     "pass": precision_neg >= args.min_precision_neg},
        "pass": (not integrity_errors and not leak_errors
                 and precision_neg >= args.min_precision_neg),
    }

    if args.json:
        print(json.dumps(report, ensure_ascii=False, indent=1))
    else:
        print(f"Korpus: {report['pos']} positiv / {report['neg']} negativ")
        print(f"Integrität: {report['integrity']}  Leak-Check: {report['leak_check']}")
        print(f"Rhetorik-Gruppe auf Negativen: {fp} FP / {len(neg)} "
              f"→ Precision {precision_neg:.4f} "
              f"(>= {args.min_precision_neg}: {'PASS' if report['rhetoric']['pass'] else 'FAIL'})")
        for err in integrity_errors + leak_errors:
            print(f"  - {err}")
        print("GESAMT:", "PASS" if report["pass"] else "FAIL")
    return 0 if report["pass"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
