#!/usr/bin/env python3
"""
Consistency checker for the three ontology serializations.

ontology.json is the source of truth; ontology.ttl and ai_slop_ontology.yaml
are maintained by hand. This script fails (exit 1) when they drift on the
facts that matter:

  - the slop types in JSON and TTL are the same set (both directions)
  - dc:date matches between JSON and TTL
  - the YAML ontology version matches the canonical document's front matter
  - multilingual language sets match between ontology.json and the skill scorer
  - the skill's inlined signal data still equals what ontology.json generates

Run:  python3 scripts/check_consistency.py
"""

import json
import os
import re
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, "skills", "ai-slop-detection", "scripts"))
sys.path.insert(0, os.path.join(ROOT, "scripts"))

errors = []


def check(condition: bool, message: str):
    if not condition:
        errors.append(message)


def main() -> int:
    with open(os.path.join(ROOT, "ontology.json")) as f:
        oj = json.load(f)
    with open(os.path.join(ROOT, "ontology.ttl")) as f:
        ttl = f.read()
    with open(os.path.join(ROOT, "AI-SLOP-ONTOLOGY.md")) as f:
        canonical = f.read()

    # 1. Slop types agree in BOTH directions.
    #    Comparing only TEXT_SLOP and DOMAIN_SLOP used to hide 13 JSON types
    #    absent from the TTL and 12 TTL-only ones, five of which were the same
    #    concept under a second name (review 2026-08).
    #
    #    BY_FORM holds axes (surreal↔banal, mass↔personalized), not types.
    #    WorkSlopFamily/AIWorkslop are defined by the human-work-seo-slop
    #    extension; the core TTL only references them from the harm graph.
    AXIS_GROUPS = {"BY_FORM"}
    EXTENSION_OWNED = {"WorkSlopFamily", "AIWorkslop"}

    json_types = {t for group, types in oj["slopTypes"].items()
                  if group not in AXIS_GROUPS for t in types}
    ttl_types = set(re.findall(r"^:([A-Za-z0-9_]+) a :SlopType", ttl, re.MULTILINE))

    for t in sorted(json_types - ttl_types):
        check(False,
              f"TTL drift: slop type '{t}' from ontology.json missing in ontology.ttl")
    for t in sorted(ttl_types - json_types - EXTENSION_OWNED):
        check(False,
              f"JSON drift: slop type '{t}' from ontology.ttl missing in ontology.json")

    # 2. Dates aligned
    ttl_date = re.search(r'dc:date "([\d-]+)"', ttl)
    check(ttl_date and ttl_date.group(1) == oj["dc:date"],
          f"Date drift: ontology.json={oj['dc:date']} vs ontology.ttl="
          f"{ttl_date.group(1) if ttl_date else 'missing'}")

    # 3. YAML version matches the canonical document front matter
    md_version = re.search(r'^version: "([^"]+)"', canonical, re.MULTILINE)
    try:
        import yaml
        with open(os.path.join(ROOT, "ai_slop_ontology.yaml")) as f:
            oy = yaml.safe_load(f)
        check(md_version and oy["ontology"]["version"] == md_version.group(1),
              f"Version drift: ai_slop_ontology.yaml={oy['ontology']['version']} vs "
              f"AI-SLOP-ONTOLOGY.md={md_version.group(1) if md_version else 'missing'}")
    except ImportError:
        print("note: pyyaml not installed, skipping YAML version check")

    # 4. Type patterns match between JSON DB and skill classifier
    import slop_classifier
    skill_pattern_types = {name for name, td in
                           slop_classifier.SLOP_TYPE_PATTERNS.items() if td["patterns"]}
    json_pattern_types = set(
        oj["signals"]["text"].get("typePatterns", {}).get("types", {}))
    check(skill_pattern_types == json_pattern_types,
          f"Type-pattern drift: skill classifier={sorted(skill_pattern_types)} vs "
          f"ontology.json typePatterns={sorted(json_pattern_types)}")

    # 5. Multilingual coverage matches between JSON DB and skill scorer
    import slop_scorer
    json_langs = {k for k, v in oj["signals"]["multilingual"].items()
                  if isinstance(v, dict) and "buzzwords" in v}
    skill_langs = set(slop_scorer.MULTILINGUAL_BUZZWORDS)
    check(json_langs == skill_langs,
          f"Multilingual drift: ontology.json={sorted(json_langs)} vs "
          f"skill scorer={sorted(skill_langs)}")

    # 6. The skill's inlined signal data is byte-identical to what
    #    ontology.json generates. Buzzword tiers, phrase categories,
    #    authority patterns and multilingual markers had all drifted before
    #    this check existed (review 2026-08 §1.3) — comparing only the
    #    language names or the type-pattern keys never touched them.
    import sync_skill_signals
    check(sync_skill_signals.main(["--check"]) == 0,
          "Skill signal data drifted from ontology.json — "
          "run python3 scripts/sync_skill_signals.py")

    # 7. Rhetorical (detect-only) patterns match between JSON DB and skill module
    import rhetorical_patterns
    skill_rhetorical = set(rhetorical_patterns.RHETORICAL_PATTERNS)
    json_rhetorical = set(
        oj["signals"]["text"].get("rhetoricalPatterns", {}).get("patterns", {}))
    check(skill_rhetorical == json_rhetorical,
          f"Rhetorical-pattern drift: skill module={sorted(skill_rhetorical)} vs "
          f"ontology.json rhetoricalPatterns={sorted(json_rhetorical)}")

    if errors:
        print("CONSISTENCY CHECK FAILED:")
        for e in errors:
            print(f"  ✗ {e}")
        return 1
    n_terms = sum(len(t["words"]) for t in
                  oj["signals"]["text"]["buzzwords"]["tiers"].values())
    n_terms += sum(len(c["items"]) for c in
                   oj["signals"]["text"]["phrases"]["categories"].values())
    print(f"Consistency check passed ({len(json_types)} slop types, "
          f"{len(json_pattern_types)} pattern-bearing types, "
          f"{len(json_rhetorical)} rhetorical patterns, "
          f"{len(json_langs)} languages, {n_terms} signal terms in sync, "
          f"dates and versions aligned).")
    return 0


if __name__ == "__main__":
    sys.exit(main())
