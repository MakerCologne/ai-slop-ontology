# Pull Request

> Pflichtfelder sind mit **(Pflicht)** markiert. DoD-Referenz: docs/SIGNAL-DOD.md (#64). Score-/Gewichtsänderungen: zusätzlich docs/SCORE-GOVERNANCE.md (#67).

- **Issue:** fixes #N
- **depends-on:** #N / keine
- **Art:** Signal | Scorer-Change | Eval | Doku | Prozess

## Corpus Evidence (Pflicht)
Trefferquoten gegen eval/corpus.jsonl / eval/control_set.jsonl. Bei Score-Änderung: Messung **vorher / nachher** am Control Set UND Benchmark (Change-Protokoll-Pflicht, #67).

## Test-Oracle (Pflicht)
Welche Tests decken den Change ab? Red-Commit-Hash (TDD).

## FP-Analyse (Pflicht)
Hard-Negative-Ergebnis (FP-Rate je Genre), keep_when-Abwägung — oder „nicht zutreffend, weil …".

## Prior Art
Verwandte Signale/PRs/Literatur (arXiv wo applicable).

## Signals-DoD-Abhaken (Pflicht bei Signalen)
- [ ] 1. Test-Oracle (Fixtures + Schwelle)
- [ ] 2. FP-Abwägung dokumentiert
- [ ] 3. SSOT-Eintrag ontology.json (inkl. `status`)
- [ ] 4. Quellenbeleg (Primärquelle)
- [ ] 5. Benchmark-Referenz (FP/FN auf #41-Korpus)
- [ ] 6. Kollisions-Check (#46)
- [ ] 7. Sequencing-Disziplin (depends-on)
- [ ] 8. Prozess-Einbettung (falls Fix-/Prozess-Feature)

## Governance (Pflicht bei Score-/Gewichtsänderung)
Optimierungs-Freigabe? Guardrail-Non-Regression (Voice-Budget #56)? Re-Baseline betroffen? — s. docs/SCORE-GOVERNANCE.md.

## Changelog
CHANGELOG.md aktualisiert? Versions-Bump konsolidiert am Batch-Ende?
