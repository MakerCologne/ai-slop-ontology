# 3. Golden-Control-Set als FN-Gate

- **Status:** accepted
- **Datum:** 2026-08-25 (rückdokumentiert; Entscheidung fiel mit MS-I1, Batch A)

## Context and Problem Statement

Vor Batch A gab es kein reproduzierbares FN-Gate: Der Skill-Scorer konnte an einzelnen Kontrolltexten durchfallen, ohne dass ein Gate es merkte. Meta-Slop-Report (b) F0/F1 zeigte das FN-Gate rot (Kontrolltext 0.322 < 0.40).

## Decision Drivers

- Messbare Abnahmekriterien vor jedem Change (M1).
- Ehrliche FN-Führung: bekannte FNs werden dokumentiert und getrackt, nicht versteckt.

## Considered Options

### Option 1: Nur Benchmark-Korpus (#41) als einziges Gate
- Gut: eine Messgröße.
- Schlecht: großes Korpus ist schwer zu pflegen; diskrete Kontrolltexte reagieren präziser auf Regressionen; #41 existierte erst später.

### Option 2: Kleines Golden Control Set (10 handgeschriebene Texte) als hartes Gate + bekannt-FN-Register
- Gut: schnell, deterministisch, je Commit lauffähig; known_fn-Einträge machen FNs sichtbar und auflösbar (RESOLVED-Meldung).
- Schlecht: geringe Abdeckung; kein Ersatz für den Benchmark.

## Decision Outcome

**Chosen option: Option 2.** `eval/control_set.jsonl` (5 Slop / 5 Hard Negatives) + `eval/run_control_set.py` als Gate (Threshold 0.40): jede slop Zeile ≥ 0.40 (außer dokumentierte known_fn), jede clean Zeile < 0.40.

## Consequences

- **Positiv:** FN-Regressionen brechen den Build; known-FN `slop-fn-02` wird beim Auflösen als RESOLVED gemeldet.
- **Negativ:** 10 Texte sind Stichproben — falsche Sicherheit, wenn ohne Benchmark geflogen wird (deshalb zusätzlich #41, ADR-0005).
- **Neutral:** Gate-Grün ist notwendige, nicht hinreichende Bedingung (Review behält Recht).

## Confirmation

- `eval/run_control_set.py` exit 1 bei Verletzung; läuft je Issue im Burn (Burn-Log D003).

## More Information

- Issues: MS-I1 (Batch A), #41, #12
- Burn-Log-Entscheidungen (D001–D012): `research/slop-ontology-gap-2026-08-24/burn-log.md` (externe Quelle)
