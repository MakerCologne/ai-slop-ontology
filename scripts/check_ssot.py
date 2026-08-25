#!/usr/bin/env python3
"""
Issue #49 — SSOT check: ontology.json is the source of truth.

Offline gate (no network, no API). Fails with exit 1 on any drift:

  C1  The skill's vendored ontology copy
      (skills/ai-slop-detection/references/ontology.json) must be
      byte-identical to the root ontology.json.

  C2  src/signal_defs_generated.py must be byte-identical to what
      scripts/generate_signal_defs.py would produce now (stale generated
      view = drift).

  C3  Every signal-bearing top-level constant (ALL_CAPS list/dict) in the
      detection modules must appear in SSOT_REGISTER below with a source
      and status. New inline signal lists without a register entry fail
      the gate — adding signals is a conscious, documented decision.

ALLOWLIST documents the *conscious deviations*: the corpus-calibrated
phrase/buzzword lists mined from eval/corpus.jsonl (Batch F evidence
discipline) deliberately do NOT live in ontology.json — ontology.json
describes signal *concepts*, the scripts carry the calibrated *match
data*. Full migration of the match data into ontology.json (schema-first
SSOT, generated matching lists) is the documented follow-up; until then
the register below is the single place that records which list has which
source.

Run:  python3 scripts/check_ssot.py
"""

import ast
import difflib
import io
import os
import sys

ROOT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..")
sys.path.insert(0, os.path.join(ROOT, "scripts"))

import generate_signal_defs  # noqa: E402

# Modules whose top-level ALL_CAPS constants carry signal/matching data.
SIGNAL_MODULES = [
    "skills/ai-slop-detection/scripts/slop_scorer.py",
    "skills/ai-slop-detection/scripts/quantifiers.py",
    "skills/ai-slop-detection/scripts/micro_patterns.py",
    "skills/ai-slop-detection/scripts/proof_metrics.py",
    "skills/ai-slop-detection/scripts/instruction_slop.py",
    "skills/ai-slop-detection/scripts/rhetorical_patterns.py",
    "skills/ai-slop-detection/scripts/anchor_diff.py",
]

# "source" values:
#   ontology.json      — data mirrored from (or checked against) the ontology
#   corpus-calibrated  — mined/calibrated from eval/corpus.jsonl (Batch F
#                        evidence discipline, tests/test_fn_series_signals.py);
#                        intentionally NOT an ontology.json copy
#   engine-config      — thresholds/tuning constants of the scoring engine,
#                        pinned by behavioral tests (tests/test_engine_sync.py)
# "status": synced | deviation (deviation requires an ALLOWLIST note)
SSOT_REGISTER = {
    "slop_scorer.py": {
        "BUZZWORD_TIERS": ("corpus-calibrated", "deviation"),
        "PHRASE_CATEGORIES": ("corpus-calibrated", "deviation"),
        "MULTILINGUAL_BUZZWORDS": ("corpus-calibrated", "synced-via-check_consistency"),
        "STRUCTURAL_INDICATORS": ("corpus-calibrated", "deviation"),
        "MORAL_PATTERNS": ("corpus-calibrated", "deviation"),
        "AUTHORITY_PATTERNS": ("corpus-calibrated", "deviation"),
        "STOPWORDS": ("engine-config", "deviation"),
        "SUBSTITUTE_VERB_PATTERNS": ("corpus-calibrated", "deviation"),
        "ADVERB_RATE_THRESHOLD": ("engine-config", "deviation"),
        "ADVERB_MIN_WORDS": ("engine-config", "deviation"),
        "INTENSIFIERS": ("corpus-calibrated", "deviation"),
        "DECISION_THRESHOLD": ("engine-config", "synced"),
    },
    "quantifiers.py": {
        "UNIVERSAL_QUANTIFIERS": ("corpus-calibrated", "deviation"),
        "AUTHORITY_CLAIMS": ("corpus-calibrated", "deviation"),
        "COUNTED_SOURCE": ("corpus-calibrated", "deviation"),
        "CITATION_MARKERS": ("corpus-calibrated", "deviation"),
        "RULE_SECTION_HEADINGS": ("corpus-calibrated", "deviation"),
        "IMPERATIVE_LEAD": ("corpus-calibrated", "deviation"),
    },
    "micro_patterns.py": {
        "INANIMATE_SUBJECTS": ("corpus-calibrated", "deviation"),
        "HUMAN_VERBS": ("corpus-calibrated", "deviation"),
        "FINANCE_OBJECTS": ("corpus-calibrated", "deviation"),
        "GRAND_ENDPOINTS": ("corpus-calibrated", "deviation"),
        "RECAP_OPENERS": ("corpus-calibrated", "deviation"),
        "MICRO_PATTERNS": ("corpus-calibrated", "deviation"),
    },
    "proof_metrics.py": {
        "METRIC_NUMBERS": ("corpus-calibrated", "deviation"),
        "SOURCE_REFS": ("corpus-calibrated", "deviation"),
        "CLAIM_CONTEXT": ("corpus-calibrated", "deviation"),
        "CONTEXT_RADIUS": ("engine-config", "deviation"),
    },
    "instruction_slop.py": {
        "GENERIC_ADVICE": ("corpus-calibrated", "deviation"),
        "OBVIOUS_RULES": ("corpus-calibrated", "deviation"),
        "TOO_VAGUE": ("corpus-calibrated", "deviation"),
    },
    "rhetorical_patterns.py": {
        "RHETORICAL_PATTERNS": ("corpus-calibrated", "deviation"),
    },
    "anchor_diff.py": {
        "AUTHORITY_CARRIERS": ("closed-list", "deviation"),
    },
}

# ALLOWLIST — conscious deviations (C3): why these lists do not come from
# ontology.json. Compiled regexes / private helpers (_UPPERCASE) are
# implementation detail, not signal inventories, and are skipped.
ALLOWLIST_NOTES = [
    "Phrase/buzzword match data is corpus-calibrated against "
    "eval/corpus.jsonl (evidence discipline: >=3 slop texts, 0 clean texts; "
    "enforced by tests/test_fn_series_signals.py). ontology.json models "
    "signal concepts, not English/German match strings.",
    "engine-config thresholds (DECISION_THRESHOLD, ADVERB_*, STOPWORDS) are "
    "calibration outputs (eval/calibrate.py, #23/#24), pinned by "
    "tests/test_engine_sync.py; they are engine state, not ontology data.",
    "MULTILINGUAL_BUZZWORDS is the one ontology-adjacent list: language sets "
    "are cross-checked by scripts/check_consistency.py (status "
    "synced-via-check_consistency).",
    "Compiled regex constants (COUNTED_SOURCE, CITATION_MARKERS, "
    "CLAIM_CONTEXT, SOURCE_REFS) are matcher implementations of registered "
    "concepts — registered as corpus-calibrated data, not separate signal "
    "inventories. Private helpers (_UPPERCASE) are skipped as implementation "
    "detail.",
    "AUTHORITY_CARRIERS (anchor_diff, #78) is a closed EN/DE authority-marker "
    "word list self-derived for the drift heuristic (concept from the "
    "evidence-ledger reference, deep/11; no third-party pattern material "
    "copied). detect-only, never score-dominant — deviation registered.",
]

SKIPPED_CONSTANT_KINDS = "compiled regex / private helper (see ALLOWLIST)"


def _top_level_signal_constants(path: str) -> dict:
    """Map constant name -> kind for signal-bearing top-level assignments."""
    with open(path, encoding="utf-8") as fh:
        tree = ast.parse(fh.read())
    found = {}
    for node in tree.body:
        targets = []
        if isinstance(node, ast.Assign):
            targets = [t for t in node.targets if isinstance(t, ast.Name)]
        elif isinstance(node, ast.AnnAssign) and isinstance(node.target, ast.Name):
            targets = [node.target]
        for target in targets:
            name = target.id
            if not name.isupper():
                continue
            value = node.value
            if isinstance(value, (ast.List, ast.Dict, ast.Set, ast.Tuple)):
                found[name] = "list/dict"
            elif isinstance(value, (ast.Call, ast.Subscript)):
                # re.compile(...) or a pull from another module's THRESHOLDS —
                # still a module-level signal/threshold constant.
                found[name] = "computed"
            elif (isinstance(value, ast.Constant)
                  and isinstance(value.value, (int, float))
                  and not isinstance(value.value, bool)):
                found[name] = "numeric threshold"
    return found


def check_skill_ontology_copy(errors: list) -> None:
    root_path = os.path.join(ROOT, "ontology.json")
    copy_path = os.path.join(
        ROOT, "skills", "ai-slop-detection", "references", "ontology.json")
    with open(root_path, "rb") as fh:
        root_bytes = fh.read()
    with open(copy_path, "rb") as fh:
        copy_bytes = fh.read()
    if root_bytes != copy_bytes:
        errors.append(
            "C1 FAIL: skills/ai-slop-detection/references/ontology.json "
            "differs from root ontology.json — copy the file or regenerate "
            "the skill bundle.")


def check_generated_defs(errors: list) -> None:
    import json
    with open(os.path.join(ROOT, "ontology.json"), encoding="utf-8") as fh:
        ontology = json.load(fh)
    expected = generate_signal_defs.render(generate_signal_defs.build_defs(ontology))
    target = os.path.join(ROOT, "src", "signal_defs_generated.py")
    if not os.path.exists(target):
        errors.append(
            "C2 FAIL: src/signal_defs_generated.py missing — run "
            "scripts/generate_signal_defs.py")
        return
    with open(target, encoding="utf-8") as fh:
        current = fh.read()
    if current != expected:
        diff = "\n".join(list(difflib.unified_diff(
            current.splitlines(), expected.splitlines(),
            "committed", "regenerated", lineterm=""))[:20])
        errors.append(
            "C2 FAIL: src/signal_defs_generated.py is stale — run "
            f"scripts/generate_signal_defs.py\n{diff}")


def check_register(errors: list) -> None:
    for rel in SIGNAL_MODULES:
        module = os.path.basename(rel)
        register = SSOT_REGISTER.get(module, {})
        path = os.path.join(ROOT, rel)
        constants = _top_level_signal_constants(path)
        for name, kind in sorted(constants.items()):
            if kind == "computed" or name.startswith("_"):
                # computed pull-throughs (DECISION_THRESHOLD etc.) are
                # registered but implemented as pulls — allowed; private
                # helpers are implementation detail (see ALLOWLIST)
                if name.startswith("_"):
                    continue
            if name not in register:
                errors.append(
                    f"C3 FAIL: {module}:{name} ({kind}) is not in the SSOT "
                    "register of scripts/check_ssot.py — register it with a "
                    "source and status (conscious decision), or move the "
                    "data into ontology.json.")
        for name in register:
            if name not in constants:
                errors.append(
                    f"C3 FAIL: {module}:{name} registered but no longer "
                    "exists — remove the stale register entry.")


def main() -> int:
    errors = []
    check_skill_ontology_copy(errors)
    check_generated_defs(errors)
    check_register(errors)

    if errors:
        print("SSOT check FAILED:")
        for err in errors:
            print(f"  - {err}")
        return 1

    registered = sum(len(v) for v in SSOT_REGISTER.values())
    print(f"SSOT check passed (C1 copy-identical, C2 generated view current, "
          f"C3 {registered} signal constants registered, "
          f"{len(ALLOWLIST_NOTES)} documented deviation groups).")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
