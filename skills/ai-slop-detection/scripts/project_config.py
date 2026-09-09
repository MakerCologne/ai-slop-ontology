#!/usr/bin/env python3
"""Project-local configuration for the slop scorer (issue #11).

A project can ship a config file (JSON) that adapts the detector to its
domain — the deslop.toml equivalent: signal families that are legitimate
in that domain can be disabled, individual terms can be allowlisted
(e.g. "harness" in an ML repo), and dimension weights can be overridden
for local recalibration.

Supported schema (all keys optional):

    {
      "disabled_signals": ["multilingual", "mirrored"],
      "term_allowlist": ["harness", "leverage"],
      "weight_overrides": {"buzzwords": 0.10}
    }

Rules:
- unknown signal family names are rejected (typo protection)
- unknown weight keys are rejected (must match DEFAULT_WEIGHTS keys)
- weight values must be numbers in [0, 1]
- the config is detect-only: it never *raises* a score, only lowers or
  leaves equal — weight_overrides may raise a weight, but that is an
  explicit local recalibration decision, documented as such.
"""

import json
import os
import re
import sys

# Signal families the scorer supports disabling. Same vocabulary as the
# learning-store exemptions (#29) — a disabled family is treated exactly
# like a reviewed-false-positive family for this project, permanently.
DISABLEABLE_FAMILIES = frozenset({
    "buzzwords", "phrases", "multilingual", "provenance",
    "trailing_moral", "fake_authority", "mirrored", "portability",
})


class ConfigError(ValueError):
    """Invalid project config — message is user-facing."""


def load_config(path: str) -> dict:
    """Load and validate a project config file. Raises ConfigError."""
    if not os.path.isfile(path):
        raise ConfigError(f"config file not found: {path}")
    with open(path, encoding="utf-8") as f:
        try:
            raw = json.load(f)
        except json.JSONDecodeError as e:
            raise ConfigError(f"config file is not valid JSON: {e}") from e
    if not isinstance(raw, dict):
        raise ConfigError("config root must be a JSON object")
    return validate(raw)


def validate(raw: dict, known_weight_keys=frozenset()) -> dict:
    """Validate a raw config dict into its canonical form.

    known_weight_keys: acceptable weight keys. The caller (slop_scorer)
    passes DEFAULT_WEIGHTS keys; tests may pass their own.
    """
    cfg = {"disabled_signals": set(), "term_allowlist": [],
           "weight_overrides": {}}
    extra = set(raw) - {"disabled_signals", "term_allowlist",
                        "weight_overrides"}
    if extra:
        raise ConfigError(
            "unknown config keys: " + ", ".join(sorted(extra)))
    disabled = raw.get("disabled_signals", [])
    if not isinstance(disabled, list) or \
            not all(isinstance(s, str) for s in disabled):
        raise ConfigError("disabled_signals must be a list of strings")
    unknown = set(disabled) - DISABLEABLE_FAMILIES
    if unknown:
        raise ConfigError(
            "unknown signal families (allowed: "
            + ", ".join(sorted(DISABLEABLE_FAMILIES)) + "): "
            + ", ".join(sorted(unknown)))
    cfg["disabled_signals"] = set(disabled)
    allow = raw.get("term_allowlist", [])
    if not isinstance(allow, list) or \
            not all(isinstance(t, str) and t.strip() for t in allow):
        raise ConfigError(
            "term_allowlist must be a list of non-empty strings")
    cfg["term_allowlist"] = [t.lower() for t in allow]
    overrides = raw.get("weight_overrides", {})
    if not isinstance(overrides, dict):
        raise ConfigError("weight_overrides must be an object")
    for k, v in overrides.items():
        if known_weight_keys and k not in known_weight_keys:
            raise ConfigError(
                f"unknown weight key: {k} (known: "
                + ", ".join(sorted(known_weight_keys)) + ")")
        if not isinstance(v, (int, float)) or isinstance(v, bool) \
                or not 0.0 <= v <= 1.0:
            raise ConfigError(
                f"weight_overrides[{k}] must be a number in [0, 1]")
    cfg["weight_overrides"] = dict(overrides)
    return cfg


def strip_allowlisted(text: str, terms: list) -> str:
    """Remove allowlisted term occurrences from the signal text
    (same mechanic as genre exempt terms: signal matching only,
    structural dimensions keep the full text)."""
    if not terms:
        return text
    # word-boundary, case-insensitive; escape for regex safety
    pattern = re.compile(
        r"\b(?:" + "|".join(re.escape(t) for t in terms) + r")\b",
        re.IGNORECASE)
    result = pattern.sub(" ", text)
    return re.sub(r"[ \t]{2,}", " ", result)
