"""Score-Trajectory-Monitoring + Anomalie-Eskalation (issue #59).

Intra-Run Guard: bewertet die Score-Trajektorie EINES Deslop-Loop-Runs
(``iterations.jsonl`` / ``iteration_records``) auf Goodhart-Anomalien.
Der Loop selbst bleibt unangetastet (ADR-0001: detect-only discipline) —
dieses Modul liest und urteilt, es schreibt nie Text.

Trigger (docs/loop-guards/59-trajectory-monitoring.md):
    1. ANOMALY    — Score-Sprung Δ > anomaly_delta (0.4) in einem Schritt,
                    ohne proportionale Edit-Größe (edits_pct < Δ/2)
                    → ESCALATE (Evasions-Verdacht; Goodhart adversarial).
    2. DIMINISHING — k (3) konsekutive akzeptierte Schritte mit Δ < ε (0.02)
                    → STOP_REPORT (kein weiterer Rewrite sinnvoll).
    3. ROLLBACK_CHAIN — 2 konsekutive Rollbacks → ESCALATE (menschliche Prüfung).

Abgrenzung zu #47: dort Score-Verteilungs-Shift über Modell-Generationen
(Quartal); hier Trajektorie je Run.
"""

from __future__ import annotations

import json
import os
from dataclasses import dataclass, field

OK = "OK"
ESCALATE = "ESCALATE"
STOP_REPORT = "STOP_REPORT"


@dataclass
class TrajectoryParams:
    anomaly_delta: float = 0.4      # Score-Sprung-Schwelle
    edit_proportion: float = 0.5    # proportional = edits_pct >= Δ * edit_proportion
    diminishing_k: int = 3          # konsekutive kleine Deltas
    diminishing_eps: float = 0.02
    rollback_chain: int = 2         # konsekutive Rollbacks -> ESCALATE


@dataclass
class TrajectoryVerdict:
    verdict: str                    # OK | ESCALATE | STOP_REPORT
    reasons: list = field(default_factory=list)
    steps: list = field(default_factory=list)  # normalisierte Trajektorie


def _step(rec: dict) -> dict:
    """Normalisiere ein deslop_loop iteration_record zu einem Trajektorie-Schritt."""
    return {
        "iter": rec.get("iter"),
        "score": rec.get("score_after", rec.get("score")),
        "edits_pct": rec.get("budget_used", rec.get("edits_pct", 0.0)),
        "action": rec.get("action", "accepted"),
    }


def build_from_loop_records(records: list) -> list:
    """iterations.jsonl / LoopResult.iteration_records → Trajektorie."""
    return [_step(r) for r in records if r.get("action") != "exit_ok"]


def evaluate(steps: list, params: TrajectoryParams | None = None) -> TrajectoryVerdict:
    """Bewerte eine Trajektorie [{iter, score, edits_pct, action}]."""
    p = params or TrajectoryParams()
    reasons: list[str] = []

    scored = [s for s in steps if s.get("score") is not None]
    accepted = [s for s in scored if s.get("action", "accepted") == "accepted"]

    # 1. Anomalie: perfekter Score-Sprung ohne proportionale Edits
    prev = None
    for s in accepted:
        if prev is not None:
            delta = (prev["score"] or 0.0) - (s["score"] or 0.0)
            if (delta > p.anomaly_delta
                    and (s.get("edits_pct") or 0.0) < delta * p.edit_proportion):
                reasons.append(
                    f"ANOMALY iter {s.get('iter')}: Δscore {delta:.3f} > "
                    f"{p.anomaly_delta} bei edits_pct "
                    f"{s.get('edits_pct', 0):.3f} < "
                    f"{delta * p.edit_proportion:.3f} — Evasions-Verdacht "
                    f"(Goodhart adversarial), menschliche Prüfung nötig")
        prev = s

    # 2. Diminishing returns: k konsekutive akzeptierte Deltas < eps
    deltas = []
    for a, b in zip(accepted, accepted[1:]):
        deltas.append((a["score"] or 0.0) - (b["score"] or 0.0))
    run = 0
    for d in deltas:
        run = run + 1 if abs(d) < p.diminishing_eps else 0
        if run >= p.diminishing_k:
            reasons.append(
                f"DIMINISHING: {p.diminishing_k} konsekutive Deltas < "
                f"ε={p.diminishing_eps} — Stop mit Report, kein weiterer "
                f"Rewrite")
            break

    # 3. Rollback-Kette: n konsekutive Rollbacks
    rb_run = 0
    for s in scored:
        if s.get("action") == "rollback":
            rb_run += 1
            if rb_run >= p.rollback_chain:
                reasons.append(
                    f"ROLLBACK_CHAIN: {p.rollback_chain} konsekutive "
                    f"Rollbacks — Kandidaten werden konsistent schlechter, "
                    f"menschliche Prüfung nötig")
                break
        else:
            rb_run = 0

    verdict = ESCALATE if any(r.startswith("ANOMALY") or
                              r.startswith("ROLLBACK_CHAIN")
                              for r in reasons) else (
        STOP_REPORT if any(r.startswith("DIMINISHING") for r in reasons)
        else OK)
    return TrajectoryVerdict(verdict=verdict, reasons=reasons, steps=steps)


def evaluate_run_dir(run_dir: str,
                     params: TrajectoryParams | None = None
                     ) -> TrajectoryVerdict:
    """Liest runs/<runId>/iterations.jsonl und bewertet die Trajektorie."""
    path = os.path.join(run_dir, "iterations.jsonl")
    records = []
    with open(path) as f:
        for line in f:
            line = line.strip()
            if line:
                records.append(json.loads(line))
    return evaluate(build_from_loop_records(records), params)


if __name__ == "__main__":
    import argparse

    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("run_dir", help="runs/<runId>/ mit iterations.jsonl")
    args = ap.parse_args()
    v = evaluate_run_dir(args.run_dir)
    print(json.dumps({"verdict": v.verdict, "reasons": v.reasons},
                     indent=2, ensure_ascii=False))
    raise SystemExit(0 if v.verdict == OK else 2)
