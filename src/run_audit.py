"""Run-Audit-Format (issue #61): standard files in runs/<runId>/.

Every loop run can be fully reconstructed from four standard files
(ericzakariasson deep/05 design):

- scan.md      initial detection: signals, confidence, severity, evidence
- fixes.md     every fix action per iteration (accepted/rejected/rollback)
- trajectory.json  machine-readable per-iteration records + scores
- report.md    final verdict, exit check, guarantee, summary table

Legacy artifacts (manifest.json, iterations.jsonl, result.json) remain
untouched for backward compatibility; this module is additive.

The loop never rewrites text (ADR-0001) — fixes.md records what the
injected fix callback did, it does not perform fixes itself.
"""

import json
import os
from datetime import datetime


def _evidence_lines(findings):
    lines = []
    for f in findings:
        ev = (getattr(f, "evidence", None) or "").strip()
        if ev:
            ev = ev.replace("\n", " ")[:160]
            lines.append(f"| `{f.signal}` | {getattr(f, 'confidence', '?'):.2f} | "
                         f"{getattr(f, 'severity', '?')} | {ev} |")
    return lines


def _fix_table(records):
    rows = []
    for rec in records:
        rows.append(
            f"| {rec.get('iter')} | {rec.get('action', '?')} | "
            f"{rec.get('score_before', '?')} → {rec.get('score_after', '?')} | "
            f"{rec.get('budget_used', 0.0)} | "
            f"{', '.join(rec.get('confirmed', []) or ['-'])} |")
    return rows


def write_run_audit(run_dir, res, baseline_findings=None, created=None):
    """Write the four standard audit files into run_dir (if run_dir set).

    res: LoopResult. baseline_findings: initial detector findings (list of
    Finding) — if not provided, reconstruction relies on iteration 1.
    """
    if not run_dir:
        return
    created = created or datetime.now().isoformat(timespec="seconds")
    records = res.iteration_records or []

    # ---- scan.md: initial detection ----
    with open(os.path.join(run_dir, "scan.md"), "w") as f:
        f.write(f"# Scan — run `{res.run_dir and os.path.basename(res.run_dir)}`\n\n"
                f"Created: {created}\n\n"
                f"- Initial slop score: **{res.score_initial:.4f}**\n"
                f"- Detected signals (iteration 1): "
                f"{', '.join(sorted({s for r in records for s in r.get('findings', [])}) or ['-'])}\n\n")
        if baseline_findings:
            f.write("| Signal | Confidence | Severity | Evidence (truncated) |\n"
                    "|---|---|---|---|\n")
            lines = _evidence_lines(baseline_findings)
            f.write("\n".join(lines) if lines else "| — | — | — | — |\n")
            f.write("\n")

    # ---- fixes.md: fix actions per iteration ----
    with open(os.path.join(run_dir, "fixes.md"), "w") as f:
        f.write(f"# Fixes — run `{os.path.basename(run_dir)}`\n\n"
                "Loop owns no rewriting logic (ADR-0001); actions below "
                "describe the injected fix callback outcome.\n\n"
                "| Iter | Action | Score before → after | Budget used | Confirmed signals |\n"
                "|---|---|---|---|---|\n")
        rows = _fix_table(records)
        f.write("\n".join(rows) if rows else "| — | — | — | — | — |\n")
        f.write("\n")

    # ---- trajectory.json: machine-readable records ----
    with open(os.path.join(run_dir, "trajectory.json"), "w") as f:
        json.dump({
            "run_dir": run_dir,
            "created": created,
            "score_initial": res.score_initial,
            "score_final": res.score_final,
            "iterations": [dict(r) for r in records],
        }, f, indent=2, ensure_ascii=False)

    # ---- report.md: final verdict ----
    with open(os.path.join(run_dir, "report.md"), "w") as f:
        f.write(f"# Run Report — `{os.path.basename(run_dir)}`\n\n"
                f"- Verdict: **{res.verdict}** (exit check: {res.exit_check})\n"
                f"- Iterations: {res.iterations}\n"
                f"- Score: {res.score_initial:.4f} → {res.score_final:.4f}\n"
                f"- Open signals: {', '.join(res.open_signals or ['-'])}\n\n"
                f"## Guarantee\n\n{res.guarantee}\n\n"
                f"## Reconstruction\n\n"
                "See `scan.md` (initial detection), `fixes.md` (per-iteration "
                "fix actions), `trajectory.json` (machine-readable records), "
                "`manifest.json`/`result.json` (legacy artifacts).\n")
