# 4. Genre-Opt-in statt Auto-Erkennung

- **Status:** accepted
- **Datum:** 2026-08-25 (rückdokumentiert; Entscheidung fiel mit #42, Batch B)

## Context and Problem Statement

Signale feuern je nach Textsorte unterschiedlich falsch: Juristensprache, Paper-Abstracts, ehrliches Marketing, Fach- und Konfigurationstexte lösen Buzzword-/Phrasen-Signale aus, ohne Slop zu sein. Frage: erkennt der Scorer das Genre automatisch, oder gibt der Aufrufer es an?

## Decision Drivers

- Auto-Erkennung wäre selbst ein unzuverlässiges ML-Teilsystem — Fehler der Genre-Klassifikation würden zu unkontrollierbaren FP/FN-Verschiebungen führen.
- Determinismus und Testbarkeit (M8): Explizite Parameter sind reproduzierbar.
- FMEA-/Guard-Systematik (M2): Guards müssen nachvollziehbar dokumentiert sein.

## Considered Options

### Option 1: Automatische Genre-Erkennung im Scorer
- Gut: null Konfiguration für Aufrufer.
- Schlecht: nicht-deterministisch; Genre-Fehler verschleiern Signal-Fehler; schwer testbar.

### Option 2: Genre-Register als Opt-in-Profile (Parameter)
- Gut: deterministisch, testbar, Profile dokumentiert; Hard Negatives je Genre im Benchmark prüfbar.
- Schlecht: Aufrufer müssen das Genre kennen/angeben; Default-Profil muss konservativ sein.

## Decision Outcome

**Chosen option: Option 2.** `genre_profiles.py` (#42) liefert dokumentierte Opt-in-Profile (z. B. legal, academic, marketing, technical, config); ohne Angabe gilt ein konservatives Default-Profil. Register-Hard-Negatives kommen aus dem Benchmark-Korpus (#41).

## Consequences

- **Positiv:** FP-Rate 0.0 über alle Hard-Negative-Genres im Benchmark (Messung 2026-08-25, v1.9.0); Profile sind reviewbare Artefakte.
- **Negativ:** Unbekannte Genres laufen auf Default — Rest-FPs bleiben möglich.
- **Neutral:** Profil-Pflege ist Teil des Re-Baseline-Kalenders (#67).

## Confirmation

- tests/test_genre_profiles.py + Genre-FP-Breakdown in `eval/run_benchmark.py`.

## More Information

- Issues: #42, #41, #23
- Burn-Log-Entscheidungen (D001–D012): `research/slop-ontology-gap-2026-08-24/burn-log.md` (externe Quelle)
