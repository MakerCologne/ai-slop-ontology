#!/usr/bin/env python3
"""Validate the Ontology Playground adapter using only the Python standard library.

Two layers:
  structural  XML wellformedness, metadata fields, entity/relationship counts
              against the manifest, one identifier per class, local domains
              and ranges.
  semantic    every class published in a view must exist in the ontology this
              catalogue claims to represent. Without it the views drifted: the
              work-slop view shipped `WorkSlop` and `HumanAuthoredWorkSlop`,
              neither of which was a name in the repo (review 2026-08 §2.1).
"""
from pathlib import Path
import json
import re
import sys
import xml.etree.ElementTree as ET

ROOT = Path(__file__).resolve().parent
REPO = ROOT.parent.parent
CATALOGUE = ROOT / "catalogue" / "community" / "hikaman"
RDF = "{http://www.w3.org/1999/02/22-rdf-syntax-ns#}"
OWL = "{http://www.w3.org/2002/07/owl#}"
RDFS = "{http://www.w3.org/2000/01/rdf-schema#}"
ALLOWED_CATEGORIES = {
    "retail", "healthcare", "finance", "manufacturing", "education", "food",
    "media", "events", "technology", "general", "school", "fibo",
}
# Playground views also carry a few structural classes that the catalogue
# needs but the ontology does not model as slop types.
SCAFFOLDING = {"SlopPhenomenon", "DetectionEvidence", "MitigationAction", "Harm"}


def known_ontology_names() -> set:
    """Every class/type name defined anywhere in the ontology or its extension."""
    names = set()
    ttl_files = [REPO / "ontology.ttl",
                 REPO / "extensions" / "human-work-seo-slop" / "human_work_seo_slop.ttl"]
    for path in ttl_files:
        if path.exists():
            names |= set(re.findall(r"^:([A-Za-z0-9_]+)\s", path.read_text(encoding="utf-8"),
                                    re.MULTILINE))
    oj = REPO / "ontology.json"
    if oj.exists():
        data = json.loads(oj.read_text(encoding="utf-8"))
        for group in data.get("slopTypes", {}).values():
            names |= set(group)
    ext = REPO / "extensions" / "human-work-seo-slop" / "human_work_seo_slop.json"
    if ext.exists():
        data = json.loads(ext.read_text(encoding="utf-8"))
        names |= {t["id"] for t in data.get("types", [])}
        names |= {p for t in data.get("types", []) for p in t.get("parents", [])}
    return names


errors = []
ONTOLOGY_NAMES = known_ontology_names()
if not ONTOLOGY_NAMES:
    errors.append("could not read the ontology — semantic check would pass vacuously")
manifest = json.loads((ROOT / "manifest.json").read_text(encoding="utf-8"))
expected = {view["slug"]: view for view in manifest["views"]}
folders = sorted(p for p in CATALOGUE.iterdir() if p.is_dir())

if {p.name for p in folders} != set(expected):
    errors.append("catalogue folders do not match manifest views")

for folder in folders:
    rdf_path = folder / "ontology.rdf"
    metadata_path = folder / "metadata.json"
    if not rdf_path.exists() or not metadata_path.exists():
        errors.append(f"{folder.name}: ontology.rdf and metadata.json are required")
        continue

    metadata = json.loads(metadata_path.read_text(encoding="utf-8"))
    if set(metadata) - {"name", "description", "category", "icon", "tags", "author"}:
        errors.append(f"{folder.name}: unsupported metadata fields")
    for required in ("name", "description", "category"):
        if not metadata.get(required):
            errors.append(f"{folder.name}: missing metadata {required}")
    if metadata.get("category") not in ALLOWED_CATEGORIES:
        errors.append(f"{folder.name}: unsupported category {metadata.get('category')}")

    root = ET.parse(rdf_path).getroot()
    classes = root.findall(f"{OWL}Class")
    relationships = root.findall(f"{OWL}ObjectProperty")
    if not 3 <= len(classes) <= 8:
        errors.append(f"{folder.name}: expected 3–8 classes, got {len(classes)}")
    view = expected.get(folder.name, {})
    if len(classes) != view.get("entities"):
        errors.append(f"{folder.name}: class count differs from manifest")
    if len(relationships) != view.get("relationships"):
        errors.append(f"{folder.name}: relationship count differs from manifest")

    for c in classes:
        name = (c.attrib.get(f"{RDF}about") or "").split("#")[-1]
        if name and name not in ONTOLOGY_NAMES and name not in SCAFFOLDING:
            errors.append(
                f"{folder.name}: class '{name}' does not exist in the ontology "
                f"(ontology.ttl / ontology.json / human-work-seo-slop)")

    class_uris = {c.attrib.get(f"{RDF}about") for c in classes}
    identifiers = {uri: 0 for uri in class_uris}
    for prop in root.findall(f"{OWL}DatatypeProperty"):
        domain = prop.find(f"{RDFS}domain")
        if domain is None:
            continue
        uri = domain.attrib.get(f"{RDF}resource")
        if uri not in identifiers:
            continue
        if any(child.tag.endswith("isIdentifier") and (child.text or "").strip().lower() == "true" for child in prop):
            identifiers[uri] += 1

    for uri, count in identifiers.items():
        if count != 1:
            errors.append(f"{folder.name}: {uri} has {count} identifier properties")

    for rel in relationships:
        domain = rel.find(f"{RDFS}domain")
        range_el = rel.find(f"{RDFS}range")
        if domain is None or range_el is None:
            errors.append(f"{folder.name}: relationship missing domain or range")
            continue
        if domain.attrib.get(f"{RDF}resource") not in class_uris:
            errors.append(f"{folder.name}: relationship domain is not a local class")
        if range_el.attrib.get(f"{RDF}resource") not in class_uris:
            errors.append(f"{folder.name}: relationship range is not a local class")

if errors:
    print("Adapter validation failed:")
    for error in errors:
        print(f"  - {error}")
    sys.exit(1)
n_classes = sum(len(ET.parse(f / "ontology.rdf").getroot().findall(f"{OWL}Class"))
                for f in folders)
print(f"Adapter validation passed ({len(folders)} catalogue entries, "
      f"{n_classes} classes checked against the ontology).")
