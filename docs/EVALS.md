# EVALS.md — Drei-Level-Evals-Architektur

**Status:** konstitutiv (v2.0.0, Issue #68) · **Blaupause:** Hamel Husain, „Your AI Product Needs Evals" (2024) — L1/L2/L3-Pyramide; Methode E6 in `research/slop-ontology-gap-2026-08-24/methoden-fundament.md` §6 (externe Quelle).
**Verwandt:** docs/METHODOLOGY.md (M1, M5, M8), adr/0003 (Control-Set-Gate), adr/0005 (Benchmark-Disziplin), docs/SCORE-GOVERNANCE.md (#67).

---

## Architektur

| Ebene | Was | Wann | Kosten |
|---|---|---|---|
| **L1 — Unit-Assertions** | deterministische Tests je Signal/Matcher: exakte Fixtures (≥1 TP + Hard Negatives), Akzeptanzschwellen, Guards — reproduzierbar, CI-fähig (M8: Determinismus vor LLM) | bei jedem Commit | sehr billig |
| **L2 — Judge + Human (Control Set)** | Golden Control Set (handgeschriebene Kontrolltexte) als hartes FN/FP-Gate; LLM/Review als Judge nur als Veto/Befund, nie alleiniges Abbruchkriterium; Human-Review mit Error-Taxonomie | bei jedem Signal-PR / Score-Change | mittel |
| **L3 — Quartals-Re-Score** | Re-Score des kompletten Benchmark-Korpus, Drift-Messung gegen eingefrorenen Referenzkorpus, Rekalibrierung der Gewichte aus Korpus-Statistik (Kalibrierungs-Loop #12, Drift #47) | quartalsweise (Re-Baseline-Kalender, #67) | teuer, selten |

L1-Pass-Rate ist eine Produktentscheidung, kein 100 %-Zwang — aber jede L1-Ausnahme wird dokumentiert. L2/L3 sind kalendarisch bzw. gate-gebunden, nicht bei jedem Commit.

## Zuordnung aller bestehenden Eval-Artefakte

### L2 — Control Set

- `eval/control_set.jsonl` — Golden Control Set: 10 handgeschriebene Texte (5 Slop / 5 Hard Negatives), known-FN-Register (ADR-0003)
- `eval/run_control_set.py` — FN/FP-Gate (Threshold 0.40, known_fn-Ausnahmen, RESOLVED-Meldung); läuft bei jedem Issue im Burn

### L3 — Quartals-Re-Score / Kalibrierung

- `eval/corpus.jsonl` — Benchmark-Korpus (314 Texte, Labels, Genres, Quellen; Belegtquote ≥ 60 %, adr/0005)
- `eval/run_benchmark.py` — Precision/Recall/F1 @ 0.40 + FP-/FN-Rate je Genre
- `eval/calibrate.py` — Gewichts-Kalibrierung aus Korpus-Statistik (nur im Re-Baseline-Zyklus, s. SCORE-GOVERNANCE.md)

### L1 — Unit-Assertions (tests/)

- `tests/test_adr.py` — ADR-Pflichtfelder (#65, Meta)
- `tests/test_adverb_rate.py` — Signal #24 Adverb-Rate (Fixtures)
- `tests/test_benchmark_runner.py` — L3-Runner selbst + Korpus-Disziplin (Zeilen, Quellen, 60 %-Regel)
- `tests/test_binary_contrast_ext.py` — Signal #26 BinaryContrast
- `tests/test_classifier.py` — src/classifier.py Klassifikation
- `tests/test_cli.py` — CLI-Härtung (MS-I1)
- `tests/test_code_slop.py` — #9 detect-only-Code-Slop (kein Score-Einfluss, ADR-0006)
- `tests/test_control_set.py` — L2-Gate-Artefakte (Dateiformat, known_fn)
- `tests/test_copula_rate.py` — Signal #22 Copula-Rate
- `tests/test_data_files.py` — Datenfile-Integrität (JSONL/JSON)
- `tests/test_diff_mode.py` — #10 Diff-Modus (nur geänderte Zeilen, Code-Routing)
- `tests/test_docs_examples.py` — Doku-Beispiele stimmen mit Scorer-Verhalten überein (#48)
- `tests/test_engine_sync.py` — SSOT-Parity Scorer↔ontology.json (ADR-0002)
- `tests/test_ssot.py` — #49 SSOT-Gate (check_ssot.py: Ontology-Kopie, Generated-View, Konstanten-Register)
- `tests/test_evals_doc.py` — diese Zuordnung prüfen (#68, Meta)
- `tests/test_fn_series_signals.py` — Batch-F-FN-Serien (0101-0606) + Beleg-Disziplin (>=3 slop-, 0 clean-Texte)
- `tests/test_fp_guards.py` — #23 Guards (Quote-Exemption, Kumulativregel)
- `tests/test_human_voice.py` — #21 positive Gegenprofil-Referenz (Struktur-Pinning, kein Scorer)
- `tests/test_fu_batch_g.py` — FU-Register-Abrechnung Batch G (FU-2/3/4 Red-Fixes aus Reviews C/D)
- `tests/test_fu_batch_g2.py` — FU-5/7/10 (as_any-Kommentar-Guard, CHANGELOG-Claim, SKILL-Benchmark-Spiegel)
- `tests/test_generated_docs.py` — #34 generierte Doku/CHANGELOG
- `tests/test_genre_profiles.py` — #42 Genre-Opt-in-Profile (ADR-0004)
- `tests/test_governance_doc.py` — #67 Governance-Pflichtabschnitte (Meta)
- `tests/test_input_norm.py` — #40 Input-Normalisierung/Evasion
- `tests/test_instruction_slop.py` — Signal Instruction-Slop
- `tests/test_intensifier_fix.py` — FU-1 Intensifier-Fix
- `tests/test_learning_store.py` — #29 Learning-Store (--learn, Escalations-Schutz)
- `tests/test_markup_anomalies.py` — Signal Markup-Anomalien
- `tests/test_methodology_doc.py` — #63 Kodex-Konsistenz (Meta)
- `tests/test_micro_patterns.py` — #13 Mikro-Muster
- `tests/test_portability.py` — #14 Portability
- `tests/test_proof_metrics.py` — Signal Proof-Metrics
- `tests/test_provenance.py` — #20 Provenance-Marker
- `tests/test_quantifiers.py` — Signal Quantifiers
- `tests/test_reinventing_wheel.py` — Signal Reinventing-the-Wheel
- `tests/test_rhetorical_patterns.py` — Signal Rhetorical Patterns
- `tests/test_rhythm_openers.py` — Signal Rhythm-Opener
- `tests/test_scorer.py` — Scorer-Kern (Score-Berechnung, Threshold)
- `tests/test_signal_dod.py` — #64 DoD-Check-Script (Meta)
- `tests/test_skill_scripts.py` — Skill-Skripte-Smoke
- `tests/test_templates.py` — #66 Templates-Pflichtfelder (Meta)
- `tests/test_tokenizer.py` — #43 Tokenizer

*Meta-Tests (Kodex/DoD/ADR/Templates/Governance/Evals) sind selbst L1: sie sichern die Prozess-Integrität der anderen Ebenen.*

## Small-Corpus-Rezept (< 1000 gelabelte Beispiele)

Für Korpus-Erweiterungen und neue Genres (Quelle: methoden-fundament.md §2, Hamel/Settles):

1. **Stratifikation vor Masse:** pro Signal × Genre × Sprache × Länge je ≥ 3–5 Beispiele, Hard Negatives inklusive. Eine stratifizierte 300er-Matrix schlägt 3000 zufällige Texte (praktiziert in #41).
2. **Few-shot-Eval-Matrix:** Signal × Korpus-Schicht als Tabelle; jede Zelle braucht Mindestbelegung, bevor ein Score als belastbar gilt.
3. **Error-driven Labeling (aktives Lernen light):** nur Beispiele labeln, bei denen der Detektor unsicher/falsch liegt — der #29-Learning-Store (`not_slop.jsonl`, `--learn`) ist der Speicher dafür; Ergänzung geplant: False-Negative-Store (slop_detected=false-Meldungen).
4. **Frozen-Golden-Set + Challenge-Set:** eingefrorenes Referenzset für Regression (L2/L3) plus kleines wachsendes Challenge-Set für neue Modellgenerationen (#47/#59).

Konsistenz dieser Zuordnung prüft `scripts/check_methodology.py`: jede Datei unter eval/ (py, jsonl) und tests/ (test_*.py) muss oben vorkommen.
