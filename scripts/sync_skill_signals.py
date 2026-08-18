#!/usr/bin/env python3
"""
Regenerate the skill scorer's inlined signal data from ontology.json.

The agent skill must stay self-contained — it is copied into agent
environments without the repo — so it carries its own copies of the buzzword
tiers, phrase categories, authority patterns and multilingual markers. Those
copies drifted from the canonical database (review 2026-08 §1.3): a buzzword
in two different tiers, one missing from each side, a duplicate, and phrase
entries in two different spellings.

This script is the single writer of those literals; scripts/check_consistency.py
fails CI when they no longer match ontology.json. Hand-edit ontology.json, then
run this.

Usage:  python3 scripts/sync_skill_signals.py [--check]
"""

import json
import os
import re
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SKILL = os.path.join(ROOT, "skills", "ai-slop-detection", "scripts", "slop_scorer.py")

# authority_claims is scored as its own dimension (fake_authority) in the skill
# rather than inside the phrase aggregate, so it lives in its own literal —
# same data, different weighting path.
AUTHORITY_CATEGORY = "authority_claims"


def _items(indent: str, values: list, width: int = 79) -> str:
    """Render string literals wrapped to `width` columns."""
    lines, cur = [], indent
    for i, v in enumerate(values):
        piece = json.dumps(v, ensure_ascii=False) + ("," if i < len(values) - 1 else "")
        if cur != indent and len(cur) + 1 + len(piece) > width:
            lines.append(cur)
            cur = indent + piece
        else:
            cur = piece if cur == indent else cur + " " + piece
            if cur == piece:
                cur = indent + piece
    lines.append(cur)
    return "\n".join(lines)


def render(ontology: dict) -> dict:
    text = ontology["signals"]["text"]

    tiers = []
    for name, data in text["buzzwords"]["tiers"].items():
        tiers.append(
            f'    "{name}": {{\n'
            f'        "confidence": {data["confidence"]},\n'
            f'        "words": [\n{_items("            ", data["words"])}\n'
            f'        ]\n'
            f'    }},'
        )
    buzzwords = "BUZZWORD_TIERS = {\n" + "\n".join(tiers) + "\n}"

    cats = []
    for name, data in text["phrases"]["categories"].items():
        if name == AUTHORITY_CATEGORY:
            continue
        cats.append(
            f'    "{name}": {{\n'
            f'        "confidence": {data["confidence"]},\n'
            f'        "phrases": [\n{_items("            ", data["items"])}\n'
            f'        ]\n'
            f'    }},'
        )
    phrases = "PHRASE_CATEGORIES = {\n" + "\n".join(cats) + "\n}"

    auth = text["phrases"]["categories"][AUTHORITY_CATEGORY]["items"]
    authority = (
        "AUTHORITY_PATTERNS = [\n" + _items("    ", auth) + "\n]"
    )

    langs = []
    for name, data in ontology["signals"]["multilingual"].items():
        if not (isinstance(data, dict) and "buzzwords" in data):
            continue
        langs.append(
            f'    "{name}": [\n{_items("        ", data["buzzwords"])}\n    ],'
        )
    multilingual = "MULTILINGUAL_BUZZWORDS = {\n" + "\n".join(langs) + "\n}"

    return {
        "BUZZWORD_TIERS": buzzwords,
        "PHRASE_CATEGORIES": phrases,
        "AUTHORITY_PATTERNS": authority,
        "MULTILINGUAL_BUZZWORDS": multilingual,
    }


def replace_block(source: str, name: str, block: str) -> str:
    """Replace `NAME = {...}` / `NAME = [...]` up to the closing brace in col 0."""
    pattern = re.compile(
        rf"^{name} = [\{{\[].*?^[\}}\]]$", re.MULTILINE | re.DOTALL)
    new, n = pattern.subn(lambda _: block, source, count=1)
    if n != 1:
        raise SystemExit(f"could not locate literal {name} in {SKILL}")
    return new


def main(argv=None) -> int:
    argv = sys.argv[1:] if argv is None else argv
    check_only = "--check" in argv

    with open(os.path.join(ROOT, "ontology.json"), encoding="utf-8") as f:
        ontology = json.load(f)
    with open(SKILL, encoding="utf-8") as f:
        source = f.read()

    updated = source
    for name, block in render(ontology).items():
        updated = replace_block(updated, name, block)

    if updated == source:
        print("skill signal data already in sync with ontology.json")
        return 0
    if check_only:
        print("skill signal data is OUT OF SYNC — run scripts/sync_skill_signals.py")
        return 1
    with open(SKILL, "w", encoding="utf-8") as f:
        f.write(updated)
    print(f"rewrote signal literals in {os.path.relpath(SKILL, ROOT)}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
