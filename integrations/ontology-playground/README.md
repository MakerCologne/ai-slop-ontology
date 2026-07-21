# Ontology Playground Adapter

Import-ready RDF/XML views of the AI Slop Ontology for
[microsoft/Ontology-Playground](https://github.com/microsoft/Ontology-Playground).

The canonical JSON, YAML and Turtle ontologies remain the source of truth. These
files are deliberately reduced, graph-oriented projections because the Playground
works best with 5–8 connected entity types per catalogue entry.

## Catalogue entries

| Slug | Purpose | Entities |
|---|---|---:|
| `ai-slop-core` | Shared concepts, evidence, harms and mitigation | 8 |
| `ai-slop-media` | Text, image, video, audio, music, code and multimodal AI Slop | 8 |
| `ai-slop-domains` | Academic, legal, work, review, security, education and political AI Slop | 8 |
| `ai-slop-intent` | Engagement, monetization, propaganda, poisoning, search, impersonation and filler | 8 |
| `work-slop` | Technology-neutral Work Slop overview | 8 |
| `management-slop` | Strategy, jargon, meetings, decisions, metrics, administration and compliance | 8 |
| `seo-slop` | Technology-neutral SEO Slop types | 8 |

## Use in the Playground

Each folder contains:

- `ontology.rdf` — RDF/XML accepted by the Playground importer
- `metadata.json` — catalogue metadata accepted by the community catalogue

To contribute them upstream, copy the seven folders into:

```text
catalogue/community/hikaman/
```

Then run:

```bash
npm run catalogue:build
npm run validate
npm test
npm run build
```

The adapter uses explicit `owl:ObjectProperty` relationships such as
`isSubtypeOf`, `supports`, `causes` and `mitigates`, because the current
Playground graph parser does not render `rdfs:subClassOf` as visible graph edges.

## Modeling note

A node represents the type of an observed slop case, not a person. Human
authorship, AI use, jargon, inconvenience, or an unpopular decision is never
sufficient by itself to classify something as slop.
