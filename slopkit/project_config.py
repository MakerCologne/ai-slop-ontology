"""Project-local configuration (upstream #11 / btm #1138): the deslop.toml
equivalent for `slop`.

A project config is a small JSON file passed via ``--config slop.json``:

    {
      "disabled_signals": ["EmDashExcess", "ListHeavy"],
      "term_allowlist":    ["harness"],
      "weight_overrides":  {"low": 0.1}
    }

Semantics
---------
disabled_signals
    Signal IDs suppressed from every report; the overall score is
    recomputed from the remaining signals with the documented formula
    ``min(1.0, sum(weight[severity] * confidence) / max(1, n))``.
term_allowlist
    Terms that are legitimate in *this* project's domain ("harness" in an
    ML repo). Matched case-insensitively against buzzword tiers and phrase
    categories; matched entries are removed before detection runs.
weight_overrides
    Partial overrides for the severity weights (critical/high/medium/low).

Everything is validated eagerly — unknown keys, unknown severities, or a
file that is not a JSON object abort with a clear error.
"""

from __future__ import annotations

import json
from dataclasses import dataclass, field
from pathlib import Path

VALID_SEVERITIES = ("critical", "high", "medium", "low")


class ConfigError(Exception):
    """Raised for malformed project config files (fail loud, not silent)."""


@dataclass
class ProjectConfig:
    disabled_signals: set[str] = field(default_factory=set)
    term_allowlist: set[str] = field(default_factory=set)
    weight_overrides: dict[str, float] = field(default_factory=dict)

    @property
    def is_active(self) -> bool:
        return bool(self.disabled_signals or self.term_allowlist
                    or self.weight_overrides)


def load_project_config(path: str | Path) -> ProjectConfig:
    """Load and validate a project config file."""
    p = Path(path)
    if not p.exists():
        raise ConfigError(f"config file not found: {p}")
    try:
        data = json.loads(p.read_text(encoding="utf-8"))
    except json.JSONDecodeError as e:
        raise ConfigError(f"{p}: invalid JSON ({e})") from e
    if not isinstance(data, dict):
        raise ConfigError(f"{p}: top level must be a JSON object")

    known = {"disabled_signals", "term_allowlist", "weight_overrides"}
    unknown = set(data) - known
    if unknown:
        raise ConfigError(f"{p}: unknown key(s): {sorted(unknown)} "
                          f"(allowed: {sorted(known)})")

    disabled = data.get("disabled_signals", [])
    if not isinstance(disabled, list) or not all(isinstance(s, str) for s in disabled):
        raise ConfigError(f"{p}: disabled_signals must be a list of signal IDs")

    allowlist = data.get("term_allowlist", [])
    if not isinstance(allowlist, list) or not all(isinstance(t, str) for t in allowlist):
        raise ConfigError(f"{p}: term_allowlist must be a list of terms")

    overrides = data.get("weight_overrides", {})
    if not isinstance(overrides, dict):
        raise ConfigError(f"{p}: weight_overrides must be an object")
    for sev, w in overrides.items():
        if sev not in VALID_SEVERITIES:
            raise ConfigError(f"{p}: weight_overrides key {sev!r} is not one of "
                              f"{list(VALID_SEVERITIES)}")
        if not isinstance(w, (int, float)) or not (0.0 <= float(w) <= 1.0):
            raise ConfigError(f"{p}: weight for {sev!r} must be a number in [0, 1]")

    return ProjectConfig(
        disabled_signals=set(disabled),
        term_allowlist={t.lower() for t in allowlist},
        weight_overrides={sev: float(w) for sev, w in overrides.items()},
    )


def apply_to_engine(eng, cfg: ProjectConfig) -> None:
    """Apply a validated config to a slopkit Engine in place.

    - allowlisted terms are removed from buzzword tiers and phrase
      categories before detection runs;
    - disabled signal IDs and the effective severity weights are stored on
      the engine so its classify wrappers can filter and re-score.
    """
    if cfg.term_allowlist:
        cl = eng._classifier
        cl.buzzword_tiers = {
            tier: [w for w in words if w.lower() not in cfg.term_allowlist]
            for tier, words in cl.buzzword_tiers.items()
        }
        cl.phrase_categories = {
            cat: [p for p in items if p.lower() not in cfg.term_allowlist]
            for cat, items in cl.phrase_categories.items()
        }
    eng._disabled_signals = set(cfg.disabled_signals)
    from classifier import SEVERITY_WEIGHTS
    weights = dict(SEVERITY_WEIGHTS)
    weights.update(cfg.weight_overrides)
    eng._severity_weights = weights


def reclassify_with_config(eng, result):
    """Filter disabled signals and recompute the overall score.

    Mirrors the classifier's documented aggregation (ontology §6):
    Noisy-OR over remaining signals with the effective severity weights,
    escalation for any critical signal or >= 2 high-severity signals, and
    the 0.70 / 0.40 / 0.25 severity bands.
    """
    disabled = getattr(eng, "_disabled_signals", set())
    if disabled:
        result.signals_detected = [
            s for s in result.signals_detected if s.signal_id not in disabled
        ]
    weights = getattr(eng, "_severity_weights", None)
    if disabled or weights:
        if result.signals_detected:
            no_slop_prob = 1.0
            for s in result.signals_detected:
                no_slop_prob *= 1.0 - weights[s.severity] * s.confidence
            result.overall_slop_score = min(1.0, round(1.0 - no_slop_prob, 4))

            has_critical = any(s.severity == "critical" for s in result.signals_detected)
            high_count = sum(
                1 for s in result.signals_detected if s.severity in ("critical", "high"))
            escalate = ((has_critical and weights["critical"] > 0)
                        or (high_count >= 2 and weights["high"] > 0))
            if escalate:
                result.overall_slop_score = max(result.overall_slop_score, 0.70)

            if result.overall_slop_score >= 0.70:
                result.severity = "slop_candidate"
                result.countermeasures = ["exclude_from_rag", "do_not_cite", "label_as_ai"]
            elif result.overall_slop_score >= 0.40:
                result.severity = "suspicious"
                result.countermeasures = ["require_human_review", "cross_check_sources"]
            elif result.overall_slop_score >= 0.25:
                result.severity = "ai_assisted"
                result.countermeasures = ["source_check_recommended"]
            else:
                result.severity = "clean"
                result.countermeasures = ["standard_quality_check"]
        else:
            result.overall_slop_score = 0.0
            result.severity = "clean"
            result.countermeasures = ["standard_quality_check"]
    return result
