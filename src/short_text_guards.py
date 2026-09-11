"""Short-text guards: documented minimum lengths per metric (upstream #52 / BS-KRITISCH).

Problem: statistical metrics degrade or become undefined on short inputs.
``std_dev`` over <3 sentences is 0/undefined, "per sentence" rates explode on
a single-sentence text (one em-dash => rate 1.0), and type-token ratios
(density, repetition) are trivially extreme on 5-word texts. Without guards
this produces false positives on tweets, commit titles, and PR descriptions.

Behavior (issue #52: "definiertes Verhalten für Kurztexte"):
- A metric below its minimum input size is *skipped*: it contributes 0 to
  the score and is reported explicitly in the result as skipped (with the
  violated minimum), never silently zeroed.
- Skipped metric weights are re-normalized over the remaining active
  weights, so a 6-metric text and a 3-metric text produce comparable
  ``overall`` values.

Minimum lengths live in ``config/threshold.json`` under
``short_text_guards`` (single source of truth, same file as the decision
threshold). A missing section aborts loudly via :mod:`threshold_config`'s
philosophy — no silent defaults.

Rationale for the numbers (documented, measurable):
- ``min_words_density: 40`` — type-token ratio stabilizes only above ~40
  tokens; below that a 5-word unique text scores density 1.0 trivially.
- ``min_words_repetition: 20`` — a most-common-token share over 20 tokens
  is meaningful; below, one repeated stopword dominates.
- ``min_sentences_burstiness: 3`` — std_dev needs >=3 samples to be an
  estimate at all (matches the existing scorer guard).
- ``min_words_burstiness: 30`` — three 5-word sentences give std_dev 0 by
  construction even for human text.
- ``min_sentences_punctuation: 2`` — per-sentence rates on a single
  sentence are binary (0.0 or 1.0), not rates.
- ``min_words_trailing_moral: 15`` — the 200-char tail window covers the
  whole text below ~15 words, so any occurrence fires regardless of
  position.
- ``min_lines_list_heavy: 4`` — matches the existing ``len(lines) > 3``
  guard, made explicit.
"""

import json
import os
import re
import sys
from typing import Optional

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CONFIG_PATH = os.path.join(ROOT, "config", "threshold.json")

REQUIRED_KEYS = {
    "min_words_density": int,
    "min_words_repetition": int,
    "min_sentences_burstiness": int,
    "min_words_burstiness": int,
    "min_sentences_punctuation": int,
    "min_words_trailing_moral": int,
    "min_lines_list_heavy": int,
}


class ShortTextGuardConfigError(SystemExit):
    """Raised (as exit) on missing/invalid guard config — never a silent default."""


def load_short_text_guards(path: str = CONFIG_PATH) -> dict:
    """Return the short-text guard minimums from config/threshold.json.

    Aborts loudly when the ``short_text_guards`` section is missing or
    malformed, mirroring threshold_config.load_threshold.
    """
    if not os.path.isfile(path):
        sys.exit(f"threshold config missing: {path} (short_text_guards needs it)")
    try:
        with open(path, encoding="utf-8") as fh:
            data = json.load(fh)
    except json.JSONDecodeError as exc:
        sys.exit(f"threshold config is not valid JSON ({path}): {exc}")

    guards = data.get("short_text_guards")
    if not isinstance(guards, dict):
        sys.exit(
            f'threshold config ({path}) lacks a "short_text_guards" section. '
            "Restore it — per-metric minimum lengths (upstream #52) must not "
            "fall back to silent defaults."
        )
    for key, typ in REQUIRED_KEYS.items():
        value = guards.get(key)
        if not isinstance(value, typ) or isinstance(value, bool) or value < 1:
            sys.exit(
                f'short_text_guards.{key} must be a positive integer in {path} '
                f"(got {value!r})"
            )
    return guards


def text_stats(text: str) -> dict:
    """Cheap shared tokenization stats used by the guard checks."""
    words = re.findall(r"\b\w+\b", text.lower())
    sentences = [s for s in re.split(r"[.!?\n]+", text) if s.strip()]
    lines = [l for l in text.strip().split("\n") if l.strip()]
    return {
        "words": len(words),
        "sentences": len(sentences),
        "lines": len(lines),
    }


def active_metrics(text: str, guards: dict) -> tuple[dict, list]:
    """Decide per metric whether it may run on ``text``.

    Returns ``(active, skipped)`` where ``active`` maps metric name ->
    bool and ``skipped`` is a list of dicts
    ``{"metric": name, "reason": "words<N", "minimum": N}``
    for every metric that must not contribute to the score.
    """
    stats = text_stats(text)
    rules = {
        "density": stats["words"] >= guards["min_words_density"],
        "repetition": stats["words"] >= guards["min_words_repetition"],
        "burstiness": (
            stats["sentences"] >= guards["min_sentences_burstiness"]
            and stats["words"] >= guards["min_words_burstiness"]
        ),
        "punctuation": stats["sentences"] >= guards["min_sentences_punctuation"],
        "trailing_moral": stats["words"] >= guards["min_words_trailing_moral"],
        "list_heavy": stats["lines"] >= guards["min_lines_list_heavy"],
    }
    # buzzwords is count-based (absolute hit count), not normalized per
    # length — it stays active on short texts by design.
    reasons = {
        "density": (f"words<{guards['min_words_density']}", guards["min_words_density"]),
        "repetition": (f"words<{guards['min_words_repetition']}", guards["min_words_repetition"]),
        "burstiness": (
            f"sentences<{guards['min_sentences_burstiness']}",
            guards["min_sentences_burstiness"],
        ),
        "punctuation": (f"sentences<{guards['min_sentences_punctuation']}", guards["min_sentences_punctuation"]),
        "trailing_moral": (f"words<{guards['min_words_trailing_moral']}", guards["min_words_trailing_moral"]),
        "list_heavy": (f"lines<{guards['min_lines_list_heavy']}", guards["min_lines_list_heavy"]),
    }
    skipped = [
        {"metric": m, "reason": r, "minimum": mn}
        for m, ok in rules.items()
        if not ok
        for r, mn in [reasons[m]]
    ]
    return rules, skipped
