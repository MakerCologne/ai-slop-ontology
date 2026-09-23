# DE-Ideology-Coverage — detect-only Rhetorik-Layer für ideologische Ritualmuster (#92)

**Status:** promoted → detect-only Integration (adr/0008 B-Default; adr/0006 detect-only) · **Ursprung:** 2026-09-02 (nursery, PR #127) · **Promotion:** 2026-09-22 · **Epic:** #89 · **Korpus:** #98 (46 pos / 40 hard-neg, FP=0) · **Implementation:** `src/de_ideology.py` + `tests/test_de_ideology.py` + SSOT-Spiegel `signals.deIdeology`

## Ziel

`slop rhetoric` / `slop check` sollen ideologische Ritualprosa **benennen**, nicht scoren. Vertrag wie bestehende `RHETORICAL_PATTERNS`: named evidence mit zitiertem Beleg, `keep_when`-Pflicht, konservativ. Kein Eintrag in noisy-OR-Gewichten.

## Patterns (10, Nursery)

Pattern-Metadaten inkl. `match_shape`, `example_slop` (`own:handwritten`) und `keep_when` je Pattern liegen in `skills/ai-slop-detection/references/de_ideology_patterns.json` (Spiegel in ontology.json als Detect-only-Metadaten nach Promotion).

| id | Phänomen | keep_when |
|---|---|---|
| `RitualFirewall` | Brandmauer als Selbstzweck | Konkretes Verfahren (Ausschuss, Minderheitsregierung, Verbot) |
| `MartyrCartel` | Opfer-/Kartell-Frame als Totalerklärung | Einzelner Vorgang mit Beleg |
| `CollectiveOther` | Herkunft als Kollektivschuld | Statistik mit Nenner, Zeitraum, Quelle |
| `ReplacementKicker` | Umvolkung / Austausch als Schluss | Demografie ohne Absichtsunterstellung |
| `EthnopluralistRebrand` | Diversität = Trennung | Ethnografie, nicht Politikforderung |
| `PurityBan` | Totalverbot statt Differenz | Konkreter Rechts-/Datenfall |
| `VibeScapegoat` | Jeder Fehler = Vibe Coding | Diff/Postmortem mit Werkzeugbeleg |
| `SalvationModel` | Modell/Partei als Erlöser | Einzelclaim mit Testbedingung |
| `UnfalsifiableTemplate` | Jedes Event bestätigt den Frame | Event-spezifische neue Information |
| `EnemyVermin` | Entmenschlichung | Klar markierte Satire, nicht gegen Gruppen |

## Technische Anbindung

- EN-Kern: `skills/ai-slop-detection/scripts/rhetorical_patterns.py` (bestehender detect-only-Vertrag).
- DE-Layer: neue Kategorie `de_ideology` im Phrase-DB-Stil (#77), Sprachgate DE/EN.
- `ontology.json`-Spiegel der Pattern-Metadaten erst mit der Promotion (beta), nicht schon in der Nursery.

## Lizenzregel

DE-Phrasen werden **nicht** 1:1 aus Drittkatalogen kopiert (Lizenzregel #76): eigene Kurzformen + `own:`-Belege.

## Tests / Promotion

- **Promotion erfolgt (2026-09-22):** Signal-DoD 3/3/2 je Pattern erfüllt (`tests/test_de_ideology.py`, 10 Patterns × 8 Fixtures + Vertragstests).
- Hard-Negative-Satz: FP=0 auf den 40 #98-Hard-Negatives UND FP=0 auf `eval/control_set.jsonl` (n=30). Korpus-Recall konservativ (12/46 — Trigger sind Literalphrasen, die Korpus-Positive sind subtiler Frame-Prosa; Recall-Pflicht bestand nicht, Precision-Gate ≥ 0,95 exkl. FP=0 erfüllt).
- `polemic_risk` bleibt detect-only — existiert als Berichtsteil von `DeIdeologyClassifier`, geht NICHT in `slop_score` ein.
