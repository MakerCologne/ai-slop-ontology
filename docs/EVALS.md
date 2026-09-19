# EVALS.md — Drei-Level-Evals-Architektur

**Status:** konstitutiv (v2.0.0, Issue #68) · **Blaupause:** Hamel Husain, „Your AI Product Needs Evals" (2024) — L1/L2/L3-Pyramide; Methode E6 in `research/slop-ontology-gap-2026-08-24/methoden-fundament.md` §6 (externe Quelle).
**Verwandt:** docs/METHODOLOGY.md (M1, M5, M8), adr/0003 (Control-Set-Gate), adr/0005 (Benchmark-Disziplin), docs/SCORE-GOVERNANCE.md (#67), docs/TOOL-EVAL-CHECKLIST.md (#71 — Bewertung Fremd-Tools).

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

- `eval/human_ideological.jsonl` — Korpus Human/Ideological Slop (#98-Zielstand: 46 positiv / 40 negativ, alle `own:handwritten`, adr/0005: keine fremden Volltexte; positives Merkmal nie allein Phrase — Leak-Check-Feld `features`); Sampling-Plan: `eval/SAMPLING-human-ideological.md`
- `eval/run_human_ideological.py` — Korpus-Gate #98 (L2): Integrität 40/40 + Segment-Pins + Leak-Check + Precision-Pin ≥ 0.95 der Rhetorik-Gruppe auf Hard-Negatives; Gate 5b in `scripts/verify.sh`
- `eval/control_set.jsonl` — Golden Control Set: 10 handgeschriebene Texte (5 Slop / 5 Hard Negatives), known-FN-Register (ADR-0003)
- `eval/human_ideological.jsonl` — Seed-Korpus Human/Ideological Slop (#98-Vorlauf, 40 Einträge, alle `own:handwritten`, adr/0005: keine fremden Volltexte); Sampling-Plan: `eval/SAMPLING-human-ideological.md`
- `eval/control_set.jsonl` — Golden Control Set: 20 handgeschriebene Texte (10 Slop, davon 6 dokumentierte known_fn / 10 Hard Negatives), known-FN-Register (ADR-0003); P4/#231: +5 CommentSlop-Sequenzen (detect-only via engagement_comment_default) und +5 legitime LinkedIn-Kommentare (FP-Rate 0)
- `eval/run_control_set.py` — FN/FP-Gate (Threshold 0.40, known_fn-Ausnahmen, RESOLVED-Meldung); läuft bei jedem Issue im Burn

> Write-side-Evals (Prevention Contract, writing-rules, `eval/prevention_genres.jsonl` + `eval/run_prevention_eval.py` + `eval/JUDGE-prevention.md`) sind seit 18.09. ausgelagert: btm-skill-pipelines/write-side-rules (Hard Rule Detector-Only, ADR-0031).

### L3 — Quartals-Re-Score / Kalibrierung

- `eval/corpus.jsonl` — Benchmark-Korpus (331 Texte = 221 slop + 110 clean; Labels, Genres, Quellen; Belegtquote ≥ 60 %, adr/0005)
- `eval/run_benchmark.py` — Precision/Recall/F1 @ 0.40 + FP-/FN-Rate je Genre
- `eval/calibrate.py` — Gewichts-Kalibrierung aus Korpus-Statistik (nur im Re-Baseline-Zyklus, s. SCORE-GOVERNANCE.md)
- `eval/sample_mine.py` — #12 Empirischer Re-Kalibrierungs-Loop: N Samples pro Modell/Domain generieren (OpenAI-kompatibler Endpoint, offline über `--samples` umgehbar), n-gram-Wiederholung schürfen, Kandidaten für neue Tiers vorschlagen — gefiltert gegen die bestehende Scorer-Vokabular-SSOT, damit nur **unbedeckte** Muster vorgeschlagen werden. Integration: `calibrate.py --sample-mine <samples.jsonl>` druckt die Tier-Vorschläge neben den Gewichten. Vorschläge sind Review-Input, nie automatische Vokabular-Änderung (Kalibrierungsdisziplin s. #47/#104).

#### Loop-Reihenfolge (#12)

1. `sample_mine.py generate` (oder fremd generierte Samples als JSONL) →
2. `sample_mine.py mine --out-candidates` → Review der Kandidaten →
3. manuelle Tier-Aufnahme über den SSOT-Pfad (ontology/Skill-Doku-Gates) →
4. `calibrate.py` (ggf. `--sample-mine`) + `run_benchmark.py` gegen unverändertes Korpus (keine EN-Regression).

#### Welche Zahl ist welcher Art (#85)

`calibrate.py` fittet die Dimensionsgewichte des Scorers **auf** `eval/corpus.jsonl`; `run_benchmark.py` misst anschließend **auf demselben Korpus**. Die Standardausgabe ist damit ein **In-Sample**-Wert und kein Schätzer für ungesehene Texte. Das gilt für jede Zahl, die ohne weiteren Zusatz kommuniziert wird — CHANGELOG, Commit-Messages, README.

Für eine **Held-out**-Schätzung: `python eval/run_benchmark.py --cross-validate K`. Die Gewichte werden je Fold nur auf dem Trainingsteil gefittet, gemessen wird auf dem Teil, den sie nie gesehen haben. Der Lauf gibt beide Zahlen nebeneinander aus.

**Der Startpunkt gehört zur Leckage.** Jeder Fold startet die Coordinate Ascent bei *uniformen* Gewichten (Masse 1/N), nicht bei den ausgelieferten `DEFAULT_WEIGHTS`. Die sind auf dem **gesamten** Korpus gefittet, also auch auf den Texten jedes Held-out-Folds; und weil Ascent ein Gewicht nur bei echter Verbesserung bewegt, bliebe eine vom Gesamt-Fit gut gesetzte Dimension einfach stehen — der Fit erreichte die Held-out-Zahl über die Initialisierung, obwohl der Kalibrator keinen Held-out-Text gesehen hat. Genau so war die erste Messung mit diesem Läufer kontaminiert (Held-out-Recall identisch zum In-sample-Recall, auf drei Stellen, auf beiden Engines). Der uniforme Start ist der schlechtere Startpunkt und liefert deshalb eine **konservative** Schätzung — die richtige Richtung für eine Zahl, deren Zweck es ist, die Engine nicht zu schmeicheln. Die Kalibrierung für den Re-Baseline-Zyklus startet unverändert bei den ausgelieferten Gewichten.

Die Untergrenzen `--min-precision`/`--min-recall` gelten dem In-sample-Lauf und werden mit `--cross-validate` **abgelehnt**, nicht ignoriert — sonst würde das CI-Gate durchlässig, sobald jemand die Flagge dort ergänzt.

Welcher Teil gefittet wird, entscheidet, wie aussagekräftig die Held-out-Zahl ist:

| Engine | Art | Bedeutung der Held-out-Zahl |
|---|---|---|
| `skill-scorer` | **gefittet** (14 Dimensionsgewichte aus `calibrate.py`) | die einzige echte Generalisierungsschätzung |
| `src-classifier` | **nicht gefittet** (Typ-Muster-Matching) | per Konstruktion gleich der In-Sample-Zahl |
| `skill-pipeline` | gemischt (nimmt den stärkeren Wert) | **untertreibt** den Overfit, weil der ungefittete Teil ihn verdeckt |

Kosten: Kreuzvalidierung ist L3, nicht L1 — eine Coordinate-Ascent-Runde kostet rund 200 s je Fold. Sie gehört in den Re-Baseline-Zyklus, nicht in CI.

**Was die Messung ergeben hat (2026-08-28, k=5, seed 17, 4 Startpunkte je Fold).** Scorer held-out 0.995 / 0.982 / 0.989 gegen in-sample 1.000 / 0.982 / 0.991; Pipeline held-out 0.995 / 0.995 / 0.995 gegen 1.000 / 0.995 / 0.998. Der Recall bleibt, die **Precision** fällt: je ein Clean-Text von 110 fällt über die Schwelle, sobald die Gewichte ihn nicht gesehen haben. Die zitierte `FP=0` ist eine Eigenschaft der Trainingsmenge.

**Mehrere Startpunkte sind keine Feinheit.** Ein einzelner Anlauf vom uniformen Vektor aus findet auf diesem Korpus in **keinem** Fold einen Zug: das Ziel ist stückweise konstant, akzeptiert wird nur eine Verbesserung durch eine Koordinate, und der uniforme Vektor liegt auf einem Plateau. Ein solcher Lauf misst eine Uniform-Baseline und nennt sie Refit. Dass das ein Optimierer-Artefakt ist und keine Aussage über die Gewichte, zeigt die Gegenprobe: `DEFAULT_WEIGHTS` schlägt den uniformen Vektor auf vier von fünf Trainingsfolds. Deshalb `--cv-starts` (Default 4), Neustarts aus Fold- und Neustart-Index geseedet, nie aus dem Korpus. Der Beitrag der Kalibrierung selbst ist damit noch nicht beziffert — das ist #106.

**Wo die Zahl steht.** Veröffentlicht wird sie an genau einer Stelle: `skills/ai-slop-detection/SKILL.md`, Abschnitt „Benchmark". Diese Angabe ist gegen einen frischen `run_benchmark.run()`-Lauf gepinnt — Korpusgröße, Slop-/Clean-Aufteilung, P/R/F1 und die vollständige Konfusionsmatrix (`tests/test_cross_validation.py::DocumentationTest`). Der Pin ist nicht theoretisch: die Angabe war beim Einbau 17 Clean-Texte alt (`n=314` statt `n=331`), und weil Recall nicht von Clean-Texten abhängt und Precision auf 1.0 stand, hatte kein Gate und kein Leser das bemerkt. Zweitkopien der Zahl in weiteren Dokumenten sind deshalb unerwünscht; wer sie zitiert, verlinkt SKILL.md.

### L1 — Unit-Assertions (tests/)

- `tests/test_gates.py` — #118 Hard Gates (Binärsignale): FAIL/PASS je Gate (placeholder_credentials, elision_comments, lorem_ipsum, dead_anchor, placeholder_image), Auto-Scope Code/Markup, Score-Neutralität (`--gates` ändert slop_score nie), gates-Key im CLI-JSON (L1)
- `tests/test_conversational_fillers.py` — #110 konversationelle Floskeln (Hassid 4–8): Quick-Update-Meta-Ankündigungen plus bewachte Spezialfälle „most people" (satzinitial, ohne First-Person-Quelle) und „hope this helps" (Positions-Guard vor Grußformel); je Familie 2 positive + 2 Hard-Negative-Fixtures; „quick update on" bewusst ausgeschlossen (FP-Baseline clean-email-01) (L1)
- `tests/test_issue104_doc_drift.py` — #104 Slice A: Doku<->SSOT-Drift (L1) — Gate-Test für scripts/check_doc_signals.py (D1/D2, beide Richtungen) plus die beiden Issue-Beispiele als Matcher-/Classifier-Fixtures ('it is worth noting' in hedging_qualifiers, Template 'in today's [X]' in opening_formulas; konkrete SSOT-Varianten bleiben matchbar)
- `tests/test_human_work_seo_extension.py` — #86 Portierung PR#6: Status-/Parent-/Source-Resolution der Work-/SEO-Slop-Extension, FP-Exclusions je Typ, Nicht-Kollaps Human/AI-Generierung, SEOSlop-Generationsneutralität (L1)
- `tests/test_parity_human_work_seo.py` — #86 DoD-2: JSON↔TTL-Parität der Extension-Klassen (detect-only-Niveau) + Import-Verbot im Scorer (adr/0009) (L1)
- `tests/test_source_verification.py` — #86 Quellenregister: Offline-Strukturprüfungen (arXiv/DOI/URL, Zukunftsdatum-Guard, Coverage-Ausweis) des aus PR#6 portierten `verify_sources.py`, inkl. Regressionstest des „no dead links bei Totalausfall"-Defekts (L1)
- `tests/test_example_fix_meta.py` — #229 Meta-Regressionstest (L1) — jedes `eval/example_fixes.jsonl`-Paar (broken→fixed) muss den eigenen Detektor passieren: broken erkannt (Score ≥ Schwelle), fixed clean (Score < Schwelle), beide Engines; verhindert Reinführung abgelehnter Schreibmuster

- `tests/test_verification_ladder.py` — #121 Verification Ladder: fake-done-Metrik je Funktion (asserted > tested > reachable > claimed-only > stub > synthetic-risk), 28 Fixtures inkl. Under-Credit-Fälle (Stub schlägt Test-Referenz) und Selbst-Analyse ohne Gates (L1)- `tests/test_issue104_doc_drift.py` — #104 Slice A: Doku<->SSOT-Drift (L1) — Gate-Test für scripts/check_doc_signals.py (D1/D2, beide Richtungen) plus die beiden Issue-Beispiele als Matcher-/Classifier-Fixtures ('it is worth noting' in hedging_qualifiers, Template 'in today's [X]' in opening_formulas; konkrete SSOT-Varianten bleiben matchbar)
- `tests/test_threshold_config.py` — #157 zentraler Threshold: config/threshold.json als einzige Quelle (Verhalten folgt der Config, Missing/Malformed/Out-of-Range brechen ab statt still zu fallen, committeter Wert 0.40 als Ratsche bis zum Sweep GL #6.3)
- `tests/test_short_text_guards.py` — #52 Kurztext-Guards: dokumentierte Mindestlängen je Metrik in config/threshold.json (short_text_guards), definiertes Skip-Verhalten (neutral + ausgewiesene skipped-Liste + Gewicht-Re-Normalisierung, buzzwords bleibt aktiv), Fixtures für 5-/20-/50-Wort-Texte (L1)
- `tests/test_model_dynamics.py` — #36 Modell-Dynamik: signalModelDynamics-Register (model_notes evidence-Pflicht, asOf-Quartal, Halbwertszeit-Pflicht für volatile Notizen) — Gate-Test für scripts/check_model_dynamics.py (M1–M5) gegen echte Ontologie und manipulierte Kopien (L1)
- `tests/test_model_notes.py` — #36 Modell-Dynamik: signalModelDynamics-SSOT-Sektion (schema, evidence-Pflicht M6, Halbwertszeit-Vokabular, Entries referenzieren reale Signale) + per-signal model_notes der Pilot-Signale + loop-guard-Doc-Existenz (L1)
- `tests/test_adr.py` — ADR-Pflichtfelder (#65, Meta)
- `tests/test_adverb_rate.py` — Signal #24 Adverb-Rate (Fixtures)
- `tests/test_opener_announcement.py` — #230 P3 Opener-Announcement (L1, detect-only): Frame-basierte Ankuendigungs-/Praise-Opener (Tier A immer, Tier B Ich-Anlauf nur text-initial ohne in-sentence Begruendung), TP/Hard-Negative-Fixtures inkl. Hard-Negative 'Ich denke, dass X, weil Y'
- `tests/test_anchor_drift.py` — #78 Anchor-Drift (detect-only, Anker-Diff, Dezimal-Grenzfall)
- `tests/test_anchor_diff_cli.py` — #78 Anchor-Diff-CLI (--anchor-diff im Diff-Modus)
- `tests/test_null_edit_contract.py` — #79 Null-Edit-Contract-Gate (93 Hard Negatives clean auf beiden Engines, Null-Edit-Stabilität, Grenzband-Register eval/hardneg_borderline.json)
- `tests/test_fp_baseline.py` — #80 FP-Baseline-Register (eval/fp_baseline.json, CI-Snapshot `scripts/fp_baseline.py --check`)
- `tests/test_calibration_drift.py` — #47 Kalibrierungs-Drift-Register (eval/calibration_reference.json, CI-Snapshot `scripts/calibration_drift.py --check`: Score-Verteilung p10/p50/p90 + per-Signal Hit-Rates gegen eingefrorenen Referenz-Snapshot; Messvorschrift docs/calibration-drift.md, Alert = Weight-Review-Trigger, kein Auto-Tuning)
- `tests/test_cross_validation.py` — #85 Held-out-Schätzer: Folds disjunkt/vollständig/stratifiziert/deterministisch (M8), Leckage-Probe über einen injizierten Kalibrator (kein Text aus dem eigenen Held-out-Fold), Null-Runden-Kontrolle (ohne Kalibrierung muss Held-out = In-Sample sein, sonst steckt der Fehler in der Fold-Mechanik), In-Sample und Held-out nebeneinander, gefitteter Scorer getrennt vom ungefitteten Typ-Klassifikator und die Pipeline als gemischt markiert, Klassifikationspflicht je Engine (unklassifizierte Engine = Fehler, keine Vermutung), CLI `--cross-validate` opt-in und stdout nur Report (Kalibrator-Fortschritt auf stderr, sonst bricht `--json`), Lauffähigkeit von `eval/calibrate.py` (Gewichtsnamen gegen den Scorer) sowie der Doku-Pin: die in SKILL.md veröffentlichten Zahlen inkl. Korpusgröße und Konfusionsmatrix gegen einen frischen Benchmark-Lauf
- `tests/test_type_pattern_position.py` — #88 Positionssemantik für TypePattern-Muster: `^`-Präfix im SSOT als klauselinitialer Marker (Textanfang, Satzende, Zeilenanfang, Listeneintrag) mit Gegenproben, Opt-in-Nachweis für unmarkierte Muster, Pattern-Parity über die drei Term-Regex-Module, Parity der hartcodierten Musterkopie in `slop_classifier.py` gegen ontology.json, drei Fachdoku-Hard-Negatives unter Schwelle, Recall-Wächter über echte Content-Farm-Texte, zwei Grenzfälle (Einzeltreffer bleibt Hypothese, Listicle-Opener in Liste zählt)
- `tests/test_severity_ssot.py` — #55 Severity-SSOT: Classifier liest Per-Signal-Tiers aus ontology.json `signalSeverity` (Legacy-Map nur Fallback), RPN-Fix-Reihenfolge im Loop (Tier → Konfidenz), empirische Kalibrierung der 5 Konflikt-Signale am Hard-Negatives-Korpus (L1)
- `tests/test_self_check_docs.py` — #48 Meta-Self-Check: jedes Repo-Markdown unter Schwelle nach dem #69-Präpass, Kern-Dokumente ohne Ausnahme, Ausnahmen-Register `eval/self_check_docs.json` mit Begründungspflicht und am Messwert klebender Obergrenze (Ratsche), Test gegen tote Ausnahmen, Fehlschlagprobe mit untergeschobenem Slop-Dokument
- `tests/test_ci_gates.py` — #84 CI-Gate-Abdeckung: der Workflow muss die vollständige Suite fahren (kein `unittest discover`, das pytest-Dateien stumm überspringt), jedes dokumentierte Gate als eigener Schritt, Benchmark mit Untergrenzen statt „informational"; dazu Soll-Ist-Abgleich Testdateien gegen Collection und die Schwellenlogik von `eval/run_benchmark.py --min-precision/--min-recall`
- `tests/test_markup_prepass.py` — #69 Markdown-Präpass: Strip-Einheiten (Code-Fences, Inline-Code, Blockquotes, Tabellen, Zitat-Listen, Inhaltsverzeichnis), Gegenprobe Prosa-Listen/Idempotenz, Selbstanwendung (README/ONTOLOGY/AI-SLOP-ONTOLOGY/USER-GUIDE < 0.40), Missbrauchsprobe (Prosa-Slop bleibt erkannt), FP-Guardrail (kein Korpus-Verdikt kippt), CLI `--strip-markup` mit Roh- und Strip-Score
- `tests/test_performative_stakes.py` — #115 performative_voice + manufactured_stakes (ZeroSlop): keep_when-Guards (First-Person-Erfahrungs-Anker, konkreter Termin/Fakt im Folgefenster), Kumulativregel, Guard-Isolation
- `tests/test_phrase_matchability.py` — #83 Phrase-Matchbarkeit: struktureller Wächter, dass keine Phrase im SSOT unmatchbar ist (jede Phrase gegen ihre eigene Instanziierung), Platzhalter-Semantik [X]=Nominalphrase / [N]=Zahl mit Gegenproben, Pattern-Parity über src/scorer, skill/slop_scorer und skill/genre_profiles
- `tests/test_project_config.py` — #11 Projekt-lokale Config: Validierung (unbekannte Familien/Keys, Gewichts-Bereich), Score-Integration (disabled_signals senkt Score, Allowlist senkt Buzzword-Count, Weight-Override), CLI --config (gültig + Fehlerfall)
- `tests/test_packaging.py` — #82 Packaging-Contract: Deklarationstest (jeder zur Laufzeit geladene Pfad ist Wheel-Inhalt, ohne Build/Netz) + Build-Test (Wheel bauen, entpacken, Engine und CLI ausserhalb des Checkouts ausführen; benchmark/selfcheck brechen mit Meldung statt Traceback ab)
- `tests/test_naturalness_guard.py` — #81 Naturalness-Guard (register_drift/over_sanitized detect-only ≤0.45, Genre-keep_when; #76-Rest M63: modal_particle_anomaly vollständiges DE-Inventar, density+stacking, detect-only ≤0.45, Colloquial-Genre-Guard, Voll-Zweibeleg de-ev-29)
- `tests/test_register_profile.py` — #74 Register-Profile v2: Stilkarte (9 Felder, JSON) + register_drift_intern (Hälften-Distanz, detect-only ≤0.5, #42-Genre-Exemptions, Kollisionsdisziplin zu #81 register_drift), Scorer-Kontext-Ausgabe ohne Score-Einfluss
- `tests/test_de_variant_rest.py` — #77-Rest: M18/M33/M65 als de_chatbot_leftover/de_signposting/de_copula_avoidance (Voll-Zweibeleg de-ev-17..19, DoD 3/3/2)
- `tests/test_de_variant_rest2.py` — #77-Rest Welle 4: M35/M59/M70 als de_fake_dialog/de_faux_candid/de_false_agency (Voll-Zweibeleg de-ev-20..22, DoD 3/3/2)
- `tests/test_de_variant_rest3.py` — #77-Rest Welle 5: M7/M26/M30 als de_dichotomy_close/de_quote_fabrication/de_register_shift (Voll-Zweibeleg de-ev-23..25, DoD 3/3/2)
- `tests/test_de_variant_rest4.py` — #77-Rest Welle 6: M32/M56/M72 als de_rhetorical_setup/de_aphorism/de_therapeutic_validation (Voll-Zweibeleg de-ev-26..28, DoD 3/3/2)

- `tests/test_naturalness_guard.py` — #81 Naturalness-Guard (register_drift/over_sanitized detect-only ≤0.45, genre-keep_when; #76-Rest M63: modal_particle_anomaly vollständiges DE-Inventar, density+stacking, detect-only ≤0.45, Colloquial-Genre-Guard, Voll-Zweibeleg de-ev-29)
- `tests/test_voice_drift.py` — #56 Voice-Drift-Guardrail: kumulatives Voice-Budget vs Draft_0 (β=25%), Burstiness-/TTR-Non-Regression (Floor draft_0×0.9), Loop-Integration (rejected_voice_drift_*, Audit-Payload, L1)


- `tests/test_findings_standard.py` — #119 Findings-Standard mit Receipts: `{signal_id, span, evidence_quote, reliability, suggested_action}` — Schema-Validierung, Adapter (rhetorical/register/naturalness), receipts aus slop_score mit char-Spans; Ausgabevertrag ohne Score-Anteil (DoD 3/3/2)
- `tests/test_naturalness_guard.py` — #81 Naturalness-Guard (register_drift/over_sanitized detect-only ≤0.45, Genre-keep_when; #76-Rest M63: modal_particle_anomaly vollständiges DE-Inventar, density+stacking, detect-only ≤0.45, Colloquial-Genre-Guard, Voll-Zweibeleg de-ev-29)
- `tests/test_register_profile.py` — #74 Register-Profile v2: Stilkarte (9 Felder, JSON) + register_drift_intern (Hälften-Distanz, detect-only ≤0.5, #42-Genre-Exemptions, Kollisionsdisziplin zu #81 register_drift), Scorer-Kontext-Ausgabe ohne Score-Einfluss
- `tests/test_domain_bindings.py` — #35 Domain-Trigger: SSOT-Sanity von `domainBindings` (≥5 Pilot-Signale, whitelist XOR blacklist, deklarierte Domains), Accessor-Semantik (Whitelist schlägt Blacklist, Default domain-agnostisch), Scorer-Integration (`--domain` zero-t gemappte Gewichtsdimensionen, JSON-Audit-Felder, Exit 2 bei unbekannter Domain), Classifier-Integration (Filter vor Noisy-OR-Aggregation, fail-loud)
- `tests/test_de_evidence_densification.py` — #76-Rest RI-2-FU: Evidence-Verdichtung (≥2 unabhängige Belege für ≥50% der de_*-Phrasen; L1) mit own:corpus-Belegtexten `eval/de_evidence_texts.jsonl` (L1-Belegtextdatei, eigene Handschrift) und C4-Coverage-Pin (Manipulationsprobe)
- `tests/test_structure_rest.py` — #76-Rest: M66 Fake-Analyse-Anhang + M71 Scheinnuance (detect-only ≤0.5, DoD 3/3/2); M67 bewusst nicht dupliziert (schon de_announcement_cleft)
- `tests/test_structure_m6.py` — #76-Rest: M6 HollowConclusion — Fazit-/Summary-Heading mit Mini-Körper ohne Zahlen/Verweise (detect-only ≤0.5, DoD 3/3/2, sprachagnostisch DE+EN)
- `tests/test_example_fix_meta.py` — #229 / P2 Meta-Regressionstest: jeder `example_fix` aus RHETORICAL_PATTERNS muss den eigenen Detektor (rhetorical_patterns + rhythm_metrics) ohne Befund passieren — Anti-Slop darf keine neuen Templates säen (L1)
- `tests/test_opener_announcement.py` — #230 / P3: OpenerAnnouncement (Lob-/Ankuendigungs-Frames, text-initiale Ich-Anlaeufe ohne Begruendung) und ParagraphConnectorRate (advisory, nie gescored) — je ≥1 TP + ≥2 Hard Negatives (L1)

### Detektions-Evals (fortgeführt nach ADR-0031; frühere Prevention-Contract-Narrative ausgelagert)

- `tests/test_comment_genre.py` — #231 / P4: Genre-Profile comment/message (Opt-in via `--genre`, ADR-0004 kein Auto-Detect), engagement_comment_default (detect-only ≤0.5, Sequenz Lob→Paraphrase→Ergänzung→Frage, ≥3/4 in Reihenfolge) und FP-Rate-0-Nachweis für die 5 legitimen Kommentar-Hard-Negatives aus dem erweiterten Control-Set (L1/L2)
- `tests/test_discourse_metrics.py` — #72 L4: explorative Diskurs-Signale rank_without_criterion & identical_enumeration (conf ≤0.35, `exploratory: True`, DoD 3/3/2) gegen versionierten L4-Referenzkorpus `eval/discourse_ref.jsonl` (Artefakt-Typen deep/10 + deep/06, Kontrollartefakte inklusive)
- `tests/test_circular_explanations.py` — #122 CircularExplanation: tautologische Definitionen (definitional-Verb + Stamm-Overlap Subjekt/Praedikat, Praedikat ≤ 3 neue Staemme, conf ≤ 0.45 detect-only) mit Hard-Negatives (technische Referenz "handles", echte Definition, Kurzsatz, verb-lose Wiederholung) und DE-Fixture
- `tests/test_de_typography.py` — #76 DE-Typografie M46/M47/M48/M49 (detect-only, DE-Sprachgate, je 3/3/2 Fixtures; Mapping: docs/de-coverage.md)
- `tests/test_de_vocab_layer.py` — #77 DE-KI-Marker-Vokabular (4 DE-Phrase-Kategorien in ontology.json, Belegpflicht je Phrase, Kollisionsfreiheit, EN-Corpus-Sicherheit)
- `tests/test_de_catalog_part2.py` — #76 Teil 2: 12 weitere DE-Phrase-Kategorien (Schema, Evidence-Pflicht mit Namespace-Präfix, #46-Kollisionsfreiheit inkl. paarweiser Substring-Check, Signal-DoD 3/3/2 je Kategorie)
- `tests/test_structure_metrics.py` — #76 Teil 2: M60 SynonymRotation + M61 IsometricUnits (detect-only, sprachagnostisch, 3/3/2-Fixtures, Schwellen fixture-kalibriert)
- `tests/test_structure_comparative.py` — #75 Signal 6: M72 ComparativeFraming / Komparativ-Rahmung ("eher X als Y", "nicht X, sondern Y", "weniger X als vielmehr Y", "less about X, more about Y"; detect-only ≤0.5, DoD 3/3/2, Einzeltreffer unmarkiert; EN "not just X but Y" bleibt bei BinaryContrast, #46)
- `tests/test_ssot_de_layer.py` — FU-17: check_ssot C4 de_*-Phrase-Layer-Pin (16 Kategorien, Evidence-Regel, Namespace-Präfix) mit 4 Manipulationsproben
- `tests/test_de_variant_rest.py` — #77-Rest: 3 neue de_*-Kategorien (M18 de_chatbot_leftover, M33 de_signposting, M65 de_copula_avoidance; je 6 Phrasen conf 0.6, Voll-Zweibeleg) mit Signal-DoD 3/3/2 je Kategorie (L1)
- `tests/test_genre_human_texts.py` — #80-Rest: Genre-Menschtexte je Genre ≥6 (own:handwritten), <0.40 auf beiden Engines, fp_baseline-Pin, Quartals-Re-Score-Anbindung (#47)
- `tests/test_collision_matrix.py` — #46 Signal-Kollisions-Matrix: jede COLL-Auflösung aus `ontology.json#/collisionMatrix` hat ein Fixture, das belegt, dass dasselbe Vorkommen genau einmal zählt (COLL-1 FakeStrongVerb vs. copula rate, COLL-2 EmDashExcess vs. FormattingSlop, COLL-3 Adverb vs. positive-voice, COLL-4 Regex-Span-Dedup)
- `tests/test_benchmark_runner.py` — L3-Runner selbst + Korpus-Disziplin (Zeilen, Quellen, 60 %-Regel)
- `tests/test_binary_contrast_ext.py` — Signal #26 BinaryContrast
- `tests/test_classifier.py` — src/classifier.py Klassifikation
- `tests/test_cli.py` — CLI-Härtung (MS-I1)
- `tests/test_findings_receipts.py` — #119 Findings-Standard mit Receipts: Feld-Vollständigkeit ({signal_id, span, evidence_quote, reliability, suggested_action}), Span↔Quote-Konsistenz, Sortierung, Clean-Text-Leerlauf, Mehrzeilen-Line-Nummern, build_findings auf Minimal-Result (L1)
- `tests/test_code_slop.py` — #9 detect-only-Code-Slop (kein Score-Einfluss, ADR-0006)
- `tests/test_project_config.py` — #11 projekt-lokale Config: --config slop.json (disabled_signals, term_allowlist, weight_overrides), strikte Validierung, Noisy-OR-Re-Scoring nach Filterung (L1)
- `tests/test_metadata_slop.py` — #45 detect-only-Metadata-Slop: Commit-Messages/PR-Bodies, JSON-Datenfelder, Config-Boilerplate (kein Score-Einfluss, ADR-0006)
- `tests/test_review_counterfactual.py` — #122-Rest detect-only Review/Approval-Slop: Counterfactual Test (ankerlose generische Approvals passen auf jeden PR; Anker unterdrücken)
- `tests/test_metadata_slop_111.py` — #111 Metadata-Slop-Erweiterung: CommitVelocitySlop (Cadence-Verhalten), PRStructureSlop (anti-slop-Regeln), CommitKeywordSlop (gitorit-Vokabular); FP-Guards per Einzel-Regel-Negativ-Fixtures
- `tests/test_sample_mine.py` — #12 Sampling-Harness: Mine schlägt nur unbedeckte n-Gramme vor (SSOT-Filter gegen Scorer-Vokabular), Doc-Frequency-Ranking, Kandidaten-Cap, Einmal-Vorkommen wird ignoriert, `generate` ohne Endpoint verweigert sauber; `calibrate.py --sample-mine` druckt Tier-Vorschläge
- `tests/test_control_set.py` — L2-Gate-Artefakte (Dateiformat, known_fn)
- `tests/test_human_ideological_runner.py` — #98-Zielstand: Runner-Exit-Code, 40/40 + Segment-Pins, Quellendisziplin, Leak-Check je Positivem
- `tests/test_copula_rate.py` — Signal #22 Copula-Rate
- `tests/test_conversational_fillers.py` — #110 conversational_fillers (Hassid-Liste): 4 Phrasen, Hard-Negative-Guards (Sign-off-Fenster, Quellenangabe)
- `tests/test_chat_artifacts.py` — #113 chat-paste artifacts & elision: 6 deterministische Mikro-Signale (Chat-Paste-Artefakte wie Zeitstempel/Lead-Dashes, Elision), Fixtures inkl. Hard Negatives (L1)
- `tests/test_weight_gain_pin.py` — #106 DoD-Rest: Doku-Pin der Gewichts-Einordnung (SCORE-GOVERNANCE.md + Herkunfts-Kommentar slop_scorer.py nennen den Kalibrierungs-Gewinn der 14-dimensionalen Gewichte gegenüber uniform 1/N; Test bindet diese Zahlen, Muster fp_baseline #80/#85) (L1)
- `tests/test_slopkit_project_config.py` — #11 (slopkit-Variante): project-local config für das slopkit-Paket (disabled_signals/term_allowlist/weight_overrides, Fail-loud Exit 2) (L1)

- `tests/test_paste_artifacts.py` — #113 detect-only-Paste-Artefakte: 6 Mikro-Signale (elision-comment, chat-preamble, fence-in-code, meta-process-comment, list-label-marker, placeholder-credential-shape; kein Score-Einfluss, ADR-0006)
- `tests/test_control_set.py` — L2-Gate-Artefakte (Dateiformat, known_fn)
- `tests/test_copula_rate.py` — Signal #22 Copula-Rate
- `tests/test_gamed_verification.py` — #112 Gamed-Verification-Diff-Signale (detect-only): AssertionDelta, SkippedTest, TrivialAssertion, StubLeftBehind — Fixtures Positiv/Negativ je Signal (Signal-DoD)
- `tests/test_geometric_aggregation.py` — #117 Geometrische Score-Aggregation: gewichtetes geometrisches Mittel je Dimension als Option neben Noisy-OR (Aequivalenz-/Grenzfaelle, Gewichts-Sensitivitaet) (L1)- `tests/test_control_set.py` — L2-Gate-Artefakte (Dateiformat, known_fn)

- `tests/test_metadata_slop_111.py` — #111 Metadata-Slop-Erweiterung: CommitVelocitySlop (Cadence-Verhalten), PRStructureSlop (anti-slop-Regeln), CommitKeywordSlop (gitorit-Vokabular); FP-Guards per Einzel-Regel-Negativ-Fixtures
- `tests/test_control_set.py` — L2-Gate-Artefakte (Dateiformat, known_fn)- `tests/test_copula_rate.py` — Signal #22 Copula-Rate
- `tests/test_data_files.py` — Datenfile-Integrität (JSONL/JSON)
- `tests/test_diff_mode.py` — #10 Diff-Modus (nur geänderte Zeilen, Code-Routing)
- `tests/test_diff_verification.py` — #112 Gamed Verification im Diff-Modus: AssertionDelta/SkippedTest/TrivialAssertion (detect-only, 3/3/2-Fixtures, Findings-Standard #119)
- `tests/test_docs_examples.py` — Doku-Beispiele stimmen mit Scorer-Verhalten überein (#48)
- `tests/test_project_config.py` — #11 Projekt-lokale Config (--config: disabled_signals/term_allowlist/weight_overrides, Fail-loud-Validierung, Strukturdimensionen unangetastet)
- `tests/test_engine_sync.py` — SSOT-Parity Scorer↔ontology.json (ADR-0002)
- `tests/test_ssot.py` — #49 SSOT-Gate (check_ssot.py: Ontology-Kopie, Generated-View, Konstanten-Register)
- `tests/test_evals_doc.py` — diese Zuordnung prüfen (#68, Meta)
- `tests/test_fn_series_signals.py` — Batch-F-FN-Serien (0101-0606) + Beleg-Disziplin (>=3 slop-, 0 clean-Texte)
- `tests/test_fp_guards.py` — #23 Guards (Quote-Exemption, Kumulativregel)
- `tests/test_human_voice.py` — #21 positive Gegenprofil-Referenz (Struktur-Pinning, kein Scorer)
- `tests/test_fu_batch_g.py` — FU-Register-Abrechnung Batch G (FU-2/3/4 Red-Fixes aus Reviews C/D)
- `tests/test_fu_batch_g2.py` — FU-5/7/10 (as_any-Kommentar-Guard, CHANGELOG-Claim, SKILL-Benchmark-Spiegel)
- `tests/test_trajectory_guard.py` — #59 Score-Trajectory-Monitoring: ANOMALY/DIMINISHING/ROLLBACK_CHAIN-Trigger, Präzedenz, Konfigurierbarkeit, Run-Dir-Ingest (L1)
- `tests/test_run_audit_format_61.py` — #61 Run-Audit-Format: Standard-Dateien scan.md/fixes.md/trajectory.json/report.md je Run, Rekonstruierbarkeit, Legacy-Kompat, No-Op ohne runs_dir (L1)
- `tests/test_llm_scanner.py` — #57 LLM-Zweit-Scanner Layer 2: Prompt-Rotation (≥3 Varianten) + Position-Swap, Bias-Akzeptanz ≥0.9 auf Control-Set, Instabilität→Downgrade „unsicher“, Belegpflicht (Zitat muss aus dem Text stammen), genau ein Pass (keine Selbstkorrektur-Runden), malformed-Judge→inconclusive, Score-Disziplin (keine Verdrahtung in den Scorer) (L1, Fake-Judges)
- `tests/test_deslop_loop.py` — #51 Loop-Runner-Orchestrator: E1–E5-Exit-Checks, Rollback, Voice-Budget, Signal-Bestätigung, Audit-Vollständigkeit (deterministische Fake-Detektoren, L1)
- `tests/test_fixer_strategies.py` — #60 Best-of-N Fix-Strategien: Auswahl-Harness (Primärkriterium Score, Tie-Break kleinster Edit innerhalb epsilon, Voice-Budget-Guardrail, Abstention/Crash-Isolation, Loop-Integration als Fix-Callback) (deterministische Fakes, L1)
- `tests/test_confirm.py` — #58 Signal-Bestätigung ≥2 unabhängige Nachweise: ConfirmGate-Pfade (llm/resample/stability/confidence), Resample-Determinismus, fp_fix_rate-Metrik, Loop-Integration mit/ohne Gate (L1)
- `tests/test_lexikon.py` — #50 Lexikon-Pilot: Schema-Validierung, Beleg-Pflicht, Build-Determinismus, Sync-Gate (dist == Neubau), llms.txt-Struktur (L1)
- `tests/test_fu12_watchlist.py` — FU-12 Generic-Phrase-Watchlist (Reviewer-Gegenproben < 0.40, Benchmark-Verteidigung)
- `tests/test_generated_docs.py` — #34 generierte Doku/CHANGELOG
- `tests/test_genre_profiles.py` — #42 Genre-Opt-in-Profile (ADR-0004)
- `tests/test_engagement_sequences.py` — #231 Kommentar-Genre (comment) + Sequenz-Signal engagement_comment_default (detect-only, Lob→Paraphrase→Ergänzung→Frage); Control-Set: 10 Kommentar-Texte, FP-Rate 0 auf legitimen Kommentaren (Genre-Threshold 0.30)
- `tests/test_governance_doc.py` — #67 Governance-Pflichtabschnitte (Meta)
- `tests/test_input_norm.py` — #40 Input-Normalisierung/Evasion
- `tests/test_project_config.py` — #11 Projekt-lokale Config (disabled_signals/term_allowlist/weight_overrides, Auto-Discovery)
- `tests/test_aggregation_geomean.py` — #117 Aggregations-Modus (slop.json `aggregation: geomean`): Config-Validierung, Geomean < additiv bei einseitigem Signal, Epsilon-Untergrenze, Floor-Erhalt
- `tests/test_instruction_slop.py` — Signal Instruction-Slop
- `tests/test_intensifier_fix.py` — FU-1 Intensifier-Fix
- `tests/test_domain_trigger.py` — #35 Domain-Bindung: triggered_by:domain-Signale feuern nur im passenden Scope, ungebundene Signale und No-Arg-Pfad unverändert (L1, TP+Scope-Negativ+SSOT-Pin)
- `tests/test_best_practices_guard.py` — #156 FP-Guard: 'Best Practices' zählt nur mit generischem Verstärker (conditional_buzzwords), Plain-Referenz ist kein Marker (L1, TP+Hard Negative+SSOT-Pin)
- `tests/test_academic_register.py` — #114 Academic-Register-Signale: EpistemicMismatch, UnquantifiedScopeClaim, VagueAttribution — je Signal 2 Positive + 2 Hard-Negatives (Inversion mit n=/Zeitraum/Zitat; L1)
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
- `tests/test_signal_reliability.py` — #116 signalReliability-Register + UI-Tells (Enums, Datumsformat, weak⇒FP-Pflicht, CC-BY-SA-Attribution) (L1)
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
