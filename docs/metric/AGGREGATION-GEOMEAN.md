# Metrik-Design: gewichtetes geometrisches Mittel als Aggregations-Option (#117)

**Status:** spec (nicht aktiviert) · **Governance:** docs/SCORE-GOVERNANCE.md, adr/0005 · **Ausgang:** BS-I7 (Signal-Kollision/Doppelbestrafung), Kollisionen parallel in `ontology.json#/collisionMatrix` (#46)

## Problem

Die bestehende Aggregation (noisy-OR, `ontology.json#/scoringFormula`) addiert unabhängige Evidenz — richtig für verschiedene Dimensionen, aber: (a) Doppeltreffer innerhalb **einer** Dimension werden zu hart bestraft bzw. doppelt gezählt (#46), (b) viele Kleinsignale einer Dimension können leere Dimensionen verdecken.

## Vorschlag (Vorbild flamehaven01/AI-SLOP-Detector)

Dimensionen (slopnessScoring) als **gewichtetes geometrisches Mittel** aggregieren: „one bad dimension can't be hidden behind good ones"; Doppelbestrafung innerhalb einer Dimension wird gedämpft.

```
slop_score = prod_d (1 - w_d * risk_d) ^ alpha_d     mit sum(alpha_d) = 1
```

- `risk_d` = gedämpfte Dimensions-Risiko-Größe (z. B. 1 - exp(-sum der Signalgewichte der Dimension)).
- `alpha_d` = Dimensionsgewicht (Start: uniform 1/N, Kalibrierung nur mit Ablations-Pflicht #106).

## Abgrenzung

- Ersetzt **nicht** die Kollisions-Matrix (#46 bleibt nötig — Doppeltreffer innerhalb einer Dimension werden hier nur gedämpft, nicht dedupliziert).
- Ersetzt **nicht** noisy-OR innerhalb einer Dimension (Evidenz-Akkumulation bleibt).

## Aktivierungspfad (Governance)

1. Spec-PR (dieser) → 2. Referenz-Implementierung als Alternativ-Aggregation hinter Flag → 3. Messung auf `eval/corpus.jsonl` **mit uniform-Vergleich** (Ablations-Pflicht, #106) → 4. Freigabe via SCORE-GOVERNANCE (Change-Protokoll, Re-Baseline).

Keine Änderung an `scoringFormula` in diesem PR.
