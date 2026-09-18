# Ontology Playground Adapter

Publication adapter for the [Ontology Playground](https://github.com/microsoft/Ontology-Playground).
The catalogue under `catalogue/community/hikaman/` is a **generated view** of the
repository SSOT (`ontology.json`, `ontology.ttl`, extension `human-work-seo-slop`) —
see `adr/0002` (no second source of truth) and issue #87.

## Why

The pre-adapter catalogue (PR #6) hand-published classes that did not exist in the
ontology (`WorkSlop`, `HumanAuthoredWorkSlop`, four invented intent types, mangled
identifiers like `sEOSlopId`). The generated view cannot drift: every published class
is looked up in the SSOT at generation *and* validation time.

## Regenerate

```sh
python integrations/ontology-playground/generate_catalogue.py
```

View selection lives in `views.json` (slug, metadata, class list, relationships).
Only class names that exist in the SSOT (or documented scaffolding/shared structural
classes) are accepted; anything else fails the run.

## Validation (CI gate)

```sh
python integrations/ontology-playground/validate_adapter.py
python integrations/ontology-playground/generate_catalogue.py --check
```

`validate_adapter.py` re-checks every published class against the SSOT, counts,
identifier coverage and local domains/ranges. `--check` fails when the committed
catalogue drifted from the SSOT. Both run in CI (`.github/workflows/tests.yml`).

## Layout

```
views.json            view definitions (the only hand-edited file here)
generate_catalogue.py SSOT → catalogue generator (+ --check drift gate)
validate_adapter.py   structural + semantic validation gate
manifest.json         generated: view/entity/relationship counts
catalogue/community/hikaman/<slug>/{ontology.rdf, metadata.json}
```
