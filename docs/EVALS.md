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

#### Welche Zahl ist welcher Art (#85)

`calibrate.py` fittet die Dimensionsgewichte des Scorers **auf** `eval/corpus.jsonl`; `run_benchmark.py` misst anschließend **auf demselben Korpus**. Die Standardausgabe ist damit ein **In-Sample**-Wert und kein Schätzer für ungesehene Texte. Das gilt für jede Zahl, die ohne weiteren Zusatz kommuniziert wird — CHANGELOG, Commit-Messages, README.

Für eine **Held-out**-Schätzung: `python eval/run_benchmark.py --cross-validate K`. Die Gewichte werden je Fold nur auf dem Trainingsteil gefittet, gemessen wird auf dem Teil, den sie nie gesehen haben. Der Lauf gibt beide Zahlen nebeneinander aus.

Welcher Teil gefittet wird, entscheidet, wie aussagekräftig die Held-out-Zahl ist:

| Engine | Art | Bedeutung der Held-out-Zahl |
|---|---|---|
| `skill-scorer` | **gefittet** (14 Dimensionsgewichte aus `calibrate.py`) | die einzige echte Generalisierungsschätzung |
| `src-classifier` | **nicht gefittet** (Typ-Muster-Matching) | per Konstruktion gleich der In-Sample-Zahl |
| `skill-pipeline` | gemischt (nimmt den stärkeren Wert) | **untertreibt** den Overfit, weil der ungefittete Teil ihn verdeckt |

Kosten: Kreuzvalidierung ist L3, nicht L1 — eine Coordinate-Ascent-Runde kostet rund 200 s je Fold. Sie gehört in den Re-Baseline-Zyklus, nicht in CI.

**Wo die Zahl steht.** Veröffentlicht wird sie an genau einer Stelle: `skills/ai-slop-detection/SKILL.md`, Abschnitt „Benchmark". Diese Angabe ist gegen einen frischen `run_benchmark.run()`-Lauf gepinnt — Korpusgröße, Slop-/Clean-Aufteilung, P/R/F1 und die vollständige Konfusionsmatrix (`tests/test_cross_validation.py::DocumentationTest`). Der Pin ist nicht theoretisch: die Angabe war beim Einbau 17 Clean-Texte alt (`n=314` statt `n=331`), und weil Recall nicht von Clean-Texten abhängt und Precision auf 1.0 stand, hatte kein Gate und kein Leser das bemerkt. Zweitkopien der Zahl in weiteren Dokumenten sind deshalb unerwünscht; wer sie zitiert, verlinkt SKILL.md.

### L1 — Unit-Assertions (tests/)

- `tests/test_adr.py` — ADR-Pflichtfelder (#65, Meta)
- `tests/test_adverb_rate.py` — Signal #24 Adverb-Rate (Fixtures)
- `tests/test_anchor_drift.py` — #78 Anchor-Drift (detect-only, Anker-Diff, Dezimal-Grenzfall)
- `tests/test_anchor_diff_cli.py` — #78 Anchor-Diff-CLI (--anchor-diff im Diff-Modus)
- `tests/test_null_edit_contract.py` — #79 Null-Edit-Contract-Gate (93 Hard Negatives clean auf beiden Engines, Null-Edit-Stabilität, Grenzband-Register eval/hardneg_borderline.json)
- `tests/test_fp_baseline.py` — #80 FP-Baseline-Register (eval/fp_baseline.json, CI-Snapshot `scripts/fp_baseline.py --check`)
- `tests/test_cross_validation.py` — #85 Held-out-Schätzer: Folds disjunkt/vollständig/stratifiziert/deterministisch (M8), Leckage-Probe über einen injizierten Kalibrator (kein Text aus dem eigenen Held-out-Fold), Null-Runden-Kontrolle (ohne Kalibrierung muss Held-out = In-Sample sein, sonst steckt der Fehler in der Fold-Mechanik), In-Sample und Held-out nebeneinander, gefitteter Scorer getrennt vom ungefitteten Typ-Klassifikator und die Pipeline als gemischt markiert, Klassifikationspflicht je Engine (unklassifizierte Engine = Fehler, keine Vermutung), CLI `--cross-validate` opt-in und stdout nur Report (Kalibrator-Fortschritt auf stderr, sonst bricht `--json`), Lauffähigkeit von `eval/calibrate.py` (Gewichtsnamen gegen den Scorer) sowie der Doku-Pin: die in SKILL.md veröffentlichten Zahlen inkl. Korpusgröße und Konfusionsmatrix gegen einen frischen Benchmark-Lauf
- `tests/test_type_pattern_position.py` — #88 Positionssemantik für TypePattern-Muster: `^`-Präfix im SSOT als klauselinitialer Marker (Textanfang, Satzende, Zeilenanfang, Listeneintrag) mit Gegenproben, Opt-in-Nachweis für unmarkierte Muster, Pattern-Parity über die drei Term-Regex-Module, Parity der hartcodierten Musterkopie in `slop_classifier.py` gegen ontology.json, drei Fachdoku-Hard-Negatives unter Schwelle, Recall-Wächter über echte Content-Farm-Texte, zwei Grenzfälle (Einzeltreffer bleibt Hypothese, Listicle-Opener in Liste zählt)
- `tests/test_self_check_docs.py` — #48 Meta-Self-Check: jedes Repo-Markdown unter Schwelle nach dem #69-Präpass, Kern-Dokumente ohne Ausnahme, Ausnahmen-Register `eval/self_check_docs.json` mit Begründungspflicht und am Messwert klebender Obergrenze (Ratsche), Test gegen tote Ausnahmen, Fehlschlagprobe mit untergeschobenem Slop-Dokument
- `tests/test_ci_gates.py` — #84 CI-Gate-Abdeckung: der Workflow muss die vollständige Suite fahren (kein `unittest discover`, das pytest-Dateien stumm überspringt), jedes dokumentierte Gate als eigener Schritt, Benchmark mit Untergrenzen statt „informational"; dazu Soll-Ist-Abgleich Testdateien gegen Collection und die Schwellenlogik von `eval/run_benchmark.py --min-precision/--min-recall`
- `tests/test_markup_prepass.py` — #69 Markdown-Präpass: Strip-Einheiten (Code-Fences, Inline-Code, Blockquotes, Tabellen, Zitat-Listen, Inhaltsverzeichnis), Gegenprobe Prosa-Listen/Idempotenz, Selbstanwendung (README/ONTOLOGY/AI-SLOP-ONTOLOGY/USER-GUIDE < 0.40), Missbrauchsprobe (Prosa-Slop bleibt erkannt), FP-Guardrail (kein Korpus-Verdikt kippt), CLI `--strip-markup` mit Roh- und Strip-Score
- `tests/test_phrase_matchability.py` — #83 Phrase-Matchbarkeit: struktureller Wächter, dass keine Phrase im SSOT unmatchbar ist (jede Phrase gegen ihre eigene Instanziierung), Platzhalter-Semantik [X]=Nominalphrase / [N]=Zahl mit Gegenproben, Pattern-Parity über src/scorer, skill/slop_scorer und skill/genre_profiles
- `tests/test_packaging.py` — #82 Packaging-Contract: Deklarationstest (jeder zur Laufzeit geladene Pfad ist Wheel-Inhalt, ohne Build/Netz) + Build-Test (Wheel bauen, entpacken, Engine und CLI ausserhalb des Checkouts ausführen; benchmark/selfcheck brechen mit Meldung statt Traceback ab)
- `tests/test_naturalness_guard.py` — #81 Naturalness-Guard (register_drift/over_sanitized detect-only ≤0.45, Genre-keep_when, modal_particle_anomaly Stub für #76)
- `tests/test_register_profile.py` — #74 Register-Profile v2: Stilkarte (9 Felder, JSON) + register_drift_intern (Hälften-Distanz, detect-only ≤0.5, #42-Genre-Exemptions, Kollisionsdisziplin zu #81 register_drift), Scorer-Kontext-Ausgabe ohne Score-Einfluss
- `tests/test_de_evidence_densification.py` — #76-Rest RI-2-FU: Evidence-Verdichtung (≥2 unabhängige Belege für ≥50% der de_*-Phrasen; L1) mit own:corpus-Belegtexten `eval/de_evidence_texts.jsonl` (L1-Belegtextdatei, eigene Handschrift) und C4-Coverage-Pin (Manipulationsprobe)
- `tests/test_structure_rest.py` — #76-Rest: M66 Fake-Analyse-Anhang + M71 Scheinnuance (detect-only ≤0.5, DoD 3/3/2); M67 bewusst nicht dupliziert (schon de_announcement_cleft)
- `tests/test_discourse_metrics.py` — #72 L4: explorative Diskurs-Signale rank_without_criterion & identical_enumeration (conf ≤0.35, `exploratory: True`, DoD 3/3/2) gegen versionierten L4-Referenzkorpus `eval/discourse_ref.jsonl` (Artefakt-Typen deep/10 + deep/06, Kontrollartefakte inklusive)
- `tests/test_de_typography.py` — #76 DE-Typografie M46/M47/M48/M49 (detect-only, DE-Sprachgate, je 3/3/2 Fixtures; Mapping: docs/de-coverage.md)
- `tests/test_de_vocab_layer.py` — #77 DE-KI-Marker-Vokabular (4 DE-Phrase-Kategorien in ontology.json, Belegpflicht je Phrase, Kollisionsfreiheit, EN-Corpus-Sicherheit)
- `tests/test_de_catalog_part2.py` — #76 Teil 2: 12 weitere DE-Phrase-Kategorien (Schema, Evidence-Pflicht mit Namespace-Präfix, #46-Kollisionsfreiheit inkl. paarweiser Substring-Check, Signal-DoD 3/3/2 je Kategorie)
- `tests/test_structure_metrics.py` — #76 Teil 2: M60 SynonymRotation + M61 IsometricUnits (detect-only, sprachagnostisch, 3/3/2-Fixtures, Schwellen fixture-kalibriert)
- `tests/test_ssot_de_layer.py` — FU-17: check_ssot C4 de_*-Phrase-Layer-Pin (16 Kategorien, Evidence-Regel, Namespace-Präfix) mit 4 Manipulationsproben
- `tests/test_genre_human_texts.py` — #80-Rest: Genre-Menschtexte je Genre ≥6 (own:handwritten), <0.40 auf beiden Engines, fp_baseline-Pin, Quartals-Re-Score-Anbindung (#47)
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
- `tests/test_deslop_loop.py` — #51 Loop-Runner-Orchestrator: E1–E5-Exit-Checks, Rollback, Voice-Budget, Signal-Bestätigung, Audit-Vollständigkeit (deterministische Fake-Detektoren, L1)
- `tests/test_lexikon.py` — #50 Lexikon-Pilot: Schema-Validierung, Beleg-Pflicht, Build-Determinismus, Sync-Gate (dist == Neubau), llms.txt-Struktur (L1)
- `tests/test_fu12_watchlist.py` — FU-12 Generic-Phrase-Watchlist (Reviewer-Gegenproben < 0.40, Benchmark-Verteidigung)
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

- `eval/corpus.jsonl` human-*-Fixtures (issue #80-Rest): je Genre ≥6 verifizierte Menschtexte; neue Fixtures `own:handwritten` (handgeschrieben verifiziert, Pre-LLM-Stil, keine Kopie geschützter Texte) für code/generic/nonfiction/news, im `fp_baseline.py --check`-Register gepinnt — Quartals-Re-Score (L3, Drift #47) misst Drift gegen dieses Register, Neu-Anreicherung weiterer Genre-Menschtexte läuft über denselben Pin-Mechanismus.
