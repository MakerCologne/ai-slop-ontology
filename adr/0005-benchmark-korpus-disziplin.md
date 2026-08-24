# 5. Benchmark-Korpus-Disziplin & ehrliche Zahlen

- **Status:** accepted
- **Datum:** 2026-08-25 (rückdokumentiert; Entscheidung fiel mit #41, Batch D)

## Context and Problem Statement

Die alte Baseline F1 0.982 beruhte auf einem 53-Texte-Corpus ohne Hard Negatives — eine Schönwetter-Metrik. Praxisfall: Mit dem erweiterten Korpus (314 Texte, 192 Slop + Hard Negatives aus 7 Genres) fiel die skill-pipeline F1 auf 0.476 (Recall 0.312), während Precision 1.0 blieb. Die alte Zahl hätte Signalausbau unbemerkt auf kaputtem Fundament legitimiert (#53).

## Decision Drivers

- Claim-Register-Disziplin: keine unbelegten oder irreführenden Zahlen (M6, #34).
- Empirie vor Ausbau (M5): erst harte Messung, dann Expansion.
- Korpus-Belegtquote: ≥ 60 % der Texte müssen Quellen-fundiert sein.

## Considered Options

### Option 1: Kleines, bequemes Korpus behalten (F1 0.982 kommunizieren)
- Gut: gute Zahlen fürs README.
- Schlecht: Goodhart — die Metrik misst den Detektor gegen sich selbst; Hard Negatives fehlen komplett; jede Expansion hätte die Zahl unkontrolliert zerstört.

### Option 2: Erweitertes, diszipliniertes Korpus (≥ 300 Texte, Hard Negatives, Quellenpflicht, 60 %-Regel) + Genre-Breakdown + ehrliche Ablösung der alten Baseline
- Gut: FP- und FN-Raten je Genre werden sichtbar; Recall-Lücken lokalisiert (Throat-Clearing/Emphasis-Phrasen) und zu Issues gemacht.
- Schlecht: die publizierte Zahl verschlechtert sich massiv — erfordert Kommunikation.

## Decision Outcome

**Chosen option: Option 2.** `eval/corpus.jsonl` (314 Zeilen, `{id,label,lang,type,genre,text,source}`), Messvorschrift threshold 0.40, Genre-FP/FN-Breakdown in `run_benchmark.py`. Die F1 0.982-Baseline wurde durch F1 0.476 (P 1.0 / R 0.312, 2026-08-25) ersetzt und der Grund im CHANGELOG dokumentiert.

## Consequences

- **Positiv:** Recall-Lücken sind jetzt adressierbare Tickets statt unsichtbarer Defekte; FP-Gate je Genre grün (0.0 in allen 7 Genres).
- **Negativ:** öffentliche Zahl ist schlechter; jedes neue Signal muss sich an harten Negatives messen lassen (gewollt, aber Aufwand).
- **Neutral:** Korpus-Erweiterung unterliegt der Re-Baseline-Kalender-Pflicht (#67).

## Confirmation

- Corpus-Disziplin-Tests: ≥ 300 Zeilen, Quellenpflicht, 60 %-Regel (tests/test_benchmark_runner.py); Genre-Breakdown im Runner.

## More Information

- Issues: #41, #53, #34, #47
- Burn-Log-Entscheidungen (D001–D012): `research/slop-ontology-gap-2026-08-24/burn-log.md` (externe Quelle)
