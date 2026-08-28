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
    "skills/ai-slop-detection/scripts/naturalness_guard.py",
    "skills/ai-slop-detection/scripts/de_typography.py",
    "skills/ai-slop-detection/scripts/structure_metrics.py",
    "skills/ai-slop-detection/scripts/register_profile.py",
    "skills/ai-slop-detection/scripts/discourse_metrics.py",
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
        "DEFAULT_WEIGHTS": ("engine-config", "calibration-output"),
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
    "de_typography.py": {
        "_DE_FUNCTION_WORDS": ("closed-list", "deviation"),
        "_CAP_FUNCTION_WORDS": ("closed-list", "deviation"),
        "_EN_MONTH_DATE": ("closed-list", "deviation"),
        "_BRAND_ALLOWLIST": ("closed-list", "deviation"),
    },
    "structure_metrics.py": {
        "SYNONYM_FAMILIES": ("closed-list", "deviation"),
        "MIN_DISTINCT_MEMBERS": ("engine-config", "fixture-calibrated"),
        "MIN_TOTAL_MENTIONS": ("engine-config", "fixture-calibrated"),
        "MIN_WORDS_ROTATION": ("engine-config", "fixture-calibrated"),
        "MIN_UNITS": ("engine-config", "fixture-calibrated"),
        "MAX_STDEV_UNITS": ("engine-config", "fixture-calibrated"),
        "MIN_WORDS_ISOMETRY": ("engine-config", "fixture-calibrated"),
        "FAKE_ANALYSIS_PATTERNS": ("closed-list", "deviation"),
        "PSEUDO_NUANCE_MARKERS": ("closed-list", "deviation"),
        "MIN_FAKE_ANALYSIS_HITS": ("engine-config", "fixture-calibrated"),
        "MIN_NUANCE_MARKERS": ("engine-config", "fixture-calibrated"),
        "MIN_WORDS_FAKE_ANALYSIS": ("engine-config", "fixture-calibrated"),
        "MIN_WORDS_NUANCE": ("engine-config", "fixture-calibrated"),
    },
    "naturalness_guard.py": {
        "FORMAL_MARKERS": ("closed-list", "deviation"),
        "COLLOQUIAL_MARKERS": ("closed-list", "deviation"),
        "FULL_FORMS": ("closed-list", "deviation"),
        "FORMAL_GENRES": ("engine-config", "synced-via-genre_profiles"),
        "MIN_WORDS_REGISTER": ("engine-config", "fixture-calibrated"),
        "MIN_WORDS_SANITIZED": ("engine-config", "fixture-calibrated"),
        "MIN_FULL_FORMS": ("engine-config", "fixture-calibrated"),
    },
    "register_profile.py": {
        "IMPERATIVE_STARTERS": ("closed-list", "deviation"),
        "MODAL_PARTICLES_DE": ("closed-list", "deviation"),
        "HEDGE_PARTICLES": ("closed-list", "deviation"),
        "INTENSIFIER_PARTICLES": ("closed-list", "deviation"),
        "REGISTER_DRIFT_EXEMPT_GENRES": ("engine-config", "synced-via-genre_profiles"),
        "MIN_WORDS_DRIFT": ("engine-config", "fixture-calibrated"),
        "MIN_MARKERS_PER_HALF": ("engine-config", "fixture-calibrated"),
        "PUNCT_PER_CHARS": ("engine-config", "deviation"),
    },
    "discourse_metrics.py": {
        "RANKED_LINE_RE": ("compiled-regex-matcher", "deviation"),
        "CRITERION_MARKERS": ("closed-list", "deviation"),
        "MIN_RANKED_ITEMS": ("engine-config", "fixture-calibrated"),
        "MIN_ENUM_ITEMS": ("engine-config", "fixture-calibrated"),
        "MAX_ENUM_CONFIDENCE": ("engine-config", "deviation"),
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
    "DEFAULT_WEIGHTS (#85) is the calibration output of eval/calibrate.py "
    "itself — 14 dimension weights, not a signal inventory, so it has no "
    "place in ontology.json. Named rather than inlined so that calibrate.py "
    "and the cross-validation runner read it instead of keeping copies; the "
    "hardcoded copy this replaced had fallen a dimension behind and made "
    "calibrate.py unrunnable (KeyError: 'portability'). Parity of the key "
    "set is pinned by tests/test_cross_validation.py.",
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
    "naturalness_guard (#81) closed marker lists (FORMAL_MARKERS, "
    "COLLOQUIAL_MARKERS, FULL_FORMS) are self-derived EN/DE inventories for "
    "the detect-only advisory signals; MIN_* thresholds are fixture-pinned "
    "(tests/test_naturalness_guard.py). No third-party pattern material "
    "copied (register-profile idea adapted as architecture, deep/11).",
    "structure_metrics (#76 Teil 2) SYNONYM_FAMILIES is a self-derived "
    "closed EN/DE synonym-family inventory for the detect-only M60 "
    "SynonymRotation / M61 IsometricUnits signals (concepts from "
    "docs/de-coverage.md NEU candidates; re-derived from the Wikipedia "
    "project page 'Anzeichen fuer KI-generierte Inhalte' + own examples; "
    "no third-party pattern material copied). MIN_* thresholds are "
    "fixture-pinned (tests/test_structure_metrics.py).",
    "de_typography (#76) closed lists (DE function words, capitalized "
    "function words, EN month names, brand allowlist) are self-derived "
    "DE gate/matcher inventories after de.wikipedia Anzeichen-fuer-KI-"
    "generierte-Inhalte + eigene Beispiele; license-safe re-derivation "
    "(no CC BY-SA pattern material copied), see docs/de-coverage.md.",
    "register_profile (#74) closed lists (IMPERATIVE_STARTERS, "
    "MODAL_PARTICLES_DE, HEDGE_PARTICLES, INTENSIFIER_PARTICLES) are "
    "self-derived EN/DE descriptive inventories for the detect-only "
    "style card; FORMAL/COLLOQUIAL markers are IMPORTED from "
    "naturalness_guard (#81) instead of duplicated. MIN_* thresholds are "
    "fixture-pinned (tests/test_register_profile.py). REGISTER_DRIFT_"
    "EXEMPT_GENRES is synced with the #42 genre-profile conventions. No "
    "third-party pattern material copied.",
    "discourse_metrics (#72) CRITERION_MARKERS is a self-derived EN/DE "
    "closed list of justification markers for the explorative detect-only "
    "rank_without_criterion / identical_enumeration signals (concept from "
    "own deep-dive notes deep/10 + deep/06; reference corpus "
    "eval/discourse_ref.jsonl, versioned). MIN_* thresholds are "
    "fixture-pinned (tests/test_discourse_metrics.py). Short public "
    "quotes in the reference corpus are attributed; no CC BY-SA pattern "
    "material copied.",
]


# --- FU-17 / RI-4: de_*-Phrase-Layer-Pin (C4) -------------------------------
# Bewusster Pin: welche de_*-Kategorien existieren und wie viele Items sie
# haben. Aenderungen am DE-Layer sind damit fuer check_ssot sichtbar (RED in
# der Suite bleibt die erste Verteidigungslinie; C4 macht Drift CI-faehig,
# auch ohne die Test-Datei). Evidence-Regel je Phrase: >= 1 Beleg, Wikipedia
# nur als Projektseiten-URL MIT Namespace-Praefix (/wiki/Wikipedia:...).
DE_LAYER = {
    "de_calque": 6,
    "de_ai_vocab": 6,
    "de_authority_floskel": 6,
    "de_meta_comment": 6,
    "de_transitions": 6,
    "de_recap": 6,
    "de_superlativ": 6,
    "de_symbolik": 6,
    "de_vague_authority": 6,
    "de_participle": 6,
    "de_binary_contrast": 6,
    "de_false_range": 6,
    "de_opening": 6,
    "de_closing": 6,
    "de_hedging": 6,
    "de_announcement_cleft": 6,
}

_DE_WIKI_OK = "/wiki/Wikipedia:Anzeichen"

# RI-2-FU (#76-Rest): mind. 50% der de_*-Phrasen tragen >= 2 unabhaengige
# Belege (Wikipedia-Projektseite + own:corpus-Belegtext u.ae.). Pin als
# Gate, damit Rueckfaelle unter die Zielmarke CI-faehig auffallen.
DE_EVIDENCE_COVERAGE_MIN = 0.50


def check_de_phrase_layer(errors: list) -> tuple:
    import json
    with open(os.path.join(ROOT, "ontology.json"), encoding="utf-8") as fh:
        ontology = json.load(fh)
    categories = (ontology.get("signals", {}).get("text", {})
                      .get("phrases", {}).get("categories", {}))
    de_cats = {c for c in categories if c.startswith("de_")}
    for cat in sorted(de_cats - set(DE_LAYER)):
        errors.append(
            f"C4 FAIL: de_*-Kategorie '{cat}' ist nicht im DE_LAYER-Pin "
            "dieses Checks — Pin bewusst erweitern (SSOT-Entscheidung "
            "dokumentieren) oder Kategorie entfernen.")
    for cat, n_items in sorted(DE_LAYER.items()):
        if cat not in categories:
            errors.append(
                f"C4 FAIL: gepinnte de_*-Kategorie '{cat}' fehlt in "
                "ontology.json — Pin aktualisieren oder Kategorie "
                "wiederherstellen.")
            continue
        data = categories[cat]
        items = data.get("items", [])
        if len(items) < n_items:
            errors.append(
                f"C4 FAIL: {cat} hat nur {len(items)} Items, Pin erwartet "
                f">= {n_items} — Phrasen geloescht? Pin bewusst anpassen.")
        evidence = data.get("evidence", {})
        for phrase in items:
            sources = evidence.get(phrase, [])
            if not sources:
                errors.append(
                    f"C4 FAIL: {cat}:{phrase} ohne Evidence (RI-2: >= 1 "
                    "Beleg je Phrase; >= 2 als FU offen dokumentiert).")
                continue
            for src in sources:
                source = src.get("source", "")
                if source.startswith("https://de.wikipedia.org"):
                    if _DE_WIKI_OK not in source:
                        errors.append(
                            f"C4 FAIL: {cat}:{phrase} Wikipedia-Beleg ohne "
                            "Namespace-Präfix (muss Projektseite "
                            "'/wiki/Wikipedia:Anzeichen...' sein, RI-1): "
                            f"{source}")

    # RI-2-FU: Evidence-Verdichtung — >= 2 Belege fuer >= 50% der Phrasen.
    total = 0
    multi = 0
    for cat in sorted(DE_LAYER):
        data = categories.get(cat)
        if not data:
            continue  # fehlende Kategorie wurde oben bereits gemeldet
        evidence = data.get("evidence", {})
        for phrase in data.get("items", []):
            total += 1
            if len(evidence.get(phrase, [])) >= 2:
                multi += 1
    if total and multi / total < DE_EVIDENCE_COVERAGE_MIN:
        errors.append(
            f"C4 FAIL: nur {multi}/{total} de_*-Phrasen mit >= 2 Evidence-"
            f"Belegen — RI-2-FU-Pin verlangt >= "
            f"{int(DE_EVIDENCE_COVERAGE_MIN * 100)}% (Rest bleibt "
            "dokumentierte Abweichung, siehe docs/de-coverage.md).")
    return multi, total


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
    multi, total = check_de_phrase_layer(errors)

    if errors:
        print("SSOT check FAILED:")
        for err in errors:
            print(f"  - {err}")
        return 1

    registered = sum(len(v) for v in SSOT_REGISTER.values())
    print(f"SSOT check passed (C1 copy-identical, C2 generated view current, "
          f"C3 {registered} signal constants registered, "
          f"{len(ALLOWLIST_NOTES)} documented deviation groups; "
          f"C4 de_*-Phrase-Layer: {len(DE_LAYER)} Kategorien gepinnt; "
          f"evidence >= 2 Belege fuer {multi}/{total} der de_*-Phrasen "
          f"(RI-2-FU-Pin >= {int(DE_EVIDENCE_COVERAGE_MIN * 100)}%).")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
