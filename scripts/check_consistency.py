#!/usr/bin/env python3
"""
Consistency checker for the three ontology serializations.

ontology.json is the source of truth; ontology.ttl and ai_slop_ontology.yaml
are maintained by hand. This script fails (exit 1) when they drift on the
facts that matter:

  - every DOMAIN_SLOP / TEXT_SLOP type in JSON exists in the TTL
  - dc:date matches between JSON and TTL
  - the YAML ontology version matches the canonical document's front matter
  - multilingual language sets match between ontology.json and the skill scorer

Run:  python3 scripts/check_consistency.py
"""

import json
import os
import re
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, "skills", "ai-slop-detection", "scripts"))

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

    # 1. Slop types present in the TTL
    json_types = set(oj["slopTypes"].get("DOMAIN_SLOP", {})) | set(
        oj["slopTypes"].get("TEXT_SLOP", {})
    )
    for t in sorted(json_types):
        check(f":{t} a :SlopType" in ttl,
              f"TTL drift: slop type '{t}' from ontology.json missing in ontology.ttl")

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

    # 6. Rhetorical (detect-only) patterns match between JSON DB and skill module
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
    print(f"Consistency check passed ({len(json_types)} slop types, "
          f"{len(json_pattern_types)} pattern-bearing types, "
          f"{len(json_rhetorical)} rhetorical patterns, "
          f"{len(json_langs)} languages, dates and versions aligned).")
    return 0


if __name__ == "__main__":
    sys.exit(main())
