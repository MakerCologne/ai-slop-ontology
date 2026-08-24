# 6. Detect-only-Module außerhalb des Scorers

- **Status:** accepted
- **Datum:** 2026-08-25 (rückdokumentiert; Entscheidung fiel mit #9, Batch D — #46-Prävention)

## Context and Problem Statement

Code-Slop-Signale (#9) und andere spezialisierte Detektionen sollen nicht unbemerkt den Text-Score verändern: Score-Wirkung wäre unbelebt (keine Kalibrierung, keine Hard-Negative-Messung) und würde die Composite-Metrik verwässern. #46 (Signal-Kollisionen) träumt genau von dieser Verschiebung.

## Decision Drivers

- Score-Änderungen brauchen Governance (Guardrail-Pflicht, Re-Baseline, Change-Protokoll — #67, M9).
- Composite-Interpretierbarkeit: jede score-wirksame Größe muss kalibriert und im Benchmark gemessen sein.
- Nutzerwunsch: Code-Slop trotzdem detektierbar und reportbar.

## Considered Options

### Option 1: Code-Slop-Signale in den Haupt-Scorer integrieren (mit Gewicht)
- Gut: eine Zahl für alles.
- Schlecht: unkalibrierte Signale verzerren den Composite-Score; Kollisionsrisiko mit Text-Signalen (#46); Score-Comparability bricht.

### Option 2: Detect-only-Module (eigene Detector-Klasse, kein Score-Einfluss, eigener Report)
- Gut: Score bleibt interpretierbar; Code-Slop-Funde sichtbar via CLI; Promotion in den Score nur über den Lebenszyklus (#63: nursery → beta braucht FP-Gate).
- Schlecht: Konsumenten müssen zwei Ausgabekanäle auswerten.

## Decision Outcome

**Chosen option: Option 2.** `code_slop.py` (#9) ist detect-only (5 Signale, eigener Report via `scripts/code_slop_check.py`); der Diff-Modus (#10) scored nur geänderte Zeilen und routet Code an das Detect-only-Modul.

## Consequences

- **Positiv:** Composite-Score unverändert stabil; klare Promotion-Pfad via Signal-Lebenszyklus (#63).
- **Negativ:** bis zur Promotion (beta/stable) fehlt Code-Slop im Score — bewusste, dokumentierte Lücke.
- **Neutral:** Promotion erzeugt Governance-Pflichten (#67).

## Confirmation

- tests/test_code_slop.py + test_diff_mode.py stellen sicher, dass Code-Funde den Score nicht beeinflussen.

## More Information

- Issues: #9, #10, #46, #55
- Burn-Log-Entscheidungen (D001–D012): `research/slop-ontology-gap-2026-08-24/burn-log.md` (externe Quelle)
