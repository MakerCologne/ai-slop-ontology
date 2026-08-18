# English Documentation

**Languages:** English · [Deutsch](../de/README.md)

## What is in which language

Identifiers are English everywhere and are never translated: class names,
properties, signal ids, file names and the contents of `ai_slop_ontology.yaml`,
`ontology.json`, `ontology.ttl` and the extension files.

The project's explanatory documents are written in German. That is the current
state of the repository, stated plainly here because this page used to claim
the opposite — it listed the repository-level documents as "canonical English
entry points" while `ONTOLOGY.md`, `ONTOLOGY-STRUCTURE.md`, `REFERENCES.md`,
`CHANGELOG.md` and the review documents are all German (review 2026-08 §3.2).

| Document | Language |
|----------|----------|
| [`../../README.md`](../../README.md) — project overview | English |
| [`../USER-GUIDE.md`](../USER-GUIDE.md) — full `slop` CLI manual | English |
| [`../../skills/ai-slop-detection/SKILL.md`](../../skills/ai-slop-detection/SKILL.md) — agent skill | English |
| [`../../extensions/human-work-seo-slop/`](../../extensions/human-work-seo-slop/) — extension README and research | English |
| [`../../integrations/ontology-playground/README.md`](../../integrations/ontology-playground/README.md) — Playground adapter | English |
| [`../../AI-SLOP-ONTOLOGY.md`](../../AI-SLOP-ONTOLOGY.md) — canonical model | German |
| [`../../ONTOLOGY.md`](../../ONTOLOGY.md), [`../../ONTOLOGY-STRUCTURE.md`](../../ONTOLOGY-STRUCTURE.md) | German |
| [`../../REFERENCES.md`](../../REFERENCES.md), [`../../CHANGELOG.md`](../../CHANGELOG.md) | German |
| [`../../REVIEW-2026-07.md`](../../REVIEW-2026-07.md), [`../../REVIEW-2026-08.md`](../../REVIEW-2026-08.md) | German |
| [`../../report.md`](../../report.md), [`../../report-extended.md`](../../report-extended.md), [`../../RESEARCH-v0.1.md`](../../RESEARCH-v0.1.md) | German |

Machine-readable artifacts win over any prose explanation, in either language.

## Translating a document

Replace it, do not copy it. A German document that gets an English version
becomes one English document plus, if still wanted, one German document that
links to it — never two files with the same content drifting apart.
`tests/test_documentation_layout.py` fails when a file under `docs/de/` or
`docs/en/` duplicates a document at the repository root.
