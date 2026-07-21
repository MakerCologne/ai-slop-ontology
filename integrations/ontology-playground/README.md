# Ontology Playground Adapter

Import-ready RDF/XML views of the AI Slop Ontology for
[microsoft/Ontology-Playground](https://github.com/microsoft/Ontology-Playground).

The canonical JSON, YAML and Turtle ontologies remain the source of truth. These
files are deliberately reduced, graph-oriented projections because the Playground
works best with small connected entity sets per catalogue entry.

## Catalogue entries

| Slug | Purpose | Entities |
|---|---|---:|
| `ai-slop-core` | Shared concepts, evidence, harms and mitigation | 8 |
| `ai-slop-media` | Text, image, video, audio, music, code and multimodal AI Slop | 8 |
| `ai-slop-domains` | Academic, legal, work, review, security, education and political AI Slop | 8 |
| `ai-slop-intent` | Engagement, monetization, propaganda, poisoning, search, impersonation and filler | 8 |
| `work-slop` | Compact overview of AI, human-authored and management Work Slop | 4 |
| `management-slop` | Strategy, jargon, meetings, decisions, metrics, administration and compliance | 8 |
| `seo-slop` | Technology-neutral SEO Slop types | 8 |

## Use in the Playground

Each folder contains:

- `ontology.rdf` — RDF/XML accepted by the Playground importer
- `metadata.json` — catalogue metadata accepted by the community catalogue

The files already use the target contribution layout under:

```text
integrations/ontology-playground/catalogue/community/hikaman/
```

For a Microsoft catalogue contribution, copy the seven folders into the root
`catalogue/community/hikaman/` directory of an Ontology Playground fork. Then run:

```bash
npm run catalogue:build
npm run validate
npm test
npm run build
```

The adapter uses explicit `owl:ObjectProperty` relationships such as
`isSubtypeOf`, `supports`, `causes` and `mitigates`, because the current
Playground graph parser does not render `rdfs:subClassOf` as visible graph edges.

## Validation

From the AI Slop Ontology repository root:

```bash
python3 integrations/ontology-playground/validate_adapter.py
python3 -m unittest tests.test_ontology_playground_adapter
```

The validator checks XML parsing, metadata fields, manifest parity, class counts,
exactly one identifier per entity, and local relationship endpoints.

## Modeling note

A node represents the type of an observed slop case, not a person. Human
authorship, AI use, jargon, inconvenience, or an unpopular decision is never
sufficient by itself to classify something as slop.
