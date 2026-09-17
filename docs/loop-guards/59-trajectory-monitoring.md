# Score-Trajectory-Monitoring + Anomalie-Eskalation (#59)

**Status:** implemented (guard/trajectory.py + tests) · **Verwandt:** Goodhart (SCORE-GOVERNANCE), #40 (adversarial Rewrites), #47 (Quartals-Drift — anders, siehe Abgrenzung)

## Trigger (intra-Run, `guard/trajectory.py`)

1. **Anomalie:** Perfekt-Score-Sprung (Δ > 0.4 in einem Schritt ohne proportionale Edit-Größe) → ESCALATE (Evasions-Verdacht, Goodhart adversarial).
2. **Diminishing Returns:** k = 3 konsekutive Iterationen mit Δ < ε = 0.02 → Stop mit Report, kein weiterer Rewrite.
3. **Rollback-Kette:** 2 konsekutive Rollbacks (z. B. Voice-Drift #56) → ESCALATE an menschliche Prüfung.

## Abgrenzung

#47 misst Score-Verteilungs-Shift über Modell-Generationen (Quartal); dieses Guard überwacht die **Trajektorie je Run**. Log: `trajectory: [{iter, score, edits_pct, verdict}]` im Run-Report.

## Implementierung

- `guard/trajectory.py` — pure Evaluierung (`evaluate`, `TrajectoryParams`), Ingest aus `iterations.jsonl` (`evaluate_run_dir`, CLI: `python3 guard/trajectory.py runs/<runId>/`), Mapping aus `LoopResult.iteration_records` (`build_from_loop_records`; `exit_ok` wird ausgeschlossen).
- Verdict-Priorität: ESCALATE (ANOMALY, ROLLBACK_CHAIN) > STOP_REPORT (DIMINISHING) > OK. CLI-Exit-Code: 0 bei OK, sonst 2 (fail-loud).
- Schwellen: Δ=0.4, proportional = `edits_pct ≥ Δ/2`, k=3, ε=0.02, Rollbacks=2 — alle via `TrajectoryParams` konfigurierbar.
- Tests: `tests/test_trajectory_guard.py` (11 Fälle inkl. Grenzfälle: proportionale Large-Drops sind OK, Präzedenz, custom Params).
