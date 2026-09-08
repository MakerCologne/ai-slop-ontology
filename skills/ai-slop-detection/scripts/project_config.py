#!/usr/bin/env python3
"""Project-local configuration for the AI-slop skill scorer (issue #11).

Signal weights are global, but terminology is not: \"harness\" is a
legitimate ML term in an ML repo and pure buzzword filler everywhere else.
A project config file lets a team tune the scorer to its own vocabulary
without forking the ontology:

.. code-block:: json

    {
      "disabled_signals": ["portability"],
      "term_allowlist": ["harness", "robust"],
      "weight_overrides": {"buzzwords": 0.05}
    }

Applied via ``python3 slop_scorer.py --config slop.json ...``:

- ``disabled_signals`` — weight names set to 0. Structural dimensions are
  still computed (the report stays complete), they just stop contributing
  to the score. Provenance floors and >= 2-family escalation keep their
  strength: escalation families are corroborating evidence, not weights.
- ``term_allowlist`` — terms removed from SIGNAL matching before the
  metrics (buzzwords / phrases / authority / multilingual), analogous to
  the #42 genre ``exempt_terms`` and the #23 quote exemption. Structural
  dimensions (density, repetition, burstiness) keep the full text.
- ``weight_overrides`` — per-signal weight values in [0, 1].

Fail-loud policy: unknown signal names, wrong types or out-of-range values
raise ``ConfigError`` at load time — a typo in the config must not
silently no-op. (``slop_score(weights=...)`` already existed as the API
surface; this module is the config/CLI layer on top, deslop.toml-style.)
"""

import json
import os

VALID_KEYS = ("disabled_signals", "term_allowlist", "weight_overrides")


class ConfigError(ValueError):
    """Raised for malformed config files — message is user-facing."""


def load_config(path, valid_signals) -> dict:
    """Load and validate a project config JSON file.

    ``valid_signals``: iterable of signal/weight names accepted by the
    scorer (DEFAULT_WEIGHTS keys). Used to validate disabled_signals and
    weight_overrides keys so typos fail loudly.
    """
    if not os.path.isfile(path):
        raise ConfigError(f"config file not found: {path}")
    try:
        with open(path, encoding="utf-8") as f:
            raw = json.load(f)
    except json.JSONDecodeError as e:
        raise ConfigError(f"config file is not valid JSON: {path} ({e})")
    if not isinstance(raw, dict):
        raise ConfigError("config root must be a JSON object")

    unknown_keys = [k for k in raw if k not in VALID_KEYS]
    if unknown_keys:
        raise ConfigError(
            "unknown config keys: " + ", ".join(sorted(unknown_keys))
            + f" (valid: {', '.join(VALID_KEYS)})")

    valid = set(valid_signals)
    cfg = {"disabled_signals": [], "term_allowlist": [], "weight_overrides": {}}

    if "disabled_signals" in raw:
        v = raw["disabled_signals"]
        if not isinstance(v, list) or not all(isinstance(s, str) for s in v):
            raise ConfigError("disabled_signals must be a list of strings")
        bad = [s for s in v if s not in valid]
        if bad:
            raise ConfigError(
                "unknown signals in disabled_signals: " + ", ".join(sorted(bad))
                + f" (valid: {', '.join(sorted(valid))})")
        cfg["disabled_signals"] = list(v)

    if "term_allowlist" in raw:
        v = raw["term_allowlist"]
        if not isinstance(v, list) or not all(
                isinstance(t, str) and t.strip() for t in v):
            raise ConfigError(
                "term_allowlist must be a list of non-empty strings")
        cfg["term_allowlist"] = list(v)

    if "weight_overrides" in raw:
        v = raw["weight_overrides"]
        if not isinstance(v, dict):
            raise ConfigError("weight_overrides must be an object")
        for k, w in v.items():
            if k not in valid:
                raise ConfigError(
                    f"unknown signal in weight_overrides: {k} "
                    f"(valid: {', '.join(sorted(valid))})")
            if not isinstance(w, (int, float)) or not 0 <= w <= 1:
                raise ConfigError(
                    f"weight_overrides[{k}] must be a number in [0, 1], got {w!r}")
        cfg["weight_overrides"] = dict(v)

    return cfg


def merge_weights(config: dict, base_weights: dict) -> dict:
    """Apply disabled_signals + weight_overrides to a copy of base weights.

    disabled_signals wins over weight_overrides — an explicitly disabled
    signal stays at 0.
    """
    merged = dict(base_weights)
    for k, w in config.get("weight_overrides", {}).items():
        merged[k] = w
    for k in config.get("disabled_signals", []):
        merged[k] = 0.0
    return merged
