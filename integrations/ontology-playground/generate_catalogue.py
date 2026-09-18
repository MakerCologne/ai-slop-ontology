#!/usr/bin/env python3
"""Generate the Ontology Playground catalogue from the repository SSOT.

The catalogue is a *generated view* (adr/0002: no second source of truth).
Every class published in a view must exist in ontology.json, ontology.ttl or
the human-work-seo-slop extension; the generator refuses to emit invented
classes. validate_adapter.py re-checks the generated artefacts and serves as
the CI gate (issue #87 DoD 2+3).

Usage:
    python integrations/ontology-playground/generate_catalogue.py [--check]
"""
from __future__ import annotations

import json
import re
import sys
import datetime
from pathlib import Path

ROOT = Path(__file__).resolve().parent
REPO = ROOT.parent.parent
CATALOGUE = ROOT / "catalogue" / "community" / "hikaman"
BASE = "https://github.com/hikaman/ai-slop-ontology"


def known_ontology_names() -> set[str]:
    names: set[str] = set()
    ttl_files = [
        REPO / "ontology.ttl",
        REPO / "extensions" / "human-work-seo-slop" / "human_work_seo_slop.ttl",
    ]
    for path in ttl_files:
        if path.exists():
            names |= set(re.findall(r"^:([A-Za-z0-9_]+)\s", path.read_text(encoding="utf-8"), re.MULTILINE))
    oj = REPO / "ontology.json"
    if oj.exists():
        data = json.loads(oj.read_text(encoding="utf-8"))
        for group in data.get("slopTypes", {}).values():
            if isinstance(group, dict):
                names |= set(group.keys())
            elif isinstance(group, list):
                names |= set(group)
    ext = REPO / "extensions" / "human-work-seo-slop" / "human_work_seo_slop.json"
    if ext.exists():
        data = json.loads(ext.read_text(encoding="utf-8"))
        names |= {t["id"] for t in data.get("types", [])}
        names |= {p for t in data.get("types", []) for p in t.get("parents", [])}
    return names


def esc(s: str) -> str:
    return (s.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;").replace('"', "&quot;"))


def class_label(name: str) -> str:
    # Prefer ontology.json labels where available; fall back to CamelCase split.
    return re.sub(r"(?<!^)(?=[A-Z])", " ", name)


def render_view(view: dict, base_ns: str) -> tuple[str, dict]:
    lines: list[str] = []
    lines.append('<?xml version="1.0" encoding="UTF-8"?>')
    lines.append('<rdf:RDF xmlns:rdf="http://www.w3.org/1999/02/22-rdf-syntax-ns#"')
    lines.append('         xmlns:rdfs="http://www.w3.org/2000/01/rdf-schema#"')
    lines.append('         xmlns:owl="http://www.w3.org/2002/07/owl#"')
    lines.append(f'         xmlns="{base_ns}#"')
    lines.append('         xml:base="%s">' % base_ns)
    for cls in view["classes"]:
        lines.append(f'  <owl:Class rdf:about="{base_ns}#{cls}">')
        lines.append(f'    <rdfs:label xml:lang="en">{esc(class_label(cls))}</rdfs:label>')
        lines.append("  </owl:Class>")
    for cls in view["classes"]:
        lines.append(f'  <owl:DatatypeProperty rdf:about="{base_ns}#hasIdentifier">')
        lines.append(f'    <rdfs:domain rdf:resource="{base_ns}#{cls}"/>')
        lines.append("    <rdfs:range rdf:resource=\"http://www.w3.org/2001/XMLSchema#string\"/>")
        lines.append("    <isIdentifier>true</isIdentifier>")
        lines.append("  </owl:DatatypeProperty>")
    for name, dom, rng in view["relationships"]:
        lines.append(f'  <owl:ObjectProperty rdf:about="{base_ns}#{name}">')
        lines.append(f'    <rdfs:domain rdf:resource="{base_ns}#{dom}"/>')
        lines.append(f'    <rdfs:range rdf:resource="{base_ns}#{rng}"/>')
        lines.append("  </owl:ObjectProperty>")
    lines.append("</rdf:RDF>")
    rdf = "\n".join(lines) + "\n"
    metadata = {
        "name": view["name"],
        "description": view["description"],
        "category": view["category"],
        "icon": view["icon"],
        "tags": view["tags"],
        "author": "hikaman",
    }
    return rdf, metadata


def main() -> int:
    config = json.loads((ROOT / "views.json").read_text(encoding="utf-8"))
    known = known_ontology_names()
    if not known:
        print("generate_catalogue: cannot read ontology — refusing to generate")
        return 1
    scaffold = set(config.get("scaffold_classes", []))
    shared = set(config.get("shared_classes", []))
    allowed = known | scaffold | shared

    errors = []
    manifest_views = []
    for view in config["views"]:
        slug = view["slug"]
        for cls in view["classes"]:
            if cls not in allowed:
                errors.append(f"{slug}: class '{cls}' does not exist in the ontology SSOT")
        for name, dom, rng in view["relationships"]:
            if dom not in view["classes"] or rng not in view["classes"]:
                errors.append(f"{slug}: relationship '{name}' references non-local class")
        n = len(view["classes"])
        if not 3 <= n <= 8:
            errors.append(f"{slug}: expected 3-8 classes, got {n}")
        manifest_views.append({
            "slug": slug,
            "name": view["name"],
            "entities": n,
            "relationships": len(view["relationships"]),
        })

    if errors:
        print("generate_catalogue failed:")
        for e in errors:
            print(f"  - {e}")
        return 1

    if "--check" in sys.argv:
        # Verify that the committed catalogue is up to date with the SSOT.
        manifest_path = ROOT / "manifest.json"
        expected_manifest = {
            "adapter_version": config["adapter_version"],
            "generated": None,  # compared separately
            "source_repository": BASE,
            "target_repository": "https://github.com/microsoft/Ontology-Playground",
            "catalogue_root": "catalogue/community/hikaman",
            "views": manifest_views,
        }
        if not manifest_path.exists():
            print("generate_catalogue --check: manifest.json missing — regenerate")
            return 1
        committed = json.loads(manifest_path.read_text(encoding="utf-8"))
        for k, v in expected_manifest.items():
            if v is not None and committed.get(k) != v:
                print(f"generate_catalogue --check: manifest '{k}' drifted — regenerate")
                return 1
        for view in config["views"]:
            folder = CATALOGUE / view["slug"]
            rdf, metadata = render_view(view, BASE)
            if not (folder / "ontology.rdf").exists() or (folder / "ontology.rdf").read_text(encoding="utf-8") != rdf:
                print(f"generate_catalogue --check: {view['slug']}/ontology.rdf drifted — regenerate")
                return 1
            if json.loads((folder / "metadata.json").read_text(encoding="utf-8")) != metadata:
                print(f"generate_catalogue --check: {view['slug']}/metadata.json drifted — regenerate")
                return 1
        print(f"generate_catalogue --check: catalogue is up to date ({len(config['views'])} views)")
        return 0

    for view in config["views"]:
        folder = CATALOGUE / view["slug"]
        folder.mkdir(parents=True, exist_ok=True)
        rdf, metadata = render_view(view, BASE)
        (folder / "ontology.rdf").write_text(rdf, encoding="utf-8")
        (folder / "metadata.json").write_text(json.dumps(metadata, indent=2) + "\n", encoding="utf-8")

    manifest = {
        "adapter_version": config["adapter_version"],
        "generated": datetime.date.today().isoformat(),
        "source_repository": BASE,
        "target_repository": "https://github.com/microsoft/Ontology-Playground",
        "catalogue_root": "catalogue/community/hikaman",
        "views": manifest_views,
    }
    (ROOT / "manifest.json").write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")
    print(f"generated {len(config['views'])} catalogue views into {CATALOGUE}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
