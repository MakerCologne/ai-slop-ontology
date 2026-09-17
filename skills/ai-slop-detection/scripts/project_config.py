#!/usr/bin/env python3
"""Project-local config for the slop scorer (issue #11).

Teams work in different domains: "harness" is a legitimate term in an ML
repo, "key" in a crypto codebase, "agents" in an LLM tool. Signal weights
are global by default; this module gives each project a local, versioned
override file (`slop.json`, the deslop.toml-equivalent) with three keys:

    {
      "disabled_signals": ["portability", "mirrored"],
      "term_allowlist": ["harness", "agents"],
      "weight_overrides": {"buzzwords": 0.10}
    }

Semantics:
  - disabled_signals: signal family ids (see SIGNAL_FAMILIES). Families with
    an exemption mechanic (buzzwords, phrases, multilingual, provenance,
    trailing_moral, mirrored, fake_authority, portability) are excluded
    entirely — including escalation/floor contributions. Purely weighted
    dimensions (density, repetition, ...) get weight 0.
  - term_allowlist: terms removed from the signal-matching text before
    buzzword/phrase/multilingual/authority matching (structural dimensions
    keep the full text) — same mechanic as genre exempt terms (#42).
  - weight_overrides: merged over DEFAULT_WEIGHTS (values are floats,
    no re-normalization — the scorer caps at 1.0 and documents that
    weights intentionally sum > 1).

Public surface:
    load_config(path) -> dict (validated)
    apply_config(slop_score_kwargs, config) -> None (in-place)
    SIGNAL_FAMILIES: valid disabled_signals ids
"""

import json
import os
import sys

# Signal families that can be disabled. Weighted-dimension ids map 1:1 to
# DEFAULT_WEIGHTS keys; adverb/copula/provenance are the conditional
# contribution families from slop_score().
_SIGNAL_FAMILIES = [
    "density", "repetition", "burstiness", "buzzwords", "phrases",
    "punctuation", "trailing_moral", "list_heavy", "fake_authority",
    "verbosity", "multilingual", "mirrored", "structural", "portability",
    # conditional contributions (weights.get(...) in slop_score)
    "adverb", "copula", "provenance",
]

# Families whose exclusion is implemented via the learning-store exemption
# mechanic (empty matches -> no escalation, no floor).
_EXEMPTABLE_FAMILIES = {
    "buzzwords", "phrases", "multilingual", "provenance", "trailing_moral",
    "mirrored", "fake_authority", "portability",
}

DEFAULT_CONFIG_NAME = "slop.json"

# Exposed for validation and docs/tests.
SIGNAL_FAMILIES = tuple(sorted(_SIGNAL_FAMILIES))


def load_config(path: str) -> dict:
    """Load and validate a project config file. Returns {}-shaped dict."""
    with open(path, encoding="utf-8") as f:
        try:
            raw = json.load(f)
        except json.JSONDecodeError as e:
            raise SystemExit(f"config error: {path} is not valid JSON: {e}")
    if not isinstance(raw, dict):
        raise SystemExit(f"config error: {path} must be a JSON object")

    unknown_keys = set(raw) - {"disabled_signals", "term_allowlist",
                               "weight_overrides"}
    if unknown_keys:
        raise SystemExit(
            f"config error: {path} unknown keys: {sorted(unknown_keys)} "
            "(supported: disabled_signals, term_allowlist, weight_overrides)")

    cfg = {"disabled_signals": [], "term_allowlist": [], "weight_overrides": {}}

    ds = raw.get("disabled_signals", [])
    if not isinstance(ds, list) or not all(isinstance(s, str) for s in ds):
        raise SystemExit(f"config error: {path} disabled_signals must be a list of strings")
    bad = [s for s in ds if s not in _SIGNAL_FAMILIES]
    if bad:
        raise SystemExit(
            f"config error: {path} unknown signal families: {bad} "
            f"(valid: {', '.join(SIGNAL_FAMILIES)})")
    cfg["disabled_signals"] = list(ds)

    ta = raw.get("term_allowlist", [])
    if not isinstance(ta, list) or not all(isinstance(t, str) for t in ta):
        raise SystemExit(f"config error: {path} term_allowlist must be a list of strings")
    if any(not t.strip() for t in ta):
        raise SystemExit(f"config error: {path} term_allowlist entries must be non-empty")
    cfg["term_allowlist"] = list(ta)

    wo = raw.get("weight_overrides", {})
    if not isinstance(wo, dict):
        raise SystemExit(f"config error: {path} weight_overrides must be an object")
    from slop_scorer import DEFAULT_WEIGHTS
    bad_w = [k for k in wo if k not in DEFAULT_WEIGHTS]
    if bad_w:
        raise SystemExit(
            f"config error: {path} unknown weight keys: {bad_w} "
            f"(valid: {', '.join(sorted(DEFAULT_WEIGHTS))})")
    for k, v in wo.items():
        if not isinstance(v, (int, float)) or isinstance(v, bool) or v < 0:
            raise SystemExit(f"config error: {path} weight_overrides.{k} must be a number >= 0")
    cfg["weight_overrides"] = dict(wo)
    return cfg


def auto_discover(directory: str) -> str:
    """Find a slop.json in/above a directory (like .git / package.json).

    Returns the path or "" when none exists. Explicit --config wins;
    auto-discovery only runs for --file input so piped text stays
    environment-independent.
    """
    d = os.path.abspath(directory)
    while True:
        candidate = os.path.join(d, DEFAULT_CONFIG_NAME)
        if os.path.isfile(candidate):
            return candidate
        parent = os.path.dirname(d)
        if parent == d:
            return ""
        d = parent
