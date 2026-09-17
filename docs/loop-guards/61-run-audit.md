# Run-Audit-Format `runs/<runId>/` (#61)

**Status:** Standard (implementiert in `src/deslop_loop.py`) · **Verwandt:** #59 (Trajectory-Monitoring), #62 (Terminierungs-Semantik) · **Quellen:** Loop-Design Herleitung (b)–(e), Report-Abschnitt (f), ericzakariasson-Design (deep/05)

## Kernaussage

Jeder Loop-Run schreibt ein vollständiges Audit-Verzeichnis `runs/<runId>/`. Akzeptanzkriterium: **Ein vergangener Run lässt sich aus den Dateien vollständig rekonstruieren** — welches Signal getriggert hat, welcher Fix angewendet bzw. abgelehnt wurde, welcher Score je Iteration erreicht war.

## Standard-Verzeichnisinhalt

| Datei | Format | Inhalt |
|---|---|---|
| `manifest.json` | JSON | `run_id`, `created`, Detektor, Loop-Parameter, Input-Größe |
| `scan.md` | Markdown | Baseline-Scan: `score_initial` + alle Baseline-Findings (Signal, Severity, Confidence) |
| `iterations.jsonl` | JSONL | Roh-Records je Iteration (append-only, auch Zwischenstände) |
| `fixes.md` | Markdown | Fix-Protokoll je Iteration: Action (`accepted`/`rollback`/`rejected_budget`/…), bestätigte Signale, Voice-Budget, Score davor → danach |
| `trajectory.json` | JSON | Maschinenlesbarer Score-Pfad: `{run_id, iterations: [{iter, action, score_before, score_after, budget_used, confirmed}]}` |
| `result.json` | JSON | Endergebnis: Verdict, Exit-Check, Iterationen, Scores, offene Signale, Garantie-Formel |
| `report.md` | Markdown | Human-lesbare Run-Zusammenfassung mit Garantie-Aussage und Rekonstruktions-Index |

## Konstruktionsregeln

1. **Append-only:** `iterations.jsonl` wird pro Iteration erweitert, nie überschrieben — auch abgelehnte Fixes (`rejected_budget`, `rollback`) bleiben sichtbar.
2. **Maßstabsbindung:** `report.md` übernimmt die Garantie-Formel aus #62 („nach Maßstab des Detektors", nie absolut).
3. **Rekonstruierbarkeit:** Für jede Iteration gilt die Kette *Signal → Aktion → Score-Delta*; fehlt eines der drei Glieder, ist der Run nicht auditierbar.
4. **Kein Silent Pass:** Jeder Exit (OK wie ESCALATE) schreibt `result.json` + `report.md` mit der Exit-Begründung.
5. **Konservativ bei Baseline:** Der Baseline-Scan (`scan.md`) dokumentiert den Zustand **vor** jedem Fix — er ist die Referenz für E4 (keine neuen Signale) und für #59-Anomalie-Checks.

## Konsumierende Guards

- **#59 Trajectory-Monitoring:** liest `trajectory.json`; plötzliche Perfekt-Scores (Evasions-Verdacht) und Stagnations-Muster werden daraus abgeleitet.
- **#47 Kalibrierungs-Drift:** re-scoring historischer `scan.md`-Baselines gegen neue Signalstände (Quartals-Re-Score).

## Referenz-Implementierung

`DeslopLoop(runs_dir=...)` in `src/deslop_loop.py` (`_write_standard_files`) — Tests: `tests/test_deslop_loop.py::test_run_audit_standard_files`.
