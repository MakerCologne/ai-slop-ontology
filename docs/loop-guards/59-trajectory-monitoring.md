# Score-Trajectory-Monitoring + Anomalie-Eskalation (#59)

**Status:** spec · **Verwandt:** Goodhart (SCORE-GOVERNANCE), #40 (adversarial Rewrites), #47 (Quartals-Drift — anders, siehe Abgrenzung)

## Trigger (intra-Run, `guard/trajectory.py`)

1. **Anomalie:** Perfekt-Score-Sprung (Δ > 0.4 in einem Schritt ohne proportionale Edit-Größe) → ESCALATE (Evasions-Verdacht, Goodhart adversarial).
2. **Diminishing Returns:** k = 3 konsekutive Iterationen mit Δ < ε = 0.02 → Stop mit Report, kein weiterer Rewrite.
3. **Rollback-Kette:** 2 konsekutive Rollbacks (z. B. Voice-Drift #56) → ESCALATE an menschliche Prüfung.

## Abgrenzung

#47 misst Score-Verteilungs-Shift über Modell-Generationen (Quartal); dieses Guard überwacht die **Trajektorie je Run**. Log: `trajectory: [{iter, score, edits_pct, verdict}]` im Run-Report.
