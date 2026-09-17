"""BEST-OF-N FIX STRATEGIES (issue #60, upstream slopgh#60; btm #1117).

Parallel fix variants per iteration instead of a sequential single-candidate
loop: sequential loops can cascade over-correction (ping-pong between
delete-then-rewrite-then-delete); parallel variants sidestep that cascade
because the loop picks ONE survivor per iteration and discards the rest.

ADR-0001 (detector-only repo) still holds: this module OWNS NO REWRITING
LOGIC. Each strategy is an injected callback with the standard fixer
signature ``fix(text, findings) -> candidate`` (None = strategy abstains).
What this module contributes is the *selection harness*:

1. run all strategies in parallel on (current text, confirmed findings),
2. verify each candidate (voice budget guardrail, #56/#30),
3. score each verified candidate with the injected detector (scorer),
4. select the best candidate by
     a. lowest detector score (primary), then
     b. HIGHEST VOICE SIMILARITY to the current text as the tie-break
        within ``selection_epsilon`` — i.e. among equally-sloppy candidates
        the LEAST-EDITED one wins. This is the explicit counter-bias to
        verbosity/structure bias: a rewrite strategy that fixes the score
        by re-shuffling the whole text does NOT beat a minimal deletion
        that reaches the same score (Minimum-Effective-Edit, #30; verifier
        selection per Cobbe et al., arXiv:2110.14168).

Selection contract ("necessary, not sufficient"): if NO candidate passes
the voice budget, ``None`` is returned and the loop escalates/continues —
never a silent pass, consistent with the DESLOP-LOOP exit semantics.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Callable, Optional

from src.deslop_loop import Finding, token_change_rate

Strategy = Callable[[str, list], Optional[str]]
Detector = Callable[[str], "tuple[float, list[Finding]]"]


@dataclass
class StrategySpec:
    """One injected fix strategy (delete / rewrite / restructure / ...)."""

    name: str
    fix: Strategy


@dataclass
class BestOfNResult:
    """Selection receipt for the audit trail (#61 run-audit concept)."""

    selected: Optional[str]
    selected_strategy: Optional[str]
    selected_score: Optional[float]
    reason: str                      # "best_score" | "tie_voice" | "no_candidate"
    candidates: list = field(default_factory=list)   # per-strategy records


def evaluate_strategies(text: str,
                        findings: list,
                        strategies: list,
                        detector: Detector,
                        voice_budget: float = 0.25,
                        selection_epsilon: float = 0.005) -> BestOfNResult:
    """Run all strategies, verify, and select one survivor (issue #60).

    Selection rule (documented, deterministic):
      1. drop candidates that violate the voice budget (guardrail first);
      2. primary key: lowest verified detector score;
      3. tie-break within ``selection_epsilon``: smallest token-change rate
         (= highest voice similarity) — anti-verbosity/structure bias.
    """
    records = []
    verified = []   # (score, change_rate, candidate, name)

    for spec in strategies:
        try:
            candidate = spec.fix(text, findings)
        except Exception as exc:  # a failing strategy must not kill the batch
            records.append({"strategy": spec.name, "error": repr(exc),
                            "status": "aborted"})
            continue
        if candidate is None:
            records.append({"strategy": spec.name, "status": "abstained"})
            continue
        change = token_change_rate(text, candidate)
        if change > voice_budget:
            records.append({"strategy": spec.name, "status": "over_budget",
                            "change_rate": round(change, 4)})
            continue
        score, _ = detector(candidate)
        verified.append((score, change, candidate, spec.name))
        records.append({"strategy": spec.name, "status": "verified",
                        "score": round(score, 4),
                        "change_rate": round(change, 4)})

    if not verified:
        return BestOfNResult(selected=None, selected_strategy=None,
                              selected_score=None, reason="no_candidate",
                              candidates=records)

    # primary: lowest score; tie-break (within epsilon): smallest change
    verified.sort(key=lambda c: (c[0], c[1]))
    best = verified[0]
    reason = "best_score"
    if (len(verified) > 1
            and verified[1][0] - best[0] <= selection_epsilon
            and verified[1][1] < best[1]):
        best = verified[1]
        reason = "tie_voice"
    return BestOfNResult(selected=best[2], selected_strategy=best[3],
                         selected_score=best[0], reason=reason,
                         candidates=records)


class BestOfNFixer:
    """Adapter: turns N injected strategies into ONE fix callback for
    ``DeslopLoop.run(text, fix=...)`` so the orchestrator stays untouched
    (E4 baseline guard, rollback edge, audit all remain in the loop)."""

    def __init__(self, strategies: list, detector: Detector,
                 voice_budget: float = 0.25,
                 selection_epsilon: float = 0.005,
                 last_result: Optional[BestOfNResult] = None):
        self.strategies = strategies
        self.detector = detector
        self.voice_budget = voice_budget
        self.selection_epsilon = selection_epsilon
        self.last_result = last_result   # mutable receipt for audits/tests

    def __call__(self, text: str, findings: list) -> Optional[str]:
        res = evaluate_strategies(text, findings, self.strategies,
                                  self.detector, self.voice_budget,
                                  self.selection_epsilon)
        self.last_result = res
        return res.selected
