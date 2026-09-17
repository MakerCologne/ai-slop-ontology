# Sampling-Plan — Eval-Korpus Human/Ideological Slop (#98)

**Status:** zielstand (#98): 46 positiv / 40 negativ, Runner `eval/run_human_ideological.py` als Gate 5b in CI · **adr:** 0003, 0005 · **Verwandt:** #47, #92, #95–#97

## Korpus-Schnitt (Minimum 40 positiv / 40 negativ)

| Segment | Ziel | Stand |
|---|---|---|
| Ritual-Brandmauer (`RitualFirewall`) | 8 | 8 |
| Kollektivframe (`CollectiveOther`/`ReplacementKicker`) | 8 | 8 |
| Purity-Kette (`PurityBan`/`VibeScapegoat`) | 8 | 8 |
| Salvation-Kette (`SalvationModel`/`MartyrCartel`) | 8 | 8 |
| Ethnopluralismus-Rebrand (`EthnopluralistRebrand`) | 8 | 8 |
| Bonus außerhalb der Kern-Segmente (`EnemyVermin`/`PolemicSlop`/`UnfalsifiableTemplate`) | — | 6 |
| Negativ: substanzielle AfD-Kritik, Migrationspolicy, BfV-Zitat, Gericht/Parlament, technische AI-Kritik, ethnografische Differenz | 40 | 40 |

Korpus: `eval/human_ideological.jsonl` (86 Einträge, alle `source: own:handwritten`, Felder `id`, `signal`, `label`, `lang`, `text`, `features`). **Keine echten Massen-Texte** werden committed (Urheberrecht/Toxizität, adr/0005) — öffentliche Quellen werden als URL-Metadaten verlinkt, Volltexte bleiben außerhalb des Repos.

## Metrik

- `rhetoric` detect-only: **Precision ≥ 0.95 auf Hard-Negatives**, Recall nachrangig.
- `polemic_risk` existiert **nicht** vor diesem Korpus (adr/0008).
- Kein Mixing mit `eval/corpus.jsonl` (AI-Slop) — eigene Datei, eigener Runner-Pfad.

## Runner-Integration (zielstand seit #98-Zielstands-PR)

- `eval/run_human_ideological.py` (Gate 5b in `scripts/verify.sh` bzw. `.gitlab-ci.yml`): Integrität (40/40, 5 Segmente je ≥8, eindeutige IDs, `own:handwritten`), Leak-Check (je Positiv ≥1 `structure:`-Merkmal), Precision-Pin ≥ 0.95 der Rhetorik-Gruppe (ideologienahe `de_*`-Kategorien aus `ontology.json`) auf Hard-Negatives. Recall bleibt nachrangig bis #92 (Option B) dedizierte Ritual-/Purity-Signale liefert.
- Validierungs-Receipts: Runner-Output (`--json`) im PR des Zielstands.

## Leak-Check

- Keine Trainingsphrase als einziges Positiv-Merkmal: für jede positiv gelabelte Text-ID wird geprüft, dass mindestens ein Merkmal außerhalb der Pattern-Phrase (Struktur, Schlussform, Kontext) trägt; dokumentiert im Runner-Report (`leak_check: pass/fail je id`).
- `source: own:handwritten` hält Formulierungen frei von Drittkatalog-Kopien (Lizenzregel #76).
