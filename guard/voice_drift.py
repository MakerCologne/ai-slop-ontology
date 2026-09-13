"""Voice-Drift-Guardrail (issue #56): Non-Regression für Minimum-Effective-Edit.

Iteriertes Rewriten homogenisiert Stil (Model Collapse; arXiv:2305.17493,
arXiv:2307.01850) und verletzt Minimum-Effective-Edit. Dieses Modul bewertet
eine Rewrite-Iteration gegen ``Draft_0`` (Baseline) auf drei messbaren
Kriterien und urteilt detect-only (ADR-0001: es wird nie Text geschrieben):

    1. TOKEN_BUDGET   — geänderte Token-Fraktion vs. Draft_0 > beta (0.25)
                        → VOICE_DRIFT (KL-Guardrail-Analogon, Gao et al.
                        arXiv:2210.10760, hier als Edit-Distanz-Budget).
    2. BURSTINESS     — Burstiness (σ/µ der Satzlängen) sinkt unter
                        burstiness_ratio (0.9) × Baseline
                        → VOICE_DRIFT (glattgeschliffener Rhythmus).
    3. TTR            — Type-Token-Ratio (Synonym-Vielfalt-Proxy) sinkt
                        unter ttr_ratio (0.9) × Baseline
                        → VOICE_DRIFT (lexikalische Verarmung).

Abgrenzung zu #59 (trajectory.py): dort Score-Verlauf je Run, hier
Stil-Drift Text vs. Text. Abgrenzung zu #47: dort Score-Shift über
Quartale/Modelle.

Nur gegen Draft_0 bewerten — nicht Kette n→n+1 —, sonst akkumuliert
Drift unbemerkt unter lauter grünen Zwischenschritten.
"""

from __future__ import annotations

import re
from dataclasses import dataclass, field
from difflib import SequenceMatcher

OK = "OK"
SKIP = "SKIP"
VOICE_DRIFT = "VOICE_DRIFT"

_WORD_RE = re.compile(r"[\w\u00c0-\u024f]+", re.UNICODE)
_SENT_RE = re.compile(r"[^.!?;:\n]+")

MIN_TOKENS = 25   # darunter ist TTR/Burstiness nicht aussagekräftig → SKIP


@dataclass
class VoiceDriftParams:
    beta_token_change: float = 0.25    # max. geänderte Token-Fraktion vs. Draft_0
    burstiness_ratio: float = 0.9      # Non-Regression: σ/µ >= ratio × Baseline
    ttr_ratio: float = 0.9             # Non-Regression: TTR >= ratio × Baseline
    min_tokens: int = MIN_TOKENS


@dataclass
class VoiceDriftVerdict:
    verdict: str                       # OK | VOICE_DRIFT | SKIP
    reasons: list = field(default_factory=list)
    metrics: dict = field(default_factory=dict)


def tokenize(text: str) -> list:
    """Kleinbuchstaben-Worttoken (sprachagnostisch grob, keine Lemmata nötig)."""
    return _WORD_RE.findall(text.lower())


def token_change_ratio(baseline_tokens: list, current_tokens: list) -> float:
    """Geänderte Token-Fraktion via SequenceMatcher-OpCodes (ins/del/repl).

    Normiert auf max(len) — symmetrisch, 0.0 bei identischen Tokenlisten.
    """
    if not baseline_tokens and not current_tokens:
        return 0.0
    denom = max(len(baseline_tokens), len(current_tokens))
    changed = 0
    matcher = SequenceMatcher(None, baseline_tokens, current_tokens, autojunk=False)
    for tag, i1, i2, j1, j2 in matcher.get_opcodes():
        if tag != "equal":
            changed += max(i2 - i1, j2 - j1)
    return changed / denom


def _sentence_lengths(text: str) -> list:
    lengths = [len(tokenize(s)) for s in _SENT_RE.findall(text)]
    return [n for n in lengths if n > 0]


def burstiness(text: str) -> float:
    """σ/µ der Satzlängen (Gries 2008); 0.0 bei ≤1 Satz oder µ=0."""
    lengths = _sentence_lengths(text)
    if len(lengths) < 2:
        return 0.0
    mean = sum(lengths) / len(lengths)
    if mean == 0:
        return 0.0
    var = sum((n - mean) ** 2 for n in lengths) / len(lengths)
    return (var ** 0.5) / mean


def ttr(tokens: list) -> float:
    """Type-Token-Ratio als Synonym-Vielfalt-Proxy."""
    if not tokens:
        return 0.0
    return len(set(tokens)) / len(tokens)


def evaluate(baseline_text: str, current_text: str,
             params: VoiceDriftParams = None) -> VoiceDriftVerdict:
    """Bewerte ``current_text`` gegen ``Draft_0`` (``baseline_text``)."""
    p = params or VoiceDriftParams()
    base_tok, cur_tok = tokenize(baseline_text), tokenize(current_text)
    metrics = {
        "token_change": token_change_ratio(base_tok, cur_tok),
        "burstiness_baseline": burstiness(baseline_text),
        "burstiness_current": burstiness(current_text),
        "ttr_baseline": ttr(base_tok),
        "ttr_current": ttr(cur_tok),
        "tokens_baseline": len(base_tok),
        "tokens_current": len(cur_tok),
    }

    if max(len(base_tok), len(cur_tok)) < p.min_tokens:
        return VoiceDriftVerdict("SKIP", ["too_short"], metrics)

    reasons = []
    if metrics["token_change"] > p.beta_token_change:
        reasons.append(
            f"TOKEN_BUDGET: {metrics['token_change']:.2f} > beta={p.beta_token_change}")
    if (metrics["burstiness_baseline"] > 0
            and metrics["burstiness_current"]
            < p.burstiness_ratio * metrics["burstiness_baseline"]):
        reasons.append(
            f"BURSTINESS: {metrics['burstiness_current']:.2f} < "
            f"{p.burstiness_ratio}×{metrics['burstiness_baseline']:.2f}")
    if (metrics["ttr_baseline"] > 0
            and metrics["ttr_current"] < p.ttr_ratio * metrics["ttr_baseline"]):
        reasons.append(
            f"TTR: {metrics['ttr_current']:.2f} < "
            f"{p.ttr_ratio}×{metrics['ttr_baseline']:.2f}")

    return VoiceDriftVerdict(VOICE_DRIFT if reasons else OK, reasons, metrics)
