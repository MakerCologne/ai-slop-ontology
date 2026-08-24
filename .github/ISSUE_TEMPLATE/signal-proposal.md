---
name: Signal-Proposal
about: Neues Slop-Signal vorschlagen (Signal-RFC)
labels: signal-proposal
---

# Signal-Proposal (Signal-RFC)

> Pflichtfelder sind mit **(Pflicht)** markiert. Fehlende Pflichtfelder = Issue wird nicht in den Burn aufgenommen (docs/SIGNAL-DOD.md #64, docs/METHODOLOGY.md #63).

- **Signal Name (Pflicht):** `snake_case`, einzigartig
- **Kategorie (Pflicht):** correctness | style | rhetoric | formatting | structure | provenance | code
- **Proposed Severity (Pflicht):** critical | high | medium | detect-only
- **Lebenszyklus-Start:** `nursery` (Default; Übergänge s. docs/METHODOLOGY.md Abschnitt 2)
- **Replaces / Supersedes:** Signal-ID falls Migration
- **depends-on (Pflicht):** Issue-Nummer(n), ohne die dieses Signal nicht gebaut werden darf (Sequencing-Disziplin, M5) — oder „keine"

## Corpus Evidence (Pflicht)
Trefferquoten auf dem Referenzkorpus (eval/corpus.jsonl): TruePos / FalsePos, n. Mind. 1 zitiertes True Positive **und** 1 Hard Negative aus einer echten Quelle (keine frei erfundenen Beispiele).

## Test-Oracle (Pflicht)
Exakte Matcherspezifikation (Regex/Metrikgrenzen) + ≥1 Positiv-/Negativ-Fixture + Akzeptanzschwelle — *vor* Implementierung (M1).

## False Positive Analysis / FP-Analyse (Pflicht)
Genre-Register, Zitat-/Pre-2022-Exemptions, keep_when-Denke — auch wenn Ergebnis „kein Guard nötig" (M2, #23/#42).

## Prior Art (Pflicht)
Wikipedia:Signs of AI writing, slopkit, no-ai-slop, verwandte Signale im Repo, Literatur (arXiv-Nummern wo applicable) (M11).

## Quellen (Pflicht)
Mind. 1 verifizierte Primärquelle mit Link (M6). claim → source → quote.

## Detection Semantics
Wie äußert sich der Fund (Guide-level)?

## Specification
Regex/Metrikgrenzen, Normalisierung, Interferenz mit anderen Signalen (Kollisions-Check #46).

## Graduation Criteria (Pflicht)
Welchen FP-Gate-Wert muss das Signal auf dem #41-Korpus erreichen für nursery→beta? (Benchmark-Referenz, DoD #5)

## Drawbacks / False-Negative-Risiko

## Unresolved Questions
