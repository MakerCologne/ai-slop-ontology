#!/usr/bin/env python3
"""Validate the Ontology Playground adapter using only the Python standard library."""
from pathlib import Path
import json
import sys
import xml.etree.ElementTree as ET

ROOT = Path(__file__).resolve().parent
CATALOGUE = ROOT / "catalogue" / "community" / "hikaman"
RDF = "{http://www.w3.org/1999/02/22-rdf-syntax-ns#}"
OWL = "{http://www.w3.org/2002/07/owl#}"
RDFS = "{http://www.w3.org/2000/01/rdf-schema#}"

ALLOWED_CATEGORIES = {
    "retail", "healthcare", "finance", "manufacturing", "education", "food",
    "media", "events", "technology", "general", "school", "fibo",
}
errors = []

for folder in sorted(p for p in CATALOGUE.iterdir() if p.is_dir()):
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
    if not 3 <= len(classes) <= 8:
        errors.append(f"{folder.name}: expected 3–8 classes, got {len(classes)}")

    class_uris = {c.attrib.get(f"{RDF}about") for c in classes}
    identifiers = {uri: 0 for uri in class_uris}
    for prop in root.findall(f"{OWL}DatatypeProperty"):
        domain = prop.find(f"{RDFS}domain")
        if domain is None:
            continue
        uri = domain.attrib.get(f"{RDF}resource")
        if uri not in identifiers:
            continue
        is_identifier = any(
            child.tag.endswith("isIdentifier") and (child.text or "").strip().lower() == "true"
            for child in prop
        )
        if is_identifier:
            identifiers[uri] += 1

    for uri, count in identifiers.items():
        if count != 1:
            errors.append(f"{folder.name}: {uri} has {count} identifier properties")

    for rel in root.findall(f"{OWL}ObjectProperty"):
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

folders = list(p for p in CATALOGUE.iterdir() if p.is_dir())
print(f"Adapter validation passed ({len(folders)} catalogue entries).")
