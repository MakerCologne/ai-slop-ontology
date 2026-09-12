# Loop-Guard 61 — Run-Audit-Format `runs/<runId>/`

**Issue:** ai-slop-ontology#61 (LOOP-I11, P2) · **PR:** burn/issue-61-run-audit-format
**Quelle:** research/slop-loop-pipeline-2026-08-24/report.md Abschnitt (f)

## Regel

Jeder Loop-Run mit `--runs-dir` erzeugt ein Standard-Verzeichnis mit vier
Dateien (additiv zu den Legacy-Artefakten `manifest.json`,
`iterations.jsonl`, `result.json`, die unverändert bleiben):

| Datei | Inhalt |
|---|---|
| `scan.md` | Initiale Detektion: Signale, Konfidenz, Severity, Evidence |
| `fixes.md` | Je Iteration: Action (accepted/rejected_budget/rollback/…), Score vorher→nachher, Budget, bestätigte Signale |
| `trajectory.json` | Maschinenlesbar: alle Iterations-Records + Start-/Endscore |
| `report.md` | Verdict, Exit-Check, Iterationen, Guarantee, Rekonstruktions-Verweise |

## Akzeptanz (aus Issue)

Ein vergangener Run lässt sich aus den Dateien vollständig rekonstruieren:
welches Signal, welcher Fix, welcher Score je Iteration. Abgedeckt durch
`tests/test_run_audit_format_61.py` (5 Tests, deterministische Fake-Detektoren).

## Guards / Grenzen

- Der Loop besitzt keine Rewrite-Logik (ADR-0001): `fixes.md` dokumentiert
  die Ergebnisse des injizierten Fix-Callbacks, führt sie nicht aus.
- Audit-Writer darf den Loop nie brechen: Wrap in try/except mit
  stderr-Warnung.
- Ohne `runs_dir` (z. B. Unit-Tests) bleibt der Writer ein No-Op.
