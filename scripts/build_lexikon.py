#!/usr/bin/env python3
"""Deterministic build of the Slop-Lexikon from YAML sources (issue #50).

SSOT: ONLY lexikon/entries/*.yaml is hand-edited. Everything this script
writes (default: lexikon/dist/) is a generated artifact:

  human view : dist/index.md      (alphabetical, narrative, with evidence)
  agent view : dist/lexikon.json  (all entries + content_hash)
               dist/llms.txt      (index, llmstxt.org-style)
               dist/llms-full.txt (full text)

Determinism rules: no timestamps in output (only from source data), sorted
iteration everywhere, canonical JSON (sort_keys, ensure_ascii=False).

The schema check implements the draft-07 subset used by
lexikon/schema/entry.schema.json (type, required, properties, items, enum,
minLength, minItems, pattern, additionalProperties). The jsonschema package
is NOT a repo dependency (see docs/LEXIKON.md).

Sync-Gate: tests/test_lexikon.py rebuilds into a tmp dir and fails if
dist/ differs from the rebuild.

Usage: python3 scripts/build_lexikon.py [--out lexikon/dist] [--check]
  --check: build into a temp dir, exit 1 if it differs from dist/ (CI gate)
"""

import argparse
import hashlib
import json
import os
import re
import shutil
import sys
import tempfile

import yaml

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
LEXIKON = os.path.join(ROOT, "lexikon")
ENTRIES_DIR = os.path.join(LEXIKON, "entries")
SCHEMA_PATH = os.path.join(LEXIKON, "schema", "entry.schema.json")

TYPES = {"object": dict, "array": list, "string": str, "integer": int}


def validate_entry(entry, schema):
    """Validate one entry against the schema subset. Returns error list."""
    errors = []
    _validate(entry, schema, "$", errors)
    return errors


def _validate(value, spec, path, errors):
    t = spec.get("type")
    if t and not isinstance(value, TYPES[t]):
        errors.append(f"{path}: expected {t}, got {type(value).__name__}")
        return
    if "enum" in spec and value not in spec["enum"]:
        errors.append(f"{path}: {value!r} not in enum {spec['enum']}")
    if "pattern" in spec and isinstance(value, str):
        if not re.search(spec["pattern"], value):
            errors.append(f"{path}: {value!r} does not match {spec['pattern']}")
    if "minLength" in spec and isinstance(value, str) and len(value) < spec["minLength"]:
        errors.append(f"{path}: shorter than {spec['minLength']}")
    if "minItems" in spec and isinstance(value, list) and len(value) < spec["minItems"]:
        errors.append(f"{path}: fewer than {spec['minItems']} items")
    if "minimum" in spec and isinstance(value, (int, float)) and value < spec["minimum"]:
        errors.append(f"{path}: below minimum {spec['minimum']}")
    if isinstance(value, dict):
        for req in spec.get("required", []):
            if req not in value:
                errors.append(f"{path}: missing required '{req}'")
        props = spec.get("properties", {})
        if spec.get("additionalProperties") is False:
            for k in value:
                if k not in props:
                    errors.append(f"{path}: additional property '{k}' not allowed")
        for k, v in value.items():
            if k in props:
                _validate(v, props[k], f"{path}.{k}", errors)
    if isinstance(value, list) and "items" in spec:
        for i, item in enumerate(value):
            _validate(item, spec["items"], f"{path}[{i}]", errors)


def load_entries():
    entries = []
    for fn in sorted(os.listdir(ENTRIES_DIR)):
        if not fn.endswith(".yaml"):
            continue
        with open(os.path.join(ENTRIES_DIR, fn)) as f:
            entries.append(yaml.safe_load(f))
    entries.sort(key=lambda e: e["term"].lower())
    return entries


def content_hash(entry):
    canonical = json.dumps(
        {"claims": entry.get("claims", []),
         "definition": entry.get("definition", "").strip(),
         "detect": entry.get("detect"),
         "counter": entry.get("counter")},
        sort_keys=True, ensure_ascii=False)
    return hashlib.sha256(canonical.encode("utf-8")).hexdigest()[:16]


def _fmt_quote(q):
    q = q.strip()
    return q[:280] + ("…" if len(q) > 280 else "")


def render_index_md(entries):
    lines = ["# Slop-Lexikon", "",
             "> Single Source of Truth: `lexikon/entries/*.yaml` — diese Datei",
             "> ist ein Build-Artifakt (`scripts/build_lexikon.py`). Nicht von",
             "> Hand editieren.", ""]
    for e in entries:
        lines.append(f"## {e['term']}")
        meta = (f"`{e['id']}` · Kategorie: {e['category']} · "
                f"Status: {e['status']} · v{e['version']} · "
                f"content_hash: `{content_hash(e)}`")
        lines += ["", meta, "", e["definition"].strip(), ""]
        if e.get("aliases"):
            lines.append(f"*Aliase:* {', '.join(e['aliases'])}")
            lines.append("")
        lines.append("**Belegte Aussagen:**")
        for i, claim in enumerate(e.get("claims", []), 1):
            lines.append(f"{i}. {claim['statement'].strip()}")
            for src in claim.get("sources", []):
                lines.append(f"   > \u201e{_fmt_quote(src['quote'])}\u201c")
                lines.append(f"   > — <{src['url']}> (Zugriff {src['accessed']})")
        lines.append("")
        if e.get("detect"):
            hints = ", ".join(e["detect"].get("hints", []))
            lines.append(f"*Detect:* {hints or 'regex-basiert'}")
            lines.append("")
        if e.get("counter"):
            lines.append(f"*Gegenmaßnahme:* {e['counter'].get('measure', '')}")
            if e["counter"].get("keep_when"):
                lines.append(f"*Keep when:* {e['counter']['keep_when']}")
            lines.append("")
        if e.get("see_also"):
            lines.append(f"*Siehe auch:* {', '.join(e['see_also'])}")
            lines.append("")
    return "\n".join(lines) + "\n"


def render_lexikon_json(entries):
    return json.dumps({
        "name": "slop-lexikon",
        "schema": "lexikon/schema/entry.schema.json",
        "entry_count": len(entries),
        "entries": [
            {
                "id": e["id"],
                "term": e["term"],
                "aliases": e.get("aliases", []),
                "definition": e["definition"].strip(),
                "category": e["category"],
                "claims": e["claims"],
                "detect": e.get("detect"),
                "counter": e.get("counter"),
                "status": e["status"],
                "version": e["version"],
                "see_also": e.get("see_also", []),
                "content_hash": content_hash(e),
            }
            for e in entries
        ],
    }, indent=2, sort_keys=True, ensure_ascii=False) + "\n"


def render_llms_txt(entries):
    lines = ["# Slop-Lexikon", "",
             "> Belegtes Glossar von AI-Slop-Signalen, -Mustern und "
             "Gegenprinzipien. Jede Aussage trägt Quelle (URL + Zitat + "
             "Zugriffsdatum). Quelle: lexikon/entries/ (SSOT).", ""]
    for e in entries:
        lines.append(f"- [{e['term']}]"
                     f"(entries/{e['id']}.yaml): "
                     f"{e['definition'].strip().splitlines()[0]}")
    lines += ["", "Optional: llms-full.txt enthält alle Einträge mit allen "
              "Belegzitaten."]
    return "\n".join(lines) + "\n"


def render_llms_full_txt(entries):
    lines = ["# Slop-Lexikon — Volltext", ""]
    for e in entries:
        lines += ["## " + e["term"], "",
                  e["definition"].strip(), ""]
        for claim in e.get("claims", []):
            lines.append(f"- {claim['statement'].strip()}")
            for src in claim.get("sources", []):
                lines.append(f"  - Quelle: {src['url']} (Zugriff {src['accessed']})")
                lines.append(f"    Zitat: {src['quote'].strip()}")
        lines.append("")
    return "\n".join(lines) + "\n"


def build(out_dir):
    entries = load_entries()
    with open(SCHEMA_PATH) as f:
        schema = json.load(f)
    errors = []
    for e in entries:
        errors += validate_entry(e, schema)
    if errors:
        for err in errors:
            print(f"FAIL — schema: {err}", file=sys.stderr)
        return 1
    artifacts = {
        "index.md": render_index_md(entries),
        "lexikon.json": render_lexikon_json(entries),
        "llms.txt": render_llms_txt(entries),
        "llms-full.txt": render_llms_full_txt(entries),
    }
    os.makedirs(out_dir, exist_ok=True)
    for fn, content in sorted(artifacts.items()):
        with open(os.path.join(out_dir, fn), "w") as f:
            f.write(content)
    print(f"OK — {len(entries)} entries -> {out_dir} "
          f"({', '.join(sorted(artifacts))})")
    return 0


def check(dist_dir):
    """Sync-Gate: rebuild in tmp, compare against dist_dir."""
    with tempfile.TemporaryDirectory() as tmp:
        rc = build(tmp)
        if rc:
            return rc
        for fn in sorted(os.listdir(tmp)):
            rebuilt = open(os.path.join(tmp, fn)).read()
            path = os.path.join(dist_dir, fn)
            if not os.path.exists(path):
                print(f"SYNC-GATE FAIL — dist/{fn} fehlt (Neubau nötig)")
                return 1
            if open(path).read() != rebuilt:
                print(f"SYNC-GATE FAIL — dist/{fn} weicht vom Neubau ab "
                      f"(dist ist Build-Artefakt: scripts/build_lexikon.py "
                      f"ausführen und committen)")
                return 1
        print("OK — Sync-Gate: dist/ ist aktuell (== Neubau)")
        return 0


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", default=os.path.join(LEXIKON, "dist"))
    ap.add_argument("--check", action="store_true")
    args = ap.parse_args()
    if args.check:
        return check(args.out)
    return build(args.out)


if __name__ == "__main__":
    sys.exit(main())
