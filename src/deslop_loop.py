"""DESLOP-LOOP orchestrator (issue #51).

A state machine that ORCHESTRATES slop removal — it never rewrites text
itself (ADR-0001: detector-only repo; ADR-0006 detect-only module
discipline). The FIX step is an injected callback with the signature
``fix(text, findings) -> candidate``; the loop verifies, budgets and
selects candidates (Best-of-N between the current best and the candidate).

States per iteration:
    DETECT -> TRIAGE (signal confirmation) -> FIX-CALLBACK -> VERIFY
    -> EXIT-CHECK (E1-E5), with a rollback edge (candidate worse than the
    current best is discarded) and an ESCALATE terminal (maxIter and
    stagnation NEVER silently pass as success).

Exit checks and their guarantees:
    E1  score < score_threshold          -> slop score below the flag
                                            threshold of the detector scale
    E2  no confirmed critical finding    -> no non-compensable hard-gate
                                            signal remains
    E3  stability: two accepted iterations with |delta| < epsilon
                                        -> stagnation above threshold:
                                           ESCALATE (honest: fixpoint != optimum)
    E4  no signals outside the baseline  -> fixes did not incubate new
                                            signals (non-idempotency guard)
    E5  max_iter reached                 -> ESCALATE, never EXIT_OK

EXIT_OK requires E1 AND E2 AND E4 at a top-of-iteration detect. E3 and E5
terminate with EXIT_ESCALATE ("human review required") — the loop never
claims success it cannot guarantee. All guarantees are bound to the
detector's scale ("slop-frei nach Maßstab des Detektors"), not to absolute
quality (#62: Fixpoint != Optimum).

Signal confirmation (#58/Self-CheckGPT concept): a finding is only passed
to the fix callback if it appeared in two consecutive top-of-iteration
DETECT runs OR its confidence >= confirm_confidence.

Voice-budget guardrail: a candidate whose token-change rate relative to
the current text exceeds voice_budget (default 25%, Minimum-Effective-Edit
/ KL-analogon per Gao et al. 2210.10760) is rejected before verification.

Audit (#61 concept): every run writes runs/<runId>/manifest.json,
iterations.jsonl and result.json.
"""

from __future__ import annotations

import datetime
import difflib
import json
import os
import re
from collections import Counter
from dataclasses import asdict, dataclass, field
from typing import Callable, Optional

Detector = Callable[[str], "tuple[float, list[Finding]]"]
Fixer = Callable[[str, list["Finding"]], Optional[str]]

_TOKEN_RE = re.compile(r"\b\w+\b")


@dataclass
class Finding:
    """One detected slop finding, detector-agnostic."""

    signal: str
    confidence: float
    evidence: str
    severity: str = "medium"


@dataclass
class LoopParams:
    score_threshold: float = 0.4
    max_iter: int = 5
    epsilon: float = 0.01
    voice_budget: float = 0.25
    confirm_confidence: float = 0.9


@dataclass
class LoopResult:
    verdict: str            # EXIT_OK | EXIT_ESCALATE
    exit_check: str         # "E1+E2" | "E3" | "E5" | "NO_FIX" ...
    iterations: int
    score_initial: float
    score_final: float
    text: str
    guarantee: str
    open_signals: list = field(default_factory=list)
    iteration_records: list = field(default_factory=list)
    run_dir: Optional[str] = None


def default_detector(ontology_path: str = "ontology.json") -> Detector:
    """Read-only wrapper around the repo's deterministic classifier."""
    import sys

    root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    sys.path.insert(0, root)
    from src.classifier import SlopClassifier

    clf = SlopClassifier(ontology_path)

    def detect(text: str):
        res = clf.classify_text(text)
        findings = [
            Finding(signal=m.signal_id, confidence=m.confidence,
                    evidence=m.evidence, severity=m.severity)
            for m in res.signals_detected
        ]
        return res.overall_slop_score, findings

    return detect


def token_change_rate(before: str, after: str) -> float:
    """Simplified token-diff change rate (Levenshtein-analogue on bags).

    1 - |multiset intersection| / max(|before|, |after|); 0.0 = identical,
    ~1.0 = fully rewritten.
    """
    a = Counter(_TOKEN_RE.findall(before.lower()))
    b = Counter(_TOKEN_RE.findall(after.lower()))
    inter = sum((a & b).values())
    total = max(sum(a.values()), sum(b.values()), 1)
    return 1.0 - inter / total


class DeslopLoop:
    """The DESLOP-LOOP orchestrator. Owns NO rewriting logic (ADR-0001)."""

    def __init__(self, detector: Optional[Detector] = None,
                 params: Optional[LoopParams] = None,
                 runs_dir: Optional[str] = None,
                 run_id: Optional[str] = None):
        self.detector = detector or default_detector()
        self.params = params or LoopParams()
        self.runs_dir = runs_dir
        self.run_id = run_id or datetime.datetime.now().strftime(
            "%Y%m%d-%H%M%S") + f"-{id(self) % 10000:04d}"

    # -- audit helpers -------------------------------------------------
    def _audit_start(self, text: str) -> Optional[str]:
        if not self.runs_dir:
            return None
        d = os.path.join(self.runs_dir, self.run_id)
        os.makedirs(d, exist_ok=True)
        manifest = {
            "run_id": self.run_id,
            "created": datetime.datetime.now().isoformat(timespec="seconds"),
            "detector": type(self.detector).__name__
            if self.detector else "default_detector",
            "params": asdict(self.params),
            "input_chars": len(text),
        }
        with open(os.path.join(d, "manifest.json"), "w") as f:
            json.dump(manifest, f, indent=2, ensure_ascii=False)
        return d

    def _audit_iter(self, run_dir, rec):
        if not run_dir:
            return
        with open(os.path.join(run_dir, "iterations.jsonl"), "a") as f:
            f.write(json.dumps(rec, ensure_ascii=False) + "\n")

    def _audit_result(self, run_dir, res: LoopResult, manifest_extra=None):
        if not run_dir:
            return
        payload = {
            "verdict": res.verdict,
            "exit_check": res.exit_check,
            "iterations": res.iterations,
            "score_initial": res.score_initial,
            "score_final": res.score_final,
            "open_signals": res.open_signals,
            "guarantee": res.guarantee,
        }
        if manifest_extra:
            payload.update(manifest_extra)
        with open(os.path.join(run_dir, "result.json"), "w") as f:
            json.dump(payload, f, indent=2, ensure_ascii=False)

    # -- main loop -----------------------------------------------------
    def run(self, text: str, fix: Optional[Fixer] = None) -> LoopResult:
        p = self.params
        run_dir = self._audit_start(text)

        score_initial, baseline_findings = self.detector(text)
        baseline_ids = {f.signal for f in baseline_findings}
        current, current_score = text, score_initial

        prev_top_ids: Optional[set] = None   # top-of-iteration detects only
        accepted_deltas: list[float] = []
        records: list[dict] = []
        verdict = exit_check = None
        guarantee = ""
        open_signals: list = []
        it = 0

        while it < p.max_iter:
            it += 1
            # ---- DETECT + TRIAGE (confirmation) ----
            top_score, findings = self.detector(current)
            confirmed = [
                f for f in findings
                if f.confidence >= p.confirm_confidence
                or (prev_top_ids is not None and f.signal in prev_top_ids)
            ]
            confirmed_ids = {f.signal for f in confirmed}
            prev_top_ids = {f.signal for f in findings}
            open_signals = sorted(confirmed_ids)

            # ---- EXIT-CHECK (pre-fix) ----
            has_critical = any(f.severity == "critical" for f in confirmed)
            e1 = top_score < p.score_threshold
            e2 = not has_critical
            e4 = confirmed_ids <= baseline_ids
            if e1 and e2 and e4:
                verdict, exit_check = "EXIT_OK", "E1+E2"
                guarantee = (
                    f"slop-frei nach Maßstab des Detektors "
                    f"(Score {top_score:.3f} < {p.score_threshold}, E1+E2 "
                    f"erfüllt, keine inkubierten Signale). Fixpoint != "
                    f"Optimum — Aussage ist maßstabsgebunden."
                )
                records.append({"iter": it, "score_before": top_score,
                                "score_after": top_score,
                                "findings": sorted({f.signal for f in findings}),
                                "confirmed": sorted(confirmed_ids),
                                "action": "exit_ok", "budget_used": 0.0})
                self._audit_iter(run_dir, records[-1])
                break

            # ---- FIX-CALLBACK (injected; loop never writes itself) ----
            if fix is None:
                verdict, exit_check = "EXIT_ESCALATE", "NO_FIX"
                guarantee = ("human review required — no fix callback "
                             "provided; open signals: "
                             + ", ".join(sorted(confirmed_ids)))
                records.append({"iter": it, "score_before": top_score,
                                "score_after": top_score,
                                "findings": sorted({f.signal for f in findings}),
                                "confirmed": sorted(confirmed_ids),
                                "action": "escalate_no_fix",
                                "budget_used": 0.0})
                self._audit_iter(run_dir, records[-1])
                break

            candidate = fix(current, confirmed)
            if candidate is None:
                verdict, exit_check = "EXIT_ESCALATE", "NO_CANDIDATE"
                guarantee = ("human review required — fix callback returned "
                             "no candidate; open signals: "
                             + ", ".join(sorted(confirmed_ids)))
                records.append({"iter": it, "score_before": top_score,
                                "score_after": top_score,
                                "findings": sorted({f.signal for f in findings}),
                                "confirmed": sorted(confirmed_ids),
                                "action": "escalate_no_candidate",
                                "budget_used": 0.0})
                self._audit_iter(run_dir, records[-1])
                break

            # ---- VOICE BUDGET (guardrail before verify) ----
            budget = token_change_rate(current, candidate)
            if budget > p.voice_budget:
                records.append({"iter": it, "score_before": top_score,
                                "score_after": current_score,
                                "findings": sorted({f.signal for f in findings}),
                                "confirmed": sorted(confirmed_ids),
                                "action": "rejected_budget",
                                "budget_used": round(budget, 4)})
                self._audit_iter(run_dir, records[-1])
                continue

            # ---- VERIFY (re-detect candidate) + rollback edge ----
            cand_score, _cand_findings = self.detector(candidate)
            if cand_score < current_score:
                delta = current_score - cand_score
                current, current_score = candidate, cand_score
                accepted_deltas.append(delta)
                action = "accepted"
            else:
                delta = None
                action = "rollback"   # Best-of-N: keep the better draft
            records.append({"iter": it, "score_before": top_score,
                            "score_after": cand_score,
                            "findings": sorted({f.signal for f in findings}),
                            "confirmed": sorted(confirmed_ids),
                            "action": action,
                            "budget_used": round(budget, 4)})
            self._audit_iter(run_dir, records[-1])

            # ---- E3: stagnation over two accepted iterations ----
            if (len(accepted_deltas) >= 2
                    and accepted_deltas[-1] < p.epsilon
                    and accepted_deltas[-2] < p.epsilon):
                verdict, exit_check = "EXIT_ESCALATE", "E3"
                guarantee = (
                    f"human review required — stagnation: two accepted "
                    f"iterations with delta < epsilon={p.epsilon}, score "
                    f"{current_score:.3f} still >= {p.score_threshold}. "
                    f"Fixpoint != Optimum. Open signals: "
                    + ", ".join(sorted(open_signals))
                )
                break

        if verdict is None:
            verdict, exit_check = "EXIT_ESCALATE", "E5"
            guarantee = (
                f"human review required — maxIter={p.max_iter} exhausted "
                f"without reaching the threshold; never a silent pass. "
                f"Score {current_score:.3f} (initial {score_initial:.3f}). "
                f"Open signals: " + ", ".join(sorted(open_signals) or ["-"])
            )

        res = LoopResult(verdict=verdict, exit_check=exit_check, iterations=it,
                         score_initial=score_initial, score_final=current_score,
                         text=current, guarantee=guarantee,
                         open_signals=open_signals,
                         iteration_records=records, run_dir=run_dir)
        self._audit_result(run_dir, res)
        return res
