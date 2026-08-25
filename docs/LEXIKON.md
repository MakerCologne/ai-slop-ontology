# Lexikon (Schema-first SSOT)

Belegtes Glossar der AI-Slop-Ontology: ein Begriff → eine YAML-Quelle →
zwei generierte Sichten (menschlich + agentenlesbar).

## SSOT-Regel

- **Nur `lexikon/entries/*.yaml` wird von Hand editiert.**
- **`lexikon/dist/` ist ein Build-Artefakt — niemals direkt editieren.**
  Der Sync-Gate-Test (`tests/test_lexikon.py::test_dist_is_in_sync_with_entries`)
  baut das Lexikon neu und lässt `dist/`-Abweichungen rot werden.

## Schema

`lexikon/schema/entry.schema.json` (draft-07-Subset; validiert von
`scripts/build_lexikon.py` — das `jsonschema`-Paket ist keine
Repo-Abhängigkeit). Pflicht je Eintrag: `id`, `term`, `definition`,
`category` (signal/pattern/type/counter), `claims[]` mit je ≥1 `source`
(`url`, `quote`, `accessed`), `status` (nursery/beta/stable, Lebenszyklus
wie METHODOLOGY.md), `version`.

**Kein Eintrag ohne Quellen-Zitat** — jede faktische Aussage trägt ihren
Beleg (Wikidata-Statement-Stil).

## Build & Sync-Gate

```bash
python3 scripts/build_lexikon.py           # baut nach lexikon/dist/
python3 scripts/build_lexikon.py --check   # Sync-Gate: dist == Neubau?
```

Output: `dist/index.md` (Human-Sicht, alphabetisch, narrativ mit Belegen),
`dist/lexikon.json` + `dist/llms.txt` + `dist/llms-full.txt` (Agent-Sicht,
llmstxt.org-Stil). Deterministisch: keine Timestamps, sortierte Iteration,
kanonisches JSON; `content_hash` je Eintrag in beiden Sichten.

Nach jeder Änderung an `entries/`: neu bauen und `dist/` mitcommitten.
