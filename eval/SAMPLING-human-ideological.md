# Sampling-Plan — Eval-Korpus Human/Ideological Slop (#98)

**Status:** spec (Korpus im Aufbau) · **adr:** 0003, 0005 · **Verwandt:** #47, #92, #95–#97

## Korpus-Schnitt (Minimum 40 positiv / 40 negativ)

| Segment | Ziel | Seed-Stand |
|---|---|---|
| Ritual-Brandmauer (`RitualFirewall`) | 8 | 4 |
| Kollektivframe (`CollectiveOther`/`ReplacementKicker`) | 8 | 4 |
| Purity-Kette (`PurityBan`/`VibeScapegoat`) | 8 | 4 |
| Salvation-Kette (`SalvationModel`/`MartyrCartel`) | 8 | 6 |
| Ethnopluralismus-Rebrand (`EthnopluralistRebrand`) | 8 | 1 |
| Negativ: substanzielle AfD-Kritik, Migrationspolicy, BfV-Zitat, Gericht/Parlament, technische AI-Kritik, ethnografische Differenz | 40 | 16 |

Seed: `eval/human_ideological.jsonl` (40 Einträge, alle `source: own:handwritten`, Felder `id`, `signal`, `label`, `lang`, `text`). **Keine echten Massen-Texte** werden committed (Urheberrecht/Toxizität, adr/0005) — öffentliche Quellen werden als URL-Metadaten verlinkt, Volltexte bleiben außerhalb des Repos.

## Metrik

- `rhetoric` detect-only: **Precision ≥ 0.95 auf Hard-Negatives**, Recall nachrangig.
- `polemic_risk` existiert **nicht** vor diesem Korpus (adr/0008).
- Kein Mixing mit `eval/corpus.jsonl` (AI-Slop) — eigene Datei, eigener Runner-Pfad.

## Runner-Integration (ausstehend bis Korpus-Zielstand)

- `run_benchmark.py --corpus eval/human_ideological.jsonl --detect-only rhetoric` (Flag statt neuer Metrik; CI-Pin Precision-Negatives im GitLab-Workflow — **kein** GitHub Actions).
- Validierungs-Receipts: Runner-Output mit P/R je Pattern + Konfusionsmatrix im PR, der den Zielstand erreicht.

## Leak-Check

- Keine Trainingsphrase als einziges Positiv-Merkmal: für jede positiv gelabelte Text-ID wird geprüft, dass mindestens ein Merkmal außerhalb der Pattern-Phrase (Struktur, Schlussform, Kontext) trägt; dokumentiert im Runner-Report (`leak_check: pass/fail je id`).
- `source: own:handwritten` hält Formulierungen frei von Drittkatalog-Kopien (Lizenzregel #76).
