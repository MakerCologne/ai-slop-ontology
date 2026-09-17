"""Signal-Bestätigung: ≥ 2 unabhängige Nachweise vor jedem Fix (#58).

Implementierung der Spec ``docs/loop-guards/58-signal-bestätigung.md``
(PR #144, Loop-Issue #58 / SelfCheckGPT-Mechanik, Manakul et al.,
arXiv:2303.08896).

Kernidee: EIN einzelner deterministischer Matcher-Treffer kann ein
False-Positive sein und treibt dann einen False-Positive-Loop — ein
legitimes Muster wird repetitiv "gefixt". Ein Finding gilt erst als
bestätigt, wenn **zwei unabhängige Nachweise** vorliegen:

  Pfad A — deterministisch + LLM-Befund (#57 Layer-2-Scanner):
      der deterministische Matcher UND ein injizierbarer
      LLM-Check bestätigen dasselbe Signal.

  Pfad B — deterministisch + Resample:
      der Matcher meldet dasselbe Signal auch nach Perturbation
      des Eingabetexts (Whitespace/Case/Interpunktion). Ein
      Zufallstreffer auf exakt eine Schreibweise fällt raus.

  Pfad C — Konfidenz / Stabilität (Backwards-kompatibel):
      confidence >= confirm_confidence ODER das Signal erschien
      bereits im vorherigen top-of-iteration DETECT (zwei
      aufeinanderfolgende Runs — das ist die ursprüngliche, in
      ``deslop_loop`` verankerte Bestätigung).

Alle Pfade sind bewusst nur **detect-side**-Gates: dieses Modul
schreibt niemals Text (ADR-0001 detect-only discipline).

Metrik (Spec-Akzeptanz): ``fp_fix_rate`` — Anteil der Fix-Trigger,
die auf unbestätigten (ein-Nachweis-)Findings beruhten. Ziel laut
Spec: FP-Fixes −50 % bei Recall-Verlust ≤ 2 Punkte, messbar
vor/nach auf dem Benchmark-Korpus.
"""

from __future__ import annotations

import re
from dataclasses import dataclass, field
from typing import Callable, Optional

# Re-use the Finding shape from the loop orchestrator. confirm.py is
# imported BY deslop_loop, so the import is circular at runtime — keep
# it type-only and duck-type at runtime instead.
from typing import TYPE_CHECKING

if TYPE_CHECKING:  # pragma: no cover
    from src.deslop_loop import Finding


# -- Resample-Perturbation (Pfad B) ----------------------------------

_WHITESPACE_RE = re.compile(r"[ \t]+")
_PUNCT_SPOTS = re.compile(r"(?<=[,:;])(?=\S)")


def resample_variants(text: str) -> list[str]:
    """Perturbationen des Eingabetexts für den Resample-Nachweis.

    Bewusst trivial & deterministisch gehalten: Whitespace-Verdünnung,
    Interpunktions-Abstand und Klein-/Großschreibung. Ein
    signalstarker Befund (echtes Slop-Muster) überlebt diese
    Perturbationen; ein Treffer, der nur auf exakt eine Schreibweise
    passt, fällt raus. Kein RNG — reproduzierbar für Audits.
    """
    v1 = _WHITESPACE_RE.sub("  ", text)            # whitespace dilution
    v2 = _PUNCT_SPOTS.sub(" ", text)               # punctuation spacing
    v3 = text[0].lower() + text[1:] if text else text  # case perturbation
    return [v for v in (v1, v2, v3) if v != text]


# -- Confirm-Gate ------------------------------------------------------

@dataclass
class ConfirmParams:
    confirm_confidence: float = 0.9   # Pfad C: Konfidenz-Einzel-Nachweis
    resample_votes: int = 1           # Pfad B: n Resample-Varianten müssen mitsprechen
    use_resample: bool = False        # Pfad B ab Werk aus (Kosten); opt-in
    use_stability: bool = True        # Pfad C: zwei aufeinanderfolgende DETECTs


@dataclass
class ConfirmedFinding:
    """Finding plus die Nachweise, die es bestätigt haben (Audit-Feld)."""
    finding: Finding
    evidence: list = field(default_factory=list)  # z.B. ["deterministic", "resample"]


class ConfirmGate:
    """Bestätigt Findings erst ab zwei unabhängigen Nachweisen (#58).

    Der Gate ersetzt das bisherige Inline-TRIAGE-Kriterium in
    ``deslop_loop`` und ist als injizierbare Strategie gebaut:

        gate = ConfirmGate(llm_check=my_llm, params=ConfirmParams(use_resample=True))
        loop = DeslopLoop(..., confirm=gate)

    Nachweis-Quellen (mindestens 2 nötig, "deterministic" zählt immer):
      * "deterministic"  — der Matcher meldet das Signal (implizit)
      * "llm"            — injizierbarer LLM-Check bestätigt es (Pfad A)
      * "resample"       — ≥ ``resample_votes`` Perturbationen melden es (Pfad B)
      * "stability"      — Signal war auch im vorherigen DETECT aktiv (Pfad C)
      * "confidence"     — confidence ≥ ``confirm_confidence`` (Pfad C)

    FP-Zähler: Jedes verworfene Finding (nur 1 Nachweis) zählt als
    *verhinderter False-Positive-Fix* — Rohstoff für die FP-Fix-Rate.
    """

    def __init__(self, llm_check: Optional[Callable[[str, str], bool]] = None,
                 params: Optional[ConfirmParams] = None):
        self.llm_check = llm_check      # (text, signal_id) -> bool
        self.params = params or ConfirmParams()
        self.stats = {"confirmed": 0, "rejected": 0,
                      "by_path": {"llm": 0, "resample": 0,
                                  "stability": 0, "confidence": 0}}

    def confirm(self, text: str, findings: list,
                prev_ids: Optional[set] = None,
                detector: Optional[Callable[[str], list]] = None
                ) -> list[ConfirmedFinding]:
        """Bestätige ``findings`` auf ``text``; liefert ConfirmedFinding-Liste."""
        out: list[ConfirmedFinding] = []
        for f in findings:
            evidence = ["deterministic"]
            if f.confidence >= self.params.confirm_confidence:
                evidence.append("confidence")
            if prev_ids is not None and f.signal in prev_ids:
                evidence.append("stability")
            # Pfad A: LLM-Zweitnachweis (injizierbar, nie hier hardcoded)
            if self.llm_check is not None and self.llm_check(text, f.signal):
                evidence.append("llm")
            # Pfad B: Resample — braucht den Detektor für die Variants
            if self.params.use_resample and detector is not None:
                votes = 0
                for variant in resample_variants(text):
                    _, vfindings = detector(variant)
                    if any(v.signal == f.signal for v in vfindings):
                        votes += 1
                if votes >= self.params.resample_votes:
                    evidence.append("resample")
            if len(set(evidence)) >= 2:
                out.append(ConfirmedFinding(finding=f, evidence=sorted(set(evidence))))
                self.stats["confirmed"] += 1
                for p in set(evidence) - {"deterministic"}:
                    if p in self.stats["by_path"]:
                        self.stats["by_path"][p] += 1
            else:
                self.stats["rejected"] += 1
        return out


def fp_fix_rate(gate_stats: dict) -> float:
    """FP-Fix-Rate = verhinderte Einzel-Nachweis-Fixes / alle Findings.

    Metrik aus der Spec (#58): misst den Anteil der Fix-Trigger, die
    ohne Bestätigungstor gefeuert hätten (also potentielle
    False-Positive-Fixes). Vor/Nach-Vergleich: ohne Gate ist die Rate
    0 (alles feuert), mit Gate ist ``rejected / (confirmed+rejected)``
    der verhinderte Anteil — gemessen auf dem Benchmark-Korpus.
    """
    total = gate_stats.get("confirmed", 0) + gate_stats.get("rejected", 0)
    if total == 0:
        return 0.0
    return gate_stats.get("rejected", 0) / total
