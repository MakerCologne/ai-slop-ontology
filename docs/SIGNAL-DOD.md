# SIGNAL-DOD.md — Signal-Definition-of-Done (maschinenlesbare Checkliste, PR-Gate)

**Status:** konstitutiv (v2.0.0, Issue #64) · **Referenziert von:** PR-Template (#66), Methodik-Kodex (#63, M1/M2/M3), Governance (#67).

Jedes neue Signal (und jede Signal-Änderung) **muss** alle 8 Punkte der Checkliste erfüllen, bevor der PR gemerged wird. Die Punkte 1, 2, 3 und 6 sind teilautomatisiert prüfbar (`scripts/check_signal_dod.py`, Heuristiken); 4, 5, 7, 8 sind Review-Pflichtfelder (Template #66).

| # | Must | Prüfung | Ebene |
|---|------|---------|-------|
| 1 | **Test-Oracle:** exakte Matcherspezifikation + ≥1 Positiv-/Negativ-Fixture + Akzeptanzschwelle *vor* Implementierung | `check_signal_dod.py` (Test-Datei-Existenz, FAIL) + Review (Fixtures, Schwelle) | auto + Review |
| 2 | **FP-Abwägung:** keep_when/Genre-Register/Quote-Exemption-Denke dokumentiert — auch wenn Ergebnis „kein Guard nötig" | `check_signal_dod.py` (keep_when-Heuristik, WARN) + Review | auto + Review |
| 3 | **SSOT-Eintrag:** Signal-Leben in ontology.json (inkl. severity/Konfidenz, künftig model_notes + `status` nach #63-Lebenszyklus) — nicht nur im Code | `check_signal_dod.py` (SKILL.md-Referenz, WARN) + `check_consistency.py` (Parity) | auto + Review |
| 4 | **Quellenbeleg:** mind. 1 verifizierte Primärquelle mit Link (+ arXiv-Nummer wo applicable) | Review (Pflichtfeld im Template #66) | Review |
| 5 | **Benchmark-Referenz:** FP-/FN-Messung auf dem Hard-Negative-Korpus (#41) als PR-Gate | `eval/run_benchmark.py`-Zahlen im PR | auto (Benchmark) |
| 6 | **Kollisions-Check:** Abgleich gegen Signal-Kollisions-Matrix (#46) — zählt jedes Vorkommen nur einmal? | Review (Kollisions-Matrix) + `check_consistency.py` | Review |
| 7 | **Sequencing-Disziplin:** depends-on-Deklaration; keine Expansion auf kaputtem Fundament | Review (depends-on-Feld im Template #66) | Review |
| 8 | **Prozess-Einbettung:** bei Fix-/Prozess-Features: Zustand, Exit-Kriterium, Eskalationspfad, Auditierbarkeit (#51, #61) | Review | Review |

## Nutzung

- **Report-Modus (default):** `python3 scripts/check_signal_dod.py` — listet alle Signal-Module mit FAIL (fehlende Tests) und WARN (fehlende keep_when-Doku / SKILL.md-Referenz). Exit 0: Der Report macht Lücken sichtbar, blockiert nicht — Bestandssignale können schrittweise nachgezogen werden.
- **Strict-Modus:** `python3 scripts/check_signal_dod.py --strict` — exit 1 bei FAIL-Findungen. Empfohlen als CI-Gate für neue Signal-PRs.
- Infra-Module (slop_scorer, slop_classifier, fp_guards, tokenizer, input_norm, genre_profiles, learning_store, generated_docs, diff_mode) werden nur auf Test-Abdeckung geprüft, nicht auf Signal-Heuristiken. Unbekannte neue Module gelten automatisch als Signal-Kandidaten und werden voll geprüft.

## Quellen

- Musts destilliert aus allen Issue-Bodies #7–#62; Blaupausen: Clippy PR-Checkliste, PLOP-Writers'-Workshop, Methode E3 in `research/slop-ontology-gap-2026-08-24/methoden-fundament.md` §6 (externe Quelle).
- Lebenszyklus-Status (`nursery` beim Start, `beta` nach Punkt-5-Gate): `docs/METHODOLOGY.md` Abschnitt 2.
