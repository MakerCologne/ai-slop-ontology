# Best-of-N Fix-Strategien: parallele Varianten statt sequenzieller Kaskade (#60)

**Status:** implementiert (Auswahl-Harness) · **Vorbild:** Verifier-basierte
Best-of-N-Auswahl (Cobbe et al., arXiv:2110.14168) · **Verwandt:** #30
(Minimum-Effective-Edit), #56 (Voice-Budget), #51 (DESLOP-LOOP), #61 (Run-Audit)

## Problem

Sequentielle Fix-Loops kaskadieren Over-Correction: Löschen erzeugt eine
Holprigkeit, die der nächste Rewrite wieder umschreibt, der daraufhin neue
Signale inkubiert (Ping-Pong). Ein Loop, der pro Iteration nur EINEN Kandidaten
prüft, merkt das erst nach dem Schaden (Rollback-Kante in #51 fängt es, aber
jede verschwendete Iteration kostet Budget).

## Regel

Pro Iteration werden **N Strategien parallel** auf denselben
(current text, confirmed findings) losgelassen — typischerweise
delete / rewrite / restructure. Der Loop wählt **genau einen Überlebenden**:

1. **Guardrail zuerst:** Kandidaten über Voice-Budget (#56, default 25 %
   Token-Change) fliegen raus — auch bei bestem Score.
2. **Primärkriterium:** niedrigster verifizierter Detektor-Score.
3. **Tie-Break innerhalb `selection_epsilon` (default 0.005):** der
   **kleinste Edit** gewinnt (höchste Voice-Ähnlichkeit). Das ist die
   explizite Gegen-Bias-Regel gegen Verbositäts-/Struktur-Bias: ein
   Rewrite, der den Score durch Umstrukturieren des ganzen Textes erreicht,
   schlägt KEINE minimale Deletion mit gleichem Score
   (Minimum-Effective-Edit, #30).

**ADR-0001 bleibt unangetastet:** Das Repo besitzt keine Rewrite-Logik.
Strategien sind injizierte Callbacks mit der Standard-Fixer-Signatur
`fix(text, findings) -> candidate`. `fixer/strategies.py` liefert nur den
Auswahl-Harness (`evaluate_strategies`) und den Adapter
(`BestOfNFixer`), der die N Strategien als EINEN Fix-Callback für
`DeslopLoop.run(text, fix=...)` kapselt — Exit-Semantik, Rollback-Kante,
E4-Baseline-Wächter und Audit verbleiben im Orchestrator.

## Fehler-Semantik

- Kein Kandidat im Budget → `None` → Loop eskaliiert/iteriert weiter
  ("necessary, not sufficient", kein stiller Pass).
- Eine crashende Strategie bricht den Batch nicht ab (Status `aborted` im
  Auswahl-Receipt, Rest konkurriert normal).
- Jede Auswahl schreibt einen Receipt (`BestOfNResult`: selected,
  selected_strategy, selected_score, reason ∈ {best_score, tie_voice,
  no_candidate}, per-Strategien-Records) — Audit-Trail nach #61-Manier.

## Metrik

Benchmark-Vergleich sequenzieller Loop vs. BoN-Loop (gleiche Strategien):
Ziel — weniger akzeptierte Iterationen bis EXIT_OK bei gleicher E4-Rate
(keine inkubierten Signale) und geringerer kumulativer Token-Change
(Voice-Drift, #56). Fixtures: `tests/test_fixer_strategies.py`
(7 Tests: Primär-/Tie-Break-Auswahl, Budget-Guardrail, Abstention,
Crash-Isolation, Loop-Integration).
